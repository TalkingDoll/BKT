"""Fresh single-thread equal-data comparison on the ten prescribed sources."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):os.environ[key]='1'
import json,platform,time,traceback
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from revision_common import ROOT,OUT,api,baseline_records,write_json,save_run,load_run,array_sha,row_count,record_execution
from revision_synthetic import collect,parity
from run_admissible_source import new_source
from run_data_comparison import bkt_instrumented,metric_factory,LABELS,summarize
from data_comparison_methods import fit_gradient_drift,run_baseline

def run():
    before=row_count('comparison');start=time.perf_counter();ns=api();old=baseline_records()['outputs/data_comparison/summary.json']
    cfg=dict(old['config'],source_indices=list(range(10)),version=3,output_directory='outputs/revision/comparison')
    cfg['resume_policy']='Reuse atomically saved prescribed revision rows by run identity. Numerical settings are frozen; changed settings or runtime require a separate revision dataset. Original measurements used fresh fits and transports, not historical aggregate timings.'
    write_json(OUT/'comparison_config.json',cfg);records=[]
    for beta_index,beta in enumerate(cfg['betas']):
        pot=ns['Potential']('A',d=2,beta=beta);target=ns['stationary_samples'](pot,2000,np.random.default_rng(7))
        metric,directions=metric_factory(target);reference=next(r for r in old['references'] if r['beta']==beta)
        threshold=reference['mean']+reference['std'];T=10.7 if beta==0 else 9.4
        times=np.unique(np.r_[np.arange(0.,T,.5),T])
        for seed in range(10):
            if all(load_run('comparison',f'beta{beta:g}_seed{seed}_{m}') for m in LABELS):continue
            xd,yd=ns['simulate_pairs'](pot,200000,np.random.default_rng(100+seed));source=new_source(cfg,500+seed)
            dic=ns['Dictionary']('rbf',pot,n=12,wfrac=.075);drift=None
            for method in LABELS:
                key=f'beta{beta:g}_seed{seed}_{method}'
                if load_run('comparison',key):continue
                print('COMPARISON START',key,flush=True)
                try:
                    if method=='A':
                        tick=time.perf_counter();est=object.__new__(ns['RREstimate']);ns['_rr_init'](est,dic,xd,yd,chunk=5000)
                        fit=time.perf_counter()-tick
                        result=bkt_instrumented(ns,pot,est,source,T,.05,64,times,metric)
                    else:
                        if drift is None:drift=fit_gradient_drift(dic,xd,yd,tau=.1,ridge=1e-8,chunk=5000)
                        fit=drift.fit_seconds
                        result=run_baseline(method,source,drift,T,pot.box,seed=seed,beta_index=beta_index,
                                            checkpoints=times,checkpoint_callback=metric)
                    cp=[dict(c,sampling_seconds=t,total_seconds=fit+t) for c,t in zip(result['callback_results'],result['checkpoint_sampling_seconds'])]
                    hits=[c for c in cp if c['sw2'] is not None and c['sw2']<=threshold]
                    good=result.get('status')!='failed' and np.isfinite(result['final']).all()
                    checks=None
                    if seed<5:
                        previous=next(r for r in old['runs'] if r['beta']==beta and r['seed']==seed and r['method']==method)
                        with np.load(ROOT/'outputs/data_comparison'/previous['endpoint_file']) as z:checks=parity(result['final'],z['final'])
                    row=dict(id=key,beta=beta,seed=seed,method=method,label=LABELS[method],status='ok' if good else 'failed',
                        sw2=cp[-1]['sw2'] if good else None,fit_seconds=fit,sample_seconds=result['sampling_seconds'],
                        total_seconds=fit+result['sampling_seconds'],metric_seconds=result['callback_seconds'],
                        hit_seconds=hits[0]['total_seconds'] if hits and good else None,
                        hit_physical_time=hits[0]['time'] if hits and good else None,checkpoint_records=cp,
                        threshold=threshold,T=T,parity=checks,source_sha256=array_sha(source),target_sha256=array_sha(target),
                        training_x_sha256=array_sha(xd),training_y_sha256=array_sha(yd),events=result.get('events',{}),source_x2_variance=.3)
                    save_run('comparison',key,row,dict(final=result['final']))
                except (FloatingPointError,np.linalg.LinAlgError) as exc:
                    row=dict(id=key,beta=beta,seed=seed,method=method,label=LABELS[method],status='failed',sw2=None,
                             error=repr(exc),traceback=traceback.format_exc(),hit_seconds=None)
                    save_run('comparison',key,row,{})
                records=collect('comparison');summary=summarize(records,old['references'],cfg)
                summary.update(runs=records,timing_provenance=dict(per_run_status='measured',threads=1))
                write_json(OUT/'comparison_summary.json',summary)
                print('COMPARISON',key,row['sw2'],row.get('total_seconds'),row['status'],flush=True)
    record_execution('comparison',time.perf_counter()-start,before,row_count('comparison'),threadpools=threadpool_info(),
        hardware=platform.uname()._asdict(),processor=platform.processor(),logical_cpus=os.cpu_count(),
        timing='Fresh fits and sampling; shared drift fit charged to both baselines; excludes input generation and metric callbacks')
    print('COMPARISON COMPLETE',flush=True)

if __name__=='__main__':
    from experiment_store import managed_outputs
    with managed_outputs('double_well'),threadpool_limits(limits=1):run()
