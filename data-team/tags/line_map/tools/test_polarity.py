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


def test_latest_print_route_takes_the_concept_sign():
    # X115 (.88): DIS interest_expense FY2021 own note +1,546; the FY2023 10-K column stores InterestExpense -1,546 (and -1,600 here, a restated year)
    def rows(own):
        return [dict(cik='1', ticker='DIS', data_point='interest_expense', period_end=pe, accession=a, status='mapped', value=v, tags='InterestExpense',
                     nodes=f'InterestExpense={v} [NOTE]', column='own', flags='roles', why='w')
                for pe, a, v in (('2021-10-02', 'A21', own), ('2022-10-01', 'A22', '1'), ('2023-09-30', 'A23', '-1973000000'))]
    face = [dict(a='A23', lines='IS|3|14|InterestExpense|0|0|terseLabel|x|1')]
    r = RA.apply_latest_print(rows('1546000000'), {'A23': 'InterestExpense|4|-1546000000|2021-10-02'}, face)[0]
    assert r['value'] == '1546000000' and r['accession'] == 'A21'   # same figure once signed: the own print stays
    r = RA.apply_latest_print(rows('1546000000'), {'A23': 'InterestExpense|4|-1600000000|2021-10-02'}, face)[0]
    assert r['value'] == D(1600000000) and r['accession'] == 'A23' and 'polarity_flip' in r['flags'] and 'InterestExpense=-1600000000' in r['nodes']


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
