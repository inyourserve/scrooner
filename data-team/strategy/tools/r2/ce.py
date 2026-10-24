import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load(); F = D['filings']; SUB = D['sub']
def cs(x, y): return x is not None and y is not None and abs(x - y) <= max(1.0, 0.005 * max(abs(x), abs(y)))
REV = ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax', 'RevenuesNetOfInterestExpense', 'RegulatedAndUnregulatedOperatingRevenue')
c = collections.Counter(); ex = collections.defaultdict(list); fam = collections.defaultdict(collections.Counter)
for a in F:
    rs = rows(D, a, 'IS'); tg = {r[4]: val(D, a, r[4], r[5], 'IS') for r in rs}
    ce = tg.get('CostsAndExpenses')
    if ce is None: continue
    oi = tg.get('OperatingIncomeLoss')
    rv = None
    for r in rs:  # last standard revenue total on face before CE
        if r[4] in REV and val(D, a, r[4], r[5], 'IS') is not None: rv = val(D, a, r[4], r[5], 'IS')
    if rv is None: k = 'no_std_revenue_total'
    else:
        cor = next((tg[t] for t in ('CostOfRevenue', 'CostOfGoodsAndServicesSold', 'CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization') if tg.get(t) is not None), None)
        gp = tg.get('GrossProfit')
        pt = next((val(D, a, r[4], r[5], 'IS') for r in rs if r[4].startswith('IncomeLossFromContinuingOperationsBeforeIncomeTaxes')), None)
        if oi is not None and cs(rv - ce, oi): k = 'A_rev_minus_CE_eq_OI (CE = all operating costs)'
        elif oi is not None and ((gp is not None and cs(gp - ce, oi)) or (cor is not None and cs(rv - cor - ce, oi))): k = 'B_CE_excludes_cost_of_revenue (CE = opex only)'
        elif pt is not None and cs(rv - ce, pt): k = 'C_rev_minus_CE_eq_pretax (CE includes interest/nonoperating)'
        elif oi is None: k = 'D_no_OI_line_and_not_pretax'
        else: k = 'E_other_items_between_CE_and_OI'
    c[k] += 1; ex[k].append(a); fam[k][family(SUB[a]['sic'])] += 1
print('filers with CostsAndExpenses on IS face', sum(c.values()))
for k in sorted(c): print(k, c[k], dict(fam[k]), ' | '.join('%s %s' % (a, SUB[a]['name'][:22]) for a in sorted(ex[k], key=lambda a: (SUB[a]['afs'], a))[:4]))
