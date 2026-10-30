import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
D = load(); T = json.load(open(os.path.join(OUT, 'taxo.json'))); F = D['filings']; SUB = D['sub']
def L(r): return r[6].lower()
def ex(lst, k=4): return ' | '.join('%s %s' % (a, SUB[a]['name'][:24]) for a in lst[:k])
# need full membership: recompute sets quickly by re-running taxo functions is heavy; use exec of taxo with RES
ns = {'__file__': os.path.abspath(__file__)}
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'taxo.py')).read().split("fams = ['bank'")[0]
exec(compile(src, 'taxo', 'exec'), ns)
RES = ns['RES']
def close_signed(x, y, tol=0.005): return x is not None and y is not None and abs(x - y) <= max(1.0, tol * max(abs(x), abs(y)))
# 1 RCFC smaller: face total tag
c = collections.Counter(); exs = collections.defaultdict(list)
for a in sorted(RES['rev:RCFC_and_Revenues_differ_RCFC_smaller']):
    k = 'face_total=Revenues' if a in RES['rev:tag_Revenues'] else 'face_total=RCFC' if a in RES['rev:tag_RCFC'] else 'face_other'
    c[k] += 1; exs[k].append(a)
print('1 RCFC<Revenues by face total', dict(c)); [print('   ', k, ex(v)) for k, v in exs.items()]
# 2 debt+lease tag on debt-only label: separate finance-lease line present?
c = collections.Counter(); exs = collections.defaultdict(list)
for a in sorted(RES['dt:tag_debt_plus_lease_combined_label_debt_only']):
    bs = rows(D, a, 'BS'); tags = collections.Counter(r[4] for r in bs if r[4].startswith('LongTermDebtAndCapitalLease') or 'FinanceLease' in r[4])
    fl = any(re.search(r'finance lease|capital lease', L(r)) for r in bs)
    k = 'separate_finance_lease_line' if fl else 'no_separate_finance_lease_line'
    c[k] += 1; exs[k].append(a)
print('2 debt+lease tag, debt-only label', dict(c)); [print('   ', k, ex(v)) for k, v in exs.items()]
# 3 Rev - CostsAndExpenses != OI: what is it?
PRE = ['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic']
c = collections.Counter(); exs = collections.defaultdict(list)
for a in sorted(RES['oi:CostsAndExpenses_rev_minus_NOT_OI']):
    rs = rows(D, a, 'IS'); rv = None
    for r in rs:
        if r[4] in ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax') and val(D, a, r[4], r[5], 'IS') is not None: rv = val(D, a, r[4], r[5], 'IS')
    ce = anyval(D, a, 'CostsAndExpenses'); pt = None
    for r in rs:
        if r[4] in PRE or re.search(r'before (income )?tax', L(r)):
            pt = val(D, a, r[4], r[5], 'IS'); break
    k = 'equals_pretax' if rv is not None and pt is not None and close_signed(rv - ce, pt) else 'other_(gains/other operating items outside total)'
    c[k] += 1; exs[k].append(a)
print('3 Rev-CE != OI', dict(c)); [print('   ', k, ex(v)) for k, v in exs.items()]
# 4 BS cash tagged with restricted-total tag but label lacks restricted
l4 = [a for a in sorted(RES['ca:tag:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents']) if not any('restricted' in L(r) for r in rows(D, a, 'BS') if r[4] == 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents')]
print('4 BS restricted-total tag with label lacking "restricted"', len(l4), 'of', len(RES['ca:tag:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents']), ex(l4))
# 6 dimension-only IS rows (generic tag + member)
c6 = []
for a in F:
    rs = rows(D, a, 'IS')
    if any(val(D, a, r[4], r[5], 'IS') is None and dimonly(D, a, r[4]) for r in rs): c6.append(a)
print('6 filers with >=1 IS face row that has only dimensioned FY values', len(c6), ex(sorted(c6)))
# 7 custom share of face lines
tot = collections.Counter(); cus = collections.Counter(); fc = collections.Counter()
for a in F:
    for st in ('IS', 'BS', 'CF'):
        rs = rows(D, a, st); tot[st] += len(rs); n = sum(1 for r in rs if is_custom(D, r[4], r[5])); cus[st] += n
        if n: fc[st] += 1
print('7 custom face lines', {s: '%d/%d=%.1f%%, filers with any %d' % (cus[s], tot[s], 100 * cus[s] / tot[s], fc[s]) for s in tot})
# 8 ProfitLoss-only: NCI present?
c = collections.Counter()
for a in RES['ni:ProfitLoss_only_no_NetIncomeLoss_face']:
    nci = anyval(D, a, 'NetIncomeLossAttributableToNoncontrollingInterest')
    c['nci_nonzero' if nci not in (None, 0.0) else 'no_nci'] += 1
print('8 ProfitLoss-only', dict(c))
# 9 gross interest tag on net label: does filer also put interest income on face?
c = collections.Counter()
for a in RES['ix:label_shift_gross_tag_on_net_line']:
    rs = rows(D, a, 'IS')
    c['separate_interest_income_row' if any(re.search(r'interest income|interest and other income|investment income', L(r)) and 'expense' not in L(r) for r in rs) else 'no_interest_income_row'] += 1
print('9 gross tag on net line', dict(c))
# 10 3M-style: NCI row but no ProfitLoss: what tag is the consolidated line?
for a in sorted(RES['ni:NCI_row_but_no_ProfitLoss_tag_consolidated_line_custom_or_missing'])[:5]:
    print('10', a, SUB[a]['name'], [(r[4][:50], r[6][:40], is_custom(D, r[4], r[5])) for r in rows(D, a, 'IS') if re.search(r'net (income|earnings|loss)', L(r)) and 'per' not in L(r)][:4])
