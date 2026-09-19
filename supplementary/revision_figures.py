"""Regenerate revision PDFs, optionally only the two corrected product figures."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from revision_common import ROOT,OUT,write_json

def main(products_only=False):
    import plot_admissible_source as a
    import plot_data_comparison as c
    checks=[];directory=ROOT/'outputs/figures'
    if not products_only:
        data,runs,groups,betas,refs,labels=a.load_data(ROOT/'outputs/admissible_source/summary.json')
        stats=a.regime_statistics(runs,betas)
        checks.append(a.regime_figure(stats,betas,refs,directory))
        a.export_tables(data,runs,groups,stats,betas,refs,labels,ROOT/'outputs/admissible_source')
        data,betas,lookup,refs,labels=c.load_summary(ROOT/'outputs/data_comparison/summary.json')
        checks.append(c.plot_comparison(betas,lookup,refs,labels,directory))
        c.write_tables(data,betas,lookup,refs,labels,ROOT/'outputs/data_comparison')
    notebook=json.loads((ROOT/'BKT_experiments.ipynb').read_text(encoding='utf-8'))
    namespace={'__name__':'revision_plot_cells'}
    original=Figure.savefig
    def checked_savefig(fig,path,*args,**kwargs):
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        boxes=[ax.get_tightbbox(renderer) for ax in fig.axes if ax.get_visible()]
        boxes += [t.get_window_extent(renderer) for t in fig.texts if t.get_visible() and t.get_text()]
        boxes += [leg.get_window_extent(renderer) for leg in fig.legends]
        inside=all(b.x0>=-1 and b.y0>=-1 and b.x1<=fig.bbox.width+1 and b.y1<=fig.bbox.height+1 for b in boxes if b is not None)
        if not inside:raise ValueError('Text or legend lies outside the canvas: '+str(path))
        text=[t for ax in fig.axes for t in (ax.title,ax.xaxis.label,ax.yaxis.label,*ax.get_xticklabels(),*ax.get_yticklabels()) if t.get_text()]
        if any(t.get_fontweight() not in ('normal',400) for t in text):raise ValueError('Unexpected bold text')
        checks.append(dict(figure=Path(path).stem,size_inches=fig.get_size_inches().tolist(),all_content_inside_canvas=inside,
                           font_weights=sorted({str(t.get_fontweight()) for t in text}),
                           font_sizes=sorted({t.get_fontsize() for t in text}),output_format='pdf'))
        return original(fig,path,*args,**kwargs)
    before=Path.cwd()
    try:
        os.chdir(ROOT);exec(''.join(notebook['cells'][22]['source']),namespace)
        Figure.savefig=checked_savefig
        for cell in ((26,) if products_only else (24,26)):exec(''.join(notebook['cells'][cell]['source']),namespace)
    finally:
        Figure.savefig=original;os.chdir(before);plt.close('all')
    assert len(checks)==(2 if products_only else 5)
    write_json(OUT/('followup_figure_checks.json' if products_only else 'figure_checks.json'),checks)
    print(json.dumps(checks,indent=2))

if __name__=='__main__':
    from experiment_store import managed_outputs
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--products-only',action='store_true')
    args=parser.parse_args()
    with managed_outputs('double_well','ou','alanine'):main(products_only=args.products_only)
