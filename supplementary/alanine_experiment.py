"""Reproduce the retained alanine spectral transport configuration.

The Fourier/Dirichlet estimator targets a smoothed angular marginal with
unit mobility. It does not estimate physical MD kinetics. The retained comparison uses 256 nonconstant modes and source moments
computed once from the initial particles. The RBF diagnostics use population
source moments. BKT particle locations never update the prescribed field.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.spatial import cKDTree
from scipy.special import ndtri
from scipy.stats import qmc
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[1]
CONFIG={'projections':32}

def wrap(x):
    return (x + np.pi) % (2 * np.pi) - np.pi


def embed(x, periodic):
    return np.concatenate([np.cos(x), np.sin(x)], axis=1) if periodic else x


def partition(train, periodic=True, centers=None):
    if centers is None:
        features = embed(train, True)
        centers, _ = kmeans2(features[::max(1, len(features)//10000)], 4,
                             iter=50, minit="++", seed=818)
    def labels(x):
        f = embed(x, True)
        return np.argmin(np.sum((f[:, None] - centers[None])**2, axis=2), axis=1)
    return labels, centers, 4


def masses(x, labels, count):
    return np.bincount(labels(x), minlength=count) / len(x)


def sw2(x, y, periodic):
    x, y = embed(x, periodic), embed(y, periodic)
    if len(x) != len(y):
        raise ValueError("The metric requires equal sample counts")
    if x.shape[1] == 1:
        return float(np.sqrt(np.mean((np.sort(x[:, 0]) - np.sort(y[:, 0]))**2)))
    rg = np.random.default_rng(2026)
    directions = rg.normal(size=(x.shape[1], CONFIG["projections"]))
    directions /= np.linalg.norm(directions, axis=0)
    return float(np.sqrt(np.mean((np.sort(x @ directions, axis=0) - np.sort(y @ directions, axis=0))**2)))


class FourierDictionary:
    def __init__(self,degree):
        self.degree=degree
        self.axis=np.arange(-degree,degree+1)
        self.freq=np.array([(i,j) for i in self.axis for j in self.axis if i>0 or (i==0 and j>0)])
        self.size=1+2*len(self.freq)
        self.width=None
        self.d,self.periodic=2,True

    def eval(self,x,gradients=True):
        phase=x@self.freq.T
        c,s=np.sqrt(2)*np.cos(phase),np.sqrt(2)*np.sin(phase)
        p=np.column_stack([np.ones(len(x)),c,s])
        dp=None
        if gradients:
            dp=np.concatenate([np.zeros((len(x),1,2)),-s[:,:,None]*self.freq[None,:,:],c[:,:,None]*self.freq[None,:,:]],axis=1)
        return p,dp

    def contract(self,x,coefficient):
        k=self.degree;n=len(self.freq)
        # Exact real tensor contraction of cos(u+v), sin(u+v); no mode truncation.
        matrix=np.zeros((2*k+1,2*k+1))
        cx,cy=abs(self.freq[:,0]),abs(self.freq[:,1])
        sx,sy=np.sign(self.freq[:,0]),np.sign(self.freq[:,1])
        a,b_=np.sqrt(2)*coefficient[1:1+n],np.sqrt(2)*coefficient[1+n:]
        np.add.at(matrix,(cx,cy),a)
        np.add.at(matrix,(k+cx,k+cy),-a*sx*sy)
        np.add.at(matrix,(k+cx,cy),b_*sx)
        np.add.at(matrix,(cx,k+cy),b_*sy)
        freq=np.arange(1,k+1)
        c0,s0=np.cos(x[:,0,None]*freq),np.sin(x[:,0,None]*freq)
        c1,s1=np.cos(x[:,1,None]*freq),np.sin(x[:,1,None]*freq)
        p0=np.column_stack([np.ones(len(x)),c0,s0]);p1=np.column_stack([np.ones(len(x)),c1,s1])
        d0=np.column_stack([np.zeros(len(x)),-s0*freq,c0*freq]);d1=np.column_stack([np.zeros(len(x)),-s1*freq,c1*freq])
        ac=p0@matrix
        rho=1+coefficient[0]+np.sum(ac*p1,axis=1)
        grad=np.column_stack([np.sum((d0@matrix)*p1,axis=1),np.sum(ac*d1,axis=1)])
        return rho,grad



def matrices(train,dic,smoothing):
    k=dic.degree;axis=np.arange(-2*k,2*k+1)
    mu=np.zeros((len(axis),len(axis)),complex)
    for start in range(0,len(train),4000):
        x=train[start:start+4000]
        a=np.exp(1j*x[:,0,None]*axis);c=np.exp(1j*x[:,1,None]*axis)
        mu+=a.T@c
    mu/=len(train)
    mu*=np.exp(-.5*smoothing**2*(axis[:,None]**2+axis[None,:]**2))
    f=dic.freq
    delta=f[:,None]-f[None,:];total=f[:,None]+f[None,:]
    md=mu[delta[:,:,0]+2*k,delta[:,:,1]+2*k]
    mt=mu[total[:,:,0]+2*k,total[:,:,1]+2*k]
    cc,ss,cs=(md+mt).real,(md-mt).real,(mt-md).imag
    m=mu[f[:,0]+2*k,f[:,1]+2*k]
    mean=np.r_[np.sqrt(2)*m.real,np.sqrt(2)*m.imag]
    gram=np.block([[cc,cs],[cs.T,ss]])
    dot=f@f.T
    energy=np.block([[dot*ss,-dot*cs.T],[-dot*cs,dot*cc]])
    return gram,energy,mean


def gaussian_moments(dic, mean, covariance, order=32):
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    grid = np.stack(np.meshgrid(nodes,nodes,indexing="ij"),-1).reshape(-1,2)
    points = wrap(mean + np.sqrt(2)*grid@np.linalg.cholesky(covariance).T)
    probability = (weights[:,None]*weights[None,:]).ravel()/np.pi
    p,_ = dic.eval(points,False)
    return probability@p


def thickness(x):
    tree = cKDTree(wrap(x)+np.pi, boxsize=2*np.pi)
    _, neighbors = tree.query(wrap(x)+np.pi,k=12)
    delta = wrap(x[neighbors]-x[:,None,:])
    delta -= delta.mean(1,keepdims=True)
    cov = np.einsum("nki,nkj->nij",delta,delta)/11
    return float(np.median(np.sqrt(np.maximum(np.linalg.eigvalsh(cov)[:,0],0))))


def integrate(source, lam, basis, moments, dic, taus, rtol=1e-8, method="DOP853", atol=1e-10,
              max_evaluations=25000, max_seconds=180,diagnostics=None):
    from revision_common import PathMasks
    watch=PathMasks(len(source),scope='All adaptive RHS evaluations, including rejected stages; torus wrapping is not box projection')
    started=time.perf_counter()
    times=np.asarray(taus)/lam[0]
    counts=dict(nfev=0,points=0,floored=0,clipped=0,min_rho=float("inf"))
    def rhs(t,flat):
        if counts["nfev"] >= max_evaluations or time.perf_counter()-started > max_seconds:
            raise RuntimeError(f"Bounded integration exceeded {max_evaluations} RHS evaluations or {max_seconds} seconds; "
                               f"nfev={counts['nfev']}, elapsed={time.perf_counter()-started:.3f}, time={t:.8g}")
        weights=moments*np.exp(-lam*t)
        nonzero=np.flatnonzero(weights)
        # Skip only coefficients that have already underflowed to exact zero.
        # This does not introduce a spectral threshold or alter the retained modes.
        stop=int(nonzero[-1])+1 if len(nonzero) else 0
        coeff=basis[:,:stop]@weights[:stop]
        rho,grad=dic.contract(flat.reshape(source.shape),coeff)
        velocity=-grad/np.maximum(rho,1e-3)[:,None]
        speed=np.linalg.norm(velocity,axis=1)
        watch.velocity(rho,speed)
        counts["nfev"]+=1; counts["points"]+=len(source)
        counts["floored"]+=int(np.sum(rho<1e-3));counts["clipped"]+=int(np.sum(speed>20))
        counts["min_rho"]=min(counts["min_rho"],float(rho.min()))
        velocity*=np.minimum(1,20/np.maximum(speed,1e-12))[:,None]
        return velocity.ravel()
    try:
        solution=solve_ivp(rhs,(times[0],times[-1]),source.ravel(),method=method,rtol=rtol,atol=atol,
                           first_step=.0001,max_step=times[-1]/80,t_eval=times)
    finally:
        if diagnostics is not None:
            observed=watch.result();diagnostics['path_masks']=observed.pop('path_masks')
            diagnostics['events']=dict(counts,**observed,seconds=time.perf_counter()-started)
    if not solution.success:raise RuntimeError(solution.message)
    counts.update(seconds=time.perf_counter()-started,success=True,method=method,rtol=rtol,atol=atol,
                  floor_fraction=counts["floored"]/counts["points"],clip_fraction=counts["clipped"]/counts["points"],
                  diagnostic_scope=f"Interval tau={taus[0]:g} to {taus[-1]:g}, including rejected solver stages")
    path_info=watch.result();path_masks=path_info.pop('path_masks');counts.update(path_info)
    if diagnostics is not None:diagnostics['path_masks']=path_masks
    return wrap(solution.y.T.reshape(len(times),*source.shape)),times,counts


def load_npz(name):
    import io
    from manuscript_results import read_bytes
    with np.load(io.BytesIO(read_bytes('alanine/'+name))) as z:
        return {key:z[key] for key in z.files}


def load_config():
    from manuscript_results import read_bytes
    return json.loads(read_bytes('alanine/config.json'))


def inputs(split):
    data=load_npz('dataset.npz')
    train,small,reference=data['train_all'],data['train_small'],data[split]
    labels,centers,k=partition(small,True)
    group=labels(small)
    selected=small[group==np.argmax(np.bincount(group,minlength=k))]
    mean=np.arctan2(np.sin(selected).mean(0),np.cos(selected).mean(0))
    covariance=np.cov(wrap(selected-mean).T)*.7**2
    return train,reference,labels,centers,k,mean,covariance


def fit_spectrum(train,case,threads=1):
    started=time.perf_counter();dic=FourierDictionary(case['degree'])
    with threadpool_limits(limits=threads):
        gram,energy,mean=matrices(train,dic,case['smoothing'])
        gc=gram-np.outer(mean,mean)
        ev,u=eigh((gc+gc.T)/2)
        keep=ev>case['cutoff']*ev.max()
        white=u[:,keep]/np.sqrt(ev[keep])
        reduced=white.T@energy@white
        lam,z=eigh((reduced+reduced.T)/2)
        positive=lam>1e-10
        lam=lam[positive][:case['rank']]
        vectors=(white@z[:,positive])[:,:len(lam)]
        basis=np.vstack([-mean@vectors,vectors])
    error=float(np.max(abs(vectors.T@gc@vectors-np.eye(len(lam)))))
    assert error<1e-5
    return lam,basis,dict(rank=len(lam),dictionary_size=dic.size,lambda1=float(lam[0]),
             gram_kept=int(keep.sum()),orthogonality_error=error,fit_seconds=time.perf_counter()-started,threads=threads)


def source_points(seed,n,mean,cov,design):
    if design=='sobol':
        points=qmc.Sobol(2,scramble=True,seed=seed).random_base2(int(np.ceil(np.log2(n))))[:n]
        source=wrap(mean+ndtri(points)@np.linalg.cholesky(cov).T)
    else:source=wrap(np.random.default_rng(seed).multivariate_normal(mean,cov,n))
    assert np.isfinite(source).all()
    return source


def score(x,target,labels,k,target_width):
    mass=masses(x,labels,k)
    return dict(sw2=sw2(x,target,True),mass_tv=float(.5*abs(mass-masses(target,labels,k)).sum()),
                masses=mass.tolist(),local_width_ratio=thickness(x)/target_width)


def distribution_summary(data=None, record=None, arrays=None):
    """Recompute endpoint diagnostics from the shared comparison clouds."""
    import alanine_convergence as convergence
    if data is None:data,_=convergence.inputs()
    if record is None:record,arrays=convergence.load_results()
    labels,_,k=partition(None,centers=data['cluster_centers'])
    rows=[]
    for seed in convergence.SEEDS:
        i=data['record']['seeds'].index(seed)
        row=next(r for r in record['runs'] if r['seed']==seed and r['method']=='BKT')
        assert row['status']=='ok' and row['checkpoints'][-1]['s']==8.
        target=data['target'][i];width=thickness(target)
        initial=score(data['source'][i],target,labels,k,width)
        final=score(arrays[row['id']+'_clouds'][-1],target,labels,k,width)
        reference=score(data['reference_a'][i],data['reference_b'][i],labels,k,
                        thickness(data['reference_b'][i]))
        rows.append(dict(seed=seed,initial=initial,final=final,
                         reference_sw=reference['sw2'],reference_mass_tv=reference['mass_tv'],
                         reference_local_width_ratio=reference['local_width_ratio'],
                         target_masses=masses(target,labels,k).tolist()))
    return dict(s=8.,rank=256,particles=1000,representative_seed=1101,runs=rows,
                scope='The endpoint clouds are exactly those used in the three-method convergence comparison.')


def verify_saved():
    import alanine_convergence as convergence
    config=load_config();_,reference,labels,centers,k,mean,cov=inputs('test')
    data,dic=convergence.inputs();record,arrays=convergence.load_results()
    assert config['setting']==data['record']['setting'] and config['seeds']==list(convergence.SEEDS)
    assert data['lam'].shape==(256,) and data['basis'].shape==(3249,256)
    np.testing.assert_array_equal(mean,data['source_mean'])
    np.testing.assert_array_equal(cov,data['source_covariance'])
    np.testing.assert_array_equal(centers,data['cluster_centers'])
    for i,seed in enumerate(convergence.SEEDS):
        expected=source_points(seed,config['particles'],mean,cov,config['setting']['source_design'])
        np.testing.assert_array_equal(expected,data['source'][i])
        ids=np.random.default_rng(seed+9000).choice(len(reference),3*config['particles'],replace=False)
        for key,indices in zip(('target','reference_a','reference_b'),np.split(ids,3)):
            np.testing.assert_array_equal(reference[indices],data[key][i])
    fresh=distribution_summary(data,record,arrays)
    assert fresh==record['distribution']
    print('The three saved source/reference designs and all endpoint distribution diagnostics match.',flush=True)
    return dict(source_designs=3,distribution_metrics='exact match')


def reproduce(seed=None,refit=False):
    """Reproduce BKT at the same 256-mode settings as the convergence figure."""
    import alanine_convergence as convergence
    data,dic=convergence.inputs();record,arrays=convergence.load_results()
    fit_diagnostics=None
    if refit:
        train=load_npz('dataset.npz')['train_all']
        lam,basis,fit_diagnostics=fit_spectrum(train,data['record']['setting'])
        np.testing.assert_allclose(lam,data['lam'],rtol=1e-6,atol=1e-10)
        data.update(lam=lam,basis=basis)
    comparisons=[]
    for selected in convergence.SEEDS:
        if seed is not None and selected!=seed:continue
        run,clouds=convergence.transport(data,dic,256,'BKT',selected)
        assert run['status']=='ok',run['failure']
        saved=arrays[convergence.case_id(256,'BKT',selected)+'_clouds']
        error=float(np.sqrt(np.mean(wrap(clouds[-1]-saved[-1])**2)))
        sw_error=abs(run['checkpoints'][-1]['sw2']-next(
            r for r in record['runs'] if r['method']=='BKT' and r['seed']==selected)['checkpoints'][-1]['sw2'])
        row=dict(seed=selected,endpoint_wrapped_rms=error,sw2_difference=sw_error,refit=refit)
        comparisons.append(row);print(json.dumps(row),flush=True)
        assert error<1e-3 and sw_error<1e-4
    if not comparisons:raise ValueError('Requested seed is absent from the retained results.')
    return dict(comparisons=comparisons,fit=fit_diagnostics)


def report():
    from manuscript_results import write_report
    write_report()


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from plot_data_comparison import configure_style,content_bottom,LEGEND_GAP_PT,LEGEND_BOTTOM_MARGIN_PT
    configure_style('fig_alanine', 14)
    import alanine_convergence as convergence
    data,_=convergence.inputs();record,arrays=convergence.load_results()
    source,target=data['source'][0],data['target'][0]
    current=arrays[convergence.case_id(256,'BKT',1101)+'_clouds'][-1]
    summary=record['distribution']
    fig,axes=plt.subplots(2,2,figsize=(14,12.5))
    fig.subplots_adjust(left=.10,right=.98,bottom=.16,top=.93,wspace=.32,hspace=.65)
    for ax in axes.flat:ax.tick_params(axis='both',pad=8)
    for ax,x,title in zip(axes.flat[:3],[source,current,target],['Local source','BKT at $s=8$','Reference MD angles']):
        ax.scatter(x[:,0],x[:,1],s=7,alpha=.48,c='#0072B2',rasterized=True)
        ax.set(xlim=(-np.pi,np.pi),ylim=(-np.pi,np.pi),xlabel=r'$\phi$ (rad)',ylabel=r'$\psi$ (rad)',title=title)
        ax.set_xticks([-3,0,3]);ax.set_yticks([-3,0,3]);ax.set_aspect('equal',adjustable='box')
    ax=axes.flat[3]
    generated=[r['final']['sw2'] for r in summary['runs']]
    reference=[r['reference_sw'] for r in summary['runs']]
    for a,b_ in zip(generated,reference):ax.plot([0,1],[a,b_],'o-',color='#0072B2',alpha=.55)
    center,sd=np.mean(reference),np.std(reference,ddof=1)
    ax.axhspan(max(0,center-sd),center+sd,color='#777777',alpha=.12)
    ax.axhline(center,ls='--',color='#555555',label='Reference-cloud mean +/- SD')
    ax.set_xticks([0,1],['BKT','Reference'])
    ax.set(title=r'Sliced $W_2$',ylabel='Distance',xlim=(-.3,1.3));ax.set_ylim(bottom=0)
    handles,labels=ax.get_legend_handles_labels()
    legend=fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,0),frameon=False,borderpad=0,borderaxespad=0)
    for _ in range(5):
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        needed=(LEGEND_GAP_PT+LEGEND_BOTTOM_MARGIN_PT)*fig.dpi/72+legend.get_window_extent(renderer).height
        shift=(needed-content_bottom(fig,axes,renderer))/fig.bbox.height
        if abs(shift)<1e-6:break
        fig.subplots_adjust(bottom=fig.subplotpars.bottom+shift)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    top=(content_bottom(fig,axes,renderer)-LEGEND_GAP_PT*fig.dpi/72)/fig.bbox.height
    legend.set_bbox_to_anchor((.5,top),transform=fig.transFigure)
    fig.savefig(ROOT/'outputs/figures/fig_alanine.pdf')
    plt.close(fig)


class TensorRBF:
    def __init__(self, grid, width):
        self.axis = np.linspace(-np.pi, np.pi, grid, endpoint=False)
        self.centers = np.stack(np.meshgrid(self.axis, self.axis, indexing="ij"), -1).reshape(-1, 2)
        self.width = width
        self.size = grid*grid + 1
        self.d, self.periodic = 2, True
        self.active = np.arange(grid*grid)


    def factors(self, x):
        delta = x[:, :, None] - self.axis[None, None, :]
        p = np.exp(-(1-np.cos(delta))/self.width**2)
        dp = -np.sin(delta)*p/self.width**2
        return p[:,0], p[:,1], dp[:,0], dp[:,1]

    def eval(self, x, gradients=True):
        a, c, da, dc = self.factors(x)
        p = np.ones((len(x), self.size))
        p[:,1:] = (a[:,:,None]*c[:,None,:]).reshape(len(x), -1)[:,self.active]
        if not gradients:
            return p, None
        dp = np.zeros((len(x), self.size, 2))
        dp[:,1:,0] = (da[:,:,None]*c[:,None,:]).reshape(len(x), -1)[:,self.active]
        dp[:,1:,1] = (a[:,:,None]*dc[:,None,:]).reshape(len(x), -1)[:,self.active]
        return p, dp

    def contract(self, x, coefficient):
        a, c, da, dc = self.factors(x)
        full=np.zeros(len(self.axis)**2)
        full[self.active]=coefficient[1:]
        matrix = full.reshape(len(self.axis), len(self.axis))
        ac = a @ matrix
        rho = 1 + coefficient[0] + np.sum(ac*c, axis=1)
        grad = np.column_stack((np.sum((da@matrix)*c,axis=1), np.sum(ac*dc,axis=1)))
        return rho, grad

def fit_rbf(train, dic, rank, cutoff):
    started = time.perf_counter()
    gram = np.zeros((dic.size, dic.size))
    energy = np.zeros_like(gram)
    for start in range(0, len(train), 2000):
        p, dp = dic.eval(train[start:start + 2000])
        gram += p.T @ p
        for axis in range(dic.d):
            energy += dp[:, :, axis].T @ dp[:, :, axis]
    gram /= len(train)
    energy /= len(train)
    # Remove the constant by centering every RBF. This preserves an exact 1.
    mean = gram[0, 1:].copy()
    gc = gram[1:, 1:] - np.outer(mean, mean)
    ev, u = eigh((gc + gc.T) / 2)
    keep = ev > cutoff * ev.max()
    white = u[:, keep] / np.sqrt(ev[keep])
    reduced = white.T @ energy[1:, 1:] @ white
    lam, z = eigh((reduced + reduced.T) / 2)
    positive = lam > 1e-10
    lam, vectors = lam[positive][:rank], (white @ z[:, positive])[:, :rank]
    if len(lam) < 2:
        raise RuntimeError("Too few positive eigenvalues")
    basis = np.zeros((dic.size, len(lam)))
    basis[1:] = vectors
    basis[0] = -mean @ vectors
    orth_error = float(np.max(np.abs(basis.T @ gram @ basis - np.eye(len(lam)))))
    centered_error = float(np.max(np.abs(gram[0] @ basis)))
    return lam, basis, dict(rank=len(lam), lambda1=float(lam[0]),
                            lambda_max=float(lam[-1]), dictionary_size=dic.size,
                            gram_kept=int(keep.sum()), width=dic.width,
                            orthogonality_error=orth_error, centering_error=centered_error,
                            fit_seconds=time.perf_counter() - started)

def rbf_diagnostic(reproduce=False, seed=None):
    """Verify or reproduce the two RBF diagnostics retained in the manuscript.

    The collapse case uses seeds 301-303 at tau=.25 and 16. The early-time
    control uses seeds 901-905 at tau=.25. These use iid source clouds;
    they are not paired with the Fourier/Sobol comparison.
    """
    saved=load_npz('rbf_diagnostic.npz')
    record=json.loads(str(saved['record']))
    train,reference,labels,centers,k,mean,cov=inputs('test')
    case=record['setting'];dic=TensorRBF(case['grid'],case['width'])
    if reproduce:
        train=wrap(train+np.random.default_rng(91073).normal(scale=case['smoothing'],size=train.shape))
        with threadpool_limits(limits=4):
            lam,basis,spec=fit_rbf(train,dic,case['rank'],case['cutoff'])
        m32=gaussian_moments(dic,mean,cov,32)@basis
        m48=gaussian_moments(dic,mean,cov,48)@basis
        moments=m48 if np.linalg.norm(m48-m32)>1e-8 else m32
        assert abs(lam[0]-record['spectrum']['lambda1'])<1e-10
        saved.update(lam=lam,basis=basis,moments=moments,cluster_centers=centers)
    checked=0
    for name in ('collapse','control'):
        case_record=record[name];taus=case_record['taus'];n=case_record['particles']
        for i,row in enumerate(case_record['runs']):
            if seed is not None and row['seed']!=seed:continue
            source=source_points(row['seed'],n,mean,cov,'iid')
            ids=np.random.default_rng(row['seed']+9000).choice(len(reference),3*n,replace=False)
            target,ra,rb=[reference[j] for j in np.split(ids,3)]
            if reproduce:
                paths,_,_=integrate(source,lam,basis,moments,dic,taus)
            else:
                paths=saved[name+'_paths'][i]
                for key,value in [('source',source),('target',target),('reference_a',ra),('reference_b',rb)]:
                    assert np.array_equal(value,saved[name+'_'+key][i])
            error=0.
            for cp in row['checkpoints']:
                idx=taus.index(cp['tau'])
                measured=score(paths[idx],target,labels,k,thickness(target))
                for metric in ('sw2','mass_tv','local_width_ratio'):
                    error=max(error,abs(measured[metric]-cp[metric]))
            assert error<1e-4,(name,row['seed'],error)
            assert abs(sw2(ra,rb,True)-row['reference_sw'])<1e-12
            checked+=1
            print(json.dumps(dict(case=name,seed=row['seed'],max_metric_difference=error)),flush=True)
    if checked==0:raise ValueError('Requested seed is absent from the retained RBF results.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['verify','reproduce','report','plot'],required=True)
    parser.add_argument('--case',choices=['fourier','rbf'],default='fourier')
    parser.add_argument('--seed',type=int)
    parser.add_argument('--refit',action='store_true')
    args=parser.parse_args()
    if args.case!='fourier' and args.stage=='plot':
        parser.error('The retained PDF shows the Fourier comparison at s=8; omit --case to redraw it.')
    with threadpool_limits(limits=1):
        if args.case=='rbf' and args.stage in ('verify','reproduce'):
            rbf_diagnostic(reproduce=args.stage=='reproduce', seed=args.seed)
        else:
            {'verify':verify_saved,'reproduce':lambda:reproduce(args.seed,args.refit),'report':report,'plot':plot}[args.stage]()
