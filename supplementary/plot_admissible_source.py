"""Plot saved admissible-source experiments without running any simulations.

Run from the project root:
    uv run --with numpy --with matplotlib python supplementary/plot_admissible_source.py

Input: outputs/admissible_source/summary.json. Per-run roles are filtered before
aggregation, so a rank-64 run reused in several protocols is counted once in
each appropriate protocol. Figures follow the notebook's presentation style.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.container import ErrorbarContainer
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
METHODS = ("FD", "RBF", "Legendre")
COLORS = {"FD": "#0072B2", "RBF": "#D55E00", "Legendre": "#009E73"}
REGIME_COLORS = {"I": "#D55E00", "S": "#009E73"}
REGIME_LABELS = {"I": "Independent coefficients", "S": "Same-sample coefficients"}
MARKERS = {"FD": "o", "RBF": "s", "Legendre": "^"}
REFERENCE_COLOR = "#525252"
LEGEND_GAP_PT = 32
LEGEND_BOTTOM_MARGIN_PT = 18
EVENT_FIELDS = ("density_floor_events", "nonpositive_density_events", "speed_cap_events",
                "projected_coordinate_events", "projected_particle_events", "stage_particle_events",
                "unique_affected_particles", "initial_outside")


from figure_style import configure_style


def moments(values):
    values = np.asarray(list(values), dtype=float)
    if not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("A saved metric group is empty or contains non-finite values")
    return {"mean": float(values.mean()), "std": float(values.std(ddof=1)) if len(values) > 1 else None,
            "n": len(values)}


def rows_for(runs, role):
    return [row for row in runs if role in row.get("roles", [])]


def group_rows(rows, keys):
    groups = {}
    for row in rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    return groups


def load_data(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("metadata", {}).get("complete") is not True:
        raise ValueError("The full numerical run must be marked complete before final figures are generated")
    runs = data["runs"]
    if not isinstance(runs, list) or not runs:
        raise ValueError("summary.json must contain the complete per-run list")
    for row in runs:
        if not np.isfinite(float(row["sw2"])) or float(row["sw2"]) < 0:
            raise ValueError("Invalid saved SW2; failed runs must be resolved or explicitly reported")
    main = group_rows(rows_for(runs, "main"), ("beta", "method"))
    betas = sorted({float(beta) for beta, _ in main})
    if len(betas) != 4 or any((beta, method) not in main for beta in betas for method in METHODS):
        raise ValueError("Expected all three main methods at each of four coupling strengths")
    references = {float(row["beta"]): row for row in data["references"]}
    if any(beta not in references for beta in betas):
        raise ValueError("A coupling case is missing its matched reference summary")
    fd_label = data.get("metadata", {}).get("fd_label")
    if not fd_label:
        config = data.get("config", {})
        fd_n = next((config[key] for key in ("fd_N", "fd_grid_N", "fd_n", "fd_grid") if key in config), None)
        if fd_n is None:
            raise ValueError("Record metadata.fd_label or the FD grid size; no grid size is guessed")
        fd_label = f"FD-{int(fd_n)}"
    labels = {"FD": fd_label, "RBF": "Koopman (RBF)", "Legendre": "Koopman (Legendre)"}
    return data, runs, main, betas, references, labels


def content_bottom(fig, axes, renderer):
    boxes = [ax.get_tightbbox(renderer) for ax in np.asarray(axes).ravel() if ax.get_visible()]
    boxes += [text.get_window_extent(renderer) for text in fig.texts if text.get_visible() and text.get_text()]
    return min(box.y0 for box in boxes if box is not None)


def shared_legend(fig, axes, order, ncol=None):
    entries = {}
    for ax in np.asarray(axes).ravel():
        for handle, label in zip(*ax.get_legend_handles_labels()):
            entries.setdefault(label, handle)
    legend = fig.legend([entries[label] for label in order], order,
                        loc="upper center", bbox_to_anchor=(.5, 0), bbox_transform=fig.transFigure,
                        ncol=ncol or len(order), frameon=False, borderpad=0, borderaxespad=0,
                        handlelength=2.1, columnspacing=1.2, handletextpad=.6)
    for _ in range(5):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        needed = ((LEGEND_GAP_PT + LEGEND_BOTTOM_MARGIN_PT) * fig.dpi / 72
                  + legend.get_window_extent(renderer).height)
        shift = (needed - content_bottom(fig, axes, renderer)) / fig.bbox.height
        if abs(shift) < 1e-6:
            break
        fig.subplots_adjust(bottom=fig.subplotpars.bottom + shift)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    top = (content_bottom(fig, axes, renderer) - LEGEND_GAP_PT * fig.dpi / 72) / fig.bbox.height
    legend.set_bbox_to_anchor((.5, top), transform=fig.transFigure)
    return legend


def finish_axis(ax, log_y=False):
    if log_y:
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(axis="y", which="major", color="#E0E0E0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(which="major", length=6, width=1)
    ax.tick_params(axis="x", labelrotation=0)


def save_figure(fig, axes, legend, name, output_dir, details):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    legend_box = legend.get_window_extent(renderer)
    gap = (content_bottom(fig, axes, renderer) - legend_box.y1) * 72 / fig.dpi
    margin = legend_box.y0 * 72 / fig.dpi
    boxes = [ax.get_tightbbox(renderer) for ax in np.asarray(axes).ravel()] + [legend_box]
    boxes += [text.get_window_extent(renderer) for text in fig.texts if text.get_visible() and text.get_text()]
    inside = all(box.x0 >= -1 and box.y0 >= -1 and box.x1 <= fig.bbox.width + 1
                 and box.y1 <= fig.bbox.height + 1 for box in boxes if box is not None)
    bars_inside = True
    for ax in np.asarray(axes).ravel():
        low, high = ax.get_ylim()
        for container in ax.containers:
            if isinstance(container, ErrorbarContainer):
                for collection in container.lines[2]:
                    for segment in collection.get_segments():
                        bars_inside = bars_inside and bool(np.all((segment[:, 1] >= low) & (segment[:, 1] <= high)))
    if not inside or not bars_inside or abs(gap - LEGEND_GAP_PT) > .1 or abs(margin - LEGEND_BOTTOM_MARGIN_PT) > .1:
        raise RuntimeError(f"Layout check failed: {name}, inside={inside}, bars={bars_inside}, gap={gap}, margin={margin}")
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{name}.pdf")
    result = {"figure": name, "size_inches": list(fig.get_size_inches()), "legend_gap_pt": gap,
              "legend_bottom_margin_pt": margin, "all_content_inside_canvas": inside,
              "all_error_bars_inside_axes": bars_inside, "standard_deviation_bars_truncated": False,
              "output_format": "pdf", **details}
    plt.close(fig)
    return result


def rank_figure(runs, betas, references, labels, output_dir):
    configure_style('fig_admissible_source_ranks', 20)
    groups = group_rows(rows_for(runs, "rank_scan"), ("beta", "method", "r_requested"))
    fig, axes = plt.subplots(1, 4, figsize=(20, 7.2), sharex=True, sharey=True)
    fig.suptitle("Spectral rank and double-well sampling", y=.98)
    fig.subplots_adjust(left=.11, right=.98, top=.73, bottom=.30, wspace=.22)
    all_ranks = sorted({int(key[2]) for key in groups})
    low, high = np.inf, 0.0
    counts = set()
    for ax, beta in zip(axes.ravel(), betas):
        for method in METHODS:
            ranks = sorted(int(key[2]) for key in groups if key[:2] == (beta, method))
            if not ranks:
                raise ValueError(f"Missing rank scan for beta={beta}, method={method}")
            stats = [moments(row["sw2"] for row in groups[(beta, method, rank)]) for rank in ranks]
            means = np.array([item["mean"] for item in stats])
            stds = np.array([item["std"] or 0.0 for item in stats])
            counts.update(item["n"] for item in stats)
            if any(item["n"] > 1 for item in stats):
                ax.errorbar(ranks, means, yerr=stds, fmt=MARKERS[method] + "-", color=COLORS[method],
                            capsize=4, label=labels[method], zorder=3)
            else:
                ax.plot(ranks, means, MARKERS[method] + "-", color=COLORS[method], label=labels[method], zorder=3)
            low, high = min(low, float(np.min(means - stds))), max(high, float(np.max(means + stds)))
        reference = references[beta]
        lower, upper = reference["mean"] - reference["std"], reference["mean"] + reference["std"]
        low, high = min(low, lower), max(high, upper)
        ax.axhspan(lower, upper, color=REFERENCE_COLOR, alpha=.10, linewidth=0)
        ax.axhline(reference["mean"], color=REFERENCE_COLOR, linestyle=":", label="Target reference")
        ax.set_title(rf"$\beta={beta:g}$")
        ax.set_xticks([8, 64, 128])
        ax.set_xticks([16, 32, 96], minor=True)
        ax.set_xlim(min(all_ranks) - 4, max(all_ranks) + 4)
        finish_axis(ax, log_y=True)
    if low <= 0:
        raise ValueError("Rank-scan log axis requires positive full displayed intervals")
    axes[0].set_ylim(low / 1.2, high * 1.2)
    axes[0].set_ylabel(r"Sliced $W_2$")
    for ax in axes:
        ax.set_xlabel(r"Modes, $r$")
    legend = shared_legend(fig, axes, [labels[method] for method in METHODS] + ["Target reference"])
    return save_figure(fig, axes, legend, "fig_admissible_source_ranks", output_dir,
                       {"y_scale": "logarithmic", "repeat_counts_per_rank_group": sorted(counts),
                        "single_seed_groups_have_no_sd_bars": True, "shared_y_limits": list(axes[0].get_ylim())})


def regime_statistics(runs, betas):
    rows = rows_for(runs, "coefficient_comparison")
    groups = group_rows(rows, ("beta", "regime"))
    result = {}
    for beta in betas:
        by_regime = {}
        for regime in ("I", "S"):
            group = groups[(beta, regime)]
            if any(row["method"] != "RBF" for row in group):
                raise ValueError("The coefficient comparison is defined for the RBF method")
            by_seed = {row["seed"]: row for row in group}
            if len(by_seed) != len(group):
                raise ValueError("Duplicate protocol rows in a paired coefficient group")
            by_regime[regime] = by_seed
        if set(by_regime["I"]) != set(by_regime["S"]):
            raise ValueError("Independent and same-sample comparisons require matched seeds")
        seeds = sorted(by_regime["I"])
        for seed in seeds:
            left, right = by_regime["I"][seed], by_regime["S"][seed]
            if left["source_seed"] != right["source_seed"]:
                raise ValueError("The paired regimes must share the same transported source cloud")
        result[beta] = {regime: moments(by_regime[regime][seed]["sw2"] for seed in seeds) for regime in ("I", "S")}
        result[beta]["I_minus_S"] = moments(by_regime["I"][seed]["sw2"] - by_regime["S"][seed]["sw2"] for seed in seeds)
    return result


def regime_figure(stats, betas, references, output_dir):
    configure_style('fig_admissible_source_coefficients', 17)
    fig, axes = plt.subplots(1, 2, figsize=(17, 7))
    fig.suptitle("Independent and same-sample coefficient estimates", y=.97)
    fig.subplots_adjust(left=.11, right=.98, top=.76, bottom=.28, wspace=.30)
    left_low, left_high = 0.0, 0.0
    for regime, marker in (("I", "s"), ("S", "^")):
        means = np.array([stats[beta][regime]["mean"] for beta in betas])
        stds = np.array([stats[beta][regime]["std"] or 0.0 for beta in betas])
        axes[0].errorbar(betas, means, yerr=stds, fmt=marker + "-", color=REGIME_COLORS[regime],
                         capsize=4, label=REGIME_LABELS[regime])
        left_low, left_high = min(left_low, float(np.min(means - stds))), max(left_high, float(np.max(means + stds)))
    means = np.array([references[beta]["mean"] for beta in betas])
    stds = np.array([references[beta]["std"] for beta in betas])
    axes[0].errorbar(betas, means, yerr=stds, fmt="D:", color=REFERENCE_COLOR, capsize=4, label="Target reference")
    left_low, left_high = min(left_low, float(np.min(means - stds))), max(left_high, float(np.max(means + stds)))
    means = np.array([stats[beta]["I_minus_S"]["mean"] for beta in betas])
    stds = np.array([stats[beta]["I_minus_S"]["std"] or 0.0 for beta in betas])
    axes[1].errorbar(betas, means, yerr=stds, fmt="o-", color=COLORS["FD"], capsize=4)
    axes[1].axhline(0, color=REFERENCE_COLOR, linestyle=":")
    right_low, right_high = min(0, float(np.min(means - stds))), max(0, float(np.max(means + stds)))
    left_span, right_span = max(left_high - left_low, 1e-8), max(right_high - right_low, 1e-8)
    axes[0].set_ylim(left_low - .04 * left_span, left_high + .08 * left_span)
    axes[1].set_ylim(right_low - .1 * right_span, right_high + .1 * right_span)
    axes[0].set_title("Koopman (RBF) sampling error")
    axes[1].set_title(r"Paired difference, $I-S$")
    axes[0].set_ylabel(r"Sliced $W_2$")
    for ax in axes:
        ax.set_xlabel(r"Coupling $\beta$")
        ax.set_xticks(betas, [f"{beta:g}" for beta in betas])
        ax.set_xlim(min(betas) - .05, max(betas) + .05)
        finish_axis(ax)
    legend = shared_legend(fig, axes, [REGIME_LABELS["I"], REGIME_LABELS["S"], "Target reference"])
    return save_figure(fig, axes, legend, "fig_admissible_source_coefficients", output_dir,
                       {"y_scale": "linear", "paired_difference": "Independent minus same-sample SW2",
                        "paired_n_by_beta": {str(beta): stats[beta]["I_minus_S"]["n"] for beta in betas}})






def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export_tables(data, runs, main, stats, betas, references, labels, output_dir):
    compact = []
    for method in METHODS:
        record = {"method": method, "label": labels[method]}
        for beta in betas:
            item = moments(row["sw2"] for row in main[(beta, method)])
            prefix = f"beta_{beta:g}"
            record.update({prefix + "_" + key: item[key] for key in ("mean", "std", "n")})
        compact.append(record)
    record = {"method": "reference", "label": "Target reference"}
    for beta in betas:
        reference = references[beta]
        prefix = f"beta_{beta:g}"
        record.update({prefix + "_mean": reference["mean"], prefix + "_std": reference["std"],
                       prefix + "_n": reference.get("n", reference.get("repetitions", 10))})
    compact.append(record)
    write_csv(output_dir / "main_results_table.csv", compact)
    paired_rows = []
    for beta in betas:
        record = {"beta": beta, "n": stats[beta]["I"]["n"]}
        for regime in ("I", "S", "I_minus_S"):
            record[regime + "_sw2_mean"], record[regime + "_sw2_std"] = stats[beta][regime]["mean"], stats[beta][regime]["std"]
        paired_rows.append(record)
    write_csv(output_dir / "coefficient_comparison_table.csv", paired_rows)
    event_rows = [row for row in runs if "main" in row.get("roles", []) or "coefficient_comparison" in row.get("roles", [])]
    event_groups = group_rows(event_rows, ("beta", "method", "regime"))
    event_records = []
    for key, group in sorted(event_groups.items()):
        beta, method, regime = key
        record = {"beta": beta, "method": method, "regime": regime, "n": len(group)}
        for event in EVENT_FIELDS:
            item = moments(row["events"][event] for row in group)
            record[event + "_mean"], record[event + "_std"] = item["mean"], item["std"]
        event_records.append(record)
    write_csv(output_dir / "event_diagnostics_table.csv", event_records)
    rank_records = []
    for key, group in sorted(group_rows(rows_for(runs, "rank_scan"), ("beta", "method", "r_requested")).items()):
        beta, method, rank = key
        item = moments(row["sw2"] for row in group)
        rank_records.append({"beta": beta, "method": method, "r_requested": rank,
                             "r_used_values": ",".join(str(int(value)) for value in sorted({row["r_used"] for row in group})),
                             "sw2_mean": item["mean"], "sw2_std": item["std"], "n": item["n"]})
    write_csv(output_dir / "rank_scan_table.csv", rank_records)
    sample_groups = group_rows(rows_for(runs, "sample_size"), ("beta", "n_pairs"))
    sample_budgets = sorted({key[1] for key in sample_groups})
    sample_records = []
    for beta in betas:
        for budget in sample_budgets:
            group = sample_groups[(beta, budget)]
            if any(row["method"] != "RBF" or row["regime"] != "S" for row in group):
                raise ValueError("The source-budget table is defined for same-sample RBF")
            item = moments(row["sw2"] for row in group)
            sample_records.append({"beta": beta, "n_pairs": budget, "n": item["n"],
                                   "sw2_mean": item["mean"], "sw2_std": item["std"]})
    if sample_records:
        write_csv(output_dir / "sample_size_table.csv", sample_records)
    step_groups = group_rows(rows_for(runs, "step_check"), ("beta", "method", "regime", "dt"))
    step_records = []
    for beta, method, regime in sorted({key[:3] for key in step_groups}):
        steps = sorted(key[3] for key in step_groups if key[:3] == (beta, method, regime))
        if len(steps) != 2:
            raise ValueError("The prescribed step check requires exactly two time steps")
        fine, coarse = steps
        fine_rows = {row["seed"]: row for row in step_groups[(beta, method, regime, fine)]}
        coarse_rows = {row["seed"]: row for row in step_groups[(beta, method, regime, coarse)]}
        if set(fine_rows) != set(coarse_rows):
            raise ValueError("The step check requires matched source seeds")
        seeds = sorted(fine_rows)
        for seed in seeds:
            if fine_rows[seed]["source_seed"] != coarse_rows[seed]["source_seed"]:
                raise ValueError("The paired step sizes must share the same source cloud")
        fine_stats = moments(fine_rows[seed]["sw2"] for seed in seeds)
        coarse_stats = moments(coarse_rows[seed]["sw2"] for seed in seeds)
        difference = moments(fine_rows[seed]["sw2"] - coarse_rows[seed]["sw2"] for seed in seeds)
        step_records.append({"beta": beta, "method": method, "regime": regime, "n": len(seeds),
                             "coarse_dt": coarse, "fine_dt": fine,
                             "coarse_sw2_mean": coarse_stats["mean"], "coarse_sw2_std": coarse_stats["std"],
                             "fine_sw2_mean": fine_stats["mean"], "fine_sw2_std": fine_stats["std"],
                             "fine_minus_coarse_mean": difference["mean"], "fine_minus_coarse_std": difference["std"]})
    if step_records:
        write_csv(output_dir / "step_check_table.csv", step_records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "outputs" / "admissible_source")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "outputs" / "figures")
    args = parser.parse_args()
    data, runs, main_groups, betas, references, labels = load_data(args.data_dir / "summary.json")
    stats = regime_statistics(runs, betas)
    configure_style()
    checks = [rank_figure(runs, betas, references, labels, args.figure_dir),
              regime_figure(stats, betas, references, args.figure_dir)]
    export_tables(data, runs, main_groups, stats, betas, references, labels, args.data_dir)
    print(json.dumps({"figures": checks, "main_table_rows": 4, "coefficient_table_rows": len(betas)}, indent=2))


if __name__ == "__main__":
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        main()
