"""Matched OU path validation, independent of the original experiment outputs.

Run checks: uv run --with numpy==2.4.6 --with scipy==1.17.1 python supplementary/ou_path_validation.py --check
Run experiment: the same command without --check. No QUICK switch or budget selection.

The analytical target is N(0,1), source N(m0,s0**2), and generator f''-x*f'.
The specified, reproducible continuous path is piecewise linear through the actual safeguarded RK4
nodes. Its residual includes time discretization, density flooring and velocity
capping. Gauss-Legendre refinement is a numerical check, NOT a rigorous enclosure.
"""

from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
import ast
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtri, roots_hermitenorm

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = Path(__file__).with_name("ou_path_config.json")


def hermite_basis(x, r):
    """Literal numerical recurrence from notebook cell 2."""
    x = np.asarray(x, float)
    P = np.zeros((r + 1, x.size)); dP = np.zeros((r + 1, x.size))
    P[0] = 1.0
    if r >= 1: P[1] = x
    for k in range(1, r):
        P[k + 1] = (x * P[k] - np.sqrt(k) * P[k - 1]) / np.sqrt(k + 1)
    for k in range(1, r + 1):
        dP[k] = np.sqrt(k) * P[k - 1]
    return P, dP


def empirical_coefficients(x, r):
    P, _ = hermite_basis(x, r)
    c = P.mean(axis=1)
    c[0] = 1.0
    return c


def population_coefficients(m, s, r):
    """E[He_k(X)/sqrt(k!)] for X~N(m,s**2), with stable recurrence."""
    c = np.zeros(r + 1)
    c[0] = 1.0
    if r:
        c[1] = m
    for k in range(1, r):
        c[k + 1] = (m * c[k] + (s*s - 1.0) * np.sqrt(k) * c[k-1]) / np.sqrt(k+1)
    return c


def population_parameters(t, m0, s0):
    t = np.asarray(t)
    m = m0 * np.exp(-t)
    variance = 1.0 + (s0*s0 - 1.0) * np.exp(-2.0*t)
    return m, np.sqrt(variance)


def exact_velocity(x, t, m0, s0):
    m, s = population_parameters(t, m0, s0)
    return (1.0/(s*s) - 1.0) * x - m/(s*s)


def exact_flow(x0, t, m0, s0):
    m, s = population_parameters(t, m0, s0)
    return m + (s/s0) * (x0-m0)


def field(x, t, c, density_floor, velocity_cap, diagnostics=None):
    P, dP = hermite_basis(x, len(c)-1)
    weights = np.exp(-np.arange(len(c))*t)*c
    rho = weights @ P
    drho = weights @ dP
    raw_speed = -drho / np.maximum(rho, density_floor)
    if not (np.isfinite(rho).all() and np.isfinite(raw_speed).all()):
        raise FloatingPointError("Nonfinite Hermite density or speed; no silent repairs are permitted.")
    if diagnostics is not None:
        floor = rho < density_floor
        nonpositive = rho <= 0.0
        cap = np.abs(raw_speed) > velocity_cap
        diagnostics["density_floor_events"] += int(floor.sum())
        diagnostics["nonpositive_density_events"] += int(nonpositive.sum())
        diagnostics["speed_cap_events"] += int(cap.sum())
        diagnostics["stage_particle_evaluations"] += x.size
        diagnostics["affected_mask"] |= floor | cap
        diagnostics["minimum_stage_density"] = min(diagnostics["minimum_stage_density"], float(rho.min()))
        diagnostics["maximum_uncapped_speed"] = max(diagnostics["maximum_uncapped_speed"], float(np.abs(raw_speed).max()))
    return np.clip(raw_speed, -velocity_cap, velocity_cap)


def transport(x0, c, T, dt, density_floor, velocity_cap):
    steps = int(round(T/dt))
    if not np.isclose(steps*dt, T, atol=1e-14, rtol=0):
        raise ValueError("Horizon must be an integer multiple of dt.")
    times = np.arange(steps+1)*dt
    paths = np.empty((steps+1, len(x0)), dtype=float)
    paths[0] = x0
    X = x0.copy()
    diag = dict(density_floor_events=0, nonpositive_density_events=0, speed_cap_events=0,
                stage_particle_evaluations=0, affected_mask=np.zeros(len(x0), dtype=bool),
                minimum_stage_density=np.inf, maximum_uncapped_speed=0.0)
    for i in range(steps):
        t = i*dt
        k1 = field(X, t, c, density_floor, velocity_cap, diag)
        k2 = field(X+.5*dt*k1, t+.5*dt, c, density_floor, velocity_cap, diag)
        k3 = field(X+.5*dt*k2, t+.5*dt, c, density_floor, velocity_cap, diag)
        k4 = field(X+dt*k3, t+dt, c, density_floor, velocity_cap, diag)
        X += dt/6*(k1+2*k2+2*k3+k4)
        paths[i+1] = X
    diag["affected_particles"] = int(diag.pop("affected_mask").sum())
    diag["particle_clip_events"] = 0
    diag["initial_projection_events"] = 0
    return times, paths, diag


def gaussian_w2(x, mean=0.0, std=1.0):
    """Exact Gaussian quantile-interval integrals for the empirical W2 metric.

    On each interval, subtract its Gaussian conditional centroid first. This
    avoids cancellation between raw second moments when errors are small.
    Long-double accumulation only protects rounding; it is not certification.
    """
    x = np.sort(np.asarray(x, dtype=float))
    M = len(x)
    if not M or std <= 0 or not np.isfinite(x).all():
        raise ValueError("Finite nonempty samples and positive target std are required.")
    borders = ndtri(np.arange(M+1, dtype=float)/M)
    phi = np.exp(-0.5*borders*borders)/np.sqrt(2*np.pi)
    centroids = M*(phi[:-1]-phi[1:])
    residual_variance = np.longdouble(1) - np.mean(np.asarray(centroids, np.longdouble)**2)
    if residual_variance < -np.longdouble(1e-13):
        raise FloatingPointError("Negative quantile-cell residual variance.")
    residual_variance = max(residual_variance, np.longdouble(0))
    displacement = np.asarray(x-mean-std*centroids, np.longdouble)
    squared = np.mean(displacement**2) + np.longdouble(std)**2*residual_variance
    return float(np.sqrt(squared))


def residual_quadrature(times, paths, m0, s0, order):
    """Integrate K(T,t)R_i(t) and K(T,t)||R(t)||_M on each saved step.

    R=secant derivative - exact velocity of the piecewise-linear path. No
    endpoint-error identity is used in computing these integrals.
    """
    nodes, weights = leggauss(order)
    _, sT = population_parameters(times[-1], m0, s0)
    integral = np.zeros(paths.shape[1])
    B = 0.0
    cumulative_B = np.zeros(len(times))
    cumulative_integral = np.zeros_like(paths)
    for j, (left, right) in enumerate(zip(times[:-1], times[1:])):
        h = right-left
        slope = (paths[j+1]-paths[j])/h
        for z, w in zip(nodes, weights):
            fraction = .5*(z+1)
            t = left+h*fraction
            Y = paths[j] + fraction*(paths[j+1]-paths[j])
            R = slope-exact_velocity(Y, t, m0, s0)
            _, st = population_parameters(t, m0, s0)
            K = sT/st
            quadrature_weight = h*.5*w*K
            integral += quadrature_weight*R
            B += quadrature_weight*float(np.sqrt(np.mean(R*R)))
        cumulative_B[j+1] = B
        cumulative_integral[j+1] = integral
    return dict(integral=integral, B=float(B), cumulative_B=cumulative_B,
                cumulative_integral=cumulative_integral)


def checked_residual(times, paths, m0, s0, qconfig):
    exact = exact_flow(paths[0], times[-1], m0, s0)
    difference = paths[-1]-exact
    D = float(np.sqrt(np.mean(difference**2)))
    cache = {}
    def evaluate(order):
        if order not in cache:
            cache[order] = residual_quadrature(times, paths, m0, s0, order)
        return cache[order]
    atol, rtol = qconfig["absolute_tolerance"], qconfig["relative_tolerance"]
    previous = evaluate(qconfig["identity_orders"][0])
    for order in qconfig["identity_orders"][1:]:
        current = evaluate(order)
        delta = float(np.sqrt(np.mean((current["integral"]-previous["integral"])**2)))
        if delta <= atol+rtol*D:
            identity_order = order
            identity_delta = delta
            identity_value = current
            break
        previous = current
    else:
        raise RuntimeError("Vector residual quadrature did not converge.")
    previous = evaluate(qconfig["bound_orders"][0])
    adaptive_intervals = 0
    adaptive_depth = 0
    for order in qconfig["bound_orders"][1:]:
        current = evaluate(order)
        delta = abs(current["B"]-previous["B"])
        if delta <= atol+rtol*current["B"]:
            bound_order = order
            bound_delta = delta
            bound_value = current
            break
        previous = current
    else:
        # The residual norm can have narrow minima or cusps even for a smooth
        # exact field. Resolve them locally instead of silently accepting a
        # failed fixed-order comparison.
        bound_value, bound_delta, adaptive_intervals, adaptive_depth = adaptive_bound_quadrature(
            times, paths, m0, s0, atol, rtol)
        bound_order = 16
    errors = identity_value["integral"]-difference
    identity_rms = float(np.sqrt(np.mean(errors**2)))
    if identity_rms > 10*(atol+rtol*D):
        raise RuntimeError("Path identity failed: independent quadrature disagrees with endpoints.")
    B = bound_value["B"]
    if D > B + 10*(atol+rtol*B):
        raise RuntimeError("Path triangle inequality failed beyond quadrature tolerance.")
    data = dict(D=D, B=B, D_quadrature=float(np.sqrt(np.mean(identity_value["integral"]**2))),
                identity_rms_error=identity_rms, identity_max_error=float(np.max(np.abs(errors))),
                D_quadrature_order=identity_order, B_quadrature_order=bound_order,
                D_quadrature_difference=identity_delta, B_quadrature_difference=bound_delta,
                B_adaptive_intervals=adaptive_intervals, B_adaptive_max_depth=adaptive_depth,
                cancellation_ratio=D/B if B else 0.0, path_triangle_gap=B-D)
    # Convert the fixed terminal kernel in cumulative integrals into each
    # checkpoint's kernel; these are valid path diagnostics at every node.
    _, all_s = population_parameters(times, m0, s0)
    scaling = all_s/all_s[-1]
    time_B = bound_value["cumulative_B"]*scaling
    time_Dq = np.sqrt(np.mean(identity_value["cumulative_integral"]**2, axis=1))*scaling
    exact_nodes = exact_flow(paths[0][None, :], times[:, None], m0, s0)
    time_D = np.sqrt(np.mean((paths-exact_nodes)**2, axis=1))
    mid_times=.5*(times[:-1]+times[1:])
    mid_paths=.5*(paths[:-1]+paths[1:])
    mid_residual=(paths[1:]-paths[:-1])/np.diff(times)[:,None]-exact_velocity(
        mid_paths,mid_times[:,None],m0,s0)
    return data, dict(path_D=time_D, path_B=time_B, path_D_quadrature=time_Dq,
                      residual_integral=identity_value["integral"],
                      residual_rms_midpoint=np.sqrt(np.mean(mid_residual**2,axis=1)))


def adaptive_bound_quadrature(times, paths, m0, s0, atol, rtol):
    """Local 8/16 point refinement for the scalar residual norm integral.

    The returned difference estimate is numerical only. It is the sum of
    absolute local differences, and is not a proven error bound.
    """
    rules = {order: leggauss(order) for order in (8,16)}
    _, sT = population_parameters(times[-1], m0, s0)
    cumulative=np.zeros(len(times)); error_total=0.; accepted=0; max_depth=0
    for j,(left,right) in enumerate(zip(times[:-1],times[1:])):
        h=right-left
        slope=(paths[j+1]-paths[j])/h
        def integrate(a,b,order):
            nodes,weights=rules[order]
            result=0.
            for z,w in zip(nodes,weights):
                t=a+.5*(z+1)*(b-a)
                Y=paths[j]+(t-left)*slope
                R=slope-exact_velocity(Y,t,m0,s0)
                _,st=population_parameters(t,m0,s0)
                result += .5*(b-a)*w*(sT/st)*float(np.sqrt(np.mean(R*R)))
            return result
        def refine(a,b,depth):
            nonlocal accepted,max_depth
            low,high=integrate(a,b,8),integrate(a,b,16)
            error=abs(high-low)
            tolerance=atol*(b-a)/(times[-1]-times[0])+rtol*abs(high)
            if error<=tolerance:
                accepted+=1; max_depth=max(max_depth,depth)
                return high,error
            if depth>=16:
                raise RuntimeError("Adaptive scalar path bound quadrature did not converge.")
            mid=.5*(a+b)
            v1,e1=refine(a,mid,depth+1); v2,e2=refine(mid,b,depth+1)
            return v1+v2,e1+e2
        value,error=refine(left,right,0)
        cumulative[j+1]=cumulative[j]+value
        error_total+=error
    return dict(B=float(cumulative[-1]),cumulative_B=cumulative),float(error_total),accepted,max_depth


def density_grid_diagnostics(c, grid_config, eps):
    grid = np.linspace(grid_config["left"], grid_config["right"], grid_config["points"])
    P, _ = hermite_basis(grid, len(c)-1)
    rows = []
    for t in grid_config["times"]:
        rho = (np.exp(-np.arange(len(c))*t)*c) @ P
        rows.append(dict(t=t, minimum_density=float(rho.min()),
                         nonpositive_grid_fraction=float(np.mean(rho <= 0)),
                         below_floor_grid_fraction=float(np.mean(rho < eps))))
    return rows


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def statistics(values):
    values = np.asarray(values, dtype=float)
    return dict(mean=float(values.mean()), std=float(values.std(ddof=1)) if len(values)>1 else 0.0,
                n=len(values))


def summarize(rows, config):
    metrics = ["D", "B", "D_quadrature", "identity_rms_error", "identity_max_error",
               "D_quadrature_difference", "B_quadrature_difference", "cancellation_ratio",
               "w2_target", "exact_flow_w2", "target_reference_w2", "w2_triangle_bound",
               "w2_triangle_gap", "w2_paired_triangle_bound", "w2_paired_triangle_gap",
               "density_floor_events", "nonpositive_density_events",
               "speed_cap_events", "affected_particles", "minimum_stage_density",
               "maximum_uncapped_speed", "transport_seconds", "residual_seconds"]
    groups, table = [], []
    for r in config["ranks"]:
        for dt in config["steps"]:
            for regime in config["regimes"]:
                selected = [row for row in rows if (row["r"], row["dt"], row["regime"]) == (r,dt,regime)]
                stats = {key: statistics([row[key] for row in selected]) for key in metrics}
                groups.append(dict(r=r, dt=dt, regime=regime, metrics=stats))
                table.extend(dict(r=r,dt=dt,regime=regime,metric=key,**value) for key,value in stats.items())
    paired = []
    for r in config["ranks"]:
        for dt in config["steps"]:
            for positive,negative in (("I","P"),("S","P"),("S","I")):
                for metric in ("w2_target", "D", "B"):
                    diffs = []
                    for seed in config["seeds"]:
                        by_regime = {row["regime"]: row for row in rows if (row["r"],row["dt"],row["seed"]) == (r,dt,seed)}
                        diffs.append(by_regime[positive][metric]-by_regime[negative][metric])
                    paired.append(dict(r=r,dt=dt,regime="paired",comparison=positive+"-"+negative,metric=metric,**statistics(diffs)))
        if len(config["steps"]) == 2:
            coarse,fine = max(config["steps"]),min(config["steps"])
            for regime in config["regimes"]:
                for metric in ("w2_target", "D", "B"):
                    diffs=[]
                    for seed in config["seeds"]:
                        by_dt={row["dt"]:row for row in rows if (row["r"],row["regime"],row["seed"]) == (r,regime,seed)}
                        diffs.append(by_dt[fine][metric]-by_dt[coarse][metric])
                    paired.append(dict(r=r,dt="paired",regime=regime,comparison=f"h={fine}-h={coarse}",metric=metric,**statistics(diffs)))
    first_r, first_dt, first_regime = config["ranks"][0],config["steps"][0],config["regimes"][0]
    baseline = [row for row in rows if (row["r"],row["dt"],row["regime"]) == (first_r,first_dt,first_regime)]
    return dict(groups=groups, references={key:statistics([row[key] for row in baseline]) for key in ("exact_flow_w2","target_reference_w2")},
                standard_deviation="sample standard deviation (ddof=1)",
                diagnostic_status=config["theoretical_status"]), table, paired


def safe_notebook_functions(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    wanted={"hermite_basis", "ou_coefficients", "ou_velocity", "ou_transport"}
    definitions=[]
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source="".join(cell["source"])
        if not any("def "+name+"(" in source for name in wanted):
            continue
        tree=ast.parse(source)
        definitions.extend(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted)
    if {node.name for node in definitions} != wanted:
        raise ValueError("Expected original notebook OU functions not found.")
    # Only these four definitions are compiled. No notebook setup or experiment
    # statements are executed, and no original outputs are written.
    namespace={"np":np}
    module=ast.Module(body=definitions, type_ignores=[])
    exec(compile(module,str(path),"exec"),namespace)
    return namespace


def run_checks(config):
    m0,s0=config["source_mean"],config["source_std"]
    rng=np.random.default_rng(87423)
    r=max(config["ranks"])
    z,w=roots_hermitenorm(128)
    P,_=hermite_basis(m0+s0*z,r)
    direct=P @ (w/np.sqrt(2*np.pi))
    coeff=population_coefficients(m0,s0,r)
    coeff_error=float(np.max(np.abs(direct-coeff)))
    np.testing.assert_allclose(coeff,direct,atol=2e-12,rtol=2e-12)
    # Delta_0 versus N(0,1) has W2=1. A translated/rescaled single atom has
    # W2^2=(atom-mean)^2+std^2.
    assert abs(gaussian_w2([0.])-1.)<1e-14
    assert abs(gaussian_w2([2.],mean=.5,std=2.)-2.5)<1e-14
    x=rng.normal(size=137)
    # Independent raw-second-moment formula, using exact bin integrals.
    borders=ndtri(np.arange(len(x)+1)/len(x)); phi=np.exp(-borders*borders/2)/np.sqrt(2*np.pi)
    direct_w2=np.sqrt(np.mean(np.sort(x)**2)+1-2*np.dot(np.sort(x),phi[:-1]-phi[1:]))
    assert abs(gaussian_w2(x)-direct_w2)<2e-14
    nb=safe_notebook_functions(ROOT/config["notebook"])
    source=rng.normal(m0,s0,size=128)
    basis_error=0.; velocity_error=0.; transport_error=0.
    for rank in config["ranks"]:
        for a,b in zip(hermite_basis(source,rank),nb["hermite_basis"](source,rank)):
            basis_error=max(basis_error,float(np.max(np.abs(a-b))))
        c=empirical_coefficients(source,rank)
        np.testing.assert_array_equal(c,nb["ou_coefficients"](source,rank))
        for t in (0.,.125,2.):
            a=field(source,t,c,config["density_floor"],config["velocity_cap"])
            b=nb["ou_velocity"](source,t,c)
            velocity_error=max(velocity_error,float(np.max(np.abs(a-b))))
        for dt in config["steps"]:
            _,paths,_=transport(source,c,.2,dt,config["density_floor"],config["velocity_cap"])
            b=nb["ou_transport"](source,rank,.2,dt)
            transport_error=max(transport_error,float(np.max(np.abs(paths[-1]-b))))
    assert basis_error==velocity_error==transport_error==0.
    # Manufactured affine-in-time paths are distinct from the OU flow, and
    # give nonzero residual and endpoint errors without Hermite transport.
    times=np.arange(21)*.05
    paths=source[None,:]+times[:,None]*(.2-.3*source[None,:])
    manufacture,_=checked_residual(times,paths,m0,s0,config["quadrature"])
    assert manufacture["D"]>0.1
    # Exact OU nodes still have interpolation residual; its vector integral
    # cancels to zero at each endpoint, as required by the path identity.
    exact_nodes=exact_flow(source[None,:],times[:,None],m0,s0)
    cancellation,_=checked_residual(times,exact_nodes,m0,s0,config["quadrature"])
    assert cancellation["D"]<1e-13 and cancellation["B"]>0
    # The standard Gaussian is stationary and zero coefficients give an
    # exactly zero numerical field, residual and endpoint discrepancy.
    stationary=np.repeat(source[None,:],len(times),axis=0)
    zero,_=checked_residual(times,stationary,0.,1.,config["quadrature"])
    assert zero["D"]==zero["B"]==0
    result=dict(population_coefficient_max_error=coeff_error, notebook_basis_max_error=basis_error,
                notebook_velocity_max_error=velocity_error, notebook_transport_max_error=transport_error,
                manufactured_path_identity_rms_error=manufacture["identity_rms_error"],
                exact_node_interpolation_B=cancellation["B"],
                exact_node_interpolation_identity_rms_error=cancellation["identity_rms_error"],
                metric_checks="passed", stationary_path_check="passed")
    print(json.dumps(result,indent=2),flush=True)
    return result


def run(config, config_path):
    checks=run_checks(config)
    out=ROOT/config["output_directory"]
    out.mkdir(parents=True,exist_ok=True)
    if (out/"runs.csv").exists():
        raise FileExistsError("runs.csv already exists; choose a new output directory or intentionally archive the prior experiment.")
    started=time.perf_counter()
    rows=[]; grids=[]
    m0,s0,M,T=config["source_mean"],config["source_std"],config["particles"],config["horizon"]
    mT,sT=population_parameters(T,m0,s0)
    continuous_bias=float(np.hypot(mT,sT-1))
    for seed in config["seeds"]:
        source_seq,coeff_seq,target_seq=np.random.SeedSequence(seed).spawn(3)
        X0=np.random.default_rng(source_seq).normal(m0,s0,size=M)
        independent=np.random.default_rng(coeff_seq).normal(m0,s0,size=M)
        target=np.random.default_rng(target_seq).standard_normal(M)
        exact_endpoint=exact_flow(X0,T,m0,s0)
        exact_w2=gaussian_w2(exact_endpoint)
        reference_w2=gaussian_w2(target)
        saved=dict(X0=X0,independent_X0=independent,target_reference=target,exact_endpoint=exact_endpoint)
        for r in config["ranks"]:
            coeffs=dict(P=population_coefficients(m0,s0,r),I=empirical_coefficients(independent,r),S=empirical_coefficients(X0,r))
            for regime,c in coeffs.items():
                saved[f"coeff_{regime}_r{r}"]=c
                for grid in density_grid_diagnostics(c,config["diagnostic_grid"],config["density_floor"]):
                    grids.append(dict(seed=seed,r=r,regime=regime,**grid))
            for dt in config["steps"]:
                hkey=f"h{round(dt*1000):03d}"
                for regime in config["regimes"]:
                    t0=time.perf_counter()
                    times,paths,diag=transport(X0,coeffs[regime],T,dt,config["density_floor"],config["velocity_cap"])
                    elapsed=time.perf_counter()-t0
                    t0=time.perf_counter()
                    residual,arrays=checked_residual(times,paths,m0,s0,config["quadrature"])
                    residual_elapsed=time.perf_counter()-t0
                    w2=gaussian_w2(paths[-1])
                    triangle=exact_w2+residual["B"]
                    if w2>triangle+1e-8:
                        raise RuntimeError("Empirical-to-target triangle check failed.")
                    row=dict(seed=seed,r=r,dt=dt,regime=regime,M=M,
                             coefficient_sample_count=0 if regime=="P" else M,
                             extra_source_sample_count=M if regime=="I" else 0,
                             **residual,w2_target=w2,exact_flow_w2=exact_w2,target_reference_w2=reference_w2,
                             continuous_flow_w2=continuous_bias,w2_triangle_bound=triangle,
                             w2_triangle_gap=triangle-w2,
                             w2_paired_triangle_bound=exact_w2+residual["D"],
                             w2_paired_triangle_gap=exact_w2+residual["D"]-w2,
                             **diag,transport_seconds=elapsed,residual_seconds=residual_elapsed)
                    rows.append(row)
                    key=f"{regime}_r{r}_{hkey}"
                    saved[f"times_{hkey}"]=times
                    saved[f"endpoint_{key}"]=paths[-1]
                    if config.get("save_full_paths",False):
                        saved[f"paths_{key}"]=paths
                    for name,values in arrays.items():
                        saved[f"{name}_{key}"]=values
                    print(f"seed={seed} r={r} h={dt:g} {regime}: W2={w2:.6g} D={residual['D']:.6g} B={residual['B']:.6g}; {elapsed+residual_elapsed:.2f}s",flush=True)
        np.savez_compressed(out/f"paths_seed_{seed}.npz",**saved)
        write_csv(out/"runs.csv",rows)
        write_csv(out/"density_grid.csv",grids)
    summary,table,paired=summarize(rows,config)
    summary["continuous_exact_flow_w2"]=continuous_bias
    summary["config"]=config
    summary["checks"]=checks
    summary["metadata"]=dict(created_utc=datetime.now(timezone.utc).isoformat(),runtime_seconds=time.perf_counter()-started,
                              python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),
                              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
                              notebook_sha256=hashlib.sha256((ROOT/config["notebook"]).read_bytes()).hexdigest(),
                              single_thread_environment={name:os.environ[name] for name in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","BLIS_NUM_THREADS")})
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (out/"runs.json").write_text(json.dumps(rows,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (out/"config.json").write_text(json.dumps(config,indent=2)+"\n",encoding="utf-8")
    write_csv(out/"summary.csv",table)
    write_csv(out/"paired_differences.csv",paired)
    print(f"Completed {len(rows)} matched runs in {time.perf_counter()-started:.1f}s. Outputs: {out}",flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=DEFAULT_CONFIG)
    parser.add_argument("--check",action="store_true",help="Run mathematical and notebook-parity checks only; write no experiment outputs.")
    parser.add_argument("--benchmark",action="store_true",help="Check and time one largest-rank fine-step P run, without saving experiment outputs.")
    args=parser.parse_args()
    config=json.loads(args.config.read_text(encoding="utf-8"))
    if args.check or args.benchmark:
        run_checks(config)
        if args.benchmark:
            rng=np.random.default_rng(1000)
            X0=rng.normal(config["source_mean"],config["source_std"],size=config["particles"])
            c=population_coefficients(config["source_mean"],config["source_std"],max(config["ranks"]))
            start=time.perf_counter()
            times,paths,diag=transport(X0,c,config["horizon"],min(config["steps"]),config["density_floor"],config["velocity_cap"])
            transport_time=time.perf_counter()-start
            start=time.perf_counter()
            result,_=checked_residual(times,paths,config["source_mean"],config["source_std"],config["quadrature"])
            print(json.dumps(dict(transport_seconds=transport_time,residual_seconds=time.perf_counter()-start,**result,**diag),indent=2),flush=True)
    else:
        run(config,args.config)


if __name__=="__main__":
    from experiment_store import managed_outputs
    with managed_outputs("ou"):
        main()
