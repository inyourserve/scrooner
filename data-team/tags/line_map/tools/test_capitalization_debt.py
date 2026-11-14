"""Tests for total_debt.py region and resolve.py pretax position (run: python3 this file)."""
import os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import total_debt, resolve


def _f(lines, calc=''):
    return dict(cik='753308', a='0000753308-18-000013', p='2017-12-31', fd='2018-02-16', calc=calc,
                lines='~'.join(f"{st}|5|{i + 1}|{t}|0|0||{lb}|{'' if v is None else v}" for i, (st, t, lb, v) in enumerate(lines)))


def test_utility_capitalization_debt_after_the_equity_line_is_debt():
    # NEE FY2017: CAPITALIZATION (common equity, long-term debt) is printed before current liabilities
    f = _f([('BS', 'Assets', 'Total assets', 97), ('BS', 'StockholdersEquity', 'Common shareholders equity', 30),
            ('BS', 'LongTermDebtNoncurrent', 'Long-term debt', 31463), ('BS', 'CommercialPaper', 'Commercial paper', 1687),
            ('BS', 'LongTermDebtCurrent', 'Current maturities of long-term debt', 1676), ('BS', 'LiabilitiesAndStockholdersEquity', 'Total', 97)])
    rows = total_debt.run([f], [], {})
    own = next(r for r in rows if r['column'] == 'own')
    assert own['status'] == 'component_sum' and D(own['value']) == D(34826)


def test_pretax_is_found_by_position_under_any_node_that_subtracts_tax():
    # COP FY2015: the node above tax is IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest
    calc = 'g|IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest|IncomeFromContinuingOperationsBeforeIncomeTaxes|1~g|IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest|IncomeTaxExpenseBenefit|-1'
    f = _f([('IS', 'Revenues', 'Revenues', 30), ('IS', 'IncomeFromContinuingOperationsBeforeIncomeTaxes', 'Income before income taxes', -7239),
            ('IS', 'IncomeTaxExpenseBenefit', 'Income tax', -2868), ('IS', 'IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest', 'Income from continuing operations', -4371)], calc)
    out, _ = resolve.resolve(f)
    assert out['income_before_tax']['value'] == D(-7239)


if __name__ == '__main__':
    n = 0
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); n += 1
    print(n, 'tests passed')
