"""Regenerate the single report from retained manuscript results; no simulations."""
from __future__ import annotations
import io
import csv
import json
import re
import statistics
import zipfile
import numpy as np
from experiment_store import ROOT, group_for

RESULTS_PATH=ROOT/'outputs/all_experiment_results_and_assessment.md'
ALANINE_DISPLAY_HORIZON=8.0
ALANINE_METHOD_LABELS={'BKT':'BKT','LAWGD':'LAWGD','KDE':'KDE'}

REPRODUCTION_NOTES = r"""## Files and reproduction

This is the only Markdown document for experiment results, limitations, fixed protocols, reproduction commands and figure conventions. One notebook, fixed supplementary runners, four checksum-verified archives and PDF figures form the retained package.

[OU data](data/ou.zip) | [Double/multiwell data](data/double_well.zip) | [Alanine inputs, parameters and results](data/alanine.zip) | [Shared references and results](data/shared.zip).

[OU](figures/fig_ou.pdf), [10D OU](figures/fig_ou10.pdf), [10D OU marginals](figures/fig_ou10_marginals.pdf), [matched paths](figures/fig_ou_path_comparison.pdf), [double-well ranks](figures/fig_admissible_source_ranks.pdf), [coefficient regimes](figures/fig_admissible_source_coefficients.pdf), [equal-data comparison](figures/fig_data_comparison.pdf), [10D double-well product](figures/fig_hd10_dictionaries.pdf), [50D double-well product](figures/fig_hd50_dictionaries.pdf), [256-mode alanine distribution](figures/fig_alanine.pdf), [three-method alanine convergence](figures/fig_alanine_convergence.pdf).

### Environment and data

Run from the project root with Python 3.11, NumPy 2.4.6, SciPy 1.17.1, Matplotlib 3.11.1 and threadpoolctl 3.6.0. The additional alanine KDE implementation also requires Numba 0.64.0. `uv run --with ...` can supply these versions without changing a global environment.

Four archives under `outputs/data/` contain the numerical inputs, parameters and results:

| Archive | Contents |
|---|---|
| `ou.zip` | 1D/10D OU, matched P/I/S paths and numerical diagnostics |
| `double_well.zip` | Double/multiwell and product systems, manuscript sensitivity studies and equal-data comparison |
| `alanine.zip` | Dataset, 256-mode Fourier inputs, RBF diagnostics and paired BKT/LAWGD/KDE trajectories with their periodic target-score fit |
| `shared.zip` | Notebook result index, shared reference data and implementation checks |

`catalog.json` and each archive manifest record member paths, sizes and SHA-256 hashes. The synthetic runners unpack the required data and verify/repack on exit; the alanine verification and plotting routines read the archives directly. Only one independent unpacked data session may be open at a time. The notebook keeps its session open until its final cell or kernel exit; close it manually with `experiment_store.close_notebook_store()` if needed. A setup cell reopens it.

```powershell
python -B supplementary/experiment_store.py verify
python -B supplementary/experiment_store.py list alanine
python -B supplementary/experiment_store.py read outputs/alanine/config.json
uv run --with numpy==2.4.6 python -B supplementary/manuscript_results.py
```

The report command reads saved data directly and runs no experiments. It is the only report generator. `--tables` exports the current manuscript CSV tables, using the admissible-source 2D results and including the coupled-10D limitation. PDFs remain in `outputs/figures/`; plotting reads saved arrays and shares the notebook font sizes and spacing.

For a numerical consistency check without changing saved results:

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/manuscript_results.py --check
```

This checks all 156 admissible-source and 30 equal-data endpoint clouds and reruns all 180 matched OU transports, residual integrals and safeguard counts. The alanine checks below cover its saved clouds and spectrum/transport reproduction separately.

### Synthetic systems

`BKT_experiments.ipynb` contains the numerical definitions, fixed main configurations and manuscript sensitivity studies. Run cells in order to reproduce. Existing compatible caches are reused. The main training sizes are frozen; the appendix rank, sample-size, time and particle-count studies are intentional manuscript results. The obsolete original-source 2D scans and their plotting cells have been removed. Four compact original-source entries in the shared result index supply only the references, horizons and parity values required by the retained supplementary runners; the current 2D results come from `admissible_source`.

| Additional study | Fixed parameters | Runner | Plotting from saved data |
|---|---|---|---|
| Matched OU paths | `ou_path_config.json` | `ou_path_validation.py` | `plot_ou_path_validation.py` |
| Admissible 2D source and I/S coefficients | `admissible_source_config.json` | `run_admissible_source.py` | `plot_admissible_source.py` |
| Equal-data comparison | `data_comparison_config.json` | `run_data_comparison.py` | `plot_data_comparison.py` |

All paths in the table are under `supplementary/`. The last two runners accept `--resume`; completed matching runs are reused. The equal-data runner also requires matching numerical-code and runtime provenance, saved endpoint checksums and individual timings; variance-0.5 records cannot be resumed under the current protocol. The OU runner refuses to overwrite completed runs. `audit_source_assumptions.py` checks the source/domain assumptions, and `diagnose_data_comparison_endpoints.py` checks the retained comparison endpoints.

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 python -B supplementary/ou_path_validation.py --check
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/run_admissible_source.py --resume
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/run_data_comparison.py --resume
```

For a fresh equal-data reproduction, retain the canonical comparison archive and shared training/reference caches, then append `--output-directory tmp/equal_data_reproduction` to the comparison command, using a previously unused directory and omitting `--resume`. The canonical source-independent input records are required for provenance checks, while every fit and transport is recomputed in the new directory. For other completed synthetic studies, use a separate workspace with that study's saved outputs absent but its shared input caches retained. No parameter search is performed.

### Alanine reproduction

The distribution and convergence figures use the same 256-mode BKT trajectories, the same three source/reference designs and the same endpoint s=8. `alanine_experiment.py` verifies the inputs, reproduces the spectral transport, plots the distribution figure and retains the RBF diagnostics. `alanine_convergence.py` handles the paired BKT/LAWGD/KDE trajectories. The archive retains only the inputs and results needed by these experiments; its RBF file includes all eight diagnostic realisations.

The five members under `outputs/alanine/` are `config.json`, `dataset.npz`, `results.npz`, `lawgd_convergence.npz` and `rbf_diagnostic.npz`. Despite its filename, `results.npz` contains the shared spectral inputs and three source/reference designs; the trajectory arrays and endpoint distribution summary are stored together in `lawgd_convergence.npz`. The 3249 dictionary functions are needed to estimate the retained 256 eigenpairs and are not 3249 transported modes.

```powershell
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --stage verify
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --stage reproduce --seed 1101 --refit
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --case rbf --stage verify
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 python -B supplementary/alanine_experiment.py --case rbf --stage reproduce --seed 301
uv run --with numpy==2.4.6 --with scipy==1.17.1 --with threadpoolctl==3.6.0 --with matplotlib==3.11.1 python -B supplementary/alanine_experiment.py --stage plot
```

`verify` recalculates metrics from saved clouds. `reproduce` reruns transport and checks against retained results; omit `--seed` for every seed. Fourier `--refit` rebuilds the spectrum; the small RBF spectrum is always refitted during reproduction. Retained particle arrays are not overwritten.

The alanine distribution PDF uses seed 1101 at s=8 for the angle panels and all three paired seeds for SW2. The coefficients are empirical moments of the initial particles, as in the convergence figure. There is no overall title or seed subtitle. The source-design and evaluation caveats appear in the Alanine section above and notebook notes.

The paired convergence figure uses `supplementary/alanine_convergence.py` and `supplementary/alanine_baselines.py`; its complete protocol is in [Three-method alanine convergence](#three-method-alanine-convergence). All nine prescribed runs reach s=8. The archive member `outputs/alanine/lawgd_convergence.npz` retains their checkpoint clouds, parameters, provenance, fixed target-score fit and numerical checks. BKT/LAWGD arrays reuse the s <= 8 prefixes of the original s=10 trajectories, recorded under `reused_from.original_horizon`; KDE is computed directly through s=8. The runner reproduces simulations or plots retained data:

```powershell
python -B supplementary/alanine_convergence.py --stage run --seed 1101
python -B supplementary/alanine_convergence.py --stage run --seed 1102
python -B supplementary/alanine_convergence.py --stage run --seed 1103
python -B supplementary/alanine_convergence.py --stage collect
python -B supplementary/alanine_convergence.py --stage verify
python -B supplementary/alanine_convergence.py --stage plot
python -B supplementary/experiment_store.py pack alanine
python -B supplementary/manuscript_results.py
```

Run these commands in the pinned environment above, including Numba 0.64.0. `run` writes temporary per-seed shards; `collect` verifies and merges them with the fitted-score metadata and KDE numerical checks into one result file. The retained archive contains the merged file, so `verify` and `plot` work directly from the archive. Temporary shards are unnecessary after the verified merge is archived. BKT/LAWGD spectral settings and the source/reference designs are retained; KDE has its own recorded periodic density estimates and integration controls.

By default, matching archived BKT/LAWGD trajectories are reused and new KDE trajectories are computed. With fresh temporary shards, add `--recompute-spectral` to rerun the spectral transports too. `--method KDE` selects only KDE. Compatible archived KDE checks are retained during collection.

`fig_alanine_convergence.pdf` uses one panel, a logarithmic error axis, the normalized interval [0, 8], and mean +/- sample SD over three paired designs. `ALANINE_DISPLAY_HORIZON` and `ALANINE_METHOD_LABELS` in `manuscript_results.py` define the shared report/figure window and labels. At its current manuscript insertion width of 0.62 textwidth it matches the printed font sizes of `fig_alanine.pdf`; there is no overall title or seed subtitle.

### Figure typography

`PAPER_FONT_SIZES` in `supplementary/figure_style.py` specifies the actual printed sizes for all manuscript figures: overall titles 11 pt, panel titles 9.5 pt, axis labels 9 pt, ticks 8.5 pt and legends 8 pt. Fonts are DejaVu Sans with normal weight. The plotting functions compensate for each canvas width and its current LaTeX insertion width, read from the manuscript files, so the number of panels does not reduce the printed font size. Subplot dimensions may differ.

Regenerate the affected PDFs after changing an insertion width. Manuscript PDFs export the full canvas without tight cropping, which would change the scaling calculation. The admissible-source rank figure uses a 1-by-4 layout; compact panels use shorter axis labels and fewer major tick labels, with every data point retained. Plot margins, title spacing and legend rows accommodate the printed sizes."""


def read_bytes(name):
    logical='outputs/'+name
    path=ROOT/logical
    if path.exists(): return path.read_bytes()
    with zipfile.ZipFile(ROOT/'outputs/data'/f'{group_for(logical)}.zip') as z:
        return z.read(logical)


def read_json(name):
    return json.loads(read_bytes(name))


def npz_record(name):
    with np.load(io.BytesIO(read_bytes(name))) as z:
        return json.loads(str(z['record']))


def pm(value):
    if isinstance(value,dict): mean,sd=value['mean'],value.get('std')
    else:
        values=list(value)
        mean=statistics.mean(values)
        sd=statistics.stdev(values) if len(values)>1 else None
    if mean is None: return 'failed'
    return f'{mean:.4f}'+(f' +/- {sd:.4f}' if sd is not None else '')


def table(lines,columns,rows):
    lines.extend(['','| '+' | '.join(columns)+' |','|'+'|'.join(['---']*len(columns))+'|'])
    lines.extend('| '+' | '.join(str(x) for x in row)+' |' for row in rows)
    lines.append('')


def append_data_comparison(lines):
    data=read_json('data_comparison/summary.json')
    rows=data['rows'];config=data['config']
    assert config['source_x2_variance']==.3 and len(rows)==6
    lines += ['## Equal-data comparison']
    table(lines,['beta','Method','SW2','Fit + sampling seconds','Reference-threshold hits'],[
        [r['beta'],r['label'],pm(dict(mean=r['sw2_mean'],std=r['sw2_std'])),
         (f"{r['total_seconds_mean']:.1f} +/- {r['total_seconds_std']:.1f}" if r['total_seconds_mean'] is not None else 'unavailable'),
         f"{r['hit_count']}/{r['n_repeats']}"] for r in rows])
    table(lines,['beta','Independent-target reference SW2','Crossing threshold'],[
        [r['beta'],pm(r),f"{r['mean']+r['std']:.4f}"] for r in data['references']])
    lines += [
        'All six entries use five paired realisations and report means +/- sample standard deviations. The source is the same as in the main two-dimensional double-well experiments: a cosine-squared first-coordinate bump on [0.4,1.6] and an independent centred Gaussian second coordinate with variance 0.3. Its density ratio is bounded for both coupling values, since 0.3 < 1/(2+beta).', '',
        'The 200000 trajectory pairs per seed, target clouds, ten-pair reference statistics and 64 projection directions are unchanged. All 30 transports and the ten spectral and ten drift fits were recomputed. Single-thread costs are measured per run and exclude common input generation and metric callbacks; the shared measured drift-fit cost is charged separately to each baseline. The BKT clouds and observation-time errors are checked against the corresponding main variance-0.3 results.', '',
        'The common horizons are T=10.7 for beta=0 and T=9.4 for beta=0.5. A reference-threshold crossing means SW2 at a prescribed common observation time is no greater than the independent-target-pair reference mean plus one sample standard deviation. The count is not restricted to the terminal observation and does not use the reference mean alone.', '',
        'Projection of training trajectories, reference samples and transported particles onto the numerical box remains a separate approximation; intermediate RK stages are also projected. The KDE method interacts through its evolving particle density. The fitted-drift Langevin clouds again show widened tails and boundary accumulation; the saved endpoint diagnostics do not isolate the causes. These comparisons concern the stated fitted models and discretisations, not a general ranking of the methods.', '',
        '### Manuscript integration', '',
        'The table above and [updated comparison figure](figures/fig_data_comparison.pdf) replace the equal-data values in Section 5 and Appendix D.2. The manuscript text and its figure copy are left for author integration. Remove the old variance-0.5 source qualification and retain the description of box projection. The figure displays errors, while costs are given in the text and table; adjust the caption accordingly. The unified variance-0.3 statement applies to the two-dimensional V_beta experiments; the uncoupled ten-dimensional experiment retains nine stationary Gaussian coordinates of variance 0.5.', '',
        'Suggested interpretation (all prescribed realisations retained):', '']
    lookup={(r['beta'],r['method']):r for r in rows}
    complete=all(r['failure_count']==0 and r['n_repeats']==5 for r in rows)
    lowest_error=complete and all(lookup[beta,'A']['sw2_mean'] < min(lookup[beta,m]['sw2_mean'] for m in ['B','D']) for beta in config['betas'])
    lowest_cost=complete and all(lookup[beta,'A']['total_seconds_mean'] < min(lookup[beta,m]['total_seconds_mean'] for m in ['B','D']) for beta in config['betas'])
    claims=[]
    if lowest_error: claims.append('the smallest mean terminal sliced Wasserstein distance')
    if lowest_cost: claims.append('the lowest mean fitting-plus-sampling cost')
    if claims:
        lines += ['> Under this fixed protocol, BKT has '+' and '.join(claims)+' at both coupling values.']
    for beta in config['betas']:
        counts=', '.join(f"{lookup[beta,m]['label']} {lookup[beta,m]['hit_count']}/{lookup[beta,m]['n_repeats']}" for m in ['A','B','D'])
        lines += [f'> At beta={beta:g}, the numbers of realisations that cross the reference threshold are {counts}.']
    lines += ['> The threshold is the independent-target reference mean plus one sample standard deviation; these finite-sample comparisons do not establish a general ordering of the methods.', '']


def append_alanine_convergence(lines):
    result=npz_record('alanine/lawgd_convergence.npz')
    spec=result['provenance']['spec'];runs=result['runs']
    methods=('BKT','LAWGD','KDE');seeds=tuple(spec['seeds'])
    times=np.asarray(spec['times'],dtype=float)
    displayed_times=times[times<=ALANINE_DISPLAY_HORIZON]
    horizon=float(displayed_times[-1]);labels=ALANINE_METHOD_LABELS
    degree=int(result['provenance']['degree']);lambda1=float(result['provenance']['lambda1'])
    groups={method:{} for method in methods}
    for row in runs:
        method,seed=row['method'],row['seed']
        if method not in groups or seed not in seeds or seed in groups[method]:
            raise ValueError('Unexpected or duplicate alanine comparison run.')
        if row['rank']!=(256 if method in ('BKT','LAWGD') else None):
            raise ValueError('The paired comparison retains only the 256-mode spectral setting.')
        groups[method][seed]=row

    def values(method,t):
        sample=[]
        for seed in seeds:
            row=groups[method].get(seed)
            if row is None:return None
            found=[c['sw2'] for c in row['checkpoints'] if c['s']==t]
            if len(found)!=1 or not np.isfinite(found[0]):return None
            sample.append(found[0])
        return sample

    def compact_fields(value,prefix='',depth=0):
        if not isinstance(value,dict):
            return [f'value={value}'] if isinstance(value,(str,int,float,bool)) else []
        selected=[]
        ordered=sorted(value.items(),key=lambda pair:(
            isinstance(pair[1],dict),
            not bool(re.search(r'error|difference|discrepancy|rms',pair[0]))))
        for key,item in ordered:
            name=f'{prefix}.{key}' if prefix else key
            if isinstance(item,dict) and depth<2:
                selected.extend(compact_fields(item,name,depth+1))
            elif isinstance(item,(str,int,float,bool)) or item is None:
                if re.search(r'pass|status|error|difference|discrepancy|rms|step|grid|bandwidth|solver|integrator|cap|rtol|atol|seed|checkpoint',key):
                    rendered=f'{item:.5g}' if isinstance(item,float) else str(item)
                    selected.append(f'{name}={rendered}')
        return selected[:12]

    lines += ['', '### Three-method alanine convergence', '',
        '**Main observation.** The mean BKT error decreases rapidly at small flow times and varies little after approaching its late-time level in this example.', '',
        f"[Convergence PDF](figures/fig_alanine_convergence.pdf). The single-panel comparison uses BKT, LAWGD and KDE, with {spec['particles']} particles per method, seeds {', '.join(map(str,seeds))}, the same initial/reference clouds and normalized horizon s={horizon:g}. BKT and LAWGD share 256 nonconstant eigenfunctions; KDE has no spectral truncation.", '',
        f"The retained checkpoint arrays cover [0, {horizon:g}]. BKT/LAWGD arrays are prefixes of the original s=10 trajectories, with that original horizon recorded in their reuse provenance; KDE is computed directly through s={horizon:g}.", '',
        'Both the spectrum and the fixed target KDE use exactly the same `train_all` array: all 250000 frames of trajectory 0. Both target the wrapped-Gaussian-smoothed empirical angle marginal with smoothing 0.1 rad. The spectral fit constructs Gram and Dirichlet matrices from smoothed Fourier moments; the KDE fit approximates the target density and its score on a periodic grid. These are different numerical representations of the same intended measure. Validation/evaluation frames enter neither fit.', '',
        f"The 256 retained eigenfunctions come from the degree-{degree} Fourier dictionary with {(2*degree+1)**2} functions. This static Gram/Dirichlet fit estimates the spectrum of a unit-mobility reversible surrogate; it uses no lagged trajectory pairs and does not recover physical MD kinetics. The common reference eigenvalue is lambda1={lambda1:.16g}; s={horizon:g} corresponds to {horizon/lambda1:.6f} units of surrogate diffusion time.", '',
        r'Write the fitted eigenpairs as $(\lambda_k,\phi_k)$. BKT uses $\widehat c_k=M^{-1}\sum_i\phi_k(X_0^i)$, frozen after initialization, and $\widehat\rho_s=1+\sum_k e^{-(\lambda_k/\lambda_1)s}\widehat c_k\phi_k$. Its field is $-\nabla\widehat\rho_s/[\lambda_1\max(\widehat\rho_s,0.001)]$ and requires no explicit target density or score. LAWGD uses the current moments $M^{-1}\sum_i\phi_k(X_s^i)$ and field $-\sum_k\lambda_k^{-1}\nabla\phi_k(X_s^j)M^{-1}\sum_i\phi_k(X_s^i)$. Thus the comparison starts from identical empirical moments. Both alanine figures use these same S-regime trajectories.', '',
        '**KDE method.** KDE denotes a kernel implementation of the classical diffusion-velocity particle method, dating at least to [Degond and Mustieles (1990)](https://doi.org/10.1137/0911018). The kernel-smoothed velocity is described in [Chertock (2017), Section 4.1.2, equations (33)-(35)](https://chertock.wordpress.ncsu.edu/files/2024/01/Chertock_particles.pdf), [DOI](https://doi.org/10.1016/bs.hna.2016.11.004). Our periodic kernels and numerical solver adapt this framework to the angle data.', '',
        r'All methods use the same reference clock $s=\lambda_1t$. BKT and LAWGD use generator $L/\lambda_1$ and mobility $I/\lambda_1$; LAWGD cancels this scaling between mobility and inverse eigenvalues. KDE uses $dX_s^i/ds=[\nabla\log\widehat\pi(X_s^i)-\nabla\log\widehat q_s(X_s^i)]/\lambda_1$. The target estimate $\widehat\pi$ is fitted once from training frames. The current density $\widehat q_s=M^{-1}\sum_j K_h^{\mathrm{per}}(\cdot-X_s^j)$ uses all evolving particles, including self terms, and is recomputed at each field evaluation. Its fixed isotropic bandwidth h=0.1 rad matches the target smoothing but serves a separate density estimate. This deterministic method interacts through the current particle cloud and uses no Brownian noise.', '',
        f"The displayed grid includes {len(displayed_times)} requested particle checkpoints per run through s={horizon:g}. Metrics are evaluated from the particle states at these times; no error curve is fitted or smoothed. The horizontal axis measures normalized flow time, not physical MD time or computation time. Numerical controls are method-specific."]
    fit=result.get('baseline_fit',{})
    if fit:
        lines += ['', f"The fixed target fit uses positive separable periodic Gaussian convolution on a {fit.get('grid_size','unreported')}-by-{fit.get('grid_size','unreported')} grid, with a deposition-variance correction; its score is the gradient of a cubic spline interpolating the log density. The evolving particle KDE is evaluated by direct periodic kernel sums. BDF integration uses an analytic particle Jacobian and a finite-difference target-score Jacobian."]
        if 'density_floor_grid_fraction' in fit:
            floor=float(fit['density_floor'])
            nodes=fit.get('density_floor_grid_nodes',fit['density_floor_grid_fraction']*fit['grid_size']**2)
            floor_mass=nodes*fit['spacing']**2*floor
            lines += [f"The target-density floor is {floor:.5g}, active at {100*fit['density_floor_grid_fraction']:.3g}% of grid nodes. Those nodes contribute {floor_mass:.3g} to the normalized density-grid quadrature mass. The floor, grid and interpolation remain part of the fitted approximation."]
    controls=[]
    for method in methods:
        if method in ('BKT','LAWGD'):
            text=(f"DOP853; rtol={spec['rtol']:g}; atol={spec['atol']:g}; "
                  f"maximum normalized step={spec['max_step']:g}; "
                  f"first normalized step={spec['first_step_raw']:g}*lambda1; "
                  f"normalized speed cap={spec['raw_bkt_speed_cap']:g}/lambda1")
            if method=='BKT':text+=f"; ratio floor={spec['bkt_ratio_floor']:g}"
        else:
            variants=[]
            for row in groups[method].values():
                diagnostic=row.get('baseline_diagnostics',{})
                parameters={**diagnostic,**diagnostic.get('numerical_parameters',{})}
                keys=('solver','integrator','backend','raw_step','step','normalized_step','max_step',
                      'first_step_raw','normalized_max_step',
                      'rtol','atol','kernel','bandwidth','kde_bandwidth','grid_size',
                      'particle_grid_size','density_floor','drift_cap','speed_cap',
                      'kde_density_floor','include_self',
                      'maximum_seconds','maximum_evaluations','maximum_steps')
                detail='; '.join(f'{key}={json.dumps(parameters[key],separators=(",",":"))}'
                                 for key in keys if key in parameters)
                if detail and detail not in variants:variants.append(detail)
            text=' / '.join(variants) if variants else 'Controls are not available in the saved run metadata.'
        controls.append([labels[method],text])
    table(lines,['Method','Recorded numerical controls'],controls)
    verification=result.get('verification')
    if verification:
        lines += [f"Saved-cloud verification checked all {verification['checkpoints']} retained checkpoints; the maximum SW2/TV discrepancy was {verification['maximum_metric_error']:g}.", '']
    table(lines,['Method','Completed archived runs','Last common plotted s'],[
        [labels[method],f"{sum(r['status']=='ok' for r in groups[method].values())}/{len(seeds)}",
         min((min(horizon,r['checkpoints'][-1]['s']) for r in groups[method].values()),default='Not available')]
        for method in methods])
    checks=result.get('baseline_numerical_checks',{})
    if checks:
        table(lines,['KDE numerical check','Recorded diagnostic'],[
            [name,'; '.join(compact_fields(check)) or 'Detailed diagnostics are retained in the result archive.']
            for name,check in checks.items()])
    table(lines,['s',*[f'{labels[method]} SW2' for method in methods]],[
        [t,*[pm(sample) if (sample:=values(method,t)) is not None else 'Not reached by all prescribed seeds'
              for method in methods]]
        for t in (1.,2.,4.,6.,8.) if t in displayed_times])
    lines += ['BKT approaches the low-error regime substantially earlier than LAWGD. Its mean error then settles smoothly into a steady plateau, while LAWGD shows a modest late rebound. The final displayed BKT and LAWGD errors are similar relative to the between-seed variability.', '']
    early,late=values('BKT',4.),values('BKT',horizon)
    if early is not None and late is not None:
        lines += [f"BKT's mean SW2 changes only from {statistics.mean(early):.4f} at s=4 to {statistics.mean(late):.4f} at s={horizon:g}, illustrating its steady late-time behavior. The main observed benefit is rapid settling followed by a smooth, sustained low-error trajectory.", '']
    kde_early,kde_plateau,kde_final=values('KDE',0.1),values('KDE',0.5),values('KDE',horizon)
    bkt_early=values('BKT',0.1)
    if all(sample is not None for sample in (kde_early,kde_plateau,kde_final,bkt_early,late)):
        lines += [f"KDE decreases initially and then settles at a higher observed error: its SW2 is {pm(kde_plateau)} at s=0.5 and {pm(kde_final)} at s={horizon:g}, compared with BKT's {pm(late)} at s={horizon:g}. BKT also reduces error earlier: at s=0.1, its SW2 is {pm(bkt_early)}, versus {pm(kde_early)} for KDE. These results describe the retained protocol; they do not isolate the source of KDE's higher plateau.", '']
    unfinished=[f"{labels[method]}, seed {seed}: {groups[method].get(seed,{}).get('status','missing')}"
                for method in methods for seed in seeds
                if groups[method].get(seed,{}).get('status')!='ok']
    if unfinished:
        lines += ['Incomplete prescribed runs: '+'; '.join(unfinished)+'. Missing tails are not imputed, and successful subsets do not supply a method mean.', '']
        if groups['KDE']:
            table(lines,['KDE seed','Status','Last archived s','Solver reached s',f'SW2 at displayed s={horizon:g}','Stop diagnostic'],[
                [seed,row['baseline_diagnostics']['status'],row['checkpoints'][-1]['s'],
                 f"{row['baseline_diagnostics'].get('completed_normalized_time',row['completed_s']):.8g}",
                 next((f"{c['sw2']:.5f}" for c in row['checkpoints'] if c['s']==horizon),'Not reached'),
                 row['baseline_diagnostics'].get('failure') or 'None']
                for seed,row in sorted(groups['KDE'].items())])
        common={method:min((min(horizon,r['checkpoints'][-1]['s']) for r in groups[method].values()),default=0.) for method in methods}
        omitted=[method for method in methods if common[method]==0.]
        if omitted:
            lines += ['No nonzero checkpoint is available for all prescribed seeds of '+', '.join(labels[method] for method in omitted)+'. These methods have no mean curve in the PDF; all individual outcomes and stop diagnostics remain in the archive. Their numerical stops do not establish poor sampling accuracy.', '']
        if any(0.<end<horizon for end in common.values()):
            lines += [f'Any partial curve and SD band stop at the last checkpoint reached by all three prescribed seeds. An x marker identifies its truncation; this endpoint is a computational limit, not an equilibrium estimate or a completed s={horizon:g} result.', '']
    lines += [
        'Rapid convergence here describes the approach to the observed low-error plateau in normalized flow time; steadiness describes the plotted mean error over time. These finite-horizon observations do not establish an asymptotic convergence rate or CPU-time speedup.', '',
        'Shading is mean +/- sample SD across the three prescribed paired source/reference designs, with one common training dataset and fixed fitted approximations. This variation is not a confidence interval or replication across independent MD datasets. SW2 uses the same 32 fixed directions in the four-dimensional periodic embedding as the main alanine experiment. The comparison uses auxiliary reversible diffusions of the smoothed angular marginal.', '',
        f"**Suggested caption.** Alanine convergence over normalized flow time s in [0, {horizon:g}]. The mean BKT error decreases rapidly at small flow times and then varies little over the remaining interval. Lines and shading show mean and sample standard deviation of sliced Wasserstein error over three paired source/reference designs, with {spec['particles']} particles per method. BKT and LAWGD share 256 nonconstant eigenfunctions and initial empirical coefficients; KDE uses the same training angles and initial/reference clouds. KDE is a classical diffusion-velocity particle method with a fixed estimated target score and feedback through a kernel estimate of the current density. Numerical controls are method-specific. The horizontal axis denotes normalized flow time, not physical MD time or computation time."]


def sample_size_rows():
    """Rebuild the appendix sensitivity table from all prescribed seed rows."""
    rows=[];study=read_json('admissible_source/summary.json')
    primary=read_json('results.json');budgets=study['config']['sample_size_budgets']
    for beta in study['config']['betas']:
        for n in budgets:
            values=[r['sw2'] for r in study['runs'] if r['beta']==beta and r['n_pairs']==n and 'sample_size' in r['roles']]
            rows.append(dict(system=f'A2_beta{beta}',n_pairs=n,mean=statistics.mean(values),std=statistics.stdev(values)))
    for name in ['B_quartic4','B_poly9','A10_beta0.0','A10_beta0.5']:
        for n in budgets:
            values=[r['sw'] for r in primary[name]['sample_size'][str(n)]]
            rows.append(dict(system=name,n_pairs=n,mean=statistics.mean(values),std=statistics.stdev(values)))
    return dict(budgets=budgets,rows=rows)


def write_tables():
    """Export both manuscript tables from the current source protocol."""
    from experiment_store import managed_outputs
    primary=read_json('results.json')
    study=read_json('admissible_source/summary.json')
    rows=[]
    for beta in study['config']['betas']:
        row=dict(system=f'A2_beta{beta}',training_pairs=200000,particles=2000,modes=64)
        for method,key in [('FD','FD'),('RBF','RBF'),('Legendre','Legendre')]:
            values=[r['sw2'] for r in study['runs'] if r['beta']==beta and r['method']==method and 'main' in r['roles']]
            row[key+'_mean']=statistics.mean(values);row[key+'_SD']=statistics.stdev(values)
        ref=next(r for r in study['references'] if r['beta']==beta)
        row.update(reference_mean=ref['mean'],reference_SD=ref['std'],reference_repeats=10)
        rows.append(row)
    for name in ['B_quartic4','B_poly9','A10_beta0.0','A10_beta0.5']:
        case=primary[name];fd=case.get('fd',case.get('fd_rscan',{}).get('64',{}))
        ref=case['reference']['metrics']['sw']
        rows.append(dict(system=name,training_pairs=case['selected_n'],particles=case['M'],modes=case['r'],
            FD_mean=fd.get('sw'),FD_SD=None,RBF_mean=case['rbf']['mean'],RBF_SD=case['rbf']['std'],
            Legendre_mean=case['poly']['mean'],Legendre_SD=case['poly']['std'],
            reference_mean=ref['mean'],reference_SD=ref['std'],reference_repeats=10))
    for d in [10,50]:
        case=read_json(f'product_{d}_results.json');ref=case['reference']['metrics']['sw']
        rows.append(dict(system=f'product_{d}',training_pairs=200000,particles=20000,modes='16 per coordinate',
            FD_mean=case['methods']['exact']['sw'],FD_SD=None,RBF_mean=case['methods']['estimated']['sw'],RBF_SD=None,
            Legendre_mean=case['methods']['legendre']['sw'],Legendre_SD=None,
            reference_mean=ref['mean'],reference_SD=ref['std'],reference_repeats=10))
    with managed_outputs('double_well'):
        folder=ROOT/'outputs/tables';folder.mkdir(exist_ok=True)
        for appendix in [False,True]:
            columns=[k for k in rows[0] if appendix or not k.startswith('Legendre')]
            path=folder/('appendix_dictionary_results.csv' if appendix else 'main_results.csv')
            with path.open('w',newline='',encoding='utf-8') as stream:
                writer=csv.DictWriter(stream,columns,extrasaction='ignore');writer.writeheader()
                writer.writerows(r for r in rows if appendix or r['system']!='product_10')
        with (folder/'well_masses.csv').open('w',newline='',encoding='utf-8') as stream:
            writer=csv.writer(stream);writer.writerow(['system','basin','target_mass'])
            for name,case in primary.items():
                for i,mass in enumerate(case.get('target',{}).get('mass2d',[])):
                    writer.writerow([name,i,mass])
        with (folder/'sample_size.csv').open('w',newline='',encoding='utf-8') as stream:
            records=sample_size_rows()['rows']
            writer=csv.DictWriter(stream,list(records[0]));writer.writeheader();writer.writerows(records)
    print('Exported current manuscript tables, including the coupled-10D limitation.')


def verify_saved_results():
    """Recompute stored cloud metrics and rerun every matched OU trajectory."""
    from threadpoolctl import threadpool_limits
    import ou_path_validation as ou
    from run_admissible_source import specifications, run_id
    checked={};largest=0.
    with threadpool_limits(limits=1):
        for study,count in [('admissible_source',156),('data_comparison',30)]:
            rows=read_json(study+'/runs.json')
            assert len(rows)==count and all(r['status']=='ok' for r in rows)
            if study=='admissible_source':
                config=read_json(study+'/config.json')
                expected={run_id(r) for beta in config['betas'] for r in specifications(config,beta)}
                assert expected=={r['run_id'] for r in rows}
            else:
                assert {(r['beta'],r['seed'],r['method']) for r in rows}=={
                    (b,s,m) for b in [0.,.5] for s in range(5) for m in ['A','B','D']}
            for beta in sorted({r['beta'] for r in rows}):
                with np.load(io.BytesIO(read_bytes(f'{study}/evaluation_beta{beta:g}.npz'))) as z:
                    target,directions=z['target'],z['directions']
                ordered=np.sort(target@directions.T,axis=0)
                for row in [r for r in rows if r['beta']==beta]:
                    key=row['run_id'] if study=='admissible_source' else f"beta{beta:g}_seed{row['seed']}_{row['method']}"
                    with np.load(io.BytesIO(read_bytes(f'{study}/endpoint_{key}.npz'))) as z:x=z['final']
                    assert np.isfinite(x).all() and x.shape==target.shape
                    measured=float(np.sqrt(np.mean((np.sort(x@directions.T,axis=0)-ordered)**2)))
                    error=abs(measured-row['sw2']);largest=max(largest,error)
                    assert error<1e-12,(study,key,error)
            checked[study]=count
            print(f'{study}: all {count} endpoint metrics and prescribed runs verified.',flush=True)
        config=read_json('ou_path_validation/config.json')
        rows=read_json('ou_path_validation/runs.json')
        assert len(rows)==180
        keys={(r['seed'],r['r'],r['dt'],r['regime']) for r in rows}
        assert keys=={(s,r,h,c) for s in config['seeds'] for r in config['ranks'] for h in config['steps'] for c in config['regimes']}
        endpoint_error=residual_error=0.
        for seed in config['seeds']:
            with np.load(io.BytesIO(read_bytes(f'ou_path_validation/paths_seed_{seed}.npz'))) as z:
                sequences=np.random.SeedSequence(seed).spawn(3)
                source=np.random.default_rng(sequences[0]).normal(config['source_mean'],config['source_std'],config['particles'])
                np.testing.assert_array_equal(source,z['X0'])
                independent=np.random.default_rng(sequences[1]).normal(config['source_mean'],config['source_std'],config['particles'])
                np.testing.assert_array_equal(independent,z['independent_X0'])
                np.testing.assert_array_equal(np.random.default_rng(sequences[2]).standard_normal(config['particles']),z['target_reference'])
                for row in [r for r in rows if r['seed']==seed]:
                    rank,regime,dt=row['r'],row['regime'],row['dt']
                    c=ou.population_coefficients(config['source_mean'],config['source_std'],rank) if regime=='P' else ou.empirical_coefficients(independent if regime=='I' else source,rank)
                    np.testing.assert_array_equal(c,z[f'coeff_{regime}_r{rank}'])
                    times,paths,diag=ou.transport(source,c,config['horizon'],dt,config['density_floor'],config['velocity_cap'])
                    key=f"{regime}_r{rank}_h{round(dt*1000):03d}"
                    endpoint_error=max(endpoint_error,float(np.max(abs(paths[-1]-z['endpoint_'+key]))))
                    assert endpoint_error<1e-12
                    residual,_=ou.checked_residual(times,paths,config['source_mean'],config['source_std'],config['quadrature'])
                    for name in ['D','B','identity_rms_error']:
                        error=abs(residual[name]-row[name]);residual_error=max(residual_error,error)
                        assert error<1e-10,(seed,key,name,error)
                    assert abs(ou.gaussian_w2(paths[-1])-row['w2_target'])<1e-12
                    for name in ['density_floor_events','nonpositive_density_events','speed_cap_events']:
                        assert diag[name]==row[name]
            print(f'OU seed {seed}: all 18 transports, residual bounds and safeguard counts reproduced.',flush=True)
        checked.update(ou_transports=180,max_sw2_difference=largest,
                       ou_endpoint_max_difference=endpoint_error,ou_residual_max_difference=residual_error)
    print(json.dumps(checked,indent=2))
    return checked


def write_report():
    primary=read_json('results.json')
    a=read_json('admissible_source/summary.json')
    lines=['# Manuscript experiment results','',
        'Retained results include favorable and unfavorable manuscript cases. Every repeated summary includes all prescribed seeds and uses sample standard deviations. Alanine retains one 256-mode Fourier experiment with distribution and convergence figures, together with the RBF control and collapse diagnostics.','',
        'Synthetic multivariate distances use 64 fixed projections (seed 0); references use ten target-cloud repetitions. The analytical OU studies compare directly with the Gaussian target. References describe empirical sampling variability and are not universal lower bounds. Alanine has a separate periodic metric.','',
        '## Manuscript correspondence']
    table(lines,['Manuscript item','Retained configuration'],[
        ['Figure 1 and dictionary tables','Koopman (RBF) and Koopman (Legendre) identify reversible gEDMD generator estimates; all use the same BKT transport. Figure 1 shows one fixed realisation, whereas repeated table entries report means and sample standard deviations.'],
        ['Table 1','10D double well product, beta=0: one double-well factor and nine stationary Gaussian factors. 50D double-well product: fifty double-well factors. Product refers to the invariant density; the potential is additive.'],
        ['[Figure 10](figures/fig_alanine.pdf)','256-mode BKT at s=8, seeds 1101-1103, empirical initial coefficients. The angle panels show seed 1101; the error panel includes all three paired designs.'],
        ['[Figure 11](figures/fig_alanine_convergence.pdf)','The same BKT trajectories over 0 <= s <= 8, compared with LAWGD and KDE. BKT and LAWGD share the 256 eigenpairs and initial empirical coefficients.']])
    lines+=['## Fixed protocols']
    table(lines,['Experiment','Setup'],[
        ['1D OU','N(1.5,0.5^2) to N(0,1); Hermite spectrum; RK4 h=0.05; initial-particle coefficients (S).'],
        ['Matched OU paths','M=2000; r=10,20,40; T=6; h=0.05,0.025; seeds 1000-1009; P/I/S; all 180 runs.'],
        ['10D OU','Coupling 0 and 0.15; M=5000; 30 modes/coordinate; T=6; h=0.05; seeds 700-702.'],
        ['2D double wells','beta=0,0.25,0.5,1; M=2000; n=200000; r=64; RBF J=145; FD-201; T=8/lambda1; h=0.05.'],
        ['4/9 wells','M=2000; n=200000; r=64; RBF/Legendre/FD-201; h=0.02; five/three seeds.'],
        ['10D double wells','beta=0,0.5; M=1000; n=100000; r=16; RBF J=657; h=0.05; two seeds.'],
        ['10D/50D double-well products','M=20000; n=200000; r=16 per coordinate; T=10.6854; h=0.02; one fixed cloud.'],
        ['Equal-data comparison','beta=0,0.5; n=200000 shared pairs; M=2000; five paired seeds; common horizon.']])
    lines+=['The synthetic ratio floor is 0.001 and speed cap is 20. The boxed double-well solver projects intermediate RK stages. The main 2D double-well experiments and equal-data comparison share the admissible source: a cosine-squared x1 bump on [0.4,1.6] and x2 variance 0.3. The uncoupled 10D experiment retains nine stationary harmonic coordinates of variance 0.5. Reproduction uses frozen main training sizes; the appendix sample-size and rank studies remain explicit sensitivity experiments.','',
        '## Ornstein-Uhlenbeck results']
    ou=read_json('ou_results.json')
    table(lines,['Scan','Values','W2'],[
        [name,', '.join(str(r[key]) for r in ou[scan]),', '.join(f"{r['w2']:.4f}" for r in ou[scan])]
        for scan,key,name in [('rank_scan','r','Rank (M=10000, T=6)'),('particle_scan','M','Particles (r=40, T=6)'),('time_scan','T','Time (r=40)')]])
    lines += [f"At M=10000 the reference is {pm(ou['reference']['metrics']['w2'])}. The 1D notebook scans use midpoint quantiles; the matched path diagnostic uses exact Gaussian quantile-interval integrals."]
    table(lines,['10D coupling','Final SW2','Reference SW2','Relative covariance error'],[
        [d['config']['coupling'],pm(d['time_summary'][-1]['metrics']['sw2']),pm(d['reference']['metrics']['sw2']),pm(d['time_summary'][-1]['metrics']['covariance_relative_error'])]
        for d in [read_json('ou_hd_uncoupled_results.json'),read_json('ou_hd_results.json')]])
    p=read_json('ou_path_validation/summary.json')
    table(lines,['Matched OU, h=0.025','Regime','W2 to target','Endpoint D','Residual-norm B'],[
        [g['r'],g['regime'],pm(g['metrics']['w2_target']),pm(g['metrics']['D']),pm(g['metrics']['B'])] for g in p['groups'] if g['dt']==.025])
    lines += [f"Exact-flow image of the same finite cloud: {pm(p['references']['exact_flow_w2'])}; independent-target reference: {pm(p['references']['target_reference_w2'])}. P gives the smaller discrepancy from the paired exact trajectories; S gives the smaller empirical target distance. I uses 2000 extra source points. The same-sample corollary compares P and S under additional deterministic common-region bounds; those hypotheses are not verified by these experiments.",'',
        'D is checked from endpoints and signed residual integration; B takes the norm before time integration. The maximum endpoint-identity RMS discrepancy is 2.7e-16. Quadrature and step differences are numerical diagnostics, not rigorously enclosed certificates. All ranks and both steps remain in the saved results.']
    table(lines,['OU rank','Minimum ratio at t=0','Screened Lipschitz integral','Minimum good-region mass'],[
        [r['r'],f"{r['density_ratio_minima'][0]:.4f}",f"{r['lipschitz_integral_good']:.4f}",f"{r['min_good_mass']:.4f}"] for r in read_json('ou_diagnostics.json')['rows']])
    lines+=['## Double wells, multiwells and products', '', 'Koopman (RBF) and Koopman (Legendre) denote generator eigenpairs estimated by reversible gEDMD with the respective dictionaries. These labels distinguish spectral approximations in the same BKT transport formula; FD denotes the finite-difference spectrum.']
    rows=[]
    for beta in a['config']['betas']:
        values={m:[r['sw2'] for r in a['runs'] if r['beta']==beta and r['method']==m and 'main' in r['roles']] for m in ['FD','RBF','Legendre']}
        rows.append([f'2D double well{" product" if beta==0 else ""}, beta={beta:g}',*[pm(values[m]) for m in ['FD','RBF','Legendre']],pm(next(r for r in a['references'] if r['beta']==beta))])
    for name,label in [('B_quartic4','2D four-well product'),('B_poly9','2D nine wells'),('A10_beta0.0','10D double well product, beta=0'),('A10_beta0.5','10D double well, beta=0.5')]:
        r=primary[name];fd=r.get('fd',r.get('fd_rscan',{}).get('64'))
        rows.append([label,f"{fd['sw']:.4f}" if fd else '--',pm(r['rbf']),pm(r['poly']),pm(r['reference']['metrics']['sw'])])
    for d in [10,50]:
        p=read_json(f'product_{d}_results.json')
        rows.append([f'{d}D double-well product',*[f"{p['methods'][m]['sw']:.4f}" for m in ['exact','estimated','legendre']],pm(p['reference']['metrics']['sw'])])
    table(lines,['System','FD','Koopman (RBF)','Koopman (Legendre)','Reference SW2'],rows)
    lines+=['Double wells and four wells reach the reference scale; nine wells and coupled 10D remain above it. Nine-well Legendre seed errors are '+', '.join(f'{x:.3f}' for x in primary['B_poly9']['poly']['sw'])+'. All are retained. The product results rely on separability: the potential is a sum of coordinate potentials and the invariant density is a product. The uncoupled 10D double well has one double-well factor and nine stationary N(0, 0.5) factors; the 10D/50D double-well products have a double-well factor in every coordinate.']
    table(lines,['Product','RBF worst marginal W2','Reference worst marginal W2','RBF energy','Reference energy','RBF negative-count TV','Reference negative-count TV'],[
        [d,f"{p['methods']['estimated']['max_marginal']:.4f}",pm(p['reference']['metrics']['max_marginal']),f"{p['methods']['estimated']['energy']:.4f}",pm(p['reference']['metrics']['energy']),f"{p['methods']['estimated']['negative_count_tv']:.4f}",pm(p['reference']['metrics']['negative_count_tv'])]
        for d in [10,50] for p in [read_json(f'product_{d}_results.json')]])
    lines+=['### Appendix sensitivity results','',
        'Rank scans use the first source seed; they retain nonmonotone and unstable results. The complete 2D ranks, paired step checks and safeguard counts remain in the 156-run admissible-source suite.']
    rows=[]
    for name,label in [('B_quartic4','4 wells'),('B_poly9','9 wells')]:
        r=primary[name]
        for method,scan in [('FD',r['fd_rscan']),('Koopman (RBF)',r['rbf']['rscan']),('Koopman (Legendre)',r['poly']['rscan'])]:
            rows.append([label,method,', '.join(f"r={rank}: {v['sw']:.3f}" for rank,v in sorted(scan.items(),key=lambda x:int(x[0])))])
    table(lines,['System','Spectrum','SW2 by rank'],rows)
    table(lines,['Coupled 10D dictionary','Size parameter','Requested rank','SW2'],[
        [{'rbf':'Koopman (RBF)','poly':'Koopman (Legendre)'}[r['dictionary']],r['size'],r['r_requested'],f"{r['sw']:.4f}"] for r in read_json('a10_sweep.json')['rows']])
    lines+=['The coupled 10D dictionary comparison uses n=100000 and the first seed. Its horizon changes with the fitted eigenvalue; no configuration reaches the reference.']
    b=sample_size_rows()
    system_labels={f'A2_beta{beta}':f'2D double well{" product" if beta==0 else ""}, beta={beta:g}' for beta in a['config']['betas']}
    system_labels.update(B_quartic4='2D four-well product',B_poly9='2D nine wells',
                         **{'A10_beta0.0':'10D double well product, beta=0',
                            'A10_beta0.5':'10D double well, beta=0.5'})
    table(lines,['System',*[f'n={n}' for n in b['budgets']]],[
        [system_labels[name],*[pm(next(r for r in b['rows'] if r['system']==name and r['n_pairs']==n)) for n in b['budgets']]]
        for name in dict.fromkeys(r['system'] for r in b['rows'])])
    table(lines,['2D beta','Independent I','Same-sample S'],[
        [beta,*[pm(r['sw2'] for r in a['runs'] if r['beta']==beta and r['method']=='RBF' and r['regime']==regime and 'coefficient_comparison' in r['roles']) for regime in ['I','S']]] for beta in a['config']['betas']])
    lines+=['I uses an extra 2000 independent source draws, with coefficients fixed thereafter. The original coupled full-plane Gaussian source violates the bounded-ratio assumption at positive coupling. Variance 0.3 restores this source condition for the four 2D cases; box projection and estimated eigenpairs still prevent verification of every theorem hypothesis.','']
    append_data_comparison(lines)
    lines+=['## Alanine dipeptide']
    cfg=read_json('alanine/config.json');case=cfg['setting']
    result=npz_record('alanine/lawgd_convergence.npz')
    distribution=result['distribution'];runs=distribution['runs']
    lines += [f"Public mdshare trajectories 0/1/2 supply fitting/validation/evaluation data (250 ns and 250000 frames each, 1 ps spacing). All trajectory-0 frames enter the fit; 25000 fixed subsampled frames define the source partition. Validation/evaluation pools have 12000 frames each. Fourier degree {case['degree']} gives {(2*case['degree']+1)**2} basis functions; the transport retains 256 nonconstant modes. Gram cutoff {case['cutoff']:g}, smoothing {case['smoothing']:.2f} rad, s=lambda1*T={distribution['s']:g}.", '',
        'The local wrapped-Gaussian source uses a training-derived mean and covariance (scale 0.7^2). Each 1000-point cloud uses the first 1000 points of a scrambled 1024-point Sobol net, the Gaussian inverse CDF and a fixed Cholesky factor. The spectral coefficients are empirical moments of these same initial particles (regime S), fixed thereafter. Sobol points are not iid samples, so this example does not directly verify the theorem\'s iid sampling bound. Seeds 1101-1103 share one fitted spectrum. The distribution figure and the BKT convergence curve use exactly the same trajectories and endpoint s=8. Integration controls are specified in the convergence protocol below.']
    table(lines,['Metric','Initial','BKT at s=8','Reference-reference'],[
        [metric,pm(r['initial'][metric] for r in runs),pm(r['final'][metric] for r in runs),pm(r[ref] for r in runs)] for metric,ref in [('sw2','reference_sw'),('mass_tv','reference_mass_tv')]])
    generated=np.mean([r['final']['masses'] for r in runs],axis=0)
    target=np.mean([r['target_masses'] for r in runs],axis=0)
    ratio=statistics.mean(r['final']['sw2'] for r in runs)/statistics.mean(r['reference_sw'] for r in runs)
    wins=sum(r['final']['sw2']<r['reference_sw'] for r in runs)
    lines += [f"BKT SW2 is {ratio:.3f} times the reference mean ({wins}/{len(runs)} smaller paired values). Local-width ratio: {pm(r['final']['local_width_ratio'] for r in runs)}. Rare-region mass: {generated[2]:.4f} versus {target[2]:.4f}. The global distances are of the same order as the sampling reference; rare-region coverage and within-basin spread remain imperfect.", '',
        'SW2 uses 32 projections (seed 2026) in [cos(phi), cos(psi), sin(phi), sin(psi)], an extrinsic periodic embedding. Mass TV measures four training-defined regions, not full densities. Three clouds per seed are disjoint subsets of one evaluation trajectory. Variability is conditional on the spectrum and reflects scrambling/reference draws, not independent MD datasets.', '',
        'The operator is a unit-mobility reversible surrogate of the smoothed angle marginal, not the physical MD generator. Outputs are angles, not full molecular configurations.']
    reproduction=result.get('reproduction_check',{})
    if reproduction:
        for check in reproduction.get('comparisons',[]):
            lines += ['', f"Fourier/BKT reproduction check, seed {check['seed']} (spectrum refitted: {check['refit']}): endpoint wrapped RMS difference {check['endpoint_wrapped_rms']:.3g} rad; absolute SW2 difference {check['sw2_difference']:.3g}. The saved trajectories are retained unchanged.", '']
    lines += ['', '### Retained RBF failure', '',
        'Periodic 16x16 RBF grid plus constant (J=257), width 0.45, r=64, Gram cutoff 1e-5, smoothing 0.08 rad (jitter seed 91073), population Gauss-Hermite source moments, and iid source clouds. Dictionary, rank, smoothing, coefficient regime, horizon and source design differ from the 256-mode Fourier experiment, so the contrast does not isolate a dictionary effect.']
    rbf=npz_record('alanine/rbf_diagnostic.npz')
    rows=[]
    for name,taus in [('collapse',[.25,16.]),('control',[.25])]:
        rr=rbf[name]['runs']
        for tau in taus:
            cp=[next(c for c in r['checkpoints'] if c['tau']==tau) for r in rr]
            rows.append([name,', '.join(str(r['seed']) for r in rr),tau,pm(c['sw2'] for c in cp),pm(c['mass_tv'] for c in cp),pm(c['local_width_ratio'] for c in cp)])
    table(lines,['Case','Seeds','tau','SW2','Mass TV','Local-width ratio'],rows)
    lines+=['The long-time RBF cloud collapses within basins despite moderate sliced error. The width diagnostic preserves this negative result. Reconstructed arrays match the original reported metrics within 1e-4, using tight ODE tolerances.']
    append_alanine_convergence(lines)
    lines+=['', '## Numerical consistency and interpretation', '',
        'The current manuscript retains eleven figure PDFs, one experiment report, fixed configurations and four checksum-verified archives. Koopman (RBF) and Koopman (Legendre) describe the dictionary used for the reversible gEDMD generator estimate; every such curve uses the same BKT transport formula.', '',
        'Data attribution: the [mdshare alanine page](https://markovmodel.github.io/mdshare/ALA2/) documents the simulations and publication credits, including Nueske et al. (2017), cited in the manuscript. The Computational Molecular Biology Group, Freie Universitaet Berlin, supplies the data under the [mdshare CC BY 4.0 terms](https://markovmodel.github.io/mdshare/). Retained arrays use float64 conversion and the fixed subsampling described above.', '',
        'The equal-data comparison now contains 30 freshly computed variance-0.3 transports with individual fit and sampling times. Its source-independent inputs are checked against the previous protocol, and its ten BKT results are checked against the main variance-0.3 experiment. Other retained numerical experiments are unchanged. The earlier reproduction audit checked all 156 admissible-source endpoints and 112 notebook transport caches, reran all 180 matched OU transports, and checked 155 synthetic and 44 alanine table entries. The paired alanine archive contains 1593 BKT/LAWGD/KDE checkpoints; their SW2 and basin TV are checked against the saved clouds by the verification command.', '',
        'The alanine distribution summary uses the three BKT endpoints at s=8 from the convergence archive, with their original sources and evaluation clouds. The saved input file contains only the 256 retained eigenpairs and the three source/reference designs needed by this experiment. No independent set of Fourier transport results is used for the distribution figure. The RBF controls remain as explicit limitations.', '',
        'Reference distances describe sampling variability and are not lower bounds for transport. In the equal-data comparison, a reference-threshold crossing uses the reference mean plus one sample standard deviation at a prescribed observation time. The two-dimensional admissible source has harmonic variance 0.3; the uncoupled ten-dimensional source has nine stationary harmonic coordinates of variance 0.5.', '',
        'FD-201 uses a 201-by-201 grid for two-dimensional systems; the high-dimensional FD comparisons use separable one-dimensional factors. Separable high-dimensional experiments do not establish performance on general coupled targets. The nine-well and coupled-10D limitations remain. The angular-marginal example does not test physical molecular kinetics.', '',
        'The same-sample comparison requires the stated common-region assumptions. Its coefficient factor is Delta_M = M^(-1/2) sum_k sqrt(Var(phi_k)); bounded individual variances give O(r/sqrt(M)), with possible additional rank dependence in the stability factor. Initial empirical coefficients do not imply exact spectral moments of the transported particles. These numerical checks do not constitute an independent proof review.']
    lines += ['', REPRODUCTION_NOTES]
    content=re.sub(r'(?m)^(#{1,6} [^\n]+)\n(?=\S)',r'\1\n\n','\n'.join(lines)+'\n')
    RESULTS_PATH.write_text(content,encoding='utf-8')
    print(f'Updated {RESULTS_PATH} ({len(lines)} lines).')
    return RESULTS_PATH


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Verify saved clouds and reproduce all 180 matched OU runs; no writes.')
    parser.add_argument('--tables',action='store_true',help='Export manuscript CSV tables from the retained results.')
    args=parser.parse_args()
    if args.check:verify_saved_results()
    elif args.tables:write_tables()
    else:write_report()
