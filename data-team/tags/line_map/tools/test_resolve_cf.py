"""Tests for resolve_cf.py. Run: python3 -m pytest data-team/tags/line_map/tools/test_resolve_cf.py (or python3 this file)."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_cf import resolve_cf

def filing(rows, calc=''):
    # row: (tag, value, negating, custom, label); all on report 8, numbered in order
    lines = '~'.join(f"CF|8|{i + 1}|{t}|{int(c)}|{int(n)}||{lb}|{'' if v is None else v}" for i, (t, v, n, c, lb) in enumerate(rows))
    return dict(cik='1', a='0000000001-25-000001', p='2024-12-31', fd='2025-02-01', lines=lines, calc=calc)

OP = ('NetCashProvidedByUsedInOperatingActivities', 100, False, False, 'Net cash from operating activities')
INV = ('NetCashProvidedByUsedInInvestingActivities', -50, False, False, 'Net cash used in investing activities')
FIN = ('NetCashProvidedByUsedInFinancingActivities', -20, False, False, 'Net cash used in financing activities')

def test_sign_is_the_raw_fact_not_the_printed_sign():
    # printed in parentheses (negating) and stored positive: the stored value stays positive; an AR increase is stored positive
    f = filing([('IncreaseDecreaseInAccountsReceivable', 7, True, False, 'Accounts receivable'), OP,
                ('PaymentsToAcquirePropertyPlantAndEquipment', 30, True, False, 'Capital expenditures'), INV, FIN])
    r = resolve_cf(f, {})
    assert r['cf_ar_change']['value'] == D(7) and r['capex']['value'] == D(30)

def test_aggregate_on_face_detail_in_note():
    # VLO / KO / CVX shape: the face prints only the net working-capital change; the receivable detail is an undimensioned note fact
    f = filing([('IncreaseDecreaseInOperatingCapital', 9, True, False, 'Changes in working capital'), OP, INV, FIN])
    r = resolve_cf(f, {('IncreaseDecreaseInAccountsReceivable', 4): D(-3)})
    assert r['cf_ar_change']['status'] == 'mapped' and r['cf_ar_change']['value'] == D(-3) and 'NOTE' in r['cf_ar_change']['nodes']
    assert r['cf_inventory_change']['status'] == 'not_presented'

def test_combined_payable_is_a_reason():
    f = filing([('IncreaseDecreaseInAccountsPayableAndAccruedLiabilities', 5, False, False, 'Accounts payable and accrued liabilities'), OP, INV, FIN])
    assert resolve_cf(f, {})['cf_ap_change']['status'] == 'combined'

def test_capex_sums_the_investing_section_and_ignores_vie_extension_and_other_sections():
    f = filing([('DepreciationDepletionAndAmortization', 1, False, False, 'D&A'), ('PaymentsToAcquirePropertyPlantAndEquipment', 30, True, False, 'Capital expenditures'), OP,
                ('PaymentsForCapitalImprovements', 5, True, False, 'Deferred turnaround costs'),
                ('xx_VieCapex', 2, True, True, 'Capital expenditures of certain variable interest entities'),
                ('PaymentsToAcquireOilAndGasPropertyAndEquipment', 9, True, False, 'Acquisition of undivided interest'), INV,
                ('PaymentsToAcquirePropertyPlantAndEquipment', 99, True, False, 'Capital expenditures financing-like'), FIN])
    r = resolve_cf(f, {})['capex']
    # the first PP&E line sits above the OPERATING total (operating section), the last above FINANCING: neither counts
    assert r['value'] == D(5) and r['tags'] == 'PaymentsForCapitalImprovements'

def test_buyback_excludes_excise_tax_and_dividend_excludes_nci():
    f = filing([OP, INV, ('PaymentsForRepurchaseOfCommonStock', 40, True, False, 'Purchases of common stock'),
                ('PaymentsForRepurchaseOfCommonStockExciseTax', 1, True, False, 'Excise tax'),
                ('PaymentsOfDividendsCommonStock', 12, True, False, 'Common stock dividends'),
                ('PaymentsOfDividendsMinorityInterest', 3, True, False, 'Distributions to noncontrolling interests'), FIN])
    r = resolve_cf(f, {})
    assert r['share_buybacks']['value'] == D(40) and r['dividends_paid']['value'] == D(12)

def test_note_common_dividend_beats_custom_face_line():
    f = filing([OP, INV, ('xx_Distributions', 20, True, True, 'Cash distributions to stockholders'), FIN])
    r = resolve_cf(f, {('PaymentsOfDividendsCommonStock', 4): D(18)})
    assert r['dividends_paid']['value'] == D(18)



def _with_is(rows, is_rows):
    f = filing(rows)
    f['lines'] += '~' + '~'.join(f"IS|2|{i + 1}|{t}|0|0||{lb}|{v}" for i, (t, v, lb) in enumerate(is_rows))
    return f


def test_generic_dividend_line_holding_preferred_is_combined():
    # BAC: one financing line 'Cash dividends paid' (PaymentsOfOrdinaryDividends) while the IS reports preferred dividends
    pref = [('PreferredStockDividendsIncomeStatementImpact', 1421, 'Preferred stock dividends')]
    rows = [OP, INV, ('PaymentsOfOrdinaryDividends', 7727, True, False, 'Cash dividends paid'), FIN]
    r = resolve_cf(_with_is(rows, pref), {})
    assert r['dividends_paid']['status'] == 'combined' and r['dividends_paid']['value'] is None
    # the same line without preferred dividends in the filing is the common line
    assert resolve_cf(filing(rows), {})['dividends_paid']['status'] == 'mapped'
    # a label naming common stays mapped; a label naming only preferred means no common dividend line (TMUS)
    rc = [OP, INV, ('PaymentsOfDividends', 500, True, False, 'Dividends paid on common stock'), FIN]
    assert resolve_cf(_with_is(rc, pref), {})['dividends_paid']['status'] == 'mapped'
    rp = [OP, INV, ('PaymentsOfDividends', 95, True, False, 'Dividends on preferred stock'), FIN]
    assert resolve_cf(_with_is(rp, pref), {})['dividends_paid']['status'] == 'not_presented'


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
