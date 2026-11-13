"""MSFT certification re-sample, seed 20261114. usage: python3 sampler.py top100-coverage.csv > draw.csv
Draw: 32 cells = 26 PROVEN + 6 REASON.
  Risk stratum (forced, not random): revenue / operating_expenses / gross_profit FY2016-FY2017 (6 PROVEN cells).
  Random PROVEN (20): rows sorted, shuffled with random.Random(20261114); greedy take IS 6 / BS 7 / CF 7,
    at most 2 per fiscal year (counting the forced cells), at most 1 per data point, forced data points excluded.
  Random REASON (6): same generator, shuffled after PROVEN; 2 per reason data point, distinct fiscal years.
"""
import csv, random, sys, collections
SRC = sys.argv[1]
rows = [r for r in csv.DictReader(open(SRC)) if r['ticker'] == 'MSFT']
BS = {'accounts_payable','accounts_receivable','cash_and_equivalents','current_assets','current_liabilities','goodwill','inventory','ppe_net','stockholders_equity','total_assets','total_debt','total_liabilities','shares_outstanding'}
CF = {'amortization_of_intangibles','capex','cash_flow_financing','cash_flow_investing','cash_paid_for_income_taxes','cash_paid_for_interest','cf_ap_change','cf_ar_change','cf_inventory_change','cfo','depreciation_and_amortization','dividends_paid','sbc','share_buybacks'}
def stmt(dp): return 'BS' if dp in BS else 'CF' if dp in CF else 'IS'
RISK_DP = {'revenue','operating_expenses','gross_profit'}; RISK_FY = {'2016','2017'}
rows.sort(key=lambda r: (r['class'], stmt(r['data_point']), r['data_point'], r['fiscal_year']))
forced = [r for r in rows if r['class'] == 'PROVEN' and r['data_point'] in RISK_DP and r['fiscal_year'] in RISK_FY]
assert len(forced) == 6, len(forced)
rng = random.Random(20261114)
proven = [r for r in rows if r['class'] == 'PROVEN' and r['data_point'] not in RISK_DP]
reason = [r for r in rows if r['class'] == 'REASON']
rng.shuffle(proven); rng.shuffle(reason)
QUOTA = {'IS': 6, 'BS': 7, 'CF': 7}
pick, per_stmt, per_year, dps = [], collections.Counter(), collections.Counter(r['fiscal_year'] for r in forced), set()
for r in proven:
    s = stmt(r['data_point'])
    if per_stmt[s] < QUOTA[s] and per_year[r['fiscal_year']] < 2 and r['data_point'] not in dps:
        pick.append(r); per_stmt[s] += 1; per_year[r['fiscal_year']] += 1; dps.add(r['data_point'])
assert len(pick) == 20, len(pick)
rp, per_dp, ry = [], collections.Counter(), set()
for r in reason:
    if per_dp[r['data_point']] < 2 and r['fiscal_year'] not in ry:
        rp.append(r); per_dp[r['data_point']] += 1; ry.add(r['fiscal_year'])
assert len(rp) == 6, len(rp)
out = csv.writer(sys.stdout)
out.writerow(['n','stratum','class','stmt','data_point','fiscal_year','period_end','shown_value','accession','r_page','tag','reason_code'])
seq = [('risk', r) for r in forced] + [('random', r) for r in sorted(pick, key=lambda r: (stmt(r['data_point']), r['fiscal_year']))] \
    + [('random', r) for r in sorted(rp, key=lambda r: (r['data_point'], r['fiscal_year']))]
for i, (st, r) in enumerate(seq, 1):
    out.writerow([i, st, r['class'], stmt(r['data_point']), r['data_point'], r['fiscal_year'], r['period_end'], r['shown_value'], r['accession'], r['r_page'], r['tag'], r['reason_code']])
