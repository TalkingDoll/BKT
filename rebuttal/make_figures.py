"""Figures of the experiments added in the revision, in the style of the figures of the submission.

Reads the result files in results/ and writes figures/fig_lawgd_double_wells.pdf (Figure 11),
figures/fig_barrier_scan.pdf (Figure 12) and figures/fig_coupled3d.pdf (three-dimensional example).
Independent panels carry their quantity as a title. A shared quantity of a row is written once on the left.
Legends are placed below the panels."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results'); FIG = os.path.join(HERE, 'figures'); os.makedirs(FIG, exist_ok=True)

STYLE = {'font.size': 8, 'axes.titlesize': 8.5, 'axes.labelsize': 8, 'legend.fontsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
         'figure.titlesize': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'axes.grid.axis': 'y',
         'grid.color': '0.9', 'grid.linewidth': 0.6, 'legend.frameon': False, 'lines.linewidth': 1.1, 'lines.markersize': 3,
         'errorbar.capsize': 1.8, 'pdf.fonttype': 42}
C = dict(bkt='#0072b2', lawgd='#d55e00', fd='#009e73', est='#8e44ad', lag='#e69f00', ref='0.35', band='0.9', data='0.5')
mean = lambda v: float(np.mean(v))
sd = lambda v: float(np.std(v, ddof=1)) if len(v) > 1 else 0.0
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


def fig_barrier():
    rows = [r for r in load('e1v2_results.json') if r['a'] <= 10]
    stat = {(r['a'], r['init'], r['seed']): r for r in load('e1_stationarity.json')}
    E = {}
    for init in ('both', 'right'):
        for a in sorted({r['a'] for r in rows}):
            R = [r for r in rows if r['a'] == a and r['init'] == init]
            g = lambda f: np.array([f(r) for r in R], float)
            E[(init, a)] = dict(dataL=g(lambda r: r['data_left_fraction']), ref=R[0]['reference_mean'], fd_w2=g(lambda r: r['fd']['w2']), fd_left=g(lambda r: r['fd']['left']),
                                rel=g(lambda r: abs(r['adapted']['rel'])), dis1=g(lambda r: r['adapted']['dis1']), w2=g(lambda r: r['adapted']['w2']), left=g(lambda r: r['adapted']['left']))
    ks = sorted(a for (i, a) in E if i == 'both')
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.6))
    for init, ls in (('both', '-'), ('right', '--')):
        dd = [E[(init, a)] for a in ks]
        ax[0].plot(ks, [np.median(x['rel']) for x in dd], color=C['est'], ls=ls, marker='o')
        ax[0].plot(ks, [np.median(x['dis1']) for x in dd], color=C['lag'], ls=ls, marker='s')
        ax[1].errorbar(ks, [mean(x['w2']) for x in dd], [sd(x['w2']) for x in dd], color=C['est'], ls=ls, marker='o')
        ax[2].errorbar(ks, [mean(x['left']) for x in dd], [sd(x['left']) for x in dd], color=C['est'], ls=ls, marker='o')
        ax[2].plot(ks, [mean(x['dataL']) for x in dd], color=C['data'], ls=ls, lw=0.9, marker='x')
        if init == 'both':
            ax[1].errorbar(ks, [mean(x['fd_w2']) for x in dd], [sd(x['fd_w2']) for x in dd], color=C['fd'], marker='^')
            ax[1].plot(ks, [x['ref'] for x in dd], color=C['ref'], ls=':', lw=0.9)
            ax[2].errorbar(ks, [mean(x['fd_left']) for x in dd], [sd(x['fd_left']) for x in dd], color=C['fd'], marker='^')
    ax[0].set_yscale('log'); ax[0].set_title(r'$|\hat\lambda_1/\lambda_1-1|$ and lag disagreement (median)')
    ax[1].set_yscale('log'); ax[1].set_title(r'$W_2$ to the target')
    ax[2].set_title('Mass of the left well'); ax[2].axhline(0.5, color=C['ref'], ls=':', lw=0.9); ax[2].set_ylim(-0.02, 0.62)
    for a_ in ax: a_.set_xlabel(r'Barrier height $a$ ($k_BT$)'); a_.set_xticks(ks)
    fig.suptitle(r'Barrier-height scan, $V=a(x^2-1)^2$, trajectory data')
    legend_below(fig, [Line2D([], [], color=C['est'], marker='o', label='Estimated eigenpairs'),
                       Line2D([], [], color=C['lag'], marker='s', label='Lag disagreement'),
                       Line2D([], [], color=C['fd'], marker='^', label='FD eigenpairs'),
                       Line2D([], [], color=C['ref'], ls=':', label='Target reference'),
                       Line2D([], [], color=C['data'], marker='x', lw=0.9, label='Left-well fraction of the data'),
                       Line2D([], [], color='k', label='Chains start in both wells'),
                       Line2D([], [], color='k', ls='--', label='Chains start in the right well')], 4, y=0.0)
    fig.tight_layout(rect=(0, 0.19, 1, 1)); fig.savefig(os.path.join(FIG, 'fig_barrier_scan.pdf')); plt.close(fig)


def fig_coupled3d():
    a, b = load('e6v2_results.json'), load('e6b_results.json'); A6, B6 = a['rows'], b['rows']; rs = [8, 16, 32, 64]
    fig, ax = plt.subplots(1, 2, figsize=(6.2, 2.5))
    series = (('fd', A6, 'fd', 'BKT, FD-41', C['fd'], '^'), ('k513', A6, 'koopman', 'BKT, $J=513$', C['bkt'], 'o'), ('k1729', B6, 'koopman', 'BKT, $J=1729$', '#56b4e9', 'o'),
              ('l513', A6, 'lawgd', 'LAWGD, $J=513$', C['lawgd'], 's'), ('l1729', B6, 'lawgd', 'LAWGD, $J=1729$', '#f0a070', 's'))
    for key, R, src, label, col, mk in series:
        for j, q in enumerate(('w2', 'tv')):
            v = np.array([[x[src][str(r)][q] for r in rs] for x in R])
            ax[j].errorbar(rs, v.mean(0), v.std(0, ddof=1), color=col, marker=mk)
    ref_band(ax[0], a['reference']['mean'], a['reference']['sd'])
    ax[0].set_title(r'Sliced $W_2$ to the target sample'); ax[1].set_title('TV of the masses of the eight wells')
    for a_ in ax: a_.set_xscale('log', base=2); a_.set_xticks(rs); a_.set_xticklabels([str(r) for r in rs]); a_.set_xlabel(r'Retained modes $r$')
    fig.suptitle(r'Coupled three-dimensional double well, $\beta=0.5$')
    legend_below(fig, [Line2D([], [], color=col, marker=mk, label=label) for _, _, _, label, col, mk in series] + [Line2D([], [], color=C['ref'], ls=':', label='Target reference')], 3)
    fig.tight_layout(rect=(0, 0.2, 1, 1)); fig.savefig(os.path.join(FIG, 'fig_coupled3d.pdf')); plt.close(fig)


def main(png=False):
    """Write the three PDFs (and PNG copies if png=True, for display in the notebook) and return their paths."""
    with plt.rc_context(STYLE):
        fig_lawgd(); fig_barrier(); fig_coupled3d()
    out = [os.path.join(FIG, f) for f in ('fig_lawgd_double_wells.pdf', 'fig_barrier_scan.pdf', 'fig_coupled3d.pdf')]
    if png:
        import subprocess
        for f in out:
            subprocess.run(['pdftoppm', '-r', '150', '-png', '-singlefile', f, f[:-4]], check=False)
        out = [f[:-4] + '.png' for f in out]
    return out


if __name__ == '__main__':
    print('\n'.join(main()))
