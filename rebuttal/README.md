# Experiments added during the ICLR 2027 discussion

`BKT_rebuttal_experiments.ipynb` contains the code of the experiments added in the revision (LAWGD with the same eigenpairs, a coupled three-dimensional double well with jointly estimated eigenpairs, a barrier-height scan with trajectory data and with reweighted data from a biased simulation, two well-separated Gaussian mixtures, the eigenvalue-only experiment, and the sensitivity to the dictionary), the result files embedded as data, and the tables and figures computed from them. Running the notebook from the top writes the library and the scripts next to it, writes the embedded results to `results/`, and recomputes every table and figure in a few seconds. Each experiment script is then run from a terminal in the same folder, as described in the notebook.

| Path | Contents |
|---|---|
| `results/` | Result files of the runs reported in the paper (also embedded in the notebook) |
| `figures/` | Figures 8 and 9 of the paper and the figure of the three-dimensional example |
| `rerun_check/` | Scripts and report of a rerun of all scripts from scratch, compared with the files in `results/` |
