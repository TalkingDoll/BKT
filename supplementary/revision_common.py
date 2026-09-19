"""Shared diagnostics and reproducible execution support for revision B1-B4."""
from __future__ import annotations

# Preserve the index s in both seed formulas; skip the target-seed collision.
PRODUCT_TARGET_SEED = 7
PRODUCT_SEED_INDICES = tuple(s for s in range(11) if 1+s != PRODUCT_TARGET_SEED)
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import numpy as np
from numpy.polynomial import legendre as L
from comparison_notebook_api import load_notebook_api

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/revision'
MASK_NAMES=('floor','nonpositive','cap','projection')

def serial(value):
    if isinstance(value,np.ndarray): return serial(value.tolist())
    if isinstance(value,np.generic): return serial(value.item())
    if isinstance(value,Path): return value.relative_to(ROOT).as_posix() if value.is_relative_to(ROOT) else str(value)
    if isinstance(value,dict): return {str(k):serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    if isinstance(value,float) and not np.isfinite(value): return None
    return value

def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+f'.{os.getpid()}.pending')
    tmp.write_text(json.dumps(serial(value),indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n');tmp.replace(path)

def array_sha(x): return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()

class PathMasks:
    """Observe numerical evaluations without modifying the state or velocity."""
    def __init__(self,shape,scope='All fixed-step RK stages and completed step projections'):
        self.masks={k:np.zeros(shape,dtype=bool) for k in MASK_NAMES}
        self.scope=scope
    def velocity(self,rho,speed,floor=1e-3,cap=20.):
        self.masks['floor'] |= rho < floor
        self.masks['nonpositive'] |= rho <= 0
        self.masks['cap'] |= speed > cap
    def projection(self,before,after):
        changed=before != after
        if changed.ndim>self.masks['projection'].ndim: changed=changed.any(axis=-1)
        self.masks['projection'] |= changed
    def result(self):
        masks=dict(self.masks);masks['affected']=np.logical_or.reduce(list(masks.values()))
        result={'diagnostic_scope':self.scope,'path_masks':masks}
        for name,mask in masks.items():
            particles=mask.any(axis=1) if mask.ndim==2 else mask
            result['unique_'+name+'_particles']=int(particles.sum())
            result[name+'_particle_fraction']=float(particles.mean())
            if mask.ndim==2: result[name+'_particle_coordinate_fraction']=float(mask.mean())
        return result

def dictionary_values(dic,X):
    """Original dictionary values, without allocating unused gradients."""
    M,d=X.shape
    if dic.kind=='rbf':
        g=[np.exp(-.5*((X[:,i,None]-dic.cen[i][None,:])/dic.wid[i])**2) for i in range(d)]
        if d==1:return np.hstack([np.ones((M,1)),g[0]])
        if d==2:return np.hstack([np.ones((M,1)),np.einsum('ma,mb->mab',g[0],g[1]).reshape(M,-1)])
        cols=[np.ones((M,1)),*g]
        cols += [np.einsum('ma,mb->mab',g[i],g[j]).reshape(M,-1) for i,j in dic.pairs]
        return np.hstack(cols)
    box=dic.pot.box;Z=2*(X-box[:,0])/(box[:,1]-box[:,0])-1
    pv=[L.legvander(Z[:,i] if dic.pot.full_plane else np.clip(Z[:,i],-1,1),dic.p) for i in range(d)]
    p=np.ones((M,len(dic.idx)))
    for j,m in enumerate(dic.idx):
        for i in range(d):p[:,j]*=pv[i][:,m[i]]
    return p

def selection_moments(basis,source,candidates,chunk=2000):
    fitted=getattr(basis,'__self__',None);total=np.zeros(len(candidates))
    for start in range(0,len(source),chunk):
        block=source[start:start+chunk]
        if fitted is not None and hasattr(fitted,'dic'):
            values=dictionary_values(fitted.dic,block)@fitted.V[:,candidates]
            total+=values.sum(axis=0)
        else:total+=basis(block,candidates)[0].sum(axis=1)
    return total/len(source)

def empirical_sw2(x,y,directions=None,seed=0,projections=64):
    """Exact quantile integration for unequal empirical sample counts."""
    if len(x)==0 or len(y)==0:return None
    if directions is None:
        directions=np.random.default_rng(seed).standard_normal((projections,x.shape[1]))
        directions/=np.linalg.norm(directions,axis=1,keepdims=True)
    a=np.sort(x@directions.T,axis=0);b=np.sort(y@directions.T,axis=0)
    if len(a)==len(b):return float(np.sqrt(np.mean((a-b)**2)))
    q=np.unique(np.r_[np.arange(len(a)+1)/len(a),np.arange(len(b)+1)/len(b)])
    mid=(q[1:]+q[:-1])/2
    ia=np.minimum((mid*len(a)).astype(int),len(a)-1)
    ib=np.minimum((mid*len(b)).astype(int),len(b)-1)
    return float(np.sqrt(np.mean(np.sum((a[ia]-b[ib])**2*np.diff(q)[:,None],axis=0))))

def summarize(values):
    values=list(values)
    valid=bool(values) and all(v is not None and np.isfinite(v) for v in values)
    return dict(values=values,n=len(values),mean=statistics.mean(values) if valid else None,
                std=statistics.stdev(values) if valid and len(values)>1 else None,
                median=statistics.median(values) if valid else None,
                nonfinite_count=sum(v is None or not np.isfinite(v) for v in values))

def definitions(ns,cells,baseline=False):
    path=OUT/'baseline_notebook.ipynb' if baseline else ROOT/'BKT_experiments.ipynb'
    notebook=json.loads(path.read_text(encoding='utf-8'))
    for index in cells:
        tree=ast.parse(''.join(notebook['cells'][index]['source']))
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom)):
                exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(path),'exec',dont_inherit=True),ns)
    return ns

def api(baseline=False):
    path=OUT/'baseline_notebook.ipynb' if baseline else ROOT/'BKT_experiments.ipynb'
    ns=load_notebook_api(path,ROOT/'outputs',fail_on_cache_miss=False)
    if ns.get('QUICK') is not False:raise ValueError('The revision protocol requires QUICK=False')
    # Restore the original atomic cache writer; old content-addressed entries remain readable.
    notebook=json.loads(path.read_text(encoding='utf-8'))
    tree=ast.parse(''.join(notebook['cells'][1]['source']))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='cached_arrays')
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(path),'exec',dont_inherit=True),ns)
    ns['_loader_metadata']['read_only_cache']=False
    return ns

def baseline_records():return json.loads((OUT/'baseline_records.json').read_text(encoding='utf-8'))

def save_run(folder,identity,row,arrays):
    folder=OUT/folder;folder.mkdir(parents=True,exist_ok=True)
    path=folder/(identity+'.npz');tmp=path.with_suffix('.pending.npz')
    np.savez_compressed(tmp,record=json.dumps(serial(row),allow_nan=False),**arrays);tmp.replace(path)

def load_run(folder,identity):
    path=OUT/folder/(identity+'.npz')
    if not path.exists():return None
    with np.load(path) as z:return json.loads(str(z['record'])),{k:z[k] for k in z.files if k!='record'}

def row_count(folder,seed=None):
    def matches(path):
        if path.name.endswith('.pending.npz'):return False
        if seed is None:return True
        return path.stem.endswith(f'_seed{seed}') or f'_seed{seed}_' in path.stem
    return sum(matches(p) for p in (OUT/folder).glob('*.npz'))

def record_execution(stage_name,wall_seconds,before,after,**metadata):
    """Keep measured work when a later invocation merely resumes saved rows."""
    path=OUT/(stage_name+'_execution.json')
    previous=json.loads(path.read_text()) if path.exists() else None
    attempt=dict(wall_seconds=wall_seconds,new_records=after-before,rows_before=before,rows_after=after)
    history=previous.get('attempts',[]) if previous else []
    if previous and not history:history=[dict(wall_seconds=previous['wall_seconds'],new_records=None,previous_execution_without_attempt_history=True)]
    history.append(attempt)
    total=(previous['wall_seconds'] if previous else 0.)+(wall_seconds if after>before or previous is None else 0.)
    write_json(path,dict(previous or {},**metadata,wall_seconds=total,attempts=history,
                         timing_scope='Sum of executions adding prescribed records; cache-only resumes are recorded separately'))

def finish_diagnostics(diagnostics,final,target,metric=None):
    masks=diagnostics.pop('path_masks')
    affected=masks['affected'];affected=affected.any(axis=1) if affected.ndim==2 else affected
    clean=final[~affected]
    diagnostics.update(retained_unaffected_particles=len(clean),full_particles=len(final),
                       filtered_metric_definition='Renormalized unaffected empirical cloud; diagnostic only; complete target retained',
                       unaffected_sw2=(metric(clean) if metric else empirical_sw2(clean,target)) if len(clean) else None)
    return diagnostics,{'mask_'+k:v for k,v in masks.items()}
