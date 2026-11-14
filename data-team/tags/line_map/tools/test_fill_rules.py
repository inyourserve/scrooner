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
    os.environ['PRINTED_ZERO'] = _csv([dict(ticker='IBM', period_end='2020-12-31', data_point='share_buybacks', accession='A1', tag='PaymentsForRepurchaseOfCommonStock', stmt='CF', r_line='R6:30', label='Common stock repurchases', evidence='e')])
    os.environ['COMPARATIVE_FILL'] = _csv([dict(ticker='CAT', period_end='2018-12-31', data_point='dividends_per_share', own_accession='A2', accession='N2', tag='CommonStockDividendsPerShareDeclared', loc='R5.htm:9', value='3.36', source='s')])
    rows = RA.fill_printed_zero_and_comparative([_row('A1', 'share_buybacks'), _row('A2', 'dividends_per_share', 'CAT', '2018-12-31'), _row('A3', 'capex')], {})
    z, c, n = rows
    assert z['status'] == 'mapped' and z['value'] == D(0) and 'printed_zero' in z['flags'] and 'R6:30' in z['nodes']
    assert c['value'] == D('3.36') and c['accession'] == 'N2' and c['column'] == 'comparative' and 'comparative_fill' in c['flags']
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


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
