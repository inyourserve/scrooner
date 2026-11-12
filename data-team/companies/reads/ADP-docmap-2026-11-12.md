# ADP document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000008670-26-000030 (CIK 0000008670, filed 2026-08-05, FY ended 2026-06-30). Statement pages: BS R6.htm, BSP R7.htm, CF R10.htm, CI R5.htm, COVER R1.htm, EQ R8.htm, EQP R9.htm, IS R3.htm, ISP R4.htm.
- Era 10-K for interest_expense (InterestExpenseOperating, FY2024): 0000008670-24-000024: IS R3.htm 'Interest expense' printed 361400000 API 361400000 match Y.
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R3.htm | Revenues | 21947400000 | 21947400000 | 20560900000 | 20560900000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | TOTAL COSTS OF REVENUES | 11760200000 | 11760200000 | 11097300000 | 11097300000 | Y | FILING-CHECKED |  |
| gross_profit | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, general, and administrative expenses | 4408200000 | 4408200000 | 4051700000 | 4051700000 | Y | FILING-CHECKED |  |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R3.htm | Research and development | 1028800000 | 1028800000 | 988600000 | 988600000 | Y | FILING-CHECKED |  |
| operating_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpense | IS R3.htm | Interest expense | 459300000 | 459300000 | 455900000 | 455900000 | Y | FILING-CHECKED |  |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R3.htm | Other (income)/expense, net | -410600000 | 410600000 | -354100000 | 354100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | EARNINGS BEFORE INCOME TAXES | 5730300000 | 5730300000 | 5310100000 | 5310100000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Provision for income taxes | 1316800000 | 1316800000 | 1230400000 | 1230400000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | NET EARNINGS | 4413500000 | 4413500000 | 4079700000 | 4079700000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | BASIC EARNINGS PER SHARE (in dollars per share) | 10.97 | 10.97 | 10.02 | 10.02 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | DILUTED EARNINGS PER SHARE (in dollars per share) | 10.94 | 10.94 | 9.98 | 9.98 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic weighted average shares outstanding (in shares) | 402300000 | 402300000 | 407100000 | 407100000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted weighted average shares outstanding (in shares) | 403300000 | 403300000 | 408700000 | 408700000 | Y | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | EQP R9.htm | Dividends (in dollars per share) | 6.64 | 6.64 | 6.02 | 6.02 | Y | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R5.htm | Comprehensive income | 4394800000 | 4394800000 | 5004600000 | 5004600000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R6.htm | Cash and cash equivalents | 4.2301e+09 | 4230100000 | 3347800000 | 3347800000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R6.htm | Accounts receivable, net of allowance for doubtful accounts  | 3521100000 | 3521100000 | 3579100000 | 3579100000 | Y | FILING-CHECKED |  |
| inventory | not_presented |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R6.htm | Total current assets | 52561100000 | 52561100000 | 43252200000 | 43252200000 | Y | FILING-CHECKED |  |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R6.htm | Property, plant and equipment, net | 641300000 | 641300000 | 655400000 | 655400000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R6.htm | Goodwill | 3284400000 | 3284400000 | 3273500000 | 3273500000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R6.htm | Total assets | 63193300000 | 63193300000 | 53369300000 | 53369300000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R6.htm | Accounts payable | 162500000 | 162500000 | 169100000 | 169100000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R6.htm | Total current liabilities | 50024900000 | 50024900000 | 41278300000 | 41278300000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R6.htm | Total liabilities | 57162100000 | 57162100000 | 47181300000 | 47181300000 | Y | FILING-CHECKED |  |
| total_debt | component sum | CommercialPaper+LongTermDebtNoncurrent | BS R6.htm | Obligations under commercial paper borrowings + Long-term de | 4964100000 | 4964100000 | 8744200000 | 8744200000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R6.htm | Total stockholders’ equity | 6031200000 | 6031200000 | 6188000000 | 6188000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 397262737 | 397262737 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R10.htm | Net cash flows provided by operating activities | 5441200000 | 5441200000 | 4939700000 | 4939700000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R10.htm | Net cash flows used in investing activities | -4713800000 | -4713800000 | -3035000000 | -3035000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R10.htm | Net cash flows provided by/(used in) financing activities | 4881000000 | 4881000000 | -6973400000 | -6973400000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquireOtherPropertyPlantAndEquipment | CF R10.htm | Capital expenditures | -196600000 | 196600000 | -168700000 | 168700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R10.htm | Depreciation and amortization | 585900000 | 585900000 | 582400000 | 582400000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R10.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R10.htm | Stock-based compensation expense | 242600000 | 242600000 | 2.661e+08 | 266100000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividends | CF R10.htm | Dividends paid | -2626300000 | 2626300000 | -2398900000 | 2398900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R10.htm | Repurchases of common stock | -2.0833e+09 | 2083300000 | -1280500000 | 1280500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ar_change | not_presented |  | CF R10.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_inventory_change | not_presented |  | CF R10.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayableTrade | CF R10.htm | Increase/(decrease) in accounts payable | -4500000 | -4500000 | 60600000 | 60600000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R10.htm | Cash paid for interest | 439600000 | 439600000 | 426800000 | 426800000 | Y | FILING-CHECKED |  |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R10.htm | Cash paid for income taxes, net of income tax refunds | 1006700000 | 1006700000 | 1198000000 | 1198000000 | Y | FILING-CHECKED |  |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2022, 2023, 2025, 2026]; ERA-CHECK others: {'InterestExpenseOperating': [2024]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- none

## Mismatches (printed vs API)
- none beyond sign differences
