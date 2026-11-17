"""Resolver fixes from the resolver-vs-served review of 2026-11-14 (data-team/tags/line_map/_resolver-vs-served-2026-11-14.csv).
Run: python3 -m pytest data-team/tags/line_map/tools/test_resolver_vs_served_fixes.py. Synthetic filings in the FSN extract format."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve, resolve_all, resolve_is
from resolve_cf import resolve_cf
import resolve_cf as resolve_cf_mod


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


def test_cf_da_printed_as_depreciation_and_amortization_is_the_line_whatever_its_wider_element():
    # UBER 2024: CF 737 (DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense, printed 'Depreciation and amortization') vs IS 711.
    # Dhairya Group C 1 (2026-11-17) takes the CF 737, superseding ruling 2026-11-14 e; a CF label that itself says it is wider still yields to the IS line
    rows = [('IS', 'Revenues', 'Revenue', 43978), ('IS', 'DepreciationDepletionAndAmortization', 'Depreciation and amortization', 711), ('IS', 'OperatingIncomeLoss', 'Income from operations', 2799),
            ('CF', 'ProfitLoss', 'Net income', 10046), ('CF', 'uber_DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense', 'Depreciation and amortization', 737),
            ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 7137)]
    f = filing(rows)
    f['lines'] = f['lines'].replace('|uber_DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense|0|', '|uber_DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense|1|')
    d = resolve_is.resolve(f, {})['depreciation_and_amortization']
    assert d['value'] == D(737)
    f['lines'] = f['lines'].replace('|Depreciation and amortization|737', '|Depreciation and amortization, including other income|737')
    assert resolve_is.resolve(f, {})['depreciation_and_amortization']['value'] == D(711)


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
    assert "RevenueFromContractWithCustomer\\w*|SalesRevenueNet)$'" in sql and "'^(CostOf|Revenues$|RevenueFromContractWithCustomer|SalesRevenueNet$|" in sql


# ---- false-reason sweep 2026-11-14 (_false-reason-candidates-2026-11-14.csv)

def _cf_fin(line):
    return [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 100),
            ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -50),
            ('CF', 'PaymentsOfDividendsCommonStock', 'Dividends paid', 20), line,
            ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -40)]


def test_repurchase_line_with_employee_tax_withholdings_is_combined_not_missing():
    # MS: 'Repurchases of common stock and employee tax withholdings' is the only repurchase line
    b = resolve_cf(filing(_cf_fin(('CF', 'PaymentsRelatedToCommonStockRepurchaseAndTaxWithholdingForShareBasedCompensation', 'Repurchases of common stock and employee tax withholdings', 3933))), {})['share_buybacks']
    assert b['status'] == 'combined' and 'employee tax withholdings' in b['why'] and b['value'] is None


def test_class_member_repurchase_line_is_a_last_resort_sum():
    # V 2016: 'Repurchase of common stock' carries Class A and Class C members only; DELL: a later 10-K's consolidated figure wins
    f = filing(_cf_fin(('CF', 'PaymentsForRepurchaseOfCommonStock', 'Repurchase of common stock', None)))
    old = dict(resolve_cf_mod.MEMBER_FACTS)
    try:
        resolve_cf_mod.MEMBER_FACTS[f['a']] = 'PaymentsForRepurchaseOfCommonStock|4|6987000000|ClassOfStock=CommonClassA;~PaymentsForRepurchaseOfCommonStock|4|170000000|ClassOfStock=CommonClassC;'
        b = resolve_cf(f, {})['share_buybacks']
        assert b['status'] == 'not_presented' and b['alt']['value'] == D(7157000000) and b['alt']['status'] == 'component_sum'
        resolve_cf_mod.MEMBER_FACTS[f['a']] = 'PaymentsForRepurchaseOfCommonStock|4|6987000000|ClassOfStock=CommonClassA;'
        assert resolve_cf(f, {})['share_buybacks']['alt'] is None   # one class is not the total
    finally:
        resolve_cf_mod.MEMBER_FACTS.clear(); resolve_cf_mod.MEMBER_FACTS.update(old)
    # one ClassOfStock member is never read as the consolidated value (DELL FY2020 class V 0; classes A-D repurchased 8)
    assert standard_inputs.member_facts({}, {f['a']: 'PaymentsForRepurchaseOfCommonStock|4|0|ClassOfStock=CommonClassV;'}) == []


def _opex_row(f, why='no node'):
    return dict(accession=f['a'], data_point='operating_expenses', status='not_presented', value=None, tags='', nodes='', why=why, flags='')


def test_operating_lines_without_a_total_or_oi_are_summed_up_to_the_first_nonoperating_line():
    # KLAC: Costs of revenues, R&D, SG&A, then 'Loss on extinguishment of debt' and 'Interest expense'; no costs total, no OI
    f = filing([('IS', 'Revenues', 'Total revenues', 2814), ('IS', 'CostOfRevenue', 'Costs of revenues', 1215), ('IS', 'ResearchAndDevelopmentExpense', 'Engineering, research and development', 530),
                ('IS', 'SellingGeneralAndAdministrativeExpense', 'Selling, general and administrative', 406), ('IS', 'GainsLossesOnExtinguishmentOfDebt', 'Loss on extinguishment of debt', 131),
                ('IS', 'InterestExpense', 'Interest expense', 106), ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'Total income before income taxes', 426)])
    pt = 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'
    f['calc'] = '~'.join(f'3|{pt}|{t}|{w}' for t, w in [('Revenues', 1), ('CostOfRevenue', -1), ('ResearchAndDevelopmentExpense', -1), ('SellingGeneralAndAdministrativeExpense', -1),
                                                       ('GainsLossesOnExtinguishmentOfDebt', -1), ('InterestExpense', -1)])   # wave 2A: no OI line -> the pretax calc must tie
    cor = dict(accession=f['a'], data_point='cost_of_revenue', status='mapped', value=D(1215), tags='CostOfRevenue', nodes='', why='', flags='')
    r = resolve_all.apply_cost_and_opex([_opex_row(f), cor], [f])[0]
    assert r['status'] == 'component_sum' and r['value'] == D(936) and 'opex_component_lines' in r['flags']
    f['calc'] = f['calc'].replace('InterestExpense|-1', 'InterestExpense|1')   # a calc that misses the printed pretax: no sum
    assert resolve_all.apply_cost_and_opex([_opex_row(f), dict(cor)], [f])[0]['status'] == 'not_presented'
    # a line the rule does not know as operating stops the run before two lines: no sum
    g = filing([('IS', 'Revenues', 'Total revenues', 2814), ('IS', 'CostOfRevenue', 'Costs of revenues', 1215), ('IS', 'ResearchAndDevelopmentExpense', 'R&D', 530),
                ('IS', 'OtherCostAndExpenseOperating', 'Other', 9), ('IS', 'InterestExpense', 'Interest expense', 106)])
    cor_g = dict(cor, accession=g['a'])
    assert resolve_all.apply_cost_and_opex([_opex_row(g), cor_g], [g])[0]['status'] == 'not_presented'


def test_a_costs_total_holding_cost_of_revenue_makes_opex_combined():
    # BMY: 'Total Expenses' holds 'Cost of products sold' and 'Other (income)/expense'; no OI line
    f = filing([('IS', 'Revenues', 'Total Revenues', 15879), ('IS', 'CostOfGoodsSold', 'Cost of products sold', 3932), ('IS', 'ResearchAndDevelopmentExpense', 'Research and development', 4534),
                ('IS', 'CostsAndExpenses', 'Total Expenses', 13498), ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'Earnings Before Income Taxes', 2381)])
    cor = dict(accession=f['a'], data_point='cost_of_revenue', status='mapped', value=D(3932), tags='CostOfGoodsSold', nodes='', why='', flags='')
    r = resolve_all.apply_cost_and_opex([_opex_row(f), cor], [f])[0]
    assert r['status'] == 'combined' and r['nodes'] == 'CostsAndExpenses=13498 [R2.htm:4]' and 'Cost of products sold' in r['why']
    # a total with only operating lines in it is not called combined
    g = filing([('IS', 'Revenues', 'Total Revenues', 100), ('IS', 'ResearchAndDevelopmentExpense', 'Research and development', 40), ('IS', 'CostsAndExpenses', 'Total Expenses', 40)])
    assert resolve_all.apply_cost_and_opex([_opex_row(g)], [g])[0]['status'] == 'not_presented'


def test_printed_totals_cover_a_valueless_line_inside_them():
    # ABBV 2015: OtherExpenses has no consolidated value; total costs and expenses - cost of products sold, both printed, with OI printed
    f = filing([('IS', 'CostOfGoodsSold', 'Cost of products sold', 4500), ('IS', 'SellingGeneralAndAdministrativeExpense', 'SG&A', 6387), ('IS', 'OtherExpenses', 'Other', None),
                ('IS', 'CostsAndExpenses', 'Total costs and expenses', 15322), ('IS', 'OperatingIncomeLoss', 'Operating earnings', 7537)])
    cor = dict(accession=f['a'], data_point='cost_of_revenue', status='mapped', value=D(4500), tags='CostOfGoodsSold', nodes='', why='', flags='')
    row = dict(_opex_row(f), status='combined', why='a line between the top line and OI has no consolidated value (OtherExpenses): no component sum')
    r = resolve_all.apply_cost_and_opex([row, cor], [f])[0]
    assert r['status'] == 'component_sum' and r['value'] == D(10822)
    other = dict(_opex_row(f), status='combined', why='the line holding the role is wider than operating_expenses')
    assert resolve_all.apply_cost_and_opex([other, cor], [f])[0]['status'] == 'combined'


def test_related_party_split_ignores_an_equal_equity_method_investee_member():
    # WDC FY2023: NonrelatedParty 1,293 + RelatedParty 292; EquityMethodInvestee 292 is the same related party
    mf = {'a1': 'AccountsPayableCurrent|0|1293|RelatedPartyTransactionsByRelatedParty=NonrelatedParty;~AccountsPayableCurrent|0|292|RelatedPartyTransactionsByRelatedParty=RelatedParty;'
                '~AccountsPayableCurrent|0|292|RelatedPartyTransactionsByRelatedParty=EquityMethodInvestee;'}
    assert standard_inputs.related_splits(mf, r'AccountsPayableCurrent')['a1']['related'] == '292'
    mf['a1'] = mf['a1'].replace('|0|292|RelatedPartyTransactionsByRelatedParty=EquityMethodInvestee', '|0|50|RelatedPartyTransactionsByRelatedParty=EquityMethodInvestee')
    assert standard_inputs.related_splits(mf, r'AccountsPayableCurrent') == {}


def test_pretax_line_naming_the_equity_income_below_it_is_not_combined():
    # NEM: 'Income (loss) before income and mining tax and other items'; the other items are tax and equity income printed below it
    pt = 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'
    def run(after):
        f = filing([('IS', 'Revenues', 'Sales', 7292), ('IS', pt, 'Income (loss) before income and mining tax and other items', 506), *after,
                    ('IS', 'IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest', 'Income from continuing operations', 369)])
        row = dict(accession=f['a'], data_point='income_before_tax', status='mapped', value=D(506), tags=pt, nodes=f'{pt}=506 [R2.htm:2]', why='', flags='', column='own')
        return resolve_all.apply_label_beyond([row], [f])[0]['status']
    assert run([('IS', 'IncomeTaxExpenseBenefit', 'Income and mining tax', 133), ('IS', 'IncomeLossFromEquityMethodInvestments', 'Equity income (loss) of affiliates', -4)]) == 'mapped'
    assert run([('IS', 'IncomeTaxExpenseBenefit', 'Income and mining tax', 133)]) == 'combined'
    assert run([('IS', 'IncomeLossFromEquityMethodInvestments', 'Equity income', -4), ('IS', 'OtherNonoperatingIncomeExpense', 'Other', 2)]) == 'combined'


def test_other_income_label_may_cite_its_note():
    # GE 2014: 'Other income (Note 17)'
    assert resolve_is.OTHER_IE_LB.match('Other income (Note 17)') and not resolve_is.OTHER_IE_LB.match('Other operating income (Note 17)')


def test_buyback_combined_by_element_or_by_label_and_alt_only_after_fill():
    tag_only = resolve_cf(filing(_cf_fin(('CF', 'PaymentsRelatedToCommonStockRepurchaseAndTaxWithholdingForShareBasedCompensation', 'Share repurchases and related payments', 9))), {})['share_buybacks']
    assert tag_only['status'] == 'combined'
    lab = ('CF', 'ms_RepurchasesOfCommonStock', 'Repurchases of common stock and employee tax withholdings', 9)
    f = filing(_cf_fin(lab)); f['lines'] = f['lines'].replace('|ms_RepurchasesOfCommonStock|0|', '|ms_RepurchasesOfCommonStock|1|')
    assert resolve_cf(f, {})['share_buybacks']['status'] == 'combined'
    # a class member beside a member of another axis: not a class-only line
    g = filing(_cf_fin(('CF', 'PaymentsForRepurchaseOfCommonStock', 'Repurchase of common stock', None)))
    old = dict(resolve_cf_mod.MEMBER_FACTS)
    try:
        resolve_cf_mod.MEMBER_FACTS[g['a']] = 'PaymentsForRepurchaseOfCommonStock|4|5|ClassOfStock=CommonClassA;~PaymentsForRepurchaseOfCommonStock|4|6|ClassOfStock=CommonClassC;~PaymentsForRepurchaseOfCommonStock|4|11|ConsolidatedEntities=Parent;'
        assert resolve_cf(g, {})['share_buybacks']['alt'] is None
    finally:
        resolve_cf_mod.MEMBER_FACTS.clear(); resolve_cf_mod.MEMBER_FACTS.update(old)
    alt = dict(status='component_sum', value=D(7157))
    rows = resolve_all.apply_alt([dict(status='mapped', value=D(611), alt=alt), dict(status='not_presented', value=None, alt=alt)])
    assert rows[0]['value'] == D(611) and rows[1]['value'] == D(7157) and 'alt' not in rows[0]


def test_opex_lines_rule_needs_two_lines_and_no_oi():
    def run(lines):
        f = filing(lines)
        cor = dict(accession=f['a'], data_point='cost_of_revenue', status='mapped', value=D(1215), tags='CostOfRevenue', nodes='', why='', flags='')
        return resolve_all.apply_cost_and_opex([_opex_row(f), cor], [f])[0]['status']
    base = [('IS', 'Revenues', 'Total revenues', 2814), ('IS', 'CostOfRevenue', 'Costs of revenues', 1215), ('IS', 'ResearchAndDevelopmentExpense', 'R&D', 530)]
    assert run(base + [('IS', 'InterestExpense', 'Interest expense', 106)]) == 'not_presented'
    assert run(base + [('IS', 'SellingGeneralAndAdministrativeExpense', 'SG&A', 406), ('IS', 'OperatingIncomeLoss', 'Operating income', 663), ('IS', 'InterestExpense', 'Interest expense', 106)]) == 'not_presented'


# ---- Dhairya rulings on the sweep, 2026-11-14

def _role(dp):
    return next(r for r in resolve_all.ROLES if r['data_point'] == dp)


def test_bank_note_facts_are_served_after_the_fill_and_trade_elements_only_on_a_bank_face():
    ind = filing([('IS', 'Revenues', 'Revenues', 100), ('IS', 'InterestIncomeExpenseNet', 'Interest expense, net', -5)])
    L, arcs = resolve.parse(ind)
    r = resolve_all.role(ind, L, arcs, {('ProvisionForLoanAndLeaseLosses', 4): D(48)}, _role('provision_for_credit_losses'))
    assert r['status'] == 'not_presented' and r['alt']['value'] == D(48) and r['alt']['nodes'] == 'ProvisionForLoanAndLeaseLosses=48 [NOTE]'
    # a trade bad-debt provision is not a bank provision on an industrial face (CVS, VZ)
    r = resolve_all.role(ind, L, arcs, {('ProvisionForDoubtfulAccounts', 4): D(256)}, _role('provision_for_credit_losses'))
    assert 'alt' not in r and r['status'] == 'not_presented'
    # on a bank face (MS prints 'Net interest') the trade element is the bank's loans
    bank = filing([('IS', 'InterestIncomeExpenseNet', 'Net interest', 1735)])
    L, arcs = resolve.parse(bank)
    r = resolve_all.role(bank, L, arcs, {('NotesReceivableNet', 0): D(137784)}, _role('loans_net'))
    assert r['alt']['value'] == D(137784)
    # other data points keep serving the note fact directly
    r = resolve_all.role(ind, L, arcs, {('PaymentsForRepurchaseOfCommonStock', 4): D(7)}, dict(_role('provision_for_credit_losses'), data_point='x', alternatives='PaymentsForRepurchaseOfCommonStock'))
    assert r['status'] == 'mapped'


def test_interest_expense_of_the_finance_arm_and_its_complement_are_summed():
    # CAT 2019: two valued lines; 2020: one line with AllOtherExcludingFinancialProducts + FinancialProducts members
    f = filing([('IS', 'InterestExpenseOfFinancialProducts', 'Interest expense of Financial Products', 754), ('IS', 'OperatingIncomeLoss', 'Operating profit', 8290),
                ('IS', 'InterestExpenseExcludingFinancialProducts', 'Interest Expense Excluding Financial Products', 421)])
    row = dict(accession=f['a'], data_point='interest_expense', status='mapped', value=D(421), flags='')
    r = resolve_all.apply_complement_interest([row], [f], {})[0]
    assert r['value'] == D(1175) and r['status'] == 'component_sum' and 'member_sum' in r['flags']
    g = filing([('IS', 'Revenues', 'Sales', 41748), ('IS', 'InterestExpense', 'Interest Expense', None)])
    mf = {g['a']: 'InterestExpense|4|514|ProductOrService=AllOtherExcludingFinancialProducts;~InterestExpense|4|589|ProductOrService=FinancialProducts;'}
    r = resolve_all.apply_complement_interest([dict(accession=g['a'], data_point='interest_expense', status='not_presented', value=None, flags='')], [g], mf)[0]
    assert r['value'] == D(1103) and r['nodes'].startswith('InterestExpense[ProductOrService=AllOtherExcludingFinancialProducts]=514 [R2.htm:2]')
    # members that are not a part and its complement are not exhaustive
    mf2 = {g['a']: 'InterestExpense|4|514|ProductOrService=Products;~InterestExpense|4|589|ProductOrService=FinancialProducts;'}
    assert resolve_all.apply_complement_interest([dict(accession=g['a'], data_point='interest_expense', status='not_presented', value=None, flags='')], [g], mf2)[0]['status'] == 'not_presented'
    # 'of X' beside 'excluding Y' is not a complement
    h = filing([('IS', 'InterestExpenseOfFinancialProducts', 'Interest expense of Financial Products', 754), ('IS', 'InterestExpenseExcludingFinancialProducts', 'Interest expense excluding Insurance', 421)])
    assert resolve_all.apply_complement_interest([dict(accession=h['a'], data_point='interest_expense', status='mapped', value=D(421), flags='')], [h], {})[0]['value'] == D(421)


def _vlo(capex_val=None, other=-40, mf=None):
    rows = [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 5000),
            ('CF', 'PaymentsToAcquirePropertyPlantAndEquipment', 'Capital expenditures', capex_val),
            ('CF', 'PaymentsForCapitalImprovements', 'Deferred turnaround and catalyst cost expenditures', None),
            ('CF', 'PaymentsToAcquireAvailableForSaleSecuritiesDebt', 'Purchases of AFS debt securities', 27),
            ('CF', 'ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities', 'Proceeds from AFS', 30),
            ('CF', 'PaymentsForProceedsFromOtherInvestingActivities', 'Other investing activities, net', other),
            ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -1842),
            ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -100)]
    f = filing(rows)
    old = dict(resolve_cf_mod.MEMBER_FACTS)
    try:
        resolve_cf_mod.MEMBER_FACTS[f['a']] = mf if mf is not None else ('PaymentsToAcquirePropertyPlantAndEquipment|4|719|ConsolidatedEntities=ExcludingVIE;~PaymentsToAcquirePropertyPlantAndEquipment|4|77|ConsolidatedEntities=VIE;'
                                                                      '~PaymentsForCapitalImprovements|4|990|ConsolidatedEntities=ExcludingVIE;~PaymentsForCapitalImprovements|4|99|ConsolidatedEntities=VIE;')
        return resolve_cf(f, {})['capex']
    finally:
        resolve_cf_mod.MEMBER_FACTS.clear(); resolve_cf_mod.MEMBER_FACTS.update(old)


def test_entity_member_capex_is_served_only_when_it_ties_to_the_investing_total():
    c = _vlo()   # 796 + 1089 + 27 - 30 - 40 = 1842
    assert c['status'] == 'component_sum' and c['value'] == D(1885) and 'member_sum' in c['flags']
    assert _vlo(other=-10)['status'] == 'not_presented'   # off by 30: the members are not shown to be complete
    assert _vlo(mf='PaymentsToAcquirePropertyPlantAndEquipment|4|796|BusinessSegments=Refining;~PaymentsForCapitalImprovements|4|1089|ConsolidatedEntities=ExcludingVIE;')['status'] == 'not_presented'


def test_a_member_only_capex_line_beside_a_valued_one_is_never_left_out():
    # VLO 2018: 'Deferred turnaround' valued, 'Capital expenditures' member-only and not tying: a reason, not the turnaround alone
    rows = [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 5000),
            ('CF', 'PaymentsToAcquirePropertyPlantAndEquipment', 'Capital expenditures', None),
            ('CF', 'PaymentsForCapitalImprovements', 'Deferred turnaround and catalyst costs', 915),
            ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -3376),
            ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -100)]
    f = filing(rows)
    old = dict(resolve_cf_mod.MEMBER_FACTS)
    try:
        resolve_cf_mod.MEMBER_FACTS[f['a']] = 'PaymentsToAcquirePropertyPlantAndEquipment|4|1628|ConsolidatedEntities=ExcludingCertainVIE;'
        c = resolve_cf(f, {})['capex']
        assert c['status'] == 'not_presented' and 'incomplete group' in c['why']
        resolve_cf_mod.MEMBER_FACTS[f['a']] = 'PaymentsToAcquirePropertyPlantAndEquipment|4|2461|ConsolidatedEntities=ExcludingCertainVIE;'
        c = resolve_cf(f, {})['capex']
        assert c['status'] == 'component_sum' and c['value'] == D(3376)
        resolve_cf_mod.MEMBER_FACTS[f['a']] = ''   # a dash line with no facts at all (GLW 2020) is not a gap
        assert resolve_cf(f, {})['capex']['value'] == D(915)
    finally:
        resolve_cf_mod.MEMBER_FACTS.clear(); resolve_cf_mod.MEMBER_FACTS.update(old)


def test_complement_pair_needs_both_parts_and_tie_needs_known_directions():
    # CAT 2021: 'of Financial Products' member-only with no stored member: one part is not consolidated interest
    f = filing([('IS', 'Revenues', 'Sales', 1), ('IS', 'FinancingInterestExpense', 'Interest expense of Financial Products', None),
                ('IS', 'InterestExpense', 'Interest expense excluding Financial Products', 488)])
    row = dict(accession=f['a'], data_point='interest_expense', status='mapped', value=D(488), flags='')
    r = resolve_all.apply_complement_interest([row], [f], {})[0]
    assert r['value'] == D(488) and r['status'] == 'mapped' and 'member_sum' not in r['flags']
    # an investing line whose direction is unknown ('Change in restricted cash') blocks the tie
    rows = [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Operating', 5000), ('CF', 'PaymentsToAcquirePropertyPlantAndEquipment', 'Capital expenditures', None),
            ('CF', 'IncreaseDecreaseInRestrictedCash', 'Change in restricted cash', 0),
            ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -796),
            ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Financing', -100)]
    g = filing(rows)
    old = dict(resolve_cf_mod.MEMBER_FACTS)
    try:
        resolve_cf_mod.MEMBER_FACTS[g['a']] = 'PaymentsToAcquirePropertyPlantAndEquipment|4|796|ConsolidatedEntities=ExcludingVIE;'
        assert resolve_cf(g, {})['capex']['status'] == 'not_presented'
    finally:
        resolve_cf_mod.MEMBER_FACTS.clear(); resolve_cf_mod.MEMBER_FACTS.update(old)


# ---- top-100 open cells, 2026-11-15

def test_gross_profit_is_derived_from_the_revenue_ruling_3_sets():
    # MPC FY2018: revenue is the sales lines (95,750 + 754), not 'Total revenues and other income' 97,102
    f = filing([('IS', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'Sales and other operating revenues', 95750), ('IS', 'RevenueFromRelatedParties', 'Sales to related parties', 754),
                ('IS', 'OtherOperatingIncome', 'Other income', 598), ('IS', 'RevenuesAndOtherIncome', 'Total revenues and other income', 97102),
                ('IS', 'CostOfGoodsAndServicesSold', 'Cost of revenues', 85456)])
    base = dict(accession=f['a'], cik='1', ticker='X', period_end='2025-12-31', column='own', flags='', calc_check='', why='')
    rows = [dict(base, data_point='revenue', status='mapped', value=D(97102), tags='RevenuesAndOtherIncome', nodes='RevenuesAndOtherIncome=97102 [R2.htm:4]'),
            dict(base, data_point='cost_of_revenue', status='mapped', value=D(85456), tags='CostOfGoodsAndServicesSold', nodes='CostOfGoodsAndServicesSold=85456 [R2.htm:5]'),
            dict(base, data_point='gross_profit', status='not_presented', value=None, tags='', nodes='')]
    rows = resolve_all.apply_label_beyond(rows, [f], only={'revenue'})
    assert rows[0]['value'] == D(96504)
    g = [r for r in resolve_all.derive_gross_profit(rows) if r['data_point'] == 'gross_profit'][0]
    assert g['value'] == D(11048)
    # only= keeps the other data points for the full pass
    other = dict(base, data_point='cost_of_revenue', status='mapped', value=D(97102), tags='RevenuesAndOtherIncome', nodes='RevenuesAndOtherIncome=97102 [R2.htm:4]')
    assert resolve_all.apply_label_beyond([dict(other)], [f], only={'revenue'})[0]['status'] == 'mapped'
    assert resolve_all.apply_label_beyond([dict(other)], [f])[0]['status'] == 'combined'


def test_comparative_revenue_sums_every_element_and_reads_the_assessed_tax_twin():
    # MPC FY2017 from the FY2018 10-K: the sales row's FY2017 column is filed as ...IncludingAssessedTax
    later = '0000000002-26-000002'
    base = dict(cik='1', ticker='X', flags='', calc_check='', why='')
    rows = [dict(base, accession='0000000001-26-000001', period_end='2017-12-31', column='own', data_point='revenue', status='component_sum', value=D(74733), tags='A+RevenueFromRelatedParties', nodes=''),
            dict(base, accession=later, period_end='2017-12-31', column='comparative', data_point='cost_of_revenue', status='mapped', value=D(66519), tags='CostOfGoodsAndServicesSold', nodes=''),
            dict(base, accession='0000000001-26-000001', period_end='2017-12-31', column='own', data_point='gross_profit', status='not_presented', value=None, tags='', nodes=''),
            dict(base, accession=later, period_end='2018-12-31', column='own', data_point='revenue', status='component_sum', value=D(96504), tags='RevenueFromContractWithCustomerExcludingAssessedTax+RevenueFromRelatedParties', nodes='')]
    old = dict(resolve_all.EXT)
    try:
        resolve_all.EXT['comp'] = {later: 'RevenueFromContractWithCustomerIncludingAssessedTax|4|74104|2017-12-31~RevenueFromRelatedParties|4|629|2017-12-31'}
        resolve_all.EXT['gp'] = {}
        g = [r for r in resolve_all.derive_gross_profit([dict(r) for r in rows]) if r['data_point'] == 'gross_profit'][0]
        assert g['value'] == D(8214) and g['column'] == 'comparative'
        resolve_all.EXT['comp'] = {later: 'RevenueFromContractWithCustomerIncludingAssessedTax|4|74104|2017-12-31'}   # one element missing: no derivation
        rows[0] = dict(rows[0], value=D(74104))   # even where the present element alone would tie
        g = [r for r in resolve_all.derive_gross_profit([dict(r) for r in rows]) if r['data_point'] == 'gross_profit'][0]
        assert g['status'] == 'not_presented'
    finally:
        resolve_all.EXT.clear(); resolve_all.EXT.update(old)


def test_taxes_paid_by_jurisdiction_are_summed_and_parentheses_proven_by_the_interest_line():
    lines = [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Operating', 9000), ('CF', 'CashPaidAbstract', 'Cash paid during the year for:', None),
             ('CF', 'IncomeTaxPaidFederalAfterRefundReceived', 'Federal income taxes, net of refunds', -543),
             ('CF', 'IncomeTaxPaidStateAndLocalAfterRefundReceived', 'Total state income taxes, net of refunds', -321),
             ('CF', 'IncomeTaxPaidForeignAfterRefundReceived', 'Foreign income taxes, net of refunds', -13), ('CF', 'InterestPaidNet', 'Interest, net of amounts capitalized', 1311)]
    f = filing(lines); f['lines'] = f['lines'].replace('|InterestPaidNet|0|0|', '|InterestPaidNet|0|1|')   # UNP: printed (1,311) through a negated label
    row = lambda: dict(accession=f['a'], data_point='cash_paid_for_income_taxes', status='not_presented', value=None, tags='', nodes='', why='', flags='', column='own')
    r = resolve_all.apply_cash_paid_taxes([row()], [f], {})[0]
    assert r['status'] == 'component_sum' and r['value'] == D(877) and 'polarity_flip' in r['flags']
    g = filing(lines)   # no negated interest label: the sign is not proven, the sum keeps the stored sign
    r = resolve_all.apply_cash_paid_taxes([dict(row(), accession=g['a'])], [g], {})[0]
    assert r['value'] == D(-877)
    h = filing(lines[:4] + lines[5:]); h['lines'] = h['lines'].replace('|InterestPaidNet|0|0|', '|InterestPaidNet|0|1|')   # no foreign line: not complete
    assert resolve_all.apply_cash_paid_taxes([dict(row(), accession=h['a'])], [h], {})[0]['status'] == 'not_presented'
    m = dict(row(), status='mapped', value=D(-1486), tags='IncomeTaxesPaidNet')
    k = filing([lines[0], lines[1], ('CF', 'IncomeTaxesPaidNet', 'Income taxes, net of refunds', -1486), lines[5]]); k['lines'] = k['lines'].replace('|InterestPaidNet|0|0|', '|InterestPaidNet|0|1|')
    assert resolve_all.apply_cash_paid_taxes([dict(m, accession=k['a'])], [k], {})[0]['value'] == D(1486)
    assert resolve_all.apply_cash_paid_taxes([dict(m, accession=k['a'], tags='IncomeTaxesPaid')], [k], {})[0]['value'] == D(-1486)   # not the printed line
    mixed = filing([lines[0], lines[1], lines[2], ('CF', 'IncomeTaxPaidStateAndLocalAfterRefundReceived', 'State', 321), lines[4], lines[5]])
    mixed['lines'] = mixed['lines'].replace('|InterestPaidNet|0|0|', '|InterestPaidNet|0|1|')
    assert resolve_all.apply_cash_paid_taxes([dict(row(), accession=mixed['a'])], [mixed], {})[0]['value'] == D(-235)   # mixed signs: as stored


# ---- founder decision 2026-11-16: years a later 10-K prints are filled (GEV final draw)

def _replay_rows(later_nodes, later_value, later_status='component_sum', dp='operating_expenses'):
    base = dict(cik='0001996810', ticker='GEV', flags='', why='', calc_check='')
    return [dict(base, accession='BEFORE:0001996810:2022-12-31', period_end='2022-12-31', column='own', data_point=dp, status='not_presented', value=None, tags='', nodes=''),
            dict(base, accession='0001996810-25-000011', period_end='2024-12-31', column='own', data_point=dp, status=later_status, value=later_value, tags='', nodes=later_nodes)]


def test_a_later_10k_column_fills_a_year_through_the_parts_of_its_own_cell():
    comp = {'0001996810-25-000011': 'ResearchAndDevelopmentExpense|4|979000000|2022-12-31~SellingGeneralAndAdministrativeExpense|4|5360000000|2022-12-31'}
    rows = _replay_rows('ResearchAndDevelopmentExpense=982000000 [R3:11]; SellingGeneralAndAdministrativeExpense=4632000000 [R3:10]', D(5614000000))
    r = resolve_all.replay_fill(rows, comp, set())[0]
    assert r['status'] == 'component_sum' and r['value'] == D(6339000000) and r['column'] == 'comparative' and r['accession'] == '0001996810-25-000011'
    assert r['nodes'] == 'ResearchAndDevelopmentExpense=979000000 [R3.htm:11@0001996810-25-000011]; SellingGeneralAndAdministrativeExpense=5360000000 [R3.htm:10@0001996810-25-000011]'
    # the coefficients come from the later cell's own arithmetic (printed totals: total costs - cost of sales)
    rows = _replay_rows('CostsAndExpenses=100 [R3:9]; -CostOfRevenue=60 [R3:3]', D(40))
    r = resolve_all.replay_fill(rows, {'0001996810-25-000011': 'CostsAndExpenses|4|90|2022-12-31~CostOfRevenue|4|55|2022-12-31'}, set())[0]
    assert r['value'] == D(35)
    # a part with no value at the column: no fill
    rows = _replay_rows('ResearchAndDevelopmentExpense=982000000 [R3:11]; SellingGeneralAndAdministrativeExpense=4632000000 [R3:10]', D(5614000000))
    assert resolve_all.replay_fill(rows, {'0001996810-25-000011': 'ResearchAndDevelopmentExpense|4|979000000|2022-12-31'}, set())[0]['status'] == 'not_presented'
    # a member part is not replayed (its earlier-column member fact is not in the extract)
    rows = _replay_rows('ReceivablesNetCurrent[RelatedPartyTransactionsByRelatedParty=NonrelatedParty]=8000 [R4:9]', D(8000), 'mapped', 'accounts_receivable')
    assert resolve_all.replay_fill(rows, {'0001996810-25-000011': 'ReceivablesNetCurrent|0|7489|2022-12-31'}, set())[0]['status'] == 'not_presented'
    # an instant fills from FY-1 only
    rows = _replay_rows('InventoryNet=9000 [R4:10]', D(9000), 'mapped', 'inventory')
    assert resolve_all.replay_fill(rows, {'0001996810-25-000011': 'InventoryNet|0|8000|2022-12-31'}, {'inventory'})[0]['status'] == 'not_presented'
    # a note-only later cell fills a face data point only for per-share and note-natured data points
    rows = _replay_rows('SellingGeneralAndAdministrativeExpense=162 [NOTE]', D(162), 'mapped', 'sga_expense')
    assert resolve_all.replay_fill(rows, {'0001996810-25-000011': 'SellingGeneralAndAdministrativeExpense|4|150|2022-12-31'}, set())[0]['status'] == 'not_presented'
    rows = _replay_rows('IncomeTaxesPaidNet=623 [NOTE]', D(623), 'mapped', 'cash_paid_for_income_taxes')
    assert resolve_all.replay_fill(rows, {'0001996810-25-000011': 'IncomeTaxesPaidNet|4|91|2022-12-31'}, set())[0]['value'] == D(91)


def test_a_combined_later_cell_carries_its_reason_to_the_earlier_column():
    rows = _replay_rows('InterestAndOtherFinancialCharges=-120 [R3.htm:13]', None, 'combined', 'other_income_expense_net')
    r = resolve_all.replay_fill(rows, {'0001996810-25-000011': 'InterestAndOtherFinancialCharges|4|151|2022-12-31'}, set())[0]
    assert r['status'] == 'combined' and r['nodes'] == 'InterestAndOtherFinancialCharges=151 [R3.htm:13@0001996810-25-000011]'
    assert resolve_all.replay_fill(_replay_rows('InterestAndOtherFinancialCharges=-120 [R3.htm:13]', None, 'combined', 'other_income_expense_net'), {}, set())[0]['status'] == 'not_presented'
    # a valueless bundled balance-sheet line is on both columns (FY-1 only)
    rows = _replay_rows('AccountsPayableAndOtherAccruedLiabilitiesCurrent [R4.htm:22]', None, 'combined', 'accounts_payable')
    rows[0]['period_end'] = '2023-12-31'
    assert resolve_all.replay_fill(rows, {}, {'accounts_payable'})[0]['status'] == 'combined'
    rows = _replay_rows('AccountsPayableAndOtherAccruedLiabilitiesCurrent [R4.htm:22]', None, 'combined', 'accounts_payable')
    assert resolve_all.replay_fill(rows, {}, {'accounts_payable'})[0]['status'] == 'not_presented'   # FY-2: no balance sheet column


def test_a_bundled_accounts_payable_line_is_combined():
    f = filing([('BS', 'AssetsCurrent', 'Total current assets', 100), ('BS', 'AccountsPayableAndOtherAccruedLiabilitiesCurrent', 'Accounts payable and equipment project payables', None),
                ('BS', 'LiabilitiesCurrent', 'Total current liabilities', 50)])
    row = dict(accession=f['a'], data_point='accounts_payable', status='not_presented', value=None, tags='', nodes='', why='', flags='', column='own')
    r = resolve_all.apply_bundled_ap([row], [f])[0]
    assert r['status'] == 'combined' and r['nodes'] == 'AccountsPayableAndOtherAccruedLiabilitiesCurrent [R2.htm:2]'
    g = filing([('BS', 'AssetsCurrent', 'Total current assets', 100), ('BS', 'AccountsPayableCurrent', 'Accounts payable and accrued expenses', 7), ('BS', 'LiabilitiesCurrent', 'Total current liabilities', 50)])
    assert resolve_all.apply_bundled_ap([dict(row, accession=g['a'], status='not_presented', nodes='')], [g])[0]['status'] == 'not_presented'


def test_replay_guards():
    acc = '0001996810-25-000011'
    two = _replay_rows('ResearchAndDevelopmentExpense=982 [R3:11]', D(982), 'mapped')
    assert resolve_all.replay_fill(two, {acc: 'ResearchAndDevelopmentExpense|4|979|2022-12-31~ResearchAndDevelopmentExpense|4|970|2022-12-31'}, set())[0]['status'] == 'not_presented'   # two values
    mixed = _replay_rows('ResearchAndDevelopmentExpense=982 [R3:11]; SellingGeneralAndAdministrativeExpense[EquityComponents=X]=0 [R3:10]', D(982))
    assert resolve_all.replay_fill(mixed, {acc: 'ResearchAndDevelopmentExpense|4|979|2022-12-31'}, set())[0]['status'] == 'not_presented'   # a member part
    odd = _replay_rows('ResearchAndDevelopmentExpense=982 [R3:11]; SellingGeneralAndAdministrativeExpense=10 [R3:10]', D(5))   # no sign pattern gives 5
    assert resolve_all.replay_fill(odd, {acc: 'ResearchAndDevelopmentExpense|4|979|2022-12-31~SellingGeneralAndAdministrativeExpense|4|9|2022-12-31'}, set())[0]['status'] == 'not_presented'
    flow = _replay_rows('InterestAndOtherFinancialCharges [R3.htm:13]', None, 'combined', 'other_income_expense_net')
    flow[0]['period_end'] = '2023-12-31'
    assert resolve_all.replay_fill(flow, {}, set())[0]['status'] == 'not_presented'   # a valueless line is carried only on a balance sheet
    f = filing([('BS', 'AssetsCurrent', 'Total current assets', 100), ('BS', 'AccountsPayableAndOtherAccruedLiabilitiesCurrent', 'Payables', None), ('BS', 'LiabilitiesCurrent', 'Total current liabilities', 50)])
    row = dict(accession=f['a'], data_point='accounts_payable', status='not_presented', value=None, tags='', nodes='', why='', flags='', column='own')
    assert resolve_all.apply_bundled_ap([row], [f])[0]['status'] == 'combined'   # by the element alone


def test_other_income_line_holding_interest_is_split_by_its_own_breakdown():
    # Dhairya ruling 2026-11-16: BMY FY2023 'Other (income)/expense, net' 1,158 = interest income 449 - interest expense 1,166 + other
    calc = '~'.join(['1|OtherNonoperatingIncomeExpense|InvestmentIncomeInterest|1', '1|OtherNonoperatingIncomeExpense|InterestExpense|-1',
                     '1|OtherNonoperatingIncomeExpense|GainLossOnInvestments|1', '1|OtherNonoperatingIncomeExpense|InvestmentIncomeDividend|1'])
    f = filing([('IS', 'Revenues', 'Total Revenues', 45006), ('IS', 'OtherNonoperatingIncomeExpense', 'Other (income)/expense, net', 1158)], calc)
    base = dict(accession=f['a'], column='own', flags='', why='')
    def run(notes, ii_status='not_presented'):
        rows = [dict(base, data_point='other_income_expense_net', status='mapped', value=D(1158), tags='OtherNonoperatingIncomeExpense', nodes='OtherNonoperatingIncomeExpense=1158 [R2.htm:2]'),
                dict(base, data_point='interest_income', status=ii_status, value=None, tags='', nodes=''),
                dict(base, data_point='interest_expense', status='mapped', value=D(1166), tags='InterestExpense', nodes='InterestExpense=1166 [NOTE]')]
        return resolve_all.apply_other_income_split(rows, [f], {f['a']: notes})
    rows = run('InvestmentIncomeInterest|4|449~InterestExpense|4|1166~InvestmentIncomeDividend|4|30')
    assert rows[0]['value'] == D(1875) and rows[0]['status'] == 'component_sum' and 'interest_split' in rows[0]['flags']   # the dividend stays in other income
    assert rows[0]['nodes'] == 'OtherNonoperatingIncomeExpense=1158 [R2.htm:2]; -InvestmentIncomeInterest=449 [NOTE]; InterestExpense=1166 [NOTE]'
    assert rows[1]['status'] == 'mapped' and rows[1]['value'] == D(449)   # the interest part serves interest_income
    assert rows[2]['value'] == D(1166)                                    # an interest row already served is kept
    assert run('InvestmentIncomeInterest|4|449', 'combined')[1]['value'] == D(449)
    # no breakdown value: the line is served under the label rule
    rows = run('GainLossOnInvestments|4|700')
    assert rows[0]['status'] == 'mapped' and rows[0]['value'] == D(1158) and rows[1]['status'] == 'not_presented'
    # the line served with its calc-weight sign (-1): the split keeps that sign
    g = dict(base, data_point='other_income_expense_net', status='mapped', value=D(-1158), tags='OtherNonoperatingIncomeExpense', nodes='OtherNonoperatingIncomeExpense=1158 [R2.htm:2]')
    r = resolve_all.apply_other_income_split([g], [f], {f['a']: 'InvestmentIncomeInterest|4|449'})[0]
    assert r['value'] == D(-709)
    assert run('InvestmentIncomeInterest|4|0')[0]['status'] == 'mapped'   # a zero interest part: nothing to split
    rows = run('InvestmentIncomeInterest|4|449~InterestExpense|4|1166')
    rows2 = resolve_all.apply_other_income_split([dict(rows[0], status='mapped', value=D(1158), nodes='OtherNonoperatingIncomeExpense=1158 [R2.htm:2]'),
                                                   dict(base, data_point='interest_expense', status='mapped', value=D(1100), tags='X', nodes='X=1100 [R2.htm:9]')], [f], {f['a']: 'InterestExpense|4|1166'})
    assert rows2[1]['value'] == D(1100)   # a served interest row is never overwritten
    h = filing([('IS', 'Revenues', 'Total Revenues', 45006), ('IS', 'OtherNonoperatingIncomeExpense', 'Other income, net', 80)], '1|OtherNonoperatingIncomeExpense|InterestIncomeExpenseNet|1')
    hr = [dict(base, accession=h['a'], data_point='other_income_expense_net', status='mapped', value=D(80), tags='T', nodes='OtherNonoperatingIncomeExpense=80 [R2.htm:2]'),
          dict(base, accession=h['a'], data_point='interest_income', status='not_presented', value=None, tags='', nodes='')]
    hr = resolve_all.apply_other_income_split(hr, [h], {h['a']: 'InterestIncomeExpenseNet|4|2'})
    assert hr[0]['value'] == D(78) and hr[1]['status'] == 'not_presented'   # net interest is no interest-income figure
    odd = dict(base, data_point='other_income_expense_net', status='mapped', value=D(500), tags='T', nodes='OtherNonoperatingIncomeExpense=1158 [R2.htm:2]')
    assert resolve_all.apply_other_income_split([odd], [f], {f['a']: 'InvestmentIncomeInterest|4|449'})[0]['value'] == D(500)   # value is not the line: not split


def test_presented_period_reason_and_never_reported_mark():
    why = lambda w: f"no 10-K covers this year: it is before the company's first 10-K (0001321655-21-000011), and that 10-K's FY-{w} column does not print the line"
    base = dict(cik='0001321655', ticker='PLTR', flags='before_first_10k', column='own', value=None, tags='', nodes='')
    rows = [dict(base, accession='BEFORE:x:2019-12-31', period_end='2019-12-31', data_point='inventory', status='not_presented', why=why(1)),
            dict(base, accession='BEFORE:x:2018-12-31', period_end='2018-12-31', data_point='inventory', status='not_presented', why=why(2)),
            dict(base, accession='BEFORE:x:2018-12-31', period_end='2018-12-31', data_point='dividends_paid', status='not_presented', why=why(2)),
            dict(base, accession='a', period_end='2021-12-31', data_point='dividends_paid', status='mapped', value=D(5), flags='', why='')]
    rows = resolve_all.mark_presented_and_never_reported(rows)
    assert rows[0]['accession'] == '0001321655-21-000011' and rows[0]['column'] == 'comparative' and 'line_not_printed' in rows[0]['flags'] and 'before_first_10k' not in rows[0]['flags']
    assert rows[1]['accession'].startswith('BEFORE:') and 'before_first_10k' in rows[1]['flags']   # no balance-sheet column for FY-2: pre-filing
    assert 'line_not_printed' in rows[2]['flags']                                                   # a flow year FY-2 is presented
    assert 'never_reported' in rows[0]['flags'] and 'never_reported' not in rows[2]['flags']       # dividends are reported in another year


# ---- founder decision 2026-11-16, priority 2: combined lines split

def test_combined_line_split_by_the_note_fact_of_the_narrow_element():
    base = dict(cik='1', ticker='WELL', column='own', flags='', why='', tags='')
    row = lambda **k: dict(base, accession='a1', period_end='2014-12-31', data_point='dividends_paid', status='combined', value=None,
                           nodes='CashDistributionsToStockholders=1035069000 [R6.htm:46]', **k)
    r = resolve_all.apply_note_split([row()], {'a1': 'PaymentsOfDividendsCommonStock|4|969661000'})[0]
    assert r['status'] == 'mapped' and r['value'] == D(969661000) and 'note_split' in r['flags']
    assert resolve_all.apply_note_split([row()], {'a1': 'PaymentsOfDividendsCommonStock|4|2000123000'})[0]['status'] == 'combined'   # larger than the line
    assert resolve_all.apply_note_split([row()], {'a1': 'PaymentsOfDividendsCommonStock|4|900123000'})[0]['status'] == 'mapped'
    rounded = dict(row(), nodes='CashDistributionsToStockholders=1035069000 [R6.htm:46]')
    assert resolve_all.apply_note_split([rounded], {'a1': 'PaymentsOfDividendsCommonStock|4|1000000000'})[0]['status'] == 'combined'   # narrative '$1.0 billion'
    da = dict(row(), data_point='depreciation_and_amortization', nodes='DepreciationAmortizationAndAccretionNet=2600 [R9.htm:6]')
    assert resolve_all.apply_note_split([da], {'a1': 'DepreciationAndAmortization|4|63'})[0]['status'] == 'combined'   # D&A is the bulk of the line
    # the next 10-K's note column (GEV FY2024 AP from the FY2025 note)
    ap = [dict(base, accession='a1', period_end='2024-12-31', data_point='accounts_payable', status='combined', value=None, nodes='AccountsPayableAndOtherAccruedLiabilitiesCurrent [R4.htm:22]'),
          dict(base, accession='a2', period_end='2025-12-31', data_point='accounts_payable', status='mapped', value=D(5721), nodes='AccountsPayableTradeCurrent=5721 [NOTE]')]
    r = resolve_all.apply_note_split(ap, {}, {'a2': 'AccountsPayableTradeCurrent|0|4966|2024-12-31'})[0]
    assert r['value'] == D(4966) and r['accession'] == 'a2' and r['column'] == 'comparative'
    ap[0].update(status='combined', value=None, accession='a1', column='own', nodes='AccountsPayableAndOtherAccruedLiabilitiesCurrent [R4.htm:22]')
    assert resolve_all.apply_note_split(ap[:1], {}, {'a2': 'AccountsPayableTradeCurrent|0|4966|2024-12-31'})[0]['status'] == 'combined'   # no next year
    far = [dict(ap[0]), dict(ap[1], period_end='2026-12-31')]
    assert resolve_all.apply_note_split(far, {}, {'a2': 'AccountsPayableTradeCurrent|0|4966|2024-12-31'})[0]['status'] == 'combined'   # two years on is not the next 10-K


def test_combined_other_income_line_is_split_by_its_breakdown():
    f = filing([('IS', 'Revenues', 'Revenues', 10), ('IS', 'NonoperatingIncomeExpense', 'Interest and other income, net', 72900000)], '1|NonoperatingIncomeExpense|InvestmentIncomeInterest|1')
    row = dict(accession=f['a'], column='own', flags='', why='', data_point='other_income_expense_net', status='combined', value=None, tags='', nodes='NonoperatingIncomeExpense=72900000 [R2.htm:2]')
    r = resolve_all.apply_other_income_split([row], [f], {f['a']: 'InvestmentIncomeInterest|4|56200000'})[0]
    assert r['status'] == 'component_sum' and r['value'] == D(16700000)


def test_a_column_counts_as_printed_from_half_the_statement():
    f = filing([('IS', 'Revenues', 'Revenues', 10), ('IS', 'CostOfRevenue', 'Cost', 6), ('IS', 'NetIncomeLoss', 'Net income', 2)])
    assert resolve_all.column_printed(f, 'revenue', '2024-12-31', {f['a']: 'Revenues|4|9|2024-12-31~CostOfRevenue|4|5|2024-12-31'})
    assert not resolve_all.column_printed(f, 'revenue', '2024-12-31', {f['a']: 'Revenues|4|9|2024-12-31'})
    assert resolve_all.column_printed(f, 'inventory', '2024-12-31', {})   # no balance-sheet lines in the fixture: not decidable, kept
    why = "no 10-K covers this year: it is before the company's first 10-K (0000000001-26-000001), and that 10-K's FY-1 column does not print the line"
    row = lambda: dict(cik='1', ticker='X', accession='BEFORE:1:2024-12-31', period_end='2024-12-31', data_point='revenue', status='not_presented', flags='before_first_10k', why=why, column='own', value=None)
    r = resolve_all.mark_presented_and_never_reported([row()], [f], {f['a']: 'Revenues|4|9|2024-12-31'})[0]
    assert 'before_first_10k' in r['flags'] and r['accession'].startswith('BEFORE')   # under half the statement: not a printed column
    r = resolve_all.mark_presented_and_never_reported([row()], [f], {f['a']: 'Revenues|4|9|2024-12-31~CostOfRevenue|4|5|2024-12-31'})[0]
    assert 'line_not_printed' in r['flags']


def test_unsplit_combined_cells_are_marked_only_combined():
    base = dict(cik='1', ticker='X', column='own', why='', flags='', tags='', value=None)
    rows = [dict(base, accession='a', period_end='2020-12-31', data_point='cf_ap_change', status='combined', nodes='IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=5 [R6.htm:16]'),
            dict(base, accession='b', period_end='2021-12-31', data_point='cf_ap_change', status='mapped', value=D(3), nodes='IncreaseDecreaseInAccountsPayable=3 [R6.htm:16]'),
            dict(base, accession='a', period_end='2020-12-31', data_point='capex', status='combined', nodes='PaymentsToAcquireProductiveAssets=9 [R6.htm:20]')]
    rows = resolve_all.mark_presented_and_never_reported(rows)
    assert 'only_combined' in rows[0]['flags'] and 'only_combined_years' in rows[0]['flags'] and rows[0]['why'].endswith('reported only combined: IncreaseDecreaseInAccountsPayableAndAccruedLiabilities')
    assert 'only_combined_row' in rows[2]['flags']
    assert 'only_combined' not in rows[1]['flags']


def test_derived_total_liabilities_is_corroborated_by_the_liabilities_fact():
    f = filing([('BS', 'LiabilitiesCurrent', 'Current liabilities', 17437), ('BS', 'RedeemableNoncontrollingInterestEquityCarryingAmount', 'Redeemable NCI', 245)])
    row = lambda v: dict(accession=f['a'], column='own', data_point='total_liabilities', status='derived', value=D(v), tags='', nodes='x', why='', flags='', calc_check='')
    r = resolve_all.apply_tl_corroboration([row(95243)], {f['a']: 'Liabilities|0|95243'}, [f])[0]
    assert r['status'] == 'mapped' and r['nodes'] == 'Liabilities=95243 [NOTE]' and 'corroborates' in r['calc_check']
    r = resolve_all.apply_tl_corroboration([row(95488)], {f['a']: 'Liabilities|0|95243'}, [f])[0]
    assert r['status'] == 'derived' and 'explained' in r['calc_check'] and 'tl_corroboration_disagree' not in r['flags']   # differs by the redeemable NCI
    r = resolve_all.apply_tl_corroboration([row(96000)], {f['a']: 'Liabilities|0|95243'}, [f])[0]
    assert 'tl_corroboration_disagree' in r['flags']
    assert resolve_all.apply_tl_corroboration([row(95243)], {}, [f])[0]['status'] == 'derived'


def test_interest_and_dividends_income_is_interest_for_the_other_income_band():
    # Dhairya 2026-11-17 call 2: MSFT FY2015 'Other income (expense), net' 346 = interest and dividends income 766 - interest expense 781 + gains ...:
    # other income = 346 + 781 - 766 = 361. InvestmentIncomeInterestAndDividend counts by its element; InvestmentIncomeNet only where the filing
    # prints it as interest and dividends income (rules/interest_dividend_lines.csv)
    for el in ('InvestmentIncomeInterestAndDividend', 'InvestmentIncomeNet'):
        calc = f'1|NonoperatingIncomeExpense|{el}|1~1|NonoperatingIncomeExpense|InterestExpense|-1~1|NonoperatingIncomeExpense|GainLossOnInvestments|1'
        f = filing([('IS', 'Revenues', 'Revenue', 93580), ('IS', 'NonoperatingIncomeExpense', 'Other income (expense), net', 346)], calc)
        row = dict(accession=f['a'], column='own', flags='', why='', data_point='other_income_expense_net', status='mapped', value=D(346),
                   tags='NonoperatingIncomeExpense', nodes='NonoperatingIncomeExpense=346 [R2.htm:2]')
        notes = {f['a']: f'{el}|4|766~InterestExpense|4|781'}
        saved = set(resolve_all.INT_DIV_LINES)
        try:
            resolve_all.INT_DIV_LINES.add((f['a'], 'InvestmentIncomeNet'))
            assert resolve_all.apply_other_income_split([dict(row)], [f], notes)[0]['value'] == D(361)
            resolve_all.INT_DIV_LINES.discard((f['a'], 'InvestmentIncomeNet'))
            got = resolve_all.apply_other_income_split([dict(row)], [f], notes)[0]['value']
            assert got == (D(361) if el == 'InvestmentIncomeInterestAndDividend' else D(1127))   # investment income not printed as interest stays in other income
        finally:
            resolve_all.INT_DIV_LINES.clear(); resolve_all.INT_DIV_LINES.update(saved)


def test_absence_is_blocked_where_a_verifier_found_the_figure_printed():
    # DE FY2025 (Dhairya call 2026-11-17): 'Interest income - excluding FS 420' is printed (a part); the consolidated total is not: open, never hidden
    assert ('0001104659-25-122321', 'interest_income') in resolve_all.ABSENCE_BLOCKED
    f = dict(filing([('IS', 'Revenues', 'Revenues', 100)]), cik='9', a='0001104659-25-122321', p='2025-10-31')
    row = dict(data_point='interest_income', status='not_presented', accession=f['a'], period_end='2025-10-31', column='own', flags='roles', why='')
    resolve_all.apply_absent_in_own_filing([row], [f], {}, {})
    assert 'absent_in_own_filing' not in row['flags']
