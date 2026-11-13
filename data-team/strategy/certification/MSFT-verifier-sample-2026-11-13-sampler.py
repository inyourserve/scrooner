import csv, random, sys, collections
SRC = sys.argv[1]
rows = [r for r in csv.DictReader(open(SRC)) if r['ticker'] == 'MSFT']
BS = {'accounts_payable','accounts_receivable','cash_and_equivalents','current_assets','current_liabilities','goodwill','inventory','ppe_net','stockholders_equity','total_assets','total_debt','total_liabilities','shares_outstanding'}
CF = {'amortization_of_intangibles','capex','cash_flow_financing','cash_flow_investing','cash_paid_for_income_taxes','cash_paid_for_interest','cf_ap_change','cf_ar_change','cf_inventory_change','cfo','depreciation_and_amortization','dividends_paid','sbc','share_buybacks'}
def stmt(dp): return 'BS' if dp in BS else 'CF' if dp in CF else 'IS'
rows.sort(key=lambda r: (r['class'], stmt(r['data_point']), r['data_point'], r['fiscal_year']))
rng = random.Random(20261113)
proven = [r for r in rows if r['class'] == 'PROVEN']
reason = [r for r in rows if r['class'] == 'REASON']
rng.shuffle(proven); rng.shuffle(reason)
# PROVEN: 8 per statement (IS/BS/CF), at most 2 per fiscal year, at most 1 per data point
pick, per_stmt, per_year, dps = [], collections.Counter(), collections.Counter(), set()
for r in proven:
    s = stmt(r['data_point'])
    if per_stmt[s] < 8 and per_year[r['fiscal_year']] < 2 and r['data_point'] not in dps:
        pick.append(r); per_stmt[s] += 1; per_year[r['fiscal_year']] += 1; dps.add(r['data_point'])
# REASON: 2 per reason data point, distinct fiscal years
rp, per_dp, ry = [], collections.Counter(), set()
for r in reason:
    if per_dp[r['data_point']] < 2 and r['fiscal_year'] not in ry:
        rp.append(r); per_dp[r['data_point']] += 1; ry.add(r['fiscal_year'])
out = csv.writer(sys.stdout)
out.writerow(['n','class','stmt','data_point','fiscal_year','period_end','shown_value','accession','r_page','tag','reason_code'])
for i, r in enumerate(sorted(pick, key=lambda r:(stmt(r['data_point']), r['fiscal_year'])) + sorted(rp, key=lambda r:(r['data_point'], r['fiscal_year'])), 1):
    out.writerow([i, r['class'], stmt(r['data_point']), r['data_point'], r['fiscal_year'], r['period_end'], r['shown_value'], r['accession'], r['r_page'], r['tag'], r['reason_code']])
