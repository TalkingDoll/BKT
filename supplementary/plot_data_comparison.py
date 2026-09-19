"""Create figures and compact tables from saved equal-data comparison results.

No numerical experiment runs here. From the project root:

    uv run --with numpy --with matplotlib python supplementary/plot_data_comparison.py

The required input is outputs/data_comparison/summary.json with rows containing
beta, method, label, n_repeats, sw2_mean, sw2_std, fit_seconds_mean,
sample_seconds_mean, total_seconds_mean, hit_count and hit_seconds_mean.
Corresponding timing *_std fields contain sample standard deviations.
The references array contains beta, mean and std. The optional config key
hit_threshold_description explains the threshold used for the timing diagnostic.
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
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter, MaxNLocator
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
METHODS = ("A", "B", "D")
COLORS = {"A": "#0072B2", "B": "#D55E00", "D": "#525252"}
MARKERS = {"A": "o", "B": "s", "D": "D"}
AXIS_LABELS = {"A": "BKT", "B": "Drift +\nLangevin", "D": "KDE\nflow"}
REFERENCE_COLOR = "#525252"
LEGEND_GAP_PT = 32
LEGEND_BOTTOM_MARGIN_PT = 18


from figure_style import configure_style


def load_summary(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["rows"]
    betas = sorted({float(row["beta"]) for row in rows})
    if len(betas) != 2:
        raise ValueError("The approved comparison figure requires two coupling values")
    lookup = {(float(row["beta"]), str(row["method"])): row for row in rows}
    expected = len(METHODS) * len(betas)
    if len(rows) != expected or len(lookup) != expected or any((beta, method) not in lookup for beta in betas for method in METHODS):
        raise ValueError("Expected one summary row for each of three methods and two coupling values")
    references = {float(row["beta"]): row for row in data["references"]}
    labels = {}
    for method in METHODS:
        names = {str(lookup[(beta, method)]["label"]) for beta in betas}
        if len(names) != 1:
            raise ValueError(f"Inconsistent label for method {method}")
        labels[method] = names.pop()
    for row in rows:
        for key in ("sw2_mean", "sw2_std"):
            value = float(row[key])
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"Invalid saved {key}: {value}")
        if int(row["n_repeats"]) < 2:
            raise ValueError("Sample-standard-deviation summaries require at least two repeats")
    for beta in betas:
        for key in ("mean", "std"):
            value = float(references[beta][key])
            if not np.isfinite(value) or value < 0:
                raise ValueError("Invalid target-reference summary")
    return data, betas, lookup, references, labels


def content_bottom(fig, axes, renderer):
    boxes = [ax.get_tightbbox(renderer) for ax in np.asarray(axes).ravel()]
    boxes.extend(text.get_window_extent(renderer) for text in fig.texts
                 if text.get_visible() and text.get_text())
    return min(box.y0 for box in boxes if box is not None)


def shared_legend(fig, axes, labels):
    entries = {}
    for ax in np.asarray(axes).ravel():
        for handle, label in zip(*ax.get_legend_handles_labels()):
            entries.setdefault(label, handle)
    order = [labels[method] for method in METHODS] + ["Target reference"]
    legend = fig.legend([entries[label] for label in order], order,
                        loc="upper center", bbox_to_anchor=(.5, 0),
                        bbox_transform=fig.transFigure, ncol=4, frameon=False,
                        borderpad=0, borderaxespad=0, handlelength=2.1,
                        columnspacing=1.1, handletextpad=.6)
    for _ in range(5):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        needed = (LEGEND_GAP_PT + LEGEND_BOTTOM_MARGIN_PT) * fig.dpi / 72 + legend.get_window_extent(renderer).height
        shift = (needed - content_bottom(fig, axes, renderer)) / fig.bbox.height
        if abs(shift) < 1e-6:
            break
        fig.subplots_adjust(bottom=fig.subplotpars.bottom + shift)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    top = (content_bottom(fig, axes, renderer) - LEGEND_GAP_PT * fig.dpi / 72) / fig.bbox.height
    legend.set_bbox_to_anchor((.5, top), transform=fig.transFigure)
    return legend


def plot_comparison(betas, lookup, references, labels, figure_dir):
    configure_style('fig_data_comparison', 17)
    fig, axes = plt.subplots(1, 2, figsize=(17, 8.5), sharey=True)
    fig.suptitle("Data-driven source-to-target sampling", y=.97)
    fig.subplots_adjust(left=.11, right=.98, top=.76, bottom=.30, wspace=.26)
    upper = 0.0
    lower = np.inf
    for ax, beta in zip(axes, betas):
        reference = references[beta]
        mean, std = float(reference["mean"]), float(reference["std"])
        ax.axhspan(max(0, mean - std), mean + std, color=REFERENCE_COLOR, alpha=.10, linewidth=0)
        ax.axhline(mean, color=REFERENCE_COLOR, linestyle=":", label="Target reference", zorder=1)
        upper = max(upper, mean + std)
        lower = min(lower, mean - std)
        for position, method in enumerate(METHODS):
            row = lookup[(beta, method)]
            mean, std = float(row["sw2_mean"]), float(row["sw2_std"])
            ax.errorbar(position, mean, yerr=std, fmt=MARKERS[method],
                        color=COLORS[method], capsize=5, markersize=9,
                        label=labels[method], zorder=3)
            upper = max(upper, mean + std)
            lower = min(lower, mean - std)
        ax.set_title(rf"Coupling $\beta={beta:g}$")
        ax.set_xticks(range(len(METHODS)), [AXIS_LABELS[method] for method in METHODS])
        ax.tick_params(axis="x", labelrotation=0)
        ax.set_xlabel("Method")
        ax.set_xlim(-.45, len(METHODS) - .55)
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.grid(axis="y", which="major", color="#E0E0E0", linewidth=.8)
        ax.set_axisbelow(True)
        ax.tick_params(which="major", length=6, width=1)
    # Delay shared scaling until both panels and all SD intervals are present.
    logarithmic = lower > 0
    if logarithmic:
        axes[0].set_ylim(lower / 1.20, upper * 1.20)
    else:
        for ax in axes:
            ax.set_yscale('linear');ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        span=upper-lower
        axes[0].set_ylim(lower-.05*span,upper+.08*span)
    axes[0].set_ylabel(r"Sliced $W_2$ to the target")
    legend = shared_legend(fig, axes, labels)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    legend_box = legend.get_window_extent(renderer)
    gap = (content_bottom(fig, axes, renderer) - legend_box.y1) * 72 / fig.dpi
    margin = legend_box.y0 * 72 / fig.dpi
    bounds = [ax.get_tightbbox(renderer) for ax in axes] + [legend_box]
    bounds.extend(text.get_window_extent(renderer) for text in fig.texts
                  if text.get_visible() and text.get_text())
    inside = all(box.x0 >= -1 and box.y0 >= -1 and box.x1 <= fig.bbox.width + 1
                 and box.y1 <= fig.bbox.height + 1 for box in bounds if box is not None)
    bars_inside = True
    for ax in axes:
        low, high = ax.get_ylim()
        for container in ax.containers:
            if isinstance(container, ErrorbarContainer):
                for collection in container.lines[2]:
                    for segment in collection.get_segments():
                        bars_inside = bars_inside and bool(np.all((segment[:, 1] >= low) & (segment[:, 1] <= high)))
    if not inside or not bars_inside or abs(gap - LEGEND_GAP_PT) > .1 or abs(margin - LEGEND_BOTTOM_MARGIN_PT) > .1:
        raise RuntimeError(f"Figure layout needs adjustment: inside={inside}, bars={bars_inside}, gap={gap}, margin={margin}")
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_dir / "fig_data_comparison.pdf")
    result = {"figure": "fig_data_comparison", "size_inches": list(fig.get_size_inches()),
              "legend_gap_pt": gap, "legend_bottom_margin_pt": margin,
              "all_content_inside_canvas": inside, "all_error_bars_inside_axes": bars_inside,
              "methods_displayed": [labels[method] for method in METHODS],
              "standard_deviation_bars_truncated": False, "shared_y_limits": list(axes[0].get_ylim()),
              "y_scale": ("logarithmic" if logarithmic else "linear")+"; full mean +/- SD intervals unchanged",
              "output_format": "pdf"}
    plt.close(fig)
    return result


def number(value, digits=4):
    if value is None:
        return "n/a"
    value = float(value)
    if digits == 3 and value != 0 and abs(value) < .001:
        return f"{value:.2e}"
    return f"{value:.{digits}f}"


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def time_interval(row, prefix):
    mean = row.get(prefix + "_mean")
    std = row.get(prefix + "_std")
    if mean is None:
        return "n/a"
    return number(mean, 3) + " +/- " + number(std, 3)


def write_tables(data, betas, lookup, references, labels, output_dir):
    """Write numerical tables for the supplied saved results, without simulations."""
    compact_rows = []
    for method in METHODS:
        record = {"method": method, "label": labels[method]}
        for beta in betas:
            row = lookup[(beta, method)]
            prefix = f"beta_{beta:g}"
            record[prefix + "_sw2_mean"] = row["sw2_mean"]
            record[prefix + "_sw2_std"] = row["sw2_std"]
            record[prefix + "_n_repeats"] = row["n_repeats"]
        compact_rows.append(record)
    write_csv(output_dir / "comparison_table.csv", compact_rows)
    costs = []
    for beta in betas:
        for method in METHODS:
            row = lookup[(beta, method)]
            cost = {"beta": beta, "method": method, "label": labels[method], "n_repeats": row["n_repeats"]}
            for key in ("fit_seconds_mean", "fit_seconds_std", "sample_seconds_mean", "sample_seconds_std",
                        "total_seconds_mean", "total_seconds_std", "hit_count", "hit_seconds_mean", "hit_seconds_std"):
                cost[key] = row.get(key)
            costs.append(cost)
    write_csv(output_dir / "cost_table.csv", costs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "outputs" / "data_comparison")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "outputs" / "figures")
    args = parser.parse_args()
    data, betas, lookup, references, labels = load_summary(args.data_dir / "summary.json")
    layout = plot_comparison(betas, lookup, references, labels, args.figure_dir)
    write_tables(data, betas, lookup, references, labels, args.data_dir)
    # The revision publisher updates the unified report after all tasks finish.
    print(json.dumps({"figure": layout, "comparison_table_rows": len(METHODS),
                      "cost_table_rows": len(METHODS) * len(betas)}, indent=2))


if __name__ == "__main__":
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        main()
