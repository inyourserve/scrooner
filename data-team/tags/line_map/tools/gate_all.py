import csv, glob, os, re, collections, json
from decimal import Decimal as D
from datetime import date
RES = collections.defaultdict(dict)
for r in csv.DictReader(open('resolved_all.csv')): RES[(r['ticker'], r['accession'])][r['data_point']] = r
own = collections.defaultdict(list)
for (tk, acc), m in RES.items():
    pe = next(iter(m.values()))['period_end']; own[tk].append((date.fromisoformat(pe), acc))
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
def find(tk, pe):
    pe = date.fromisoformat(pe)
    m = [acc for d, acc in own.get(tk, []) if abs((d - pe).days) <= 10]
    return m[0] if m else None
VAL = ('mapped', 'component_sum', 'derived')
NOV = ('not_presented', 'combined', 'no_role')
out = []; C = collections.Counter(); COV = collections.Counter(); bydp = collections.defaultdict(collections.Counter)
for x in csv.DictReader(open('cov_latest.csv')):
    tk, dp = x['ticker'], x['data_point']
    acc = find(tk, x['period_end'])
    if acc is None: COV['no_own_10k_in_fsn'] += 1; bydp[dp]['no_own_10k'] += 1; continue
    r = RES[(tk, acc)].get(dp)
    if r is None: COV['dp_not_in_resolver'] += 1; bydp[dp]['not_in_resolver'] += 1; continue
    st = r['status']
    COV['covered_value' if st in VAL else ('covered_reason' if st in ('not_presented', 'combined') else 'no_role')] += 1
    bydp[dp][st] += 1
    if x['class'] == 'PROVEN' and x['accession'] == acc and x['shown_value']:
        ok = st in VAL and same(num(r['value']), num(x['shown_value']))
        C[('proven', ok)] += 1
        if not ok: out.append(dict(src='proven', ticker=tk, dp=dp, pe=x['period_end'], key=x['shown_value'], key_tag=x['tag'], st=st, val=r['value'], tags=r['tags'], why=r['why'][:200]))
json.dump({k: dict(v) for k, v in bydp.items()}, open('bydp.json', 'w'))
print('cells', sum(COV.values()), COV)
tot = sum(COV.values()); cov = COV['covered_value'] + COV['covered_reason']
print('coverage of template cells: %.2f%% (value or reason)' % (100 * cov / tot), ' of cells with an own 10-K in FSN: %.2f%%' % (100 * cov / (tot - COV['no_own_10k_in_fsn'])))
a, b = C[('proven', True)], C[('proven', False)]; print('PROVEN agreement %.2f%% (%d/%d)' % (100 * a / (a + b), a, a + b))
w = csv.DictWriter(open('gate_all_disagree.csv', 'w', newline=''), fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(collections.Counter((o['dp'], o['st']) for o in out).most_common(40))
