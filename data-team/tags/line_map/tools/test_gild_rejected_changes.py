"""CERT-REGISTRY-rulings-2026-11-21 addendum 2, items 13-14: the two GILD changes the approver REJECTED stay reverted
in the resolver inputs and output (item 15: rejected changes are reverted before a re-cert token is written).
Run: python3 -m pytest data-team/tags/line_map/tools/test_gild_rejected_changes.py. Mutation: restore the text_disclosures
row's decision `mapped` (or the resolver row) and the first test fails."""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, '..', 'rules')
RES = os.path.join(HERE, '..', 'resolver', 'GILD.csv')


def _res(dp, pe):
    return [r for r in csv.DictReader(open(RES, newline='')) if r['data_point'] == dp and r['period_end'] == pe]


def test_item_13_gild_interest_income_fy2024_text_stated_value_is_not_served():
    td = [r for r in csv.DictReader(open(os.path.join(RULES, 'text_disclosures.csv'), newline=''))
          if r['ticker'] == 'GILD' and r['data_point'] == 'interest_income' and r['period_end'] == '2024-12-31']
    assert td and all(r['decision'] != 'mapped' for r in td) and 'item 13' in td[0]['why']
    # the rejected claim (text_disclosures, no proof row) is gone from the resolver output. A later full read that fills
    # EVERY year (GILD-2026-11-23.csv, ruling 13's own route) is a new change, served with flag filing_read.
    rows = _res('interest_income', '2024-12-31')
    assert len(rows) == 1
    assert not (rows[0]['decision'] == 'mapped' and 'filing_read' not in rows[0]['flags'].split(';'))


def test_item_14_gild_total_liabilities_fy2015_keeps_the_certified_derived_value():
    rows = _res('total_liabilities', '2015-12-31')
    assert len(rows) == 1 and rows[0]['decision'] == 'derived_not_printed'
    assert rows[0]['value'] == '32601000000' and rows[0]['accession'] == '0000882095-17-000006'
    assert 'structural_not_presented' not in rows[0]['flags']
