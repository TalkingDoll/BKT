"""Recompute descriptive endpoint diagnostics from saved comparison arrays.

No training data, fitted models, samplers or numerical trajectories are loaded
or rerun. Run with NumPy available from the project root or any directory.
"""
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/data_comparison"


def main():
    rows = json.loads((OUT / "runs.json").read_text(encoding="utf-8"))
    config = json.loads((OUT / "config.json").read_text(encoding="utf-8"))
    box = np.asarray(config["box"])

    def diagnose(x):
        at = (x == box[:, 0]) | (x == box[:, 1])
        return dict(particles=len(x), mean=x.mean(axis=0).tolist(),
                    standard_deviation=x.std(axis=0, ddof=1).tolist(),
                    covariance=np.cov(x, rowvar=False, ddof=1).tolist(),
                    minimum=x.min(axis=0).tolist(), maximum=x.max(axis=0).tolist(),
                    left_mass=float(np.mean(x[:, 0] < 0)),
                    tail_abs_x1_gt_1p8=float(np.mean(abs(x[:, 0]) > 1.8)),
                    tail_abs_x2_gt_2=float(np.mean(abs(x[:, 1]) > 2.)),
                    boundary_atom_fraction=float(np.mean(at.any(axis=1))),
                    boundary_atom_fraction_per_coordinate=at.mean(axis=0).tolist())

    def moments(values):
        x = np.asarray(values, float)
        return dict(mean=x.mean(axis=0).tolist(),
                    std=x.std(axis=0, ddof=1).tolist() if len(x) > 1 else None,
                    n=len(x))

    targets, individual, groups = [], [], []
    for beta in config["betas"]:
        with np.load(OUT / f"evaluation_beta{beta:g}.npz") as evaluation:
            target = evaluation["target"]
            directions = evaluation["directions"]
            target_sorted = np.sort(target @ directions.T, axis=0)
            targets.append(dict(beta=beta, **diagnose(target)))
        for method in config["methods"]:
            available = [r for r in rows if r["beta"] == beta and r["method"] == method
                         and r.get("status") == "ok"]
            clouds, records = [], []
            for row in available:
                with np.load(OUT / row["endpoint_file"]) as data:
                    x = data["final"]
                clouds.append(x)
                squared_error = (np.sort(x @ directions.T, axis=0)-target_sorted)**2
                q = (np.arange(len(x))+.5)/len(x)
                outer = (q < .025) | (q > .975)
                contribution = float(squared_error[outer].sum()/squared_error.size)
                total = float(squared_error.mean())
                record = dict(beta=beta, seed=row["seed"], method=method, **diagnose(x),
                              sw2_squared=total,
                              outer_5pct_projection_quantiles_sw2_squared_contribution=contribution,
                              outer_5pct_projection_quantiles_fraction_of_sw2_squared=contribution/total if total else 0.,
                              saved_endpoint_file=row["endpoint_file"])
                individual.append(record)
                records.append(record)
            if records:
                metrics = ["mean", "standard_deviation", "left_mass", "tail_abs_x1_gt_1p8",
                           "tail_abs_x2_gt_2", "boundary_atom_fraction",
                           "outer_5pct_projection_quantiles_fraction_of_sw2_squared"]
                groups.append(dict(beta=beta, method=method, n_repeats=len(records),
                                   pooled=diagnose(np.concatenate(clouds)),
                                   per_replicate_statistics={key: moments([r[key] for r in records]) for key in metrics}))
    result = dict(
        created_utc=datetime.now(timezone.utc).isoformat(),
        status="complete" if len(individual) == len(config["betas"])*len(config["source_indices"])*len(config["methods"]) else "partial",
        saved_successful_endpoint_count=len(individual),
        expected_method_runs=len(config["betas"])*len(config["source_indices"])*len(config["methods"]),
        scope="Post-hoc descriptive calculations from saved endpoint and evaluation arrays only; no fitting, trajectory simulation, training-data loading or parameter selection.",
        definitions=dict(
            boundary_atom="A coordinate equals its finite box bound exactly.",
            tail_regions="Exploratory fixed descriptive regions |x1|>1.8 and |x2|>2; not additional success criteria.",
            projection_tail="The outer 5 percent of empirical quantile intervals (2.5 percent in each tail) across the existing 64 directions; weighted contribution sums to the reported total squared SW2 with the central contribution.",
            group_statistics="Mean and sample SD across available equal-size replicates; pooled moments are separately labeled.",
            caveat="Tail and boundary observations are associations in these numerical outputs and do not isolate finite-lag regression, dictionary approximation, integration error or boundary treatment as a cause."),
        targets=targets, groups=groups, runs=individual)
    (OUT / "endpoint_diagnostics.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(f"Saved {len(individual)} endpoint diagnostics; no samplers were rerun.")


if __name__ == "__main__":
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        main()
