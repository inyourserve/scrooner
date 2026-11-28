"""Filing reads, M3-cert fixes (2026-11-29): BA DPS text locators and the CRWD interest_income year state.
Run: python3 -m pytest data-team/tags/line_map/tools/test_filing_reads_m3cert.py. Mutation check: see each test's docstring."""
import csv, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filing_reads
from test_filing_reads import cells, read, row, _evidence


def test_text_read_of_zero_replaces_an_inferred_printed_zero_with_the_quote_and_section_locator(tmp_path):
    """(.94) BA DPS FY2020-21: the resolver's printed_zero node ('R6.htm:35' of an FSN report the store keeps no page of) and the
    reader's text read agree on 0; the quote and the section locator are served (stated_zero, no value change). A read that names an
    R page (INTC DPS FY2025) keeps the node. Mutation: drop the printed_zero branch of apply and this fails."""
    quote = '"Dividends declared per share (1) | — | 8.22 | 7.19 | 5.97 | 4.69"'
    rd = read(dp='dividends_per_share', pe='2020-12-31', fy='2020', value='0', acc='0000012927-21-000011', quote=quote)
    rd.update(r_page='ba-20201231.htm Item 6', element='text_stated (Item 6 Selected Financial Data, printed dash)')
    p = cells(tmp_path, rd)
    r0 = row(status='mapped', value=D(0), dp='dividends_per_share', pe='2020-12-31', acc='0000012927-21-000011',
             flags='roles;printed_zero;filing_read', nodes='CommonStockDividendsPerShareDeclared=0 [R6.htm:35] | why: the own face prints a dash')
    out = filing_reads.apply([dict(r0)], p)[0]
    assert out['nodes'] == '' and out['quote'] == quote
    assert out['locator'] == 'ba-20201231.htm Item 6 of 0000012927-21-000011'
    assert out['value'] == D(0) and out['quote_period'] == '2020-12-31' and out['column'] == 'own'
    assert out['flags'].split(';')[:2] == ['filing_read', 'stated_zero']
    # a read that cites an R page agrees with the node and leaves it (INTC DPS FY2025)
    rd2 = dict(rd, r_page='R9.htm; intc-10k text')
    kept = filing_reads.apply([dict(r0)], cells(tmp_path, rd2))[0]
    assert kept['nodes'].startswith('CommonStockDividendsPerShareDeclared') and 'quote' not in kept
    # a zero the resolver read from a face fact (no printed_zero flag) is also untouched
    assert filing_reads.apply([dict(r0, flags='roles')], p)[0]['nodes'].startswith('CommonStockDividendsPerShareDeclared')
    # a non-zero agreeing value is never replaced
    rd3 = dict(rd, value='8.22')
    r3 = dict(r0, value=D('8.22'), flags='roles;printed_zero')
    assert filing_reads.apply([r3], cells(tmp_path, rd3))[0]['nodes'].startswith('CommonStockDividendsPerShareDeclared')


def test_import_accepts_the_interest_income_not_separately_stated_class(tmp_path):
    """Founder 2026-11-28 (session scrooner-36): CRWD interest_income FY2018-20, where only a residual 'Other income (expense), net'
    is printed, is a hidden year of class interest_income_not_separately_stated. Mutation: drop the class from HIDE_RE and this fails."""
    rd = tmp_path / 'resolver'; rd.mkdir()
    with open(rd / 'CRWD.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end']); w.writeheader()
        w.writerow(dict(cik='0001535527', ticker='CRWD', data_point='interest_income', period_end='2019-01-31'))
    skips = tmp_path / 'skips.csv'; skips.write_text('ticker,data_point,fiscal_year,reason\n')
    ev = _evidence(tmp_path, [dict(ticker='CRWD', data_point='interest_income', fiscal_year='2019', outcome='HIDE', element='',
                                   accession='0001535527-20-000006', r_page='R4.htm',
                                   quote='HIDE interest_income_not_separately_stated: "Other income (expense), net"', confidence='medium')])
    kept, skipped = filing_reads.import_files(str(rd), [ev], str(skips))
    assert not skipped and [k['hide_class'] for k in kept] == ['interest_income_not_separately_stated']
