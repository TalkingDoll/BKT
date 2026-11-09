"""Compare the results of the fresh rerun (bkt_rerun/results) with the delivered results (notebook/results).

Every numeric entry is compared, except computing times, which depend on the machine load. Reports per file the
number of entries, the largest absolute and relative differences and the paths where they occur."""
import json, os, re, sys
import numpy as np
ORIG = '../results'
NEW = '<folder of a fresh rerun>/results'
TIMING = re.compile(r'^(seconds|fit_seconds|transport_seconds|elapsed)$')   # computing times only


def walk(a, b, path, out, timing):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out['missing'].append(f'{path}/{k}'); continue
            if TIMING.search(str(k)):
                timing.append((f'{path}/{k}', a[k], b[k])); continue
            walk(a[k], b[k], f'{path}/{k}', out, timing)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out['missing'].append(f'{path} (length {len(a)} vs {len(b)})')
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f'{path}[{i}]', out, timing)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        x, y = float(a), float(b); out['n'] += 1
        if not (np.isfinite(x) and np.isfinite(y)):
            if not (np.isnan(x) and np.isnan(y)) and x != y: out['diff'].append((path, x, y, np.inf, np.inf))
            return
        d = abs(x - y); r = d / max(abs(x), abs(y), 1e-300)
        if d > 0: out['diff'].append((path, x, y, d, r))
    elif a != b:
        out['other'].append((path, str(a)[:40], str(b)[:40]))


def compare(name):
    a = json.load(open(os.path.join(ORIG, name))); b = json.load(open(os.path.join(NEW, name)))
    out = dict(n=0, diff=[], missing=[], other=[]); timing = []
    walk(a, b, '', out, timing)
    d = sorted(out['diff'], key=lambda z: -z[4])
    worst_r = d[0][4] if d else 0.0; worst_a = max((z[3] for z in d), default=0.0)
    print(f"{name:24s} entries {out['n']:6d} | differing {len(d):5d} | max rel {worst_r:.1e} | max abs {worst_a:.1e} | missing {len(out['missing'])} | other {len(out['other'])} | timing fields {len(timing)}")
    for z in d[:4]:
        print(f"    {z[0][:90]}: {z[1]:.6g} vs {z[2]:.6g}")
    for z in out['missing'][:3]: print('    missing', z)
    for z in out['other'][:3]: print('    other', z)
    return out, timing


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(f for f in os.listdir(ORIG) if f.endswith('.json'))
    for nm in names:
        if os.path.exists(os.path.join(NEW, nm)):
            compare(nm)
        else:
            print(f'{nm:24s} not yet produced by the rerun')
    for nm in ('e6_target.npy',):
        if os.path.exists(os.path.join(NEW, nm)):
            x, y = np.load(os.path.join(ORIG, nm)), np.load(os.path.join(NEW, nm))
            print(f'{nm:24s} shape {x.shape} | max abs diff {np.abs(x - y).max():.1e}')
