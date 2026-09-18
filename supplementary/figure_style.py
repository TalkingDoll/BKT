"""Match printed font sizes across figures at their current LaTeX widths."""
from pathlib import Path
import re
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PAPER_FONT_SIZES = {'base': 8.5, 'title': 11, 'panel': 9.5, 'axis': 9, 'ticks': 8.5, 'legend': 8}
# Keep this object stable: the notebook imports it before selecting each figure.
FONT_SIZES = {}
LEGEND_GAP_PT = 32
LEGEND_BOTTOM_MARGIN_PT = 18


def manuscript_width_inches(name):
    paper = ROOT / 'manuscript_iclr'
    style = (paper / 'iclr2027_conference.sty').read_text(encoding='utf-8')
    match = re.search(r'\\textwidth\s+([\d.]+)\s+(?:true\s+)?in\b', style)
    if not match:
        raise ValueError('Expected the manuscript text width to be specified in inches')
    text_width = float(match[1])
    source = '\n'.join((paper / f'{stem}.tex').read_text(encoding='utf-8') for stem in ['main', 'appendix'])
    source = re.sub(r'(?m)(?<!\\)%.*$', '', source)
    pattern = r'\\includegraphics\[width=(?P<fraction>[\d.]*)\\textwidth\]\{' + re.escape(name) + r'\}'
    matches = list(re.finditer(pattern, source))
    widths = {text_width * float(item['fraction'] or 1) for item in matches}
    if len(widths) != 1:
        raise ValueError(f'{name}: expected one unambiguous manuscript insertion width')
    return widths.pop()


def configure_style(name=None, canvas_width=None):
    # Non-manuscript notebook figures use a nominal standalone scale.
    scale = 25 / PAPER_FONT_SIZES['base'] if name is None else canvas_width / manuscript_width_inches(name)
    FONT_SIZES.update({key: value * scale for key, value in PAPER_FONT_SIZES.items()})
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': FONT_SIZES['base'],
        'font.weight': 'normal', 'figure.titleweight': 'normal',
        'axes.titleweight': 'normal', 'axes.labelweight': 'normal',
        'figure.titlesize': FONT_SIZES['title'], 'axes.titlesize': FONT_SIZES['panel'],
        'axes.labelsize': FONT_SIZES['axis'], 'xtick.labelsize': FONT_SIZES['ticks'],
        'ytick.labelsize': FONT_SIZES['ticks'], 'legend.fontsize': FONT_SIZES['legend'],
        'axes.titlepad': 5.5 * scale, 'axes.labelpad': 3.5 * scale,
        'xtick.major.pad': 2.2 * scale, 'ytick.major.pad': 2.2 * scale,
        'lines.linewidth': .8 * scale, 'lines.markersize': 2.4 * scale,
        'axes.spines.top': False, 'axes.spines.right': False,
        'pdf.fonttype': 42, 'ps.fonttype': 42,
        'savefig.facecolor': 'white', 'figure.facecolor': 'white',
    })
