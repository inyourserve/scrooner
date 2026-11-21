"""Tests for resolve_all.apply_opex_combined_total_less_cor (rule X117, resolver .88; registry operating_expenses fallback 2).
Run: python3 -m pytest this file. Mutation check: with the function returning its rows untouched, the first two tests fail."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_all as RA

DIS_LINES = '~'.join(['IS|3|9|Revenues|0|0|terseLabel|Revenues|91361000000',
                      'IS|3|10|CostOfGoodsAndServicesSold|0|1|negatedLabel|Cost of Goods and Services Sold|',
                      'IS|3|11|SellingGeneralAndAdministrativeExpense|0|1|negatedTerseLabel|Selling, general, administrative and other|15759000000',
                      'IS|3|12|DepreciationDepletionAndAmortization|0|1|negatedTerseLabel|Depreciation and amortization|4990000000',
                      'IS|3|13|CostsAndExpenses|0|1|negatedTotalLabel|Total costs and expenses|79447000000'])
DIS_CALC = '4|CostsAndExpenses|CostOfGoodsAndServicesSold|1~4|CostsAndExpenses|DepreciationDepletionAndAmortization|1~4|CostsAndExpenses|SellingGeneralAndAdministrativeExpense|1'


def _rows(acc='A24', cor_acc='A24', opex_nodes='CostsAndExpenses=79447000000.0000 [R3.htm:13]'):
    return [dict(accession=acc, data_point='operating_expenses', status='combined', value=None, nodes=opex_nodes, column='own', flags='roles', why='only combined'),
            dict(accession=cor_acc, data_point='cost_of_revenue', status='component_sum', value=D(58698000000), column='own', flags='roles',
                 nodes='CostOfGoodsAndServicesSold[ProductOrService=Product]=6189000000 [R3.htm:10]; CostOfGoodsAndServicesSold[ProductOrService=Service]=52509000000 [R3.htm:10]')]


def test_opex_inside_total_costs_and_expenses_is_the_total_less_cost_of_revenue():
    # DIS FY2024 10-K R3: Total costs and expenses 79,447 - cost of products 6,189 - cost of services 52,509 = 20,749 (= SG&A 15,759 + D&A 4,990)
    r = RA.apply_opex_combined_total_less_cor(_rows(), [dict(a='A24', lines=DIS_LINES, calc=DIS_CALC)])[0]
    assert r['status'] == 'component_sum' and r['value'] == D(20749000000)
    assert r['nodes'].startswith('CostsAndExpenses=79447000000.0000 [R3.htm:13]; -CostOfGoodsAndServicesSold[ProductOrService=Product]=6189000000')
    assert 'derived:total_costs_and_expenses-cost_of_revenue' in r['flags'].split(';')


def test_other_income_expense_inside_the_total_comes_out_by_its_calc_weight():
    # MRK-style: Cost of sales 13,509; SG&A 10,102; R&D 9,752; Restructuring 632; Other (income) expense, net (402); total 33,593 -> opex 20,486
    lines = '~'.join(['IS|2|3|CostOfGoodsAndServicesSold|0|0|terseLabel|Cost of sales|13509000000', 'IS|2|4|SellingGeneralAndAdministrativeExpense|0|0|t|Selling, general and administrative|10102000000',
                      'IS|2|5|ResearchAndDevelopmentExpense|0|0|t|Research and development|9752000000', 'IS|2|6|RestructuringCharges|0|0|t|Restructuring costs|632000000',
                      'IS|2|7|OtherNonoperatingIncomeExpense|0|1|t|Other (income) expense, net|402000000', 'IS|2|8|CostsAndExpenses|0|0|t|Total Costs, Expenses and Other|33593000000'])
    calc = '~'.join(f'2|CostsAndExpenses|{t}|{w}' for t, w in (('CostOfGoodsAndServicesSold', 1), ('SellingGeneralAndAdministrativeExpense', 1), ('ResearchAndDevelopmentExpense', 1), ('RestructuringCharges', 1), ('OtherNonoperatingIncomeExpense', -1)))
    rows = _rows('A18', 'A18', 'CostsAndExpenses=33593000000.0000 [R2.htm:8]')
    rows[1].update(status='mapped', value=D(13509000000), nodes='CostOfGoodsAndServicesSold=13509000000 [R2.htm:3]')
    r = RA.apply_opex_combined_total_less_cor(rows, [dict(a='A18', lines=lines, calc=calc)])[0]
    assert r['value'] == D(20486000000) and 'OtherNonoperatingIncomeExpense=402000000 [R2.htm:7]' in r['nodes']
    # the same line with no calc weight: its sign inside the total is unknown -> stays combined
    rows = _rows('A18', 'A18', 'CostsAndExpenses=33593000000.0000 [R2.htm:8]')
    rows[1].update(status='mapped', value=D(13509000000), nodes='CostOfGoodsAndServicesSold=13509000000 [R2.htm:3]')
    assert RA.apply_opex_combined_total_less_cor(rows, [dict(a='A18', lines=lines, calc='')])[0]['status'] == 'combined'


def test_cost_of_revenue_of_another_filing_or_an_untied_calc_group_leaves_it_combined():
    assert RA.apply_opex_combined_total_less_cor(_rows(cor_acc='A26'), [dict(a='A24', lines=DIS_LINES, calc=DIS_CALC)])[0]['status'] == 'combined'
    bad = DIS_LINES.replace('|4990000000', '|4000000000')
    assert RA.apply_opex_combined_total_less_cor(_rows(), [dict(a='A24', lines=bad, calc=DIS_CALC)])[0]['status'] == 'combined'
