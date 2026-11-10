"""Figures of the experiments added in the revision, in the style of the figures of the submission.

Reads the result files in results/ and writes figures/fig_lawgd_double_wells.pdf (Figure 8).
Independent panels carry their quantity as a title. A shared quantity of a row is written once on the left.
The legend is placed below the panels."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results'); FIG = os.path.join(HERE, 'figures'); os.makedirs(FIG, exist_ok=True)

STYLE = {'font.size': 8, 'axes.titlesize': 8.5, 'axes.labelsize': 8, 'legend.fontsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
         'figure.titlesize': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'axes.grid.axis': 'y',
         'grid.color': '0.9', 'grid.linewidth': 0.6, 'legend.frameon': False, 'lines.linewidth': 1.1, 'lines.markersize': 3,
         'errorbar.capsize': 1.8, 'pdf.fonttype': 42}
C = dict(bkt='#0072b2', lawgd='#d55e00', ref='0.35', band='0.9')
load = lambda name: json.load(open(os.path.join(RES, name)))


def ref_band(ax, m, s, **kw):
    ax.axhspan(m - s, m + s, color=C['band'], lw=0, zorder=0); ax.axhline(m, color=C['ref'], ls=':', lw=0.9, zorder=1)


def legend_below(fig, handles, ncol, y=0.0):
    fig.legend(handles=handles, loc='lower center', ncol=ncol, bbox_to_anchor=(0.5, y), handlelength=1.8, columnspacing=1.2, handletextpad=0.5)


def fig_lawgd():
    rows = load('e5v2_results.json')
    names = {'A2_beta0.0': r'$\beta=0$', 'A2_beta0.25': r'$\beta=0.25$', 'A2_beta0.5': r'$\beta=0.5$', 'A2_beta1.0': r'$\beta=1$', 'B_quartic4': 'Four wells'}
    fig, axs = plt.subplots(1, 5, figsize=(7.0, 2.25), sharey=True)
    for ax, (key, label) in zip(axs, names.items()):
        R = [r for r in rows if r['system'] == key]
        S = [c for c, _ in R[0]['lawgd']['checkpoints']]
        for meth, col, mk in (('bkt', C['bkt'], 'o'), ('lawgd', C['lawgd'], 's')):
            v = np.array([[x for _, x in r[meth]['checkpoints']] for r in R])
            ax.errorbar(S, v.mean(0), v.std(0, ddof=1), color=col, marker=mk)
        ref_band(ax, R[0]['reference']['metrics']['sw']['mean'], R[0]['reference']['metrics']['sw']['std'])
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_title(label); ax.set_xlabel(r'Flow time $s=\hat\lambda_1 t$')
    axs[0].set_ylabel(r'Sliced $W_2$')
    fig.suptitle('BKT and LAWGD with the same estimated eigenpairs')
    legend_below(fig, [Line2D([], [], color=C['bkt'], marker='o', label='BKT'), Line2D([], [], color=C['lawgd'], marker='s', label='LAWGD'),
                       Line2D([], [], color=C['ref'], ls=':', label='Target reference')], 3)
    fig.tight_layout(rect=(0, 0.1, 1, 1)); fig.savefig(os.path.join(FIG, 'fig_lawgd_double_wells.pdf')); plt.close(fig)


def main(png=False):
    """Write the PDF (and a PNG copy if png=True, for display in the notebook) and return the paths."""
    with plt.style.context('default'), plt.rc_context(STYLE):       # independent of the settings of the calling session
        fig_lawgd()
    out = [os.path.join(FIG, 'fig_lawgd_double_wells.pdf')]
    if png:
        import subprocess
        for f in out:
            subprocess.run(['pdftoppm', '-r', '150', '-png', '-singlefile', f, f[:-4]], check=False)
        out = [f[:-4] + '.png' for f in out]
    return out


if __name__ == '__main__':
    print('\n'.join(main()))
