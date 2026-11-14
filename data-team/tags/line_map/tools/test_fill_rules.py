"""Tests for resolve_all.fill_printed_zero_and_comparative (rulings 2026-11-14). Run: python3 this file."""
import os, sys, csv, tempfile
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA


def _csv(rows):
    f = tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, newline='')
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows); f.close()
    return f.name


def _row(acc, dp, ticker='IBM', pe='2020-12-31'):
    return dict(ticker=ticker, accession=acc, period_end=pe, data_point=dp, status='not_presented', value=None, tags='', nodes='', why='', flags='roles')


def test_printed_dash_is_zero_and_comparative_fills_with_the_next_filing():
    os.environ['PRINTED_ZERO'] = _csv([dict(ticker='IBM', period_end='2020-12-31', data_point='share_buybacks', accession='A1', tag='PaymentsForRepurchaseOfCommonStock', stmt='CF', r_line='R6:30', label='Common stock repurchases', evidence='e')])
    os.environ['COMPARATIVE_FILL'] = _csv([dict(ticker='CAT', period_end='2018-12-31', data_point='dividends_per_share', own_accession='A2', accession='N2', tag='CommonStockDividendsPerShareDeclared', loc='R5.htm:9', value='3.36', source='s')])
    rows = RA.fill_printed_zero_and_comparative([_row('A1', 'share_buybacks'), _row('A2', 'dividends_per_share', 'CAT', '2018-12-31'), _row('A3', 'capex')], {})
    z, c, n = rows
    assert z['status'] == 'mapped' and z['value'] == D(0) and 'printed_zero' in z['flags'] and 'R6:30' in z['nodes']
    assert c['value'] == D('3.36') and c['accession'] == 'N2' and c['column'] == 'comparative' and 'comparative_fill' in c['flags']
    assert n['status'] == 'not_presented'   # a line absent from the face stays not_presented


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
