"""Tests for resolve_all.apply_amort_finer_print (rule X116, resolver .88, ruling 15 'finer figure wins'). Run: python3 -m pytest this file.
Mutation check: with apply_amort_finer_print returning its rows untouched, the first test fails."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA


def _own(pe, acc, v, flags='roles;note_only', nodes=None):
    return dict(cik='310158', ticker='MRK', data_point='amortization_of_intangibles', period_end=pe, accession=acc, status='mapped', value=D(v),
                tags='', nodes=nodes or f'AmortizationOfIntangibleAssets={v} [NOTE]', column='own', flags=flags, why='')


def _later(pe, acc, v):
    return _own(pe, acc, v, 'roles;face;amort_by_note_equality', f'AdjustmentForAmortization={v} [R8.htm:4]')


def test_rounded_note_yields_to_the_later_cf_face_line_the_later_filing_proves():
    # MRK FY2018: own note 'AmortizationOfIntangibleAssets' 2.9B; the FY2020 10-K CF prints 'Amortization' 3,103 for 2018
    rows = [_own('2018-12-31', 'A18', 2900000000), _own('2019-12-31', 'A19', 2000000000), _later('2020-12-31', 'A20', 1899000000)]
    comp = {'A20': 'AdjustmentForAmortization|4|3103000000|2018-12-31~AdjustmentForAmortization|4|1695000000|2019-12-31'}
    r18, r19, r20 = RA.apply_amort_finer_print(rows, comp)
    assert r18['value'] == D(3103000000) and r18['accession'] == 'A20' and r18['column'] == 'comparative'
    assert r18['nodes'] == 'AdjustmentForAmortization=3103000000 [R8.htm:4@A20]' and 'finer_print' in r18['flags']
    assert r19['value'] == D(1695000000)   # FY+1 when FY+2 is absent
    assert r20['value'] == D(1899000000)


def test_precise_notes_unproved_later_lines_and_far_figures_stay():
    comp = {'A20': 'AdjustmentForAmortization|4|3103000000|2018-12-31'}
    rows = [_own('2018-12-31', 'A18', 2913000000), _later('2020-12-31', 'A20', 1899000000)]   # a precise note figure: nothing finer
    assert RA.apply_amort_finer_print(rows, comp)[0]['value'] == D(2913000000)
    rows = [_own('2018-12-31', 'A18', 2900000000), _own('2020-12-31', 'A20', 1899000000, 'roles;face', 'AdjustmentForAmortization=1899000000 [R8.htm:4]')]
    assert RA.apply_amort_finer_print(rows, comp)[0]['value'] == D(2900000000)   # the later line is not proven intangible amortization
    rows = [_own('2018-12-31', 'A18', 2000000000), _later('2020-12-31', 'A20', 1899000000)]   # 3,103 is over 20% off 2.0B: another line
    assert RA.apply_amort_finer_print(rows, comp)[0]['value'] == D(2000000000)
