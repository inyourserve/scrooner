# Dependency graph, extracted from mapper code + live analytics.metric_definition_input (2026-10-21).
# node -> dict(kind, module, basis, inputs=[(node,role)], note)
G={}
def add(name,kind,module,basis,inputs=(),note=''):
    G[name]=dict(kind=kind,module=module,basis=basis,inputs=list(inputs),note=note)

# ---- leaf concepts (XBRL tags -> canonical_fact via resolve.py first_match/sum) ----
LEAF_IS=['revenue','cost_of_revenue','gross_profit','operating_expenses','operating_income','research_and_development','sga_expense',
 'interest_income','interest_expense','income_before_tax','income_tax_expense','net_income','basic_eps','diluted_eps','sbc',
 'depreciation_and_amortization','amortization_of_intangibles','other_income_expense_net','comprehensive_income','effective_tax_rate_reported']
LEAF_BS=['cash_and_equivalents','accounts_receivable','inventory','current_assets','ppe_net','goodwill','total_assets','accounts_payable','current_liabilities',
 'total_liabilities','stockholders_equity','shares_outstanding','public_float','employee_count']
LEAF_CF=['cfo','capex','cash_flow_investing','cash_flow_financing','dividends_paid','dividends_per_share','share_buybacks','cf_ar_change','cf_inventory_change','cf_ap_change']
LEAF_SECTOR=['bdc_total_investment_income','collaborative_arrangement_revenue','net_lease_revenue']
for n in LEAF_IS+LEAF_BS+LEAF_CF+LEAF_SECTOR:
    basis='instant' if n in LEAF_BS else 'duration'
    add(n,'leaf_concept','resolve.py (concept_mapping tags)',basis,[],'XBRL tag(s) via concept_mapping; first_match')
add('total_debt','leaf_concept','resolve.py','instant',[],'sum mode over debt tags')
add('total_debt_split','leaf_concept','resolve.py','instant',[],'sum of LongTermDebtCurrent+Noncurrent')
# ---- resolved / derived concepts ----
for base in ['cash_and_equivalents','current_assets','current_liabilities','ppe_net','total_assets','total_liabilities','stockholders_equity','shares_outstanding',
 'income_before_tax','income_tax_expense','interest_expense','net_income','basic_eps','diluted_eps','cfo','cash_flow_investing','cash_flow_financing',
 'dividends_paid','dividends_per_share','share_buybacks','employee_count']:
    add(base+'_resolved','resolved_concept','conflict_resolution.py / dedup_majority_resolver.py',G[base]['basis'],[(base,'base')],'base concept plus conflict-filled periods (superset)')
add('revenue_sanity_resolved','resolved_concept','conflict_resolution.py','duration',[('revenue','base')],'revenue plus conflict-fill and sanity filter')
add('capex_resolved','resolved_concept','concept_fallback.py','duration',[('capex','base')],'capex + PaymentsToAcquireSoftware (only where capex exists)')
add('depreciation_and_amortization_resolved','resolved_concept','concept_fallback.py','duration',[('depreciation_and_amortization','base')],'max of DepreciationAndAmortization / DepreciationDepletionAndAmortization')
add('total_debt_resolved','derived_concept','concept_fallback.py resolve_total_debt_components','instant',[('total_debt','alt'),('total_debt_split','alt')],'component-based debt: all-in tag, else summed components; OR over alternatives')
add('gross_profit_resolved','derived_concept','concept_fallback.py ARITHMETIC_FALLBACKS','duration',[('gross_profit','alt'),('revenue','alt_derive'),('cost_of_revenue_resolved','alt_derive')],'gross_profit, else revenue - cost_of_revenue_resolved (revenue>0)')
add('cost_of_revenue_resolved','derived_concept','concept_fallback.py ARITHMETIC_FALLBACKS','duration',[('cost_of_revenue','alt'),('revenue','alt_derive'),('gross_profit','alt_derive')],'cost_of_revenue (or rendered-report dimensional sum), else revenue - gross_profit')
add('operating_expenses_resolved','derived_concept','concept_fallback.py ARITHMETIC_FALLBACKS','duration',[('operating_expenses','alt'),('gross_profit_resolved','alt_derive'),('operating_income','alt_derive')],'operating_expenses, else gross_profit_resolved - operating_income')
add('operating_income_resolved','derived_concept','conflict_resolution.py derive_operating_income','duration',[('operating_income','alt'),('revenue','alt_derive'),('operating_expenses','alt_derive')],'operating_income (+conflict-fill), else revenue - opex - ...')
# ---- engine metrics (calculate.py; inputs mirror analytics.metric_definition_input) ----
def eng(name,inputs,shape,basis='per period',note=''):
    add(name,'metric','calculate.py ('+shape+')',basis,inputs,note)
eng('gross_margin',[('revenue','add'),('cost_of_revenue','subtract'),('revenue','denominator')],'sum_diff_ratio',note='quarterly/FY engine; TTM variant in ttm.py reads gross_profit_resolved / revenue_sanity_resolved')
eng('operating_margin',[('operating_income','numerator'),('revenue','denominator')],'ratio',note='TTM variant (ttm.py) reads operating_income_resolved / revenue_sanity_resolved')
eng('net_margin',[('net_income','numerator'),('revenue','denominator')],'ratio',note='TTM variant (ttm.py) reads net_income_resolved / revenue_sanity_resolved')
eng('pretax_margin',[('income_before_tax','numerator'),('revenue','denominator')],'ratio')
eng('roe',[('net_income','numerator'),('stockholders_equity','denominator')],'ratio','FY + TTM (ttm.py)')
eng('roa',[('net_income','numerator'),('total_assets','denominator')],'ratio','FY + TTM (ttm.py)')
eng('roic',[('operating_income','nopat_base'),('income_tax_expense','tax_rate_numerator'),('income_before_tax','tax_rate_denominator'),('total_debt_resolved','invested_capital_add'),('stockholders_equity','invested_capital_add'),('cash_and_equivalents','invested_capital_subtract')],'roic','FY + TTM (ttm.py)')
eng('fcf',[('cfo','add'),('capex','subtract')],'sum_diff')
eng('fcf_margin',[('cfo','add'),('capex','subtract'),('revenue','denominator')],'sum_diff_ratio')
eng('debt_to_equity',[('total_debt_resolved','numerator'),('stockholders_equity','denominator')],'ratio')
eng('current_ratio',[('current_assets','numerator'),('current_liabilities','denominator')],'ratio')
eng('quick_ratio',[('current_assets','add'),('inventory','subtract'),('current_liabilities','denominator')],'sum_diff_ratio',note='inventory is zero-when-absent (ZERO_WHEN_ABSENT_CONCEPTS)')
eng('interest_coverage_ratio',[('operating_income','numerator'),('interest_expense','denominator')],'ratio')
eng('sbc_pct_revenue',[('sbc','numerator'),('revenue','denominator')],'ratio')
eng('ebitda',[('operating_income_resolved','add'),('depreciation_and_amortization_resolved','add')],'additive','quarterly rows + persisted TTM row (expanded_metrics.py: 4 consecutive quarters, <=150 days old)')
eng('debtor_days',[('accounts_receivable','numerator'),('revenue','denominator')],'days','FY only')
eng('inventory_days',[('inventory','numerator'),('cost_of_revenue','denominator')],'days','FY only')
eng('payables_days',[('accounts_payable','numerator'),('cost_of_revenue','denominator')],'days','FY only')
eng('goodwill_pct_assets',[('goodwill','numerator'),('total_assets','denominator')],'ratio')
eng('eps_dilution_spread',[('basic_eps','add'),('diluted_eps','subtract'),('basic_eps','denominator')],'sum_diff_ratio')
eng('rnd_intensity',[('research_and_development','numerator'),('revenue','denominator')],'ratio')
eng('net_interest_income',[('interest_income','add'),('interest_expense','subtract')],'sum_diff')
eng('capex_pct_revenue',[('capex','numerator'),('revenue','denominator')],'ratio')
eng('sga_pct_revenue',[('sga_expense','numerator'),('revenue','denominator')],'ratio')
eng('payout_ratio',[('dividends_per_share','numerator'),('diluted_eps','denominator')],'ratio')
eng('net_cash',[('cash_and_equivalents','add'),('total_debt_resolved','subtract')],'sum_diff')
eng('net_cash_per_share',[('cash_and_equivalents','add'),('total_debt_resolved','subtract'),('shares_outstanding','denominator')],'sum_diff_ratio')
eng('book_value_per_share',[('stockholders_equity','numerator'),('shares_outstanding','denominator')],'ratio')
eng('working_capital',[('current_assets','add'),('current_liabilities','subtract')],'sum_diff')
eng('net_change_in_cash',[('cfo','add'),('cash_flow_investing','add'),('cash_flow_financing','add')],'additive')
eng('ocf_to_net_income',[('cfo','numerator'),('net_income','denominator')],'ratio')
eng('cash_returned_to_shareholders',[('dividends_paid','add'),('share_buybacks','add')],'additive')
# ---- growth (ttm.py GROWTH_METRICS): input concept at t and t-lag; prior_period missing => H1 ----
for m,(c,l) in {'revenue_growth_yoy':('revenue',1),'revenue_growth_3y_cagr':('revenue',3),'revenue_growth_5y_cagr':('revenue',5),'revenue_growth_10y_cagr':('revenue',10),
 'eps_growth_yoy':('diluted_eps',1),'eps_growth_3y_cagr':('diluted_eps',3),'eps_growth_5y_cagr':('diluted_eps',5),'eps_growth_10y_cagr':('diluted_eps',10),
 'dps_growth_yoy':('dividends_per_share',1),'dps_growth_3y_cagr':('dividends_per_share',3),
 'net_income_growth_yoy':('net_income',1),'net_income_growth_3y_cagr':('net_income',3),'net_income_growth_5y_cagr':('net_income',5),'net_income_growth_10y_cagr':('net_income',10),
 'diluted_shares_growth_yoy':('shares_outstanding',1),'diluted_shares_growth_3y_cagr':('shares_outstanding',3),'diluted_shares_growth_5y_cagr':('shares_outstanding',5)}.items():
    add(m,'metric','ttm.py GROWTH_METRICS','FY t vs FY t-%d'%l,[(c,'base_t'),(c,'base_t_minus_%d'%l)],'prior-period missing => reason missing:prior_period(..); negative/zero base => null by rule')
for m,l in {'fcf_growth_yoy':1,'fcf_growth_3y_cagr':3,'fcf_growth_5y_cagr':5}.items():
    add(m,'metric','fcf_growth.py','FY t vs FY t-%d'%l,[('fcf','base_t'),('fcf','base_t_minus_%d'%l)],'reads the fcf METRIC FY rows (metric of metric)')
# ---- TTM / expanded (expanded_metrics.py) ----
def ex(name,inputs,note='',kind='metric',module='expanded_metrics.py',basis='TTM'):
    add(name,kind,module,basis,inputs,note)
ex('net_debt_ebitda',[('total_debt_resolved','numerator'),('cash_and_equivalents','numerator'),('ebitda','ttm_denominator')])
ex('debt_to_ebitda',[('total_debt_resolved','numerator'),('ebitda','ttm_denominator')])
ex('ebitda_margin',[('ebitda','ttm_numerator'),('revenue','ttm_denominator')])
ex('fcf_per_share',[('fcf','ttm_numerator'),('shares_outstanding','denominator')],'fcf TTM = sum of 4 quarterly fcf metric rows')
ex('share_repurchases_pct_fcf',[('share_buybacks','ttm_numerator'),('fcf','ttm_denominator')])
ex('dividends_pct_fcf',[('dividends_paid','ttm_numerator'),('fcf','ttm_denominator')])
ex('cash_conversion_cycle',[('debtor_days','add'),('inventory_days','add'),('payables_days','subtract')],'metric of metrics, FY')
ex('institutional_ownership_pct',[('institutional_ownership','source'),('shares_outstanding','denominator')],basis='latest')
ex('share_dilution_trend',[('shares_outstanding','now'),('shares_outstanding','one_year_ago')],basis='latest vs ~1y ago')
ex('ev_ebitda',[('market_cap','ev_base'),('total_debt_resolved','add'),('cash_and_equivalents','subtract'),('ebitda','ttm_denominator')])
ex('ev_sales',[('market_cap','ev_base'),('total_debt_resolved','add'),('cash_and_equivalents','subtract'),('revenue','ttm_denominator')])
ex('peg_ratio',[('trailing_pe','numerator'),('eps_growth_yoy','denominator')])
ex('buyback_yield',[('share_buybacks','ttm_numerator'),('market_cap','denominator')])
ex('total_shareholder_yield',[('dividends_paid','ttm_optional'),('share_buybacks','ttm_optional'),('market_cap','denominator'),('shares_outstanding','now'),('shares_outstanding','one_year_ago')],'missing dividends/buybacks default to 0 here; blank only if market_cap or 1y-ago shares missing')
# ---- price metrics (price_metrics.py) ----
add('market_cap','price_metric','price_metrics.py','latest',[('shares_outstanding','multiplicand'),('price','multiplier')],'shares_outstanding (fallback diluted weighted shares, cover-page) x Alpaca price (core.market_price_alpaca)')
add('trailing_pe','price_metric','price_metrics.py','TTM',[('diluted_eps','ttm_denominator'),('price','numerator')],'else market_cap / TTM net income')
add('price_to_sales','price_metric','price_metrics.py','TTM',[('market_cap','numerator'),('revenue','ttm_denominator')])
add('price_to_book','price_metric','price_metrics.py','latest',[('market_cap','numerator'),('stockholders_equity','denominator')])
add('dividend_yield','price_metric','price_metrics.py','TTM',[('dividends_per_share','ttm_numerator'),('price','denominator')])
add('fcf_yield','price_metric','price_metrics.py','TTM',[('cfo','ttm_add'),('capex','ttm_subtract'),('market_cap','denominator')])
add('price','external_source','core.market_price_alpaca','daily',[],'Alpaca delayed_sip bars; not a canonical concept')
# ---- quality / reconciliation ----
add('piotroski_f_score','metric','quality_score.py','FY t and FY t-1',[(c,'req') for c in ['net_income','cfo','total_assets','current_assets','current_liabilities','revenue','gross_profit_resolved','total_debt_resolved','shares_outstanding']],'all 9 inputs x 2 years required; gross_profit falls back to revenue - cost_of_revenue')
add('fcf_gt_net_income','metric','quality_flags.py','FY',[('cfo','req'),('capex','req'),('net_income','req')])
add('zero_debt','metric','quality_flags.py','FY',[('total_debt_resolved','req')],'null (not 0) when debt not reported')
add('profitable_streak_years','metric','quality_flags.py','latest FY',[('net_income','req')])
add('margin_expanding_3yr','metric','quality_flags.py','3 consecutive FY',[('gross_profit','req'),('revenue','req')],'needs gross margin for 3 consecutive FY')
add('dividend_growth_streak_years','metric','dividend_streak.py','latest FY',[('dividends_per_share','req')],'null reason no_dividend_history when no DPS ever')
add('effective_tax_rate_gap','metric','tax_reconciliation.py','FY',[('effective_tax_rate_reported','req'),('income_tax_expense','req'),('income_before_tax','req')])
add('ar_change_reconciliation_gap','metric','reconciliation.py','FY t, t-1',[('accounts_receivable','req'),('cf_ar_change','req')])
add('inventory_change_reconciliation_gap','metric','reconciliation.py','FY t, t-1',[('inventory','req'),('cf_inventory_change','req')])
add('ap_change_reconciliation_gap','metric','reconciliation.py','FY t, t-1',[('accounts_payable','req'),('cf_ap_change','req')])
# ---- ownership sources ----
add('institutional_ownership','external_source','core.institutional_ownership (Form 13F)','latest window',[],'')
add('insider_ownership','external_source','core.insider_ownership_summary (Form 4)','12 months',[],'')
add('mutual_fund_ownership','external_source','core.fund_ownership_summary (N-PORT)','2 periods',[],'')
