"""Resolver fixes from the resolver-vs-served review of 2026-11-14 (data-team/tags/line_map/_resolver-vs-served-2026-11-14.csv).
Run: python3 -m pytest data-team/tags/line_map/tools/test_resolver_vs_served_fixes.py. Synthetic filings in the FSN extract format."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve, resolve_all, resolve_is
from resolve_cf import resolve_cf


def filing(lines, calc=''):
    # line: (stmt, tag, label, value[, prole]); report 2, numbered in order
    s = '~'.join(f"{x[0]}|2|{i + 1}|{x[1]}|0|0|{x[4] if len(x) > 4 else 'terseLabel'}|{x[2]}|{'' if x[3] is None else x[3]}" for i, x in enumerate(lines))
    return dict(cik='1', a='0000000001-26-000001', p='2025-12-31', fd='2026-02-01', lines=s, calc=calc)


def test_total_assets_anchor_is_the_liabilities_and_capital_line_not_the_last_printed_total():
    # PLD 2022: L&SE is tagged LiabilitiesAndPartnersCapital...; the LP's equity section repeats 'Total equity' after it
    bs = [('BS', 'CashAndCashEquivalentsAtCarryingValue', 'Cash', 278483000), ('BS', 'OtherAssets', 'Other assets', 87618965000), ('BS', 'Assets', 'Total assets', 87897448000, 'totalLabel'),
          ('BS', 'Liabilities', 'Total liabilities', 30034355000, 'totalLabel'), ('BS', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', 'Total equity', 57863093000, 'totalLabel'),
          ('BS', 'LiabilitiesAndPartnersCapitalIncludingPortionAttributableToNoncontrollingInterest', 'Total liabilities and equity', 87897448000, 'totalLabel'),
          ('BS', 'MinorityInterest', 'Noncontrolling interests', 4625811000), ('BS', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', 'Total equity', 57863093000, 'totalLabel')]
    core, _ = resolve.resolve(filing(bs))
    assert core['total_assets']['value'] == D(87897448000) and core['total_assets']['tags'] == 'Assets'


def test_net_income_is_the_line_before_preferred_dividends():
    # AVGO FY2019: Net income (ProfitLoss) 2,724; dividends on preferred stock 29; net income attributable to common stock 2,695
    isl = [('IS', 'Revenues', 'Net revenue', 22597), ('IS', 'OperatingIncomeLoss', 'Operating income', 3444),
           ('IS', 'ProfitLoss', 'Net income', 2724), ('IS', 'PreferredStockDividendsIncomeStatementImpact', 'Dividends on preferred stock', 29),
           ('IS', 'NetIncomeLossAttributableToNoncontrollingInterest', 'Net income attributable to noncontrolling interest', 0),
           ('IS', 'NetIncomeLossAvailableToCommonStockholdersBasic', 'Net income attributable to common stock', 2695)]
    rows = resolve_all.run([filing(isl)], {}, {'0000000001': 'X'}, {})
    ni = next(r for r in rows if r['data_point'] == 'net_income')
    assert ni['value'] == D(2724) and ni['tags'] == 'ProfitLoss'


def test_amortization_excludes_incentive_right_of_use_and_cost_excluded_lines():
    note = {('AmortizationOfIntangibleAssets', 4): D(235)}
    cf = lambda tag, lb: filing([('CF', 'NetIncomeLoss', 'Net income', 900), ('CF', tag, lb, 764),
                                 ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 2000)])
    for tag, lb in (('AmortizationofCustomerandMerchantIncentives', 'Amortization of customer and merchant incentives'),          # MA: contra-revenue incentives
                    ('Amortizationofintangibleandrightofuseassets', 'Amortization of intangible and right-of-use assets'),        # AVGO FY2020+: holds ROU amortization
                    ('Amortizationofintangibleassetsexcludingamountincludedincostofrevenue', 'Amortization of intangibles')):      # STX: the opex part only
        a = resolve_is.resolve(cf(tag, lb), note)['amortization_of_intangibles']
        assert a['value'] == D(235) and a['r_page'] == 'NOTE', tag
    a = resolve_is.resolve(cf('xx_AmortizationOther', 'Amortization of customer and merchant incentives'), note)['amortization_of_intangibles']   # label alone
    assert a['value'] == D(235)
    a = resolve_is.resolve(cf('AmortizationOfIntangibleAssets', 'Amortization of intangible assets'), note)['amortization_of_intangibles']
    assert a['value'] == D(764)


def test_net_interest_line_takes_a_gross_note_tag_other_than_its_own():
    # LIN 2024: 'Interest expense - net' (InterestExpenseNonoperating 256); the note's InterestExpenseDebt 555 is gross
    isl = [('IS', 'Revenues', 'Sales', 1000), ('IS', 'OperatingIncomeLoss', 'Operating profit', 900),
           ('IS', 'NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent', 'Net pension and OPEB cost (benefit), excluding service cost', -10),
           ('IS', 'InterestExpenseNonoperating', 'Interest expense - net', 256), ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes', 'Income before income taxes', 654)]
    notes = {('InterestExpenseNonoperating', 4): D(256), ('InterestExpenseDebt', 4): D(555)}
    assert resolve_is.resolve(filing(isl), notes)['interest_expense']['value'] == D(555)
    # MCD: the only note tag is the face line's own: it stays
    assert resolve_is.resolve(filing(isl), {('InterestExpenseNonoperating', 4): D(256)})['interest_expense']['value'] == D(256)


def cff(rows):
    lines = '~'.join(f"CF|8|{i + 1}|{t}|{int(c)}|1||{lb}|{v}" for i, (t, v, c, lb) in enumerate(rows))
    return dict(cik='1', a='0000000001-25-000001', p='2024-12-31', fd='2025-02-01', lines=lines, calc='')


OP = ('NetCashProvidedByUsedInOperatingActivities', 100, False, 'Net cash from operating activities')
INV = ('NetCashProvidedByUsedInInvestingActivities', -50, False, 'Net cash used in investing activities')
FIN = ('NetCashProvidedByUsedInFinancingActivities', -20, False, 'Net cash used in financing activities')


def test_capex_line_that_also_holds_investments_is_combined_only_when_it_is_the_only_capex_line():
    psx = cff([OP, ('CapitalExpendituresAndInvestments', 2194, True, 'Capital expenditures and investments'), INV, FIN])
    c = resolve_cf(psx, {})['capex']
    assert c['status'] == 'combined' and c['value'] is None
    nee = cff([OP, ('NeeCapitalExpendituresOfFpl', 3000, True, 'Capital expenditures of FPL'),
               ('OtherCapitalExpenditures', 149, True, 'Other capital expenditures and other investments'), INV, FIN])
    c = resolve_cf(nee, {})['capex']
    assert c['status'] == 'component_sum' and c['value'] == D(3149)


# ---- Dhairya rulings 2026-11-14 (a)-(e) and filer XBRL errors
import standard_inputs, total_debt


def test_no_oi_band_starts_after_the_operating_lines_after_the_costs_total():
    # DIS FY2019: Restructuring and impairment charges after Costs and expenses are operating, never other income
    PT = 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes'
    isl = [('IS', 'Revenues', 'Revenues', 69570000000), ('IS', 'CostsAndExpenses', 'Costs and expenses', 57719000000, 'totalLabel'),
           ('IS', 'RestructuringSettlementAndImpairmentProvisions', 'Restructuring and impairment charges', 1183000000),
           ('IS', 'NonoperatingIncomeExpense', 'Other income, net', 4357000000), ('IS', 'InterestIncomeExpenseNonoperatingNet', 'Interest expense, net', -978000000),
           ('IS', 'IncomeLossFromEquityMethodInvestments', 'Equity in the income (loss) of investees, net', -103000000), ('IS', PT, 'Income before income taxes', 13944000000)]
    o = resolve_is.resolve(filing(isl), {})['other_income_expense_net']
    assert o['value'] == D(4254000000) and 'Restructuring' not in o['tags']


def test_reit_distribution_line_is_combined_while_preferred_dividends_are_paid():
    # WELL 2014-18: 'Cash distributions to stockholders' while the IS deducts preferred dividends; 2019+: common only
    def f(pref):
        rows = [('IS', 'PreferredStockDividendsIncomeStatementImpact', 'Preferred dividends', pref), ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash from operating activities', 100),
                ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -50),
                ('CF', 'CashDistributionsToStockholders', 'Cash distributions to stockholders', 1210), ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -20)]
        return filing(rows)
    assert resolve_cf(f(65), {})['dividends_paid']['status'] == 'combined'
    d = resolve_cf(f(0), {})['dividends_paid']
    assert d['status'] == 'mapped' and d['value'] == D(1210)


def test_expenses_by_nature_have_no_sga():
    # BKNG: marketing, sales and other, personnel (spanning functions), G&A; no SG&A line
    isl = [('IS', 'Revenues', 'Total revenues', 6796), ('IS', 'MarketingExpense', 'Marketing expenses', 2179),
           ('IS', 'LaborAndRelatedExpense', 'Personnel, including stock-based compensation', 1944), ('IS', 'GeneralAndAdministrativeExpense', 'General and administrative', 581),
           ('IS', 'OperatingIncomeLoss', 'Operating income', 2092)]
    rows = [dict(accession=filing(isl)['a'], data_point='sga_expense', status='component_sum', value=D(2760), tags='a+b', nodes='', why='', flags='')]
    r = resolve_all.apply_expenses_by_nature(rows, [filing(isl)])[0]
    assert r['status'] == 'not_presented' and r['value'] is None and 'expenses_by_nature' in r['flags']
    isl.insert(1, ('IS', 'SellingGeneralAndAdministrativeExpense', 'Selling, general and administrative', 900))
    rows[0]['status'] = 'mapped'
    assert resolve_all.apply_expenses_by_nature(rows, [filing(isl)])[0]['status'] == 'mapped'


def test_debt_total_holding_fed_funds_and_repos_takes_its_other_parts():
    # COF 2015: 'Total other debt' 42,949 = fed funds purchased and repos 981 + senior and subordinated notes 21,837 + other borrowings 20,131
    bs = [('BS', 'Assets', 'Total assets', 334048), ('BS', 'Deposits', 'Total deposits', 217721), ('BS', 'SecuredDebt', 'Securitized debt obligations', 16166),
          ('BS', 'FederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchase', 'Federal funds purchased and securities loaned or sold under agreements to repurchase', 981),
          ('BS', 'UnsecuredDebt', 'Senior and subordinated notes', 21837), ('BS', 'OtherBorrowings', 'Other borrowings', 20131),
          ('BS', 'cof_DebtExcludingSecuredDebt', 'Total other debt', 42949), ('BS', 'StockholdersEquity', "Total stockholders' equity", 47284)]
    f = filing(bs, '1|cof_DebtExcludingSecuredDebt|FederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchase|1~1|cof_DebtExcludingSecuredDebt|UnsecuredDebt|1~1|cof_DebtExcludingSecuredDebt|OtherBorrowings|1')
    f['lines'] = f['lines'].replace('|cof_DebtExcludingSecuredDebt|0|', '|cof_DebtExcludingSecuredDebt|1|')
    own = next(r for r in total_debt.run([f], [], {}) if r['column'] == 'own')
    assert D(own['value']) == D(58134) and 'Federal' not in own['tags']
    # the repo part not printed separately: the line is combined
    f2 = dict(f, lines='~'.join(x for x in f['lines'].split('~') if '|FederalFunds' not in x))
    own2 = next(r for r in total_debt.run([f2], [], {}) if r['column'] == 'own')
    assert own2['status'] == 'combined' and own2['value'] == ''


def test_note_finance_lease_equal_to_a_face_debt_line_is_inside_it():
    # COF 2020: 'Other borrowings' 75 = the note FinanceLeaseLiability 75
    bs = [('BS', 'Assets', 'Total assets', 421602), ('BS', 'SecuredDebt', 'Securitized debt obligations', 12414), ('BS', 'OtherBorrowings', 'Other borrowings', 75),
          ('BS', 'StockholdersEquity', "Total stockholders' equity", 60204)]
    f = filing(bs)
    vals = [dict(a=f['a'], vals=f"FinanceLeaseLiability|0|{f['p']}|75")]
    own = next(r for r in total_debt.run([f], vals, {}) if r['column'] == 'own')
    assert D(own['value']) == D(12489) and 'equals a face debt line' in own['flags']


def test_cf_da_that_includes_other_income_da_yields_to_the_is_line():
    # UBER 2024: CF 737 (DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense) vs IS 711
    rows = [('IS', 'Revenues', 'Revenue', 43978), ('IS', 'DepreciationDepletionAndAmortization', 'Depreciation and amortization', 711), ('IS', 'OperatingIncomeLoss', 'Income from operations', 2799),
            ('CF', 'ProfitLoss', 'Net income', 10046), ('CF', 'uber_DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense', 'Depreciation and amortization', 737),
            ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 7137)]
    f = filing(rows)
    f['lines'] = f['lines'].replace('|uber_DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense|0|', '|uber_DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense|1|')
    d = resolve_is.resolve(f, {})['depreciation_and_amortization']
    assert d['value'] == D(711)


def test_filer_xbrl_error_serves_the_printed_value():
    f = filing([('IS', 'IncomeLossFromEquityMethodInvestments', 'Equity in net income (loss) of affiliates', -6000000)])
    nf = {f['a']: 'IncomeTaxesPaidNet|4|-7469000000.0000~Other|4|5'}
    errs = {(f['a'], 'IncomeLossFromEquityMethodInvestments', 4): dict(xbrl=D(-6000000), printed=D(6000000), evidence='e'),
            (f['a'], 'IncomeTaxesPaidNet', 4): dict(xbrl=D(-7469000000), printed=D(7469000000), evidence='e')}
    assert standard_inputs.apply_filer_errors([f], nf, errs) == {f['a']}
    assert '|6000000' in f['lines'] and 'IncomeTaxesPaidNet|4|7469000000' in nf[f['a']]
    # a stored value that is not the listed XBRL value is left alone
    g = filing([('IS', 'IncomeLossFromEquityMethodInvestments', 'Equity', -7000000)])
    assert standard_inputs.apply_filer_errors([g], {}, {(g['a'], 'IncomeLossFromEquityMethodInvestments', 4): errs[(f['a'], 'IncomeLossFromEquityMethodInvestments', 4)]}) == set()


def _td(bs, vals, flloc=None, calc=''):
    f = filing(bs, calc)
    return next(r for r in total_debt.run([f], [dict(a=f['a'], vals='~'.join(f"{t}|0|{f['p']}|{v}" for t, v in vals))], flloc or {}) if r['column'] == 'own')


def test_face_lease_part_adds_the_other_part():
    # VRTX 2019: face FinanceLeaseLiabilityNoncurrent 538,576; note FinanceLeaseLiability 577,371 -> current 38,795 added
    bs = [('BS', 'Assets', 'Total assets', 13000000), ('BS', 'FinanceLeaseLiabilityNoncurrent', 'Long-term finance lease liabilities', 538576),
          ('BS', 'StockholdersEquity', "Total shareholders' equity", 8000000)]
    r = _td(bs, [('FinanceLeaseLiabilityNoncurrent', 538576), ('FinanceLeaseLiability', 577371)])
    assert D(r['value']) == D(577371) and 'FinanceLeaseLiabilityCurrent' in r['tags']
    # inside a debt line (ExtensibleList 'in'): not added
    f = filing(bs)
    r2 = next(x for x in total_debt.run([f], [dict(a=f['a'], vals=f"FinanceLeaseLiability|0|{f['p']}|577371")], {f['a']: 'in'}) if x['column'] == 'own')
    assert D(r2['value']) == D(538576)
    # pre-842 capital leases with no location evidence (CVX): flagged, not added
    bs3 = [bs[0], ('BS', 'CapitalLeaseObligationsNoncurrent', 'Capital lease obligations', 68), bs[2]]
    r3 = _td(bs3, [('CapitalLeaseObligationsCurrent', 17)])
    assert D(r3['value']) == D(68) and 'READER CHECK' in r3['flags']


def test_company_lease_location_from_its_other_filings():
    # IBM 2024: no ExtensibleList, but the company's 2021-23 filings say 'in': the note lease is not added by absence
    bs = [('BS', 'Assets', 'Total assets', 137175), ('BS', 'ShortTermBorrowings', 'Short-term debt', 5089), ('BS', 'LongTermDebtNoncurrent', 'Long-term debt', 49884),
          ('BS', 'StockholdersEquity', 'Total IBM stockholders equity', 27307)]
    f = filing(bs); g = dict(filing(bs), a='0000000001-25-000002', p='2023-12-31')
    vals = [dict(a=f['a'], vals=f"FinanceLeaseLiability|0|{f['p']}|1000"), dict(a=g['a'], vals='')]
    r = next(x for x in total_debt.run([f, g], vals, {g['a']: 'in'}) if x['accession'] == f['a'] and x['column'] == 'own')
    assert D(r['value']) == D(54973) and "company's other filings" in r['flags']


def test_receivable_from_a_sale_of_rights_is_not_accounts_receivable():
    import resolve_bs
    R = dict(alternatives='AccountsReceivableNetCurrent|ReceivablesNetCurrent', combined_if='', custom_label='receivable', note_ok='Y')
    iqos = dict(tag='ReceivableCommercializationRightsCurrent', custom=True, lb='Receivable from the sale of IQOS System commercialization rights', val=D(1721), rep=3, ln=3)
    assert resolve_bs.pick(R, [iqos], {}, 'accounts_receivable') in (None, {}) or resolve_bs.pick(R, [iqos], {}, 'accounts_receivable').get('value') != D(1721)
    trade = dict(iqos, tag='xx_TradeReceivables', lb='Trade receivables', val=D(48))
    assert resolve_bs.pick(R, [trade], {}, 'accounts_receivable')['value'] == D(48)


# ---- machine-parseable nodes and exact member names (Engineering, member-parts loader)
import re as _re
NODE = _re.compile(r'^-?\w+(\[\w+=[\w-]+\])?=-?[\d.]+ \[(R\d+(\.htm)?:\d+|NOTE|SE)\]$')


def parseable(nodes): return all(NODE.match(p) for p in nodes.split('; '))


def test_product_service_cor_keeps_the_filings_member_names():
    # TMUS FY2020 (0001283699-21-000039): CostOfGoodsAndServicesSold under ProductOrService=ProductEquipment 16,388 and Service 11,878
    mf = {'A': 'CostOfGoodsAndServicesSold|4|16388000000|ProductOrService=ProductEquipment;~CostOfGoodsAndServicesSold|4|11878000000|ProductOrService=Service;'}
    x = standard_inputs.product_service_cor({}, mf)['A']
    assert x['product_member'] == 'ProductEquipment' and x['service_member'] == 'Service'


def test_cor_member_nodes_are_parseable_with_the_member_and_line():
    f = filing([('IS', 'Revenues', 'Total revenues', 68397), ('IS', 'CostOfGoodsAndServicesSold', 'Cost of equipment sales', None)])
    resolve_all.EXT['cor'] = {f['a']: dict(tag='CostOfGoodsAndServicesSold', product='16388000000', service='11878000000', product_member='ProductEquipment', service_member='Service')}
    rows = [dict(accession=f['a'], data_point='cost_of_revenue', status='not_presented', value=None, tags='', nodes='', why='', flags='')]
    try:
        r = resolve_all.apply_cost_and_opex(rows, [f])[0]
    finally:
        resolve_all.EXT.pop('cor', None)
    assert r['value'] == D(28266000000) and parseable(r['nodes'])
    assert '[ProductOrService=ProductEquipment]=16388000000 [R2.htm:2]' in r['nodes'] and '[ProductOrService=Service]=11878000000 [R2.htm:2]' in r['nodes']


def test_filer_missing_fact_takes_the_printed_value():
    # RTX FY2019: the face prints Total Liabilities 95,390; the XBRL tags only the prior year
    f = filing([('BS', 'Liabilities', 'Total Liabilities', None)])
    errs = {(f['a'], 'Liabilities', 0): dict(xbrl=None, printed=D(95390000000), evidence='e')}
    assert standard_inputs.apply_filer_errors([f], {}, errs) == {f['a']}
    assert '|Total Liabilities|95390000000' in f['lines']
    g = filing([('BS', 'Liabilities', 'Total Liabilities', 1)])   # a tagged fact is not 'missing'
    assert standard_inputs.apply_filer_errors([g], {}, {(g['a'], 'Liabilities', 0): errs[(f['a'], 'Liabilities', 0)]}) == set()


def test_net_income_with_a_zero_nci_line_is_one_node():
    isl = [('IS', 'Revenues', 'Net revenue', 22597), ('IS', 'OperatingIncomeLoss', 'Operating income', 3444),
           ('IS', 'ProfitLoss', 'Net income', 2724000000), ('IS', 'PreferredStockDividendsIncomeStatementImpact', 'Dividends on preferred stock', 29000000),
           ('IS', 'NetIncomeLossAttributableToNoncontrollingInterest', 'Net income attributable to noncontrolling interest', 0),
           ('IS', 'NetIncomeLossAvailableToCommonStockholdersBasic', 'Net income attributable to common stock', 2695000000)]
    ni = next(r for r in resolve_all.run([filing(isl)], {}, {'0000000001': 'X'}, {}) if r['data_point'] == 'net_income')
    assert ni['tags'] == 'ProfitLoss' and len(ni['nodes'].split('; ')) == 1 and parseable(ni['nodes'].replace('[R2:', '[R2.htm:'))


def test_location_total_keeps_its_axis():
    mf = {'A': 'AmortizationOfIntangibleAssets|4|303000000|FiniteLivedIntangibleAssetsByMajorClass=OperatingExpense;~'
               'AmortizationOfIntangibleAssets|4|577000000|FiniteLivedIntangibleAssetsByMajorClass=CostOfSales;~'
               'AmortizationOfIntangibleAssets|4|880000000|FiniteLivedIntangibleAssetsByMajorClass=CostofSalesandOperatingExpenses;'}
    x = standard_inputs.amortization_location_total({}, mf)['A']
    assert x['axis'] == 'FiniteLivedIntangibleAssetsByMajorClass' and x['total_member'] == 'CostofSalesandOperatingExpenses' and x['value'] == D(880000000)


def test_sbc_note_fact_node_has_no_prose():
    rows = [('CF', 'NetIncomeLoss', 'Net income', 3617), ('CF', 'ShareBasedCompensation', 'Share-based payments', -15),
            ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 4500)]
    s = resolve_cf(filing(rows), {('AllocatedShareBasedCompensationExpense', 4): D(111)})['sbc']
    assert s['value'] == D(111) and parseable(s['nodes'])


# ---- resolver .24: one node grammar; incomplete calc groups are never judged
def _norm(rows, filings=()):
    bad = resolve_all.normalize_nodes(rows, list(filings))
    return bad, rows


def test_every_node_shape_lands_in_the_grammar():
    A, B = '0000000001-26-000001', '0000000009-27-000002'
    rows = [
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='total_debt', status='component_sum', value=D(2), column='own',
             nodes='ShortTermBorrowings=1 [BS R4:18 debt-role tag]; FinanceLeaseLiability=1 [NOTE note lease; no ExtensibleList and no debt line contains it (location by absence: CHECK)]', why='w'),
        dict(ticker='X', period_end='2024-12-31', accession=B, data_point='share_buybacks', status='mapped', value=D(0), column='comparative',
             nodes=f'PaymentsForRepurchaseOfCommonStock=0 [R7.htm:23 of {B}, FY-2 column]', why=''),
        dict(ticker='X', period_end='2023-12-31', accession=B, data_point='total_debt', status='component_sum', value=D(0), column='comparative',
             nodes=f'ShortTermBorrowings=0 [BS R2:24 debt-role tag]; LongTermDebt=0 [BS R2:28 debt-role tag] [comparative column of {B}]', why=''),
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='comprehensive_income', status='combined', value=None, column='own',
             nodes=f"ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest [R3.htm:9 'Comprehensive income', own 10-K {A}]", why=''),
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='shares_outstanding', status='mapped', value=D(5), column='own',
             nodes='CommonStockSharesOutstanding=5 [BS parenthetical / NOTE]', why=''),
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='revenue', status='mapped', value=D(10), column='own', nodes='Revenues=10 [R2:1]', why=''),
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='cost_of_revenue', status='component_sum', value=D(4), column='own',
             nodes='CostOfGoodsAndServicesSold[ProductOrService=Product]=3 [R2.htm:2]; -OtherIncome=-1 [R2.htm:3]', why=''),
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='gross_profit', status='derived', value=D(6), column='own',
             nodes='revenue=10; -cost_of_revenue=4', why=''),
        dict(ticker='X', period_end='2025-12-31', accession=A, data_point='other_income_expense_net', status='mapped', value=D(-7), column='own',
             nodes='OtherIncomeAndExpense [R2.htm]', why=''),
    ]
    bad, rows = _norm(rows)
    assert bad == 0
    for r in rows:
        assert all(resolve_all.NODE_GRAMMAR.match(p) for p in r['nodes'].split('; ')), r['nodes']
    by = {(r['data_point'], r['period_end']): r for r in rows}
    assert by[('total_debt', '2025-12-31')]['nodes'] == 'ShortTermBorrowings=1 [R4.htm:18]; FinanceLeaseLiability=1 [NOTE]' and 'location by absence' in by[('total_debt', '2025-12-31')]['why']
    assert by[('share_buybacks', '2024-12-31')]['nodes'].endswith(f'[R7.htm:23@{B}]')
    assert by[('total_debt', '2023-12-31')]['nodes'] == f'ShortTermBorrowings=0 [R2.htm:24@{B}]; LongTermDebt=0 [R2.htm:28@{B}]'
    assert by[('comprehensive_income', '2025-12-31')]['nodes'] == 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest [R3.htm:9]'
    assert by[('shares_outstanding', '2025-12-31')]['nodes'] == 'CommonStockSharesOutstanding=5 [BSP]'
    assert by[('gross_profit', '2025-12-31')]['nodes'] == 'Revenues=10 [R2.htm:1]; -CostOfGoodsAndServicesSold[ProductOrService=Product]=3 [R2.htm:2]; OtherIncome=-1 [R2.htm:3]'
    assert by[('other_income_expense_net', '2025-12-31')]['nodes'] == 'OtherIncomeAndExpense=-7 [R2.htm]'


def test_incomplete_calc_group_is_skipped_never_summed():
    A = '0000101829-20-000013'
    cf = {A: 'Liabilities|0|93492000000|2018-12-31'}
    # RTX FY2019: Liabilities printed but untagged for 2019, tagged for 2018: the failing group is incomplete
    assert resolve_all.finalize_calc('calc LiabilitiesAndStockholdersEquity: FAIL [no value: Liabilities]', A, cf) == 'calc LiabilitiesAndStockholdersEquity: skipped: child missing (Liabilities)'
    # a caption the filing never tags (CommitmentsAndContingencies) and a group that foots without the child (a printed dash) stand
    assert resolve_all.finalize_calc('calc LiabilitiesAndStockholdersEquity: FAIL [no value: CommitmentsAndContingencies]', A, cf) == 'calc LiabilitiesAndStockholdersEquity: FAIL'
    assert resolve_all.finalize_calc('calc LiabilitiesAndStockholdersEquity: ok [no value: Liabilities]', A, cf) == 'calc LiabilitiesAndStockholdersEquity: ok'
    assert resolve_all.finalize_calc('calc X: ok', A, cf) == 'calc X: ok'


def test_calc_check_names_children_without_a_value():
    # RTX FY2019 shape: Total Liabilities printed, no value; the calc of L&SE names it instead of silently summing the rest
    LSE = 'LiabilitiesAndStockholdersEquity'; EQ = 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
    bs = [('BS', 'Assets', 'Total Assets', 139716000000, 'totalLabel'), ('BS', 'Liabilities', 'Total Liabilities', None, 'totalLabel'),
          ('BS', EQ, 'Total Equity', 44231000000, 'totalLabel'), ('BS', LSE, 'Total Liabilities and Equity', 139716000000, 'totalLabel')]
    _, checks = resolve.resolve(filing(bs, f'3|{LSE}|Liabilities|1~3|{LSE}|{EQ}|1'))
    assert f'calc {LSE}: FAIL [no value: Liabilities]' in checks


# ---- false reasons (PM, approvals/PM-final-draw-2026-11-14.md)
def _ci_row(a, status='combined'):
    return dict(accession=a, data_point='comprehensive_income', status=status, value=None, tags='', nodes='', why='parent not printed', flags='ci_incl_nci', column='own')


def test_ci_parent_line_printed_on_the_ci_statement_is_served():
    # PM FY2016 R5: 'Comprehensive earnings attributable to PMI' (ComprehensiveIncomeNetOfTax 6,810) below 'Total comprehensive earnings'
    a = 'PM16'
    clines = {a: 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|5|13|Total comprehensive earnings~'
                 'ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|5|15|Noncontrolling interests~ComprehensiveIncomeNetOfTax|5|16|Comprehensive earnings attributable to PMI'}
    nf = {a: 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|4|7043000000~ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|4|233000000~ComprehensiveIncomeNetOfTax|4|6810000000'}
    r = resolve_all.apply_ci_parent([_ci_row(a)], clines, nf)[0]
    assert r['status'] == 'mapped' and r['value'] == D(6810000000) and r['nodes'] == 'ComprehensiveIncomeNetOfTax=6810000000 [R5.htm:16]' and 'ci_incl_nci' not in r['flags']
    # a custom-tagged line labelled 'attributable to <company>' counts too; the NCI line never does
    clines2 = {a: 'xx_ComprehensiveEarningsPmi|5|16|Comprehensive earnings attributable to PMI~ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|5|15|Comprehensive earnings attributable to noncontrolling interests'}
    nf2 = {a: 'xx_ComprehensiveEarningsPmi|4|6810000000~ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|4|233000000'}
    assert resolve_all.apply_ci_parent([_ci_row(a)], clines2, nf2)[0]['value'] == D(6810000000)
    nci_only = {a: 'ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|5|15|Comprehensive earnings attributable to noncontrolling interests'}
    assert resolve_all.apply_ci_parent([_ci_row(a)], nci_only, {a: 'ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|4|233000000'})[0]['status'] == 'combined'
    # an NCI-inclusive element is never the parent, whatever its label says
    incl = {a: 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|5|13|Comprehensive income attributable to shareholders'}
    assert resolve_all.apply_ci_parent([_ci_row(a)], incl, {a: 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|4|7043000000'})[0]['status'] == 'combined'
    # WFC FY2021: the parent line's fact carries only parent-scoped members
    mf = {a: 'ComprehensiveIncomeNetOfTax|4|19652000000|EquityComponents=Parent;~ComprehensiveIncomeNetOfTax|4|19652000000|ConsolidatedEntities=ParentCompany;'}
    w = resolve_all.apply_ci_parent([_ci_row(a)], {a: 'ComprehensiveIncomeNetOfTax|4|17|Wells Fargo comprehensive income'}, {}, mf)[0]
    assert w['value'] == D(19652000000) and w['nodes'].startswith('ComprehensiveIncomeNetOfTax[')


def test_amortization_by_location_without_a_total_is_summed_when_corroborated():
    # PM FY2022 R60: CostOfSales 58 + MA&R 101; the class-axis member 159 corroborates the sum
    mf = {'A': 'AmortizationOfIntangibleAssets|4|58000000|IncomeStatementLocation=CostOfSales;~AmortizationOfIntangibleAssets|4|101000000|IncomeStatementLocation=MarketingAdministrationAndResearchCosts;~'
               'AmortizationOfIntangibleAssets|4|159000000|FiniteLivedIntangibleAssetsByMajorClass=TrademarksandDistributionNetworks;'}
    x = standard_inputs.amortization_location_total({}, mf)['A']
    assert x['value'] == D(159000000) and x['axis'] == 'IncomeStatementLocation' and x.get('corroborated')
    # no corroborating fact: no sum (two location rows alone may be a partial split)
    assert 'A' not in standard_inputs.amortization_location_total({}, {'A': mf['A'].rsplit('~', 1)[0]})


def test_fsn_dropped_facts_are_added_to_the_member_facts(tmp_path):
    p = tmp_path / 'f.csv'
    p.write_text('accession,tag,qtrs,segment,value,evidence\nA,AmortizationOfIntangibleAssets,4,IncomeStatementLocation=CostOfSales;,58000000,e\nA,X,4,,5,e\n')
    mf, nf = {}, {}
    assert standard_inputs.fsn_dropped_facts(str(p), mf, nf) == 2
    assert mf['A'] == 'AmortizationOfIntangibleAssets|4|58000000|IncomeStatementLocation=CostOfSales;' and nf['A'] == 'X|4|5'


def test_member_only_capex_lines_take_the_filings_capex_fact():
    # VLO 2019: 'Capital expenditures' and 'Deferred turnaround and catalyst cost expenditures' print with member facts only
    rows = [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 5531),
            ('CF', 'PaymentsToAcquirePropertyPlantAndEquipment', 'Capital expenditures', None),
            ('CF', 'PaymentsForCapitalImprovements', 'Deferred turnaround and catalyst cost expenditures', None),
            ('CF', 'PaymentsToAcquireInterestInJointVenture', 'Investments in unconsolidated joint ventures', 164),
            ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -3001),
            ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -2997)]
    c = resolve_cf(filing(rows), {('PaymentsToAcquireProductiveAssets', 4): D(2846)})['capex']
    assert c['status'] == 'mapped' and c['value'] == D(2846) and 'member facts only' in c['why']
    assert resolve_cf(filing(rows), {})['capex']['status'] == 'not_presented'


def test_printed_total_expenses_line_is_the_opex():
    # PLD 2024: 'Total expenses' between 'Total revenues' and 'Operating income before gains on real estate transactions'
    isl = [('IS', 'Revenues', 'Total revenues', 8201610000), ('IS', 'GeneralAndAdministrativeExpense', 'General and administrative', 418765000),
           ('IS', 'pld_OperatingExpensesBeforeGains', 'Total expenses', 5103569000),
           ('IS', 'pld_OperatingIncomeBeforeGains', 'Operating income before gains on real estate transactions, net', 3098041000)]
    f = filing(isl)
    rows = [dict(accession=f['a'], data_point='operating_expenses', status='not_presented', value=None, tags='', nodes='', why='no node', flags='')]
    r = resolve_all.apply_cost_and_opex(rows, [f])[0]
    assert r['value'] == D(5103569000) and r['status'] == 'mapped'
    # 'Total costs and expenses' holds cost of revenue (QCOM): not the opex
    f2 = filing([isl[0], ('IS', 'CostsAndExpenses', 'Total costs and expenses', 18937000000), ('IS', 'OperatingIncomeLoss', 'Operating income', 7000000000)])
    rows2 = [dict(accession=f2['a'], data_point='operating_expenses', status='not_presented', value=None, tags='', nodes='', why='no node', flags='')]
    assert resolve_all.apply_cost_and_opex(rows2, [f2])[0]['value'] != D(18937000000)


def _bmy(other=('IS', 'OtherNonoperatingIncomeExpense', 'Other (income)/expense, net', 1158000000), extra=(), after=()):
    isl = [('IS', 'Revenues', 'Total Revenues', 45006000000), ('IS', 'CostOfGoodsAndServicesSold', 'Cost of products sold', 10693000000), other,
           ('IS', 'CostsAndExpenses', 'Total Expenses', 35400000000), *extra,
           ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'Earnings before income taxes', 9606000000),
           ('IS', 'IncomeTaxExpenseBenefit', 'Income tax provision', 400000000), *after]
    calc = '~'.join(['1|IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest|Revenues|1',
                     '1|IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest|CostsAndExpenses|-1',
                     '2|CostsAndExpenses|CostOfGoodsAndServicesSold|1', '2|CostsAndExpenses|OtherNonoperatingIncomeExpense|-1', '2|CostsAndExpenses|OtherCostAndExpenseOperating|1',
                     '3|OtherNonoperatingIncomeExpense|GainLossOnInvestments|1', '3|OtherNonoperatingIncomeExpense|InvestmentIncomeInterest|1'])
    return resolve_is.resolve(filing(isl, calc), {})['other_income_expense_net']


def test_other_income_expense_printed_inside_total_expenses_is_the_data_point():
    # ruling 2026-11-14 (BMY): served in the income convention through its calc weight; its note breakdown does not make it a total
    r = _bmy()
    assert r['status'] == 'mapped' and r['value'] == D(1158000000) and 'presented_within_expenses' in r['flags']
    # an expense-named element with no calc weight enters negated (RTX 2015 OtherExpenses 211 = other expense)
    r = _bmy(('IS', 'OtherExpenses', 'Other expenses', 211000000))
    assert r['value'] == D(-211000000)
    # the calc weight decides the sign: an expense element added into total expenses is other expense
    assert _bmy(('IS', 'OtherCostAndExpenseOperating', 'Other expense, net', 50000000))['value'] == D(-50000000)
    # 'Other operating expense' is opex, and a line below pretax is not in the income band
    assert _bmy(('IS', 'OtherCostAndExpenseOperating', 'Other operating expense, net', 50000000))['status'] == 'not_presented'
    assert _bmy(('IS', 'CostOfServices', 'Cost of services', 5), after=(('IS', 'OtherNonoperatingIncomeExpense', 'Other income', 9),))['status'] == 'not_presented'


def test_other_income_guards_twin_dash_and_incomplete_group():
    # the alternate-sign twin with no value is the same printed line (RTX 2015)
    twin = resolve_is.resolve(filing([('IS', 'Revenues', 'Net sales', 100), ('IS', 'OtherExpenses', 'Other (expense) income, net', 7), ('IS', 'OtherIncome', 'Other (expense) income, net', None),
                                      ('IS', 'OperatingIncomeLoss', 'Operating profit', 93), ('IS', 'InterestExpense', 'Interest expense', 3),
                                      ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'Income before income taxes', 90)]), {})['other_income_expense_net']
    assert twin['status'] == 'mapped' and twin['value'] == D(-7)
    # a dash printed in the band (LMT 2016) stays for the printed-zero rule
    dash = _bmy(extra=(('IS', 'OtherNonoperatingIncome', 'Other non-operating income, net', None),))
    assert dash['status'] == 'not_presented'
    # a part with no consolidated fact: an incomplete group is never summed
    inc = resolve_is.resolve(filing([('IS', 'OtherMember', 'Other income', None), ('IS', 'Revenues', 'Net sales and revenues', 100),
                                                                 ('IS', 'OtherExpenses', 'Other expenses', 4), ('IS', 'CostsAndExpenses', 'Total', 60),
                                                                 ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'Income before income taxes', 40)]), {})['other_income_expense_net']
    assert inc['status'] == 'not_presented' and 'other_part_no_fact' in inc['flags']


def test_revenue_member_row_takes_its_member_fact():
    # DE FY2024: 'Other Income' is a ProductOrService=Other row; its fact comes from rules/fsn_dropped_facts.csv
    f = filing([('IS', 'OtherMember', 'Other Income', None), ('IS', 'Revenues', 'Net sales and revenues', 51716000000), ('IS', 'CostsAndExpenses', 'Total', 42510000000),
                ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', 'Income before Income Taxes', 9206000000)])
    old = dict(resolve_is.MEMBER_FACTS)
    try:
        resolve_is.MEMBER_FACTS[f['a']] = 'Revenues|4|1198000000|ProductOrService=Other;~Revenues|1|300000000|ProductOrService=Other;'
        r = resolve_is.resolve(f, {})['other_income_expense_net']
        assert r['status'] == 'mapped' and r['value'] == D(1198000000) and r['nodes'] == 'Revenues[ProductOrService=Other]=1198000000 [R2.htm:1]'
        assert resolve_all.NODE_GRAMMAR.match(r['nodes'])
    finally:
        resolve_is.MEMBER_FACTS.clear(); resolve_is.MEMBER_FACTS.update(old)


def test_revenue_table_member_is_never_the_consolidated_revenue():
    # the extract now carries revenue facts by ProductOrService member on an IS line (DE, WELL 'Other income'); a lone member is a row
    mf = {'0000000001-26-000001': 'RevenueFromContractWithCustomerExcludingAssessedTax|4|19429000|ProductOrService=ProductAndServiceOther;'}
    assert standard_inputs.member_facts({}, mf) == []
    assert len(standard_inputs.member_facts({}, {'0000000001-26-000001': 'NetIncomeLoss|4|5|Scenario=Previously Reported;'.replace(' ', '')})) == 1


def test_extract_selects_revenue_rows_by_product_or_service_member():
    sql = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extract_notefacts.sql')).read()
    assert "RevenueFromContractWithCustomer\\w*|SalesRevenueNet)$'" in sql and "'^(CostOf|Revenues$|RevenueFromContractWithCustomer|SalesRevenueNet$)'" in sql
