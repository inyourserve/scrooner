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
