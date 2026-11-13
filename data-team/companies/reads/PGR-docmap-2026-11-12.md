# PGR document-first map, 2026-11-12 (read-only, built bottom-up from the 10-K)

Latest 10-K: accession 0000080661-26-000086, period end 2025-12-31. Evidence: R pages of FilingSummary (face statements + notes opened: R1.htm, R3.htm, R4.htm, R5.htm, R6.htm, R7.htm, R8.htm, R45.htm, R46.htm, R47.htm, R49.htm, R68.htm, R72.htm, R75.htm, R76.htm, R77.htm, R78.htm, R95.htm, R96.htm, R98.htm, R99.htm, R105.htm), values compared with data.sec.gov companyfacts (undimensioned, same accession). Values below are scaled to full units (USD, shares, USD/share). match = printed vs API; Y(abs) = same magnitude, sign differs (expense/outflow printed negative, tag positive).  Custom (company-prefix) tags are not in companyfacts: match NA.

Insurer (P&C) template. Face statements: R3 'Consolidated Statements of Comprehensive Income' (one report: income, EPS and OCI; FSN stmt=CI), R4 balance sheet, R7 cash flows, R8 changes in shareholders' equity. FY0 = FY2025.

| data_point | status | tags | page | label | fy0 printed | fy0 api | fy1 printed | fy1 api | match | note |
|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | R3.htm | Total revenues | 87671000000 | 87671000000 | 75372000000 | 75372000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cost_of_revenue | OUT |  |  |  |  |  |  |  |  | insurer template OUT: IS prints premiums, investment income, realized gains, fees; losses and LAE, policy acquisition costs, other underwriting expenses; no cost-of-revenue line |
| gross_profit | OUT |  |  |  |  |  |  |  |  | insurer template OUT: no gross profit line |
| operating_expenses | mapped | BenefitsLossesAndExpenses | R3.htm | Total expenses | 73448000000 | 73448000000 | 64659000000 | 64659000000 | Y/Y | candidate: printed 'Total expenses' (includes losses, acquisition costs, interest); insurer COND row / fy0=2025-12-31 fy1=2024-12-31 |
| sga_expense | not_presented |  |  |  |  |  |  |  |  | no SG&A or G&A line; 'Other underwriting expenses' (OtherUnderwritingExpense 11,329) is the insurer's own expense line |
| research_and_development | OUT |  |  |  |  |  |  |  |  | insurer template OUT; no R&D line |
| operating_income | OUT |  |  |  |  |  |  |  |  | insurer template OUT: no operating income subtotal (Total revenues - Total expenses -> Income before income taxes) |
| interest_expense | mapped | InterestExpenseDebt | R3.htm | Interest expense | 278000000 | 278000000 | 279000000 | 279000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| interest_income | not_presented |  |  |  |  |  |  |  |  | no interest income line; 'Investment income' (InterestAndDividendIncomeOperating 3,583) is the insurer's investment-income line (interest + dividends), a different concept |
| other_income_expense_net | not_presented |  |  |  |  |  |  |  |  | no non-operating other income line on the IS |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 14223000000 | 14223000000 | 10713000000 | 10713000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 2915000000 | 2915000000 | 2233000000 | 2233000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| net_income | mapped | NetIncomeLoss | R3.htm | Net income | 11308000000 | 11308000000 | 8480000000 | 8480000000 | Y/Y | 'Net income' 11,308 (no NCI); 'Net income available to common shareholders' (NetIncomeLossAvailableToCommonStockholdersBasic) is the EPS numerator, equal in FY2025, differs FY2024 by preferred dividends 17 / fy0=2025-12-31 fy1=202 |
| basic_eps | mapped | EarningsPerShareBasic | R3.htm | Basic: Earnings per common share (usd per share) | 19.29 | 19.29 | 14.45 | 14.45 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | R3.htm | Diluted: Earnings per common share (usd per share) | 19.23 | 19.23 | 14.4 | 14.4 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Average common shares outstanding – Basic | 586300000 | 586300000 | 585500000 | 585500000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Total average equivalent common shares – Diluted | 588100000 | 588100000 | 587700000 | 587700000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | R8.htm | Common shares, dividends declared (USD per share) | 13.9 | 13.9 | 4.9 | 4.9 | Y/Y | equity statement R8 (dividends declared per share; PGR pays annual variable + quarterly dividends, see Dividends note R105) / fy0=2025-12-31 fy1=2024-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R3.htm | Comprehensive income (loss) | 12834000000 | 12834000000 | 8673000000 | 8673000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_and_equivalents | mapped | Cash | R4.htm | Cash and cash equivalents | 125000000 | 125000000 | 143000000 | 143000000 | Y/Y | BS face 'Cash and cash equivalents' 125 is tagged us-gaap:Cash (not CashAndCashEquivalentsAtCarryingValue); 'Restricted cash and cash equivalents' 13 and 'Total cash, cash equivalents, restricted cash...' 138 (= CF end cash) are s |
| accounts_receivable | not_presented |  |  |  |  |  |  |  |  | BS prints 'Premiums receivable, net of allowance' (PremiumsReceivableAtCarryingValue 15,362): premiums receivable, a different concept; no AR line |
| inventory | OUT |  |  |  |  |  |  |  |  | insurer template OUT |
| current_assets | OUT |  |  |  |  |  |  |  |  | unclassified BS: no current totals (R4 read) |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | R4.htm | Property and equipment, net of accumulated depreciation of $ | 783000000 | 783000000 | 790000000 | 790000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| goodwill | not_presented |  |  |  |  |  |  |  |  | no goodwill line on the BS; Goodwill tag absent from the filing per MetaLinks |
| total_assets | mapped | Assets | R4.htm | Total assets | 123039000000 | 123039000000 | 105745000000 | 105745000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| accounts_payable | combined | AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R4.htm | Accounts payable, accrued expenses, and other liabilities | 9318000000 | 9318000000 | 7651000000 | 7651000000 | Y/Y | 'Accounts payable, accrued expenses, and other liabilities' combined line (own label) / fy0=2025-12-31 fy1=2024-12-31 |
| current_liabilities | OUT |  |  |  |  |  |  |  |  | unclassified BS: no current totals (R4 read) |
| total_liabilities | mapped | Liabilities | R4.htm | Total liabilities | 92716000000 | 92716000000 | 80154000000 | 80154000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| total_debt | mapped | DebtLongtermAndShorttermCombinedAmount | R4.htm | Debt | 6897000000 | 6897000000 | 6893000000 | 6893000000 | Y/Y | BS prints one 'Debt' line (long- and short-term combined, 6,897); no separate current/long-term split / fy0=2025-12-31 fy1=2024-12-31 |
| stockholders_equity | mapped | StockholdersEquity | R4.htm | Total shareholders’ equity | 30323000000 | 30323000000 | 25591000000 | 25591000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| shares_outstanding | not_presented |  | BS R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand R5 prints issued 798,000,000 and treasury 212,000,000 only; no BS-date outstanding count printed; instants never summed; dei never used | 2026-11-12 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 17548000000 | 17548000000 | 15119000000 | 15119000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -14527000000 | -14527000000 | -13749000000 | -13749000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -3037000000 | -3037000000 | -1316000000 | -1316000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| capex | OUT | PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -348000000 | 348000000 | -285000000 | 285000000 | Y(abs)/Y(abs) | insurer template OUT by definition (capex/FCF family; approved category C) although the CF prints 'Purchases of property and equipment' (348): value shown for the record, not a template cell / fy0=2025-12-31 fy1=2024-12-31 |
| depreciation_and_amortization | mapped | Depreciation | R7.htm | Depreciation | 313000000 | 313000000 | 284000000 | 284000000 | Y/Y | CF 'Depreciation' 313 (PP&E depreciation only: perimeter label); no amortization-of-intangibles line / fy0=2025-12-31 fy1=2024-12-31 |
| amortization_of_intangibles | not_presented |  |  |  |  |  |  |  |  | no intangible-amortization line; AmortizationOfIntangibleAssets absent per MetaLinks |
| sbc | mapped | RestrictedStockExpense | R7.htm | Amortization of equity-based compensation | 132000000 | 132000000 | 122000000 | 122000000 | Y/Y | CF 'Amortization of equity-based compensation' 132 (tag RestrictedStockExpense) / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to common shareholders | -2871000000 | 2871000000 | -674000000 | 674000000 | Y(abs)/Y(abs) | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| share_buybacks | mapped | pgr:PaymentsforRepurchaseofCommonStockintheOpenMarket | R7.htm | Acquisition of treasury shares acquired in open market | -74000000 |  | -13000000 |  | NA/NA | 'Acquisition of treasury shares acquired in open market' (custom tag, case variant of earlier years); 'Acquisition of treasury shares for equity award tax withholding' 92 is excluded (founder 2026-11-04 item 4) / API MISSING: Paym |
| cf_ar_change | not_presented |  |  |  |  |  |  |  |  | CF 'Premiums receivable' (IncreaseDecreaseInPremiumsReceivable) is premiums, a different concept |
| cf_inventory_change | OUT |  |  |  |  |  |  |  |  | insurer template OUT |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | R7.htm | Accounts payable, accrued expenses, and other liabilities | 1556000000 | 1556000000 | 1236000000 | 1236000000 | Y/Y | 'Accounts payable, accrued expenses, and other liabilities' combined change (own label) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | R57.htm | Interest | 276000000 | 276000000 | 276000000 | 276000000 | Y/Y | Reporting and accounting policies note R57 (supplemental cash flow) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | R78.htm | Income taxes | 3107000000 | 3107000000 | 2585000000 | 2585000000 | Y/Y | Income Taxes Paid note R78 (ASU 2023-09) / fy0=2025-12-31 fy1=2024-12-31 |

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
No disagreement with the CSV rows for PGR. interest_expense = face 'Interest expense' (InterestExpenseDebt 278, agrees); buybacks = 'Acquisition of treasury shares acquired in open market' (custom tag, case variant PaymentsforRepurchaseofCommonStockintheOpenMarket in FY2025) and the tax-withholding purchases (92) are excluded (agrees); the percent-change column exclusion is not applicable to FY2025 R3. template_out_pending_read rows CONFIRMED OUT by the FY2025 10-K: cost_of_revenue, gross_profit, operating_income (R3 has none), current_assets and current_liabilities (R4 unclassified). The IS and the comprehensive-income statement are ONE report (R3). New finding: cash: PGR's face 'Cash and cash equivalents' is tagged us-gaap:Cash (125) with a separate 'Total cash, cash equivalents, restricted cash' 138.

## Era checks (older 10-K opened: tag on the same printed line?)
Older 10-K opened: 0000080661-23-000006 (period 2022-12-31); face pages ['R3.htm', 'R4.htm', 'R5.htm', 'R6.htm', 'R7.htm', 'R8.htm']. Result: 30 mapped rows checked.
- cash_paid_for_income_taxes: tag us-gaap:IncomeTaxesPaidNet ABSENT from the old filing 0000080661-23-000006 (2022-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read)
- (29 rows: same tag and same label on the older 10-K, no change)

## Mismatches / unresolved
- none

## Method and untested scope
- FILING-CHECKED = value read from the 10-K R page (MetaLinks used to locate tags/pages) and compared with companyfacts for the same accession; not_presented/OUT rows are FILING-CHECKED for the statements opened (all face statements plus the note pages that carry the candidate tags per MetaLinks); a note not opened could still hold an unprinted detail.
- Era check: one older 10-K per company (statement pages only, via MetaLinks); same-tag / label comparison on the same statement type. Note-page values of the older filing were not opened.
- Not covered: 10-Q-era tag history, quarterly values, segment-level data points, FSN store comparison (document-first read only).
## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)
- shares_outstanding: mapped dei:EntityCommonStockSharesOutstanding -> not_presented  | shares_outstanding = BS-date count, never dei (Dhairya ruling 2026-11-12)
- shares_outstanding: check: hand -> not_presented | check: hand R5 prints issued 798,000,000 and treasury 212,000,000 only; no BS-date outstanding count printed; instants never summed; dei nev
- 17 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
