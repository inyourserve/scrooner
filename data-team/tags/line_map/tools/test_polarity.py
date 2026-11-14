"""Tests for the one-sign-per-concept rule (resolve_all.apply_polarity, rules/polarity.csv). Run: python3 this file."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA


def row(dp, v, status='mapped'):
    return dict(data_point=dp, status=status, value=None if v is None else D(v), flags='roles', why='w')


def test_expense_on_a_reversed_element_is_normalised_and_recorded():
    r = RA.apply_polarity([row('interest_expense', -1973)])[0]   # DIS FY2023 InterestExpense filed negative
    assert r['value'] == D(1973) and 'polarity_flip' in r['flags'] and 'polarity' in r['why']


def test_signed_concepts_and_component_sums_keep_their_sign():
    rs = RA.apply_polarity([row('income_tax_expense', -5), row('cf_ar_change', -7), row('operating_expenses', -337, 'component_sum'), row('interest_expense', 9)])
    assert [r['value'] for r in rs] == [D(-5), D(-7), D(-337), D(9)] and not any('polarity_flip' in r['flags'] for r in rs)


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
