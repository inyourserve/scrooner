"""Resolver data refresh (data_refresh.py, .github/workflows/resolver-data-refresh.yml and filings-extract-chain.yml):
scope selection and the BAD-not-increasing gate. Run: python3 -m pytest data-team/tags/line_map/tools/test_data_refresh.py.
Each test names the mutation it catches (checked by hand on 2026-11-22)."""
import csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_refresh as dr

COLS = ['cik', 'ticker', 'data_point', 'period_end', 'grain', 'decision', 'nodes', 'value', 'accession', 'column', 'calc_check',
        'flags', 'quote', 'locator', 'quote_period', 'resolver_version']


def _resolver(tmp_path, rows_by_ticker):
    d = tmp_path / 'resolver'; d.mkdir()
    for t, rows in rows_by_ticker.items():
        with open(d / f'{t}.csv', 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader()
            for r in rows: w.writerow({c: r.get(c, '') for c in COLS} | {'ticker': t})
    return d


def _row(cik, pe, acc, dp='revenue', value='100', decision='mapped', column='own'):
    return dict(cik=cik, data_point=dp, period_end=pe, grain='D', decision=decision, value=value, accession=acc, column=column)


def test_new_filing_selects_only_a_newer_annual_filing_the_resolver_has_not_seen(tmp_path):
    """Mutation: drop `per > mx` -> the old filing the resolver dropped on purpose (X110 duplicate) re-selects ABC every
    night and the chain never converges; drop the form check -> a 10-Q or 10-K/A selects DEF."""
    d = _resolver(tmp_path, {'ABC': [_row('0000000001', '2024-12-31', '0000000001-25-000001')],
                             'DEF': [_row('0000000002', '2025-06-30', '0000000002-25-000009')]})
    latest = dr.latest_by_cik(d)
    fsn = [dict(cik='1', accession='0000000001-21-000003', form='10-K', period='2020-12-31'),     # old, dropped by X110
           dict(cik='2', accession='0000000002-26-000001', form='10-Q', period='2025-09-30'),     # a quarter
           dict(cik='2', accession='0000000002-26-000002', form='10-K/A', period='2025-12-31'),   # an amendment
           dict(cik='9', accession='0000000009-26-000001', form='10-K', period='2025-12-31'),     # not a resolver company
           dict(cik='1', accession='0000000001-25-000001', form='10-K', period='2024-12-31')]     # already resolved
    assert dr.new_filing_ciks(latest, fsn) == []
    fsn.append(dict(cik='0000000001', accession='0000000001-26-000004', form='10-K', period='2025-12-31'))
    assert dr.new_filing_ciks(latest, fsn) == ['0000000001']


def test_new_filing_ignores_comparative_and_before_rows_for_the_latest_period(tmp_path):
    """A comparative or BEFORE: row never counts as the company's latest resolved period. Mutation: drop the column/BEFORE
    filter in latest_by_cik -> a later comparative row hides the new filing."""
    d = _resolver(tmp_path, {'ABC': [_row('0000000001', '2023-12-31', '0000000001-24-000001'),
                                     _row('0000000001', '2025-12-31', '0000000001-24-000001', column='comparative')]})
    fsn = [dict(cik='1', accession='0000000001-26-000004', form='10-K', period='2025-12-31')]
    assert dr.new_filing_ciks(dr.latest_by_cik(d), fsn) == ['0000000001']


def test_push_scope_is_fix_file_tickers_plus_changed_cells_and_only_resolver_companies():
    """Mutation: drop cells_changed_tickers from the push scope -> a skip-list change (no fix file of GHI changed) leaves
    GHI's cells ahead of its resolver file; drop the `t in tick_cik` filter -> NEWCO (no resolver file) is resolved."""
    tick_cik = {'ABC': '0000000001', 'GHI': '0000000003', 'XYZ': '0000000004'}
    old = [dict(ticker='GHI', data_point='sbc', fiscal_year='2020', value='5'), dict(ticker='XYZ', data_point='sbc', fiscal_year='2020', value='7')]
    new = [dict(ticker='GHI', data_point='sbc', fiscal_year='2020', value='6'), dict(ticker='XYZ', data_point='sbc', fiscal_year='2020', value='7')]
    changed = ['data-team/strategy/open-shown-fixes/ABC-2026-11-23.csv', 'data-team/strategy/open-shown-fixes/NEWCO-2026-11-23.csv',
               'data-team/strategy/open-shown-fixes/README.md', 'data-team/tags/line_map/resolver/XYZ.csv']
    assert dr.scope('push', tick_cik, changed_paths=changed, old_cells=old, new_cells=new) == ['ABC', 'GHI']


def test_extract_scope_is_the_extract_ciks_and_dispatch_defaults_to_all():
    tick_cik = {'ABC': '0000000001', 'GHI': '0000000003', 'XYZ': '0000000004'}
    assert dr.scope('extract', tick_cik, extract_ciks=['3', '0000000004', '77']) == ['GHI', 'XYZ']
    assert dr.scope('dispatch', tick_cik, tickers=['']) == ['ABC', 'GHI', 'XYZ']
    assert dr.scope('dispatch', tick_cik, tickers=['XYZ', 'NOPE']) == ['XYZ']


def test_covers_needs_every_scope_cik_in_the_manifest():
    assert dr.covers('1,3,4', ['0000000003', '4'])
    assert not dr.covers('1,3', ['0000000003', '4'])


def test_merge_cells_moves_only_the_scope():
    """Mutation: return new_rows -> XYZ's committed cells move ahead of its (unrefreshed) resolver file."""
    old = [dict(ticker='ABC', v='old'), dict(ticker='XYZ', v='old'), dict(ticker='ZZZ', v='old')]
    new = [dict(ticker='ABC', v='new'), dict(ticker='NEW', v='new'), dict(ticker='XYZ', v='new')]
    got = dr.merge_cells(old, new, ['ABC', 'NEW'])
    assert got == [dict(ticker='ABC', v='new'), dict(ticker='NEW', v='new'), dict(ticker='XYZ', v='old'), dict(ticker='ZZZ', v='old')]


def _read(t, dp, fy, value):
    return dict(ticker=t, data_point=dp, fiscal_year=fy, outcome='VALUE', value=value, rule_proposal='', quote='')


def test_oracle_counts_blank_and_off_by_more_than_0_06_percent(tmp_path):
    """Mutation: TOL 0.0006 -> 0.006 hides the 0.1% miss; drop the BLANK filter -> a combined row's value counts as served."""
    d = _resolver(tmp_path, {'ABC': [_row('1', '2024-12-31', 'a', 'revenue', '100060'),          # +0.06%: OK
                                     _row('1', '2024-12-31', 'a', 'sbc', '1001'),                # +0.1%: BAD
                                     _row('1', '2024-12-31', 'a', 'capex', '50', 'combined'),    # blank: BAD
                                     _row('1', '2024-12-31', 'a', 'dps', '0'),                   # 0 = 0: OK
                                     _row('1', '2024-12-31', 'b', 'goodwill', '7', column='comparative')]})   # comparative only: OK
    reads = [_read('ABC', 'revenue', '2024', '100000'), _read('ABC', 'sbc', '2024', '1000'), _read('ABC', 'capex', '2024', '50'),
             _read('ABC', 'dps', '2024', '0'), _read('ABC', 'goodwill', '2024', '7'), _read('NOPE', 'revenue', '2024', '1')]
    o = dr.oracle(d, reads)
    assert (o['bad'], o['checked'], o['no_period']) == (2, 5, 1)
    assert [c.split('|')[1] for c in o['bad_cells']] == ['capex', 'sbc']


def test_latest_value_reads_takes_the_latest_dated_file(tmp_path):
    """A later HIDE read retires an earlier VALUE read of the same cell (X109 precedence)."""
    hdr = 'ticker,data_point,fiscal_year,outcome,value,element,accession,r_page,quote,rule_proposal,confidence\n'
    (tmp_path / 'ABC-2026-11-17.csv').write_text(hdr + 'ABC,sbc,2020,VALUE,5,,,,,,\nABC,capex,2020,VALUE,9,,,,,,\n')
    (tmp_path / 'ABC-2026-11-22.csv').write_text(hdr + 'ABC,sbc,2020,HIDE,,,,,HIDE never_reported x,,\nABC,capex,2020,VALUE,10,,,,,,\n')
    got = dr.latest_value_reads(sorted(tmp_path.glob('*.csv')))
    assert [(r['data_point'], r['value']) for r in got] == [('capex', '10')]


def test_gate_refuses_a_bad_increase_or_failed_tests_and_passes_equal_or_fewer():
    """Mutation: `>` -> `>=` refuses a no-op refresh; dropping the BAD check lets a regression through; dropping the tests
    check commits on red tests."""
    b = dict(bad=9, bad_cells=[f'c{i}' for i in range(9)])
    assert dr.gate(True, b, dict(bad=9, bad_cells=b['bad_cells']))[0]
    assert dr.gate(True, b, dict(bad=3, bad_cells=['c1', 'c2', 'c3']))[0]
    ok, why = dr.gate(True, b, dict(bad=10, bad_cells=b['bad_cells'] + ['NEW|sbc|2024']))
    assert not ok and 'oracle BAD rose 9 -> 10' in why[0] and 'NEW|sbc|2024' in why[0]
    ok, why = dr.gate(False, b, b)
    assert not ok and why == ['line_map tests failed']


def test_next_version_suffixes_the_latest_rule_release():
    head = '| version | date |\n|---|---|\n'
    assert dr.next_version(head + '| .88 | x |\n| .89 | x |\n') == '.89.d1'
    assert dr.next_version(head + '| .89 | x |\n| .89.d1 | x |\n| .89.d2 | x |\n') == '.89.d3'
    assert dr.next_version(head + '| .89.d2 | x |\n| .90 | x |\n') == '.90.d1'


def test_fix_file_tickers_reads_dotted_tickers():
    assert dr.fix_file_tickers(['data-team/strategy/open-shown-fixes/BRK.B-2026-11-23.csv', 'x/open-shown-fixes/AAPL-2026-11-17.csv',
                                'data-team/strategy/open-shown-fixes/_notes.csv']) == {'BRK.B', 'AAPL'}
