"""Filing reads (X109, Dhairya 2026-11-21 item 0): reviewed full-10-K reads become served claims with quote and locator.
Run: python3 -m pytest data-team/tags/line_map/tools/test_filing_reads.py. Mutation check: with filing_reads.apply
returning its rows untouched, every test but the import tests fails."""
import csv, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filing_reads

COLS = filing_reads.OUT_COLS


def cells(tmp_path, *rows):
    p = tmp_path / 'cells.csv'
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, '') for c in COLS})
    return str(p)


def read(dp='sga_expense', pe='2019-01-31', outcome='VALUE', value='424360000', acc='0001058057-21-000009', fy='2019', hc='', quote='R4 IS: "Selling, general and administrative | 467,240 | 464,580 | 424,360"'):
    return dict(cik='0001835632', ticker='MRVL', data_point=dp, period_end=pe, fiscal_year=fy, outcome=outcome, value=value,
                element='us-gaap:SellingAndMarketingExpense', accession=acc, r_page='R4.htm', hide_class=hc, quote=quote,
                rule_proposal='sga_tag_era', source_file='MRVL-2026-11-21.csv')


def row(status='not_presented', value=None, dp='sga_expense', pe='2019-01-31', acc='0001058057-19-000010', flags='roles', **kw):
    r = dict(ticker='MRVL', cik='1835632', accession=acc, period_end=pe, data_point=dp, status=status, tags='', value=value, r_page='',
             nodes='', why='', source='roles', calc_check='', flags=flags, column='own')
    r.update(kw); return r


def test_blank_cell_becomes_a_text_stated_claim_with_quote_locator_and_period(tmp_path):
    p = cells(tmp_path, read())
    r = filing_reads.apply([row()], p)[0]
    assert r['status'] == 'mapped' and r['value'] == D(424360000) and r['nodes'] == '' and r['tags'] == ''
    assert r['accession'] == '0001058057-21-000009' and r['column'] == 'comparative'   # the FY2021 10-K prints FY2019
    assert r['quote'].startswith('R4 IS') and 'R4.htm' in r['locator'] and r['quote_period'] == '2019-01-31'
    fl = r['flags'].split(';')
    assert 'filing_read' in fl and 'text_stated' in fl and 'replaces:not_presented' in fl and 'rounding_vintage' not in fl


def test_agreeing_xbrl_node_stays_and_is_marked_filing_read(tmp_path):
    p = cells(tmp_path, read(dp='total_debt', pe='2022-01-31', value='4547977000', acc='0001835632-22-000016'))
    r = row(status='component_sum', value=D(4547977000), dp='total_debt', pe='2022-01-31', acc='0001835632-22-000016', flags='total_debt',
            nodes='ShortTermBorrowings=63166000 [R3.htm:19]; LongTermDebtNoncurrent=4484811000 [R3.htm:21]')
    out = filing_reads.apply([r], p)[0]
    assert out['status'] == 'component_sum' and out['nodes'].startswith('ShortTermBorrowings') and out['value'] == D(4547977000)
    assert out['flags'] == 'total_debt;filing_read' and 'quote' not in out


def test_a_coarser_rounding_of_the_same_figure_never_replaces_the_finer_value(tmp_path):
    # ruling c (2026-11-21): XOM sbc FY2024 835M stays, not the later 0.8B print; MRVL total_debt FY2022 keeps 4,547,977k over 4,548.0M
    p = cells(tmp_path, read(pe='2021-01-31', fy='2021', value='467200000', acc='0001835632-23-000013'))
    r = row(status='mapped', value=D(467240000), pe='2021-01-31', acc='0001835632-22-000016', nodes='SellingAndMarketingExpense=467240000 [R5.htm:7]')
    out = filing_reads.apply([r], p)[0]
    assert out['value'] == D(467240000) and out['nodes'].startswith('Selling') and out['flags'] == 'roles;filing_read' and out['accession'] == '0001835632-22-000016'
    # a finer read over a coarser resolver value is a different value, not a rounding: the read wins
    p2 = cells(tmp_path, read(pe='2021-01-31', fy='2021', value='467240000', acc='0001835632-22-000016'))
    r2 = row(status='mapped', value=D(467200000), pe='2021-01-31', acc='0001835632-23-000013', nodes='SellingAndMarketingExpense=467200000 [R5.htm:7]')
    out2 = filing_reads.apply([r2], p2)[0]
    assert out2['value'] == D(467240000) and 'text_stated' in out2['flags']


def test_different_value_is_replaced_by_the_read_and_the_old_decision_is_recorded(tmp_path):
    # MRVL other income FY2018: resolver 22,194 (NonoperatingIncomeExpense + interest expense), the FY2020 10-K prints 'Other income, net | 4,813'
    p = cells(tmp_path, read(dp='other_income_expense_net', pe='2018-01-31', fy='2018', value='4813000', acc='0001058057-20-000014'))
    r = row(status='component_sum', value=D(22194000), dp='other_income_expense_net', pe='2018-01-31', acc='0001058057-18-000009', nodes='NonoperatingIncomeExpense=21509000 [R4.htm:11]; InterestExpense=685000 [NOTE]')
    out = filing_reads.apply([r], p)[0]
    assert out['value'] == D(4813000) and out['status'] == 'mapped' and out['nodes'] == '' and 'replaces:component_sum' in out['flags'] and 'component_sum=22194000' in out['why']


def test_hide_row_on_a_valued_cell_becomes_not_presented_with_class_and_quote(tmp_path):
    q = 'HIDE structural_not_presented: Deere prints "Other income" as a revenue line (ProductOrServiceAxis member); the IS has no non-operating section'
    p = cells(tmp_path, read(dp='other_income_expense_net', pe='2022-10-31', fy='2022', outcome='HIDE', value='', hc='structural_not_presented', acc='0001558370-22-018703', quote=q))
    r = row(status='mapped', value=D(1295000000), dp='other_income_expense_net', pe='2022-10-31', acc='0001558370-22-018703', flags='roles;presented_within_expenses', nodes='Revenues[ProductOrServiceAxis=OtherIncomeMember]=1295000000 [R3.htm:9]')
    out = filing_reads.apply([r], p)[0]
    assert out['status'] == 'not_presented' and out['value'] is None and out['nodes'] == ''
    assert out['flags'] == 'filing_read_hide;structural_not_presented' and out['quote'] == q and 'R4.htm' in out['locator']
    # a cell already blank keeps its decision and flags, gaining the class and the quote
    r2 = row(status='not_presented', dp='other_income_expense_net', pe='2022-10-31', acc='0001558370-22-018703', flags='roles;absent_in_own_filing')
    out2 = filing_reads.apply([r2], p)[0]
    assert out2['status'] == 'not_presented' and out2['flags'] == 'roles;absent_in_own_filing;filing_read_hide;structural_not_presented' and out2['quote'] == q


def test_rows_of_other_periods_cells_and_before_rows_are_untouched(tmp_path):
    p = cells(tmp_path, read())
    others = [row(pe='2020-01-31'), row(dp='revenue'), row(accession='BEFORE:0001058057-19-000010'), row(column='fill')]
    out = filing_reads.apply(others, p)
    assert all(o['status'] == 'not_presented' and 'filing_read' not in o['flags'] for o in out)


def _evidence(tmp_path, rows):
    p = tmp_path / 'MRVL-2026-11-21.csv'
    cols = ['ticker', 'data_point', 'fiscal_year', 'outcome', 'value', 'element', 'accession', 'r_page', 'quote', 'rule_proposal', 'confidence']
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, '') for c in cols})
    return str(p)


def test_import_keys_fiscal_years_to_resolver_periods_skips_rule_rows_and_listed_conflicts(tmp_path):
    rd = tmp_path / 'resolver'; rd.mkdir()
    with open(rd / 'MRVL.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end']); w.writeheader()
        for pe in ('2019-01-31', '2021-01-31'): w.writerow(dict(cik='0001835632', ticker='MRVL', data_point='sga_expense', period_end=pe))
    skips = tmp_path / 'skips.csv'
    skips.write_text('ticker,data_point,fiscal_year,reason\nMRVL,sga_expense,2021,conflicts with ruling X\n')
    base = dict(ticker='MRVL', data_point='sga_expense', element='us-gaap:SellingAndMarketingExpense', r_page='R4.htm', confidence='high')
    ev = _evidence(tmp_path, [dict(base, fiscal_year='2019', outcome='VALUE', value='424360000', accession='0001058057-21-000009', quote='R4 IS: "Selling | 424,360"'),
                              dict(base, fiscal_year='2021', outcome='VALUE', value='467200000', accession='0001835632-23-000013', quote='R5 IS'),
                              dict(base, fiscal_year='2019', outcome='RULE', quote='stays open'),
                              dict(base, fiscal_year='2018', outcome='VALUE', value='1', accession='0001058057-20-000014', quote='no period in the resolver'),
                              dict(base, fiscal_year='2019', outcome='HIDE', quote='HIDE line_presented_combined - the band is one line'),
                              dict(base, fiscal_year='2019', outcome='HIDE', quote='no class here')])
    kept, skipped = filing_reads.import_files(str(rd), [ev], str(skips))
    assert [(k['fiscal_year'], k['outcome'], k['period_end'], k['hide_class']) for k in kept] == [('2019', 'VALUE', '2019-01-31', ''), ('2019', 'HIDE', '2019-01-31', 'line_presented_combined')]
    reasons = [s['reason'] for s in skipped]
    assert len(skipped) == 4 and reasons[0] == 'conflicts with ruling X' and reasons[1].startswith('RULE row') and 'no single resolver period' in reasons[2] and 'without a hide class' in reasons[3]
    assert kept[0]['cik'] == '0001835632' and kept[0]['source_file'] == 'MRVL-2026-11-21.csv'


def test_committed_cells_file_is_consistent_with_its_skips_and_the_resolver_periods():
    here = os.path.dirname(os.path.abspath(__file__))
    cells_ = list(csv.DictReader(open(filing_reads.CELLS)))
    assert cells_ and all(r['period_end'] and r['accession'] and r['quote'] for r in cells_)
    assert all(r['hide_class'] for r in cells_ if r['outcome'] == 'HIDE') and all(r['value'] for r in cells_ if r['outcome'] == 'VALUE')
    skips = {(s['ticker'], s['data_point'], fy) for s in csv.DictReader(open(filing_reads.SKIPS)) for fy in s['fiscal_year'].split(';')}
    assert not [r for r in cells_ if (r['ticker'], r['data_point'], r['fiscal_year']) in skips], 'a skipped row is in the cells file'
    assert all(r['outcome'] in ('VALUE', 'HIDE') for r in cells_)


def test_import_accepts_the_only_after_tax_disclosed_class(tmp_path):
    """Ruling 2026-11-21 (Dhairya): sbc disclosed only after tax is never served as sbc; the read lands as a hide of
    class only_after_tax_disclosed (VZ FY2017-25, GE FY2015-17). Mutation: drop the class from HIDE_RE and this fails."""
    rd = tmp_path / 'resolver'; rd.mkdir()
    with open(rd / 'VZ.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end']); w.writeheader()
        w.writerow(dict(cik='0000732712', ticker='VZ', data_point='sbc', period_end='2019-12-31'))
    skips = tmp_path / 'skips.csv'; skips.write_text('ticker,data_point,fiscal_year,reason\n')
    ev = _evidence(tmp_path, [dict(ticker='VZ', data_point='sbc', fiscal_year='2019', outcome='HIDE', element='', accession='0000732712-22-000008',
                                   r_page='R97.htm', quote='HIDE only_after_tax_disclosed - RSU and PSU expense stated after tax only', confidence='high')])
    kept, skipped = filing_reads.import_files(str(rd), [ev], str(skips))
    assert not skipped and [k['hide_class'] for k in kept] == ['only_after_tax_disclosed']
