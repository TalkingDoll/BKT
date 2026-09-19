# Backward Kolmogorov Transport (BKT)

Code, experiment configurations, figures, and numerical results for
**Backward Kolmogorov Transport: Sampling Invariant Laws of Reversible
Diffusions from Trajectory Data**.

The experiments cover Ornstein-Uhlenbeck processes, double-well and multi-well
systems, separable high-dimensional products, and the dihedral marginal of
alanine dipeptide. The notebook contains the numerical definitions;
supplementary scripts reproduce individual studies and their figures.

## Repository contents

| Path | Contents |
|---|---|
| [BKT_experiments.ipynb](BKT_experiments.ipynb) | Main experiment notebook |
| [supplementary/](supplementary/) | Runners, plotting scripts, diagnostics, and runnable configurations |
| [configs/retained/](configs/retained/) | Small configuration snapshots extracted from the local experiment archives |
| [outputs/figures/](outputs/figures/) | All 11 retained figure PDFs |
| [Experiment report](outputs/all_experiment_results_and_assessment.md) | Results, interpretation, and detailed reproduction commands |
| [Per-realisation JSON](outputs/revision_results.json) | Group-B numerical records, all outcomes, corrected products, and alanine follow-up diagnostics |
| [Data catalog](outputs/data/catalog.json) | Inventory, sizes, and SHA-256 hashes for local archived data |

## Environment

Use Python 3.11. Install the recorded numerical dependencies from the project
root:

```sh
python -m pip install -r requirements.txt
```

Open `BKT_experiments.ipynb` with a Jupyter-compatible environment using the
same Python environment. Run the notebook from this project directory.
Scripts locate the project root from their own location; saved project paths
are relative to that root, so the folder can be moved or renamed.

## Local experiment data

The four experiment archives, with current sizes recorded in the data catalog, are intentionally
excluded from Git. They remain on the local machine. This repository publishes
the code, configurations, report, per-realisation JSON, and figures; a fresh clone does **not** contain
the retained datasets, cached eigenpairs, or particle trajectories.

To use workflows that read the retained results, copy the local archives into:

```text
outputs/data/
  alanine.zip
  double_well.zip
  ou.zip
  shared.zip
  catalog.json       # already included in Git
```

The report's `data/*.zip` links refer to these local files. They become usable
after restoring the archives; the archives are not downloadable from this
repository. Configuration snapshots in `configs/retained/` are for inspection
and do not replace the archived numerical data. Their source members and
checksums are listed in [manifest.json](configs/retained/manifest.json). Snapshot
files use UTF-8/LF serialization for stable Git checksums; the manifest also
records the original archive-member byte hashes and checks that the parsed
configurations agree.

With the archives restored, validate them without running experiments:

```sh
python -B supplementary/experiment_store.py verify
```

The notebook and synthetic runners temporarily unpack the archives and repack
them when their session closes. Run one data session at a time. The ignore
rules also exclude unpacked generated outputs and numerical arrays, so these
local working files are not accidentally committed.

## Reproduction

After restoring the local archives and installing dependencies, regenerate the
report from retained results:

```sh
python -B supplementary/manuscript_results.py
```

See the [experiment report](outputs/all_experiment_results_and_assessment.md)
for the synthetic and molecular experiment commands, runtime requirements,
configuration choices, and verification scope. Some commands run substantial
numerical computations; the report distinguishes plotting, verification, and
reproduction.

The runnable synthetic configurations are under `supplementary/`. Alanine
settings and the other archived configuration snapshots are also published in
`configs/retained/`.

The fixed B1--B4 revision is run by `supplementary/revision_queue.py`, followed
by `revision_verify.py`, `revision_publish.py`, and `revision_figures.py`. The queue resumes prescribed
realisations without outcome-based seed selection. Product indices are
0--5 and 7--10: source seed 1+s skips target seed 7. It includes independent 10D
mode selection, ten-repetition summaries, alanine estimation checks, and
per-particle safeguard diagnostics. The report contains the results and any
reproduction discrepancies; B5 is not included.

The fixed group-B follow-up is reproduced with:

```sh
python -u -B supplementary/revision_followup.py run
python -B supplementary/revision_verify.py
python -B supplementary/revision_publish.py
python -B supplementary/revision_figures.py --products-only
```

The follow-up reuses the unchanged nine product realisations and runs index 10
only. It diagnoses all three archived alanine spectra and reruns the three
distinct integrations fitted on trajectory 3 once with both resource budgets
multiplied by five. Each path is evaluated against both other trajectories.
All results, including incomplete paths and the explicitly excluded historical
product index 6, are labelled in the same report and public JSON. The optional
confined multiwell study is not run. Saved follow-up runs are resumed without
repeating their integrations.

## Figures

- [1D Ornstein-Uhlenbeck](outputs/figures/fig_ou.pdf)
- [10D Ornstein-Uhlenbeck](outputs/figures/fig_ou10.pdf)
- [10D OU marginals](outputs/figures/fig_ou10_marginals.pdf)
- [Matched OU paths](outputs/figures/fig_ou_path_comparison.pdf)
- [Double-well rank comparison](outputs/figures/fig_admissible_source_ranks.pdf)
- [Coefficient regimes](outputs/figures/fig_admissible_source_coefficients.pdf)
- [Equal-data comparison](outputs/figures/fig_data_comparison.pdf)
- [10D product](outputs/figures/fig_hd10_dictionaries.pdf)
- [50D product](outputs/figures/fig_hd50_dictionaries.pdf)
- [Alanine distribution](outputs/figures/fig_alanine.pdf)
- [Alanine convergence](outputs/figures/fig_alanine_convergence.pdf)

## Data attribution

The molecular experiment uses public alanine dipeptide trajectories documented
by [mdshare](https://markovmodel.github.io/mdshare/ALA2/). Dataset attribution
and licensing information are retained in the experiment report; the original
dataset URL is recorded in the alanine configuration snapshot.
