"""Plot saved OU path-validation runs; no simulations or parameter selection.

Run from the project root with:

    uv run --with numpy --with matplotlib python supplementary/plot_ou_path_validation.py

The input
is outputs/ou_path_validation/runs.csv produced by the experiment runner.
Presentation settings use the shared figure style. Only the figure and table
used by the manuscript are exported; saved numerical runs are not replaced.
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
REGIMES = ("P", "I", "S")
LABELS = {"P": "Population coefficients", "I": "Independent coefficients", "S": "Same-sample coefficients"}
COLORS = {"P": "#0072B2", "I": "#D55E00", "S": "#009E73"}
MARKERS = {"P": "o", "I": "s", "S": "^"}
REFERENCE_COLOR = "#525252"
LEGEND_GAP_PT = 32
LEGEND_BOTTOM_MARGIN_PT = 18


from figure_style import configure_style


def read_runs(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"No saved runs found in {path}")
    for row in rows:
        for key, value in list(row.items()):
            if key != "regime" and value != "":
                try:
                    row[key] = float(value)
                except ValueError:
                    pass
        if row["regime"] not in REGIMES:
            raise ValueError(f"Unknown coefficient regime: {row['regime']}")
    return rows


def selected(rows: list[dict], dt: float, regime: str, rank: int | None = None) -> list[dict]:
    return [row for row in rows if np.isclose(row["dt"], dt)
            and row["regime"] == regime and (rank is None or row["r"] == rank)]


def mean_sd(values) -> tuple[float, float]:
    values = np.asarray(list(values), dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("Non-finite metric in saved runs")
    return float(values.mean()), float(values.std(ddof=1)) if len(values) > 1 else 0.0


def series(rows: list[dict], dt: float, regime: str, ranks: list[int], metric: str):
    values = [mean_sd(row[metric] for row in selected(rows, dt, regime, rank)) for rank in ranks]
    return np.array(values, dtype=float).T


def finish_axis(ax, ranks: list[int], log_y: bool = False) -> None:
    ax.set_xticks(ranks)
    ax.tick_params(axis="x", labelrotation=0)
    ax.set_xlim(min(ranks) - 3, max(ranks) + 3)
    if log_y:
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(axis="y", which="major", color="#E0E0E0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(which="major", length=6, width=1)


def content_bottom(fig, axes, renderer) -> float:
    bounds = [ax.get_tightbbox(renderer) for ax in np.asarray(axes).ravel() if ax.get_visible()]
    bounds += [text.get_window_extent(renderer) for text in fig.texts
               if text.get_visible() and text.get_text()]
    return min(box.y0 for box in bounds if box is not None)


def shared_legend(fig, axes, ncol: int = 3):
    entries = {}
    for ax in np.asarray(axes).ravel():
        for handle, label in zip(*ax.get_legend_handles_labels()):
            entries.setdefault(label, handle)
    # Matplotlib fills columns first: keep the three coefficient regimes in
    # the top legend row and the two baselines in the second row.
    if "Exact-flow particles" in entries:
        labels = [LABELS["P"], "Exact-flow particles", LABELS["I"],
                  "Target reference", LABELS["S"]]
    else:
        labels = [LABELS[regime] for regime in REGIMES]
    legend = fig.legend([entries[label] for label in labels], labels,
                        loc="upper center", bbox_to_anchor=(.5, 0),
                        bbox_transform=fig.transFigure, ncol=ncol, frameon=False,
                        borderpad=0, borderaxespad=0, handlelength=2.1,
                        columnspacing=1.35, handletextpad=.6)
    for _ in range(12):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        needed = ((LEGEND_GAP_PT + LEGEND_BOTTOM_MARGIN_PT) * fig.dpi / 72
                  + legend.get_window_extent(renderer).height)
        shift = max(0, needed - content_bottom(fig, axes, renderer)) / fig.bbox.height
        if shift < 1e-6:
            break
        fig.subplots_adjust(bottom=fig.subplotpars.bottom + shift)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    top = (content_bottom(fig, axes, renderer) - LEGEND_GAP_PT * fig.dpi / 72) / fig.bbox.height
    legend.set_bbox_to_anchor((.5, top), transform=fig.transFigure)
    return legend


def save_figure(fig, axes, legend, name: str, output_dir: Path) -> dict:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    legend_box = legend.get_window_extent(renderer)
    gap = (content_bottom(fig, axes, renderer) - legend_box.y1) * 72 / fig.dpi
    bottom_margin = legend_box.y0 * 72 / fig.dpi
    bounds = [ax.get_tightbbox(renderer) for ax in np.asarray(axes).ravel()]
    bounds.append(legend_box)
    bounds.extend(text.get_window_extent(renderer) for text in fig.texts
                  if text.get_visible() and text.get_text())
    inside = all(box.x0 >= -1 and box.y0 >= -1
                 and box.x1 <= fig.bbox.width + 1 and box.y1 <= fig.bbox.height + 1
                 for box in bounds if box is not None)
    bars_inside = True
    for ax in np.asarray(axes).ravel():
        low_x, high_x = ax.get_xlim()
        low_y, high_y = ax.get_ylim()
        for container in ax.containers:
            if isinstance(container, ErrorbarContainer):
                for collection in container.lines[2]:
                    for segment in collection.get_segments():
                        bars_inside = bars_inside and bool(
                            np.all((segment[:, 0] >= low_x) & (segment[:, 0] <= high_x))
                            and np.all((segment[:, 1] >= low_y) & (segment[:, 1] <= high_y)))
    if abs(gap - LEGEND_GAP_PT) > .1 or bottom_margin < LEGEND_BOTTOM_MARGIN_PT - .1 or not inside or not bars_inside:
        raise RuntimeError(f"Layout check failed for {name}: gap={gap}, margin={bottom_margin}, inside={inside}")
    fig.savefig(output_dir / f"{name}.pdf")
    result = {"figure": name, "size_inches": list(fig.get_size_inches()),
              "legend_gap_pt": gap, "legend_bottom_margin_pt": bottom_margin,
              "all_content_inside_canvas": inside, "all_error_bars_inside_axes": bars_inside,
              "standard_deviation_bars_truncated": False, "output_format": "pdf"}
    plt.close(fig)
    return result


def plot_series(ax, rows, dt, ranks, metric, label=True, positive=False):
    for regime in REGIMES:
        means, stds = series(rows, dt, regime, ranks, metric)
        if positive and np.any(means - stds <= 0):
            raise ValueError("A log panel cannot show the full SD interval; use a linear or symlog axis")
        ax.errorbar(ranks, means, yerr=stds, fmt=MARKERS[regime] + "-",
                    color=COLORS[regime], capsize=4,
                    label=LABELS[regime] if label else None, zorder=3)


def comparison_figure(rows, ranks, steps, output_dir):
    configure_style('fig_ou_path_comparison', 17)
    fig, axes = plt.subplots(1, len(steps), figsize=(17, 7), sharey=True)
    axes = np.asarray(axes).reshape(-1)
    fig.suptitle("Ornstein-Uhlenbeck sampling with matched particles", y=.97)
    fig.subplots_adjust(left=.105, right=.98, top=.76, bottom=.30, wspace=.24)
    # The baseline is shared across ranks, regimes and step sizes for each seed.
    first_per_seed = {int(row["seed"]): row for row in rows}
    baseline_mean, baseline_std = mean_sd(row["exact_flow_w2"] for row in first_per_seed.values())
    reference_mean, reference_std = mean_sd(row["target_reference_w2"] for row in first_per_seed.values())
    displayed_max = max(baseline_mean + baseline_std, reference_mean + reference_std)
    for ax, dt in zip(axes, steps):
        plot_series(ax, rows, dt, ranks, "w2_target")
        for regime in REGIMES:
            means, stds = series(rows, dt, regime, ranks, "w2_target")
            displayed_max = max(displayed_max, float(np.max(means + stds)))
        ax.axhspan(max(0, baseline_mean - baseline_std), baseline_mean + baseline_std,
                   color="#9A6700", alpha=.09, linewidth=0)
        ax.axhline(baseline_mean, color="#9A6700", linestyle="--", label="Exact-flow particles", zorder=2)
        ax.axhspan(max(0, reference_mean - reference_std), reference_mean + reference_std,
                   color=REFERENCE_COLOR, alpha=.09, linewidth=0)
        ax.axhline(reference_mean, color=REFERENCE_COLOR, linestyle=":", label="Target reference", zorder=1)
        ax.set_title(rf"Step size $h={dt:g}$")
        ax.set_xlabel(r"Nonconstant modes $r$")
        finish_axis(ax, ranks)
    # Set shared limits after both panels are populated so that the first
    # panel cannot freeze autoscaling and crop the second panel's SD bars.
    axes[0].set_ylim(0, 1.06 * displayed_max)
    axes[0].set_ylabel(r"$W_2$ to the analytical target")
    legend = shared_legend(fig, axes, ncol=3)
    return save_figure(fig, axes, legend, "fig_ou_path_comparison", output_dir)


def tex_number(mean, sd):
    return rf"${mean:.4f} \pm {sd:.4f}$"


def write_tables(rows, ranks, steps, output_dir):
    metrics = ["w2_target", "exact_flow_w2", "D", "B", "cancellation_ratio",
               "identity_rms_error", "D_quadrature_difference", "B_quadrature_difference",
               "density_floor_events", "nonpositive_density_events", "speed_cap_events"]
    records = []
    for dt in steps:
        for rank in ranks:
            for regime in REGIMES:
                group = selected(rows, dt, regime, rank)
                item = {"dt": dt, "r": rank, "regime": regime, "n": len(group)}
                for metric in metrics:
                    item[f"{metric}_mean"], item[f"{metric}_std"] = mean_sd(row[metric] for row in group)
                records.append(item)
    with (output_dir / "summary_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    table = [r"% Generated from saved runs by supplementary/plot_ou_path_validation.py.",
             r"\begin{table}[t]", r"\centering", r"\small",
             r"\caption{Matched OU sampling and pathwise errors at the prescribed finer step $h=0.025$. "
             r"Entries are means $\pm$ sample standard deviations over ten matched source seeds. "
             r"P, I and S denote population, independent-sample and same-sample coefficients. "
             r"$D_T$ is the paired endpoint discrepancy; $B_T$ is its residual-norm bound evaluated "
             r"by numerical quadrature. The values are numerical diagnostics, not certified bounds. "
             r"Both prescribed step sizes and the identity and protection diagnostics are retained in the CSV data.}",
             r"\label{tab:ou_path_validation}",
             r"\begin{tabular}{ccrrr}", r"\toprule",
             r"$r$ & Coefficients & $W_2$ & $D_T$ & $B_T$ \\", r"\midrule"]
    for item in records:
        if not np.isclose(item["dt"], min(steps)):
            continue
        values = [tex_number(item[f"{metric}_mean"], item[f"{metric}_std"])
                  for metric in ["w2_target", "D", "B"]]
        table.append(f"{item['r']} & {item['regime']} & " + " & ".join(values) + r" \\")
    table += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    (output_dir / "summary_table.tex").write_text("\n".join(table), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "outputs" / "ou_path_validation")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "outputs" / "figures")
    args = parser.parse_args()
    rows = read_runs(args.data_dir / "runs.csv")
    ranks = sorted({int(row["r"]) for row in rows})
    steps = sorted({float(row["dt"]) for row in rows}, reverse=True)
    expected = len(ranks) * len(steps) * len(REGIMES) * len({row["seed"] for row in rows})
    keys = {(row["seed"], row["r"], row["dt"], row["regime"]) for row in rows}
    if len(rows) != expected or len(keys) != expected:
        raise ValueError("Saved runs must contain a unique, complete matched factorial design")
    for seed in {row["seed"] for row in rows}:
        same_seed = [row for row in rows if row["seed"] == seed]
        for metric in ("exact_flow_w2", "target_reference_w2"):
            values = np.asarray([row[metric] for row in same_seed], dtype=float)
            if not np.allclose(values, values[0], rtol=1e-13, atol=1e-14):
                raise ValueError(f"The matched {metric} must be shared across each seed's runs")
    args.figure_dir.mkdir(parents=True, exist_ok=True)
    configure_style()
    checks = [comparison_figure(rows, ranks, steps, args.figure_dir)]
    write_tables(rows, ranks, steps, args.data_dir)
    print(json.dumps({"figures": checks, "table_rows": len(ranks) * len(steps) * len(REGIMES)}, indent=2))


if __name__ == "__main__":
    from experiment_store import managed_outputs
    with managed_outputs("ou"):
        main()
