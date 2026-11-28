"""Resolver .94 rules (Stage 3 Resolve / M1). X137: working-capital change lines printed only combined are served with their
combined badge, and a pre-2026-11-22 'HIDE line_presented_combined' read no longer hides them. X139: weighted diluted shares
reported only by class leave out a class converting one-for-one into another (GOOG Class A diluted + Class C diluted). X140: the
latest print follows a single face line a later filing re-tagged under a filer extension (BAC FY2017 revenue, ORCL FY2017 pretax).
X139/X140 mutation-checked when added: with _diluted_class_total returning None, or line_renamed limited to capex again, they fail.
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


def test_x139_diluted_shares_by_class_leave_out_the_converting_class():
    # GOOG FY2019 (FY2021 10-K note, thousands): diluted A 346,342 (incl. Class B conversion) | B 46,527 | C 352,214;
    # basic A 299,402 | B 46,527 | C 346,667. Total diluted = A + C = 698,556 (ruling: Class A diluted + Class C diluted)
    W, B = 'WeightedAverageNumberOfDilutedSharesOutstanding', 'WeightedAverageNumberOfSharesOutstandingBasic'
    f = lambda t, v, m: f'{t}|4|{v}|ClassOfStock={m};'
    goog = '~'.join([f(B, 299402000, 'CommonClassA'), f(B, 46527000, 'CommonClassB'), f(B, 346667000, 'CapitalClassC'),
                     f(W, 346342000, 'CommonClassA'), f(W, 46527000, 'CommonClassB'), f(W, 352214000, 'CapitalClassC')])
    no_conv = '~'.join([f(B, 100, 'A'), f(B, 50, 'B'), f(W, 102, 'A'), f(W, 51, 'B')])   # no class holds another's conversion
    visa = '~'.join([f(B, 498000000, 'CommonClassA'), f(B, 245000000, 'CommonClassB'), f(B, 26000000, 'CommonClassC'),   # V FY2014: B and C
                     f(W, 631000000, 'CommonClassA'), f(W, 245000000, 'CommonClassB'), f(W, 26000000, 'CommonClassC')])  # convert at other ratios
    no_basic = '~'.join([f(W, 346342000, 'CommonClassA'), f(W, 46527000, 'CommonClassB'), f(W, 352214000, 'CapitalClassC')])
    row = lambda a: dict(accession=a, data_point='weighted_diluted_shares', status='not_presented', value=None, flags='roles;never_reported', why='', column='own')
    g, n, x, v = resolve_all.apply_weighted_class([row('G'), row('N'), row('X'), row('V')], {'G': goog, 'N': no_conv, 'X': no_basic, 'V': visa})
    assert g['status'] == 'component_sum' and g['value'] == D(698556000)
    assert 'CommonClassB' not in g['nodes'] and 'converted_class_excluded' in g['flags'] and 'never_reported' not in g['flags']
    assert n['status'] == 'not_presented' and 'reported_per_class' in n['flags']   # not additive, nothing proves a conversion: open
    assert x['status'] == 'not_presented'                                          # no basic counts to prove the conversion
    assert v['status'] == 'not_presented'                                          # V: A diluted 631 holds B and C as converted, not 1:1


def test_x140_latest_print_follows_a_single_face_line_retagged_by_a_later_filing():
    from test_pr4_lane_rules import _lp_face
    # BAC FY2017 revenue: own 'Revenues' 87,352; the FY2019 10-K prints the year under bac:RevenuesNetOfInterestExpense... 87,126
    mk = lambda pe, acc, nodes, v: dict(cik='70858', ticker='BAC', data_point='revenue', period_end=pe, accession=acc, status='mapped', value=v,
                                        tags='', nodes=nodes, column='own', flags='')
    rows = lambda: [mk('2017-12-31', 'B17', 'Revenues=87352 [R2.htm:25]', '87352'),
                    mk('2018-12-31', 'B18', 'Revenues=1 [R2.htm:25]', '1'),
                    mk('2019-12-31', 'B19', 'RevenuesNetOfInterestExpenseBeforeProvisionForLoanLoss=91244 [R2.htm:10]', '91244')]
    face = _lp_face('RevenuesNetOfInterestExpenseBeforeProvisionForLoanLoss')
    out = resolve_all.apply_latest_print(rows(), {'B19': 'RevenuesNetOfInterestExpenseBeforeProvisionForLoanLoss|4|87126|2017-12-31'}, face)[0]
    assert out['value'] == D(87126) and 'latest_print' in out['flags'] and out['accession'] == 'B19'
    # the own element still reported for the year in the later column: no re-tag (another line), the own figure stays
    both = 'RevenuesNetOfInterestExpenseBeforeProvisionForLoanLoss|4|87126|2017-12-31~Revenues|4|87352|2017-12-31'
    assert resolve_all.apply_latest_print(rows(), {'B19': both}, face)[0]['value'] == '87352'
    # outside 0.5-2x: another line's role, kept
    assert resolve_all.apply_latest_print(rows(), {'B19': 'RevenuesNetOfInterestExpenseBeforeProvisionForLoanLoss|4|300000|2017-12-31'}, face)[0]['value'] == '87352'
