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


def test_bank_data_points_are_read_only_from_a_bank_income_statement():
    # WMT FY2023 R3:13 InterestIncomeExpenseNet 'Interest, net' -1,874 was served as net_interest_income (found by the library's learned labels)
    R = next(r for r in resolve_all.ROLES if r['data_point'] == 'net_interest_income')
    f = filing([('IS', 'Revenues', 'Total revenues', 611289), ('IS', 'InterestIncomeExpenseNet', 'Interest, net', -1874)]); L, arcs = resolve.parse(f)
    assert resolve_all.role(f, L, arcs, {}, R)['status'] == 'not_presented'
    f = filing([('IS', 'InterestAndDividendIncomeOperating', 'Total interest income', 100), ('IS', 'InterestIncomeExpenseNet', 'Net interest income', 60)]); L, arcs = resolve.parse(f)
    assert resolve_all.role(f, L, arcs, {}, R)['status'] == 'mapped'


def test_a_label_learned_for_the_data_point_blocks_proven_absence():
    resolve_all.LEARNED['inventory'] = {'merchandise inventories'}
    assert not _absent([('BS', 'xyz_Stock', 'Merchandise inventories', 5)], dp='inventory')
    assert _absent([('BS', 'xyz_Stock', 'Prepaid expenses', 5)], dp='inventory')


def test_bank_data_points_are_out_of_template_outside_the_bank_template():
    # Dhairya ruling 2026-11-16: DE's financing-receivable provision is OUT; a bank (net interest income face) keeps its cell
    ind = dict(filing([('IS', 'Revenues', 'Net sales', 100)]), cik='1', a='A1')
    bank = dict(filing([('IS', 'InterestIncomeExpenseNet', 'Net interest income', 60)]), cik='2', a='B1')
    rows = [dict(cik='1', data_point='provision_for_credit_losses', status='mapped', value=D(5), tags='X', nodes='X=5', flags='roles', why=''),
            dict(cik='2', data_point='provision_for_credit_losses', status='mapped', value=D(9), tags='X', nodes='X=9', flags='roles', why=''),
            dict(cik='1', data_point='revenue', status='mapped', value=D(100), tags='Revenues', nodes='', flags='', why=''),
            dict(cik='1', data_point='loans_net', status='not_presented', value=None, accession='BEFORE:1:2018-01-31', flags='before_first_10k', why='')]
    for r in rows[:3]:
        r.setdefault('accession', 'A')
    resolve_all.apply_bank_template(rows, [ind, bank])
    assert rows[3]['status'] == 'not_presented' and rows[3]['flags'] == 'before_first_10k'   # no filing: the loader needs an accession
    assert rows[0]['status'] == 'not_in_template' and rows[0]['value'] is None
    assert rows[1]['status'] == 'mapped' and rows[2]['status'] == 'mapped'


def test_text_disclosure_fills_only_open_cells_of_the_same_filing(tmp_path):
    # MRVL FY2015 'we did not have any outstanding debt' (stated_zero contract, RESOLVER-OUTPUT-FORMAT.md); MCK FY2021 R&D stated in
    # Item 1 only ('Text stated' contract, edf2cfa1). XBRL always wins.
    p = tmp_path / 't.csv'
    p.write_text('cik,ticker,data_point,period_end,accession,decision,value_source,value,section,locator,quote_period,quote,why\n'
                 '0001835632,MRVL,total_debt,2015-01-31,A1,mapped,stated_zero,0,item7a,"Item 7A, p. 52",2015-01-31,"we did not have any outstanding debt",x\n'
                 '0001835632,MRVL,total_debt,2016-01-31,A2,mapped,stated_zero,0,item7a,"Item 7A, p. 55",2016-01-31,"q",x\n'
                 '0001835632,MRVL,total_debt,2017-01-31,A3,mapped,stated_zero,0,item7a,"Item 7A, p. 42",2017-01-31,"q",x\n'
                 '0000927653,MCK,research_and_development,2021-03-31,M1,mapped,text_stated,74000000,item1,"Item 1, p. 13",2021-03-31,"R&D $74 million",x\n')
    rows = [dict(cik='1835632', data_point='total_debt', period_end='2015-01-31', accession='A1', status='not_presented', value=None, flags='total_debt', why='w', nodes='n'),
            dict(cik='1835632', data_point='total_debt', period_end='2016-01-31', accession='OTHER', status='not_presented', value=None, flags='', why=''),
            dict(cik='1835632', data_point='total_debt', period_end='2017-01-31', accession='A3', status='component_sum', value=D(5), flags='total_debt', why=''),
            dict(cik='927653', data_point='research_and_development', period_end='2021-03-31', accession='M1', status='not_presented', value=None, flags='', why='')]
    resolve_all.apply_text_disclosures(rows, str(p))
    z = rows[0]
    assert (z['status'], z['value'], z['flags'], z['nodes']) == ('mapped', D(0), 'stated_zero', '')
    assert z['quote'] and z['locator'] == 'Item 7A, p. 52' and z['quote_period'] == '2015-01-31'
    assert rows[1]['status'] == 'not_presented'                     # another filing's text never fills this cell
    assert rows[2]['value'] == D(5)                                 # XBRL wins
    assert (rows[3]['status'], rows[3]['value'], rows[3]['flags'], rows[3]['nodes']) == ('mapped', D(74000000), 'text_stated', '') and rows[3]['quote_period'] == '2021-03-31'


def test_text_disclosure_reader_pairs_the_fiscal_year_and_refuses_facility_zeros():
    import text_disclosure as td
    mck = 'Item 1. Business\nResearch and Development: Research and development ("R&D") expenses were $74 million, $96 million, and $71 million during 2021, 2020, and 2019, respectively.\n'
    assert td.read_cell(mck, dict(data_point='research_and_development', period_end='2021-03-31'))['value'] == '74000000'
    assert td.read_cell(mck, dict(data_point='research_and_development', period_end='2020-03-31'))['decision'] == 'open'   # a prior year's label is not settled from this filing
    credit = 'Item 7A. Market risk\nThe 2020 Credit Facility had no borrowings during 2021 and no amounts outstanding as of March 31, 2021.\n'
    assert td.read_cell(credit, dict(data_point='total_debt', period_end='2021-03-31'))['decision'] == 'open'
    mrvl = 'Item 7A. Market risk\nOur interest rate risk relates to our portfolio as we did not have any outstanding debt as of January 31, 2015.\n'
    r = td.read_cell(mrvl, dict(data_point='total_debt', period_end='2015-01-31'))
    assert r['value_source'] == 'stated_zero' and r['value'] == '0' and r['section'] == 'item7a' and r['quote_period'] == '2015-01-31'
    assert r['locator'].startswith('Item 7A. Market risk')
    wrapped = td.to_text('<p>Item 7A. Market risk</p><div>Our risk relates to our portfolio</div><div>as we did not have any outstanding debt as of January 31, 2015.</div>')
    assert 'Our risk relates to our portfolio as we did not have any outstanding debt' in wrapped
    split = 'Item 7A.\nQuantitative and Qualitative Disclosures About Market Risk\nWe did not have any outstanding debt as of January 31, 2015.\n52\n'
    r = td.read_cell(split, dict(data_point='total_debt', period_end='2015-01-31'))
    assert r['locator'] == 'Item 7A. Quantitative and Qualitative Disclosures About Market Risk, p. 52'
    other = 'Item 7A. Market risk\nWe did not have any outstanding debt other than finance leases as of January 31, 2015.\n'
    assert td.read_cell(other, dict(data_point='total_debt', period_end='2015-01-31'))['decision'] == 'open'
    ba = 'Item 5. Market\nAs a result, we did not pay any dividends in 2023, 2022 and 2021.\n'
    assert td.read_cell(ba, dict(data_point='dividends_paid', period_end='2023-12-31'))['value_source'] == 'stated_zero'
    assert td.read_cell(ba, dict(data_point='dividends_paid', period_end='2024-12-31'))['decision'] == 'open'   # 2024 is not named
    silent = 'Item 7. MD&A\nWe manage liquidity carefully in fiscal 2015.\n'
    assert td.read_cell(silent, dict(data_point='total_debt', period_end='2015-01-31'))['decision'] == 'open'


def test_fsn_dropped_facts_missing_path_fails_loudly(tmp_path):
    import pytest, standard_inputs
    with pytest.raises(FileNotFoundError):
        standard_inputs.fsn_dropped_facts(str(tmp_path / 'nope.csv'), {}, {})


def test_ci_parent_derived_from_total_and_nci_lines_of_the_ci_statement():
    # Ritwik draw 2026-11-16, BA FY2015: CI prints 'Comprehensive income, net of tax' 6,328 and NCI -3, no parent line -> 6,331
    a = 'BA15'
    cl = {a: 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|4|22|Comprehensive income, net of tax~'
             'ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|4|21|Comprehensive (loss)/income related to noncontrolling interests'}
    nf = {a: 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest|4|6328000000~ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|4|-3000000'}
    rows = [dict(accession=a, data_point='comprehensive_income', status='combined', value=None, tags='', nodes='', why='', flags='ci_incl_nci', column='own')]
    resolve_all.apply_ci_parent(rows, cl, nf)
    r = rows[0]
    assert r['status'] == 'derived' and r['value'] == D(6331000000) and 'ci_parent_derived' in r['flags'] and 'ci_incl_nci' not in r['flags']
    assert r['nodes'].startswith('ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest=6328000000 [R4.htm:22]; -ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest=-3000000')
    only_total = [dict(rows[0], status='combined', value=None, flags='ci_incl_nci')]
    resolve_all.apply_ci_parent(only_total, {a: cl[a].split('~')[0]}, nf)
    assert only_total[0]['status'] == 'combined'                                  # no NCI line printed: stays the point reason


def test_equity_statement_dps_dash_is_a_printed_zero_unless_a_later_10k_prints_a_value():
    # BA FY2020 'Cash dividends declared, per share' 2019 8.22, 2020 -; MU FY2021 own dash but the FY2022 10-K prints 0.10 for FY2021
    import standard_inputs
    rows = [dict(accession='BA20', data_point='dividends_per_share', status='not_presented')]
    z = {'BA20': 'CommonStockDividendsPerShareDeclared|EQ|6|35|Cash dividends declared, per share'}
    roles = {'dividends_per_share': ('NOTE', ['CommonStockDividendsPerShareDeclared'])}
    pz = standard_inputs.printed_zero(rows, z, roles)
    assert pz[('BA20', 'dividends_per_share')]['stmt'] == 'EQ'
    assert standard_inputs.printed_zero(rows, {'BA20': 'CommonStockDividendsPerShareDeclared|EQ|6|35|x'}, {'dividends_per_share': ('IS', ['CommonStockDividendsPerShareDeclared'])}) == {}
    old = dict(resolve_all.EXT)
    try:
        resolve_all.EXT.clear()
        resolve_all.EXT.update(pz={('BA20', 'dividends_per_share'): pz[('BA20', 'dividends_per_share')], ('MU21', 'dividends_per_share'): dict(pz[('BA20', 'dividends_per_share')])},
                               cf={('MU21', 'dividends_per_share'): dict(tag='CommonStockDividendsPerShareDeclared', value='0.10', accession='MU22')})
        rs = [dict(accession='BA20', data_point='dividends_per_share', status='not_presented', flags='', ticker='BA'),
              dict(accession='MU21', data_point='dividends_per_share', status='not_presented', flags='', ticker='MU')]
        resolve_all.fill_printed_zero_and_comparative(rs, {})
    finally:
        resolve_all.EXT.clear(); resolve_all.EXT.update(old)
    assert rs[0]['value'] == D(0) and 'printed_zero' in rs[0]['flags']
    assert rs[1]['value'] == D('0.10') and rs[1]['column'] == 'comparative'


def test_per_share_scale_error_is_divided_and_flagged():
    # STX FY2024 10-K stores DPS 2,800,000 (own) and 2,770,000 (FY2022 column) for the printed $2.80 / $2.77
    import standard_inputs
    filings = [dict(a=f'S{y}', cik='1137789', p=f'{y}-06-30', lines='') for y in (2021, 2022, 2023, 2024)]
    notes = {'S2021': 'CommonStockDividendsPerShareDeclared|4|2.66', 'S2022': 'CommonStockDividendsPerShareDeclared|4|2.77',
             'S2023': 'CommonStockDividendsPerShareDeclared|4|2.80', 'S2024': 'CommonStockDividendsPerShareDeclared|4|2800000'}
    comp = {'S2024': 'CommonStockDividendsPerShareDeclared|4|2770000|2022-06-30~EarningsPerShareBasic|4|1.5|2023-06-30'}
    fixed = standard_inputs.per_share_scale_errors(filings, notes, comp)
    assert notes['S2024'] == 'CommonStockDividendsPerShareDeclared|4|2.8' and comp['S2024'].startswith('CommonStockDividendsPerShareDeclared|4|2.77|2022-06-30')
    assert fixed[('S2024', 'CommonStockDividendsPerShareDeclared', '2022-06-30')] == (D(2770000), D('2.77'))
    assert notes['S2021'].endswith('|2.66') and 'EarningsPerShareBasic|4|1.5' in comp['S2024']     # in-range values untouched
    rows = [dict(accession='S2024', period_end='2022-06-30', data_point='dividends_per_share', status='mapped', value=D('2.77'),
                 nodes='CommonStockDividendsPerShareDeclared=2.77 [NOTE]', flags='roles', why='w')]
    resolve_all.apply_scale_flags(rows, fixed)
    assert rows[0]['flags'] == 'roles;filer_scale_error' and '2770000' in rows[0]['why']


def test_combined_other_income_yields_to_the_later_10k_labelled_line():
    # MO FY2014: own band has only the mixed interest line (combined); the FY2015 10-K prints 'Other income, net' 0 for 2014
    import standard_inputs
    rows = [dict(cik='1', accession='M14', period_end='2014-12-31', data_point='other_income_expense_net', status='combined', tags='InterestIncomeExpenseNet', nodes='', value=None),
            dict(cik='1', accession='M15', period_end='2015-12-31', data_point='other_income_expense_net', status='mapped', tags='OtherNonoperatingIncomeExpense',
                 nodes='OtherNonoperatingIncomeExpense=5000000 [R4.htm:12]', value=D(5000000))]
    comp = {'M15': 'OtherNonoperatingIncomeExpense|4|0|2014-12-31'}
    out = standard_inputs.comparative_fill(rows, comp, set())
    assert out[('M14', 'other_income_expense_net')]['value'] == '0' and out[('M14', 'other_income_expense_net')]['accession'] == 'M15'
    rows[1]['tags'] = 'NonoperatingIncomeExpense'; rows[1]['nodes'] = 'NonoperatingIncomeExpense=5 [R4.htm:12]'
    comp = {'M15': 'NonoperatingIncomeExpense|4|0|2014-12-31'}
    assert ('M14', 'other_income_expense_net') not in standard_inputs.comparative_fill(rows, comp, set())   # only the pure labelled element


def test_suspended_dividend_and_program_buyback_statements_are_year_zeros():
    # Dhairya rulings 2026-11-16 (BA): suspension stated in the own 10-K -> dividends paid and DPS 0; the annual open-market program
    # statement naming the year -> buybacks 0; the Item 5 fourth-quarter table footnote (no year) never fills the year
    import text_disclosure as td
    rc = lambda t, dp, pe: td.read_cell(t, dict(data_point=dp, period_end=pe))
    susp = 'Item 7. MD&A\nOur dividend to common shareholders has been suspended since 2020.\n'
    assert rc(susp, 'dividends_paid', '2025-12-31')['value_source'] == 'stated_zero'
    assert rc(susp, 'dividends_per_share', '2025-12-31')['value_source'] == 'stated_zero'
    assert rc('Item 7. MD&A\nOur dividend remained suspended through 2021 and was reinstated in 2022.\n', 'dividends_paid', '2025-12-31')['decision'] == 'open'
    pay = 'Item 7. MD&A\nAs a result, we did not pay any dividends in 2023, 2022 and 2021.\n'
    assert rc(pay, 'dividends_per_share', '2023-12-31')['value'] == '0'
    assert rc(pay, 'dividends_per_share', '2024-12-31')['decision'] == 'open'
    annual = 'Item 7. MD&A\nDuring the years ended December 31, 2022, 2021 and 2020, we did not repurchase any shares through our open market share repurchase program.\n'
    assert rc(annual, 'share_buybacks', '2022-12-31')['value_source'] == 'stated_zero'
    q4 = 'Item 5. Market\nWe did not purchase any shares of our common stock in the open market pursuant to a repurchase program.\n'
    assert rc(q4, 'share_buybacks', '2023-12-31')['decision'] == 'open'


def test_stated_value_from_the_latest_later_10k_that_names_the_year(tmp_path):
    # Dhairya 2026-11-16: BA DPS FY2022 has no own-filing statement; the FY2023 and FY2024 10-Ks name 2022 -> the latest wins,
    # its accession is recorded, quote_period stays the cell's period end; an EARLIER filing never fills a later year
    p = tmp_path / 't.csv'
    p.write_text('cik,ticker,data_point,period_end,accession,own,decision,value_source,value,section,locator,quote_period,quote,why\n'
                 '12927,BA,dividends_per_share,2022-12-31,0000012927-24-000010,0,mapped,stated_zero,0,item7,"Item 7, p. 40",2022-12-31,"in 2023, 2022 and 2021",x\n'
                 '12927,BA,dividends_per_share,2022-12-31,0000012927-25-000015,0,mapped,stated_zero,0,item7,"Item 7, p. 41",2022-12-31,"in 2024, 2023 and 2022",x\n'
                 '12927,BA,dividends_per_share,2023-12-31,0000012927-23-000007,0,mapped,stated_zero,0,item7,"Item 7, p. 39",2023-12-31,"q",x\n')
    rows = [dict(cik='12927', data_point='dividends_per_share', period_end='2022-12-31', accession='0000012927-23-000007', status='not_presented', value=None, flags='roles', why=''),
            dict(cik='12927', data_point='dividends_per_share', period_end='2023-12-31', accession='0000012927-24-000010', status='not_presented', value=None, flags='roles', why='')]
    resolve_all.apply_text_disclosures(rows, str(p))
    r = rows[0]
    assert (r['status'], r['value'], r['accession'], r['column'], r['quote_period']) == ('mapped', D(0), '0000012927-25-000015', 'comparative', '2022-12-31')
    assert r['flags'] == 'stated_zero;stated_in_later_filing' and r['locator'] == 'Item 7, p. 41'
    assert rows[1]['status'] == 'not_presented'          # the FY2022 10-K (earlier) never speaks for FY2023


def test_stated_zero_keeps_the_excluded_preferred_line_in_its_reason(tmp_path):
    # BA FY2025: the CF prints only 'Dividends paid on Mandatory convertible preferred stock' 331 (excluded); the 10-K states the
    # common dividend has been suspended since 2020 -> stated_zero, flag and reason keep the excluded line
    p = tmp_path / 't.csv'
    p.write_text('cik,ticker,data_point,period_end,accession,own,decision,value_source,value,section,locator,quote_period,quote,why\n'
                 '12927,BA,dividends_paid,2025-12-31,0001628280-26-004357,1,mapped,stated_zero,0,item7,"Item 7, p. 38",2025-12-31,"Our dividend to common shareholders has been suspended since 2020.",x\n')
    rows = [dict(cik='12927', data_point='dividends_paid', period_end='2025-12-31', accession='0001628280-26-004357', status='not_presented', value=None,
                 flags='dividends_preferred_only', nodes='PaymentsOfDividends=331000000 [R8.htm:45]',
                 why="the financing dividend line 'Dividends paid on Mandatory convertible preferred stock' is preferred dividends; no common dividend line")]
    resolve_all.apply_text_disclosures(rows, str(p))
    r = rows[0]
    assert (r['status'], r['value'], r['nodes']) == ('mapped', D(0), '') and r['flags'] == 'stated_zero;dividends_preferred_only'
    assert "excluded: the financing dividend line 'Dividends paid on Mandatory convertible preferred stock'" in r['why']


def test_later_filing_reader_needs_the_year_named():
    import text_disclosure as td
    susp = 'Item 7. MD&A\nOur dividend to common shareholders has been suspended since 2020.\n'
    assert td.read_cell(susp, dict(data_point='dividends_per_share', period_end='2022-12-31', own='0'))['decision'] == 'open'
    named = 'Item 7. MD&A\nAs a result, we did not pay any dividends in 2023, 2022 and 2021.\n'
    assert td.read_cell(named, dict(data_point='dividends_per_share', period_end='2022-12-31', own='0'))['value'] == '0'


def test_table_line_amount_needs_year_header_and_scale_and_future_schedules_never_count():
    # ETN FY2024 MD&A: '(In millions ...) 2024 2023 2022' / 'Intangible asset amortization expense $ 425 $ 450 $ 499' -> 425,000,000
    # (equals ETN's CorporateNonSegment fact); a table whose first year is not the cell's, or with no scale, stays open
    import text_disclosure as td
    rc = lambda t, pe, own='1': td.read_cell(t, dict(data_point='amortization_of_intangibles', period_end=pe, own=own))
    etn = 'Item 7. MD&A\nIntangible asset amortization expense is as follows:\n(In millions except for per share data) 2024 2023 2022\nIntangible asset amortization expense $ 425 $ 450 $ 499\n'
    r = rc(etn, '2024-12-31')
    assert r['value'] == '425000000' and r['value_source'] == 'text_stated' and r['quote'].endswith('$ 425 $ 450 $ 499')
    assert rc(etn, '2023-12-31')['decision'] == 'open'                  # 2023 is not the first column
    assert rc(etn, '2024-12-31', own='0')['decision'] == 'open'         # table lines: own filing only
    assert rc(etn.replace('(In millions except for per share data) ', ''), '2024-12-31')['decision'] == 'open'   # no scale
    future = 'Item 8. Notes\nEstimated amortization expense of intangible assets is $ 400 million in 2025.\n'
    assert rc(future, '2025-12-31')['decision'] == 'open'
    said = 'Item 8. Notes\nAmortization expense of intangible assets was $ 425 million in 2024.\n'
    assert rc(said, '2024-12-31')['value'] == '425000000'


def test_sbc_reported_only_by_award_type_is_summed_or_kept_open_never_absent():
    # MO FY2019: AllocatedShareBasedCompensationExpense PerformanceShares 4 + RestrictedAndDeferredStock 28 = 32 (note text states both);
    # VZ: one member (RSU and PSU) -> open, flag reported_by_award_type, not hideable; overlapping members are never summed
    mf = {'MO19': 'AllocatedShareBasedCompensationExpense|4|4000000|AwardType=PerformanceShares;~AllocatedShareBasedCompensationExpense|4|28000000|AwardType=RestrictedAndDeferredStock;',
          'VZ19': 'ShareBasedCompensation|4|872000000|AwardType=RestrictedStockUnitsAndPerformanceStockUnits;',
          'X19': 'ShareBasedCompensation|4|10|AwardType=RestrictedStock;~ShareBasedCompensation|4|30|AwardType=RestrictedStockAndPerformanceShares;'}
    rows = [dict(accession=a, data_point='sbc', status='not_presented', value=None, flags='cf_family;never_reported', why='w', column='own') for a in ('MO19', 'VZ19', 'X19')]
    resolve_all.apply_sbc_award_members(rows, mf)
    mo, vz, x = rows
    assert mo['status'] == 'component_sum' and mo['value'] == D(32000000) and 'award_type_member_sum' in mo['flags']
    assert mo['nodes'].startswith('AllocatedShareBasedCompensationExpense[AwardType=PerformanceShares]=4000000 [NOTE]')
    assert vz['status'] == 'not_presented' and 'reported_by_award_type' in vz['flags'] and 'never_reported' not in vz['flags']
    assert x['status'] == 'not_presented' and 'reported_by_award_type' in x['flags']      # overlapping member names: not summed


def test_sbc_reported_by_award_type_is_never_flagged_absent():
    filings = [dict(a='VZ19', cik='1', p='2019-12-31', lines=''), dict(a='Z19', cik='2', p='2019-12-31', lines='')]
    rows = [dict(cik='1', accession='VZ19', data_point='sbc', period_end='2019-12-31', status='not_presented', value=None, flags='cf_family;reported_by_award_type', why='w', column='own'),
            dict(cik='2', accession='Z19', data_point='sbc', period_end='2019-12-31', status='not_presented', value=None, flags='cf_family', why='w', column='own')]
    resolve_all.apply_absent_in_own_filing(rows, filings, {}, {})
    assert 'absent_in_own_filing' not in rows[0]['flags'] and 'absent_in_own_filing' in rows[1]['flags']


def test_a_single_award_type_member_is_never_the_consolidated_value():
    import standard_inputs
    out = standard_inputs.member_facts({}, {'VZ19': 'ShareBasedCompensation|4|872000000|AwardType=RestrictedStockUnitsAndPerformanceStockUnits;'})
    assert out == []
