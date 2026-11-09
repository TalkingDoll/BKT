"""Compare the tables printed by the executed notebook on the rerun results with those of the delivered notebook.

The tables are read back from the HTML outputs of cells 30-40 and compared cell by cell; columns that hold
computing times are dropped. Stream outputs are compared line by line, ignoring lines that report times."""
import io, json, re, sys
import pandas as pd
ORIG = '../BKT_rebuttal_experiments.ipynb'
NEW = '<executed copy of the notebook on the rerun results>'
TIMECOL = re.compile(r'(second|fit s|run s|^s$|time)', re.I)


def tables(path):
    nb = json.load(open(path)); out = {}
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] != 'code' or i < 30: continue
        tabs, streams = [], []
        for o in c.get('outputs', []):
            if 'text/html' in o.get('data', {}):
                tabs.append(pd.read_html(io.StringIO(''.join(o['data']['text/html'])))[0])
            elif o.get('output_type') == 'stream':
                streams += [l for l in ''.join(o['text']).split('\n') if l.strip() and not re.search(r'\d+(\.\d+)?\s*s\b|second|fit', l)]
        out[i] = (tabs, streams)
    return out


A, B = tables(ORIG), tables(NEW); bad = 0
for i in sorted(A):
    ta, sa = A[i]; tb, sb = B.get(i, ([], []))
    for k, (x, y) in enumerate(zip(ta, tb)):
        cols = [c for c in x.columns if not TIMECOL.search(str(c))]
        x2, y2 = x[cols].astype(str), y[[c for c in cols if c in y.columns]].astype(str)
        same = x2.shape == y2.shape and (x2.values == y2.values).all()
        if not same:
            bad += 1; diff = (x2 != y2) if x2.shape == y2.shape else None
            print(f'cell {i} table {k}: DIFFERENT', x2.shape, y2.shape)
            if diff is not None:
                for r, c in zip(*diff.values.nonzero()):
                    print('   ', x2.iloc[r, 0], cols[c], x2.iloc[r, c], '->', y2.iloc[r, c])
        else:
            print(f'cell {i} table {k}: identical ({x2.shape[0]} rows, {x2.shape[1]} columns compared, timing columns dropped {len(x.columns) - len(cols)})')
    if len(ta) != len(tb): bad += 1; print(f'cell {i}: {len(ta)} tables vs {len(tb)}')
    if sa != sb:
        bad += 1; print(f'cell {i}: printed lines differ'); [print('   -', l[:150]) for l in sa if l not in sb]; [print('   +', l[:150]) for l in sb if l not in sa]
print('differences:', bad)
