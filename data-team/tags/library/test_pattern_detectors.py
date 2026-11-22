"""Pattern detectors (founder 2026-11-22): each gap class has a detector that counts every occurrence; one tiny fixture each."""
import csv, os, sys
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pattern_detectors as pd   # noqa: E402

A = '0000000001-25-000001'


def res(dp, pe, value, nodes='', decision='mapped', flags='roles', quote='', tk='T', acc=A):
    return dict(cik='0000000001', ticker=tk, data_point=dp, period_end=pe, grain='FY', decision=decision, nodes=nodes, value=value,
                accession=acc, flags=flags, quote=quote)


def exp(dp, pe, display, value='', cls='PROVEN', parts='', tag='', hide_class='', tk='T', acc=A):
    return dict(ticker=tk, data_point=dp, fiscal_year=pe[:4], period_end=pe, display=display, shown_value=value, parts=parts,
                tag=tag, hide_class=hide_class, reason_code='', accession=acc, **{'class': cls})


def test_p01_text_stated_years():
    # GILD shape: a table line states three years, the resolver serves only the own year
    rows = [res('interest_income', '2024-12-31', '281000000', flags='roles;text_stated', quote='Interest income ( 281 ) ( 376 ) ( 106 )'),
            res('interest_income', '2023-12-31', '', decision='not_presented')]
    hits = pd.p01_text_stated_years(rows)
    assert [(h['period_end'][:4], h['pattern_id']) for h in hits] == [('2023', 'P01'), ('2022', 'P01')]
    # once 376 is served (any data point) only 106 is open; figures in different statements never form one run
    rows.append(res('interest_income', '2023-12-31', '376000000'))
    assert [h['period_end'][:4] for h in pd.p01_text_stated_years(rows)] == ['2022']
    solo = [res('sbc', '2024-12-31', '74000000', flags='text_stated', quote='R&D expenses were $74 million in FY2024; Note 9 shows 12')]
    assert pd.p01_text_stated_years(solo) == []
    # words: '$1.4 billion, $1.5 billion and $0.6 billion' is one run; a served 1.512B rounds to 1.5B
    cs = [res('cash_paid_for_interest', '2026-07-31', '1400000000', flags='text_stated',
              quote='cash paid for interest was $1.4 billion, $1.5 billion and $0.6 billion for fiscal 2026, 2025, and 2024'),
          res('cash_paid_for_interest', '2025-07-31', '1512000000')]
    assert [h['period_end'][:4] for h in pd.p01_text_stated_years(cs)] == ['2024']


def test_p02_coarser_duplicate():
    r = res('total_debt', '2023-01-31', '4563000000', nodes='ShortTermBorrowings=400000000.0000 [R5.htm:16]; LongTermDebtCurrent=4163000000.0000 [R5.htm:20]',
            decision='component_sum')
    r['data_point'] = 'total_debt'
    dup = {(A, 'ShortTermBorrowings', '2023-01-31', 0): [(D('372000000'), -6), (D('400000000'), -8)]}
    (h,) = pd.p02_coarser_duplicate([r], dup)
    assert h['element'] == 'ShortTermBorrowings' and '372000000' in h['detail']
    # the finer figure served: no hit; two different figures (not a rounding of each other): no hit
    r2 = dict(r, nodes='ShortTermBorrowings=372000000.0000 [R5.htm:16]')
    assert pd.p02_coarser_duplicate([r2], dup) == []
    assert pd.p02_coarser_duplicate([r], {(A, 'ShortTermBorrowings', '2023-01-31', 0): [(D('310000000'), -6), (D('400000000'), -8)]}) == []
    # the export layer: a shown part at the coarser figure
    e = exp('total_debt', '2023-01-31', 'SHOWN_VALUE', '4563000000', parts=f'ShortTermBorrowings=400000000@{A}#R5;LongTermDebtCurrent=4163000000@{A}#R5')
    (h,) = pd.p02_coarser_duplicate([], dup, [e])
    assert h['layer'] == 'export'


def test_p03_share_scale():
    rows = [res('net_income', '2019-12-31', '7189000000'), res('basic_eps', '2019-12-31', '6.40'),
            res('weighted_basic_shares', '2019-12-31', '1123000'), res('weighted_diluted_shares', '2019-12-31', '1129000000')]
    (h,) = pd.p03_share_scale(rows)
    assert h['data_point'] == 'weighted_basic_shares' and '10^-3' in h['detail']
    shown = [exp('net_income', '2019-12-31', 'SHOWN_VALUE', '7189000000'), exp('basic_eps', '2019-12-31', 'SHOWN_VALUE', '6.40'),
             exp('shares_outstanding', '2019-12-31', 'SHOWN_VALUE', '1085000000000')]
    (h,) = pd.p03_share_scale(shown, 'export')
    assert h['layer'] == 'export' and '10^3' in h['detail']
    tiny_eps = [res('net_income', '2019-12-31', '1000000'), res('basic_eps', '2019-12-31', '0.01'), res('weighted_basic_shares', '2019-12-31', '100')]
    assert pd.p03_share_scale(tiny_eps) == []


def test_p04_round_share_count():
    rows = [res('shares_outstanding', '2023-09-30', '1800000000', nodes='CommonStockSharesOutstanding=1800000000.0000 [R3.htm:30]'),
            res('shares_outstanding', '2022-09-30', '1824000000', nodes='CommonStockSharesOutstanding=1824000000.0000 [R3.htm:30]'),
            res('shares_outstanding', '2021-09-30', '1800000000', nodes='CommonStockSharesOutstanding[EquityComponents=CommonStock]=1800000000.0000 [R6.htm:3]')]
    (h,) = pd.p04_round_share_count(rows)
    assert h['period_end'] == '2023-09-30' and h['element'] == 'CommonStockSharesOutstanding'


def test_p05_p06_hidden_presented():
    tags = {'other_income_expense_net': {'OtherNonoperatingIncomeExpense'}, 'shares_outstanding': {'CommonStockSharesOutstanding'}}
    rows = [exp('other_income_expense_net', '2015-01-31', 'HIDDEN_YEAR', cls='REASON', hide_class='line_presented_combined'),
            exp('shares_outstanding', '2024-01-31', 'HIDDEN_YEAR', cls='REASON', hide_class='structural_not_presented'),
            exp('shares_outstanding', '2023-01-31', 'HIDDEN_YEAR', cls='REASON', hide_class='pre_filing')]
    k15, q24 = '0000000001-15-000001', '0000000001-24-000105'
    presented = {'T': [(k15, '10-K', '2015-01-31', 'OtherNonoperatingIncomeExpense', '2015-01-31', 4),
                       (q24, '10-Q', '2024-04-30', 'CommonStockSharesOutstanding', '2024-01-31', 0),
                       (q24, '10-Q', '2024-04-30', 'OtherNonoperatingIncomeExpense', '2024-01-31', 4)]}
    hits = pd.p05_p06_hidden_presented(rows, presented, tags)
    assert [(h['pattern_id'], h['data_point'], h['accession']) for h in hits] == [
        ('P06', 'other_income_expense_net', k15), ('P05', 'shares_outstanding', q24)]
    # the row's elements only: a part of a sum is not the row presented
    assert pd.dp_tags_of(os.path.join(HERE, 'nonexistent.csv'), [res('sbc', '2024-12-31', '5', nodes='ShareBasedCompensation=5.0000 [R7.htm:4]')]) == {}


def test_p07_line_double_count():
    n = 'SellingGeneralAndAdministrativeExpense=100.0000 [R2.htm:11]'
    rows = [res('sga_expense', '2022-08-31', '100', nodes=n), res('operating_expenses', '2022-08-31', '100', nodes=n),
            # a total and its part sharing a line is fine; so are basic/diluted EPS on one BasicAndDiluted line
            res('operating_expenses', '2021-08-31', '150', decision='component_sum', nodes='SellingGeneralAndAdministrativeExpense=100.0000 [R2.htm:11]; ResearchAndDevelopmentExpense=50.0000 [R2.htm:12]'),
            res('sga_expense', '2021-08-31', '100', nodes='SellingGeneralAndAdministrativeExpense=100.0000 [R2.htm:11]'),
            res('basic_eps', '2021-08-31', '1.2', nodes='EarningsPerShareBasicAndDiluted=1.2 [R2.htm:20]'),
            res('diluted_eps', '2021-08-31', '1.2', nodes='EarningsPerShareBasicAndDiluted=1.2 [R2.htm:20]'),
            # siblings that cannot share a printed number
            res('interest_expense', '2021-08-31', '9', nodes='InterestExpense=9.0000 [R2.htm:14]'),
            res('operating_expenses', '2020-08-31', '0', decision='component_sum', nodes='InterestExpense=9.0000 [R2.htm:14]; CostsAndExpenses=1.0000 [R2.htm:15]')]
    rows[-1]['period_end'] = '2021-08-31'
    # a difference of printed lines (opex = gross profit - operating income) reuses lines and is no double count
    rows += [res('gross_profit', '2019-08-31', '40', nodes='GrossProfit=40.0000 [R2.htm:3]'),
             res('operating_expenses', '2019-08-31', '30', decision='component_sum', nodes='GrossProfit=40.0000 [R2.htm:3]; -OperatingIncomeLoss=10.0000 [R2.htm:9]')]
    hits = pd.p07_line_double_count(rows)
    pairs = sorted({(h['period_end'][:4], h['data_point']) for h in hits})
    assert pairs == [('2021', 'interest_expense'), ('2021', 'operating_expenses'), ('2022', 'operating_expenses'), ('2022', 'sga_expense')]


def test_p08_derived_parts():
    B = '0000000001-24-000001'
    rows = [exp('gross_profit', '2015-12-31', 'SHOWN_VALUE', '10', cls='DERIVED'),
            exp('gross_profit', '2016-12-31', 'SHOWN_VALUE', '10', cls='DERIVED', parts=f'Revenues=30@{A}#R4;-CostOfRevenue=20@{B}#R4'),
            exp('gross_profit', '2017-12-31', 'SHOWN_VALUE', '10', cls='DERIVED', parts=f'Revenues=30@{A}#R4;-CostOfRevenue=20@{A}#R4'),
            exp('gross_profit', '2018-12-31', 'HIDDEN_YEAR', cls='DERIVED')]
    hits = pd.p08_derived_parts(rows, [res('shares_outstanding', '2019-12-31', '5', decision='derived_not_printed', nodes='')])
    assert [(h['period_end'][:4], h['layer']) for h in hits] == [('2015', 'export'), ('2016', 'export'), ('2019', 'resolver')]


def test_registry_rows_name_a_detector_a_test_and_a_card():
    pats = pd.load_patterns()
    assert [p['pattern_id'] for p in pats] == [f'P0{i}' for i in range(1, 9)]
    tests = open(os.path.join(HERE, 'test_pattern_detectors.py')).read()
    for p in pats:
        assert hasattr(pd, p['detector'].split('.')[-1]), p
        assert p['test'].split('::')[-1] in tests, p
        assert os.path.exists(os.path.join(pd.ROOT, p['card'])), p


def test_run_keeps_previous_fsn_hits_without_live(tmp_path):
    prev = [dict(pattern_id='P06', ticker='T', data_point='x', period_end='2015-01-31', element='E', accession=A, layer='export', source='fsn', detail='d')]
    hits = pd.run([], [], previous=prev)
    assert [h['source'] for h in hits] == ['previous:fsn']
    assert pd.run([], [], dup={}, presented={}, previous=prev) == []
