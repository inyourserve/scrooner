import json,collections,csv
R=json.load(open('cls.json'))
V1={ # metric -> list of AND concept sets (all must be on face)
 'gross_margin':['revenue','cost_of_revenue'],
 'operating_margin':['operating_income','revenue'],
 'net_margin':['net_income','revenue'],
 'roe':['net_income','stockholders_equity'],
 'roic':['operating_income','income_tax_expense','income_before_tax','total_debt_resolved','stockholders_equity','cash_and_equivalents'],
 'revenue_growth(yoy,3y)':['revenue'],
 'eps_growth(yoy,3y)':['diluted_eps'],
 'fcf':['cfo','capex'],
 'fcf_margin':['cfo','capex','revenue'],
 'debt_to_equity':['total_debt_resolved','stockholders_equity'],
 'current_ratio':['current_assets','current_liabilities'],
 'interest_coverage_ratio':['operating_income','interest_expense'],
 'market_cap':['shares_outstanding'],
 'trailing_pe':['diluted_eps'],
 'price_to_sales':['revenue'],
 'price_to_book':['stockholders_equity'],
 'dividend_yield':['dividends_per_share'],
 'fcf_yield':['cfo','capex'],
}
fams=[]
byf=collections.defaultdict(list)
for k,r in R.items():
    if r['flags']: byf[r['fam']].append(r)
order=['corporate_other','pre_revenue_rd_overlay','bank_thrift','deposit_taker_nonbank_sic','nonbank_lender_credit_fintech','broker_dealer_exchange','asset_manager_adviser','insurer_underwriter','insurance_agent_broker','REIT_equity','REIT_mortgage','real_estate_operator','utility_waste','energy','MLP_partnership','commodity_crypto_pool_trust','exploration_stage_miner','BDC_fund','SPAC_blank_check','trust_holding_other_investor','no_revenue_line_other']
out=['fam,n,'+','.join(V1)]
for fam in order:
    rs=byf[fam]
    if not rs: continue
    out.append(fam+','+str(len(rs))+','+','.join(str(round(100*sum(all(r['flags'][c] for c in V1[m]) for r in rs)/len(rs))) for m in V1))
print('\n'.join(out)); open('v1presence.csv','w').write('\n'.join(out))
