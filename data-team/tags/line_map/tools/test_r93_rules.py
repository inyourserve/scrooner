"""Resolver .93 rules X134 (other income = the printed band without its interest lines), X135 (cash excludes restricted cash),
X136 (net income never available-to-common: any printed preferred line). Run: python3 -m pytest
data-team/tags/line_map/tools/test_r93_rules.py. Mutation-checked when added."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all

ACC = '0000927653-18-000010'


def _row(dp, status, value, nodes, flags='roles', acc=ACC):
    return dict(ticker='MCK', cik='927653', accession=acc, period_end='2018-03-31', data_point=dp, status=status, tags='',
                value=None if value is None else D(value), r_page='', nodes=nodes, why='', source='roles', calc_check='', flags=flags, column='own')


def _ln(ln, tag, lb, val):
    return f"IS|2|{ln}|{tag}|0|0|terseLabel|{lb}|{'' if val is None else val}"


def _mck(lines):
    return dict(a=ACC, lines='~'.join(lines), calc='')


MCK_LINES = [_ln(20, 'OperatingIncomeLoss', 'Operating Income', '762000000.0000'),
             _ln(21, 'NonoperatingIncomeExpense', 'Other Income, Net', '130000000.0000'),
             _ln(22, 'IncomeLossFromEquityMethodInvestments', 'Loss from Equity Method Investment in Change Healthcare', None),
             _ln(23, 'GainsLossesOnExtinguishmentOfDebt', 'Loss on Debt Extinguishment', '-122000000.0000'),
             _ln(24, 'InterestAndDebtExpense', 'Interest Expense', '283000000.0000'),
             _ln(25, 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'Income before taxes', '239000000.0000')]


def _base(oi_value='8000000', oi_flags='roles'):
    return [_row('operating_income', 'mapped', '762000000', 'OperatingIncomeLoss=762000000.0000 [R2.htm:20]'),
            _row('income_before_tax', 'mapped', '239000000',
                 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest=239000000.0000 [R2.htm:25]'),
            _row('other_income_expense_net', 'component_sum', oi_value,
                 'NonoperatingIncomeExpense=130000000.0000 [R2.htm:21]; GainsLossesOnExtinguishmentOfDebt=-122000000.0000 [R2.htm:23]', flags=oi_flags)]


def test_x134_band_holds_every_non_interest_line_incl_equity_method():
    # MCK FY2018: the equity-method loss line (no own fact in the extract) is inside pretax; other income = 239 - 762 + 283 = -240
    out = resolve_all.apply_other_income_band(_base(), [_mck(MCK_LINES)])
    r = out[2]
    assert (r['status'], r['value']) == ('component_sum', D(-240000000))
    assert 'InterestAndDebtExpense=283000000.0000 [R2.htm:24]' in r['nodes']
    assert resolve_all.OI_BADGE_IDENTITY in r['flags'].split(';')


def test_x134_never_overrides_a_read_or_a_split_row_and_keeps_the_filers_rounding():
    assert resolve_all.apply_other_income_band(_base(oi_flags='roles;filing_read'), [_mck(MCK_LINES)])[2]['value'] == D(8000000)
    assert resolve_all.apply_other_income_band(_base(oi_flags='roles;interest_split'), [_mck(MCK_LINES)])[2]['value'] == D(8000000)
    # GILD FY2024 shape: the printed line misses the identity by the filer's rounding (1M): the printed figure stays
    assert resolve_all.apply_other_income_band(_base(oi_value='-239000000'), [_mck(MCK_LINES)])[2]['value'] == D(-239000000)


def test_x134_a_label_alone_never_makes_an_interest_line():
    # NEE: 'differential membership interests' is not interest; a band line that is not interest by element or pure label leaves the cell
    lines = MCK_LINES[:4] + [_ln(24, 'IncomeAssociatedWithDifferentialMembershipInterests', 'Income associated with differential membership interests', '283000000.0000')] + MCK_LINES[5:]
    assert resolve_all.apply_other_income_band(_base(), [_mck(lines)])[2]['value'] == D(8000000)
    # a pure 'Interest expense' label on another element is interest (InterestCostsIncurred)
    lines = MCK_LINES[:4] + [_ln(24, 'InterestCostsIncurred', 'Interest expense', '283000000.0000')] + MCK_LINES[5:]
    assert resolve_all.apply_other_income_band(_base(), [_mck(lines)])[2]['value'] == D(-240000000)


def test_x135_cash_total_less_the_filings_restricted_cash():
    acc = '0000896159-24-000003'
    r = _row('cash_and_equivalents', 'mapped', '2621000000', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents=2621000000.0000 [R3.htm:10]', 'bs_family;face', acc)
    f = dict(a=acc, lines='BS|3|10|CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents|0|0|terseLabel|Cash, including restricted cash $172|2621000000.0000', calc='')
    out = resolve_all.apply_cash_less_restricted([dict(r)], {acc: 'RestrictedCash|0|172000000.0000'}, [f])
    assert (out[0]['status'], out[0]['value']) == ('component_sum', D(2449000000))
    assert resolve_all.CASH_BADGE_LESS_RC in out[0]['flags'].split(';')
    # noncurrent restricted cash is never inside the cash line; no restricted fact keeps the line
    assert resolve_all.apply_cash_less_restricted([dict(r)], {acc: 'RestrictedCashAndCashEquivalentsNoncurrent|0|172000000.0000'}, [f])[0]['value'] == D(2621000000)
    assert resolve_all.apply_cash_less_restricted([dict(r)], {}, [f])[0]['value'] == D(2621000000)


def test_x136_any_printed_preferred_line_is_preferred():
    for t in ('DividendsPreferredStock', 'PreferredStockDividendsIncomeStatementImpact', 'PreferredStockRedemptionPremium'):
        assert resolve_all.PREF_LINE.match(t)
    assert not resolve_all.PREF_LINE.match('NetIncomeLossAvailableToCommonStockholdersBasic')
