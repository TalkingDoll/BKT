"""Run the fixed equal-available-data comparison, independently of notebook experiments."""
from __future__ import annotations

import os
for _thread_option in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_thread_option] = "1"

import argparse
import hashlib
import inspect
import json
import math
from pathlib import Path
from portable_paths import portable_path
import statistics as stats
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import scipy
from threadpoolctl import threadpool_info, threadpool_limits

from comparison_notebook_api import load_notebook_api
from data_comparison_methods import fit_gradient_drift, run_baseline
from run_admissible_source import new_source

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "supplementary/data_comparison_config.json"
LABELS = {"A": "BKT", "B": "Drift + Langevin", "D": "KDE particle flow"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_sha(x):
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def serial(value):
    if isinstance(value, (str, Path)):
        return portable_path(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return serial(value.item())
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(serial(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def metric_factory(target, projections=64, seed=0):
    rng = np.random.default_rng(seed)
    directions = rng.standard_normal((projections, target.shape[1]))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    sorted_target = np.sort(target @ directions.T, axis=0)

    def metric(t, x):
        if not np.isfinite(x).all():
            return {"time": float(t), "sw2": None}
        value = np.sqrt(np.mean((np.sort(x @ directions.T, axis=0) - sorted_target) ** 2))
        return {"time": float(t), "sw2": float(value)}
    return metric, directions


def bkt_instrumented(ns, pot, fitted, source, horizon, dt, rank, checkpoints, callback):
    """The notebook RK4 operations, with diagnostic callbacks outside compute timing."""
    started = time.perf_counter()
    excluded = 0.0
    x = source.copy()
    indices = np.arange(rank + 1)
    p0, _ = fitted.basis(source, indices)
    c0 = p0.mean(1)
    c0[0] = 1.0
    lam = fitted.lam[indices]
    events = dict(stage_evaluations=0, density_floor_events=0, nonpositive_density_events=0,
                  speed_cap_events=0, projected_coordinate_events=0)
    saved_results, sample_times, actual_times = [], [], []
    wanted = {int(round(t / dt)) for t in checkpoints}

    def record(step):
        nonlocal excluded
        elapsed = time.perf_counter() - started - excluded
        t0 = time.perf_counter()
        result = callback(step * dt, x)
        excluded += time.perf_counter() - t0
        saved_results.append(result)
        sample_times.append(elapsed)
        actual_times.append(step * dt)

    def project(z):
        projected = pot.reflect(z)
        events["projected_coordinate_events"] += int(np.count_nonzero(projected != z))
        return projected

    def velocity(y, t):
        w = np.exp(-lam * t) * c0
        coefficients = fitted.V[:, indices] @ w
        p, dp = fitted.dic.eval(y)
        rho = p @ coefficients
        gradient = np.einsum("mjd,j->md", dp, coefficients)
        velocity = -gradient / np.maximum(rho, .001)[:, None]
        norm = np.linalg.norm(velocity, axis=1, keepdims=True)
        events["stage_evaluations"] += len(y)
        events["density_floor_events"] += int(np.count_nonzero(rho < .001))
        events["nonpositive_density_events"] += int(np.count_nonzero(rho <= 0))
        events["speed_cap_events"] += int(np.count_nonzero(norm > 20))
        return velocity * np.minimum(1., 20. / np.maximum(norm, 1e-12))

    record(0)
    nsteps = int(round(horizon / dt))
    for i in range(nsteps):
        t = i * dt
        k1 = velocity(x, t)
        k2 = velocity(project(x + .5 * dt * k1), t + .5 * dt)
        k3 = velocity(project(x + .5 * dt * k2), t + .5 * dt)
        k4 = velocity(project(x + dt * k3), t + dt)
        x = project(x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4))
        if i + 1 in wanted:
            record(i + 1)
    return dict(final=x, callback_results=saved_results,
                checkpoint_sampling_seconds=sample_times, checkpoint_times=actual_times,
                sampling_seconds=time.perf_counter() - started - excluded,
                callback_seconds=excluded, events=events,
                requested_horizon=horizon, effective_horizon=nsteps * dt)


def summarize(rows, references, config):
    def mean_sd(values):
        values = list(values)
        return (stats.mean(values), stats.stdev(values) if len(values) > 1 else 0.0)
    summaries = []
    for beta in config["betas"]:
        for method in LABELS:
            group = [row for row in rows if row["beta"] == beta and row["method"] == method]
            valid = [row for row in group if row["status"] == "ok" and row.get("sw2") is not None]
            item = dict(beta=beta, method=method, label=LABELS[method], n_repeats=len(group),
                        successful_runs=len(valid), failure_count=len(group)-len(valid),
                        hit_count=sum(row.get("hit_seconds") is not None for row in group))
            for key, target in [("sw2", "sw2"), ("fit_seconds", "fit_seconds"),
                                ("sample_seconds", "sample_seconds"), ("total_seconds", "total_seconds")]:
                if len(valid) == len(group) and len(group):
                    item[target+"_mean"], item[target+"_std"] = mean_sd(row[key] for row in valid)
                else:
                    item[target+"_mean"] = item[target+"_std"] = None
            hits = [row["hit_seconds"] for row in group if row.get("hit_seconds") is not None]
            item["hit_seconds_mean"], item["hit_seconds_std"] = mean_sd(hits) if hits else (None, None)
            summaries.append(item)
    return dict(config=config, rows=summaries, references=references)


def numerical_provenance(config):
    """Reject mixed protocols, numerical implementations and runtimes on resume."""
    notebook = json.loads((ROOT / "BKT_experiments.ipynb").read_text(encoding="utf-8"))
    definitions = [notebook["cells"][i]["source"] for i in (1, 2, 3, 4)]
    return dict(config=config, python=list(sys.version_info[:3]), numpy=np.__version__, scipy=scipy.__version__,
                runner_sha256=sha(__file__), methods_sha256=sha(ROOT / "supplementary/data_comparison_methods.py"),
                notebook_api_sha256=sha(ROOT / "supplementary/comparison_notebook_api.py"),
                notebook_numerical_cells_sha256=hashlib.sha256(json.dumps(definitions).encode()).hexdigest(),
                source_generator_sha256=hashlib.sha256(inspect.getsource(new_source).encode()).hexdigest())


def run(config_path, resume=False, probe=False, output_directory=None):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    out = (ROOT / (output_directory or config["output_directory"])).resolve()
    if not out.is_relative_to(ROOT):
        raise ValueError("The output directory must be inside the project.")
    out.mkdir(exist_ok=True, parents=True)
    main_out = ROOT / "outputs/admissible_source"
    main_config = json.loads((main_out / "config.json").read_text(encoding="utf-8"))
    for name in ("source_mean_x1", "source_bump_half_width", "source_bump_cdf_grid_points",
                 "source_bump_cdf_first_value", "source_x2_variance", "source_seed_base", "particles"):
        assert config[name] == main_config[name], f"Main-source configuration mismatch: {name}"
    main_rows = json.loads((main_out / "runs.json").read_text(encoding="utf-8"))
    main_records = {(row["beta"], row["seed"]): row for row in main_rows
                    if row["method"] == "RBF" and row["regime"] == "S" and "main" in row["roles"]}
    previous_out = ROOT / "outputs/data_comparison"
    previous_inputs = {(row["beta"], row["seed"]): row for row in
                       json.loads((previous_out / "input_provenance.json").read_text(encoding="utf-8"))}
    previous_config = json.loads((previous_out / "config.json").read_text(encoding="utf-8"))
    source_or_provenance = {"version", "source_mean_x1", "source_bump_half_width", "source_bump_cdf_grid_points",
                            "source_bump_cdf_first_value", "source_x2_variance", "source_generator",
                            "bkt_parity_reference", "resume_policy"}
    for name, value in previous_config.items():
        if name not in source_or_provenance:
            assert config[name] == value, f"A non-source protocol parameter changed: {name}"
    if config.get("version") == 3:
        raise ValueError("The ten-realisation revision uses supplementary/revision_comparison.py. "
                         "Run revision_queue.py for the complete B1--B4 protocol, then revision_publish.py. "
                         "This legacy entry point does not mix its resume records with revision records.")
    assert config["version"] == 2 and config["source_x2_variance"] == .3
    assert config["bkt_step"] == config["kde_step"] == .05 and config["retained_nonconstant_modes"] == 64
    assert config["bkt_density_floor"] == .001 and config["bkt_speed_cap"] == 20
    assert config["langevin_step"] == .002 and config["drift_ridge_after_column_scaling"] == 1e-8
    old = json.loads((ROOT / "outputs/results.json").read_text(encoding="utf-8"))
    baseline_hashes = {key: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
                       for key, value in old.items() if key != "comparison"}
    ns = load_notebook_api(output_dir=ROOT / "outputs", fail_on_cache_miss=True)
    results_path = out / "runs.json"
    if results_path.exists() and not resume:
        raise FileExistsError("Completed run records exist; use --resume to keep them.")
    if probe and results_path.exists():
        raise FileExistsError("Use an empty staging directory for an input probe; existing run records are protected.")
    rows = json.loads(results_path.read_text()) if resume and results_path.exists() else []
    identity = numerical_provenance(config)
    if rows:
        if json.loads((out / "config.json").read_text()) != config:
            raise ValueError("Refusing resume: configuration mismatch.")
        identity_path = out / "numerical_provenance.json"
        if not identity_path.exists() or json.loads(identity_path.read_text()) != identity:
            raise ValueError("Refusing resume: numerical-code or runtime provenance mismatch.")
        for row in rows:
            if row["status"] == "ok":
                with np.load(out / row["endpoint_file"]) as saved:
                    assert array_sha(saved["final"]) == row["endpoint_sha256"], "Changed resume endpoint"
                assert all(isinstance(row.get(key), (int, float)) and row[key] >= 0
                           for key in ("fit_seconds", "sample_seconds", "total_seconds")), "Missing individual timings"
    write_json(out / "config.json", config)
    write_json(out / "numerical_provenance.json", identity)
    references, provenance = [], []
    started = time.perf_counter()

    def persist():
        write_json(results_path, rows)
        write_json(out / "input_provenance.json", provenance)
        partial = summarize(rows, references, config)
        partial["timing_provenance"] = dict(per_run_status="measured", fit_policy="Fresh single-thread fits; drift fitting charged to each baseline")
        write_json(out / "summary.json", partial)

    def save_method(beta, source_index, method, result, fit_seconds, target_threshold, common, extra=None):
        final = result["final"]
        checkpoint_rows = result["callback_results"]
        checkpoint_costs = result["checkpoint_sampling_seconds"]
        last_available_sw = checkpoint_rows[-1]["sw2"]
        failed = result.get("status") == "failed"
        final_sw = None if failed else last_available_sw
        hits = [(rec, cost) for rec, cost in zip(checkpoint_rows, checkpoint_costs)
                if rec["sw2"] is not None and rec["sw2"] <= target_threshold]
        hit = hits[0] if hits and not failed else None
        status = "failed" if failed else "ok" if np.isfinite(final).all() and final_sw is not None else "nonfinite"
        row = dict(beta=beta, seed=source_index, method=method, label=LABELS[method], status=status,
                   sw2=final_sw, last_available_sw2=last_available_sw, failure=result.get("failure"),
                   fit_seconds=fit_seconds, sample_seconds=result["sampling_seconds"],
                   total_seconds=fit_seconds+result["sampling_seconds"],
                   metric_seconds=result["callback_seconds"],
                   hit_seconds=fit_seconds+hit[1] if hit else None,
                   hit_physical_time=hit[0]["time"] if hit else None,
                   threshold=target_threshold, effective_horizon=result.get("effective_horizon"),
                   completed_horizon=result.get("completed_horizon", result.get("effective_horizon")),
                   checkpoint_records=[dict(rec, sampling_seconds=cost, total_seconds=fit_seconds+cost)
                                       for rec, cost in zip(checkpoint_rows, checkpoint_costs)],
                   events=result.get("events", {}), **common, **(extra or {}))
        file = out / f"endpoint_beta{beta:g}_seed{source_index}_{method}.npz"
        np.savez_compressed(file, final=final)
        row["endpoint_file"] = file.name
        row["endpoint_sha256"] = array_sha(final)
        rows.append(row)
        persist()
        display_sw = "failed" if final_sw is None else f"{final_sw:.6g}"
        print(f"beta={beta:g} seed={source_index} {method}: SW2={display_sw}; fit={fit_seconds:.2f}s sample={result['sampling_seconds']:.2f}s; hit={row['hit_seconds']}", flush=True)

    for beta_index, beta in enumerate(config["betas"]):
        key = f"A2_beta{beta}"
        existing = old[key]
        pot = ns["Potential"]("A", d=2, beta=beta)
        reference = existing["reference"]
        assert reference["repetitions"] == 10
        ref = dict(beta=beta, mean=reference["metrics"]["sw"]["mean"],
                   std=reference["metrics"]["sw"]["std"], source="existing ten independent target-cloud pairs",
                   details=reference)
        references.append(ref)
        threshold = ref["mean"] + ref["std"]
        requested = existing["rbf"]["rows"][0]["T"]
        horizon = round(requested / config["bkt_step"]) * config["bkt_step"]
        checkpoints = np.unique(np.r_[np.arange(0., horizon, config["checkpoint_interval"]), horizon])
        t0 = time.perf_counter()
        target = ns["stationary_samples"](pot, config["particles"], np.random.default_rng(config["target_seed"]))
        target_load_seconds = time.perf_counter() - t0
        metric, directions = metric_factory(target, config["projections"], config["projection_seed"])
        for directory in (previous_out, main_out):
            with np.load(directory / f"evaluation_beta{beta:g}.npz") as saved:
                assert np.array_equal(target, saved["target"]), "Evaluation target changed"
                assert np.array_equal(directions, saved["directions"]), "Projection directions changed"
        np.savez_compressed(out / f"evaluation_beta{beta:g}.npz", target=target, directions=directions)

        for source_index in config["source_indices"]:
            t0 = time.perf_counter()
            xd, yd = ns["simulate_pairs"](pot, config["training_pairs"], np.random.default_rng(100+source_index))
            load_seconds = time.perf_counter() - t0
            x0 = new_source(config, config["source_seed_base"]+source_index)
            main_record = main_records[beta, source_index]
            assert main_record["reference_mean"] == ref["mean"] and main_record["reference_std"] == ref["std"]
            assert main_record["T"] == horizon and main_record["r_used"] == 64 and main_record["dt"] == .05
            previous = previous_inputs[beta, source_index]
            with np.load(main_out / main_record["initial_file"]) as saved:
                assert np.array_equal(x0, saved["initial"]), "Source differs from main S experiment"
            hashes = dict(training_x_sha256=array_sha(xd), training_y_sha256=array_sha(yd),
                          source_sha256=array_sha(x0), target_sha256=array_sha(target),
                          directions_sha256=array_sha(directions))
            for name in ("training_x_sha256", "training_y_sha256", "target_sha256"):
                assert hashes[name] == previous[name] == main_record[name], f"Changed fixed input: {name}"
            assert hashes["source_sha256"] == main_record["source_sha256"]
            assert xd.shape == yd.shape == (200000, 2) and x0.shape == target.shape == (2000, 2)
            assert abs(metric(0., x0)["sw2"]-ns["sliced_w2"](x0, target)) < 1e-12
            provenance.append(dict(beta=beta, seed=source_index, **hashes,
                                   source_matches_main=True, fixed_inputs_match_previous=True,
                                   training_load_seconds=load_seconds,
                                   target_load_seconds=target_load_seconds, nominal_horizon=requested,
                                   shared_effective_horizon=horizon))
            if probe:
                print(f"INPUTS OK beta={beta:g} seed={source_index} T={horizon:g}", flush=True)
                continue
            np.savez_compressed(out / f"source_beta{beta:g}_seed{source_index}.npz", initial=x0)
            common = dict(training_pairs_available=200000, training_seed=100+source_index,
                          source_seed=500+source_index, particles=2000, nominal_horizon=requested,
                          source_x2_variance=config["source_x2_variance"], **hashes,
                          shared_horizon=horizon, source_outside_box=int(np.any((x0<pot.box[:,0]) | (x0>pot.box[:,1]),axis=1).sum()))
            done = {row["method"] for row in rows if row["beta"] == beta and row["seed"] == source_index}
            for retained in (row for row in rows if row["beta"] == beta and row["seed"] == source_index):
                assert all(retained.get(name) == value for name, value in hashes.items()), "Resume input mismatch"
            dic = ns["Dictionary"]("rbf", pot, n=12, wfrac=.075)

            if "A" not in done:
                t0 = time.perf_counter()
                fitted = object.__new__(ns["RREstimate"])
                ns["_rr_init"](fitted, dic, xd, yd, chunk=5000)
                fit_seconds = time.perf_counter() - t0
                assert fitted.r_max >= 64 and dic.size() == 145
                result = bkt_instrumented(ns, pot, fitted, x0, horizon, .05, 64, checkpoints, metric)
                existing_sw = main_record["sw2"]
                discrepancy = abs(result["callback_results"][-1]["sw2"] - existing_sw)
                if discrepancy > 2e-9:
                    raise AssertionError(f"BKT does not reproduce the main variance-0.3 result: {discrepancy}")
                with np.load(main_out / main_record["endpoint_file"]) as saved:
                    endpoint_discrepancy = float(np.max(np.abs(result["final"]-saved["final"])))
                assert endpoint_discrepancy < 2e-8, "BKT endpoint differs from main experiment"
                checkpoint_discrepancy = max(abs(new["sw2"]-saved["sw2"]) for new, saved in
                                             zip(result["callback_results"], main_record["checkpoint_records"]))
                assert len(result["callback_results"]) == len(main_record["checkpoint_records"])
                assert checkpoint_discrepancy < 2e-9, "BKT checkpoints differ from main experiment"
                save_method(beta, source_index, "A", result, fit_seconds, threshold, common,
                            dict(existing_bkt_sw2=existing_sw, bkt_parity_absolute_error=discrepancy,
                                 bkt_endpoint_max_absolute_error=endpoint_discrepancy,
                                 bkt_checkpoint_max_absolute_error=checkpoint_discrepancy,
                                 bkt_parity_reference=main_record["run_id"],
                                 dictionary_size=145, rank=64, training_positions_used=200000))
                del fitted, result

            if not {"B", "D"}.issubset(done):
                drift = fit_gradient_drift(dic, xd, yd, tau=.1, ridge=1e-8, chunk=5000)
                write_json(out / f"drift_beta{beta:g}_seed{source_index}.json", drift.diagnostics)
                np.savez_compressed(out / f"drift_beta{beta:g}_seed{source_index}.npz",
                                    coefficients=drift.coefficients, column_rms=drift.column_rms)
                for method in ("B", "D"):
                    if method in done:
                        continue
                    print(f"START beta={beta:g} seed={source_index} {method}", flush=True)
                    try:
                        result = run_baseline(method, x0, drift, horizon, pot.box,
                                              seed=source_index, beta_index=beta_index,
                                              checkpoints=checkpoints, checkpoint_callback=metric)
                        save_method(beta, source_index, method, result, drift.fit_seconds, threshold, common,
                                    dict(drift_diagnostics=drift.diagnostics, training_positions_used=200000,
                                         training_pairs_used_for_fitting=200000))
                    except Exception as error:
                        rows.append(dict(beta=beta, seed=source_index, method=method, label=LABELS[method],
                                         status="failed", error=repr(error), traceback=traceback.format_exc(),
                                         fit_seconds=drift.fit_seconds, sw2=None, hit_seconds=None, **common))
                        persist()
                        print(f"FAILED beta={beta:g} seed={source_index} {method}: {error}", flush=True)
                del drift

    if probe:
        write_json(out / "input_probe.json", provenance)
        return
    expected_count = len(config["betas"])*len(config["source_indices"])*len(config["methods"])
    assert config["methods"] == list(LABELS)
    assert len(rows) == expected_count and len({(r["beta"],r["seed"],r["method"]) for r in rows}) == expected_count
    result = summarize(rows, references, config)
    result["runs"] = rows
    result["timing_provenance"] = dict(per_run_status="measured", fit_policy="Fresh single-thread fits; drift fitting charged to each baseline")
    result["metadata"] = dict(created_utc=datetime.now(timezone.utc).isoformat(), runtime_seconds=time.perf_counter()-started,
                               python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                               threadpools=threadpool_info(), config_sha256=sha(config_path),
                               script_sha256=sha(__file__), methods_sha256=sha(ROOT/'supplementary/data_comparison_methods.py'),
                               notebook_sha256=sha(ROOT/'BKT_experiments.ipynb'),
                               cache_stats=dict(ns.get("STATS", {})))
    write_json(out / "summary.json", result)
    current = json.loads((ROOT / "outputs/results.json").read_text(encoding="utf-8"))
    current_hashes = {key: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
                      for key,value in current.items() if key != "comparison"}
    assert current_hashes == baseline_hashes, "Primary results changed during the comparison."
    print(f"COMPLETED {len(rows)} runs. Numerical failures={sum(r['status']!='ok' for r in rows)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--output-directory", type=Path, help="Stage results within the project without changing the canonical configured path")
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        run(args.config, resume=args.resume, probe=args.probe, output_directory=args.output_directory)


if __name__ == "__main__":
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        main()
