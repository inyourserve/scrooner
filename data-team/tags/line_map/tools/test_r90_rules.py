"""Resolver .90 rules X125-X129 and the 2026-11-23 import. Run: python3 -m pytest data-team/tags/line_map/tools/test_r90_rules.py.
Each test fails with its rule removed (mutation-checked when added)."""
import csv, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filing_reads, resolve_all


def _r(dp, status, nodes='', why='', value=None, pe='2022-12-31', cik='1551182', acc='0001551182-23-000004', flags='roles'):
    return dict(ticker='T', cik=cik, accession=acc, period_end=pe, data_point=dp, status=status, tags='', value=value, r_page='',
                nodes=nodes, why=why, source='roles', calc_check='', flags=flags, column='own')


def test_x125_interest_expense_net_and_interest_and_dividend_income_lines_are_served_with_a_combined_badge():
    # ETN FY2022 'Interest expense - net' (InterestIncomeExpenseNet, stored -144) -> 144, badge combined:Interest expense - net;
    # QCOM FY2017 note fact InvestmentIncomeInterestAndDividend 619 -> 619, badge combined:Interest and dividend income
    rows = [
        _r('interest_expense', 'combined', 'InterestIncomeExpenseNet=-144000000.0000 [R3.htm:5]',
           "IS face prints only the combined line InterestIncomeExpenseNet 'Interest expense - net'", flags='roles'),
        _r('interest_income', 'combined', 'InvestmentIncomeInterestAndDividend=619000000.0000 [NOTE]',
           'the element InvestmentIncomeInterestAndDividend reports investment income', flags='roles;label_beyond'),
        # wider labels stay combined: 'Investment and other income', 'net of capitalized interest' (the expense itself)
        _r('interest_income', 'combined', 'InvestmentIncomeInterestAndDividend=12000000.0000 [R4.htm:9]',
           "its label 'Investment and other income' names more than interest"),
        _r('interest_expense', 'combined', 'InterestIncomeExpenseNonoperatingNet=-330000000.0000 [R2.htm:14]',
           "IS face prints only the combined line 'Interest expense, net of capitalized interest of $23'"),
    ]
    out = resolve_all.apply_combined_interest_lines(rows, [])
    assert (out[0]['status'], out[0]['value'], out[0]['flags']) == ('mapped', D(144000000), 'roles;combined:Interest expense - net')
    assert out[0]['nodes'] == '-InterestIncomeExpenseNet=-144000000 [R3.htm:5]'
    assert (out[1]['status'], out[1]['value'], out[1]['flags']) == ('mapped', D(619000000), 'roles;combined:Interest and dividend income')
    assert [r['status'] for r in out[2:]] == ['combined', 'combined']


def test_x126_a_stated_table_row_or_sentence_fills_every_stated_year(tmp_path):
    # VZ FY2015 EX-13 'Interest income $ 115 $ 108 $ 64' fills FY2014 (108) and FY2013 (64) as comparative statements;
    # XOM 'was $ 648 million, $ 612 million, and $ 672 million for 2022, 2021, and 2020' pairs amounts with the named years
    p = tmp_path / 'td.csv'
    cols = ['cik', 'ticker', 'data_point', 'period_end', 'accession', 'own', 'decision', 'value_source', 'value', 'section', 'locator', 'quote_period', 'quote', 'why']
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        w.writerow(dict(cik='0000732712', ticker='VZ', data_point='interest_income', period_end='2015-12-31', accession='0001193125-16-473367', own='1',
                        decision='mapped', value_source='text_stated', value='115000000', section='ex13', locator='VZ FY2015 EX-13', quote_period='2015-12-31',
                        quote='Interest income $ 115 $ 108 $ 64', why='w'))
        w.writerow(dict(cik='0000034088', ticker='XOM', data_point='sbc', period_end='2022-12-31', accession='0000034088-23-000020', own='1',
                        decision='mapped', value_source='text_stated', value='648000000', section='item8_notes', locator='XOM 10-K p. 103', quote_period='2022-12-31',
                        quote='The compensation cost was $ 648 million, $ 612 million, and $ 672 million for 2022, 2021, and 2020, respectively.', why='w'))
    rows = [_r('interest_income', 'not_presented', pe='2014-12-31', cik='732712', acc='0001193125-15-000001'),
            _r('interest_income', 'not_presented', pe='2015-12-31', cik='732712', acc='0001193125-16-473367'),
            _r('sbc', 'not_presented', pe='2021-12-31', cik='34088', acc='0000034088-22-000011'),
            _r('sbc', 'not_presented', pe='2020-12-31', cik='34088', acc='0000034088-21-000012')]
    out = resolve_all.apply_text_disclosures(rows, str(p))
    assert [(r['status'], r['value']) for r in out] == [('mapped', D(108000000)), ('mapped', D(115000000)), ('mapped', D(612000000)), ('mapped', D(672000000))]
    assert out[0]['column'] == 'comparative' and out[0]['accession'] == '0001193125-16-473367' and out[0]['quote_period'] == '2014-12-31'
    assert 'stated_in_later_filing' in out[0]['flags']


def test_x127_the_notes_pretax_expense_serves_the_whole_sbc_row_when_no_add_back_and_no_gross_equity_line():
    # MO: FY2015 one award type (RS/RSU 51), FY2017 two award types (49 + 6); no CF add-back, no equity-statement sbc line
    rows = [_r('sbc', 'not_presented', why='share-based compensation expense is reported only by award type (RestrictedAndDeferredStock 51000000); one award type does not prove the total',
               pe='2015-12-31', cik='764180', flags='cf_family;reported_by_award_type'),
            _r('sbc', 'component_sum', value=D(55000000), pe='2017-12-31', cik='764180', flags='cf_family;award_type_member_sum')]
    out = resolve_all.apply_sbc_note_expense(rows)
    assert (out[0]['status'], out[0]['value']) == ('mapped', D(51000000))
    assert out[0]['flags'] == 'cf_family;as_printed:note' and out[1]['flags'] == 'cf_family;award_type_member_sum;as_printed:note'
    # a company with a CF add-back in any year keeps its award-type rows untouched
    rows2 = [_r('sbc', 'not_presented', why='reported only by award type (RestrictedStockUnitsRSU 9000000)', pe='2015-12-31', cik='1', flags='cf_family;reported_by_award_type'),
             _r('sbc', 'component_sum', value=D(20), pe='2017-12-31', cik='1', flags='cf_family;award_type_member_sum'),
             _r('sbc', 'mapped', value=D(30), pe='2018-12-31', cik='1', flags='cf_family')]
    out2 = resolve_all.apply_sbc_note_expense(rows2)
    assert out2[0]['status'] == 'not_presented' and 'as_printed:note' not in out2[1]['flags']
    # CB: a filing read REPLACED award-type sums with the equity statement's figure -> the note is not the row's source
    rows3 = [_r('sbc', 'component_sum', value=D(156), pe='2014-12-31', cik='3', flags='cf_family;award_type_member_sum'),
             _r('sbc', 'mapped', value=D(286), pe='2021-12-31', cik='3', flags='cf_family;filing_read;text_stated;replaces:component_sum')]
    assert 'as_printed:note' not in resolve_all.apply_sbc_note_expense(rows3)[0]['flags']
    # MO FY2016 filled by a read (replaces:not_presented, the note figure) keeps the note row and carries the badge
    rows4 = [_r('sbc', 'component_sum', value=D(55), pe='2017-12-31', cik='4', flags='cf_family;award_type_member_sum'),
             _r('sbc', 'mapped', value=D(44), pe='2016-12-31', cik='4', flags='cf_family;filing_read;text_stated;replaces:not_presented')]
    assert all('as_printed:note' in r['flags'] for r in resolve_all.apply_sbc_note_expense(rows4))


def test_x128_a_per_share_value_at_the_filers_monetary_scale_is_divided_and_flagged():
    # STX DPS FY2022 2,770,000 beside 2.66 / 2.80 / 2.80 in the other years -> 2.77, flag filer_scale_error
    rows = [_r('dividends_per_share', 'mapped', 'CommonStockDividendsPerShareDeclared=2770000.0000 [R9.htm:4]', value=D(2770000), pe='2022-07-01', cik='1137789')]
    rows += [_r('dividends_per_share', 'mapped', value=D(v), pe=pe, cik='1137789') for v, pe in (('2.66', '2021-07-02'), ('2.80', '2023-06-30'), ('2.80', '2024-06-28'))]
    out = resolve_all.apply_per_share_scale_guard(rows)
    assert out[0]['value'] == D('2.77') and 'filer_scale_error' in out[0]['flags'] and out[0]['nodes'].startswith('CommonStockDividendsPerShareDeclared=2.77 ')
    # a company whose per-share figures are all large (BRK-A) is never touched
    big = [_r('basic_eps', 'mapped', value=D(v), pe=pe, cik='2') for v, pe in (('61000', '2021-12-31'), ('59000', '2022-12-31'), ('66000', '2023-12-31'))]
    assert [r['value'] for r in resolve_all.apply_per_share_scale_guard(big)] == [D(61000), D(59000), D(66000)]


def _write_read(tmp_path, name, rows):
    cols = ['ticker', 'data_point', 'fiscal_year', 'outcome', 'value', 'element', 'accession', 'r_page', 'quote', 'rule_proposal', 'confidence']
    p = tmp_path / name
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, '') for c in cols})
    return str(p)


def _resolver_dir(tmp_path, dp, pes):
    rd = tmp_path / 'resolver'; rd.mkdir(exist_ok=True)
    with open(rd / 'NVDA.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end']); w.writeheader()
        for pe in pes: w.writerow(dict(cik='0001045810', ticker='NVDA', data_point=dp, period_end=pe))
    skips = tmp_path / 'skips.csv'; skips.write_text('ticker,data_point,fiscal_year,reason\n')
    return str(rd), str(skips)


def test_x129_a_hide_read_takes_its_class_from_the_rule_proposal_when_the_quote_is_the_search_evidence(tmp_path):
    # NVDA cash_paid_for_interest FY2026: outcome HIDE, the quote is the full-text search, the rule text says 'HIDE disclosure_discontinued'
    rd, skips = _resolver_dir(tmp_path, 'cash_paid_for_interest', ['2026-01-25'])
    p = _write_read(tmp_path, 'NVDA-2026-11-23.csv', [dict(ticker='NVDA', data_point='cash_paid_for_interest', fiscal_year='2026', outcome='HIDE',
                                                            accession='0001045810-26-000021', quote='The FY2026 10-K was read in full; full-text search 0 hits',
                                                            rule_proposal='HIDE disclosure_discontinued (discontinued-disclosure ruling 2026-11-22)')])
    kept, skipped = filing_reads.import_files(rd, [p], skips)
    assert not skipped and kept[0]['hide_class'] == 'disclosure_discontinued'


def test_the_2026_11_23_read_supersedes_the_2026_11_22_read_of_the_same_cell(tmp_path):
    rd, skips = _resolver_dir(tmp_path, 'total_debt', ['2019-01-27'])
    base = dict(ticker='NVDA', data_point='total_debt', fiscal_year='2019', outcome='VALUE', accession='0001045810-19-000023', r_page='R4.htm')
    old = _write_read(tmp_path, 'NVDA-2026-11-22.csv', [dict(base, value='1991000000', quote='old')])
    new = _write_read(tmp_path, 'NVDA-2026-11-23.csv', [dict(base, value='1988000000', quote='new')])
    kept, skipped = filing_reads.import_files(rd, [old, new], skips)
    assert [(k['value'], k['source_file']) for k in kept] == [('1988000000', 'NVDA-2026-11-23.csv')]
    assert 'superseded by the 2026-11-23 read' in skipped[0]['reason']
