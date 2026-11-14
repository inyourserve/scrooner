"""Gate for resolve_bs.py: served PROVEN balance-sheet-family cells (analytics.cell_proof, latest row per cell, verdict PROVEN, own filing
accession) against (a) the published resolver-all110 rows and (b) the same file with the resolve_bs.py rows laid over it.
Usage: gate_bs.py proof_bs.json resolver-all110.csv resolver-bs.csv out_disagreements.csv"""
import csv, json, sys, collections
from datetime import date
from decimal import Decimal as D
PROOF = {'cash_and_equivalents_resolved': 'cash_and_equivalents', 'ppe_net_resolved': 'ppe_net', 'shares_outstanding_resolved': 'shares_outstanding',
         'current_assets_resolved': 'current_assets', 'current_liabilities_resolved': 'current_liabilities', 'stockholders_equity_resolved': 'stockholders_equity',
         'accounts_receivable': 'accounts_receivable', 'inventory': 'inventory', 'accounts_payable': 'accounts_payable', 'goodwill': 'goodwill'}
def unit(v):
    v = abs(v); k = 0
    while k < 9 and v != 0 and v % (10 ** (k + 1)) == 0: k += 1
    return D(10) ** k
def same(a, b):
    if a is None or b is None: return False
    if abs(b) < 1000: return abs(abs(a) - abs(b)) <= D('0.011')
    return abs(abs(a) - abs(b)) <= max(unit(a), unit(b)) * D('1.5')
def num(s):
    try: return D(str(s).replace(',', '').strip())
    except Exception: return None
VAL = ('mapped', 'component_sum', 'derived_not_printed')
def load(path):
    return {(r['accession'], r['data_point']): r for r in csv.DictReader(open(path))}
def main(proof_json, base_csv, bs_csv, out_csv):
    base = load(base_csv); mine = dict(base); mine.update(load(bs_csv))
    cells = [r for r in json.load(open(proof_json)) if r[6] == 'PROVEN' and r[1] in PROOF and r[5]]
    res = collections.defaultdict(collections.Counter); dis = []
    for cik, dpn, pe, val, tag, acc, verdict, det in cells:
        dp = PROOF[dpn]
        for name, tab in (('before', base), ('after', mine)):
            r = tab.get((acc, dp))
            if r is None or abs((date.fromisoformat(r['period_end']) - date.fromisoformat(pe)).days) > 10: res[(dp, name)]['not_compared'] += 1; continue   # own column only
            ok = r['decision'] in VAL and same(num(r['value']), num(val))
            res[(dp, name)]['agree' if ok else 'DISAGREE'] += 1
            if name == 'after' and not ok:
                dis.append(dict(ticker=r['ticker'], dp=dp, period_end=pe, served=val, served_tag=tag, decision=r['decision'], value=r['value'], nodes=r['nodes'][:160]))
    tot = {n: collections.Counter() for n in ('before', 'after')}
    for (dp, name), c in sorted(res.items()):
        print(f"{dp:24s} {name:6s} agree {c['agree']:5d} disagree {c['DISAGREE']:4d} not_compared {c['not_compared']}")
        tot[name].update(c)
    for n, c in tot.items(): print(n, 'agreement %.2f%% (%d/%d)' % (100 * c['agree'] / max(1, c['agree'] + c['DISAGREE']), c['agree'], c['agree'] + c['DISAGREE']))
    if dis:
        w = csv.DictWriter(open(out_csv, 'w', newline=''), fieldnames=list(dis[0].keys())); w.writeheader(); w.writerows(dis)
    print('disagreements after:', len(dis), collections.Counter((d['dp'], d['decision']) for d in dis))
if __name__ == '__main__': main(*sys.argv[1:5])
