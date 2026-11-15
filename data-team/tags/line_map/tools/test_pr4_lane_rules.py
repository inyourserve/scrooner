"""PR #4 (fsn_store cf_detector / cf_family_replay lane rules, Verifier 2026-11-08) ported into resolve_cf, 2026-11-15."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_cf import resolve_cf


def filing(lines):
    s = '~'.join(f"{x[0]}|2|{i + 1}|{x[1]}|0|0|terseLabel|{x[2]}|{x[3]}" for i, x in enumerate(lines))
    return dict(cik='1', a='0000000001-26-000001', p='2025-12-31', fd='2026-02-01', lines=s, calc='')


def fin(*lines, div=True):
    head = [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 100),
            ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -50)]
    d = [('CF', 'PaymentsOfDividendsCommonStock', 'Dividends paid', 20)] if div else []
    return filing(head + d + list(lines) + [('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -40)])


def test_repurchase_including_shares_surrendered_for_tax_is_combined():
    # MCK FY2019 R8:44 PaymentsForRepurchaseOfCommonStock 'Share repurchases, including shares surrendered for tax withholding' 1,639
    b = resolve_cf(fin(('CF', 'PaymentsForRepurchaseOfCommonStock', 'Share repurchases, including shares surrendered for tax withholding', 1639)), {})['share_buybacks']
    assert b['status'] == 'combined' and b['value'] is None and b['flags'] == 'buyback_label_combined'


def test_treasury_stock_and_warrants_line_is_combined():
    # JPM FY2015 R8:43 'Treasury stock and warrants repurchased' 5,616
    b = resolve_cf(fin(('CF', 'PaymentsForRepurchaseOfCommonStock', 'Treasury stock and warrants repurchased', 5616)), {})['share_buybacks']
    assert b['status'] == 'combined' and b['value'] is None


def test_plain_repurchase_line_stays_mapped():
    b = resolve_cf(fin(('CF', 'PaymentsForRepurchaseOfCommonStock', 'Repurchase of common stock', 7258)), {})['share_buybacks']
    assert b['status'] == 'mapped' and b['value'] == 7258


def test_stock_bought_under_equity_plans_is_not_a_buyback():
    # MU FY2014 R7:36 'Cash paid to purchase common stock under equity plans' 76; the same-tag fact is no note fallback
    b = resolve_cf(fin(('CF', 'PaymentsForRepurchaseOfCommonStock', 'Cash paid to purchase common stock under equity plans', 76)), {('PaymentsForRepurchaseOfCommonStock', 4): 76})['share_buybacks']
    assert b['status'] == 'not_presented' and b['value'] is None and b['flags'] == 'buyback_sbc_plan_only'


def test_preferred_only_dividend_line_is_no_common_dividend_even_without_a_preferred_fact():
    # TMUS FY2016 R6:38 PaymentsOfDividends 'Dividends on preferred stock' 55 (no separate preferred-dividend fact in the face set)
    d = resolve_cf(fin(('CF', 'PaymentsOfDividends', 'Dividends on preferred stock', 55), div=False), {})['dividends_paid']
    assert d['status'] == 'not_presented' and d['value'] is None and d['flags'] == 'dividends_preferred_only'


def test_dividends_and_distributions_to_unit_holders_is_combined():
    # AVGO FY2018 R6:36 PaymentsOfDividends 'Dividend and distribution payments' 2,998 (ordinary shares + exchangeable LP units); BXP alike
    d = resolve_cf(fin(('CF', 'PaymentsOfDividends', 'Dividend and distribution payments', 2998), div=False), {})['dividends_paid']
    assert d['status'] == 'combined' and d['value'] is None and d['flags'] == 'dividends_incl_unit_distributions'


def test_reit_distributions_to_stockholders_stay_mapped():
    # WELL 'Cash distributions to stockholders' (no preferred): REIT distributions count
    d = resolve_cf(fin(('CF', 'CashDistributionsToStockholders', 'Cash distributions to stockholders', 900), div=False), {})['dividends_paid']
    assert d['status'] == 'mapped' and d['value'] == 900


def test_declared_but_not_paid_is_never_the_cash_dividend():
    # BXP 'Dividends and distributions declared but not paid': a non-cash disclosure, even under a cash-dividend tag
    d = resolve_cf(fin(('CF', 'PaymentsOfDividends', 'Dividends declared but not paid', 300), div=False), {})['dividends_paid']
    assert d['status'] == 'not_presented' and d['value'] is None


def test_distribution_to_affiliate_is_no_common_dividend():
    # TMUS FY2014 R6:43 PaymentsOfCapitalDistribution 'Distribution to affiliate' 0
    d = resolve_cf(fin(('CF', 'PaymentsOfCapitalDistribution', 'Distribution to affiliate', 0), div=False), {})['dividends_paid']
    assert d['status'] == 'not_presented' and d['value'] is None


# ---- PR #6 bs_derive (Verifier VERIFY-BS-DERIVE-2026-11-08, KMB 10-Q 0000055785-24-000054, 2024-03-31)
import resolve

KMB = [('BS', 'Assets', 'TOTAL ASSETS', 17092), ('BS', 'LiabilitiesCurrent', 'Total Current Liabilities', 6878),
       ('BS', 'LongTermDebtAndCapitalLeaseObligations', 'Long-Term Debt', 7161),
       ('BS', 'PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent', 'Noncurrent Employee Benefits', 652),
       ('BS', 'DeferredIncomeTaxLiabilitiesNet', 'Deferred Income Taxes', 395), ('BS', 'OtherLiabilitiesNoncurrent', 'Other Liabilities', 796),
       ('BS', 'RedeemableCommonAndPreferredSecuritiesOfSubsidiaries', 'Redeemable Preferred Securities of Subsidiaries', 26),
       ('BS', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', "Total Stockholders' Equity", 1184),
       ('BS', 'LiabilitiesAndStockholdersEquity', "TOTAL LIABILITIES AND STOCKHOLDERS' EQUITY", 17092)]


def _tl(face):
    f = filing(face)
    kids = [t for _, t, _, _ in face if t not in ('Assets', 'LiabilitiesAndStockholdersEquity')]
    f['calc'] = '~'.join(f"2|LiabilitiesAndStockholdersEquity|{c}|1" for c in kids)
    return resolve.resolve(f)[0].get('total_liabilities')


def test_redeemable_line_after_the_liabilities_is_temporary_equity():
    r = _tl(KMB)
    assert r and r['status'] == 'derived' and r['value'] == 15882


def test_mandatorily_redeemable_is_a_liability_wherever_printed():
    mand = [(s, t, 'Mandatorily redeemable preferred stock', v) if t.startswith('Redeemable') else (s, t, lb, v) for s, t, lb, v in KMB]
    assert _tl(mand)['value'] == 15908


def test_redeemable_line_among_the_liabilities_stays_a_liability():
    among = KMB[:5] + [KMB[6], KMB[5]] + KMB[7:]
    assert _tl(among)['value'] == 15908


# ---- working-capital line combined by its label under another element (queue 2026-11-16, ADI FY2015-16)
def _wc(*lines):
    head = [('CF', 'NetIncomeLoss', 'Net income', 700), ('CF', 'IncreaseDecreaseInAccountsReceivable', 'Accounts receivable', 71)]
    return resolve_cf(filing(head + list(lines) + [('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 907),
                                                   ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing', -50)]), {})


def test_ap_line_naming_more_items_under_a_custom_element_is_combined():
    # ADI FY2015 R7:19 DecreaseIncreaseInAccountsPayableDeferredIncomeAndAccruedLiabilities 'Accounts payable, deferred income and accrued liabilities' 56,614
    r = _wc(('CF', 'DecreaseIncreaseInAccountsPayableDeferredIncomeAndAccruedLiabilities', 'Accounts payable, deferred income and accrued liabilities', 56614))['cf_ap_change']
    assert r['status'] == 'combined' and 'DecreaseIncreaseInAccountsPayableDeferredIncomeAndAccruedLiabilities' in r['nodes']


def test_inventory_write_down_line_is_never_the_combined_inventory_line():
    # TSLA 'Inventory and purchase commitments write-downs' is a non-cash adjustment, not the inventory change
    r = _wc(('CF', 'InventoryWriteDown', 'Inventory and purchase commitments write-downs', 100))['cf_inventory_change']
    assert r['status'] == 'not_presented'


def test_brokerage_receivables_line_is_not_trade_receivables():
    # SCHW 'Receivables from brokerage clients' (IncreaseDecreaseInBrokerageReceivables)
    head = [('CF', 'NetIncomeLoss', 'Net income', 700)]
    r = resolve_cf(filing(head + [('CF', 'IncreaseDecreaseInBrokerageReceivables', 'Receivables from brokerage clients, brokers, dealers and clearing organizations', -44),
                                  ('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 907)]), {})['cf_ar_change']
    assert r['status'] == 'not_presented'


def test_combined_working_capital_cell_takes_the_later_pure_element():
    # TSLA FY2015 'Inventories and operating lease vehicles' (own, combined); the FY2016 10-K prints IncreaseDecreaseInInventories for FY2015
    import standard_inputs
    rows = [dict(cik='1', data_point='cf_inventory_change', period_end='2015-12-31', accession='A15', status='combined', tags='X', nodes='X=1 [R7.htm:12]', value=None),
            dict(cik='1', data_point='cf_inventory_change', period_end='2016-12-31', accession='A16', status='mapped', tags='IncreaseDecreaseInInventories',
                 nodes='IncreaseDecreaseInInventories=632867000 [R7.htm:12]', value='632867000')]
    comp = {'A16': 'IncreaseDecreaseInInventories|4|369364000|2015-12-31'}
    out = standard_inputs.comparative_fill(rows, comp, set())
    assert out[('A15', 'cf_inventory_change')]['value'] in ('369364000', 369364000) or str(out[('A15', 'cf_inventory_change')]['value']).startswith('369364000')
    # a combined cell of another data point never takes a later figure (AVGO dividends incl. preferred)
    for r in rows: r['data_point'] = 'dividends_paid'
    rows[1]['tags'] = 'PaymentsOfDividends'; rows[1]['nodes'] = 'PaymentsOfDividends=1 [R7.htm:30]'
    comp = {'A16': 'PaymentsOfDividends|4|369364000|2015-12-31'}
    assert ('A15', 'dividends_paid') not in standard_inputs.comparative_fill(rows, comp, set())


def test_combined_working_capital_cell_never_takes_a_later_combined_element():
    import standard_inputs
    rows = [dict(cik='1', data_point='cf_ap_change', period_end='2015-12-31', accession='A15', status='combined', tags='X', nodes='X=1 [R7.htm:12]', value=None),
            dict(cik='1', data_point='cf_ap_change', period_end='2016-12-31', accession='A16', status='mapped', tags='IncreaseDecreaseInAccountsPayableAndAccruedLiabilities',
                 nodes='IncreaseDecreaseInAccountsPayableAndAccruedLiabilities=5 [R7.htm:12]', value='5')]
    comp = {'A16': 'IncreaseDecreaseInAccountsPayableAndAccruedLiabilities|4|4|2015-12-31'}
    assert ('A15', 'cf_ap_change') not in standard_inputs.comparative_fill(rows, comp, set())
