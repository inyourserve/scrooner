"""Tests for resolve_all.fill_printed_zero_and_comparative (rulings 2026-11-14). Run: python3 this file."""
import os, sys, csv, tempfile
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA


def _csv(rows):
    f = tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, newline='')
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows); f.close()
    return f.name


def _row(acc, dp, ticker='IBM', pe='2020-12-31'):
    return dict(ticker=ticker, accession=acc, period_end=pe, data_point=dp, status='not_presented', value=None, tags='', nodes='', why='', flags='roles')


def test_printed_dash_is_zero_and_comparative_fills_with_the_next_filing():
    # inputs from the standard extract (standard_inputs.printed_zero / comparative_fill); no side files
    RA.EXT['pz'] = {('A1', 'share_buybacks'): dict(tag='PaymentsForRepurchaseOfCommonStock', stmt='CF', r_line='R6:30', label='Common stock repurchases')}
    RA.EXT['cf'] = {('A2', 'dividends_per_share'): dict(accession='N2', tag='CommonStockDividendsPerShareDeclared', value='3.36', window='FY-1')}
    nxt = dict(ticker='CAT', accession='N2', period_end='2019-12-31', data_point='dividends_per_share', status='mapped', value=D('3.48'), nodes='CommonStockDividendsPerShareDeclared=3.48 [R5.htm:9]', flags='')
    rows = RA.fill_printed_zero_and_comparative([_row('A1', 'share_buybacks'), _row('A2', 'dividends_per_share', 'CAT', '2018-12-31'), _row('A3', 'capex'), nxt], {})[:3]
    z, c, n = rows
    assert z['status'] == 'mapped' and z['value'] == D(0) and 'printed_zero' in z['flags'] and 'R6:30' in z['nodes']
    assert c['value'] == D('3.36') and c['accession'] == 'N2' and c['column'] == 'comparative' and 'comparative_fill' in c['flags'] and '[R5.htm:9 of N2' in c['nodes']
    assert n['status'] == 'not_presented'   # a line absent from the face stays not_presented


def test_receivables_and_payables_include_the_related_party_face_line():
    # COP FY2016: 'Accounts and notes receivable-related parties' (DueFromRelatedPartiesCurrent 165) beside the trade line;
    # AMD FY2018 'Prepayment and receivables - related parties' is a mixed line and is not added
    lines = '~'.join(['BS|5|4|AccountsAndNotesReceivableNet|0|0||Accounts and notes receivable|3249', 'BS|5|5|DueFromRelatedPartiesCurrent|0|0||Accounts and notes receivable-related parties|165',
                      'BS|5|6|RelatedPartyTransactionPrepaidExpenseCurrent|0|0||Prepayment and receivables - related parties|52',
                      'BS|5|15|AccountsPayableCurrent|0|0||Accounts payable|3631', 'BS|5|16|DueToRelatedPartiesCurrent|0|0||Accounts payable-related parties|22'])
    f = dict(cik='1', a='A9', p='2016-12-31', fd='2017-02-01', lines=lines, calc='')
    rows = [dict(ticker='COP', accession='A9', period_end='2016-12-31', data_point=dp, status='mapped', value=D(v), tags=t, nodes=f'{t}={v} [R5.htm:4]', why='', flags='roles')
            for dp, t, v in (('accounts_receivable', 'AccountsAndNotesReceivableNet', 3249), ('accounts_payable', 'AccountsPayableCurrent', 3631))]
    rows = RA.apply_ar_related(RA.apply_ap_related(rows, [f]), [f])
    ar, ap = rows
    assert ar['value'] == D(3414) and 'ar_related_sum' in ar['flags'] and ar['status'] == 'component_sum'
    assert ap['value'] == D(3653) and 'ap_related_sum' in ap['flags']


def test_opex_from_printed_totals_when_the_tree_has_no_node():
    # PEP FY2019: OI's calc children are Revenues, COGS and SG&A (no GP node); opex = GP - OI = 26,738
    # QCOM FY2022: 'Other' is filed +1,059 but the printed total ties at -1,059; opex = total costs - cost of revenue = 9,705
    pep = dict(cik='1', a='P1', p='2019-12-31', fd='', calc='', lines='~'.join(['IS|2|3|GrossProfit|0|0||Gross profit|37029', 'IS|2|5|OperatingIncomeLoss|0|0||Operating Profit|10291']))
    qcom = dict(cik='2', a='Q1', p='2022-09-30', fd='', calc='', lines='~'.join(['IS|4|9|CostsAndExpenses|0|0||Total costs and expenses|28340', 'IS|4|10|OperatingIncomeLoss|0|0||Operating income|15860']))
    rows = [dict(ticker='PEP', accession='P1', period_end='2019-12-31', data_point='operating_expenses', status='not_presented', value=None, flags=''),
            dict(ticker='QCOM', accession='Q1', period_end='2022-09-30', data_point='operating_expenses', status='not_presented', value=None, flags=''),
            dict(ticker='QCOM', accession='Q1', period_end='2022-09-30', data_point='cost_of_revenue', status='mapped', value=D(18635), flags='')]
    p, q, _ = RA.apply_cost_and_opex(rows, [pep, qcom])
    assert p['value'] == D(26738) and q['value'] == D(9705) and 'opex_from_printed_totals' in q['flags']


def test_gross_profit_not_printed_is_derived_and_corroborated():
    # ruling C1: revenue - cost of revenue, derived_not_printed; an unpresented GrossProfit fact that differs makes it DISAGREE
    RA.EXT['gp'] = {'G1': D('1607.6')}   # standard_inputs.gross_profit_facts over the extract (unpresented GrossProfit fact)
    rows = [dict(ticker='SCCO', accession='G1', period_end='2015-12-31', data_point=dp, status=st, value=v, flags='', calc_check='')
            for dp, st, v in (('gross_profit', 'not_presented', None), ('revenue', 'mapped', D('5045.9')), ('cost_of_revenue', 'mapped', D('2927.6')))]
    g = RA.derive_gross_profit(rows)[0]
    assert g['status'] == 'derived' and g['value'] == D('2118.3') and 'derived_not_printed' in g['flags'] and 'DISAGREE' in g['calc_check']
    rows[2]['status'] = 'not_presented'; rows[0].update(status='not_presented', value=None, flags='', calc_check='')
    assert RA.derive_gross_profit(rows)[0]['status'] == 'not_presented'   # cost of revenue not resolvable (ORCL)


def test_gross_profit_rulings_scco_explained_difference_and_cop_later_column():
    # SCCO 2015: the filer's GrossProfit fact (1,607.6) = revenue - COR - D&A; the cell stays derived 2,118.3 with an explained difference
    RA.EXT['gp'] = {'S1': D('1607.6')}
    rows = [dict(ticker='SCCO', cik='1', accession='S1', period_end='2015-12-31', data_point=dp, status=st, value=v, flags='', calc_check='')
            for dp, st, v in (('gross_profit', 'not_presented', None), ('revenue', 'mapped', D('5045.9')), ('cost_of_revenue', 'mapped', D('2927.6')),
                              ('depreciation_and_amortization', 'mapped', D('510.7')))]
    g = RA.derive_gross_profit(rows)[0]
    assert g['value'] == D('2118.3') and 'gp_filer_fact_excludes_da' in g['flags'] and 'DISAGREE' not in g['calc_check']
    # COP 2016: cost of revenue from the later 10-K's FY-2 column; revenue from the same column ties to the own revenue cell -> derived, cites that filing
    RA.EXT['gp'] = {}
    RA.EXT['comp'] = {'L19': 'SalesX|4|23693|2016-12-31'}
    def cop(rev_comp):
        RA.EXT['comp'] = {'L19': f'SalesX|4|{rev_comp}|2016-12-31'}
        rows = [dict(ticker='COP', cik='2', accession='C16', period_end='2016-12-31', data_point='gross_profit', status='not_presented', value=None, flags=''),
                dict(ticker='COP', cik='2', accession='C16', period_end='2016-12-31', data_point='revenue', status='mapped', value=D(23693), tags='SalesRevenueNet', flags=''),
                dict(ticker='COP', cik='2', accession='L19', period_end='2016-12-31', data_point='cost_of_revenue', status='mapped', value=D(9994), column='comparative', flags=''),
                dict(ticker='COP', cik='2', accession='L19', period_end='2018-12-31', data_point='revenue', status='mapped', value=D(36417), tags='SalesX', flags='')]
        return RA.derive_gross_profit(rows)[0]
    g = cop(23693)
    assert g['value'] == D(13699) and g['accession'] == 'L19' and g['column'] == 'comparative'
    assert cop(23718)['status'] == 'not_presented'      # the later column's revenue does not tie to the own revenue cell (MPC)
    RA.EXT['comp'] = {}


def test_a_line_whose_label_names_items_beyond_the_data_point_is_combined():
    # MSFT CF 'Depreciation, amortization, and other' -> combined; CVX 'Sales and other operating revenues' stays revenue
    fm = dict(cik='1', a='M1', p='2024-06-30', fd='', calc='', lines='CF|6|4|DepreciationAmortizationAndOther|1|0||Depreciation, amortization, and other|22287')
    fc = dict(cik='2', a='C1', p='2024-12-31', fd='', calc='', lines='IS|2|2|Revenues|0|0||Sales and other operating revenues|193414')
    rows = [dict(ticker='MSFT', accession='M1', period_end='2024-06-30', data_point='depreciation_and_amortization', status='mapped', value=D(22287), nodes='DepreciationAmortizationAndOther=22287 [R6.htm:4]', flags=''),
            dict(ticker='MSFT', accession='M1', period_end='2024-06-30', data_point='interest_income', status='mapped', value=D(3157), nodes='InvestmentIncomeNet=3157 [NOTE]', flags=''),
            dict(ticker='CVX', accession='C1', period_end='2024-12-31', data_point='revenue', status='mapped', value=D(193414), nodes='Revenues=193414 [R2.htm:2]', flags='')]
    da, ii, rev = RA.apply_label_beyond(rows, [fm, fc])
    assert da['status'] == 'combined' and da['value'] is None and 'label_beyond' in da['flags']
    assert ii['status'] == 'combined' and rev['status'] == 'mapped'


def test_trade_and_other_is_receivables_when_it_is_the_only_receivables_line():
    # AR single-line ruling: CAT 'Receivables - trade and other' alone on the face stays mapped; beside a trade line it is combined
    one = dict(cik='1', a='A1', p='2024-12-31', fd='', calc='', lines='BS|2|3|AccountsReceivableNetCurrent|0|0||Receivables - trade and other|9282')
    two = dict(cik='2', a='A2', p='2024-12-31', fd='', calc='', lines='~'.join(['BS|2|3|AccountsReceivableNetCurrent|0|0||Receivables - trade and other|9282', 'BS|2|4|AccountsReceivableTradeCurrent|0|0||Trade receivables|8000']))
    rows = [dict(ticker='CAT', accession=a, period_end='2024-12-31', data_point='accounts_receivable', status='mapped', value=D(9282), nodes='AccountsReceivableNetCurrent=9282 [R2.htm:3]', flags='') for a in ('A1', 'A2')]
    r1, r2 = RA.apply_label_beyond(rows, [one, two])
    assert r1['status'] == 'mapped' and r2['status'] == 'combined'


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
