"""Ten paired realisations of the fixed separable 10D and 50D products."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','BLIS_NUM_THREADS'):os.environ[key]='1'
import argparse,time
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from revision_common import OUT,api,definitions,baseline_records,load_run,save_run,write_json,array_sha,row_count,record_execution
from revision_synthetic import observe,parity,collect
from revision_common import PRODUCT_SEED_INDICES,PRODUCT_TARGET_SEED

def setup(baseline=False):
    ns=definitions(api(baseline),[18],baseline=baseline);G=ns['setup_1d'](lambda x:(x**2-1)**2)
    ns.update(Gp=G,basis_p=ns['grid_basis_factory'](G),xgp=G['xg'],lam_p=G['lam'],Phi_p=G['Phi'],cdf_p=G['cdf'],
              PRODUCT_WORKERS=8,PRODUCT_LEGENDRE_DEGREE=32,PRODUCT_LEGENDRE_TOL=1e-10,PRODUCT_LEGENDRE_CHUNK=5000)
    return ns

def run(d,seed_index=None):
    ns=setup();old=setup(True);original=baseline_records()[f'outputs/product_{d}_results.json']
    M=20000;n=200000;T=8/ns['lam_p'][1];centers=np.linspace(-2.8,2.8,80);width=.14
    target=ns['sample_pi_product'](M,d,np.random.default_rng(PRODUCT_TARGET_SEED))
    for seed in PRODUCT_SEED_INDICES if seed_index is None else [seed_index]:
        if seed not in PRODUCT_SEED_INDICES:raise ValueError('Product source seed must differ from target seed')
        names=('exact','estimated','legendre')
        if all(load_run('products',f'product{d}_{name}_seed{seed}') for name in names):continue
        rng=np.random.default_rng(1+seed);x0=np.column_stack([ns['bump_sampler'](1.,.6,M,rng) for _ in range(d)])
        def compute():
            x,y=ns['sde_pairs_d'](n,d,.1,np.random.default_rng(1001+seed),lambda x:-4*x*(x**2-1))
            return dict(X=x,Y=y)
        key=dict(d=d,n=n,seed=1001+seed,dt=.002,burn=20.,tau=.1,grid=ns['xgp'],cdf=ns['cdf_p'],code=ns['code_hash'](ns['sde_pairs_d']))
        training=ns['cached_arrays']('product_training',key,compute);xd=training['X'];del training
        for name in names:
            identity=f'product{d}_{name}_seed{seed}'
            if load_run('products',identity):continue
            tic=time.perf_counter();lams=[];bases=[]
            if name=='exact':lams=[ns['lam_p']]*d;bases=[ns['basis_p']]*d
            else:
                for i in range(d):
                    if name=='estimated':lam,basis=ns['rr_eig_1d'](xd[:,i],centers,width)
                    else:lam,basis,_=ns['fit_legendre_1d'](xd[:,i],ns['xgp'],ns['Phi_p'],degree=32,tol=1e-10,chunk=5000,r_max=24)
                    lams.append(lam);bases.append(basis)
            fit_seconds=time.perf_counter()-tic;ranks=[min(16,len(lam)-1) for lam in lams]
            info={};tic=time.perf_counter()
            x=ns['transport_product'](x0,lams,bases,ranks,T,.02,workers=8,diagnostics=info)
            sampling_seconds=time.perf_counter()-tic;checks=None
            if seed==0:
                cachekey=dict(method=name,d=d,X0=x0,lam=lams,r=ranks,T=T,dt=.02,xgrid=ns['xgp'],Phi=ns['Phi_p'],
                    centres=centers,width=width,legendre_degree=32,training=None if name=='exact' else xd,
                    code=old['code_hash'](old['transport_product'],old['rr_eig_1d'],old['fit_legendre_1d'],old['grid_basis_factory']))
                previous=old['cached_arrays']('product_transport',cachekey,lambda:old['transport_product'](x0,lams,bases,ranks,T,.02))
                checks=parity(x,previous)
            metrics=ns['particle_metrics'](x,target)
            metrics['negative_count_tv']=float(.5*np.abs(ns['neg_count_dist'](x,d)-ns['neg_count_dist'](target,d)).sum())
            info,masks=observe(info,x,target)
            row=dict(id=identity,system=f'product{d}',dimension=d,seed=seed,method={'exact':'FD','estimated':'RBF','legendre':'Legendre'}[name],
                source_seed=1+seed,training_seed=1001+seed,target_seed=7,particles=M,n_pairs=n,rank=16,r_used=ranks,T=T,dt=.02,
                sw2=metrics['sw'],metrics=metrics,reference=original['reference']['metrics']['sw'],diagnostics=info,parity=checks,status='ok',
                fit_seconds=fit_seconds,sampling_seconds=sampling_seconds,coordinate_workers=8,blas_threads=1,
                source_sha256=array_sha(x0),target_sha256=array_sha(target),training_x_sha256=array_sha(xd))
            save_run('products',identity,row,dict(final=x,source_x1=x0[:,0],target_x1=target[:,0],**masks));collect('products')
            print('PRODUCT',identity,'SW2',row['sw2'],'seconds',sampling_seconds,'parity',checks,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('dimension',type=int,choices=[10,50])
    p.add_argument('--seed-index',type=int,choices=PRODUCT_SEED_INDICES);args=p.parse_args();before=row_count('products',args.seed_index);start=time.perf_counter()
    with threadpool_limits(limits=1):
        run(args.dimension,args.seed_index)
        execution=f'product{args.dimension}' if args.seed_index is None else f'execution_attempts/product{args.dimension}_seed{args.seed_index}'
        record_execution(execution,time.perf_counter()-start,before,row_count('products',args.seed_index),coordinate_workers=8,threadpools=threadpool_info(),
                         cost_interpretation='Retained eight independent coordinate workers; descriptive cost, not part of the single-thread sampler comparison')
    print('PRODUCT STAGE COMPLETE',args.dimension,flush=True)

if __name__=='__main__':
    from experiment_store import managed_outputs
    with managed_outputs('double_well'):main()
