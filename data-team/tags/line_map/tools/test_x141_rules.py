"""Resolver rule X141 (Stage 3 Resolve, 2026-11-29): a printed band line holding interest with other items is served as
other_income_expense_net, and a single financing 'Dividends paid' line holding preferred dividends as dividends_paid, each
with its combined:<label> badge (registry fallback 3 / fallback 2, founder standard 2026-11-22). Filings read 2026-11-29:
AMAT FY2023 10-K R3, NFLX FY2019 10-K R2, SCHW FY2019 10-K R6.
Run: python3 -m pytest data-team/tags/line_map/tools/test_x141_rules.py. Mutation-checked when added (drop the
apply_combined_band_and_dividends body and these fail)."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all

ACC = '0000006951-23-000041'


def _r(dp, nodes, why, flags='roles;only_combined;only_combined_row', acc=ACC, status='combined'):
    return dict(ticker='AMAT', cik='6951', accession=acc, period_end='2023-10-29', data_point=dp, status=status, tags='', value=None,
                nodes=f"{nodes} | why: {why}", why='', flags=flags, column='own')


AMAT_OI = _r('other_income_expense_net', 'OtherNonoperatingIncomeExpense=300000000.0000 [R3.htm:13]',
             "IS lines between OperatingIncomeLoss (R3:11) and pretax (R3:14): 'Interest and other income (expense), net' holds interest "
             "together with other items; no separate other-income line | reported only combined: OtherNonoperatingIncomeExpense")
SCHW_DIV = _r('dividends_paid', 'PaymentsOfDividends=1060000000.0000 [R6.htm:37]; PreferredStockDividendsAndOtherAdjustments=178000000.0000 [R2.htm:27]',
              "the single financing line 'Dividends paid' holds common and preferred dividends (the filing reports "
              "PreferredStockDividendsAndOtherAdjustments=178000000.0000; no separate preferred line): common dividends are not printed",
              flags='cf_family;dividends_incl_preferred;only_combined;only_combined_row', acc='0000316709-20-000012')


def test_x141_band_line_and_dividends_line_are_served_with_the_badge():
    oi, div = resolve_all.apply_combined_band_and_dividends([dict(AMAT_OI), dict(SCHW_DIV)])
    assert (oi['status'], oi['value'], oi['nodes']) == ('mapped', D(300000000), 'OtherNonoperatingIncomeExpense=300000000 [R3.htm:13]')
    fl = oi['flags'].split(';')
    assert 'combined:interest income' in fl and not {'only_combined', 'only_combined_row'} & set(fl)
    assert (div['status'], div['value'], div['nodes']) == ('mapped', D(1060000000), 'PaymentsOfDividends=1060000000 [R6.htm:37]')
    assert 'combined:Dividends paid' in div['flags'].split(';')


def test_x141_badges_fit_the_registry_combined_step():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'pipeline', 'src'))
    from scrooner_pipeline.metrics import registry
    oi, div = resolve_all.apply_combined_band_and_dividends([dict(AMAT_OI), dict(SCHW_DIV)])
    for r in (oi, div):
        b = registry.badge_for(r['data_point'], 'general', {'decision': r['status'], 'flags': r['flags'], 'nodes': r['nodes']})
        assert b and b.startswith('combined:'), (r['data_point'], b)


def test_x141_leaves_every_other_shape_combined():
    # an interest-only label ('Interest and investment income', HD) is not an other-income line
    hd = _r('other_income_expense_net', 'InvestmentIncomeInterest=1.0000 [R3.htm:13]', "x: 'Interest and investment income' holds interest")
    # two band lines, or a negated node, are not one printed line
    two = _r('other_income_expense_net', 'A=1.0000 [R3.htm:13]; B=2.0000 [R3.htm:14]', "x: 'Interest and other income, net' holds")
    neg = _r('other_income_expense_net', '-A=1.0000 [R3.htm:13]', "x: 'Interest and other income, net' holds")
    # one printed line, one data point (X130): the filing's interest_income row already serves the element
    ii = _r('interest_income', 'OtherNonoperatingIncomeExpense=300000000.0000 [R3.htm:13]', 'x', flags='roles', status='mapped')
    # a dividends line without the preferred evidence flag, or another element
    div_plain = dict(SCHW_DIV, flags='cf_family;only_combined;only_combined_row')
    div_other = dict(SCHW_DIV, nodes=SCHW_DIV['nodes'].replace('PaymentsOfDividends=', 'PaymentsOfDividendsCommonStock='))
    out = resolve_all.apply_combined_band_and_dividends([hd, two, neg, dict(AMAT_OI), ii, div_plain, div_other])
    assert [r['status'] for r in out] == ['combined', 'combined', 'combined', 'combined', 'mapped', 'combined', 'combined']
