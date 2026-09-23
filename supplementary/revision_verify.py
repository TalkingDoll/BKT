"""Recompute revision endpoint distances and validate every saved path mask."""
from __future__ import annotations
import json
import numpy as np
from revision_common import ROOT,OUT,api,definitions,load_run,empirical_sw2,write_json
from revision_synthetic import collect

def verify_masks(row,arrays):
    masks={k[5:]:v for k,v in arrays.items() if k.startswith('mask_')}
    if not masks:return 0
    assert set(masks)=={'floor','nonpositive','cap','projection','affected'},row['id']
    assert all(a.dtype==bool and a.shape==masks['affected'].shape for a in masks.values())
    assert np.array_equal(masks['affected'],np.logical_or.reduce([masks[k] for k in ('floor','nonpositive','cap','projection')]))
    assert np.all(~masks['nonpositive'] | masks['floor']),row['id']
    cloud=arrays.get('final')
    if cloud is None and 'clouds' in arrays:cloud=arrays['clouds'][-1]
    if cloud is None and 'states' in arrays:cloud=arrays['states'][-1]
    if cloud is not None:assert len(masks['affected'])==len(cloud),row['id']
    diag=row.get('diagnostics',row.get('events',{}))
    for k,a in masks.items():
        p=a.any(1) if a.ndim==2 else a
        assert int(p.sum())==diag['unique_'+k+'_particles'],(row['id'],k)
        assert abs(float(p.mean())-diag[k+'_particle_fraction'])<1e-15
        if a.ndim==2:assert abs(float(a.mean())-diag[k+'_particle_coordinate_fraction'])<1e-15
    return len(masks)

def main():
    from revision_alanine import ac,ae,metric_unequal
    from revision_products import setup
    ns=api();ou=definitions(ns.copy(),[8,16]);products=setup();original,_=ac.inputs()
    targets={};report=[];maximum=0.;mask_count=0
    for folder in ('a2','a10','multi','ou','products','comparison','alanine'):
        rows=collect(folder);count=0
        for row in rows:
            _,arrays=load_run(folder,row['id'])
            needs_masks=folder!='comparison' and row.get('task') not in ('B3a_fit','B3b_fit') and not (folder=='alanine' and row.get('method')=='KDE')
            if needs_masks and row.get('status') in ('ok','incomplete'):
                assert 'mask_affected' in arrays,('Missing prescribed path masks',row['id'])
            mask_count+=verify_masks(row,arrays)
            if row.get('status') not in ('ok',None):continue
            if folder=='alanine':
                if row.get('task') in ('B3a_fit','B3b_fit'):continue
                target=arrays.get('target',original['target'][ac.SEEDS.index(row['seed'])]);x=arrays['clouds'][-1]
                value=row['checkpoints'][-1]['sw2']
                distance=lambda y:metric_unequal(y,target)
            elif folder=='ou':
                if row['system']=='OU1':x=arrays['final'];distance=ou['w2_gauss']
                else:
                    x=arrays['states'][-1];_,_,_,cov=ou['ou_hd_model'](10,row['coupling'])
                    directions=np.random.default_rng(0).standard_normal((64,10));directions/=np.linalg.norm(directions,axis=1,keepdims=True)
                    distance=lambda y:ou['ou_hd_metrics'](y,cov,directions)['sw2']
                value=row['sw2']
            else:
                if folder=='products':
                    key=f"product{row['dimension']}"
                    if key not in targets:targets[key]=products['sample_pi_product'](20000,row['dimension'],np.random.default_rng(7))
                else:
                    key=f"A2_beta{row['beta']}" if folder in ('a2','comparison') else row['system']
                    if key not in targets:
                        if key.startswith('A'):pot=ns['Potential']('A',d=10 if key.startswith('A10') else 2,beta=float(key.split('beta')[1]))
                        else:pot=ns['Potential'](key[2:])
                        targets[key]=ns['stationary_samples'](pot,1000 if pot.d==10 else 2000,np.random.default_rng(7))
                target=targets[key];x=arrays['final'];distance=lambda y:empirical_sw2(y,target);value=row['sw2']
            measured=distance(x);error=abs(measured-value);maximum=max(maximum,error)
            assert error<=1e-12,(row['id'],'full distance',error)
            if 'mask_affected' in arrays:
                affected=arrays['mask_affected'];affected=affected.any(1) if affected.ndim==2 else affected
                diag=row.get('diagnostics',row.get('events',{}));saved=diag.get('unaffected_sw2')
                if affected.all():assert saved is None
                else:
                    difference=abs(distance(x[~affected])-saved);maximum=max(maximum,difference)
                    assert difference<=1e-12,(row['id'],'filtered distance',difference)
            count+=1
        report.append(dict(task=folder,stored_rows=len(rows),checked_endpoint_distances=count))
        print('VERIFIED',folder,count,flush=True)
    result=dict(tasks=report,checked_masks=mask_count,max_absolute_metric_difference=maximum,
                scope='Recomputed full/filtered distances and all mask unions, counts and fractions')
    write_json(OUT/'verification.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    from experiment_store import managed_outputs
    from threadpoolctl import threadpool_limits
    with managed_outputs('double_well','ou','alanine'),threadpool_limits(limits=1):main()
