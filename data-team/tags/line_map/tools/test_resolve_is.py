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


def test_accretion_tag_is_combined_when_the_filing_reports_accretion():
    # ruling 2026-11-14 (DUK): label plus evidence; an ARO accretion fact of the same filing makes the line combined
    cf = [('CF', 'NetIncomeLoss', 'Net income', 10), ('CF', 'DepreciationAmortizationAndAccretionNet', 'Depreciation and amortization', 7),
          ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash from operating activities', 22)]
    assert run(cf, {('AssetRetirementObligationAccretionExpense', 4): D(1)})['depreciation_and_amortization']['status'] == 'combined'
    assert run(cf)['depreciation_and_amortization']['status'] == 'mapped'
    # equity accretion (preferred, redeemable NCI) is not accretion inside D&A
    assert run(cf, {('PreferredStockAccretionOfRedemptionDiscount', 4): D(4)})['depreciation_and_amortization']['status'] == 'mapped'


def test_comprehensive_income_including_nci_is_the_parent_when_the_filing_has_no_nci():
    # ruling 2026-11-14: no NCI element (V, UNP, JNJ) -> the NCI-inclusive figure is the parent's (mapped); NCI present -> combined
    lines = [('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', 'Income before taxes', 8),
             ('BS', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', 'Total equity', 30)]
    notes = {('ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest', 4): D(56)}
    c = run(lines, notes)['comprehensive_income']
    assert c['status'] == 'mapped' and c['value'] == D(56)
    c2 = run(lines + [('IS', 'NetIncomeLossAttributableToNoncontrollingInterest', 'NCI', 2)], notes)['comprehensive_income']
    assert c2['status'] == 'combined'


def test_affiliate_interest_beside_a_net_line_is_a_part_not_the_data_point():
    # CEG FY2022: 'Interest expense, net' (250) and 'Interest expense to affiliates' (1): the gross figure is the note fact, never the affiliate part
    lines = [('IS', 'Revenues', 'Total operating revenues', 900), ('IS', 'OperatingIncomeLoss', 'Operating income', 100),
             ('IS', 'InterestExpense', 'Interest expense, net', 250), ('IS', 'RelatedPartyTransactionInterestExpense', 'Interest expense to affiliates', 1),
             ('IS', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes', 'Income before income taxes', -151)]
    r = run(lines, {('InterestExpense', 4): D(250)})['interest_expense']
    assert r['value'] == D(250) and r['r_page'] == 'NOTE'
    assert run(lines)['interest_expense']['status'] == 'combined'          # no gross fact: the net line is a point reason


def test_opex_is_not_presented_when_only_other_income_sits_between_gross_profit_and_oi():
    # LMT: Net sales - Cost of sales = Gross profit; 'Other income (expense), net' (+) -> Operating profit. No expense line: not presented, never -487
    import resolve as RS
    lines = [('IS', 'Revenues', 'Total net sales', 47248), ('IS', 'CostOfGoodsAndServicesSold', 'Total cost of sales', 42186),
             ('IS', 'GrossProfit', 'Gross profit', 5062), ('IS', 'OtherOperatingIncomeExpenseNet', 'Other income (expense), net', 487),
             ('IS', 'OperatingIncomeLoss', 'Operating profit', 5549)]
    calc = '~'.join(['1|GrossProfit|Revenues|1', '1|GrossProfit|CostOfGoodsAndServicesSold|-1', '2|OperatingIncomeLoss|GrossProfit|1', '2|OperatingIncomeLoss|OtherOperatingIncomeExpenseNet|1'])
    out, _ = RS.resolve(filing(lines, calc))
    assert out['operating_expenses']['status'] == 'not_presented' and 'no expense line' in out['operating_expenses']['path']


PT = 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes'
def calc(*kids): return '~'.join(f'1|{PT}|{t}|{w}' for t, w in kids)


def test_band_line_takes_its_calc_weight_toward_pretax_not_the_fact_sign():
    # AVGO FY2018: 'Impairment on investment' 106 (weight -1) beside 'Other income, net' 144 -> 38, not 250
    lines = [('IS', 'Revenues', 'Net revenue', 1000), ('IS', 'OperatingIncomeLoss', 'Operating income', 500),
             ('IS', 'InterestExpense', 'Interest expense', 100), ('IS', 'CostmethodInvestmentsOtherThanTemporaryImpairment', 'Impairment on investment', 106),
             ('IS', 'OtherNonoperatingIncomeExpense', 'Other income, net', 144), ('IS', PT, 'Income before income taxes', 438)]
    f = filing(lines, calc(('OperatingIncomeLoss', 1), ('InterestExpense', -1), ('CostmethodInvestmentsOtherThanTemporaryImpairment', -1), ('OtherNonoperatingIncomeExpense', 1)))
    o = R.resolve(f, {})['other_income_expense_net']
    assert o['status'] == 'component_sum' and o['value'] == D(38) and 'identity_break' not in o['flags']
    # a pension expense element printed alone (PM): positive expense with weight -1 is other expense
    lines = [lines[0], lines[1], ('IS', 'NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent', 'Pension and other employee benefit costs', 41),
             ('IS', PT, 'Income before income taxes', 459)]
    f = filing(lines, calc(('OperatingIncomeLoss', 1), ('NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent', -1)))
    assert R.resolve(f, {})['other_income_expense_net']['value'] == D(-41)


def test_printed_total_with_a_plain_label_role_is_a_subtotal_of_the_band():
    # RTX 2020: 'Total non-operating expense, net' (terseLabel, no calc) beside its parts
    lines = [('IS', 'Revenues', 'Net sales', 1000), ('IS', 'OperatingIncomeLoss', 'Operating profit (loss)', -1889),
             ('IS', 'NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent', 'Non-service pension benefit', -902),
             ('IS', 'InterestExpense', 'Interest expense, net', 1366), ('IS', 'NonoperatingIncomeExpense', 'Total non-operating expense, net', 464),
             ('IS', PT, 'Income (loss) before income taxes', -2353)]
    f = filing(lines, calc(('OperatingIncomeLoss', 1), ('NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent', -1), ('InterestExpense', -1)))
    f['lines'] = f['lines'].replace('|totalLabel|Total non-operating', '|terseLabel|Total non-operating')
    o = R.resolve(f, {})['other_income_expense_net']
    assert o['status'] == 'mapped' and o['value'] == D(902) and 'identity_break' not in o['flags']


def test_capitalized_interest_is_neither_other_income_nor_gross_interest():
    # SCCO: 'Capitalized interest' (InterestCostsCapitalized) between OI and pretax
    lines = [('IS', 'Revenues', 'Net sales', 1000), ('IS', 'OperatingIncomeLoss', 'Operating income', 500),
             ('IS', 'InterestExpense', 'Interest expense', 300), ('IS', 'InterestCostsCapitalized', 'Capitalized interest', -127),
             ('IS', 'OtherNonoperatingIncomeExpense', 'Other income (expense)', -41), ('IS', PT, 'Income before income taxes', 286)]
    r = R.resolve(filing(lines), {})
    assert r['other_income_expense_net']['value'] == D(-41) and r['other_income_expense_net']['status'] == 'mapped'
    assert r['interest_expense']['value'] == D(300)
    # 'Interest expense, net of capitalized interest' stays interest expense (MCD, VLO)
    assert R.kind(dict(tag='InterestExpense', lb='Interest expense, net of capitalized interest of $5')) != 'IEcap'


def test_finance_lease_interest_is_gross_interest_and_operating_losses_is_not_operating_income():
    lines = [('IS', 'Revenues', 'Total revenues', 1000), ('IS', 'OperatingIncomeLoss', 'Operating income', 500),
             ('IS', 'InterestExpenseDebt', 'Debt', 200), ('IS', 'FinanceLeaseAndFinancingObligationInterestExpense', 'Finance lease and financing obligations', 30),
             ('IS', 'NonoperatingIncomeExpense', 'Other (gains) and losses', 21), ('IS', PT, 'Income before income taxes', 249)]
    r = R.resolve(filing(lines), {})
    assert r['interest_expense']['value'] == D(230) and r['other_income_expense_net']['value'] == D(21)
    assert not R.OI_LB.search('Operating losses') and R.OI_LB.search('Operating loss')


def test_identity_break_is_flagged_not_dropped():
    # T 2019: equity income tagged -6 where the printed total needs +6
    lines = [('IS', 'Revenues', 'Total operating revenues', 1000), ('IS', 'OperatingIncomeLoss', 'Operating income', 27955),
             ('IS', 'InterestExpense', 'Interest expense', 8422), ('IS', 'IncomeLossFromEquityMethodInvestments', 'Equity in net income (loss) of affiliates', -6),
             ('IS', 'OtherNonoperatingIncomeExpense', 'Other income (expense) - net', -1071), ('IS', PT, 'Income before income taxes', 18468)]
    f = filing(lines, calc(('OperatingIncomeLoss', 1), ('InterestExpense', -1), ('IncomeLossFromEquityMethodInvestments', 1), ('OtherNonoperatingIncomeExpense', 1)))
    o = R.resolve(f, {})['other_income_expense_net']
    assert o['value'] == D(-1077) and 'identity_break' in o['flags']
