"""Resolver .94 rule X137: working-capital change lines printed only combined are served with their combined badge, and a
pre-2026-11-22 'HIDE line_presented_combined' read no longer hides them.
Run: python3 -m pytest data-team/tags/line_map/tools/test_r94_rules.py. Mutation-checked when added (drop the
apply_combined_working_capital_change body or the 'combined:' reversal in filing_reads.apply and these fail)."""
import csv, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all
import filing_reads


def _r(dp, nodes, label, ticker='XOM'):
    return dict(ticker=ticker, cik='34088', accession='0000034088-18-000015', period_end='2015-12-31', data_point=dp, status='combined',
                tags='', value=None, r_page='', nodes=f"{nodes} | why: the line holding the role is wider than {dp}: its label '{label}' names other items",
                why='', source='roles', calc_check='', flags='cf_family;label_beyond;only_combined;only_combined_row', column='own')


def test_x137_working_capital_line_led_by_its_item_is_served_with_the_badge():
    xom = _r('cf_ap_change', 'IncreaseDecreaseInAccountsPayable=-7471000000.0000 [R7.htm:13]', 'Increase/(reduction) - Accounts and other payables')
    nee = _r('cf_ar_change', 'IncreaseDecreaseInAccountsReceivable=-90000000.0000 [R7.htm:21]', 'Customer and other receivables', 'NEE')
    mcd = _r('cf_inventory_change', 'IncreaseDecreaseInOtherOperatingCapitalNet=12.0000 [R6.htm:9]', 'Inventories, prepaid expenses and other current assets', 'MCD')
    mpc = _r('cf_ap_change', 'IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=-438000000.0000 [R8.htm:16]', 'Current liabilities and other current assets', 'MPC')
    gs = _r('cf_ar_change', 'IncreaseDecreaseInReceivables=5.0000 [R8.htm:12]', 'Receivables and payables (excluding loans receivable), net', 'GS')
    signed = _r('cf_ap_change', '-IncreaseDecreaseInAccountsPayable=5.0000 [R7.htm:13]', 'Accounts and other payables')
    two = _r('cf_ap_change', 'A=1.0000 [R7.htm:13]; B=2.0000 [R7.htm:14]', 'Accounts and other payables')
    out = resolve_all.apply_combined_working_capital_change([xom, nee, mcd, mpc, gs, signed, two])
    assert (out[0]['status'], out[0]['value']) == ('mapped', D(-7471000000))
    fl = out[0]['flags'].split(';')
    assert 'combined:Increase/(reduction) - Accounts and other payables' in fl and not {'only_combined', 'only_combined_row', 'label_beyond'} & set(fl)
    assert out[0]['nodes'] == 'IncreaseDecreaseInAccountsPayable=-7471000000 [R7.htm:13]'
    assert out[1]['status'] == 'mapped' and 'combined:Customer and other receivables' in out[1]['flags']
    assert out[2]['status'] == 'mapped' and 'combined:Inventories%2C prepaid expenses and other current assets' in out[2]['flags']
    assert [r['status'] for r in out[3:]] == ['combined'] * 4   # led by another item; both sides; a signed node; two lines


def test_x137_badges_fit_the_registry_combined_step():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'pipeline', 'src'))
    from scrooner_pipeline.metrics import registry
    out = resolve_all.apply_combined_working_capital_change(
        [_r('cf_ap_change', 'IncreaseDecreaseInAccountsPayable=915000000.0000 [R7.htm:13]', 'Increase/(reduction) - Accounts and other payables')])
    assert registry.badge_for('cf_ap_change', 'general', {'decision': out[0]['status'], 'flags': out[0]['flags'], 'nodes': out[0]['nodes']}) \
        == 'combined:Increase/(reduction) - Accounts and other payables'


def test_combined_hide_read_does_not_remove_a_cell_served_as_the_combined_line(tmp_path):
    # XOM-2026-11-21 read: 'HIDE line_presented_combined' on cf_ap_change FY2015; the resolver now serves the line with its badge
    p = tmp_path / 'cells.csv'
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=filing_reads.OUT_COLS); w.writeheader()
        w.writerow({c: '' for c in filing_reads.OUT_COLS} | dict(cik='0000034088', ticker='XOM', data_point='cf_ap_change', period_end='2015-12-31',
                   fiscal_year='2015', outcome='HIDE', accession='0000034088-18-000015', r_page='R7.htm', hide_class='line_presented_combined',
                   quote='HIDE line_presented_combined - the label names other payables', source_file='XOM-2026-11-21.csv'))
    served = resolve_all.apply_combined_working_capital_change(
        [_r('cf_ap_change', 'IncreaseDecreaseInAccountsPayable=-7471000000.0000 [R7.htm:13]', 'Increase/(reduction) - Accounts and other payables')])
    r = filing_reads.apply(served, str(p))[0]
    assert r['status'] == 'mapped' and r['value'] == D(-7471000000) and 'filing_read_hide_reversed' in r['flags']
    plain = dict(served[0], status='mapped', flags='cf_family')   # a printed line with no badge: the read's hide stands
    assert filing_reads.apply([plain], str(p))[0]['status'] == 'not_presented'
