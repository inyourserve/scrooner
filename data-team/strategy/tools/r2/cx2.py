import sys, os, re, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
ns = {'__file__': os.path.abspath(__file__)}
exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'taxo.py')).read().split("RES = collections")[0], 't', 'exec'), ns)
D = ns['D']; SUB = ns['SUB']; F = ns['F']
def L(r): return r[6].lower()
# capex: PPE tag present + other capex lines
res = []; ex = []
for a in F:
    cf = rows(D, a, 'CF')
    i0 = next((i for i, r in enumerate(cf) if r[4].startswith('NetCashProvidedByUsedInOperatingActivities')), None)
    i1 = next((i for i, r in enumerate(cf) if r[4].startswith('NetCashProvidedByUsedInInvestingActivities')), None)
    if i0 is not None and i1 is not None and i1 > i0: cf = cf[i0 + 1:i1]
    cr = [r for r in cf if ns['CAPRE'].search(L(r)) and not re.search(r'proceeds|sale|disposal|accrued|unpaid|non-?cash|included in|accounts payable|financed|supplemental|lease', L(r)) and not r[4].startswith(('Repayment','CapitalExpendituresIncurred','Noncash','CapitalizedComputerSoftwareAmort','CapitalizedComputerSoftwareImp'))]
    ppe = [r for r in cr if r[4] == 'PaymentsToAcquirePropertyPlantAndEquipment']
    oth = [r for r in cr if r[4] != 'PaymentsToAcquirePropertyPlantAndEquipment']
    if ppe and oth:
        pv = val(D, a, ppe[0][4], ppe[0][5], 'CF'); ov = sum(abs(val(D, a, r[4], r[5], 'CF') or 0) for r in oth)
        if pv: res.append(ov / abs(pv)); ex.append((ov / abs(pv), a, SUB[a]['name'][:24], [r[6][:35] for r in oth][:2]))
print('filers with PaymentsToAcquirePPE plus other capex lines', len(res))
for th in (0.01, 0.05, 0.10, 0.5):
    print('  other lines >= %d%% of PPE line: %d' % (th * 100, sum(1 for x in res if x >= th)))
print('  median ratio %.3f' % statistics.median(res))
for e in sorted(ex, reverse=True)[:3] + sorted(ex)[len(ex)//2:len(ex)//2+2]: print('  ', '%.2f' % e[0], e[1], e[2], e[3])
# D&A: split with a combined tag: other lines share
res = []; ex = []
for a in F:
    cf = rows(D, a, 'CF'); op = []
    for r in cf:
        if r[4].startswith('NetCashProvidedByUsedInOperatingActivities'): break
        op.append(r)
    da = [r for r in op if ns['DARE'].search(L(r)) and not ns['DAEX'].search(L(r))]
    comb = [r for r in da if r[4] in ns['DA1']]; oth = [r for r in da if r[4] not in ns['DA1']]
    if comb and oth:
        cv = val(D, a, comb[0][4], comb[0][5], 'CF'); ov = sum(abs(val(D, a, r[4], r[5], 'CF') or 0) for r in oth)
        if cv: res.append(ov / abs(cv)); ex.append((ov / abs(cv), a, SUB[a]['name'][:24], [(r[4][:40], r[6][:35]) for r in oth][:2]))
print('filers with combined D&A tag plus other D&A lines', len(res))
for th in (0.01, 0.05, 0.10, 0.5):
    print('  other lines >= %d%% of combined line: %d' % (th * 100, sum(1 for x in res if x >= th)))
print('  median ratio %.3f' % statistics.median(res))
for e in sorted(ex, reverse=True)[:3] + sorted(ex)[len(ex)//2:len(ex)//2+2]: print('  ', '%.2f' % e[0], e[1], e[2], e[3])
