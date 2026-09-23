"""Fixed B1/B2 synthetic repetitions and B4 path diagnostics; no tuning."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):os.environ[key]='1'
import argparse,json,time,traceback
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from revision_common import (ROOT,OUT,api,definitions,current_records,write_json,array_sha,
                             save_run,load_run,finish_diagnostics,summarize,empirical_sw2,row_count,record_execution)
from run_admissible_source import new_source,specifications,run_id,instrumented_transport,metric_function

def parity(x,old):
    error=float(np.max(np.abs(x-old)))
    return dict(endpoint_bitwise_equal=bool(np.array_equal(x,old)),endpoint_max_absolute_difference=error,
                passes_1e12=error<=1e-12)

def completed(folder,key):
    return load_run(folder,key) is not None

def collect(folder):
    rows=[]
    for p in sorted((OUT/folder).glob('*.npz')):
        if p.name.endswith('.pending.npz'):continue
        with np.load(p) as z:
            if 'record' in z:rows.append(json.loads(str(z['record'])))
    if folder=='products':
        from revision_common import PRODUCT_SEED_INDICES
        rows=[r for r in rows if r['seed'] in PRODUCT_SEED_INDICES]
    write_json(OUT/(folder+'_runs.json'),rows)
    return rows

def observe(info,x,target,metric=None):
    if 'path_masks' not in info:raise ValueError('Particle identities must be retained')
    if 'affected' not in info['path_masks']:
        info['path_masks']['affected']=np.logical_or.reduce(list(info['path_masks'].values()))
    for name,mask in info['path_masks'].items():
        particles=mask.any(axis=1) if mask.ndim==2 else mask
        info['unique_'+name+'_particles']=int(particles.sum())
        info[name+'_particle_fraction']=float(particles.mean())
    return finish_diagnostics(info,x,target,metric)

def ou_stage():
    ns=definitions(api(),[8,16]);base=current_records()
    source=1.5+.5*np.random.default_rng(0).standard_normal(10000)
    ranks=sorted(set([r['r'] for r in base['outputs/ou_results.json']['rank_scan']]+[40]))
    for rank in ranks:
        key=f'ou1_r{rank}'
        if completed('ou',key):continue
        info={};t=time.perf_counter();x=ns['ou_transport'](source,rank,6.,.05,diagnostics=info)
        seconds=time.perf_counter()-t
        info,masks=observe(info,x,None,metric=lambda y:float(ns['w2_gauss'](y)))
        row=dict(id=key,system='OU1',rank=rank,seed=0,sw2=float(ns['w2_gauss'](x)),diagnostics=info,
                 sampling_seconds=seconds,status='ok')
        save_run('ou',key,row,dict(final=x,**masks));print(key,row['sw2'],flush=True)
    for coupling in (0.,.15):
        name='ou_hd_uncoupled_results.json' if coupling==0 else 'ou_hd_results.json'
        baseline=base['outputs/'+name];cfg=baseline['config']
        A,rates,Q,cov=ns['ou_hd_model'](10,coupling)
        directions=np.random.default_rng(0).standard_normal((64,10));directions/=np.linalg.norm(directions,axis=1,keepdims=True)
        for seed in range(700,710):
            key=f'ou10_c{coupling:g}_seed{seed}'
            if completed('ou',key):continue
            x0=.5+.5*np.random.default_rng(seed).standard_normal((5000,10))
            result=ns['ou_hd_transport'](x0,rates,Q,30,cfg['times'],.05);x=result['states'][-1]
            metrics=[dict(time=t,**ns['ou_hd_metrics'](state,cov,directions)) for t,state in zip(cfg['times'],result['states'])]
            info,masks=observe(result['diagnostics'],x,None,metric=lambda y:ns['ou_hd_metrics'](y,cov,directions)['sw2'])
            row=dict(id=key,system='OU10',coupling=coupling,seed=seed,sw2=metrics[-1]['sw2'],metrics=metrics,
                     diagnostics=info,sampling_seconds=result['transport_seconds'],status='ok')
            save_run('ou',key,row,dict(states=result['states'],**masks));print(key,row['sw2'],flush=True)
    collect('ou')

def a2_stage(seed_index=None):
    ns=api();base=current_records();previous=base['outputs/admissible_source/summary.json']
    cfg=dict(previous['config']);cfg['seed_counts']={str(b):10 for b in cfg['betas']}
    cfg['version']=2
    cfg['cache_policy']='Reuse input and spectral caches for the fixed configuration; retain every prescribed source realisation.'
    cfg['max_beta_workers']=1;cfg['output_directory']='outputs/revision/a2'
    cfg['expected_unique_runs']=sum(len(specifications(cfg,b)) for b in cfg['betas'])
    write_json(OUT/'a2_config.json',cfg)
    for beta in cfg['betas']:
        pot=ns['Potential']('A',d=2,beta=beta);ex=ns['exact_2d'](pot,n=201,kmax=129)
        target=ns['stationary_samples'](pot,2000,np.random.default_rng(7));metric,directions=metric_function(target,cfg)
        horizon=round((8/ex['lam'][1])/.05)*.05
        ref=base['outputs/results.json'][f'A2_beta{beta}']['reference']['metrics']['sw']
        specs=specifications(cfg,beta)
        for seed in range(10) if seed_index is None else [seed_index]:
            pending=[r for r in specs if r['seed']==seed and not completed('a2',run_id(r))]
            if not pending:continue
            xd,yd=ns['simulate_pairs'](pot,200000,np.random.default_rng(100+seed))
            x0=new_source(cfg,500+seed);independent=new_source(cfg,700+seed);fits={}
            for spec in pending:
                key=run_id(spec);method=spec['method'];n=spec['n_pairs'];fit=None
                if method=='FD':lam,basis=ex['lam'],ex['basis'];J=0
                else:
                    pair=(method,n)
                    if pair not in fits:
                        dic=ns['Dictionary']('rbf',pot,n=12,wfrac=.075) if method=='RBF' else ns['Dictionary']('poly',pot,p=16)
                        fits[pair]=ns['RREstimate'](dic,xd[:n],yd[:n],chunk=5000,align=ex['align'])
                    fit=fits[pair];lam,basis,J=fit.lam,fit.basis,fit.dic.size()
                rank=min(spec['r_requested'],len(lam)-1)
                result=instrumented_transport(pot,lam,basis,x0,independent if spec['regime']=='I' else x0,
                                              rank,horizon,spec['dt'],cfg,metric,fit)
                x=result['final'];info=dict(result['events'],path_masks=result['path_masks'])
                info,masks=observe(info,x,target)
                row=dict(**spec,id=key,system=f'A2_beta{beta}',particles=2000,T=horizon,J=J,r_used=rank,
                         source_seed=500+seed,training_seed=100+seed,target_seed=7,
                         sw2=result['sw2'],status=result['status'],failure=result['failure'],diagnostics=info,
                         reference=ref,checkpoints=result['checkpoint_records'],sampling_seconds=result['sampling_seconds'],
                         training_x_sha256=array_sha(xd[:n]) if n else None,training_y_sha256=array_sha(yd[:n]) if n else None,
                         source_sha256=array_sha(x0),target_sha256=array_sha(target))
                save_run('a2',key,row,dict(final=x,coefficients=result['coefficients'],**masks))
                print('A2',key,'SW2',row['sw2'],flush=True)
            collect('a2')

def regular_stage(high=False,seed_index=None):
    ns=api();base=current_records()['outputs/results.json']
    cases=[('A10_beta0.0','A',0.)] if high else [('B_quartic4','quartic4',0.),('B_poly9','poly9',0.)]
    folder='a10' if high else 'multi'
    for name,kind,beta in cases:
        pot=ns['Potential'](kind,d=10 if high else 2,beta=beta);M=1000 if high else 2000
        main=base[name];selected=main['selected_n'];dt=.05 if high else .02;rank=16 if high else 64
        target=ns['stationary_samples'](pot,M,np.random.default_rng(7));align=None;horizon=None;ex=None
        if not high:ex=ns['exact_2d'](pot,n=201,kmax=129);horizon=8/ex['lam'][1];align=ex['align']
        elif beta==0:
            G=ns['exact_1d']();horizon=8/G['lam'][1]
            align=lambda X:np.stack([np.interp(X[:,0],G['xg'],G['Phi'][:,k]) for k in range(5)])
            grid=ns['grid_basis_factory'](G)
            def factor(X,r):
                P,dP=grid(X[:,0],int(r.max()) if isinstance(r,np.ndarray) else r)
                if isinstance(r,np.ndarray):P,dP=P[r],dP[r]
                grad=np.zeros((len(P),len(X),10));grad[:,:,0]=dP
                return P,grad
        for seed in range(10) if seed_index is None else [seed_index]:
            rng=np.random.default_rng(500+seed)
            x0=ns['source_A'](pot,M,rng) if high else np.column_stack([ns['bump_sampler'](1.,.6 if kind=='quartic4' else .3,M,rng) for _ in range(2)])
            selection=ns['source_A'](pot,100000,np.random.default_rng(900+seed)) if high else None
            jobs=[]
            for method in ('rbf','poly'):
                budgets=[10000,100000,200000] if method=='rbf' or high else [selected]
                jobs.extend((method,n,rank,None,'main' if n==selected else 'sample_size') for n in budgets)
            if not high and seed==0:
                for method in ('rbf','poly'):
                    jobs.extend((method,selected,r,None,'rank_scan') for r in sorted(set([16,32,64,96]+[len(pot.wells())-1])) if r!=rank)
            if kind=='quartic4' and seed>0:jobs.append(('poly',selected,32,None,'instability_repeats'))
            fits={}
            for method,n,r,size,role in jobs:
                key=f'{name}_{method}_n{n}_r{r}_size{size or 0}_seed{seed}'
                if completed(folder,key):continue
                fitkey=(method,n,size)
                if fitkey not in fits:fits[fitkey]=ns['fit_for'](pot,method,n,seed,align,size)
                est=fits[fitkey];info={};tic=time.perf_counter()
                try:
                    x,actual,T=ns['learned_transport'](pot,est,x0,r,dt,horizon,selection_source=selection,diagnostics=info)
                    seconds=time.perf_counter()-tic
                    finite=bool(np.isfinite(x).all());value=ns['sliced_w2'](x,target) if finite else None
                    info,masks=observe(info,x,target)
                    row=dict(id=key,system=name,seed=seed,source_seed=500+seed,training_seed=100+seed,
                        selection_seed=900+seed if high else None,selection_sample_count=100000 if high else None,
                        method={'rbf':'RBF','poly':'Legendre'}[method],n_pairs=n,r_requested=r,r_used=actual,J=est.dic.size(),
                        dictionary_size_parameter=size,role=role,T=T,dt=dt,sw2=value,status='ok' if finite else 'nonfinite',
                        diagnostics=info,reference=main['reference']['metrics']['sw'],sampling_seconds=seconds,
                        lambda1=float(est.lam[1]),source_sha256=array_sha(x0),target_sha256=array_sha(target))
                    save_run(folder,key,row,dict(final=x,**masks))
                except (FloatingPointError,np.linalg.LinAlgError) as exc:
                    row=dict(id=key,system=name,seed=seed,method={'rbf':'RBF','poly':'Legendre'}[method],
                             n_pairs=n,r_requested=r,dictionary_size_parameter=size,dt=dt,
                             role=role,status='failed',sw2=None,error=repr(exc),traceback=traceback.format_exc())
                    save_run(folder,key,row,{})
                print(folder,key,'SW2',row['sw2'],'status',row['status'],flush=True)
            fd_ranks=[rank]
            if not high and seed==0:fd_ranks=sorted(set([8,16,32,64,128,len(pot.wells())-1]))
            if not high or beta==0:
                for r in fd_ranks:
                    key=f'{name}_FD_r{r}_seed{seed}'
                    if completed(folder,key):continue
                    lam,basis=(G['lam'],factor) if high else (ex['lam'],ex['basis'])
                    info={};tic=time.perf_counter();x=ns['transport'](x0,lam,basis,r,horizon,dt,pot,diagnostics=info)
                    seconds=time.perf_counter()-tic
                    info,masks=observe(info,x,target)
                    row=dict(id=key,system=name,method='FD',seed=seed,n_pairs=0,r_requested=r,r_used=r,T=horizon,dt=dt,
                        sw2=ns['sliced_w2'](x,target),status='ok',diagnostics=info,
                        role='main' if r==rank else 'rank_scan',reference=main['reference']['metrics']['sw'],sampling_seconds=seconds)
                    save_run(folder,key,row,dict(final=x,**masks));print(folder,key,row['sw2'],flush=True)
            collect(folder)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=['ou','a2','multi','a10'])
    parser.add_argument('--seed-index',type=int,choices=range(10))
    args=parser.parse_args()
    if args.stage=='ou' and args.seed_index is not None:parser.error('OU runs as a single stage')
    before=row_count(args.stage,args.seed_index);start=time.perf_counter()
    with threadpool_limits(limits=1):
        {'ou':ou_stage,'a2':lambda:a2_stage(args.seed_index),'multi':lambda:regular_stage(seed_index=args.seed_index),
         'a10':lambda:regular_stage(True,args.seed_index)}[args.stage]()
        if args.seed_index is None:
            record_execution(args.stage,time.perf_counter()-start,before,row_count(args.stage),stage=args.stage,
                             threadpools=threadpool_info())
    print('STAGE COMPLETE',args.stage,'seconds',time.perf_counter()-start,flush=True)

if __name__=='__main__':
    from experiment_store import managed_outputs
    with managed_outputs('double_well','ou'):main()
