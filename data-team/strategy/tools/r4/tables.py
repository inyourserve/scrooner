import json,collections
R=json.load(open('cls.json'))
C33=['accounts_payable','accounts_receivable','basic_eps','capex','cash_and_equivalents','cash_flow_financing','cash_flow_investing','cfo','cost_of_revenue','current_assets','current_liabilities','depreciation_and_amortization_resolved','diluted_eps','dividends_paid','dividends_per_share','goodwill','income_before_tax','income_tax_expense','interest_expense','interest_income','inventory','net_income','operating_income','research_and_development','revenue','sbc','sga_expense','share_buybacks','shares_outstanding','stockholders_equity','total_assets','total_debt_resolved']
# operating_income_resolved is derived from operating_income; keep 33rd = operating_income_resolved ~ operating_income
byf=collections.defaultdict(list)
for r in R.values():
    if r['flags']: byf[r['fam']].append(r)
order=sorted(byf,key=lambda f:-len(byf[f]))
print('concept,'+','.join(f"{f}({len(byf[f])})" for f in order))
for c in C33:
    print(c+','+','.join(str(round(100*sum(r['flags'][c] for r in byf[f])/len(byf[f]))) for f in order))
