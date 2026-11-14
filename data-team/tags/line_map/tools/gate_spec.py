"""Gate a resolver-format CSV against served PROVEN cells (own filing only), SIGNED comparison (a sign error is a
disagreement). Usage: gate_spec.py RESOLVER.csv COVERAGE.csv OUT_DISAGREE.csv"""
import csv, sys, collections
from decimal import Decimal as D
from datetime import date
res, cov, outp = sys.argv[1:4]
R = {}
for r in csv.DictReader(open(res)): R[(r['ticker'], r['accession'], r['data_point'])] = r
def unit(v):
    v = abs(v); k = 0
    while k < 9 and v != 0 and v % (10 ** (k + 1)) == 0: k += 1
    return D(10) ** k
def num(s):
    try: return D(str(s).replace(',', '').strip())
    except Exception: return None
def same(a, b):
    if a is None or b is None: return False
    if abs(b) < 1000: return abs(a - b) <= D('0.011')
    return abs(a - b) <= max(unit(a), unit(b)) * D('1.5')
C = collections.Counter(); out = []; dpC = collections.defaultdict(collections.Counter)
for x in csv.DictReader(open(cov)):
    if x['class'] != 'PROVEN' or not x['accession'] or not x['shown_value']: continue
    r = R.get((x['ticker'], x['accession'], x['data_point']))
    if r is None or abs((date.fromisoformat(r['period_end']) - date.fromisoformat(x['period_end'])).days) > 10: continue   # own-period filing only
    v = num(r['value']); s = num(x['shown_value'])
    ok = same(v, s); C[ok] += 1; dpC[x['data_point']][ok] += 1
    if not ok:
        kind = 'sign_only' if v is not None and s is not None and same(abs(v), abs(s)) else ('no_value' if v is None else 'value')
        out.append(dict(ticker=x['ticker'], data_point=x['data_point'], period_end=x['period_end'], served=x['shown_value'], served_tag=x['tag'], decision=r['decision'], value=r['value'], kind=kind, nodes=r['nodes'][:250], flags=r['flags']))
print('PROVEN signed agreement %.2f%% (%d/%d)' % (100 * C[True] / (C[True] + C[False]), C[True], C[True] + C[False]))
print(collections.Counter(o['kind'] for o in out))
w = csv.DictWriter(open(outp, 'w', newline=''), fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
