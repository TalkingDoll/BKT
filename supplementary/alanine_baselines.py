"""Periodic target-score estimation and deterministic empirical KDE flow.

The fit approximates the same wrapped-Gaussian-smoothed angular marginal as
the alanine Dirichlet estimator. It does not estimate physical MD kinetics.
All public routines operate in memory; this module writes no experiment files.
"""
from __future__ import annotations

import hashlib
import json
import math
import time

import numba
from numba import njit
import numpy as np
from scipy.ndimage import spline_filter, gaussian_filter
from scipy.integrate import BDF

TWO_PI = 2.0 * np.pi


def _sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def fit_target(train, grid_size=512, smoothing=0.1):
    """Positive periodic target fit with the prescribed Gaussian smoothing.

    Cloud-in-cell deposition adds variance spacing**2/6 per coordinate. The
    separable Gaussian convolution subtracts this assignment variance from
    its kernel variance, preserving the prescribed smoothing to leading
    order. Full-torus positive convolution avoids FFT cancellation in dilute
    regions. A machine-tiny floor only protects the logarithm from underflow.
    The periodic cubic B-spline interpolates log density and is differentiated
    analytically, giving a conservative target score.
    """
    started = time.perf_counter()
    train = np.asarray(train, dtype=np.float64)
    if train.ndim != 2 or train.shape[1] != 2 or not len(train) or not np.isfinite(train).all():
        raise ValueError('Training coordinates must be a nonempty finite N-by-2 array.')
    n = int(grid_size)
    if n < 16 or n != grid_size or smoothing <= 0:
        raise ValueError('Invalid grid or smoothing.')
    spacing = TWO_PI / n
    coordinate = ((train + np.pi) % TWO_PI) / spacing
    lower = np.floor(coordinate).astype(np.int64)
    fraction = coordinate - lower
    mass = np.zeros((n, n), dtype=np.float64)
    for i in (0, 1):
        for j in (0, 1):
            weight = (fraction[:, 0] if i else 1 - fraction[:, 0]) * (fraction[:, 1] if j else 1 - fraction[:, 1])
            np.add.at(mass, ((lower[:, 0] + i) % n, (lower[:, 1] + j) % n), weight / len(train))
    assignment_variance = spacing**2 / 6
    if smoothing**2 <= assignment_variance:
        raise ValueError('The target grid does not resolve the prescribed smoothing.')
    kernel_sigma = float(np.sqrt(smoothing**2 - assignment_variance))
    raw_density = gaussian_filter(mass, sigma=kernel_sigma / spacing,
                                  mode='wrap', radius=n // 2) / spacing**2
    floor = float(np.finfo(np.float64).tiny)
    floored = raw_density < floor
    density = np.maximum(raw_density, floor)
    normalization = float(density.sum() * spacing**2)
    density /= normalization
    coefficients = np.ascontiguousarray(spline_filter(np.log(density), order=3, mode='grid-wrap'))
    metadata = dict(
        estimator='CIC histogram, positive separable periodic Gaussian convolution with assignment-variance correction, cubic B-spline log density',
        target='Unit-mobility reversible surrogate of the smoothed angular marginal; not the physical MD generator',
        grid_size=n, spacing=float(spacing), smoothing=float(smoothing),
        assignment_variance=float(assignment_variance), kernel_sigma=kernel_sigma,
        convolution_radius=n // 2, absolute_density_floor=floor, density_floor=float(floor / normalization),
        density_floor_grid_nodes=int(floored.sum()), density_floor_grid_fraction=float(floored.mean()),
        raw_density_minimum=float(raw_density.min()), density_normalization_before_rescaling=normalization,
        train_frames=len(train), train_sha256=_sha(train), coefficient_sha256=_sha(coefficients),
        fit_seconds=time.perf_counter() - started, numpy=np.__version__, numba=numba.__version__,
    )
    return dict(log_density_coefficients=coefficients, density=density, metadata=metadata)


@njit(cache=False)
def _weights(t):
    t2 = t * t
    t3 = t2 * t
    return ((1 - t)**3 / 6, (3 * t3 - 6 * t2 + 4) / 6,
            (-3 * t3 + 3 * t2 + 3 * t + 1) / 6, t3 / 6)


@njit(cache=False)
def _derivatives(t):
    return (-0.5 * (1 - t)**2, 1.5 * t * t - 2 * t,
            -1.5 * t * t + t + 0.5, 0.5 * t * t)


@njit(cache=False)
def _score_one(x, y, coefficients):
    n = coefficients.shape[0]
    scale = n / TWO_PI
    u = ((x + np.pi) % TWO_PI) * scale
    v = ((y + np.pi) % TWO_PI) * scale
    i, j = int(math.floor(u)), int(math.floor(v))
    wx, wy = _weights(u - i), _weights(v - j)
    dx, dy = _derivatives(u - i), _derivatives(v - j)
    gx, gy = 0.0, 0.0
    for a in range(4):
        row = (i + a - 1) % n
        value, derivative = 0.0, 0.0
        for b in range(4):
            c = coefficients[row, (j + b - 1) % n]
            value += c * wy[b]
            derivative += c * dy[b]
        gx += dx[a] * value
        gy += wx[a] * derivative
    return scale * gx, scale * gy


@njit(cache=False)
def _log_density_one(x, y, coefficients):
    n = coefficients.shape[0]
    u = ((x + np.pi) % TWO_PI) * n / TWO_PI
    v = ((y + np.pi) % TWO_PI) * n / TWO_PI
    i, j = int(math.floor(u)), int(math.floor(v))
    wx, wy = _weights(u - i), _weights(v - j)
    value = 0.0
    for a in range(4):
        for b in range(4):
            value += coefficients[(i + a - 1) % n, (j + b - 1) % n] * wx[a] * wy[b]
    return value


@njit(cache=False)
def _scores(points, coefficients):
    result = np.empty_like(points)
    for i in range(len(points)):
        result[i, 0], result[i, 1] = _score_one(points[i, 0], points[i, 1], coefficients)
    return result


def _coefficients(fit):
    coefficients = np.asarray(fit['log_density_coefficients'], dtype=np.float64)
    if coefficients.ndim != 2 or coefficients.shape[0] != coefficients.shape[1] or not np.isfinite(coefficients).all():
        raise ValueError('The fitted periodic scalar field must be a finite square array.')
    return np.ascontiguousarray(coefficients)


def target_score(points, fit):
    """Evaluate the analytic periodic gradient of the fitted log density."""
    points = np.ascontiguousarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError('Points must be a finite N-by-2 array.')
    return _scores(points, _coefficients(fit))


def direct_wrapped_kernel_score(points, train, smoothing=0.1):
    """Small read-only reference: direct wrapped-Gaussian mixture and gradient."""
    train = np.asarray(train, dtype=np.float64)
    values, gradients = [], []
    shifts = TWO_PI * np.arange(-2, 3)
    for point in np.asarray(points, dtype=np.float64):
        delta = (point - train + np.pi) % TWO_PI - np.pi
        d = delta[:, :, None] + shifts[None, None, :]
        log_weight = -0.5 * (d / smoothing)**2
        # One shared shift per coordinate avoids underflow without changing
        # relative component weights or the ratio defining the score.
        offset = log_weight.max(axis=(0, 2))
        weight = np.exp(log_weight - offset[None, :, None])
        kernel = weight.sum(axis=2)
        derivative = (-d / smoothing**2 * weight).sum(axis=2)
        total = (kernel[:, 0] * kernel[:, 1]).sum()
        gradients.append([(derivative[:, 0] * kernel[:, 1]).sum() / total,
                          (kernel[:, 0] * derivative[:, 1]).sum() / total])
        values.append(total / len(train) * np.exp(offset.sum()) / (2 * np.pi * smoothing**2))
    return np.asarray(values), np.asarray(gradients)


def _kde_wrap(points):
    return (points + np.pi) % TWO_PI - np.pi


@njit(cache=False)
def _periodic_kernel_axis(delta, variance, image_radius):
    delta = (delta + np.pi) % TWO_PI - np.pi
    value = gradient = hessian = 0.0
    for image in range(-image_radius, image_radius + 1):
        offset = delta + TWO_PI * image
        scaled = offset / variance
        weight = math.exp(-0.5 * offset * scaled)
        value += weight
        gradient -= scaled * weight
        hessian += (scaled * scaled - 1.0 / variance) * weight
    return value, gradient, hessian


@njit(cache=False, inline='always')
def _particle_kernel_terms(delta_x, delta_y, variance, image_radius):
    if variance <= 0.15**2:
        # At sigma=.1, omitted adjacent-image weights are below 5e-215.
        # Every particle density includes its unit self term, so omitting
        # these images is far below double precision for particle scores.
        x = (delta_x + np.pi) % TWO_PI - np.pi
        y = (delta_y + np.pi) % TWO_PI - np.pi
        ax, ay = x / variance, y / variance
        weight = math.exp(-0.5 * (x * ax + y * ay))
        return (weight, -ax * weight, -ay * weight,
                (ax * ax - 1.0 / variance) * weight,
                ax * ay * weight, (ay * ay - 1.0 / variance) * weight)
    wx, dx, dxx = _periodic_kernel_axis(delta_x, variance, image_radius)
    wy, dy, dyy = _periodic_kernel_axis(delta_y, variance, image_radius)
    return wx * wy, dx * wy, wx * dy, dxx * wy, dx * dy, wx * dyy


@njit(cache=False)
def _particle_kernel_sums(points, variance, image_radius):
    count = len(points)
    self_value = _periodic_kernel_axis(0.0, variance, image_radius)[0] ** 2
    density = np.full(count, self_value)
    gradient = np.zeros((count, 2))
    for i in range(count):
        for j in range(i):
            weight, gx, gy, _, _, _ = _particle_kernel_terms(
                points[i, 0] - points[j, 0], points[i, 1] - points[j, 1], variance, image_radius)
            density[i] += weight
            density[j] += weight
            gradient[i, 0] += gx
            gradient[i, 1] += gy
            gradient[j, 0] -= gx
            gradient[j, 1] -= gy
    return gradient / density.reshape((count, 1)), density / (count * TWO_PI * variance)


@njit(cache=False)
def _particle_kernel_jacobian(points, variance, image_radius):
    count = len(points)
    score, normalized_density = _particle_kernel_sums(points, variance, image_radius)
    density = normalized_density * (count * TWO_PI * variance)
    result = np.zeros((2 * count, 2 * count))
    for i in range(count):
        for j in range(i):
            _, gx, gy, hxx, hxy, hyy = _particle_kernel_terms(
                points[i, 0] - points[j, 0], points[i, 1] - points[j, 1], variance, image_radius)
            for component in range(2):
                for axis in range(2):
                    hessian = hxx if component == 0 and axis == 0 else hyy if component == 1 and axis == 1 else hxy
                    gradient = gx if axis == 0 else gy
                    ij = (hessian - score[i, component] * gradient) / density[i]
                    ji = (hessian + score[j, component] * gradient) / density[j]
                    result[2 * i + component, 2 * j + axis] = ij
                    result[2 * j + component, 2 * i + axis] = ji
                    result[2 * i + component, 2 * i + axis] -= ij
                    result[2 * j + component, 2 * j + axis] -= ji
    return result


class _PeriodicParticleKDE:
    """Direct smooth wrapped Gaussian KDE, with all current particles as centers."""
    def __init__(self, bandwidth=0.1):
        self.bandwidth = float(bandwidth)
        self.variance = self.bandwidth ** 2
        # At the prescribed bandwidth .1, the nearest and two adjacent images
        # are sufficient far beyond floating-point precision. The extension
        # keeps the first omitted image at least eight standard deviations away.
        self.image_radius = max(1, int(math.ceil(8 * self.bandwidth / TWO_PI)))

    def score(self, points):
        score, density = _particle_kernel_sums(points, self.variance, self.image_radius)
        if not np.isfinite(score).all() or not np.isfinite(density).all() or np.any(density <= 0):
            raise FloatingPointError('Nonfinite or nonpositive current-particle KDE density or score.')
        return score, density


def _kde_jacobian(points, fit, kde):
    jac = _particle_kernel_jacobian(points, kde.variance, kde.image_radius)
    eps = 1e-5
    for axis in range(2):
        shift = np.zeros(2)
        shift[axis] = eps
        derivative = (target_score(points + shift, fit) - target_score(points - shift, fit)) / (2 * eps)
        for component in range(2):
            jac[np.arange(len(points)) * 2 + component, np.arange(len(points)) * 2 + axis] += derivative[:, component]
    return jac


def run_kde(source, fit, lambda1, times, seed, *, bandwidth=0.1,
            rtol=1e-6, atol=1e-8, first_step_raw=1e-5, normalized_max_step=.05,
            maximum_seconds=1800., maximum_evaluations=200000,
            progress_seconds=25., progress=True):
    """Current-particle KDE flow with BDF and a smooth direct-kernel Jacobian.

    Raw velocity is target_score - current_particle_KDE_score. Integration
    uses raw time s/lambda1 and reports exactly the requested normalized
    checkpoints using the accepted BDF step's dense output. The particle KDE is evaluated directly
    over all particle pairs, with analytic kernel derivatives; at sigma=.1
    the dominant periodic image is sufficient below double precision. It uses fixed isotropic bandwidth, chosen to match the
    prescribed target smoothing. Its centers are all current particles and
    are updated at every field evaluation; the bandwidth is not fitted online.
    No speed cap, density floor, particle subsampling or continuum PDE is used.
    An incomplete run retains NaNs at unreached checkpoints and is identified
    explicitly. Compilation, saved cloud copies and progress output are
    excluded from transport timing; no evaluation metric is computed here.
    """
    source=np.asarray(source,dtype=np.float64);times=np.asarray(times,dtype=np.float64)
    if source.ndim!=2 or source.shape[1]!=2 or len(source)<2 or not np.isfinite(source).all():
        raise ValueError('Source must contain at least two finite angular points.')
    if times.ndim!=1 or len(times)<2 or times[0]!=0 or not np.isfinite(times).all() or np.any(np.diff(times)<=0):
        raise ValueError('Normalized checkpoints must increase strictly from zero.')
    if not np.isfinite([lambda1,bandwidth]).all() or lambda1<=0 or bandwidth<=0:
        raise ValueError('Positive lambda1 and bandwidth are required.')
    kde=_PeriodicParticleKDE(bandwidth);coefficients=_coefficients(fit)
    warm=time.perf_counter()
    warm_source=source[:min(17,len(source))]
    target_score(warm_source,fit);kde.score(warm_source);_kde_jacobian(warm_source,fit,kde)
    compile_seconds=time.perf_counter()-warm
    clouds=np.full((len(times),len(source),2),np.nan);clouds[0]=source
    rows=[dict(s=0.,raw_time=0.,steps=0,nfev=0,njev=0,nlu=0,cpu_seconds=0.,wall_seconds=0.)]
    counts=dict(nfev=0,njev=0);maximum_speed=0.;steps=0;cursor=1;solver=None
    excluded_cpu=excluded_wall=0.;cpu0=time.process_time();wall0=time.perf_counter();last_progress=wall0
    status='ok';failure=None

    def bound():
        if time.perf_counter()-wall0-excluded_wall>=maximum_seconds or counts['nfev']>=maximum_evaluations:
            raise RuntimeError('KDE transport resource limit reached.')

    def rhs(raw_time,flat):
        nonlocal maximum_speed
        bound();points=flat.reshape(source.shape)
        velocity=target_score(points,fit)-kde.score(points)[0]
        if not np.isfinite(velocity).all():raise FloatingPointError('Nonfinite current-particle KDE velocity.')
        maximum_speed=max(maximum_speed,float(np.linalg.norm(velocity,axis=1).max()))
        counts['nfev']+=1
        return velocity.ravel()

    def jac(raw_time,flat):
        bound();counts['njev']+=1
        return _kde_jacobian(flat.reshape(source.shape),fit,kde)

    try:
        solver=BDF(rhs,0.,source.ravel().copy(),float(times[-1]/lambda1),jac=jac,
                   rtol=rtol,atol=atol,first_step=first_step_raw,max_step=normalized_max_step/lambda1)
        while solver.status=='running':
            bound();message=solver.step();steps+=1
            if solver.status=='failed':raise FloatingPointError(str(message))
            if cursor<len(times) and times[cursor]/lambda1<=solver.t+1e-10:
                dense=solver.dense_output()
                while cursor<len(times) and times[cursor]/lambda1<=solver.t+1e-10:
                    c=time.process_time();w=time.perf_counter()
                    raw=float(times[cursor]/lambda1)
                    clouds[cursor]=_kde_wrap(dense(raw).reshape(source.shape))
                    rows.append(dict(s=float(times[cursor]),raw_time=raw,steps=steps,
                                     nfev=counts['nfev'],njev=counts['njev'],nlu=int(solver.nlu),
                                     cpu_seconds=c-cpu0-excluded_cpu,wall_seconds=w-wall0-excluded_wall))
                    cursor+=1;excluded_cpu+=time.process_time()-c;excluded_wall+=time.perf_counter()-w
            if progress and time.perf_counter()-last_progress>=progress_seconds:
                c=time.process_time();w=time.perf_counter()
                print(json.dumps(dict(method='KDE',seed=int(seed),normalized_time=float(solver.t*lambda1),
                                      completed_checkpoints=cursor,nfev=counts['nfev'],njev=counts['njev'],
                                      transport_cpu_seconds=c-cpu0-excluded_cpu,
                                      transport_wall_seconds=w-wall0-excluded_wall)),flush=True)
                last_progress=time.perf_counter();excluded_cpu+=time.process_time()-c;excluded_wall+=last_progress-w
    except RuntimeError as exc:
        status='resource_limit';failure=str(exc)
    except (FloatingPointError,np.linalg.LinAlgError,ValueError) as exc:
        status='numerical_failure';failure=str(exc)
    if status=='ok' and cursor!=len(times):status='incomplete'
    cpu=time.process_time()-cpu0-excluded_cpu;wall=time.perf_counter()-wall0-excluded_wall
    diagnostics=dict(status=status,failure=failure,method='KDE',seed=int(seed),rng=None,
        lambda1=float(lambda1),requested_times=times.tolist(),completed_checkpoints=cursor,
        completed_raw_time=float(solver.t) if solver is not None else 0.,
        completed_normalized_time=float(solver.t*lambda1) if solver is not None else 0.,
        steps=steps,nfev=counts['nfev'],njev=counts['njev'],nlu=int(solver.nlu) if solver is not None else 0,
        score_evaluations=counts['nfev']*len(source),threads=1,
        transport_cpu_seconds=cpu,transport_wall_seconds=wall,compilation_seconds=compile_seconds,
        maximum_score_norm=maximum_speed,drift_cap=None,checkpoints=rows,
        source_sha256=_sha(source),target_coefficient_sha256=_sha(coefficients),
        numerical_target_density_floor=fit.get('metadata',{}).get('density_floor'),
        maximum_seconds=float(maximum_seconds),maximum_evaluations=int(maximum_evaluations),
        solver='BDF; analytic fixed-bandwidth direct particle-kernel Jacobian',
        numerical_parameters=dict(rtol=float(rtol),atol=float(atol),
            first_step_raw=float(first_step_raw),normalized_max_step=float(normalized_max_step),
            bandwidth=float(bandwidth),bandwidth_rule='Fixed isotropic standard deviation equal to prescribed target smoothing',
            kernel='Periodic Gaussian; all current particles including self',
            particle_backend='Direct all-particle kernel sums; no particle mesh',
            wrapped_images_per_axis=1 if bandwidth <= .15 else 2*kde.image_radius+1,
            periodic_image_rule='Dominant image for sigma<=.15 (omitted weights below 6e-96); adjacent-image sum otherwise',
            kde_density_floor=None,speed_cap=None),
        clock='Raw t=s/lambda1; unit-mobility deterministic probability flow, not physical MD time',
        jacobian='Analytic direct particle-kernel derivatives; central differences for target spline Hessian',
        coefficient_regime='Dynamic current empirical KDE, with no independent continuum density')
    return diagnostics,clouds


def implementation_checks():
    """Check periodic scores, the interacting Jacobian and short-time accuracy.

    Synthetic checks use fixed inputs and tolerances; they do not select an
    alanine bandwidth or optimize an evaluation metric.
    """
    rng = np.random.default_rng(3911)
    train = _kde_wrap(rng.normal(size=(4000, 2)) * [0.6, 0.4] + [2.8, -2.7])
    fit = fit_target(train)
    points = _kde_wrap(rng.normal(size=(40, 2)) * [0.55, 0.35] + [2.8, -2.7])
    score = target_score(points, fit)
    periodic_error = float(np.max(abs(score - target_score(points + [TWO_PI, -TWO_PI], fit))))
    coefficients = fit['log_density_coefficients']
    finite_difference = np.empty_like(points)
    eps = 1e-6
    for i, (x, y) in enumerate(points):
        finite_difference[i, 0] = (_log_density_one(x + eps, y, coefficients) - _log_density_one(x - eps, y, coefficients)) / (2 * eps)
        finite_difference[i, 1] = (_log_density_one(x, y + eps, coefficients) - _log_density_one(x, y - eps, coefficients)) / (2 * eps)
    derivative_error = float(np.max(abs(score - finite_difference)))
    _, exact_score = direct_wrapped_kernel_score(points, train)
    target_kernel_error = float(np.max(np.linalg.norm(score - exact_score, axis=1)))
    assert periodic_error < 1e-9 and derivative_error < 1e-6
    assert target_kernel_error < 0.025, target_kernel_error

    source = _kde_wrap(rng.normal(size=(24, 2)) * [0.2, 0.16] + [2.8, -2.7])
    kde = _PeriodicParticleKDE(0.1)
    particle_score, density = kde.score(source)
    _, direct_score = direct_wrapped_kernel_score(source, source, 0.1)
    particle_kernel_error = float(np.max(np.linalg.norm(particle_score - direct_score, axis=1)))
    particle_periodicity = float(np.max(abs(particle_score - kde.score(source + [TWO_PI, -TWO_PI])[0])))
    assert particle_kernel_error < 1e-10, particle_kernel_error
    assert particle_periodicity < 1e-9 and density.min() > 0
    jacobian = _kde_jacobian(source, fit, kde)
    direction = rng.normal(size=source.shape)
    direction /= np.linalg.norm(direction)
    def field(cloud):
        return target_score(cloud, fit) - kde.score(cloud)[0]
    finite_difference = ((field(source + eps * direction) - field(source - eps * direction)) / (2 * eps)).ravel()
    jacobian_error = float(np.max(abs(jacobian @ direction.ravel() - finite_difference)))
    assert jacobian_error < 1e-5, jacobian_error
    # An off-diagonal block demonstrates dependence on other current particles.
    interaction = jacobian.copy()
    for i in range(len(source)):
        interaction[2*i:2*i+2, 2*i:2*i+2] = 0.
    assert np.max(abs(interaction)) > 1e-3

    settings = dict(bandwidth=0.1, maximum_seconds=120., progress=False)
    normal, coarse = run_kde(source, fit, 1., [0., 0.01, 0.05, 0.1], 3911, **settings)
    tight, fine = run_kde(source, fit, 1., [0., 0.01, 0.05, 0.1], 3911,
                         rtol=1e-8, atol=1e-10, **settings)
    assert normal['status'] == tight['status'] == 'ok', (normal, tight)
    solver_difference = float(np.max(abs(_kde_wrap(coarse - fine))))
    assert solver_difference < 1e-3, solver_difference
    return dict(status='ok', periodicity_error=periodic_error,
                analytic_gradient_error=derivative_error,
                direct_target_score_maximum_error=target_kernel_error,
                direct_particle_score_maximum_error=particle_kernel_error,
                particle_score_periodicity_error=particle_periodicity,
                particle_jacobian_directional_error=jacobian_error,
                short_solver_maximum_coordinate_difference=solver_difference,
                short_solver_checkpoints=[0., 0.01, 0.05, 0.1],
                short_solver_tolerances=[[1e-6, 1e-8], [1e-8, 1e-10]])


if __name__ == '__main__':
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        print(json.dumps(implementation_checks(), indent=2), flush=True)


