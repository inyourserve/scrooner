"""PR #4 (fsn_store cf_detector / cf_family_replay lane rules, Verifier 2026-11-08) ported into resolve_cf, 2026-11-15."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resolve_cf import resolve_cf


def filing(lines):
    # a 5th element True marks an extension (custom) element
    s = '~'.join(f"{x[0]}|2|{i + 1}|{x[1]}|{int(len(x) > 4 and x[4])}|0|terseLabel|{x[2]}|{x[3]}" for i, x in enumerate(lines))
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


# ---- sga_expense: PM/MO 'Marketing, administration and research costs' (queue 2026-11-16)
import resolve_all
from decimal import Decimal as D


def _sga(lines, notes):
    f = filing(lines)
    L, arcs = resolve.parse(f)
    return resolve_all.role(f, L, arcs, notes, next(r for r in resolve_all.ROLES if r['data_point'] == 'sga_expense'))


def test_marketing_administration_and_research_line_is_combined_sga():
    # PM FY2017 R4:5 MarketingAdministrationAndResearchCosts 6,725; the G&A note fact (164) is not SG&A
    r = _sga([('IS', 'GrossProfit', 'Gross profit', 18316), ('IS', 'MarketingAdministrationAndResearchCosts', 'Marketing, administration and research costs', 6725),
              ('IS', 'OperatingIncomeLoss', 'Operating income', 11503)], {('GeneralAndAdministrativeExpense', 4): D(164)})
    assert r['status'] == 'combined' and r['tags'] == 'MarketingAdministrationAndResearchCosts'


def test_lone_general_and_administrative_note_fact_is_never_sga():
    r = _sga([('IS', 'GrossProfit', 'Gross profit', 18316), ('IS', 'OperatingIncomeLoss', 'Operating income', 11503)], {('GeneralAndAdministrativeExpense', 4): D(164)})
    assert r['status'] == 'not_presented' and r['value'] is None
    # the full SG&A note fact still serves
    r = _sga([('IS', 'GrossProfit', 'Gross profit', 18316)], {('SellingGeneralAndAdministrativeExpense', 4): D(6000)})
    assert r['status'] == 'mapped' and r['value'] == D(6000)


# ---- Dhairya ruling 2026-11-16: absent_in_own_filing (a gap year inside a valued row hides only on proven absence)
def _absent(lines, notes='', later_comp='', dp='cash_paid_for_interest'):
    own = dict(filing(lines), cik='9', a='A16', p='2016-09-30')
    nxt = dict(filing([('CF', 'NetIncomeLoss', 'Net income', 1)]), cik='9', a='A17', p='2017-09-30')
    row = dict(data_point=dp, status='not_presented', accession='A16', period_end='2016-09-30', column='own', flags='roles', why='no line')
    resolve_all.apply_absent_in_own_filing([row], [own, nxt], {'A16': notes}, {'A17': later_comp})
    return 'absent_in_own_filing' in row['flags']


def test_absence_proven_when_no_face_line_no_fact_and_no_later_fact():
    # QCOM FY2016 10-K: no interest-paid line, no InterestPaid/InterestPaidNet fact (FY2015 printed 8M)
    assert _absent([('IS', 'Revenues', 'Revenues', 100)])


def test_absence_not_claimed_when_an_undimensioned_fact_exists():
    assert not _absent([('IS', 'Revenues', 'Revenues', 100)], notes='InterestPaidNet|4|8000000')


def test_absence_not_claimed_when_any_statement_prints_the_element():
    assert not _absent([('BS', 'InterestPaidNet', 'Interest paid', None)])


def test_absence_not_claimed_when_a_later_10k_prints_the_year():
    # a comparative year is filled or replayed, never hidden
    assert not _absent([('IS', 'Revenues', 'Revenues', 100)], later_comp='InterestPaidNet|4|7000000|2016-09-30')


def test_absence_not_claimed_for_a_custom_financing_line_naming_buybacks():
    assert not _absent([('CF', 'xyz_SharesBoughtBack', 'Purchases of common stock', 50)], dp='share_buybacks')
    assert _absent([('CF', 'ProceedsFromIssuanceOfLongTermDebt', 'Proceeds from debt', 50)], dp='share_buybacks')


def test_continuing_operations_ci_total_serves_only_without_discontinued_operations():
    # ADI FY2015 R3: adi_ComprehensiveIncomeFromContinuingOperations 814,553, no discontinued operations
    R = next(r for r in resolve_all.ROLES if r['data_point'] == 'comprehensive_income')
    f = filing([('IS', 'Revenues', 'Revenues', 100)]); L, arcs = resolve.parse(f)
    r = resolve_all.role(f, L, arcs, {('ComprehensiveIncomeFromContinuingOperations', 4): D(814553)}, R)
    assert r['status'] == 'mapped' and r['value'] == D(814553)
    r = resolve_all.role(f, L, arcs, {('ComprehensiveIncomeFromContinuingOperations', 4): D(814553), ('IncomeLossFromDiscontinuedOperationsNetOfTax', 4): D(5)}, R)
    assert r['status'] == 'not_presented'


def test_net_treasury_purchases_line_is_combined_buybacks():
    # GE FY2017 R6:40 ProceedsFromRepurchaseOfEquity 'Net dispositions (purchases) of GE shares for treasury' -2,550
    b = resolve_cf(fin(('CF', 'ProceedsFromRepurchaseOfEquity', 'Net dispositions (purchases) of GE shares for treasury', -2550)), {})['share_buybacks']
    assert b['status'] == 'combined' and b['value'] is None and 'dispositions/issuances, net' in b['why']


def test_share_count_line_does_not_block_proven_absence():
    # DHR FY2015 CF 'Shares held as Treasury shares' (a share count, StockRedeemed...Shares)
    assert _absent([('CF', 'StockRedeemedThroughDistributionOfABusinessDuringPeriodShares', 'Shares held as Treasury shares', 26)], dp='share_buybacks')


def test_note_natured_year_fills_from_a_later_note_comparative():
    # TSLA FY2017 amortization: the FY2019 10-K maps its own year from the note and holds AmortizationOfIntangibleAssets 40 for 2017
    import standard_inputs
    def rows(dp, tag):
        return [dict(cik='1', data_point=dp, period_end='2017-12-31', accession='A17', status='not_presented', tags='', nodes='', value=None),
                dict(cik='1', data_point=dp, period_end='2018-12-31', accession='A18', status='not_presented', tags='', nodes='', value=None),
                dict(cik='1', data_point=dp, period_end='2019-12-31', accession='A19', status='mapped', tags=tag, nodes=f'{tag}=44 [NOTE]', value='44')]
    out = standard_inputs.comparative_fill(rows('amortization_of_intangibles', 'AmortizationOfIntangibleAssets'), {'A19': 'AmortizationOfIntangibleAssets|4|40|2017-12-31'}, set())
    assert str(out[('A17', 'amortization_of_intangibles')]['value']).startswith('40')
    # a note figure never fills a face data point (PM SG&A 162M)
    out = standard_inputs.comparative_fill(rows('sga_expense', 'SellingGeneralAndAdministrativeExpense'), {'A19': 'SellingGeneralAndAdministrativeExpense|4|40|2017-12-31'}, set())
    assert ('A17', 'sga_expense') not in out


def test_total_debt_absence_reads_every_debt_element_and_debt_label():
    # FTNT FY2019: no borrowings of any kind before its 2021 notes
    assert _absent([('BS', 'AccountsPayableCurrent', 'Accounts payable', 5)], dp='total_debt')
    assert not _absent([('BS', 'LongTermDebtNoncurrent', 'Long-term debt', 5)], dp='total_debt')
    assert not _absent([('BS', 'xyz_SeniorNotes', 'Senior notes, net', 5)], dp='total_debt')
    assert _absent([('BS', 'OperatingLeaseLiabilityNoncurrent', 'Operating lease liabilities', 5)], dp='total_debt')


def test_gross_profit_absence_needs_no_cost_of_revenue_to_derive_from():
    own = dict(filing([('IS', 'Revenues', 'Revenues', 100)]), cik='9', a='A16', p='2016-12-31')
    gp = dict(data_point='gross_profit', status='not_presented', accession='A16', period_end='2016-12-31', column='own', flags='core', why='')
    resolve_all.apply_absent_in_own_filing([gp], [own], {}, {})
    assert 'absent_in_own_filing' in gp['flags']
    gp['flags'] = 'core'
    cor = dict(data_point='cost_of_revenue', status='mapped', accession='A16', period_end='2016-12-31', column='own', flags='', why='')
    resolve_all.apply_absent_in_own_filing([gp, cor], [own], {}, {})
    assert 'absent_in_own_filing' not in gp['flags']


def test_eps_printed_only_per_class_is_combined_not_missing():
    # DELL FY2018 R4:29 'Earnings (loss) per share attributable to Dell Technologies Inc.' (DHI Group / Class V members only)
    f = dict(filing([('IS', 'NetIncomeLoss', 'Net loss', -1), ('IS', 'EarningsPerShareBasicAbstract', 'Earnings (loss) per share attributable to Dell Technologies Inc. - basic', '')]), a='A18')
    rows = [dict(data_point='basic_eps', status='not_presented', accession='A18', column='own', flags='roles', why='', value=None),
            dict(data_point='diluted_eps', status='not_presented', accession='A18', column='own', flags='roles', why='', value=None)]
    resolve_all.apply_eps_per_class(rows, [f])
    assert rows[0]['status'] == 'combined' and 'eps_per_class' in rows[0]['flags'] and 'per class of stock' in rows[0]['why']
    assert rows[1]['status'] == 'not_presented'   # no diluted line printed at all
    # a valued per-share line is never touched
    f2 = dict(filing([('IS', 'EarningsPerShareBasic', 'Basic EPS', '6.38')]), a='A20')
    r = dict(data_point='basic_eps', status='not_presented', accession='A20', column='own', flags='', why='', value=None)
    resolve_all.apply_eps_per_class([r], [f2])
    assert r['status'] == 'not_presented'


def test_custom_ppe_and_intangibles_purchase_line_is_capex():
    # NVDA FY2021 R8:21 nvda_PurchasesOfPropertyAndEquipmentAndIntangibleAssets 'Purchases related to property and equipment and intangible a' (cut at 60)
    f = filing([('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 5822),
                ('CF', 'PurchasesOfPropertyAndEquipmentAndIntangibleAssets', 'Purchases related to property and equipment and intangible a', 1128, True),
                ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -19675)])
    c = resolve_cf(f, {})['capex']
    assert c['status'] == 'mapped' and c['value'] == 1128
    # an intangibles-only purchase line stays out
    f = filing([('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 5822),
                ('CF', 'xyz_PurchasesOfIntangibles', 'Purchases of intangible assets', 50, True),
                ('CF', 'NetCashProvidedByUsedInInvestingActivities', 'Net cash used in investing activities', -19675)])
    assert resolve_cf(f, {})['capex']['status'] == 'not_presented'


def test_cf_family_flags_reach_the_output_row():
    f = filing([('CF', 'NetCashProvidedByUsedInOperatingActivities', 'Net cash provided by operating activities', 100),
                ('CF', 'PaymentsForRepurchaseOfCommonStock', 'Share repurchases, including shares surrendered for tax withholding', 1639),
                ('CF', 'NetCashProvidedByUsedInFinancingActivities', 'Net cash used in financing activities', -40)])
    assert resolve_all.family_rows(f, {}, '')['share_buybacks']['flags'] == 'buyback_label_combined'


def test_unclassified_balance_sheet_proves_current_subtotals_absent():
    # GE FY2015-18: no AssetsCurrent / LiabilitiesCurrent anywhere in the filing
    assert _absent([('BS', 'Assets', 'Total assets', 100)], dp='current_assets')
    assert _absent([('BS', 'Liabilities', 'Total liabilities', 60)], dp='current_liabilities')
    assert not _absent([('BS', 'AssetsCurrent', 'Total current assets', 40)], dp='current_assets')


def test_dash_on_a_payment_line_is_inferred_from_the_filings_other_columns():
    # BA FY2022 R8:40 'Dividends paid': 2022 -, 2021 -, 2020 (1,158); the zlines extract has no row for this filing
    import standard_inputs
    f = dict(filing([('CF', 'PaymentsOfDividendsCommonStock', 'Dividends paid', '')]), a='A22', p='2022-12-31')
    row = dict(data_point='dividends_paid', status='not_presented', accession='A22', column='own')
    roles = {'dividends_paid': ('CF', ['PaymentsOfDividendsCommonStock'])}
    pz = standard_inputs.printed_zero_inferred([row], [f], {'A22': 'PaymentsOfDividendsCommonStock|4|1158|2020-12-31'}, {}, roles)
    assert pz[('A22', 'dividends_paid')]['r_line'] == 'R2:1'
    # an own-period member fact means the year has a value: no dash
    assert not standard_inputs.printed_zero_inferred([row], [f], {'A22': 'PaymentsOfDividendsCommonStock|4|1158|2020-12-31'}, {'A22': 'PaymentsOfDividendsCommonStock|4|9|ClassOfStock=A;'}, roles)
    # no earlier-column fact: nothing to infer from
    assert not standard_inputs.printed_zero_inferred([row], [f], {}, {}, roles)
    # never outside the payment lines (GOOG EPS by class, PSX PP&E)
    eps = dict(row, data_point='basic_eps')
    assert not standard_inputs.printed_zero_inferred([eps], [f], {'A22': 'PaymentsOfDividendsCommonStock|4|1158|2020-12-31'}, {}, {'basic_eps': ('CF', ['PaymentsOfDividendsCommonStock'])})


def test_lines_the_family_excludes_never_block_proven_absence():
    # BA FY2023 'Treasury shares issued for 401(k) contribution'; PM FY2018 subsidiary shares from NCI; TSLA NCI distributions
    assert _absent([('CF', 'Employee401kTreasuryStockContributionNoncashExpense', 'Treasury shares issued for 401(k) contribution', 1515)], dp='share_buybacks')
    assert _absent([('CF', 'PaymentsToMinorityShareholders', 'Purchase of subsidiary shares from noncontrolling interests', 5)], dp='share_buybacks')
    assert _absent([('CF', 'xyz_DistributionsNci', 'Distributions paid to noncontrolling interests', 5)], dp='dividends_paid')
    assert not _absent([('CF', 'xyz_Buyback', 'Purchases of treasury stock', 5)], dp='share_buybacks')


def test_interest_income_fills_from_a_later_note_but_never_from_interest_and_dividends():
    # GE FY2017: the FY2019 10-K's note holds InvestmentIncomeInterest 105 for 2017; DELL/BLK's InvestmentIncomeInterestAndDividend is wider
    import standard_inputs
    def rows(tag):
        return [dict(cik='1', data_point='interest_income', period_end='2017-12-31', accession='A17', status='not_presented', tags='', nodes='', value=None),
                dict(cik='1', data_point='interest_income', period_end='2018-12-31', accession='A18', status='not_presented', tags='', nodes='', value=None),
                dict(cik='1', data_point='interest_income', period_end='2019-12-31', accession='A19', status='mapped', tags=tag, nodes=f'{tag}=143 [NOTE]', value='143')]
    out = standard_inputs.comparative_fill(rows('InvestmentIncomeInterest'), {'A19': 'InvestmentIncomeInterest|4|105|2017-12-31'}, set())
    assert str(out[('A17', 'interest_income')]['value']).startswith('105')
    out = standard_inputs.comparative_fill(rows('InvestmentIncomeInterestAndDividend'), {'A19': 'InvestmentIncomeInterestAndDividend|4|105|2017-12-31'}, set())
    assert ('A17', 'interest_income') not in out


def test_card_member_loans_are_the_loan_classes_of_a_member_only_line_when_classes_tie_to_total_assets():
    # AXP FY2022 R2: 'Financing receivables, net' (NotesReceivableNet) by class: Card Member loans 104,217, receivables 57,384, other 5,357
    lines = [('BS', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'Total cash and cash equivalents', 33914),
             ('BS', 'NotesReceivableNet', 'Financing receivables, net', ''), ('BS', 'DebtAndEquitySecuritiesAvailableForSale', 'Investment securities', 4578),
             ('BS', 'PropertyPlantAndEquipmentNet', 'Premises and equipment', 5215), ('BS', 'OtherAssets', 'Other assets', 17689), ('BS', 'Assets', 'Total assets', 228354)]
    f = dict(filing(lines), a='A22')
    f['calc'] = '~'.join(f"1|Assets|{t}|1" for t in ('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'NotesReceivableNet', 'DebtAndEquitySecuritiesAvailableForSale', 'PropertyPlantAndEquipmentNet', 'OtherAssets'))
    seg = 'FinancingReceivableRecordedInvestmentByClassOfFinancingReceivable'
    mf = {'A22': f'NotesReceivableNet|0|104217|{seg}=CardmemberLoans;~NotesReceivableNet|0|57384|{seg}=CardMemberReceivables;~NotesReceivableNet|0|5357|{seg}=OtherLoans;'}
    def run(mf):
        r = dict(data_point='loans_net', status='not_presented', accession='A22', column='own', flags='roles', why='', value=None)
        resolve_all.apply_member_loans([r], [f], mf)
        return r
    r = run(mf)
    assert r['status'] == 'component_sum' and r['value'] == 104217 + 5357 and 'member_sum' in r['flags'] and 'CardMemberReceivables' in r['why']
    # classes that do not tie to total assets: stays open
    assert run({'A22': mf['A22'].replace('|5357|', '|5000|')})['status'] == 'not_presented'


def test_printed_all_class_share_total_beats_an_incomplete_class_sum():
    # Google Inc FY2014 R3:18 'Common and Capital Stock, Shares, Outstanding' 680,172,000; class A 286,560,000 + B 53,213,000 only
    import resolve_bs
    cpv = ('3|18|CommonandCapitalStockSharesOutstanding|Common and Capital Stock, Shares, Outstanding||680172000~'
           '3|23|CommonStockSharesOutstanding|Common stock, shares outstanding|ClassOfStock=CommonClassA;|286560000~'
           '3|23|CommonStockSharesOutstanding|Common stock, shares outstanding|ClassOfStock=CommonClassB;|53213000')
    r = resolve_bs.shares({'cpv': cpv}, {}, {})
    assert r['value'] == 680172000 and r['rule'] == 'class_total'
    # without the total the class sum stands
    r = resolve_bs.shares({'cpv': cpv.split('~', 1)[1]}, {}, {})
    assert r['value'] == 339773000 and r['rule'] == 'class_sum'


def test_combined_ci_including_nci_takes_the_later_parent_figure():
    # DIS FY2017 (predecessor 10-K prints only CI including NCI); the FY2019 10-K prints ComprehensiveIncomeNetOfTax for 2017
    import standard_inputs
    rows = [dict(cik='1', data_point='comprehensive_income', period_end='2017-09-30', accession='A17', status='combined', tags='X', nodes='X=1 [R4.htm:9]', value=None),
            dict(cik='1', data_point='comprehensive_income', period_end='2018-09-30', accession='A18', status='combined', tags='X', nodes='X=1 [R4.htm:9]', value=None),
            dict(cik='1', data_point='comprehensive_income', period_end='2019-09-30', accession='A19', status='mapped', tags='ComprehensiveIncomeNetOfTax', nodes='ComprehensiveIncomeNetOfTax=5 [R4.htm:9]', value='5')]
    out = standard_inputs.comparative_fill(rows, {'A19': 'ComprehensiveIncomeNetOfTax|4|9431|2017-09-30'}, set())
    assert str(out[('A17', 'comprehensive_income')]['value']).startswith('9431')
    rows[2]['tags'] = 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest'
    rows[2]['nodes'] = 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest=5 [R4.htm:9]'
    assert ('A17', 'comprehensive_income') not in standard_inputs.comparative_fill(rows, {'A19': 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|4|9431|2017-09-30'}, set())


def test_a_gap_year_inside_the_run_gets_rows_from_the_next_10k_columns():
    # MRVL FY2021: predecessor 10-Ks to FY2020, successor from FY2022; the FY2022 10-K prints FY2021 in its FY-1 column
    import standard_inputs
    filings = [dict(cik='9', a='A20', p='2020-02-01'), dict(cik='9', a='A22', p='2022-01-29')]
    rows = [dict(ticker='MRVL', cik='0000000009', data_point='revenue', column='own')]
    comp = {'A22': 'Revenues|4|2969|2021-01-30', 'A20': ''}
    out = standard_inputs.before_first_10k_rows(rows, filings, comp, start='2014-01-01')
    assert [(r['period_end'], r['data_point']) for r in out] == [('2021-01-30', 'revenue')]
    # a year an own 10-K covers never gets a second row
    filings.append(dict(cik='9', a='A21', p='2021-01-30'))
    assert standard_inputs.before_first_10k_rows(rows, filings, comp, start='2014-01-01') == []


# ---- Dhairya 2026-11-16: note data points with a filer's own element; quarterly DPS
def test_custom_interest_paid_note_element_serves_and_flags_net_of_interest_received():
    # QCOM FY2016 note: qcom:Interestpaidnetofinterestreceived 282
    R = next(r for r in resolve_all.ROLES if r['data_point'] == 'cash_paid_for_interest')
    f = filing([('IS', 'Revenues', 'Revenues', 100)]); L, arcs = resolve.parse(f)
    r = resolve_all.role(f, L, arcs, {('Interestpaidnetofinterestreceived', 4): D(282)}, R)
    assert r['status'] == 'mapped' and r['value'] == D(282) and 'net_of_interest_received' in r['flags']
    # a component (ANET interest on notes payable, PANW contractual interest) is never the whole figure
    for t in ('InterestPaidNotesPayable', 'InterestPaidContractualInterest', 'InterestPaidLeaseFinancingObligation'):
        assert resolve_all.role(f, L, arcs, {(t, 4): D(3)}, R)['status'] == 'not_presented'


def test_any_element_named_for_a_note_data_point_blocks_proven_absence():
    assert not _absent([('IS', 'Revenues', 'Revenues', 100)], notes='InterestPaidNotesPayable|4|3639000')
    assert _absent([('IS', 'Revenues', 'Revenues', 100)], notes='InterestExpense|4|5')


def test_custom_amortization_element_by_location_is_the_location_total():
    # CRM FY2020: crm:AmortizationOfPurchasedIntangiblesFromBusinessCombinations, CostOfSales 440 + SellingAndMarketingExpense 352
    import standard_inputs
    mf = {'A20': 'AmortizationOfPurchasedIntangiblesFromBusinessCombinations|4|440|IncomeStatementLocation=CostOfSales;~'
                 'AmortizationOfPurchasedIntangiblesFromBusinessCombinations|4|352|IncomeStatementLocation=SellingAndMarketingExpense;'}
    x = standard_inputs.amortization_location_total({}, mf)['A20']
    assert x['value'] == 792 and x['tag'] == 'AmortizationOfPurchasedIntangiblesFromBusinessCombinations'
    # a standard AmortizationOfIntangibleAssets location set wins over a custom one
    mf['A20'] += '~AmortizationOfIntangibleAssets|4|500|IncomeStatementLocation=CostOfSales;~AmortizationOfIntangibleAssets|4|292|IncomeStatementLocation=OperatingExpense;'
    assert 'tag' not in standard_inputs.amortization_location_total({}, mf).get('A20', {})


def test_annual_dps_is_the_sum_of_four_quarterly_facts_of_the_same_filing():
    # C FY2023: 0.51 x 2 + 0.53 x 2 = 2.08, no annual fact
    import standard_inputs
    f = [dict(a='A23', p='2023-12-31')]
    nf = {'A23': 'CommonStockDividendsPerShareDeclared|1|0.53'}
    cf = {'A23': 'CommonStockDividendsPerShareDeclared|1|0.51|2023-03-31~CommonStockDividendsPerShareDeclared|1|0.51|2023-06-30~CommonStockDividendsPerShareDeclared|1|0.53|2023-09-30'}
    x = standard_inputs.quarterly_dps(nf, cf, f)['A23']
    assert x['value'] == D('2.08') and len(x['parts']) == 4
    assert 'A23' not in standard_inputs.quarterly_dps({'A23': nf['A23'] + '~CommonStockDividendsPerShareDeclared|4|2.08'}, cf, f)   # an annual fact exists
    assert 'A23' not in standard_inputs.quarterly_dps(nf, {'A23': cf['A23'].rsplit('~', 1)[0]}, f)   # only three quarters


# ---- Dhairya 2026-11-16 (second filing-checked sample, 8 of 20 face hides wrong)
def _ov(lines, dp, notes=''):
    f = dict(filing(lines), a='A22')
    r = dict(data_point=dp, status='not_presented', accession='A22', column='own', flags='bs_family', why='', value=None)
    resolve_all.apply_face_label_overrides([r], [f], {'A22': notes})
    return r


def test_face_label_names_the_data_point_whatever_its_element():
    # AT&T FY2022 R6:12 'Inventories' tagged PrepaidExpenseCurrent 3,123
    r = _ov([('BS', 'PrepaidExpenseCurrent', 'Inventories', 3123), ('BS', 'OtherAssetsCurrent', 'Prepaid and other current assets', 14818)], 'inventory')
    assert r['status'] == 'mapped' and r['value'] == 3123 and 'label_overrides_element' in r['flags']
    assert _ov([('BS', 'OtherAssetsCurrent', 'Prepaid and other current assets', 14818)], 'inventory')['status'] == 'not_presented'
    # and such a line blocks a proven-absence hide
    assert not _absent([('BS', 'PrepaidExpenseCurrent', 'Inventories', 3123)], dp='inventory')


def test_insurer_premiums_receivable_is_accounts_receivable():
    # PGR FY2022 R2:15 PremiumsReceivableAtCarryingValue 10,416.9 (ruling 2026-11-16)
    r = _ov([('BS', 'PremiumsReceivableAtCarryingValue', 'Premiums receivable, net of allowance for credit losses', 10416900000)], 'accounts_receivable')
    assert r['status'] == 'mapped' and 'insurer_premiums_receivable' in r['flags']


def test_trade_receivables_from_a_composition_note():
    # NFLX FY2022 'Other current assets' note: TradeReceivablesHeldForSaleAmount 988.9M
    r = _ov([('BS', 'OtherAssetsCurrent', 'Other current assets', 3208021000)], 'accounts_receivable', notes='TradeReceivablesHeldForSaleAmount|0|988898000~OtherReceivablesNetCurrent|0|1826388000')
    assert r['status'] == 'mapped' and r['value'] == 988898000 and 'from_composition_note' in r['flags']


def test_sbc_is_the_sum_of_award_type_components_without_after_tax_amounts():
    # CVX FY2022: restricted stock/units 1,013 (custom) + StockOptionPlanExpense 60; after-tax 770 / 46 never count
    notes = ('CompensationExpenseForStockAppreciationRightsRestrictedStockPerformanceUnitsAndRestrictedStockUnits|4|1013~StockOptionPlanExpense|4|60~'
             'AfterTaxCompensationExpenseForStockOptions|4|46~AfterTaxCompensationExpenseForStockAppreciationRightsRestrictedStockPerformanceUnitsAndRestrictedStockUnits|4|770')
    r = _ov([('CF', 'NetIncomeLoss', 'Net income', 35465)], 'sbc', notes=notes)
    assert r['status'] == 'component_sum' and r['value'] == 1073 and 'award_type_sum' in r['flags']
    assert _ov([('CF', 'NetIncomeLoss', 'Net income', 35465)], 'sbc', notes='StockOptionPlanExpense|4|60')['status'] == 'not_presented'
