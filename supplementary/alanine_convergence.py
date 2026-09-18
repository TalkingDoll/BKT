"""Reproduce the paired three-method alanine convergence figure.

Spectra, source clouds and reference clouds come from the retained alanine
archive. BKT and LAWGD share 256 nonconstant modes of the static
Fourier/Dirichlet estimate. The KDE-based diffusion-velocity method fits its
fixed target score to the same 250,000 estimation frames and updates only
the density estimate of the moving particles. Both target representations
use wrapped-Gaussian smoothing of 0.1 rad and the same normalized clock;
neither estimates physical MD kinetics from lagged trajectory pairs.

The KDE formulation follows Degond and Mustieles (1990),
doi:10.1137/0911018, and Chertock (2017), Section 4.1.2,
doi:10.1016/bs.hna.2016.11.004. Periodic kernels and the fitted target score
are adaptations for this experiment. No parameter search is performed.
"""
from __future__ import annotations
import os
for _name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
import hashlib
import inspect
import io
import json
from pathlib import Path
import time
import numpy as np
from scipy.integrate import DOP853
from threadpoolctl import threadpool_limits
import alanine_experiment as alanine
from manuscript_results import read_bytes,ALANINE_DISPLAY_HORIZON,ALANINE_METHOD_LABELS

ROOT=Path(__file__).resolve().parents[1]
LOGICAL='alanine/lawgd_convergence.npz'
RANKS=(256,)
SEEDS=(1101,1102,1103)
METHODS=('BKT','LAWGD','KDE')
CASES=((256,'BKT'),(256,'LAWGD'),(None,'KDE'))
TIMES=np.unique(np.round(np.r_[np.arange(0,.20001,.01),np.arange(.25,8.00001,.05)],12))
SPEC=dict(ranks=RANKS,seeds=SEEDS,methods=METHODS,particles=1000,
          times=TIMES.tolist(),rtol=1e-8,atol=1e-10,max_step=.05,
          first_step_raw=.0001,raw_bkt_speed_cap=20.,bkt_ratio_floor=.001,
          maximum_seconds=1200.,maximum_evaluations=150000,
          clock='All methods use the same lambda1 and surrogate mobility I/lambda1; s is normalized flow time, not physical MD time or CPU time.',
          coefficients='BKT and LAWGD use the same empirical initial moments. BKT freezes them; LAWGD updates the current particle moments.',
          safeguards='BKT and LAWGD use the same normalized speed cap20/lambda1. Only BKT has a density denominator and its floor. KDE has no drift cap. Counts include trial stages.',
          evaluation='Three paired Sobol/reference designs share one fitted spectrum; variability is not across independent MD datasets.',
          figure='Full interval 0..8, all three methods and three seeds; mean and sample SD. Actual checkpoint clouds, no fitted or smoothed curve.',
          baseline_target=dict(grid_size=512,smoothing=.1),
          kde=dict(bandwidth=.1,rtol=1e-6,atol=1e-8,first_step_raw=1e-5,
                   normalized_max_step=.05,maximum_seconds=7200.,maximum_evaluations=1000000),
          retained_dictionary='The 256 retained modes use a degree-28, 3249-function Fourier dictionary.')


def sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def inputs():
    payload=read_bytes('alanine/results.npz')
    with np.load(io.BytesIO(payload)) as z:
        data={k:z[k] for k in z.files}
    data['record']=json.loads(str(data['record']))
    data['archive_member_sha256']=hashlib.sha256(payload).hexdigest()
    return data,alanine.FourierDictionary(data['record']['setting']['degree'])


def geometry(dic,x):
    f=np.arange(1,dic.degree+1)
    a=x[:,0,None]*f;b=x[:,1,None]*f
    ca,sa,cb,sb=np.cos(a),np.sin(a),np.cos(b),np.sin(b)
    one=np.ones(len(x));zero=np.zeros(len(x))
    return (np.column_stack([one,ca,sa]),np.column_stack([one,cb,sb]),
            np.column_stack([zero,-sa*f,ca*f]),np.column_stack([zero,-sb*f,cb*f]))


def mean_features(dic,geo):
    u,v,_,_=geo;cross=u.T@v/len(u);k=dic.degree;f=dic.freq
    a,b=abs(f[:,0]),abs(f[:,1]);sa,sb=np.sign(f[:,0]),np.sign(f[:,1])
    real=cross[a,b]-sa*sb*cross[k+a,k+b]
    imag=sa*cross[k+a,b]+sb*cross[a,k+b]
    return np.r_[1.,np.sqrt(2)*real,np.sqrt(2)*imag]


def contract(dic,coef,geo):
    u,v,du,dv=geo;k=dic.degree;n=len(dic.freq);f=dic.freq
    a,b=abs(f[:,0]),abs(f[:,1]);sa,sb=np.sign(f[:,0]),np.sign(f[:,1])
    c,s=np.sqrt(2)*coef[1:1+n],np.sqrt(2)*coef[1+n:]
    matrix=np.zeros((2*k+1,2*k+1))
    np.add.at(matrix,(a,b),c);np.add.at(matrix,(k+a,k+b),-c*sa*sb)
    np.add.at(matrix,(k+a,b),s*sa);np.add.at(matrix,(a,k+b),s*sb)
    uv=u@matrix
    return (1+coef[0]+np.sum(uv*v,axis=1),
            np.column_stack([np.sum((du@matrix)*v,axis=1),np.sum(uv*dv,axis=1)]))


def metrics(x,target,centers):
    def mass(y):
        e=alanine.embed(y,True)
        label=np.argmin(((e[:,None]-centers[None])**2).sum(2),axis=1)
        return np.bincount(label,minlength=4)/len(y)
    m=mass(x)
    return dict(sw2=alanine.sw2(x,target,True),mass_tv=float(.5*abs(m-mass(target)).sum()),masses=m.tolist())


def checks(data,dic):
    errors=[]
    for rank in RANKS:
        b=np.ascontiguousarray(data['basis'][:,:rank]);lam=data['lam'][:rank]
        for name in ('source','target'):
            x=data[name][0,:17];geo=geometry(dic,x);p,dp=dic.eval(x)
            np.testing.assert_allclose(mean_features(dic,geo),p.mean(0),atol=2e-13,rtol=2e-13)
            coef=b@((mean_features(dic,geo)@b)/lam)
            rho,grad=contract(dic,coef,geo);r0,g0=dic.contract(x,coef)
            np.testing.assert_allclose(rho,r0,atol=1e-9,rtol=1e-10)
            np.testing.assert_allclose(grad,g0,atol=1e-9,rtol=1e-10)
            phi=p@b;gphi=np.einsum('mid,ik->mkd',dp,b,optimize=True)
            direct=-np.einsum('ikd,jk,k->ijd',gphi,phi,1/lam,optimize=True).mean(1)
            np.testing.assert_allclose(-grad,direct,atol=1e-7,rtol=1e-8)
            errors.append(dict(rank=rank,cloud=name,explicit_kernel_error=float(abs(grad+direct).max())))
    return errors


def transport(data,dic,rank,method,seed):
    i=data['record']['seeds'].index(seed);source,target=data['source'][i],data['target'][i]
    b=np.ascontiguousarray(data['basis'][:,:rank]);lam=data['lam'][:rank]
    l1=float(data['lam'][0]);cap=SPEC['raw_bkt_speed_cap']/l1
    initial=mean_features(dic,geometry(dic,source))@b
    events=dict(nfev=0,point_evaluations=0,nonpositive_density=0,density_floor=0,speed_cap=0,
                minimum_density_ratio=None,maximum_uncapped_normalized_speed=0.)
    rows=[];clouds=[];excluded_cpu=excluded_wall=0.
    wall0=time.perf_counter();cpu0=time.process_time();last_progress=wall0
    def rhs(s,flat):
        if events['nfev']>=SPEC['maximum_evaluations'] or time.perf_counter()-wall0-excluded_wall>SPEC['maximum_seconds']:
            raise RuntimeError('Resource limit reached; no completed endpoint is claimed.')
        x=flat.reshape(source.shape);geo=geometry(dic,x)
        if method=='BKT':
            weights=initial*np.exp(-(lam/l1)*s)
            nz=np.flatnonzero(weights);stop=int(nz[-1])+1 if len(nz) else 0
            coef=b[:,:stop]@weights[:stop];rho,grad=contract(dic,coef,geo)
            velocity=-grad/(np.maximum(rho,SPEC['bkt_ratio_floor'])*l1)[:,None]
            events['nonpositive_density']+=int((rho<=0).sum())
            events['density_floor']+=int((rho<SPEC['bkt_ratio_floor']).sum())
            old=events['minimum_density_ratio'];value=float(rho.min())
            events['minimum_density_ratio']=value if old is None else min(old,value)
        else:
            current=mean_features(dic,geo)@b
            velocity=-contract(dic,b@(current/lam),geo)[1]
        norm=np.linalg.norm(velocity,axis=1)
        if not np.isfinite(velocity).all():raise FloatingPointError('Nonfinite field.')
        events['maximum_uncapped_normalized_speed']=max(events['maximum_uncapped_normalized_speed'],float(norm.max()))
        events['speed_cap']+=int((norm>cap).sum())
        velocity*=np.minimum(1,cap/np.maximum(norm,1e-12))[:,None]
        events['nfev']+=1;events['point_evaluations']+=len(x)
        return velocity.ravel()
    def checkpoint(s,flat):
        nonlocal excluded_cpu,excluded_wall
        row=dict(s=float(s),cpu_seconds=time.process_time()-cpu0-excluded_cpu,
                 wall_seconds=time.perf_counter()-wall0-excluded_wall,nfev=events['nfev'])
        w=time.perf_counter();c=time.process_time()
        x=alanine.wrap(flat.reshape(source.shape));clouds.append(x.copy())
        row.update(metrics(x,target,data['cluster_centers']));rows.append(row)
        if s in (0.,.1,.5,1.,2.,3.,4.,6.,8.,10.):
            print(f'CHECK {method} r={rank} seed={seed} s={s:g} SW2={row["sw2"]:.8f}',flush=True)
        excluded_wall+=time.perf_counter()-w;excluded_cpu+=time.process_time()-c
    checkpoint(0.,source);cursor=1;solver=None;failure=None
    try:
        solver=DOP853(rhs,0.,source.ravel(),float(TIMES[-1]),rtol=SPEC['rtol'],atol=SPEC['atol'],
                      first_step=SPEC['first_step_raw']*l1,max_step=SPEC['max_step'])
        while solver.status=='running':
            message=solver.step()
            if solver.status=='failed':raise RuntimeError(str(message))
            if cursor<len(TIMES) and TIMES[cursor]<=solver.t+1e-12:
                interpolation=solver.dense_output()
                while cursor<len(TIMES) and TIMES[cursor]<=solver.t+1e-12:
                    checkpoint(TIMES[cursor],interpolation(TIMES[cursor]));cursor+=1
            if time.perf_counter()-last_progress>=25:
                print(f'PROGRESS {method} r={rank} seed={seed} s={solver.t:.6g} nfev={events["nfev"]}',flush=True)
                last_progress=time.perf_counter()
    except (RuntimeError,FloatingPointError) as exc:
        failure=str(exc)
    row=dict(method=method,rank=rank,seed=seed,status='ok' if failure is None and cursor==len(TIMES) else 'incomplete',
             failure=failure,completed_s=float(solver.t) if solver else 0.,checkpoints=rows,events=events,
             cpu_seconds=time.process_time()-cpu0-excluded_cpu,wall_seconds=time.perf_counter()-wall0-excluded_wall,
             source_sha256=sha(source),target_sha256=sha(target),initial_empirical_moments_sha256=sha(initial))
    return row,np.asarray(clouds)


def numerical_fingerprint():
    functions=(geometry,mean_features,contract,metrics,checks,transport,
               run_baseline,validate_baseline,baseline_row)
    source='\n'.join(inspect.getsource(f) for f in functions)+json.dumps(SPEC,sort_keys=True)
    source+=Path(__file__).with_name('alanine_baselines.py').read_text(encoding='utf-8')
    return hashlib.sha256(source.encode()).hexdigest()


def save(path,record,arrays):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.pending.npz')
    np.savez(temporary,record=json.dumps(record,allow_nan=False),**arrays)
    temporary.replace(path)


def load_results():
    with np.load(io.BytesIO(read_bytes(LOGICAL))) as z:
        return json.loads(str(z['record'])),{k:z[k] for k in z.files if k!='record'}


def case_id(rank,method,seed):
    return f'r{rank}_{method}_s{seed}' if rank is not None else f'{method}_s{seed}'


def baseline_fit():
    """Fit the fixed target KDE to the spectrum's estimation frames.

    This offline fit is separate from the evolving current-particle KDE in
    run_kde. Its grid/spline approximation and the Fourier/Galerkin spectrum
    target the same smoothed empirical law with different numerical errors.
    The data hash below prevents reuse of a fit from another training set.
    """
    import alanine_baselines as baselines
    path=ROOT/'tmp/alanine_comparison/target_fit.npz'
    if path.exists():
        with np.load(path) as z:
            fit={k:z[k] for k in z.files if k not in ('metadata','record')}
            fit['metadata']=json.loads(str(z['metadata'] if 'metadata' in z.files else z['record']))
    else:
        with np.load(io.BytesIO(read_bytes('alanine/dataset.npz'))) as z:
            fit=baselines.fit_target(z['train_all'],**SPEC['baseline_target'])
        path.parent.mkdir(parents=True,exist_ok=True)
        np.savez(path,metadata=json.dumps(fit['metadata']),
                 **{k:v for k,v in fit.items() if k!='metadata'})
    with np.load(io.BytesIO(read_bytes('alanine/dataset.npz'))) as z:
        assert fit['metadata']['train_sha256']==sha(z['train_all'])
    for k,v in SPEC['baseline_target'].items():assert fit['metadata'][k]==v
    assert fit['metadata']['coefficient_sha256']==sha(fit['log_density_coefficients'])
    return fit


def provenance(data,dic):
    result=dict(spec=SPEC,lambda1=float(data['lam'][0]),degree=dic.degree,
                source_archive_member_sha256=data['archive_member_sha256'],
                numerical_code_sha256=numerical_fingerprint(),
                spectra={str(r):dict(lam=sha(data['lam'][:r]),basis=sha(data['basis'][:,:r])) for r in RANKS})
    return json.loads(json.dumps(result,allow_nan=False))


def import_spectral_runs(seed,data):
    """Reuse byte-identical prescribed spectral trajectories; never select by outcome."""
    payload=read_bytes(LOGICAL)
    with np.load(io.BytesIO(payload)) as z:
        old=json.loads(str(z['record']));selected=[];arrays={}
        assert old['provenance']['source_archive_member_sha256']==data['archive_member_sha256']
        old_spec=old['provenance']['spec']
        np.testing.assert_array_equal(old_spec['times'][:len(TIMES)],TIMES)
        for key in ('particles','rtol','atol','max_step','first_step_raw','raw_bkt_speed_cap','bkt_ratio_floor'):
            assert old_spec[key]==SPEC[key],f'Cannot reuse changed spectral control {key}'
        for rank,method in CASES[:2]:
            key=case_id(rank,method,seed)
            row=next((r for r in old['runs'] if r['id']==key),None)
            if row is None or row['status']!='ok':continue
            assert old['provenance']['spectra'][str(rank)]==dict(
                lam=sha(data['lam'][:rank]),basis=sha(data['basis'][:,:rank]))
            original_horizon=row.get('reused_from',{}).get('original_horizon',old_spec['times'][-1])
            row['reused_from']=dict(archive_member_sha256=hashlib.sha256(payload).hexdigest(),
                                   numerical_code_sha256=old['provenance']['numerical_code_sha256'],
                                   original_horizon=original_horizon,
                                   note='Exact saved prefix; event counters refer to the original integration horizon.')
            row['checkpoints']=row['checkpoints'][:len(TIMES)]
            row['completed_s']=float(TIMES[-1])
            row['cpu_seconds']=row['checkpoints'][-1]['cpu_seconds']
            row['wall_seconds']=row['checkpoints'][-1]['wall_seconds']
            selected.append(row);arrays[key+'_clouds']=z[key+'_clouds'][:len(TIMES)]
    return selected,arrays


def run_baseline(data,fit,method,seed):
    import alanine_baselines as baselines
    i=data['record']['seeds'].index(seed);source,target=data['source'][i],data['target'][i]
    assert method=='KDE'
    diagnostic,clouds=baselines.run_kde(source,fit,float(data['lam'][0]),TIMES,seed,**SPEC['kde'])
    return baseline_row(data,method,seed,diagnostic,clouds)


def validate_baseline(data,method,seed,diagnostic,clouds):
    count=int(diagnostic['completed_checkpoints'])
    assert 1<=count<=len(TIMES) and len(diagnostic['checkpoints'])==count
    assert diagnostic['lambda1']==float(data['lam'][0])
    np.testing.assert_array_equal(diagnostic['requested_times'],TIMES)
    np.testing.assert_array_equal([c['s'] for c in diagnostic['checkpoints']],TIMES[:count])
    assert clouds.shape in ((count,SPEC['particles'],2),(len(TIMES),SPEC['particles'],2))
    assert np.isfinite(clouds[:count]).all()
    i=data['record']['seeds'].index(seed)
    assert diagnostic['source_sha256']==sha(data['source'][i])
    np.testing.assert_array_equal(clouds[0],data['source'][i])
    assert method=='KDE' and diagnostic['seed']==seed and diagnostic['drift_cap'] is None
    for key,value in SPEC['kde'].items():
        actual=diagnostic[key] if key.startswith('maximum_') else diagnostic['numerical_parameters'][key]
        assert actual==value,f'Mismatched KDE control {key}'


def baseline_row(data,method,seed,diagnostic,clouds):
    validate_baseline(data,method,seed,diagnostic,clouds)
    i=data['record']['seeds'].index(seed);source,target=data['source'][i],data['target'][i]
    count=int(diagnostic['completed_checkpoints']);clouds=clouds[:count]
    checkpoints=[]
    for s,x,c in zip(TIMES,clouds,diagnostic['checkpoints']):
        checkpoints.append({**c,'s':float(s),**metrics(x,target,data['cluster_centers'])})
    row=dict(id=case_id(None,method,seed),method=method,rank=None,seed=seed,
             status='ok' if diagnostic['status']=='ok' and count==len(TIMES) else 'incomplete',
             failure=None if diagnostic['status']=='ok' else diagnostic['status'],
             completed_s=float(TIMES[count-1]),checkpoints=checkpoints,
             cpu_seconds=diagnostic['transport_cpu_seconds'],wall_seconds=diagnostic['transport_wall_seconds'],
             source_sha256=sha(source),target_sha256=sha(target),baseline_diagnostics=diagnostic)
    return row,clouds


def run(seed,recompute_spectral=False,selected_method=None):
    data,dic=inputs();fit=baseline_fit();path=ROOT/f'tmp/alanine_comparison/seed{seed}.npz'
    protocol=provenance(data,dic)
    if path.exists():
        with np.load(path) as z:
            record=json.loads(str(z['record']));arrays={k:z[k] for k in z.files if k!='record'}
        if record['provenance']!=protocol:raise ValueError('Existing shard has a different protocol.')
    else:
        rows,arrays=([],{}) if recompute_spectral else import_spectral_runs(seed,data)
        record=dict(provenance=protocol,checks=checks(data,dic),baseline_fit=fit['metadata'],runs=rows)
        save(path,record,arrays)
    for rank,method in CASES:
        if selected_method is not None and method!=selected_method:continue
        key=case_id(rank,method,seed)
        if any(r['id']==key for r in record['runs']):continue
        print(f'START {method} seed={seed}',flush=True)
        if rank is not None:row,clouds=transport(data,dic,rank,method,seed)
        else:
            staged=ROOT/f'tmp/alanine_comparison/{method.lower()}_seed{seed}.npz'
            if staged.exists():
                with np.load(staged) as z:
                    diagnostic=json.loads(str(z['record']));clouds=z['clouds']
                assert diagnostic['target_coefficient_sha256']==fit['metadata']['coefficient_sha256']
                assert diagnostic['source_sha256']==sha(data['source'][data['record']['seeds'].index(seed)])
                row,clouds=baseline_row(data,method,seed,diagnostic,clouds)
            else:row,clouds=run_baseline(data,fit,method,seed)
        row['id']=key;record['runs'].append(row);arrays[key+'_clouds']=clouds
        save(path,record,arrays)
        print(f'DONE {method} seed={seed} {row["status"]} SW2={row["checkpoints"][-1]["sw2"]:.8f}',flush=True)


def verify(record=None,arrays=None):
    if record is None:record,arrays=load_results()
    data,dic=inputs();expected={(r,m,s) for r,m in CASES for s in SEEDS}
    actual={(r['rank'],r['method'],r['seed']) for r in record['runs']}
    if len(record['runs'])!=len(expected) or actual!=expected:raise ValueError('Incomplete or duplicate run grid.')
    assert record['provenance']==provenance(data,dic)
    with np.load(io.BytesIO(read_bytes('alanine/dataset.npz'))) as z:
        assert record['baseline_fit']['train_sha256']==sha(z['train_all'])
    assert record['baseline_fit']['coefficient_sha256']==sha(arrays['target_log_density_coefficients'])
    checked=0;maximum_error=0.;complete_runs=0;incomplete_runs=[]
    for row in record['runs']:
        count=len(row['checkpoints'])
        assert 1<=count<=len(TIMES) and row['completed_s']==TIMES[count-1]
        if row['status']=='ok':
            assert count==len(TIMES)
            complete_runs+=1
        else:
            assert row['status']=='incomplete' and row['rank'] is None
            assert row['baseline_diagnostics']['status'] in ('resource_limit','numerical_failure','nonfinite_particles','incomplete')
            incomplete_runs.append(dict(id=row['id'],last_checkpoint=row['completed_s'],failure=row['failure']))
        assert row['id']==case_id(row['rank'],row['method'],row['seed'])
        i=data['record']['seeds'].index(row['seed']);cloud=arrays[row['id']+'_clouds']
        assert cloud.shape==(count,SPEC['particles'],2) and np.isfinite(cloud).all()
        if row['rank'] is not None:
            b=np.ascontiguousarray(data['basis'][:,:row['rank']])
            initial=mean_features(dic,geometry(dic,data['source'][i]))@b
            assert row['initial_empirical_moments_sha256']==sha(initial)
        else:
            diagnostic=row['baseline_diagnostics']
            validate_baseline(data,row['method'],row['seed'],diagnostic,cloud)
            assert diagnostic['target_coefficient_sha256']==record['baseline_fit']['coefficient_sha256']
            executed=diagnostic.get('executed_module_sha256',diagnostic.get('module_sha256'))
            if executed is not None:
                assert executed==hashlib.sha256(Path(__file__).with_name('alanine_baselines.py').read_bytes()).hexdigest()
            if 'source_archive_member_sha256' in diagnostic:
                assert diagnostic['source_archive_member_sha256']==data['archive_member_sha256']
        assert row['source_sha256']==sha(data['source'][i]) and row['target_sha256']==sha(data['target'][i])
        np.testing.assert_array_equal(cloud[0],data['source'][i])
        np.testing.assert_allclose([c['s'] for c in row['checkpoints']],TIMES[:count],atol=0,rtol=0)
        for c,x in zip(row['checkpoints'],cloud):
            fresh=metrics(x,data['target'][i],data['cluster_centers'])
            if not np.isfinite([c['sw2'],c['mass_tv']]).all():raise ValueError('Nonfinite saved metric.')
            np.testing.assert_array_equal(c['masses'],fresh['masses'])
            error=max(abs(c[k]-fresh[k]) for k in ('sw2','mass_tv'))
            maximum_error=max(maximum_error,error);checked+=1
    expected_arrays={r['id']+'_clouds' for r in record['runs']}|{'target_log_density_coefficients','target_density'}
    assert set(arrays)==expected_arrays,'Unexpected or obsolete result arrays'
    if maximum_error>1e-12:raise ValueError('Saved metric mismatch.')
    assert record['distribution']==alanine.distribution_summary(data,record,arrays)
    return dict(checkpoints=checked,maximum_metric_error=maximum_error,runs=len(record['runs']),
                complete_runs=complete_runs,incomplete_runs=incomplete_runs)


def collect():
    import platform
    import scipy
    import numba
    record=None;arrays={};fit=baseline_fit()
    for seed in SEEDS:
        path=ROOT/f'tmp/alanine_comparison/seed{seed}.npz'
        with np.load(path) as z:
            part=json.loads(str(z['record']))
            if record is None:
                record=dict(provenance=part['provenance'],checks=part['checks'],baseline_fit=fit['metadata'],runs=[])
            elif part['provenance']!=record['provenance']:raise ValueError('Shard protocol mismatch.')
            record['runs'].extend(part['runs']);arrays.update({k:z[k] for k in z.files if k!='record'})
    arrays.update(target_log_density_coefficients=fit['log_density_coefficients'],target_density=fit['density'])
    record['baseline_numerical_checks']={}
    previous,_=load_results()
    if (previous['provenance'].get('numerical_code_sha256')==record['provenance']['numerical_code_sha256']
        and previous.get('baseline_fit',{}).get('coefficient_sha256')==fit['metadata']['coefficient_sha256']):
        record['baseline_numerical_checks']=previous.get('baseline_numerical_checks',{}).copy()
        if previous.get('provenance')==record['provenance'] and 'reproduction_check' in previous:
            record['reproduction_check']=previous['reproduction_check']
    for name in ('kde_checks',):
        path=ROOT/f'tmp/alanine_comparison/{name}.json'
        if path.exists():record['baseline_numerical_checks'][name]=json.loads(path.read_text(encoding='utf-8'))
    data,_=inputs()
    record['distribution']=alanine.distribution_summary(data,record,arrays)
    record['verification']=verify(record,arrays)
    record['software']=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,numba=numba.__version__,
                            imported_alanine_code_sha256=hashlib.sha256(Path(alanine.__file__).read_bytes()).hexdigest())
    data,_=inputs()
    record['references']=[dict(seed=s,**metrics(data['reference_a'][i],data['reference_b'][i],data['cluster_centers']))
                          for i,s in enumerate(SEEDS)]
    save(ROOT/'outputs'/LOGICAL,record,arrays)
    print(json.dumps(record['verification']),flush=True)


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator,FuncFormatter,NullLocator
    from figure_style import configure_style,FONT_SIZES
    record,_=load_results()
    configure_style('fig_alanine_convergence',17.)
    fig,ax=plt.subplots(figsize=(17.,10.))
    fig.subplots_adjust(left=.16,right=.982,bottom=.35,top=.96)
    colors={'BKT':'#0072B2','LAWGD':'#D55E00','KDE':'#009E73'}
    styles={'BKT':'-','LAWGD':'--','KDE':'-.'}
    labels=ALANINE_METHOD_LABELS
    display_times=TIMES[TIMES<=ALANINE_DISPLAY_HORIZON]
    if not len(display_times) or display_times[-1]!=ALANINE_DISPLAY_HORIZON:
        raise ValueError('The displayed endpoint must be a retained checkpoint.')
    lower=[];upper=[]
    for method in METHODS:
        rows=sorted((r for r in record['runs'] if r['method']==method),key=lambda r:r['seed'])
        if [r['seed'] for r in rows]!=list(SEEDS):raise ValueError('Missing prescribed seed.')
        count=min(len(display_times),*(len(r['checkpoints']) for r in rows))
        if count<2:
            print(f'OMITTED {method}: no nonzero checkpoint shared by all prescribed seeds.',flush=True)
            continue
        shown_times=display_times[:count]
        values=np.array([[c['sw2'] for c in r['checkpoints'][:count]] for r in rows])
        mean,std=values.mean(0),values.std(0,ddof=1)
        lower.extend(mean-std);upper.extend(mean+std)
        ax.fill_between(shown_times,mean-std,mean+std,color=colors[method],alpha=.11,linewidth=0,zorder=1)
        label=labels[method]+(' (partial)' if count<len(display_times) else '')
        ax.plot(shown_times,mean,styles[method],color=colors[method],label=label,zorder=3)
        if count<len(display_times):
            ax.plot(shown_times[-1],mean[-1],marker='x',color=colors[method],linestyle='none',zorder=4)
    if min(lower)<=0:raise ValueError('SD band requires a nonlogarithmic scale.')
    ylow=min(.025,.9*min(lower));yhigh=max(.75,1.05*max(upper))
    ax.set_xlabel(r'Normalized flow time $s$');ax.set_ylabel(r'Sliced $W_2$ to target')
    margin=.01*ALANINE_DISPLAY_HORIZON
    xlimits=[-margin,ALANINE_DISPLAY_HORIZON+margin]
    ax.set_xlim(*xlimits);ax.set_ylim(ylow,yhigh);ax.set_yscale('log')
    ax.set_xticks(np.arange(0.,ALANINE_DISPLAY_HORIZON+1e-12,2.))
    ticks=[v for v in (.01,.02,.03,.05,.1,.2,.5,1.,2.,5.) if ylow<=v<=yhigh]
    ax.yaxis.set_major_locator(FixedLocator(ticks));ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'))
    ax.yaxis.set_minor_locator(NullLocator());ax.grid(axis='y',color='#DFE3E8',linewidth=.75,zorder=0)
    ax.set_axisbelow(True)
    handles,legend_labels=ax.get_legend_handles_labels()
    legend=fig.legend(handles,legend_labels,ncol=len(handles),loc='lower center',bbox_to_anchor=(.5,.018),
                      frameon=False,handlelength=2.2,columnspacing=1.3)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    boxes=[ax.get_tightbbox(renderer),legend.get_window_extent(renderer)]
    if not all(b.x0>=-1 and b.y0>=-1 and b.x1<=fig.bbox.width+1 and b.y1<=fig.bbox.height+1 for b in boxes):
        raise ValueError(f'Figure text outside canvas: {[b.bounds for b in boxes]}; canvas {fig.bbox.bounds}.')
    if boxes[1].y1>=boxes[0].y0:raise ValueError('Legend overlaps axes labels.')
    path=ROOT/'outputs/figures/fig_alanine_convergence.pdf';path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,metadata={'Title':'Paired alanine convergence','Author':'',
                              'Subject':f'{len(handles)} plotted methods, three paired designs, normalized flow time 0 to {ALANINE_DISPLAY_HORIZON:g}; 256 shared modes for BKT and LAWGD.'})
    plt.close(fig)
    print(json.dumps(dict(path=str(path),font_sizes=FONT_SIZES,axes_limits=[xlimits,[ylow,yhigh]],
                          display_horizon=ALANINE_DISPLAY_HORIZON,legend_labels=legend_labels,
                          intended_latex_width='0.62textwidth',global_title=False,mean_and_sample_sd=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=['run','collect','verify','plot'],required=True)
    parser.add_argument('--seed',type=int,choices=SEEDS)
    parser.add_argument('--method',choices=METHODS,help='Run only this method; matching archived spectral clouds remain reusable.')
    parser.add_argument('--recompute-spectral',action='store_true',help='Recompute the prescribed spectral runs instead of reusing archived clouds.')
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        if args.stage=='run':
            if args.seed is None:parser.error('--seed is required for run')
            run(args.seed,args.recompute_spectral,args.method)
        elif args.stage=='collect':collect()
        elif args.stage=='plot':plot()
        else:print(json.dumps(verify()),flush=True)

