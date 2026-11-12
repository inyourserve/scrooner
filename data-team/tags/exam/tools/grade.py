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
    rows = []; keyed = {}
    adj = {}
    ap = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adjudications.csv')
    if os.path.exists(ap):
        for a in csv.DictReader(open(ap)): adj[(a['ticker'], a['data_point'])] = a['ruling']
    for dm in sorted(glob.glob(f'{ddir}/*-docmap-*.csv')):
        tk = os.path.basename(dm).split('-docmap')[0]
        if only and tk not in only: continue
        pf = f'{pdir}/{tk}-prediction.csv'
        pred = {r['data_point']: r for r in csv.DictReader(open(pf))} if os.path.exists(pf) else None
        K = {r['data_point']: r for r in csv.DictReader(open(dm))}
        def num(x):
            try: return float(x)
            except (TypeError, ValueError): return None
        o, rv, oi, cr = (num(K.get(d, {}).get('fy0_api')) for d in ('operating_expenses', 'revenue', 'operating_income', 'cost_of_revenue'))
        ko = K.get('operating_expenses', {}); kc = K.get('cost_of_revenue', {})
        cor_present = norm_status(kc.get('status')) in ('mapped', 'component_sum', 'combined')
        ce = 'costsandexpenses' in tagset(ko.get('tags'))
        incl = bool(o is not None and rv is not None and oi is not None and abs(o - (rv - oi)) <= max(abs(o) * 0.0005, 1) and cor_present)
        incl = incl or (ce and cor_present and o is not None and cr is not None and abs(o) > abs(cr))
        onestep = ce and not cor_present and norm_status(kc.get('status')) != 'out'
        keyed[tk] = {'cor': incl or onestep}
        for k in csv.DictReader(open(dm)):
            dp = k['data_point']
            if pred is None: rows.append(dict(ticker=tk, data_point=dp, result='no_prediction', error_class='', key_status=k['status'], pred_status='', key_tags=k['tags'], pred_tags='')); continue
            p = pred.get(dp)
            if p is None: rows.append(dict(ticker=tk, data_point=dp, result='wrong', error_class='missed', key_status=k['status'], pred_status='', key_tags=k['tags'], pred_tags='')); continue
            ks, ps = norm_status(k['status']), norm_status(p['status'])
            err = ''
            if (tk, dp) in adj and norm_status(k['status']) != norm_status(p['status']):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: ' + adj[(tk, dp)], key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
            if dp == 'operating_expenses' and norm_status(k['status']) == 'mapped' and keyed.get(tk, {}).get('cor'):
                rows.append(dict(ticker=tk, data_point=dp, result='key_error', error_class='key: opex total includes cost of revenue (Dhairya ruling 2026-11-12)', key_status=k['status'], pred_status=p['status'], key_tags=k['tags'], pred_tags=p['tags'])); continue
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
