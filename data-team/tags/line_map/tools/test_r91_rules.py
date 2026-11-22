"""Resolver .91 rules X130 (pattern P07) and X132 (pattern P01). Run: python3 -m pytest data-team/tags/line_map/tools/test_r91_rules.py.
Each test fails with its rule removed (mutation-checked when added)."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all


def _r(dp, status, nodes='', why='', value=None, pe='2020-01-31', acc='0000104169-20-000011', flags='roles', column='own', **kw):
    return dict(ticker='WMT', cik='104169', accession=acc, period_end=pe, data_point=dp, status=status, tags='', value=value, r_page='',
                nodes=nodes, why=why, source='roles', calc_check='', flags=flags, column=column, **kw)


def _filing(acc, label):
    return dict(a=acc, lines=f'IS|2|6|CostOfRevenue|0|0|terseLabel|Cost of sales|394605000000.0000~'
                             f'IS|2|7|SellingGeneralAndAdministrativeExpense|0|0|terseLabel|{label}|108791000000.0000')


def test_x130_one_printed_line_serves_one_data_point():
    # WMT FY2020: the only operating line is 'Operating, selling, general and administrative expenses' (R2.htm:7), served as both
    # sga_expense and operating_expenses. sga keeps it (badge combined:<label>); opex is included_in:sga_expense.
    node = 'SellingGeneralAndAdministrativeExpense=108791000000.0000 [R2.htm:7]'
    rows = [_r('operating_expenses', 'mapped', node + ' | why: IS line 7: the expense node between Revenues and OI', value=D(108791000000), flags='core'),
            _r('sga_expense', 'mapped', node + ' | why: IS face SellingGeneralAndAdministrativeExpense', value=D(108791000000)),
            # COST shape, latest-print column: a pure SG&A label adds no badge
            _r('operating_expenses', 'mapped', 'SellingGeneralAndAdministrativeExpense=19779000000.0000 [R3.htm:11@0000909832-22-000021]',
               value=D(19779000000), pe='2022-08-31', acc='0000909832-22-000021', column='comparative', flags='core'),
            _r('sga_expense', 'mapped', 'SellingGeneralAndAdministrativeExpense=19779000000.0000 [R3.htm:11@0000909832-22-000021]',
               value=D(19779000000), pe='2022-08-31', acc='0000909832-22-000021', column='comparative'),
            # a total that is a sum of several lines keeps its value (a total and its part may share a line)
            _r('operating_expenses', 'component_sum', 'SellingGeneralAndAdministrativeExpense=10899000000.0000 [R4.htm:7]; PreOpeningCosts=63000000.0000 [R4.htm:8]',
               value=D(10962000000), pe='2014-08-31', acc='0000909832-14-000021'),
            _r('sga_expense', 'mapped', 'SellingGeneralAndAdministrativeExpense=10899000000.0000 [R4.htm:7]', value=D(10899000000), pe='2014-08-31',
               acc='0000909832-14-000021')]
    files = [_filing('0000104169-20-000011', 'Operating, selling, general and administrative expenses'),
             dict(a='0000909832-22-000021', lines='IS|3|11|SellingGeneralAndAdministrativeExpense|0|0|terseLabel|Selling, general and administrative|19779000000.0000')]
    out = resolve_all.apply_one_line_one_data_point(rows, files)
    # .92: WMT's label names operating expenses first -> opex keeps the line (badge combined:<label>), sga is included_in:opex
    assert (out[0]['status'], out[0]['value']) == ('mapped', D(108791000000))
    assert 'combined:Operating%2C selling%2C general and administrative expenses' in out[0]['flags'].split(';')
    assert (out[1]['status'], out[1]['value']) == ('combined', None) and 'included_in:operating_expenses' in out[1]['flags'].split(';')
    assert {'only_combined', 'only_combined_years'} <= set(out[1]['flags'].split(';'))   # sga has a valued year (2014 row)
    assert 'reported only combined: SellingGeneralAndAdministrativeExpense included_in:operating_expenses' in out[1]['why']
    # a pure SG&A label (COST) -> sga keeps it, opex included_in:sga_expense, no badge
    assert out[2]['status'] == 'combined' and 'included_in:sga_expense' in out[2]['flags'].split(';')
    assert 'only_combined' in out[2]['flags'].split(';') and not any(f.startswith('combined:') for f in out[3]['flags'].split(';'))
    assert (out[4]['status'], out[4]['value']) == ('component_sum', D(10962000000))


def test_x132_a_reads_multi_year_row_serves_every_year_it_prints():
    # MU FY2023 read from the FY2025 10-K: 'Accounts payable and accrued expenses | 862 | 1,915 | (1,302)' under (2025 | 2024 | 2023),
    # served -1,302M with badge combined:...; FY2024 (combined, no read) takes 1,915M and FY2025 862M. A served year is never replaced,
    # a year a read decided (filing_read_hide) is never filled, and a row that does not hold the read's own value adds nothing.
    q = ('FY2025 10-K (latest print of FY2023) CF (2025 | 2024 | 2023): "Accounts payable and accrued expenses | 862 | 1,915 | (1,302)". '
         'No MU 10-K prints a separate accounts-payable change line.')
    read = _r('cf_ap_change', 'mapped', value=D(-1302000000), pe='2023-08-31', acc='0000723125-25-000028', column='comparative',
              flags='cf_family;filing_read;text_stated;replaces:combined;combined:Accounts payable and accrued expenses', quote=q, locator='R8.htm', quote_period='2023-08-31')
    y24 = _r('cf_ap_change', 'combined', 'IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=1915000000 [R8.htm:20]', value=D(1915000000),
             pe='2024-08-31', acc='0000723125-24-000027', flags='cf_family;only_combined')
    y25 = _r('cf_ap_change', 'mapped', 'IncreaseDecreaseInAccountsPayable=862000000 [R8.htm:20]', value=D(862000000), pe='2025-08-29', acc='0000723125-25-000028')
    gild = _r('interest_income', 'mapped', value=D(281000000), pe='2024-12-31', acc='0000882095-25-000010', column='comparative',
              flags='roles;filing_read;text_stated', quote='R79 ($ in millions, Dec. 31, 2025 | 2024 | 2023): "Interest income | (349) | (281) | (376)"', locator='R79', quote_period='2024-12-31')
    g23 = _r('interest_income', 'not_presented', pe='2023-12-31', acc='0000882095-24-000005')
    g25 = _r('interest_income', 'not_presented', pe='2025-12-31', acc='0000882095-26-000003', flags='roles;filing_read_hide;structural_not_presented')
    other = _r('interest_income', 'mapped', value=D(5), pe='2016-12-31', acc='0000882095-17-000005', flags='roles;filing_read;text_stated',
               quote='($ in millions, 2016 | 2015): "Interest income | 7 | 9"', locator='x', quote_period='2016-12-31')
    o15 = _r('interest_income', 'not_presented', pe='2015-12-31', acc='0000882095-16-000005')
    for x in (gild, g23, g25, other, o15): x['ticker'] = 'GILD'
    out = resolve_all.apply_read_stated_years([read, y24, y25, gild, g23, g25, other, o15])
    assert (out[1]['status'], out[1]['value'], out[1]['column'], out[1]['accession']) == ('mapped', D(1915000000), 'comparative', '0000723125-25-000028')
    assert out[1]['quote_period'] == '2024-08-31' and 'combined:Accounts payable and accrued expenses' in out[1]['flags'].split(';')
    assert out[2]['value'] == D(862000000) and out[2]['nodes'].startswith('IncreaseDecreaseInAccountsPayable=')   # served: untouched
    assert (out[4]['status'], out[4]['value']) == ('mapped', D(376000000))   # the note prints income negative: the read's sign holds
    assert out[5]['status'] == 'not_presented'   # a read's hide is a decision
    assert out[7]['status'] == 'not_presented'   # the row does not hold the read's own value (5): nothing is added
