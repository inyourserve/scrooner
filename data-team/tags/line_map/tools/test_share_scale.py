"""Tests for resolve_all.apply_share_scale (rule X114, resolver .88). Run: python3 -m pytest this file.
Mutation check: with apply_share_scale returning its rows untouched, the scaling tests fail."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA


def _r(dp, v, nodes='', status='mapped', pe='2020-12-31'):
    return dict(cik='0001163165', ticker='COP', accession='0001562762-21-000027', period_end=pe, data_point=dp, status=status,
                value=D(v), nodes=nodes, why='', flags='roles')


def _period(ni='-2701000000', eps='-2.51', pe='2020-12-31'):
    return [_r('net_income', ni, pe=pe), _r('basic_eps', eps, pe=pe)]


def test_weighted_count_stored_at_the_printed_thousands_scale_is_scaled_with_its_node():
    # COP FY2020 10-K R2: 'Average Common Shares Outstanding (in thousands) Basic 1,078,030', stored 1078030
    rows = _period() + [_r('weighted_basic_shares', 1078030, 'WeightedAverageNumberOfSharesOutstandingBasic=1078030.0000 [R2.htm:29]')]
    r = RA.apply_share_scale(rows)[-1]
    assert r['value'] == D(1078030000) and r['nodes'] == 'WeightedAverageNumberOfSharesOutstandingBasic=1078030000 [R2.htm:29]'
    assert 'filer_scale_error' in r['flags'] and 'share_scale_x1000' in r['flags']


def test_derived_year_end_count_scales_every_part_and_millions_scale_is_found():
    # RTX FY2014: issued 1,423,684 - treasury 514,309 (thousands) = 909,375; NI 6,220M / EPS 6.92 = 899M (year-end within 15%)
    rows = _period('6220000000', '6.92', '2014-12-31') + [_r('shares_outstanding', 909375, 'CommonStockSharesIssued=1423684.0000 [R5.htm:7]; -TreasuryStockShares=514309.0000 [R5.htm:8]', 'derived', '2014-12-31')]
    r = RA.apply_share_scale(rows)[-1]
    assert r['value'] == D(909375000) and r['nodes'] == 'CommonStockSharesIssued=1423684000 [R5.htm:7]; -TreasuryStockShares=514309000 [R5.htm:8]'
    # SYK FY2014: outstanding 378 (millions); NI 515M / EPS 1.36 = 378.7M
    rows = _period('515000000', '1.36', '2014-12-31') + [_r('shares_outstanding', 378, 'CommonStockSharesOutstanding=378.0000 [BSP]', pe='2014-12-31')]
    r = RA.apply_share_scale(rows)[-1]
    assert r['value'] == D(378000000) and 'share_scale_x1000000' in r['flags']


def test_full_counts_split_gaps_and_periods_without_eps_stay():
    full = _period() + [_r('weighted_basic_shares', 1078030000, 'WeightedAverageNumberOfSharesOutstandingBasic=1078030000 [R2.htm:29]')]
    assert RA.apply_share_scale(full)[-1]['value'] == D(1078030000)
    split = _period('4000000000', '110') + [_r('shares_outstanding', 37400000)]   # 3x gap (a later split), not a scale
    assert RA.apply_share_scale(split)[-1]['value'] == D(37400000) and 'filer_scale_error' not in split[-1]['flags']
    noeps = [_r('net_income', '-2701000000'), _r('weighted_basic_shares', 1078030)]
    assert RA.apply_share_scale(noeps)[-1]['value'] == D(1078030)
    off = _period() + [_r('weighted_basic_shares', 900000)]   # x1000 is 16% off the implied count: no agreeing scale
    assert RA.apply_share_scale(off)[-1]['value'] == D(900000)
