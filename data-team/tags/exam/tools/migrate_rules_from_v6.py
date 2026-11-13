"""One-time migration (2026-11-13): knowledge in predict.py v6 + library CSVs -> data-team/tags/rules/<namespace>.csv.
Usage: make_rules.py LIBRARY_DIR OUT_RULES_DIR"""
import csv, json, sys, os, re
lib_dir, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
COLS = ['rule_id', 'version', 'namespace', 'data_point', 'scope', 'era', 'kind', 'when', 'then', 'precedence', 'evidence', 'author', 'date', 'note']
DATE = '2026-11-13'
STMTS = {'BS': {'accounts_payable','accounts_receivable','cash_and_equivalents','current_assets','current_liabilities','goodwill','inventory','ppe_net','shares_outstanding','stockholders_equity','total_assets','total_debt','total_liabilities','deposits','loans_net'},
         'CF': {'capex','cash_flow_financing','cash_flow_investing','cfo','cf_ap_change','cf_ar_change','cf_inventory_change','depreciation_and_amortization','dividends_paid','sbc','share_buybacks','cash_paid_for_interest','cash_paid_for_income_taxes'}}
NOTES = {'cash_paid_for_income_taxes','cash_paid_for_interest','amortization_of_intangibles','interest_income','weighted_basic_shares','weighted_diluted_shares','dividends_per_share'}
PER_SHARE = {'basic_eps','diluted_eps','dividends_per_share','shares_outstanding','weighted_basic_shares','weighted_diluted_shares'}
BANKDP = {'deposits','loans_net','net_interest_income','noninterest_income','noninterest_expense','provision_for_credit_losses','total_interest_income'}
def dp_of(c):
    c = (c or '').strip(); c = {'revenue_sanity_resolved': 'revenue'}.get(c, c)
    return c[:-9] if c.endswith('_resolved') else c
def ns_of(dp, stmt=''):
    if dp in BANKDP: return 'bank'
    if dp in PER_SHARE: return 'per_share'
    if dp in NOTES: return 'notes'
    if dp in STMTS['BS']: return 'bs'
    if dp in STMTS['CF']: return 'cf'
    if dp: return 'is'
    return {'BS': 'bs', 'CF': 'cf'}.get(stmt, 'is')
R = {}
def add(ns, rid, dp, scope, kind, when, then, prec, ev, author='Tag Expert', note=''):
    R.setdefault(ns, []).append(dict(rule_id=rid, version=1, namespace=ns, data_point=dp, scope=scope, era='', kind=kind,
        when=json.dumps(when, separators=(',', ':')), then=json.dumps(then, separators=(',', ':')), precedence=prec, evidence=ev, author=author, date=DATE, note=note))
# 1. library tag rows (file order kept: engine keeps the first match per (stmt, tag) like the dict did)
for i, r in enumerate(csv.DictReader(open(f'{lib_dir}/standard-tag-library.csv'))):
    dp = dp_of(r['concept']) or dp_of(r['parent_concept'])
    add(ns_of(dp, r['stmt']), f"lib.{r['stmt'].lower()}.{r['tag']}", dp, 'all', 'tag',
        {'stmt': r['stmt'], 'tag': r['tag'], 'order': i},
        {'decision': r['decision'], 'concept': r['concept'], 'parent_concept': r['parent_concept'], 'reason_class': r['reason_class']},
        'data point', r['evidence'] or r['source'], note=(r['caveat'] or '')[:300])
# 2. company overrides
for i, r in enumerate(csv.DictReader(open(f'{lib_dir}/company-overrides.csv'))):
    add('company', f"company.{r['company']}.{re.sub(r'[^A-Za-z0-9]', '', r['tag'])}", dp_of(r['concept']) if not r['concept'].startswith('(') else '', r['company'], 'override',
        {'cik': r['cik'], 'tag': r['tag'], 'stmt': r['stmt'], 'order': i}, {'concept': r['concept'], 'status': r['status'], 'value_source': r.get('value_source', '')},
        'company', r['evidence'], note=r['note'])
# 3. combined-line concepts (needs-detail answers; first occurrence per tag wins, like setdefault)
seen = set()
for i, r in enumerate(csv.DictReader(open(f'{lib_dir}/needs-detail-answers-r1r2.csv'))):
    if r['tag'] in seen: continue
    seen.add(r['tag']); dp = dp_of(r['concept'])
    add(ns_of(dp), f"nd.{r['tag']}", dp, 'all', 'combined_concept', {'tag': r['tag'], 'order': i}, {'data_point': dp, 'members': r.get('members', '')},
        'data point', 'needs-detail-answers-r1r2.csv (' + r['source'] + ')')
# 4. knowledge that lived in predict.py v6 (literals copied verbatim)
DPS = ['accounts_payable','accounts_receivable','amortization_of_intangibles','basic_eps','capex','cash_and_equivalents','cash_flow_financing',
 'cash_flow_investing','cash_paid_for_income_taxes','cash_paid_for_interest','cf_ap_change','cf_ar_change','cf_inventory_change','cfo',
 'comprehensive_income','cost_of_revenue','current_assets','current_liabilities','deposits','depreciation_and_amortization','diluted_eps',
 'dividends_paid','dividends_per_share','goodwill','gross_profit','income_before_tax','income_tax_expense','interest_expense','interest_income',
 'inventory','loans_net','net_income','net_interest_income','noninterest_expense','noninterest_income','operating_expenses','operating_income',
 'other_income_expense_net','ppe_net','provision_for_credit_losses','research_and_development','revenue','sbc','sga_expense','share_buybacks',
 'shares_outstanding','stockholders_equity','total_assets','total_debt','total_interest_income','total_liabilities','weighted_basic_shares',
 'weighted_diluted_shares']
for i, dp in enumerate(DPS):
    add(ns_of(dp), f'template.{dp}', dp, 'all', 'data_point', {'order': i}, {'home_stmt': 'BS' if dp in STMTS['BS'] else 'CF' if dp in STMTS['CF'] else 'IS'}, 'default', 'docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv)')
BANK = {'deposits':['Deposits'],'loans_net':['LoansAndLeasesReceivableNetReportedAmount','LoansAndLeasesReceivableNetOfDeferredIncome','FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss'],
 'net_interest_income':['InterestIncomeExpenseNet'],'noninterest_income':['NoninterestIncome'],'noninterest_expense':['NoninterestExpense'],
 'provision_for_credit_losses':['ProvisionForLoanLeaseAndOtherLosses','ProvisionForLoanAndLeaseLosses','ProvisionForCreditLossesNet','ProvisionForLoanLossesExpensed'],
 'total_interest_income':['InterestAndDividendIncomeOperating']}
for dp, tags in BANK.items():
    add('bank', f'bank.{dp}.tags', dp, 'bank', 'bank_tag', {'tags': tags}, {'status': 'mapped'}, 'template', 'sector-faces.md; bank template')
NOTE = {'cash_paid_for_income_taxes':'IncomeTaxesPaidNet','cash_paid_for_interest':'InterestPaidNet','amortization_of_intangibles':'AmortizationOfIntangibleAssets',
 'interest_income':'InvestmentIncomeInterest','weighted_basic_shares':'WeightedAverageNumberOfSharesOutstandingBasic','weighted_diluted_shares':'WeightedAverageNumberOfDilutedSharesOutstanding',
 'dividends_per_share':'CommonStockDividendsPerShareDeclared','sbc':'ShareBasedCompensation'}
NODEF = {'dividends_per_share', 'interest_income', 'sbc'}
for dp, t in NOTE.items():
    add(ns_of(dp), f'notes.{dp}.default_tag', dp, 'all', 'note_default', {'no_face_line': True, 'no_note_facts_input': True}, {'tag': t, 'status': 'mapped', 'disabled_when_no_face': dp in NODEF}, 'default', 'dev-set majority (exam README v2/v3)')
NOTE_RULES = {
 'interest_income': [('InvestmentIncomeInterest', 'mapped'), ('InterestIncomeOther', 'component_in_note'), ('InvestmentIncomeInterestAndDividend', 'combined')],
 'amortization_of_intangibles': [('AmortizationOfIntangibleAssets', 'mapped'), ('AdjustmentForAmortization', 'mapped')],
 'cash_paid_for_income_taxes': [('IncomeTaxesPaidNet', 'mapped'), ('IncomeTaxesPaid', 'mapped')],
 'cash_paid_for_interest': [('InterestPaidNet', 'mapped'), ('InterestPaid', 'mapped')],
 'sbc': [('ShareBasedCompensation', 'mapped'), ('AllocatedShareBasedCompensationExpense', 'mapped')],
 'dividends_per_share': [('CommonStockDividendsPerShareDeclared', 'mapped'), ('CommonStockDividendsPerShareCashPaid', 'mapped')],
 'weighted_basic_shares': [('WeightedAverageNumberOfSharesOutstandingBasic', 'mapped'), ('WeightedAverageNumberOfShareOutstandingBasicAndDiluted', 'mapped')],
 'weighted_diluted_shares': [('WeightedAverageNumberOfDilutedSharesOutstanding', 'mapped'), ('WeightedAverageNumberOfShareOutstandingBasicAndDiluted', 'mapped')]}
EVN = {'cash_paid_for_interest': 'DQC_0065; Dhairya note convention 2026-11-12', 'cash_paid_for_income_taxes': 'FASB Income Taxes TIG v1.0 2025-02; Dhairya note convention 2026-11-12'}
for dp, lst in NOTE_RULES.items():
    for k, (t, st) in enumerate(lst):
        add('notes', f'notes.{dp}.fact.{t}', dp, 'all', 'note_fact', {'tag': t, 'rank': k}, {'status': st}, 'data point', EVN.get(dp, 'Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB)'))
for dp in ['cost_of_revenue','operating_expenses','sga_expense','interest_expense','capex','depreciation_and_amortization','research_and_development','revenue','income_tax_expense','total_debt']:
    add(ns_of(dp), f'{ns_of(dp)}.{dp}.duration_sum', dp, 'all', 'sum_allowed', {}, {'sum': True}, 'data point', 'Dhairya ruling (a) 2026-11-12 (durations); total_debt founder doc 02 2026-11-04 item 5')
DEMOTE = {
 'interest_expense': r'(?i)(,\s*net\b|net of interest income|and other|interest and other)(?!.*capitaliz)',
 'revenue': r'(?i)and other income',
 'depreciation_and_amortization': r'(?i)impair|accretion|nuclear|and other|gain|loss',
 'share_buybacks': r'(?i)excise|withh|warrant|units|and other|preferred',
 'dividends_paid': r'(?i)preferred|equivalent|units|and other',
 'capex': r'(?i)acquisitions? of (?:business|compan|restaurant)|businesses|and investments|net of (?:proceeds|disposals)',
 'accounts_receivable': r'(?i)and other|notes|other receivable',
 'accounts_payable': r'(?i)accrued|and other',
 'cash_and_equivalents': r'(?i)restricted',
 'goodwill': r'(?i)intangible',
 'other_income_expense_net': r'(?i)interest',
 'cf_ap_change': r'(?i)\band\b|other', 'cf_ar_change': r'(?i)\band\b|other', 'cf_inventory_change': r'(?i)\band\b|other'}
DEV = {'interest_expense': 'interest card; Dhairya SPGI caption ruling 2026-11-12', 'depreciation_and_amortization': 'Dhairya DUK ruling 2026-11-12', 'share_buybacks': 'founder doc 02 2026-11-04 item 4',
       'capex': 'founder doc 02 2026-11-04 item 3', 'accounts_receivable': 'doc 02 2026-11-01 item 2 (label demotes only)', 'cash_and_equivalents': 'cash.md; Dhairya CB ruling'}
for dp, rx in DEMOTE.items():
    add(ns_of(dp), f'{ns_of(dp)}.{dp}.label_demote', dp, 'all', 'label_demote', {'label_regex': rx}, {'decision': 'combined'}, 'data point', DEV.get(dp, 'doc 02 2026-11-01 item 2: a label may demote, never promote'))
PREF = {'stockholders_equity': 'StockholdersEquity', 'net_income': 'NetIncomeLoss', 'comprehensive_income': 'ComprehensiveIncomeNetOfTax', 'cash_paid_for_interest': 'InterestPaidNet', 'cash_paid_for_income_taxes': 'IncomeTaxesPaidNet'}
for dp, t in PREF.items():
    add(ns_of(dp), f'{ns_of(dp)}.{dp}.prefer.{t}', dp, 'all', 'prefer_tag', {'among': 'mapped candidates'}, {'tag': t}, 'data point', 'DQC_0065' if 'Paid' in t else 'net-income/equity cards')
add('bank', 'bank.detect', '', 'bank', 'sector_detect', {'all_of': ['Deposits'], 'any_of': ['InterestAndDividendIncomeOperating','InterestExpenseDeposits','NoninterestIncome','LoansAndLeasesReceivableNetReportedAmount']}, {'group': 'bank'}, 'template', 'sector-faces.md (Deposits + NII is not a bank test alone)')
add('insurer', 'insurer.detect', '', 'insurer', 'sector_detect', {'any_of': ['PremiumsEarnedNet','LiabilityForFuturePolicyBenefits','LiabilityForUnpaidClaimsAndClaimsAdjustmentExpense']}, {'group': 'insurer'}, 'template', 'sector-faces.md')
add('bs', 'bs.detect_classified', '', 'all', 'sector_detect', {'any_of': ['AssetsCurrent']}, {'group': 'classified_bs'}, 'default', 'balance-sheet card (unclassified BS)')
add('bank', 'template.out.bank_insurer', '', 'bank;insurer', 'sector_out', {'groups': ['bank', 'insurer_unclassified']}, {'status': 'OUT', 'data_points': ['current_assets','current_liabilities','cost_of_revenue','gross_profit','inventory','cf_inventory_change','research_and_development']}, 'template', 'sector templates (docmap OUT rows)')
add('bs', 'bs.current.unclassified', '', 'all', 'unclassified_np', {}, {'data_points': ['current_assets', 'current_liabilities'], 'status': 'not_presented'}, 'default', 'doc 02 2026-11-01 item 4 (no derived instants)')
add('per_share', 'per_share.shares_outstanding.stmt', 'shares_outstanding', 'all', 'stmt_restrict', {'stmts': ['BS', 'EQ']}, {}, 'data point', 'Dhairya shares ruling 2026-11-12')
add('per_share', 'per_share.parenthetical_allowed', '', 'all', 'parenthetical_allowed', {}, {'data_points': ['shares_outstanding', 'dividends_per_share']}, 'data point', 'net-income-and-shares card')
OP = {
 'is.operating_expenses.procedure': ('operating_expenses', {'template_totals': ['NoninterestExpense', 'BenefitsLossesAndExpenses'], 'total_tags': ['OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses'],
     'band_exclude': ['GrossProfit', 'OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses'], 'tolerance': 0.0005, 'oi_tag': 'OperatingIncomeLoss', 'gp_tag': 'GrossProfit',
     'cos_label_regex': r'(?i)cost of|costs of|fuel|purchased power|food and paper|food & paper|production|operating costs|cost of operations|operations and maintenance|direct|distribution and servicing|cost of sales',
     'cos_tag_prefixes': ['CostOf', 'Fuel', 'PurchasedPower', 'Production', 'DirectCosts', 'DirectOperatingCosts', 'OperatingCostsAndExpenses', 'UtilitiesOperatingExpense', 'CostDirect']},
     'Dhairya opex rulings 2026-11-12 (operating-income.md §11; canonical_concept 53/208); FASB DISE TIG Example 1'),
 'bs.accounts_receivable.single_line': ('accounts_receivable', {'receivable_label': r'(?i)receivable', 'exclude_label': r'(?i)allowance|noncurrent|non-current|long-term', 'wider_label': r'(?i)\band\b|other|notes|contract'},
     'Dhairya AR override rule 2026-11-12; doc 02 item 2'),
 'is.interest_expense.plain_caption_net_tag': ('interest_expense', {'tags': ['InterestIncomeExpenseNet', 'InterestIncomeExpenseNonoperatingNet'], 'label_fullmatch': r'(?i)\s*interest expense\s*'},
     'interest card VRTX/AAON rule'),
 'is.net_income.no_parent_line': ('net_income', {'available_tag': 'NetIncomeLossAvailableToCommonStockholdersBasic', 'profitloss_tag': 'ProfitLoss', 'preferred_label': r'(?i)preferred', 'nci_tag_parts': ['NoncontrollingInterest', 'MinorityInterest']},
     'net-income-and-shares card §12; Dhairya ruling (b)'),
 'cf.depreciation_and_amortization.lone_line': ('depreciation_and_amortization', {'lone_tags': ['Depreciation', 'OtherDepreciationAndAmortization']}, 'capex-and-da card §7'),
 'cf.capex.sum_lines': ('capex', {}, 'founder doc 02 2026-11-04 item 3'),
 'is.sga_expense.lone_ga': ('sga_expense', {'tags': ['GeneralAndAdministrativeExpense', 'SellingGeneralAndAdministrativeExpense']}, 'dev keys (lone G&A mapped)'),
 'is.interest_expense.sole_debt': ('interest_expense', {'tag': 'InterestExpenseDebt'}, 'interest card (sole-debt rule)'),
 'notes.interest_income.inside_net_line': ('interest_income', {'pretax_prefix': 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes', 'oi_tag': 'OperatingIncomeLoss', 'label_any': r'(?i)interest', 'label_net': r'(?i)income|, net|and other'},
     'interest card; dev keys'),
 'is.opex_components': ('operating_expenses', {'tags': ['SellingGeneralAndAdministrativeExpense', 'ResearchAndDevelopmentExpense', 'SellingAndMarketingExpense', 'GeneralAndAdministrativeExpense', 'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost', 'AmortizationOfIntangibleAssets', 'RestructuringCharges', 'OtherCostAndExpenseOperating']}, 'v2 opex parts (kept for version parity; superseded by the procedure)'),
}
for rid, (dp, params, ev) in OP.items():
    add(rid.split('.')[0] if rid.split('.')[0] in ('is', 'bs', 'cf', 'notes') else 'is', rid, dp, 'all', 'procedure', params, {'procedure': rid}, 'data point', ev)
for ns, rows in R.items():
    w = csv.DictWriter(open(f'{out}/{ns}.csv', 'w', newline=''), fieldnames=COLS); w.writeheader(); w.writerows(rows)
print({ns: len(v) for ns, v in R.items()}, 'total', sum(len(v) for v in R.values()))
