"""Grade predictions against reader docmaps. Usage: grade.py PRED_DIR DOCMAP_DIR [TICKERS...] -> per-row CSV on stdout, summary on stderr.
correct = status matches (component sum == component_sum) and, for mapped/combined/component_sum, the tag set matches (prefix ignored)."""
import csv, glob, os, sys
from math import comb
def norm_status(s): return (s or '').strip().lower().replace(' ', '_')
def tagset(s):
    import re
    return {re.sub(r'\{.*?\}','',t).split(':')[-1].strip().lower() for t in re.split(r'[;,+]', s or '') if t.strip()}
def cp_upper(k, n, a=0.05):
    """Clopper-Pearson two-sided 95% upper bound on the error rate (log-space binomial CDF; no overflow)."""
    from math import lgamma, log, exp
    if n == 0 or k >= n: return 1.0
    def cdf(p):
        lp, lq = log(p), log(1 - p)
        return sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * lp + (n - i) * lq) for i in range(k + 1))
    lo, hi = k / n if k else 0.0, 1.0
    for _ in range(80):
        p = (lo + hi) / 2
        if p <= 0: lo = 1e-12; continue
        lo, hi = (p, hi) if cdf(p) > a / 2 else (lo, p)
    return hi
def main(pdir, ddir, *only):
    rows = []
    for dm in sorted(glob.glob(f'{ddir}/*-docmap-*.csv')):
        tk = os.path.basename(dm).split('-docmap')[0]
        if only and tk not in only: continue
        pf = f'{pdir}/{tk}-prediction.csv'
        pred = {r['data_point']: r for r in csv.DictReader(open(pf))} if os.path.exists(pf) else None
        for k in csv.DictReader(open(dm)):
            dp = k['data_point']
            if pred is None: rows.append(dict(ticker=tk, data_point=dp, result='no_prediction', error_class='', key_status=k['status'], pred_status='', key_tags=k['tags'], pred_tags='')); continue
            p = pred.get(dp)
            if p is None: rows.append(dict(ticker=tk, data_point=dp, result='wrong', error_class='missed', key_status=k['status'], pred_status='', key_tags=k['tags'], pred_tags='')); continue
            ks, ps = norm_status(k['status']), norm_status(p['status'])
            err = ''
            if dp == 'shares_outstanding' and 'entitycommonstocksharesoutstanding' in tagset(k['tags']):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: dei cover count (Dhairya ruling 2026-11-12)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if ks != ps: err = 'status'
            elif ks in ('mapped', 'combined', 'component_sum', 'component_in_note') and tagset(k['tags']) != tagset(p['tags']): err = 'tag'
            rows.append(dict(ticker=tk, data_point=dp, result='correct' if not err else 'wrong', error_class=err, key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags']))
    w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    g = [r for r in rows if r['result'] in ('correct', 'wrong')]; n = len(g); k = sum(r['result'] == 'wrong' for r in g)
    print(f'graded {n} lines, wrong {k}, accuracy {100*(n-k)/max(n,1):.1f}%, error upper bound (CP 95%) {100*cp_upper(k,n):.1f}%; no_prediction {sum(r["result"]=="no_prediction" for r in rows)}; key_errors {sum(r["result"]=="key_error" for r in rows)}', file=sys.stderr)
if __name__ == '__main__':
    main(*sys.argv[1:])
