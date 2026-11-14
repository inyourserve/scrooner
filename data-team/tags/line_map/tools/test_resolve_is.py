"""Tests for resolve_is.py (run: python3 -m pytest data-team/tags/line_map/tools/test_resolve_is.py). Synthetic filings in the FSN
extract format: lines 'stmt|report|line|tag|custom|negating|prole|label|value' joined by '~'."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_is as R


def filing(lines, calc=''):
    return dict(cik='1', a='0000000001-26-000001', p='2025-12-31', fd='2026-02-01',
                lines='~'.join('|'.join(str(x) for x in (st, 2, i + 1, tag, 0, int(tag == 'InterestExpense'), 'totalLabel' if lb.startswith('Total') else 'terseLabel', lb, v)) for i, (st, tag, lb, v) in enumerate(lines)), calc=calc)


IS_AMZN = [('IS', 'Revenues', 'Net sales', 100), ('IS', 'OperatingIncomeLoss', 'Operating income', 20),
           ('IS', 'InvestmentIncomeInterest', 'Interest income', 51), ('IS', 'InterestExpense', 'Interest expense', 83),
           ('IS', 'OtherNonoperatingIncomeExpense', 'Other income (expense), net', -37),
           ('IS', 'NonoperatingIncomeExpense', 'Total non-operating income (expense)', -69),
           ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes', 'Income before income taxes', 14)]


def run(lines, notes=None):
    return R.resolve(filing(lines), notes or {})


def test_other_income_excludes_separately_printed_interest_and_the_subtotal():
    o = run(IS_AMZN)['other_income_expense_net']
    assert o['status'] == 'mapped' and o['value'] == D(-37) and o['tags'] == 'OtherNonoperatingIncomeExpense'
    assert run(IS_AMZN)['interest_expense']['value'] == D(83) and run(IS_AMZN)['interest_income']['value'] == D(51)


def test_single_nonoperating_total_with_interest_is_combined():
    lines = [IS_AMZN[0], IS_AMZN[1], ('IS', 'NonoperatingIncomeExpense', 'Other income (expense), net', 291), IS_AMZN[6]]
    o = run(lines)['other_income_expense_net']
    assert o['status'] == 'combined' and o['value'] is None


def test_interest_net_line_takes_the_gross_note_fact():
    lines = [IS_AMZN[0], IS_AMZN[1], ('IS', 'InterestIncomeExpenseNet', 'Interest expense, net', -4), IS_AMZN[6]]
    r = run(lines, {('InterestExpenseDebt', 4): D(9)})
    assert r['interest_expense']['status'] == 'mapped' and r['interest_expense']['value'] == D(9) and r['interest_expense']['r_page'] == 'NOTE'
    assert r['other_income_expense_net']['status'] == 'not_presented'
    assert run(lines)['interest_expense']['status'] == 'combined'


def test_comprehensive_income_including_nci_is_a_point_reason():
    ci = [('CI', 'ProfitLoss', 'Net income', 10), ('CI', 'NetIncomeLossAttributableToNoncontrollingInterest', 'NCI', 1),
          ('CI', 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest', 'Comprehensive income', 12)]
    c = run(ci)['comprehensive_income']
    assert c['status'] == 'combined' and c['flags'] == 'ci_incl_nci' and c['value'] is None
    p = run(ci + [('CI', 'ComprehensiveIncomeNetOfTax', 'Comprehensive income attributable to parent', 11)])['comprehensive_income']
    assert p['status'] == 'mapped' and p['value'] == D(11)


def test_da_with_accretion_is_combined_and_intangible_amortization_excludes_capitalized_software():
    cf = [('CF', 'NetIncomeLoss', 'Net income', 10), ('CF', 'DepreciationAmortizationAndAccretionNet', 'Depreciation, amortization and accretion', 7),
          ('CF', 'AmortizationOfIntangibleAssets', 'Amortization of acquisition-related intangibles', 3),
          ('CF', 'CapitalizedComputerSoftwareAmortization1', 'Amortization of capitalized software', 2),
          ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash from operating activities', 22)]
    r = run(cf)
    assert r['depreciation_and_amortization']['status'] == 'combined'
    assert r['amortization_of_intangibles']['value'] == D(3) and r['amortization_of_intangibles']['tags'] == 'AmortizationOfIntangibleAssets'


AMD24 = [('CF', 'NetIncomeLoss', 'Net income', 1641), ('CF', 'OtherDepreciationAndAmortization', 'Depreciation and amortization', 671),
         ('CF', 'AdjustmentForAmortization', 'Amortization of operating lease right-of-use assets', 2393),
         ('CF', 'OperatingLeaseRightOfUseAssetAmortizationExpense', 'Amortization of operating lease right-of-use assets', 113),
         ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 3041),
         ('IS', 'AmortizationOfAcquisitionRelatedIntangibles_Opex', 'Amortization of acquisition-related intangibles', 1448)]


def test_generic_amortization_line_equal_to_the_rounded_note_fact_is_intangible_amortization():
    # AMD FY2024 (0000002488-25-000012): FSN gives line 5 the label of line 7; the tag and the note fact ($2.4 billion) decide
    r = run(AMD24, {('AmortizationOfIntangibleAssets', 4): D(2400)})
    a, d = r['amortization_of_intangibles'], r['depreciation_and_amortization']
    assert a['status'] == 'mapped' and a['value'] == D(2393) and a['tags'] == 'AdjustmentForAmortization'
    assert d['status'] == 'component_sum' and d['value'] == D(3064)
    # without the note fact the generic line proves nothing: D&A stays the face line, amortization is not the lease line
    r0 = run(AMD24)
    assert r0['depreciation_and_amortization']['value'] == D(671) and r0['amortization_of_intangibles']['value'] != D(2393)


def test_note_equality_respects_the_note_rounding():
    assert R.note_close(D(1780), D(1800)) and R.note_close(D(2393), D(2400))
    assert not R.note_close(D(1700), D(1800)) and not R.note_close(D(2399), D(2390)) and not R.note_close(D(5), D(100))


def test_accretion_tag_printed_as_plain_depreciation_and_amortization_is_the_da_line():
    # AAPL FY2014-17, JPM, WMT, RTX: the element is DepreciationAmortizationAndAccretionNet, the printed label names only D&A
    cf = [('CF', 'NetIncomeLoss', 'Net income', 10), ('CF', 'DepreciationAmortizationAndAccretionNet', 'Depreciation and amortization', 7),
          ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash from operating activities', 22)]
    d = run(cf)['depreciation_and_amortization']
    assert d['status'] == 'mapped' and d['value'] == D(7)
    # SPGI FY2014: the same element printed 'Depreciation' beside an amortization line is depreciation, not the total
    sp = [cf[0], ('CF', 'DepreciationAmortizationAndAccretionNet', 'Depreciation', 86), ('CF', 'AmortizationOfIntangibleAssets', 'Amortization of intangibles', 98), cf[2]]
    d = run(sp)['depreciation_and_amortization']
    assert d['status'] == 'component_sum' and d['value'] == D(184)
