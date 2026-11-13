"""Collect, for every ticker of rank >= 101 with a docmap on a work/reads/* branch, the docmap and the prediction committed on
origin/main BEFORE that docmap's first commit. Run from a repo checkout after `git fetch origin main 'refs/heads/work/reads/*:...'`.
Usage: collect_blind.py RANKS_CSV OUT_DIR   (writes OUT_DIR/dm, OUT_DIR/pred, OUT_DIR/timing.csv)"""
import subprocess, csv, os, sys
def g(*a): return subprocess.run(['git'] + list(a), capture_output=True, text=True).stdout
ranks = {r[1]: int(r[0]) for r in csv.reader(open(sys.argv[1]))}
out = sys.argv[2]; os.makedirs(f'{out}/dm', exist_ok=True); os.makedirs(f'{out}/pred', exist_ok=True)
brs = [b.strip() for b in g('branch', '-r').split('\n') if 'work/reads/' in b]
first, path, br = {}, {}, {}
for b in brs:
    for f in g('ls-tree', '-r', '--name-only', b, 'data-team/companies/reads/').split():
        if '-docmap-' in f and f.endswith('.csv'):
            t = os.path.basename(f).split('-docmap')[0]
            ts = g('log', '--diff-filter=A', '--format=%cI', '-1', b, '--', f).strip()
            if t in ranks and ranks[t] >= 101 and ts and (t not in first or ts < first[t]):
                first[t], path[t], br[t] = ts, f, b
log = []
for t, ts in sorted(first.items(), key=lambda x: x[1]):
    open(f'{out}/dm/{os.path.basename(path[t])}', 'w').write(g('show', f'{br[t]}:{path[t]}'))
    c = g('log', 'origin/main', f'--before={ts}', '--format=%H %cI', '-1', '--', f'data-team/tags/exam/{t}-prediction.csv').split()
    pf = f'{out}/pred/{t}-prediction.csv'
    if c:
        open(pf, 'w').write(g('show', f'{c[0]}:data-team/tags/exam/{t}-prediction.csv')); log.append((t, ranks[t], ts, c[1], c[0][:8]))
    else:
        if os.path.exists(pf): os.remove(pf)
        log.append((t, ranks[t], ts, 'NONE', ''))
csv.writer(open(f'{out}/timing.csv', 'w')).writerows([('ticker', 'rank', 'docmap_first_commit', 'prediction_commit', 'sha')] + log)
print(len(first), 'blind tickers;', sum(x[3] == 'NONE' for x in log), 'without an earlier prediction')
