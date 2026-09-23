"""Fixed-fit alanine cost, evaluation, source control, and path diagnostics."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):os.environ[key]='1'
import argparse,copy,json,subprocess,sys,time,tempfile
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
import alanine_experiment as ae
import alanine_convergence as ac
import alanine_baselines as ab
from revision_common import OUT,write_json,save_run,load_run,array_sha,empirical_sw2,summarize,row_count,record_execution
from revision_synthetic import collect,parity

SEEDS=(1101,1102,1103)

def label_rotation_endpoint(row):
    """Distinguish a saved checkpoint from the requested terminal result."""
    score=row.get('last_checkpoint_score',row.get('endpoint'))
    if score is None:raise ValueError('Missing saved rotation checkpoint score')
    saved_s=float(row['checkpoints'][-1]['s'])
    complete=row['status']=='ok' and saved_s==8.
    row.update(last_checkpoint_s=saved_s,last_checkpoint_score=score,
               requested_endpoint_available=complete,endpoint=score if complete else None)
    if not complete:
        events=row['events']
        if 'last_checkpoint_unaffected_sw2' not in events:
            events['last_checkpoint_unaffected_sw2']=events.get('unaffected_sw2')
        events['unaffected_sw2']=None
    return row

def metric_unequal(x,target):
    directions=np.random.default_rng(2026).normal(size=(4,32));directions/=np.linalg.norm(directions,axis=0)
    return empirical_sw2(ae.embed(x,True),ae.embed(target,True),directions.T)

def attach(row,clouds,target):
    info=row['events'];masks=info.pop('path_masks');affected=masks['affected'];last=clouds[-1]
    info.update(retained_unaffected_particles=int((~affected).sum()),full_particles=len(last),
        unaffected_sw2=metric_unequal(last[~affected],target) if (~affected).any() else None,
        periodic_wrapping_is_not_box_projection=True)
    return {'mask_'+k:v for k,v in masks.items()}

def reference_summary(data):
    centers=data['cluster_centers'];rows=[]
    for i,seed in enumerate(SEEDS):
        a,b=data['reference_a'][i],data['reference_b'][i]
        rows.append(dict(seed=seed,**ac.metrics(a,b,centers)))
    return rows

def late_time(row,reference_sd):
    cp=row['checkpoints'];s=np.array([c['s'] for c in cp]);e=np.array([c['sw2'] for c in cp])
    if s[-1]!=8:return dict(late_error=None,first_hit_wall_seconds=None,status='incomplete')
    q=s>=6;level=float(np.trapezoid(e[q],s[q])/2)
    hits=[c for c in cp if abs(c['sw2']-level)<=reference_sd]
    return dict(late_error=level,reference_sd=reference_sd,
        definition='First prescribed checkpoint in absolute-error band around time-average SW2 on s in [6,8]; not a common-accuracy comparison',
        first_hit_s=hits[0]['s'] if hits else None,
        first_hit_wall_seconds=hits[0]['wall_seconds'] if hits else None)

def spectrum(train,index,case):
    if index!=0:raise ValueError("The retained alanine experiment fits trajectory 1 only")
    identity=f'spectrum_fit{index}';saved=load_run('alanine',identity)
    if saved:
        info,arrays=saved
        if info['train_sha256']!=array_sha(train):raise ValueError('Spectrum training provenance mismatch')
        return arrays['lam'],arrays['basis'],info
    cpu=time.process_time();lam,basis,info=ae.fit_spectrum(train,case,threads=1)
    if len(lam)!=256:raise ValueError(f'The prescribed 256-mode fit produced only {len(lam)} modes')
    info.update(id=identity,task='B3a_fit' if index==0 else 'B3b_fit',fit_trajectory=index,train_sha256=array_sha(train),
                fit_cpu_seconds=time.process_time()-cpu,threadpools=threadpool_info())
    save_run('alanine',identity,info,dict(lam=lam,basis=basis));print('SPECTRUM',index,info,flush=True)
    return lam,basis,info

def cost_stage():
    data,dic=ac.inputs();old,oldarrays=ac.load_results();dataset=ae.load_npz('dataset.npz')
    spectrum(dataset['train_all'],0,data['record']['setting'])
    saved=load_run('alanine','kde_target_fit')
    if saved:
        metadata,fit=saved;fit['metadata']=metadata
    else:
        cpu=time.process_time();fit=ab.fit_target(dataset['train_all'],**ac.SPEC['baseline_target'])
        metadata=dict(fit['metadata'],fit_cpu_seconds=time.process_time()-cpu,threads=1,id='kde_target_fit',task='B3a_fit')
        save_run('alanine','kde_target_fit',metadata,{k:v for k,v in fit.items() if k!='metadata'})
    references=reference_summary(data);refsd=summarize(r['sw2'] for r in references)['std']
    for seed in SEEDS:
        i=SEEDS.index(seed)
        for method in ('BKT','LAWGD','KDE'):
            identity=f'cost_{method}_seed{seed}'
            if load_run('alanine',identity):continue
            if method=='KDE':
                diagnostic,clouds=ab.run_kde(data['source'][i],fit,float(data['lam'][0]),ac.TIMES,seed,**ac.SPEC['kde'])
                row,clouds=ac.baseline_row(data,method,seed,diagnostic,clouds)
                row.update(coefficient_wall_seconds=0.,coefficient_cpu_seconds=0.,coefficient_stage='Not applicable to KDE')
                row['events']={'nfev':diagnostic['nfev']}
                masks={}
            else:
                row,clouds=ac.transport(data,dic,256,method,seed);masks=attach(row,clouds,data['target'][i])
            key=ac.case_id(None if method=='KDE' else 256,method,seed)
            expected=oldarrays[key+'_clouds'][:len(clouds)]
            checks=parity(clouds,expected)
            checks['requested_horizon_completed']=row['status']=='ok' and row['checkpoints'][-1]['s']==8
            checks['passes_1e12']=checks['passes_1e12'] and checks['requested_horizon_completed']
            checks['periodic_max_absolute_difference']=float(np.max(abs(ae.wrap(clouds-expected))))
            oldrow=next(r for r in old['runs'] if r['method']==method and r['seed']==seed)
            checks['max_checkpoint_sw2_difference']=max(abs(a['sw2']-b['sw2']) for a,b in zip(row['checkpoints'],oldrow['checkpoints']))
            row.update(id=identity,task='B3a_cost',threads=1,parity=checks,
                       late_time=late_time(row,refsd),reference=references[i],lambda1=float(data['lam'][0]),
                       fit_seconds=(metadata['fit_seconds'] if method=='KDE' else load_run('alanine','spectrum_fit0')[0]['fit_seconds']))
            save_run('alanine',identity,row,dict(clouds=clouds,**masks));collect('alanine')
            print('ALANINE COST',method,seed,row['checkpoints'][-1]['sw2'],row['wall_seconds'],row['parity'],flush=True)

def full_trajectories():
    with np.load(OUT/'alanine_raw.npz') as z:trajectories=[np.asarray(z[k],dtype=np.float64) for k in z.files]
    assert len(trajectories)==3 and all(x.shape==(250000,2) for x in trajectories)
    existing=ae.load_npz('dataset.npz')
    np.testing.assert_array_equal(trajectories[0],existing['train_all'])
    for i,key in [(1,'val'),(2,'test')]:
        np.testing.assert_array_equal(trajectories[i][np.linspace(0,249999,12000,dtype=int)],existing[key])
    np.testing.assert_array_equal(trajectories[0][np.linspace(0,249999,25000,dtype=int)],existing['train_small'])
    return trajectories

def design(train,evaluation,lam,basis,case,kind='sobol'):
    small=train[np.linspace(0,len(train)-1,25000,dtype=int)]
    labels,centers,k=ae.partition(small,True);groups=labels(small)
    selected=small[groups==np.argmax(np.bincount(groups,minlength=k))]
    mean=np.arctan2(np.sin(selected).mean(0),np.cos(selected).mean(0));cov=np.cov(ae.wrap(selected-mean).T)*.7**2
    pool=evaluation[np.linspace(0,len(evaluation)-1,12000,dtype=int)]
    sources=[];targets=[];ras=[];rbs=[]
    for seed in SEEDS:
        sources.append(ae.source_points(seed,1000,mean,cov,kind))
        ids=np.random.default_rng(seed+9000).choice(len(pool),3000,replace=False)
        target,ra,rb=[pool[j] for j in np.split(ids,3)];targets.append(target);ras.append(ra);rbs.append(rb)
    return dict(source=np.asarray(sources),target=np.asarray(targets),reference_a=np.asarray(ras),reference_b=np.asarray(rbs),
                source_mean=mean,source_covariance=cov,cluster_centers=centers,lam=lam,basis=basis,
                record=dict(seeds=list(SEEDS),setting=case))

def variability_stage(fit_filter=None,evaluation_filter=None,seed_filter=None):
    trajectories=full_trajectories();original,dic=ac.inputs();case=original['record']['setting']
    for fit_index in (0,) if fit_filter is None else [fit_filter]:
        lam,basis,spec=spectrum(trajectories[fit_index],fit_index,case)
        for evaluation in range(3) if evaluation_filter is None else [evaluation_filter]:
            if evaluation==fit_index:continue
            data=design(trajectories[fit_index],trajectories[evaluation],lam,basis,case)
            if fit_index==0 and evaluation==2:
                for key in ('source','target','reference_a','reference_b','source_mean','source_covariance','cluster_centers'):
                    np.testing.assert_array_equal(data[key],original[key])
            references=reference_summary(data)
            for seed in SEEDS if seed_filter is None else [seed_filter]:
                identity=f'rotation_fit{fit_index}_eval{evaluation}_seed{seed}'
                if load_run('alanine',identity):continue
                i=SEEDS.index(seed);row,clouds=ac.transport(data,dic,256,'BKT',seed)
                masks=attach(row,clouds,data['target'][i]);labels,_,k=ae.partition(None,centers=data['cluster_centers'])
                score=ae.score(clouds[-1],data['target'][i],labels,k,ae.thickness(data['target'][i]))
                row.update(id=identity,task='B3b_rotation',fit_trajectory=fit_index,evaluation_trajectory=evaluation,
                           lambda1=float(lam[0]),endpoint=score,reference=references[i],threads=1,
                           source_mean=data['source_mean'],source_covariance=data['source_covariance'])
                label_rotation_endpoint(row)
                save_run('alanine',identity,row,dict(clouds=clouds,target=data['target'][i],reference_a=data['reference_a'][i],
                                                   reference_b=data['reference_b'][i],**masks))
                collect('alanine');print('ALANINE ROTATION',identity,score,flush=True)

def parallel_variability():
    # Fit once before the independent fixed-fit evaluation processes.
    trajectories=full_trajectories();original,_=ac.inputs()
    spectrum(trajectories[0],0,original['record']['setting'])
    def run_one(fit_index,evaluation,seed):
        name=f'rotation_fit{fit_index}_eval{evaluation}_seed{seed}'
        command=[sys.executable,'-u','-B',__file__,'variability','--fit-trajectory',str(fit_index),
                 '--evaluation-trajectory',str(evaluation),'--seed',str(seed)]
        with tempfile.TemporaryFile(mode='w+',encoding='utf-8') as stream:
            result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
            if result.returncode:
                stream.seek(0);print(stream.read(),flush=True)
        row=dict(id=name,exit_code=result.returncode)
        print('ROTATION FINISHED',json.dumps(row),flush=True)
        return row
    results=[]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures=[executor.submit(run_one,i,j,s) for i in (0,) for j in (1,2) for s in SEEDS]
        for future in as_completed(futures):results.append(future.result())
    collect('alanine')
    if any(r['exit_code']!=0 for r in results):raise RuntimeError('A fixed-fit evaluation process failed; all available numerical records are retained')

def iid_stage():
    data,dic=ac.inputs();data=copy.deepcopy(data)
    for i,seed in enumerate(SEEDS):data['source'][i]=ae.source_points(seed,1000,data['source_mean'],data['source_covariance'],'iid')
    references=reference_summary(data)
    for seed in SEEDS:
        identity=f'iid_seed{seed}'
        if load_run('alanine',identity):continue
        i=SEEDS.index(seed);row,clouds=ac.transport(data,dic,256,'BKT',seed);masks=attach(row,clouds,data['target'][i])
        row.update(id=identity,task='B3c_iid',reference=references[i],threads=1)
        save_run('alanine',identity,row,dict(clouds=clouds,**masks));collect('alanine')
        print('ALANINE IID',seed,row['checkpoints'][-1],flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['cost','variability','iid'])
    p.add_argument('--fit-trajectory',type=int,choices=(0,));p.add_argument('--evaluation-trajectory',type=int,choices=range(3))
    p.add_argument('--seed',type=int,choices=SEEDS);args=p.parse_args()
    filtered=any(v is not None for v in (args.fit_trajectory,args.evaluation_trajectory,args.seed))
    if filtered and (args.stage!='variability' or any(v is None for v in (args.fit_trajectory,args.evaluation_trajectory,args.seed)) or args.fit_trajectory==args.evaluation_trajectory):
        p.error('A filtered rotation requires distinct fit/evaluation trajectories and one prescribed seed')
    identity=f'rotation_fit{args.fit_trajectory}_eval{args.evaluation_trajectory}_seed{args.seed}' if filtered else None
    before=int(load_run('alanine',identity) is not None) if filtered else row_count('alanine');start=time.perf_counter()
    with threadpool_limits(limits=1):
        variability=(lambda:variability_stage(args.fit_trajectory,args.evaluation_trajectory,args.seed)) if filtered else parallel_variability
        {'cost':cost_stage,'variability':variability,'iid':iid_stage}[args.stage]()
        after=int(load_run('alanine',identity) is not None) if filtered else row_count('alanine')
        if not filtered:
            record_execution('alanine_'+args.stage,time.perf_counter()-start,before,after,threadpools=threadpool_info(),
                             repetition_processes=4 if args.stage=='variability' else 1,
                             estimation_policy='One fixed spectrum from trajectory 1; evaluation transports may use four single-BLAS-thread processes')
    print('ALANINE STAGE COMPLETE',args.stage,flush=True)

if __name__=='__main__':
    from experiment_store import managed_outputs
    with managed_outputs('double_well','alanine'):main()
