"""Resolver .89 rules X119-X124. Run: python3 -m pytest data-team/tags/line_map/tools/test_r89_rules.py.
Each test fails with its rule removed (mutation-checked when added)."""
import csv, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filing_reads, resolve_all, resolve_is
from test_filing_reads import cells, read, row, _evidence


def test_fiscal_year_keys_to_the_company_fiscal_year_end_never_a_calendar_dec_31(tmp_path):
    # X119: MU fiscal 2023 = the year ended 2023-08-31; a stray calendar period (the served layer's 2023-12-31 open row) never splits the key
    res = [dict(period_end=pe) for pe in ('2022-08-31', '2023-08-31', '2023-12-31', '2024-08-31')]
    assert filing_reads.fiscal_periods(res, dict(fiscal_year='2023', rule_proposal='', quote='')) == ['2023-08-31']
    # a read that states its period end is keyed to it when the resolver has that period
    res2 = [dict(period_end=pe) for pe in ('2023-01-31', '2023-12-31')]
    assert filing_reads.fiscal_periods(res2, dict(fiscal_year='2023', rule_proposal='PERIOD KEY: write against period_end 2023-12-31', quote='')) == ['2023-12-31']
    rd = tmp_path / 'resolver'; rd.mkdir()
    with open(rd / 'MU.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cik', 'ticker', 'data_point', 'period_end']); w.writeheader()
        for pe in ('2022-08-31', '2023-08-31', '2023-12-31', '2024-08-31'): w.writerow(dict(cik='0000723125', ticker='MU', data_point='cf_ap_change', period_end=pe))
    p = tmp_path / 'MU-2026-11-22.csv'
    cols = ['ticker', 'data_point', 'fiscal_year', 'outcome', 'value', 'element', 'accession', 'r_page', 'quote', 'rule_proposal', 'confidence']
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        w.writerow(dict(ticker='MU', data_point='cf_ap_change', fiscal_year='2023', outcome='VALUE', value='-1302000000', element='x', accession='0000723125-25-000028',
                        r_page='R8.htm', quote='"Accounts payable and accrued expenses | 862 | 1,915 | (1,302)"', rule_proposal='badge=combined:Accounts payable and accrued expenses'))
    skips = tmp_path / 'skips.csv'; skips.write_text('ticker,data_point,fiscal_year,reason\n')
    kept, skipped = filing_reads.import_files(str(rd), [str(p)], str(skips))
    assert [k['period_end'] for k in kept] == ['2023-08-31'] and not skipped


def test_a_year_before_the_first_10k_takes_a_value_read_that_cites_a_real_filing(tmp_path):
    # X120: PLTR shares FY2018, printed in the first 10-K's equity statement (0001193125-21-060650 R6)
    p = cells(tmp_path, read(dp='shares_outstanding', pe='2018-12-31', fy='2018', value='549367691', acc='0001193125-21-060650'))
    r = filing_reads.apply([row(dp='shares_outstanding', pe='2018-12-31', accession='BEFORE:0001835632:2018-12-31', flags='before_first_10k')], p)[0]
    assert r['status'] == 'mapped' and r['value'] == D(549367691) and r['accession'] == '0001193125-21-060650' and r['column'] == 'comparative'
    assert 'text_stated' in r['flags'] and 'before_first_10k' not in r['flags']
    # a HIDE read leaves the before-first-10k row as it is
    p2 = cells(tmp_path, read(dp='shares_outstanding', pe='2018-12-31', fy='2018', outcome='HIDE', value='', hc='pre_filing', acc='0001193125-21-060650'))
    r2 = filing_reads.apply([row(dp='shares_outstanding', pe='2018-12-31', accession='BEFORE:0001835632:2018-12-31', flags='before_first_10k')], p2)[0]
    assert r2['status'] == 'not_presented' and r2['flags'] == 'before_first_10k'


def test_printed_unit_comes_from_the_quote_not_from_trailing_zeros(tmp_path):
    # X121: CB sbc FY2025, the equity statement prints '400' ($M): not a 10^8 rounding of the note's 399, the read replaces it
    assert filing_reads.printed_unit(D(400000000), 'APIC column, "Share-based compensation expense" rows 322 | 361 | 400 (2023 | 2024 | 2025, $M)') == D(10) ** 6
    assert filing_reads.printed_unit(D(800000000), 'share-based compensation of $0.8 billion') == D(10) ** 8
    assert filing_reads.printed_unit(D(400000000), 'no figure here') == D(10) ** 8
    p = cells(tmp_path, read(dp='sbc', pe='2025-12-31', fy='2025', value='400000000', acc='0000896159-26-000005', quote='rows 322 | 361 | 400 ($M)'))
    r = row(status='component_sum', value=D(399000000), dp='sbc', pe='2025-12-31', acc='0000896159-26-000005', nodes='A[AwardType=X]=91000000 [NOTE]; A[AwardType=Y]=308000000 [NOTE]')
    out = filing_reads.apply([r], p)[0]
    assert out['value'] == D(400000000) and 'text_stated' in out['flags']
    # the coarser print still never replaces the finer figure (ruling c: XOM 835M vs '0.8 billion')
    p2 = cells(tmp_path, read(dp='sbc', pe='2024-12-31', fy='2024', value='800000000', acc='0000034088-26-000045', quote='$0.8 billion'))
    r2 = row(status='mapped', value=D(835000000), dp='sbc', pe='2024-12-31', acc='0000034088-25-000010', nodes='ShareBasedCompensation=835000000 [R7.htm:5]')
    assert filing_reads.apply([r2], p2)[0]['value'] == D(835000000)


def test_sbc_without_a_cash_flow_add_back_is_the_equity_statement_line_one_source_per_row():
    # X122 (registry sbc fallback 2): the APIC column fact replaces a note award-type sum; a CF add-back row is never touched
    mf = {'A1': 'AdjustmentsToAdditionalPaidInCapitalSharebasedCompensationRequisiteServicePeriodRecognitionValue|4|400000000|EquityComponents=AdditionalPaidInCapital;',
          'A2': 'AdjustmentsToAdditionalPaidInCapitalSharebasedCompensationRequisiteServicePeriodRecognitionValue|4|50000000|EquityComponents=AdditionalPaidInCapital;'}
    award = dict(accession='A1', data_point='sbc', status='component_sum', value=D(399000000), flags='roles;award_type_member_sum', nodes='x', column='own')
    cf = dict(accession='A2', data_point='sbc', status='mapped', value=D(48000000), flags='roles', nodes='ShareBasedCompensation=48000000 [R7.htm:4]', column='own')
    out = resolve_all.apply_sbc_equity_statement([award, cf], mf)
    assert out[0]['status'] == 'mapped' and out[0]['value'] == D(400000000) and out[0]['flags'] == 'roles;sbc_equity_statement'
    assert out[0]['nodes'].endswith('[EquityComponents=AdditionalPaidInCapital]=400000000 [SE]') and resolve_all.NODE_GRAMMAR.match(out[0]['nodes'])
    assert out[1]['value'] == D(48000000) and out[1]['flags'] == 'roles'


def test_opex_badges_are_read_from_the_registry():
    # X124: resolve_all carries no copy of the fallback order; each opex derivation flags its registry step
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'pipeline', 'src'))
    from scrooner_pipeline.metrics import registry
    b = registry.load_data_points()[('operating_expenses', 'general')].badges
    assert (resolve_all.OPEX_BADGE_TC, resolve_all.OPEX_BADGE_SUM, resolve_all.OPEX_BADGE_GPOI) == (b[1], b[2], b[3])
    try:
        resolve_all.registry_badge('operating_expenses', 'no_such_formula')
        assert False
    except ValueError:
        pass
