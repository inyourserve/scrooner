"""Tests for resolve_all.apply_rounded_share_count (rule X111, Dhairya 2026-11-22). Run: python3 -m pytest this file."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA


def _row(acc, v):
    return dict(ticker='X', accession=acc, period_end='2023-09-30', data_point='shares_outstanding', status='mapped', value=D(v),
                nodes=f'CommonStockSharesOutstanding={v}.0000 [BSP]', why='', flags='bs_family;note')


MF = {'DIS23': 'CommonStockSharesOutstanding|0|1830000000.0000|EquityComponents=CommonStock;~WeightedAverageNumberOfSharesOutstandingBasic|4|1828000000.0000|X=Y;',
      'NEM20': 'CommonStockSharesOutstanding|0|-4000000.0000|EquityComponents=TreasuryStockCommon;~CommonStockSharesOutstanding|0|804000000.0000|EquityComponents=CommonStock;',
      'DIS25': 'CommonStockSharesOutstanding|0|1791000000.0000|EquityComponents=CommonStock;',
      'FAR': 'CommonStockSharesOutstanding|0|1700000000.0000|EquityComponents=CommonStock;'}


def test_rounded_undimensioned_count_loses_to_the_equity_statement_count():
    r, = RA.apply_rounded_share_count([_row('DIS23', 1800000000)], MF)
    assert r['value'] == D(1830000000) and 'rounded_count_replaced' in r['flags'] and '[EquityComponents=CommonStock]=1830000000' in r['nodes']
    r, = RA.apply_rounded_share_count([_row('DIS25', 1900000000)], MF)   # tagged 1.9B, the statement counts 1,791M
    assert r['value'] == D(1791000000)


def test_count_the_members_tie_to_stays():
    r, = RA.apply_rounded_share_count([_row('NEM20', 800000000)], MF)   # 804 - 4 = 800
    assert r['value'] == D(800000000) and 'rounded_count_replaced' not in r['flags']


def test_no_member_count_a_non_round_value_or_a_far_count_stays():
    rows = [_row('CVS22', 1300000000), _row('DIS23', 1830000000), _row('FAR', 1900000000)]
    out = RA.apply_rounded_share_count([dict(x) for x in rows], MF)
    assert [o['value'] for o in out] == [D(1300000000), D(1830000000), D(1900000000)]
    assert not any('rounded_count_replaced' in o['flags'] for o in out)
