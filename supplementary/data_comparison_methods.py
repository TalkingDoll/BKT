"""Data-only finite-lag drift, Euler-Maruyama and exact KDE-flow baselines.

This module does not load a notebook, generate training data or write results.
The dictionary and paired trajectory arrays are supplied by the caller. The
fixed defaults are specified before looking at experiment results: column-RMS
scaled gradient regression with ridge 1e-8; EM step .002; RK4 step .05; full
Silverman KDE covariance plus 1e-8 I; exact blockwise pair sums, including self.

Set BLAS thread environment variables before importing NumPy in the calling
process. The defaults below also enforce one thread when this module imports
NumPy first. Run implementation checks and one synthetic KDE benchmark with:
  uv run --with numpy==2.4.6 --with scipy==1.17.1 python supplementary/data_comparison_methods.py --check --benchmark
"""

from __future__ import annotations

import os
for _thread_variable in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import argparse
import json
import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.linalg import solve, solve_triangular
from scipy.spatial.distance import cdist
from scipy.special import logsumexp, ndtri


def _finite_points(X, name="particles"):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or not len(X) or not np.isfinite(X).all():
        raise ValueError(f"{name} must be a finite nonempty (samples, dimensions) array.")
    return X


@dataclass
class GradientDrift:
    """Conservative finite-lag drift b_hat(x)=-sum_j a_j grad psi_j(x).

    The additive constant potential is discarded. Finite-lag regression
    estimates conditional mean increments divided by tau; it is not asserted
    to recover the infinitesimal drift without finite-lag bias.
    """

    dictionary: object
    coefficients: np.ndarray
    column_rms: np.ndarray
    diagnostics: dict
    fit_seconds: float

    def __call__(self, X):
        _, gradient = self.dictionary.eval(np.asarray(X, dtype=float))
        return -np.einsum("mjd,j->md", gradient[:, 1:, :], self.coefficients, optimize=True)


def _condition(eigenvalues):
    smallest, largest = float(eigenvalues[0]), float(eigenvalues[-1])
    return float(largest/smallest) if smallest > 0 else None


def fit_gradient_drift(dictionary, Xd, Yd, tau=.1, ridge=1e-8, chunk=5000):
    """Fit all vector components jointly with a common potential coefficient.

    Rows of the regression matrix are -grad psi_j(X_i) for each coordinate,
    and targets are (Y_i-X_i)/tau. Gram and target moments are normalized by
    n*d. Every nonconstant column is divided by its training RMS. The fixed
    ridge is applied to this normalized Gram matrix, without data tuning.
    """
    started = time.perf_counter()
    Xd = _finite_points(Xd, "Xd"); Yd = _finite_points(Yd, "Yd")
    if Xd.shape != Yd.shape or tau <= 0 or ridge <= 0 or chunk <= 0:
        raise ValueError("Matching pair arrays and positive tau, ridge and chunk are required.")
    n, d = Xd.shape
    J = dictionary.size()
    if J < 2:
        raise ValueError("Dictionary must contain a constant and nonconstant functions.")
    gram = np.zeros((J-1, J-1)); rhs = np.zeros(J-1); target_second = 0.
    for start in range(0, n, chunk):
        _, gradients = dictionary.eval(Xd[start:start+chunk])
        if gradients.shape != (min(chunk, n-start), J, d):
            raise ValueError("Dictionary gradient shape must be (samples, functions, dimensions).")
        if np.any(gradients[:, 0, :] != 0):
            raise ValueError("The first dictionary function must be the constant with zero gradient.")
        A = -gradients[:, 1:, :].transpose(0, 2, 1).reshape(-1, J-1)
        b = ((Yd[start:start+chunk]-Xd[start:start+chunk])/tau).reshape(-1)
        gram += A.T @ A
        rhs += A.T @ b
        target_second += float(b @ b)
    gram /= n*d; rhs /= n*d; target_second /= n*d
    column_rms = np.sqrt(np.diag(gram))
    if not np.isfinite(column_rms).all() or np.any(column_rms <= 0):
        raise FloatingPointError("A nonconstant gradient feature has zero or nonfinite training RMS.")
    scaled = gram / column_rms[:, None] / column_rms[None, :]
    scaled = .5*(scaled+scaled.T)
    regularized = scaled + ridge*np.eye(J-1)
    scaled_coefficient = solve(regularized, rhs/column_rms, assume_a="pos")
    coefficients = scaled_coefficient/column_rms
    if not np.isfinite(coefficients).all():
        raise FloatingPointError("Nonfinite drift regression coefficients.")
    raw_eigenvalues = np.linalg.eigvalsh(gram)
    scaled_eigenvalues = np.linalg.eigvalsh(scaled)
    regularized_eigenvalues = scaled_eigenvalues+ridge
    residual_second = target_second-2*float(coefficients @ rhs)+float(coefficients @ gram @ coefficients)
    tolerance = 1e-11*max(1., target_second)
    if residual_second < -tolerance:
        raise FloatingPointError("Regression residual moment is negative beyond rounding tolerance.")
    diagnostics = dict(n_pairs=n, dimension=d, dictionary_functions=J,
        fitted_gradient_functions=J-1, constant_column_dropped=True, tau=float(tau), ridge=float(ridge),
        scaling="column RMS over n*d coordinate observations", gram_normalization=n*d,
        column_rms_min=float(column_rms.min()), column_rms_max=float(column_rms.max()),
        gram_eigenvalue_min=float(raw_eigenvalues[0]), gram_eigenvalue_max=float(raw_eigenvalues[-1]),
        gram_condition=_condition(raw_eigenvalues),
        normalized_gram_eigenvalue_min=float(scaled_eigenvalues[0]),
        normalized_gram_eigenvalue_max=float(scaled_eigenvalues[-1]),
        normalized_gram_condition=_condition(scaled_eigenvalues),
        regularized_gram_condition=_condition(regularized_eigenvalues),
        nonpositive_numerical_gram_eigenvalues=int(np.count_nonzero(scaled_eigenvalues <= 0)),
        condition_null_means="nonpositive smallest numerical eigenvalue; condition is not finite-positive",
        target_coordinate_rms=float(np.sqrt(target_second)),
        residual_coordinate_rms=float(np.sqrt(max(0., residual_second))),
        finite_lag_caveat="Conditional finite-lag mean increment divided by tau; no infinitesimal-drift unbiasedness claim.")
    return GradientDrift(dictionary, coefficients, column_rms, diagnostics, time.perf_counter()-started)


def silverman_bandwidth(particles, ridge=1e-8):
    """Full covariance H = [M(d+2)/4]^(-2/(d+4)) cov_ddof1(X) + ridge I."""
    X = _finite_points(particles)
    M, d = X.shape
    if M < 2 or ridge <= 0:
        raise ValueError("At least two particles and positive covariance regularization are required.")
    sample_covariance = np.atleast_2d(np.cov(X, rowvar=False, ddof=1))
    factor = (M*(d+2)/4.)**(-1./(d+4))
    H = factor*factor*sample_covariance+ridge*np.eye(d)
    return H, dict(silverman_factor=float(factor), covariance_ridge=float(ridge),
                   covariance_ddof=1, particles=M, dimension=d)


def gaussian_kde_score(particles, queries=None, bandwidth=None, block_size=256,
                       covariance_ridge=1e-8, return_info=False):
    """Exact finite Gaussian-mixture score, with all M centers including self.

    If queries is omitted, evaluate the score at the current particle cloud.
    H is recomputed from that cloud unless explicitly supplied (the supplied-H
    option is useful for independent derivative checks). Blocks change memory
    usage only; no neighbors, random features or subsampling are used.
    """
    X = _finite_points(particles)
    Q = X if queries is None else _finite_points(queries, "queries")
    if Q.shape[1] != X.shape[1] or block_size <= 0:
        raise ValueError("Query dimensions must agree and block size must be positive.")
    if bandwidth is None:
        H, info = silverman_bandwidth(X, ridge=covariance_ridge)
    else:
        H = np.asarray(bandwidth, dtype=float)
        info = dict(bandwidth_supplied=True)
    d = X.shape[1]
    if H.shape != (d, d) or not np.isfinite(H).all():
        raise ValueError("Bandwidth must be a finite square matrix of the correct dimension.")
    chol = np.linalg.cholesky(H)
    Z = solve_triangular(chol, X.T, lower=True, check_finite=False).T
    Zq = Z if queries is None else solve_triangular(chol, Q.T, lower=True, check_finite=False).T
    inverse = solve(H, np.eye(d), assume_a="pos")
    scores = np.empty_like(Q)
    for start in range(0, len(Q), block_size):
        stop = min(start+block_size, len(Q))
        log_weights = -.5*cdist(Zq[start:stop], Z, metric="sqeuclidean")
        log_weights -= log_weights.max(axis=1, keepdims=True)
        weights = np.exp(log_weights)
        weighted_centers = (weights @ X)/weights.sum(axis=1, keepdims=True)
        scores[start:stop] = (weighted_centers-Q[start:stop]) @ inverse
    if not np.isfinite(scores).all():
        raise FloatingPointError("Nonfinite exact KDE score; no speed cap was applied.")
    if return_info:
        eigenvalues = np.linalg.eigvalsh(H)
        info.update(bandwidth_eigenvalue_min=float(eigenvalues[0]),
                    bandwidth_eigenvalue_max=float(eigenvalues[-1]),
                    bandwidth_condition=float(eigenvalues[-1]/eigenvalues[0]),
                    score_norm_max=float(np.linalg.norm(scores, axis=1).max()),
                    kernel_centers=len(X), include_self=True, exact_pair_sums=True,
                    block_size=int(block_size))
        return scores, info
    return scores




def run_baseline(method, X0, drift: Callable, T, box, dt=None, seed=None,
                 beta_index=0, checkpoints=None, checkpoint_callback=None,
                 block_size=256):
    """Run B (Euler-Maruyama) or D (drift minus exact current KDE score).

    Checkpoint callback signature is callback(actual_time, particle_copy).
    Both callback execution and creating the callback's private particle copy
    are excluded from sampling_seconds. Returned checkpoint arrays are the
    pre-callback states, so callbacks cannot mutate a trajectory. nsteps uses
    int(round(T/dt)), exactly as in the notebook; no remainder step is added.
    ``seed`` is the source replicate index s, not the complete stochastic seed:
    B uses SeedSequence(20000+s).spawn(beta_index+1)[beta_index].
    """
    method = str(method).upper()
    if method not in ("B", "D"):
        raise ValueError("method must be 'B' or 'D'.")
    X = _finite_points(X0, "X0").copy()
    box = np.asarray(box, dtype=float)
    if box.shape != (X.shape[1], 2) or np.any(box[:, 0] >= box[:, 1]) or not np.isfinite(box).all():
        raise ValueError("Box must have one ordered finite lower/upper pair per dimension.")
    dt = (.002 if method == "B" else .05) if dt is None else float(dt)
    if T <= 0 or dt <= 0:
        raise ValueError("Positive horizon and step are required.")
    nsteps = int(round(T/dt))
    if nsteps <= 0:
        raise ValueError("Rounded horizon must include at least one step.")
    if method == "B":
        if seed is None or beta_index < 0 or int(beta_index) != beta_index:
            raise ValueError("B requires a source replicate seed and a nonnegative integer beta_index.")
        sequence = np.random.SeedSequence(20000+int(seed)).spawn(int(beta_index)+1)[int(beta_index)]
        rng = np.random.default_rng(sequence)
        rng_info = dict(base_seed=20000+int(seed), beta_index=int(beta_index), spawn_key=list(sequence.spawn_key))
    else:
        rng_info = None
    requested = np.asarray([] if checkpoints is None else checkpoints, dtype=float)
    if not np.isfinite(requested).all() or np.any(requested < 0) or np.any(requested > T+1e-12):
        raise ValueError("Checkpoints must be finite and between zero and the requested horizon.")
    checkpoint_steps = sorted(set([0, nsteps]+[min(nsteps, max(0, int(round(t/dt)))) for t in requested]))
    scheduled = set(checkpoint_steps)
    states=[]; actual_times=[]; actual_steps=[]; cumulative_seconds=[]; callback_results=[]
    events=dict(field_evaluations=0, drift_evaluations=0, kde_evaluations=0,
                covariance_recomputations=0, clip_particle_events=0, clip_coordinate_events=0,
                clip_calls=0, speed_cap_events=0, initial_projection_events=0,
                nonfinite_events=0, maximum_raw_velocity_norm=0., maximum_drift_norm=0.,
                minimum_kde_bandwidth_eigenvalue=None, maximum_kde_bandwidth_eigenvalue=None,
                maximum_kde_bandwidth_condition=None)
    affected = np.zeros(len(X), dtype=bool)
    callback_seconds=0.; started=time.perf_counter()

    def clip(Y):
        nonlocal affected
        if not np.isfinite(Y).all():
            events["nonfinite_events"] += 1
            raise FloatingPointError("Nonfinite particle update before box clipping.")
        changed = (Y < box[:,0]) | (Y > box[:,1])
        mask = changed.any(axis=1)
        affected |= mask
        events["clip_calls"] += 1
        events["clip_particle_events"] += int(mask.sum())
        events["clip_coordinate_events"] += int(changed.sum())
        return np.clip(Y, box[:,0], box[:,1])

    def velocity(Y):
        b=np.asarray(drift(Y), dtype=float)
        events["field_evaluations"] += 1; events["drift_evaluations"] += 1
        if b.shape != Y.shape or not np.isfinite(b).all():
            events["nonfinite_events"] += 1
            raise FloatingPointError("Learned drift has a wrong shape or nonfinite entries.")
        events["maximum_drift_norm"] = max(events["maximum_drift_norm"], float(np.linalg.norm(b, axis=1).max()))
        if method == "D":
            score,info=gaussian_kde_score(Y, block_size=block_size, return_info=True)
            events["kde_evaluations"] += 1; events["covariance_recomputations"] += 1
            for output,key,operation in (("minimum_kde_bandwidth_eigenvalue","bandwidth_eigenvalue_min",min),
                                         ("maximum_kde_bandwidth_eigenvalue","bandwidth_eigenvalue_max",max),
                                         ("maximum_kde_bandwidth_condition","bandwidth_condition",max)):
                events[output] = info[key] if events[output] is None else operation(events[output],info[key])
            b=b-score
        events["maximum_raw_velocity_norm"] = max(events["maximum_raw_velocity_norm"],float(np.linalg.norm(b,axis=1).max()))
        return b

    def checkpoint(step):
        nonlocal callback_seconds
        actual_times.append(step*dt); actual_steps.append(step); states.append(X.copy())
        cumulative_seconds.append(time.perf_counter()-started-callback_seconds)
        if checkpoint_callback is None:
            callback_results.append(None)
        else:
            callback_started=time.perf_counter()
            callback_results.append(checkpoint_callback(step*dt, X.copy()))
            callback_seconds += time.perf_counter()-callback_started

    checkpoint(0)
    completed=0; failure=None
    for i in range(nsteps):
        try:
            if method == "B":
                X = clip(X+dt*velocity(X)+np.sqrt(2*dt)*rng.standard_normal(X.shape))
            else:
                k1=velocity(X)
                k2=velocity(clip(X+.5*dt*k1))
                k3=velocity(clip(X+.5*dt*k2))
                k4=velocity(clip(X+dt*k3))
                X=clip(X+dt/6*(k1+2*k2+2*k3+k4))
        except (FloatingPointError, np.linalg.LinAlgError) as exception:
            failure=dict(exception_type=type(exception).__name__,message=str(exception),
                         failed_step=i+1,last_completed_time=completed*dt)
            break
        completed=i+1
        if completed in scheduled:
            checkpoint(completed)
    if completed not in actual_steps:
        checkpoint(completed)
    events["clipped_unique_particles"]=int(affected.sum())
    return dict(method=method,status="failed" if failure else "completed",failure=failure,
                final=X.copy(),checkpoint_times=np.asarray(actual_times),
                checkpoint_step_indices=np.asarray(actual_steps,dtype=int),
                checkpoints=np.asarray(states),checkpoint_sampling_seconds=np.asarray(cumulative_seconds),
                callback_results=callback_results,events=events,
                sampling_seconds=time.perf_counter()-started-callback_seconds,callback_seconds=callback_seconds,
                dt=dt,requested_horizon=float(T),effective_horizon=nsteps*dt,completed_horizon=completed*dt,
                requested_steps=nsteps,completed_steps=completed,rng=rng_info,
                time_convention="int(round(T/dt)) full steps; no fractional remainder step",
                initial_particles_clipped=False,
                method_details="learned finite-lag drift plus sqrt(2) noise" if method=="B" else
                    "learned finite-lag drift minus exact current-cloud Gaussian KDE score; full covariance recomputed at every RK4 stage; no speed cap")


def run_checks():
    """Small deterministic checks only; no experiment or tuning is performed."""
    class QuadraticDictionary:
        def size(self): return 6
        def eval(self,X):
            x,y=X.T; P=np.column_stack([np.ones(len(X)),.5*x*x,.5*y*y,x*y,x,y])
            G=np.zeros((len(X),6,2)); G[:,1,0]=x;G[:,2,1]=y
            G[:,3,0]=y;G[:,3,1]=x;G[:,4,0]=1;G[:,5,1]=1
            return P,G
    rng=np.random.default_rng(948371)
    X=rng.normal(size=(1000,2)); truth=np.array([1.3,.8,.2,-.1,.3])
    dictionary=QuadraticDictionary(); _,G=dictionary.eval(X)
    drift=-np.einsum('mjd,j->md',G[:,1:,:],truth)
    fit=fit_gradient_drift(dictionary,X,X+.1*drift)
    regression_error=float(np.max(np.abs(fit.coefficients-truth)))
    np.testing.assert_allclose(fit.coefficients,truth,atol=3e-8,rtol=3e-8)
    cloud=rng.normal(size=(73,2)); queries=np.array([[.1,-.2],[.7,.5],[-.4,.8]])
    H,_=silverman_bandwidth(cloud)
    score=gaussian_kde_score(cloud,queries=queries,bandwidth=H,block_size=2)
    inverse=np.linalg.inv(H)
    def logdensity(q):
        delta=cloud-q
        return logsumexp(-.5*np.einsum('mi,ij,mj->m',delta,inverse,delta))
    difference=np.empty_like(score); epsilon=1e-5
    for i,q in enumerate(queries):
        for j in range(2):
            shift=np.zeros(2);shift[j]=epsilon
            difference[i,j]=(logdensity(q+shift)-logdensity(q-shift))/(2*epsilon)
    kde_derivative_error=float(np.max(np.abs(score-difference)))
    np.testing.assert_allclose(score,difference,atol=1e-8,rtol=1e-8)
    # Symmetric quantile product cloud represents a stationary Gaussian. The
    # known smoothed population score is -x/(1+Silverman_factor^2), up to the
    # negligible fixed covariance ridge. This is a sanity check, not a new run.
    q=ndtri((np.arange(40)+.5)/40); xx,yy=np.meshgrid(q,q)
    gaussian=np.column_stack([xx.ravel(),yy.ravel()])
    probes=np.array([[0.,0.],[.4,-.3],[-.4,.3]])
    scores,info=gaussian_kde_score(gaussian,queries=probes,return_info=True)
    expected=-probes/(1+info['silverman_factor']**2)
    stationary_error=float(np.max(np.abs(scores-expected)))
    assert stationary_error<.03 and np.max(np.abs(scores[0]))<1e-12
    assert np.max(np.abs(scores[1]+scores[2]))<1e-12
    # Constant drift and the actual rounded-step convention give an exact EM
    # reference when we independently replay the specified random stream.
    small=np.zeros((8,2)); b=lambda x: np.full_like(x,.15)
    result=run_baseline('B',small,b,T=.0104,box=[[-10,10],[-10,10]],seed=2,beta_index=1,
                        checkpoints=[0,.004,.0104],checkpoint_callback=lambda t,x: float(np.mean(x)))
    generator=np.random.default_rng(np.random.SeedSequence(20002).spawn(2)[1]);manual=small.copy()
    for _ in range(round(.0104/.002)):
        manual = manual+.002*np.full_like(manual,.15)+np.sqrt(.004)*generator.standard_normal(manual.shape)
    np.testing.assert_array_equal(result['final'],manual)
    assert result['effective_horizon']==.01 and result['events']['kde_evaluations']==0
    assert np.all(np.diff(result['checkpoint_sampling_seconds'])>=0)
    # Symmetric stationary particles retain exact antisymmetry through the
    # uncapped KDE RK4 stages; recomputation count is checked explicitly.
    symmetric=np.vstack([rng.normal(size=(10,2)),-rng.normal(size=(10,2))])
    symmetric=np.vstack([symmetric,-symmetric])
    dresult=run_baseline('D',symmetric,lambda x:-x,T=.05,box=[[-10,10],[-10,10]])
    assert dresult['status']=='completed' and dresult['events']['kde_evaluations']==4
    np.testing.assert_allclose(dresult['final'][:20],-dresult['final'][20:],atol=1e-12)
    assert dresult['events']['speed_cap_events']==0
    return dict(status='PASS',manufactured_gradient_coefficient_max_error=regression_error,
                kde_logdensity_finite_difference_max_error=kde_derivative_error,
                stationary_gaussian_smoothed_score_sanity_max_error=stationary_error,
                em_rng_replay='bitwise identical',rounded_horizon='verified',
                kde_rk4_stage_recomputations='four for one full step',
                kde_rk4_antisymmetry='passed',hyperparameter_selection=False)


def benchmark_kde():
    """One synthetic M=2000 exact KDE stage only; no actual experiment data."""
    X=np.random.default_rng(981735).normal(size=(2000,2))
    started=time.perf_counter()
    score,info=gaussian_kde_score(X,block_size=256,return_info=True)
    seconds=time.perf_counter()-started
    return dict(particles=2000,dimensions=2,block_size=256,stage_seconds=seconds,
                estimated_four_stage_seconds=4*seconds,finite=bool(np.isfinite(score).all()),
                input='single synthetic standard Gaussian cloud; no trajectories run',info=info)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--benchmark',action='store_true')
    arguments=parser.parse_args()
    if not arguments.check and not arguments.benchmark:
        parser.error('This module has no experiment entry point; use --check or --benchmark.')
    if arguments.check:
        print(json.dumps(run_checks(),indent=2,allow_nan=False),flush=True)
    if arguments.benchmark:
        print(json.dumps(benchmark_kde(),indent=2,allow_nan=False),flush=True)


if __name__=='__main__':
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        main()
