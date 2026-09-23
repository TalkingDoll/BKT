"""Audit existing source/domain code without running or modifying experiments.

Run with the same NumPy environment as ou_path_validation.py. All conclusions
about global integrability below are analytic, not inferred from grid maxima.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from manuscript_results import write_report


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "ou_path_validation"


def notebook_definitions():
    notebook_path = ROOT / "BKT_experiments.ipynb"
    data = notebook_path.read_bytes()
    notebook = json.loads(data)
    requested = {"Potential", "bump_sampler", "source_A"}
    nodes = []
    locations = {}
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        for node in ast.parse(source).body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in requested:
                nodes.append(node)
                locations[node.name] = {
                    "cell_index_zero_based": index,
                    "source": ast.get_source_segment(source, node),
                }
    assert set(locations) == requested
    namespace = {"np": np}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(notebook_path), "exec"), namespace)
    return namespace, locations, hashlib.sha256(data).hexdigest()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    namespace, locations, notebook_hash = notebook_definitions()
    Potential = namespace["Potential"]
    source_A = namespace["source_A"]
    rows = []
    for beta in (0.0, 0.25, 0.5, 1.0):
        potential = Potential("A", d=2, beta=beta)
        assert not potential.full_plane
        assert np.array_equal(potential.box, [[-2.8, 2.8], [-2.5, 2.5]])
        trial = np.array([[0.0, 3.0], [0.0, -3.0]])
        assert np.array_equal(potential.reflect(trial), [[0.0, 2.5], [0.0, -2.5]])
        for source_seed in range(500, 505):
            initial = source_A(potential, 2000, np.random.default_rng(source_seed))
            outside = np.any((initial < potential.box[:, 0]) | (initial > potential.box[:, 1]), axis=1)
            rows.append({
                "beta": beta,
                "source_seed": source_seed,
                "particles": len(initial),
                "initial_outside_box_count": int(outside.sum()),
                "initial_outside_box_fraction": float(outside.mean()),
                "max_abs_x2": float(np.max(np.abs(initial[:, 1]))),
                "full_space_ratio_L2": bool(beta < 2.0),
                "full_space_ratio_Linfinity": bool(beta == 0.0),
            })
    # If X2 ~ N(0,1/2), P(|X2| > 2.5) = erfc(2.5).
    tail_probability = math.erfc(2.5)
    payload = {
        "classification": "source/domain audit; not a transport-error certificate",
        "notebook_sha256": notebook_hash,
        "definitions": locations,
        "intended_full_space_target": "pi_beta proportional to exp(-((x1^2-1)^2+x2^2+beta*(x2-x1)^2/2))",
        "source": {
            "x1_support": [0.4, 1.6],
            "x1_sampler": "4001-point inverse-CDF approximation to a cosine-squared bump",
            "x2_law": "N(0,1/2), neither conditioned nor clipped at initialization",
            "x2_tail_probability_outside_box": tail_probability,
            "expected_outside_count_M2000": 2000 * tail_probability,
        },
        "analytic_assumptions": {
            "full_space_ratio": "C_beta*f(x1)*exp((x1^2-1)^2+beta*(x2-x1)^2/2)",
            "Linfinity": "finite at beta=0; infinite for every beta>0",
            "L2": "finite for 0<=beta<2; infinite for beta>=2 for this bump",
            "narrower_gaussian_sufficient_condition": "variance tau^2 < 1/(2+beta), with bounded compactly supported x1 density",
            "modified_sources_run": False,
            "other_validity_region_conditions_verified": False,
        },
        "actual_code": {
            "A_box": [[-2.8, 2.8], [-2.5, 2.5]],
            "A_projection": "coordinatewise np.clip in diffusion steps, RK stages and final RK update",
            "reflect_box_flag": "False, but unused by reflect(); it does not disable clipping",
            "A_training_and_target_samples": "finite-burn projected Euler chain; not exact samples of full-space or continuous boxed Gibbs law",
            "A_FD": "finite-box Neumann discretization",
            "unprojected_source_vs_box_target": "not absolutely continuous: positive source mass outside the box",
            "projected_source_vs_box_target": "projecting tails creates singular boundary-face mass (atoms in the clipped x2 marginal); not absolutely continuous with respect to a continuous boxed Gibbs law",
            "OU_position_projection_or_reflection": False,
            "OU_minus4_plus4": "diagnostic grid, not a transport constraint",
        },
        "rows": rows,
        "scope": "Existing particles, spectra, simulation results and notebook are unchanged. No new double-well sampling experiment is run.",
    }
    (OUTPUT / "source_assumptions.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (OUTPUT / "source_initial_tail_counts.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    update_report(payload)


def update_report(payload):
    write_report()


if __name__ == "__main__":
    from experiment_store import managed_outputs
    with managed_outputs("ou"):
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--from-saved", action="store_true", help="Update the central report using the existing audit JSON only")
        args = parser.parse_args()
        if args.from_saved:
            update_report(json.loads((OUTPUT / "source_assumptions.json").read_text(encoding="utf-8")))
        else:
            main()
