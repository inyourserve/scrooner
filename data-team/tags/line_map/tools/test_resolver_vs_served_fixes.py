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
