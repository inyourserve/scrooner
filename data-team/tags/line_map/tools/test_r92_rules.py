"""Resolver .92 rule X133 (cf_ap_change combined line served with a badge). X130's .92 label-first form is in test_r91_rules.py.
Run: python3 -m pytest data-team/tags/line_map/tools/test_r92_rules.py. Mutation-checked when added."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all


def _r(nodes, why, status='combined', flags='cf_family;only_combined;only_combined_years'):
    return dict(ticker='MU', cik='723125', accession='0000723125-22-000038', period_end='2022-08-31', data_point='cf_ap_change',
                status=status, tags='', value=None, r_page='', nodes=nodes, why=why, source='roles', calc_check='', flags=flags, column='own')


def test_x133_combined_ap_change_line_is_served_with_its_badge():
    # MU FY2022: the CF prints only 'Accounts payable and accrued expenses' (IncreaseDecreaseInAccountsPayableAndAccruedLiabilities)
    mu = _r('IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=744000000.0000 [R8.htm:11]',
            "CF face prints only the combined line IncreaseDecreaseInAccountsPayableAndAccruedLiabilities 'Accounts payable and accrued expenses'"
            " | reported only combined: IncreaseDecreaseInAccountsPayableAndAccruedLiabilities")
    wide = _r('IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=5.0000 [R8.htm:11]',
              "CF face prints only the combined line X 'Current liabilities and other current assets'")
    neg = _r('-IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=5.0000 [R8.htm:11]', "combined line X 'Accounts payable and accrued expenses'")
    out = resolve_all.apply_combined_ap_change([mu, wide, neg])
    assert (out[0]['status'], out[0]['value']) == ('mapped', D(744000000))
    flags = out[0]['flags'].split(';')
    assert 'combined:Accounts payable and accrued expenses' in flags and 'only_combined' not in flags and 'only_combined_years' not in flags
    assert out[0]['nodes'] == 'IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=744000000 [R8.htm:11]'
    assert out[1]['status'] == 'combined' and out[2]['status'] == 'combined'   # not a payables-first label; a signed node


def test_x133_badge_keeps_the_full_printed_label_jnj_fy2015():
    """JNJ FY2015 (verifier 2026-11-22): the badge read 'combined:(Decrease)/Increase in accounts payable and accrued liabilit'
    because the standard extract cut every presentation label at 60 characters (left(plabel, 60)). The extract now keeps the
    whole label, and X133 carries it unchanged into the badge. Mutation: restore the cap in any extract SQL and this fails."""
    full = '(Decrease)/Increase in accounts payable and accrued liabilities'
    jnj = _r('IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=-3000000.0000 [R8.htm:15]',
             f"CF face prints only the combined line IncreaseDecreaseInAccountsPayableAndAccruedLiabilities '{full}'")
    assert 'combined:' + full in resolve_all.apply_combined_ap_change([jnj])[0]['flags'].split(';')
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ('extract.sql', 'extract_bs.sql', 'resolve_cf_extract.sql'):
        sql = open(os.path.join(here, name)).read()
        assert 'left(coalesce(l.plabel' not in sql, name
        assert "coalesce(l.plabel,'')" in sql, name
