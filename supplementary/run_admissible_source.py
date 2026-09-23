"""Fixed admissible-source double-well study; original outputs are read-only.

This runner writes only outputs/admissible_source. It changes the second
source-coordinate variance to 0.3 and supports fixed independent coefficients.
No result selection is performed. Figure/report/notebook updates are separate.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from portable_paths import portable_path
import platform
import statistics
import sys
import time

import numpy as np
import scipy
from threadpoolctl import threadpool_info, threadpool_limits

from comparison_notebook_api import load_notebook_api, CacheMissError

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "supplementary/admissible_source_config.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_sha(value):
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def serial(value):
    if isinstance(value, (str, Path)):
        return portable_path(value)
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return serial(value.item())
    if isinstance(value, dict): return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [serial(v) for v in value]
    return value


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(serial(value), indent=2, allow_nan=False)+"\n", encoding="utf-8")
    temporary.replace(path)


def new_source(config, seed):
    rng = np.random.default_rng(seed)
    center, width = config["source_mean_x1"], config["source_bump_half_width"]
    grid = np.linspace(center-width, center+width, config["source_bump_cdf_grid_points"])
    density = np.cos(np.pi*(grid-center)/(2*width))**2
    cdf = np.cumsum(density); cdf /= cdf[-1]
    cdf[0] = 0.0
    first = np.interp(rng.random(config["particles"]), cdf, grid)
    second = np.sqrt(config["source_x2_variance"])*rng.standard_normal(config["particles"])
    return np.column_stack([first, second])


def specifications(config, beta):
    """Deduplicate physical runs; roles preserve every planned comparison."""
    rows = {}
    def add(seed, method, regime, n, rank, dt, role):
        key = (seed, method, regime, n, rank, dt)
        if key not in rows:
            rows[key] = dict(beta=beta, seed=seed, method=method, regime=regime,
                             n_pairs=n, r_requested=rank, dt=dt, roles=[])
        if role not in rows[key]["roles"]: rows[key]["roles"].append(role)
    for seed in range(config["seed_counts"][str(beta)]):
        for method in config["methods"]:
            n = 0 if method == "FD" else config["main_training_pairs"]
            add(seed, method, "S", n, config["main_rank"], config["main_dt"], "main")
        for regime in ("S", "I"):
            add(seed, "RBF", regime, config["main_training_pairs"], config["main_rank"], config["main_dt"], "coefficient_comparison")
        for n in config["sample_size_budgets"]:
            add(seed, "RBF", "S", n, config["main_rank"], config["main_dt"], "sample_size")
        if beta == config["step_check_beta"]:
            for dt in (config["main_dt"], config["step_check_dt"]):
                for method, regime in (("FD", "S"), ("RBF", "S"), ("RBF", "I"), ("Legendre", "S")):
                    n = 0 if method == "FD" else config["main_training_pairs"]
                    add(seed, method, regime, n, config["main_rank"], dt, "step_check")
    for method in config["methods"]:
        ranks = config["fd_rank_scan"] if method == "FD" else config["learned_rank_scan"]
        n = 0 if method == "FD" else config["main_training_pairs"]
        for rank in ranks:
            add(config["rank_scan_seed"], method, "S", n, rank, config["main_dt"], "rank_scan")
    return list(rows.values())


def run_id(row):
    return f"beta{row['beta']:g}_seed{row['seed']}_{row['method']}_{row['regime']}_n{row['n_pairs']}_r{row['r_requested']}_h{round(row['dt']*1000):03d}"


def metric_function(target, config):
    rng = np.random.default_rng(config["projection_seed"])
    directions = rng.standard_normal((config["projection_directions"], target.shape[1]))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    ordered_target = np.sort(target @ directions.T, axis=0)
    def metric(particles):
        return float(np.sqrt(np.mean((np.sort(particles @ directions.T, axis=0)-ordered_target)**2)))
    return metric, directions


def instrumented_transport(pot, lam, basis, source, coefficient_source, rank, horizon, dt,
                           config, metric, fitted=None):
    """Original preweighted gEDMD / exact FD field and original RK4 ordering."""
    started = time.perf_counter(); excluded = 0.
    X = source.copy(); indices = np.arange(rank+1)
    P0, _ = basis(coefficient_source, indices)
    coefficients = P0.mean(axis=1); coefficients[0] = 1.0
    selected_lam = lam[indices]
    M, d = X.shape
    masks = {key: np.zeros(M, bool) for key in ("floor", "nonpositive", "cap", "projection")}
    events = dict(density_floor_events=0, nonpositive_density_events=0, speed_cap_events=0,
                  projected_coordinate_events=0, projected_particle_events=0,
                  stage_particle_events=0, projected_coordinate_evaluations=0,
                  projected_particle_evaluations=0, stage_calls=0, projection_calls=0,
                  minimum_stage_density=None, maximum_raw_velocity_norm=0.,
                  initial_outside=int(np.any((X < pot.box[:,0]) | (X > pot.box[:,1]), axis=1).sum()),
                  initial_projection_events=0)
    def project(Y):
        if not np.isfinite(Y).all(): raise FloatingPointError("Nonfinite intermediate particles before projection")
        clipped = pot.reflect(Y)
        different = clipped != Y
        affected = different.any(axis=1)
        masks["projection"] |= affected
        events["projection_calls"] += 1
        events["projected_coordinate_events"] += int(different.sum())
        events["projected_particle_events"] += int(affected.sum())
        events["projected_coordinate_evaluations"] += Y.size
        events["projected_particle_evaluations"] += len(Y)
        return clipped
    def velocity(Y, t):
        w = np.exp(-selected_lam*t)*coefficients
        if fitted is not None:
            aggregate = fitted.V[:, indices] @ w
            P, dP = fitted.dic.eval(Y)
            rho = P @ aggregate
            gradient = np.einsum("mjd,j->md", dP, aggregate)
        else:
            P, dP = basis(Y, indices)
            rho = w @ P
            gradient = np.einsum("k,kmd->md", w, dP)
        v = -gradient/np.maximum(rho, config["density_floor"])[:,None]
        norm = np.linalg.norm(v, axis=1, keepdims=True)
        if not np.isfinite(v).all(): raise FloatingPointError("Nonfinite spectral velocity")
        floor = rho < config["density_floor"]; nonpositive = rho <= 0
        cap = norm[:,0] > config["speed_cap"]
        masks["floor"] |= floor; masks["nonpositive"] |= nonpositive; masks["cap"] |= cap
        events["density_floor_events"] += int(floor.sum())
        events["nonpositive_density_events"] += int(nonpositive.sum())
        events["speed_cap_events"] += int(cap.sum())
        events["stage_particle_events"] += len(Y); events["stage_calls"] += 1
        minimum = float(rho.min())
        events["minimum_stage_density"] = minimum if events["minimum_stage_density"] is None else min(events["minimum_stage_density"], minimum)
        events["maximum_raw_velocity_norm"] = max(events["maximum_raw_velocity_norm"], float(norm.max()))
        return v*np.minimum(1., config["speed_cap"]/np.maximum(norm, 1e-12))
    nsteps = int(round(horizon/dt))
    checkpoint_times = np.unique(np.r_[np.arange(0., horizon, config["checkpoint_interval"]), horizon])
    wanted = {int(round(t/dt)) for t in checkpoint_times}
    records = []
    def record(step):
        nonlocal excluded
        elapsed = time.perf_counter()-started-excluded
        tick = time.perf_counter(); score = metric(X); excluded += time.perf_counter()-tick
        records.append(dict(time=step*dt, step=step, sw2=score, sampling_seconds=elapsed))
    record(0); completed = 0; failure = None
    for i in range(nsteps):
        try:
            t = i*dt; k1 = velocity(X,t)
            k2 = velocity(project(X+.5*dt*k1), t+.5*dt)
            k3 = velocity(project(X+.5*dt*k2), t+.5*dt)
            k4 = velocity(project(X+dt*k3), t+dt)
            X = project(X+dt/6*(k1+2*k2+2*k3+k4))
        except FloatingPointError as error:
            failure = str(error); break
        completed = i+1
        if completed in wanted: record(completed)
    if records[-1]["step"] != completed: record(completed)
    for name, mask in masks.items(): events["unique_"+name+"_particles"] = int(mask.sum())
    events["unique_affected_particles"] = int(np.logical_or.reduce(list(masks.values())).sum())
    events["requested_steps"] = nsteps; events["completed_steps"] = completed
    return dict(final=X, coefficients=coefficients, sw2=None if failure else records[-1]["sw2"],
                status="failed" if failure else "ok", failure=failure,
                events=events, path_masks=dict(masks,affected=np.logical_or.reduce(list(masks.values()))), checkpoint_records=records,
                sampling_seconds=time.perf_counter()-started-excluded, metric_seconds=excluded)


def load_fit(api, pot, ex, xd, yd, method, n, config, out, beta, seed, allow_fit=True):
    tic = time.perf_counter()
    dic = api["Dictionary"]("rbf",pot,n=config["rbf_n_per_direction"],wfrac=config["rbf_width_fraction"]) if method == "RBF" else api["Dictionary"]("poly",pot,p=config["legendre_degree"])
    expected = config["rbf_dictionary_size"] if method == "RBF" else config["legendre_dictionary_size"]
    if dic.size() != expected: raise AssertionError("Unexpected dictionary size")
    local = out / f"fit_beta{beta:g}_seed{seed}_{method}_n{n}.npz"
    local_key = dict(x=array_sha(xd[:n]), y=array_sha(yd[:n]), method=method, n=n,
                     dictionary_code=api["class_hash"](api["Dictionary"]),
                     estimator_code=api["code_hash"](api["_rr_init"]))
    if local.exists():
        with np.load(local) as data:
            if json.loads(str(data["key"])) != local_key: raise ValueError("Supplement fit provenance mismatch")
            fitted = object.__new__(api["RREstimate"])
            for key in ("V", "lam", "Gm", "Am", "lam_lag"): setattr(fitted, key, data[key].copy())
            fitted.kept = int(data["kept"]); fitted.r_max = min(200,len(fitted.lam)-1); fitted.dic = dic
        return fitted, dict(kind="supplement_fit_cache", path=local.name, seconds=time.perf_counter()-tic, fit_seconds=0.)
    before = len(api["_loader_metadata"]["cache_events"])
    try:
        fitted = api["RREstimate"](dic,xd[:n],yd[:n],chunk=5000,align=ex["align"])
        event = api["_loader_metadata"]["cache_events"][-1]
        return fitted, dict(kind="original_spectrum_cache", path=str(event["path"]), seconds=time.perf_counter()-tic, fit_seconds=0.)
    except CacheMissError:
        if not allow_fit: raise
        misses = api["_loader_metadata"]["cache_events"][before:]
        if any(event["name"] != "rr_eigenpairs" for event in misses): raise
        fitting_started = time.perf_counter()
        fitted = object.__new__(api["RREstimate"])
        api["_rr_init"](fitted,dic,xd[:n],yd[:n],chunk=5000,align=ex["align"])
        fit_seconds = time.perf_counter()-fitting_started
        np.savez_compressed(local,key=np.array(json.dumps(local_key)),V=fitted.V,lam=fitted.lam,
                            Gm=fitted.Gm,Am=fitted.Am,lam_lag=fitted.lam_lag,kept=fitted.kept)
        return fitted, dict(kind="new_original_initializer_fit", path=local.name, seconds=time.perf_counter()-tic, fit_seconds=fit_seconds)


def beta_context(api, config, beta, original):
    tic = time.perf_counter(); pot = api["Potential"]("A",d=2,beta=beta)
    if not np.array_equal(pot.box,np.asarray(config["box"])): raise AssertionError("Box changed")
    ex = api["exact_2d"](pot,n=config["fd_grid_N"],kmax=config["fd_cached_nonconstant_modes"])
    target = api["stationary_samples"](pot,config["particles"],np.random.default_rng(config["target_seed"]))
    nominal = float(8./ex["lam"][1]); horizon = round(nominal/config["main_dt"])*config["main_dt"]
    old_nominal = original[f"A2_beta{beta}"]["rbf"]["rows"][0]["T"]
    if abs(nominal-old_nominal) > 1e-10: raise AssertionError("FD horizon differs from existing experiment")
    reference = original[f"A2_beta{beta}"]["reference"]
    if reference["repetitions"] != config["reference_repetitions"]: raise AssertionError("Reference repetitions changed")
    metric, directions = metric_function(target, config)
    return pot,ex,target,metric,directions,nominal,horizon,reference,time.perf_counter()-tic


def probe(config, out):
    """Mandatory input cache checks and two explicitly requested old-source parity runs."""
    api = load_notebook_api(fail_on_cache_miss=True)
    original = json.loads((ROOT/"outputs/results.json").read_text())
    source_checks=[]
    pot = api["Potential"]("A",d=2,beta=0.)
    for base in (config["source_seed_base"],config["independent_coefficient_seed_base"]):
        for seed in range(max(config["seed_counts"].values())):
            old=api["source_A"](pot,config["particles"],np.random.default_rng(base+seed))
            new=new_source(config,base+seed)
            same=bool(np.array_equal(old[:,0],new[:,0]))
            if not same: raise AssertionError("CDF endpoint repair changed a prescribed first-coordinate draw")
            source_checks.append(dict(seed=base+seed,first_coordinate_bitwise_equal=True))
    pairs=[]; parity=[]; references=[]
    for beta in config["betas"]:
        pot,ex,target,metric,directions,nominal,horizon,ref,seconds=beta_context(api,config,beta,original)
        references.append(dict(beta=beta,mean=ref["metrics"]["sw"]["mean"],std=ref["metrics"]["sw"]["std"],repetitions=ref["repetitions"]))
        for seed in range(config["seed_counts"][str(beta)]):
            xd,yd=api["simulate_pairs"](pot,config["main_training_pairs"],np.random.default_rng(config["training_seed_base"]+seed))
            pairs.append(dict(beta=beta,seed=seed,training_x_sha256=array_sha(xd),training_y_sha256=array_sha(yd)))
            if beta==0. and seed==0:
                old_source=api["source_A"](pot,config["particles"],np.random.default_rng(config["source_seed_base"]))
                fit,info=load_fit(api,pot,ex,xd,yd,"RBF",config["main_training_pairs"],config,out,beta,seed,allow_fit=False)
                for name,lam,basis,fitted,expected in (
                    ("RBF",fit.lam,fit.basis,fit,original['A2_beta0.0']['rbf']['rows'][0]['sw']),
                    ("FD",ex['lam'],ex['basis'],None,original['A2_beta0.0']['fd_rscan']['64']['sw'])):
                    result=instrumented_transport(pot,lam,basis,old_source,old_source,64,horizon,.05,config,metric,fitted)
                    error=abs(result['sw2']-expected)
                    if error>config['old_source_parity_tolerance']:raise AssertionError(f'{name} old-source parity failed: {error}')
                    parity.append(dict(method=name,sw2=result['sw2'],existing_sw2=expected,absolute_difference=error))
                    print(f'PARITY {name}: difference={error:.3g}',flush=True)
    report=dict(status='PASS',source_checks=source_checks,old_source_parity=parity,training_inputs=pairs,references=references,
                cache_stats=dict(api['STATS']),configuration_sha256=sha(DEFAULT_CONFIG),
                note='Only two explicitly requested old-source parity transports were run; no new-source experiment was run in this probe.')
    write_json(out/'probe_checks.json',report)
    return report


def beta_worker(config, beta):
    with threadpool_limits(limits=1):
        started=time.perf_counter();out=ROOT/config['output_directory'];api=load_notebook_api(fail_on_cache_miss=True)
        original=json.loads((ROOT/'outputs/results.json').read_text())
        pot,ex,target,metric,directions,nominal,horizon,reference,context_seconds=beta_context(api,config,beta,original)
        np.savez_compressed(out/f'evaluation_beta{beta:g}.npz',target=target,directions=directions)
        shard=out/f'runs_beta{beta:g}.json';rows=json.loads(shard.read_text()) if shard.exists() else []
        done={row['run_id'] for row in rows};specs=specifications(config,beta)
        q=1/(2*config['source_x2_variance'])-1-beta/2
        if q<=0:raise AssertionError('The source Gaussian ratio is not uniformly tail dominated')
        for seed in range(config['seed_counts'][str(beta)]):
            tic=time.perf_counter()
            xd,yd=api['simulate_pairs'](pot,config['main_training_pairs'],np.random.default_rng(config['training_seed_base']+seed))
            training_load_seconds=time.perf_counter()-tic
            source=new_source(config,config['source_seed_base']+seed)
            independent=new_source(config,config['independent_coefficient_seed_base']+seed)
            source_file=out/f'source_beta{beta:g}_seed{seed}.npz'
            np.savez_compressed(source_file,initial=source,independent_coefficients=independent)
            fit_objects={};fit_records={}
            for spec in (r for r in specs if r['seed']==seed):
                identity=run_id(spec)
                if identity in done:continue
                method,n=spec['method'],spec['n_pairs']
                if method=='FD':
                    fitted=None;lam=ex['lam'];basis=ex['basis'];J=0
                    fit_info=dict(kind='original_FD_cache',seconds=context_seconds,fit_seconds=0.)
                else:
                    key=(method,n)
                    if key not in fit_objects:
                        fit_objects[key],fit_records[key]=load_fit(api,pot,ex,xd,yd,method,n,config,out,beta,seed)
                    fitted=fit_objects[key];fit_info=fit_records[key];lam=fitted.lam;basis=fitted.basis;J=fitted.dic.size()
                rank=min(spec['r_requested'],len(lam)-1)
                coefficient_source=independent if spec['regime']=='I' else source
                result=instrumented_transport(pot,lam,basis,source,coefficient_source,rank,horizon,spec['dt'],config,metric,fitted)
                endpoint=out/f'endpoint_{identity}.npz'
                np.savez_compressed(endpoint,final=result['final'],coefficients=result['coefficients'])
                row=dict(**spec,run_id=identity,r_used=rank,J=J,T=horizon,nominal_T=nominal,
                         source_seed=config['source_seed_base']+seed,
                         coefficient_seed=(config['independent_coefficient_seed_base'] if spec['regime']=='I' else config['source_seed_base'])+seed,
                         coefficient_sample_count=config['particles'],extra_coefficient_samples=config['particles'] if spec['regime']=='I' else 0,
                         particles=config['particles'],source_x2_variance=config['source_x2_variance'],
                         sw2=result['sw2'],status=result['status'],failure=result['failure'],
                         reference_mean=reference['metrics']['sw']['mean'],reference_std=reference['metrics']['sw']['std'],
                         events=result['events'],checkpoint_records=result['checkpoint_records'],
                         sampling_seconds=result['sampling_seconds'],metric_seconds=result['metric_seconds'],
                         fit_cache=fit_info,training_load_seconds=training_load_seconds,
                         initial_file=source_file.name,endpoint_file=endpoint.name,endpoint_sha256=array_sha(result['final']),
                         source_sha256=array_sha(source),coefficient_source_sha256=array_sha(coefficient_source),
                         coefficients_sha256=array_sha(result['coefficients']),training_x_sha256=array_sha(xd[:n]) if n else None,
                         training_y_sha256=array_sha(yd[:n]) if n else None,target_sha256=array_sha(target))
                rows.append(row);done.add(identity);write_json(shard,rows)
                print(f"beta={beta:g} seed={seed} {method}-{spec['regime']} n={n} r={spec['r_requested']} h={spec['dt']:g}: SW2={result['sw2']} ({result['sampling_seconds']:.1f}s) [{len(rows)}/{len(specs)}]",flush=True)
        if len(rows)!=len(specs):raise AssertionError('Incomplete beta shard')
        meta=dict(beta=beta,runtime_seconds=time.perf_counter()-started,cache_stats=dict(api['STATS']),threadpools=threadpool_info(),q_tail_coefficient=q)
        write_json(out/f'metadata_beta{beta:g}.json',meta)
        return meta


def aggregate(config, out, probe_report, started, original_hash):
    rows=[]
    for beta in config['betas']:
        shard=out/f'runs_beta{beta:g}.json'
        if shard.exists():rows.extend(json.loads(shard.read_text()))
    rows.sort(key=lambda r:(r['beta'],r['seed'],r['method'],r['regime'],r['n_pairs'],r['r_requested'],-r['dt']))
    groups=[]
    keys=sorted(set((r['beta'],r['method'],r['regime'],r['n_pairs'],r['r_requested'],r['dt']) for r in rows))
    for beta,method,regime,n,rank,dt in keys:
        part=[r for r in rows if (r['beta'],r['method'],r['regime'],r['n_pairs'],r['r_requested'],r['dt'])==(beta,method,regime,n,rank,dt)]
        good=all(r['status']=='ok' for r in part)
        values=[r['sw2'] for r in part]
        groups.append(dict(beta=beta,method=method,regime=regime,n_pairs=n,r_requested=rank,r_used=sorted(set(r['r_used'] for r in part)),dt=dt,
                           roles=sorted(set(role for r in part for role in r['roles'])),n=len(part),failures=sum(r['status']!='ok' for r in part),
                           sw2_mean=statistics.mean(values) if good else None,
                           sw2_std=statistics.stdev(values) if good and len(values)>1 else 0. if good else None))
    metadata=dict(created_utc=datetime.now(timezone.utc).isoformat(),runtime_seconds=time.perf_counter()-started,
                  complete=len(rows)==config['expected_unique_runs'],fd_label=f"FD-{config['fd_grid_N']}",
                  python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),
                  config_sha256=sha(DEFAULT_CONFIG),runner_sha256=sha(__file__),notebook_sha256=sha(ROOT/'BKT_experiments.ipynb'),
                  original_results_sha256=original_hash,worker_processes=config['max_beta_workers'],threads_per_worker=1,
                  timing_interpretation='Descriptive instrumented wall times under up to two simultaneous beta workers; no inter-method speedup claim.',
                  source_domain_status='Gaussian source ratio tail coefficient q=1/(2*0.3)-1-beta/2 is positive for every included beta. The finite-box numerical protocol still differs from full-space dynamics.',
                  coefficient_independence='I coefficients use only source seed700+s; transported initial particles use seed500+s. Coefficients are computed once and never refreshed.')
    summary=dict(config=config,runs=rows,groups=groups,references=probe_report['references'],metadata=metadata)
    write_json(out/'runs.json',rows);write_json(out/'summary.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--probe',action='store_true')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text())
    if config.get('version',1)>=2:
        raise ValueError('The ten-realisation revision uses revision_synthetic.py a2, followed by revision_verify.py and revision_publish.py. This legacy CLI preserves the original-source probe and must not overwrite the revision records.')
    out=ROOT/config['output_directory'];out.mkdir(parents=True,exist_ok=True)
    count=sum(len(specifications(config,b)) for b in config['betas'])
    if count!=config['expected_unique_runs']:raise AssertionError(f"Expected {config['expected_unique_runs']} physical runs, planned {count}")
    saved_config=out/'config.json'
    if saved_config.exists() and json.loads(saved_config.read_text())!=config:raise ValueError('Saved configuration differs; use a separate output directory')
    if any(out.glob('runs_beta*.json')) and not args.resume and not args.probe:raise FileExistsError('Existing experiment shards; use --resume')
    write_json(saved_config,config)
    source_manifest=dict(source_x2_variance=config['source_x2_variance'],source_x2_std=float(np.sqrt(config['source_x2_variance'])),
                         first_coordinate='Piecewise-linear inverse CDF of the original 4001-point cosine-squared bump, with first CDF value explicitly zero',
                         first_coordinate_support=[.4,1.6],q_by_beta={str(b):1/(2*config['source_x2_variance'])-1-b/2 for b in config['betas']},
                         full_space_Linfinity='Positive q makes the Gaussian ratio tail uniformly dominated while x1 is compactly supported. No H1 regularity or projected-domain theorem claim is inferred.',
                         original_first_coordinate_sampler_unchanged=True)
    write_json(out/'source_configuration.json',source_manifest)
    probe_path=out/'probe_checks.json'
    with threadpool_limits(limits=1):
        if probe_path.exists():
            probe_report=json.loads(probe_path.read_text())
            if probe_report['configuration_sha256']!=sha(args.config):raise ValueError('Probe configuration differs')
        else:probe_report=probe(config,out)
    print(f'PROBE PASS; fixed unique runs={count}; per-beta='+str({b:len(specifications(config,b)) for b in config['betas']}),flush=True)
    if args.probe:return
    started=time.perf_counter();original_hash=sha(ROOT/'outputs/results.json')
    order=sorted(config['betas'],key=lambda b:-len(specifications(config,b)))
    with ProcessPoolExecutor(max_workers=config['max_beta_workers']) as pool:
        futures={pool.submit(beta_worker,config,b):b for b in order}
        for future in as_completed(futures):
            meta=future.result();print(f"FINISHED beta={meta['beta']:g}",flush=True)
            aggregate(config,out,probe_report,started,original_hash)
    summary=aggregate(config,out,probe_report,started,original_hash)
    if len(summary['runs'])!=count or len({r['run_id'] for r in summary['runs']})!=count:raise AssertionError('Incomplete final suite')
    if sha(ROOT/'outputs/results.json')!=original_hash:raise AssertionError('Original numerical results changed during this independent suite')
    print(f"COMPLETED {count} runs; failures={sum(r['status']!='ok' for r in summary['runs'])}; elapsed={time.perf_counter()-started:.1f}s",flush=True)


if __name__=='__main__':
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        main()
