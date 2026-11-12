# CVS document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000064803-26-000010 (CIK 0000064803, filed 2026-02-10, FY ended 2025-12-31). Statement pages: BS R5.htm, BSP R6.htm, CF R7.htm, CI R4.htm, COVER R1.htm, EQ R8.htm, EQP R9.htm, IS R3.htm.
- Era 10-K for interest_expense (InterestExpense, FY2023): 0000064803-24-000007: IS R3.htm 'Interest expense' printed 2658000000 API 2658000000 match Y.
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | IS R3.htm | Total revenues | 402067000000 | 402067000000 | 372809000000 | 372809000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | Cost of products sold | 221167000000 | 221167000000 | 206287000000 | 206287000000 | Y | FILING-CHECKED |  |
| gross_profit | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 4660000000 | 4660000000 | 8516000000 | 8516000000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | -3119000000 | 3119000000 | -2958000000 | 2958000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R3.htm | Other income | 112000000 | 112000000 | 99000000 | 99000000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Income before income tax provision | 2136000000 | 2136000000 | 6148000000 | 6148000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income tax provision | 408000000 | 408000000 | 1562000000 | 1562000000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net income attributable to CVS Health | 1768000000 | 1768000000 | 4614000000 | 4614000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic (in dollars per share) | 1.4 | 1.4 | 3.67 | 3.67 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted (in dollars per share) | 1.39 | 1.39 | 3.66 | 3.66 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic (in shares) | 1267000000 | 1267000000 | 1259000000 | 1259000000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted (in shares) | 1271000000 | 1271000000 | 1262000000 | 1262000000 | Y | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | EQP R9.htm | Dividends declared per share (in dollars per share) | 2.66 | 2.66 | 2.66 | 2.66 | Y (printed column 4) | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive income attributable to CVS Health | 2294000000 | 2294000000 | 4791000000 | 4791000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and cash equivalents | 8453000000 | 8453000000 | 8586000000 | 8586000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R5.htm | Accounts receivable, net | 39779000000 | 39779000000 | 36469000000 | 36469000000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R5.htm | Inventories | 19246000000 | 19246000000 | 18107000000 | 18107000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total current assets | 74714000000 | 74714000000 | 68645000000 | 68645000000 | Y | FILING-CHECKED |  |
| ppe_net | combined | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | BS R5.htm | Property and equipment, net | 13083000000 | 13083000000 | 12993000000 | 12993000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill | 85478000000 | 85478000000 | 91272000000 | 91272000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R5.htm | Total assets | 253538000000 | 253538000000 | 253215000000 | 253215000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableTradeCurrent | BS R5.htm | Accounts payable | 17641000000 | 17641000000 | 15892000000 | 15892000000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total current liabilities | 88692000000 | 88692000000 | 84609000000 | 84609000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R5.htm | Total liabilities | 178156000000 | 178156000000 | 177485000000 | 177485000000 | Y | FILING-CHECKED |  |
| total_debt | component sum | ShortTermBorrowings+LongTermDebtAndCapitalLeaseObligationsCurrent+LongTermDebtAndCapitalLeaseObligations | BS R5.htm | Short-term debt + Current portion of long-term debt + Long-t | 64570000000 | 64570000000 | 66270000000 | 66270000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R5.htm | Total CVS Health shareholders’ equity | 75214000000 | 75214000000 | 75560000000 | 75560000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 1272211063 | 1272211063 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R7.htm | Net cash provided by operating activities | 10639000000 | 10639000000 | 9107000000 | 9107000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R7.htm | Net cash used in investing activities | -5871000000 | -5871000000 | -7613000000 | -7613000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R7.htm | Net cash provided by (used in) financing activities | -4940000000 | -4940000000 | -1135000000 | -1135000000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R7.htm | Purchases of property and equipment | -2832000000 | 2832000000 | -2781000000 | 2781000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R7.htm | Depreciation and amortization | 4606000000 | 4606000000 | 4597000000 | 4597000000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R7.htm | Stock-based compensation | 535000000 | 535000000 | 540000000 | 540000000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividends | CF R7.htm | Dividends paid | -3397000000 | 3397000000 | -3373000000 | 3373000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R7.htm | Repurchase of common stock | 0 | 0 | -3023000000 | 3023000000 | Y | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R7.htm | Accounts receivable, net | -3498000000 | 3498000000 | -1301000000 | 1301000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R7.htm | Inventories | -1267000000 | 1267000000 | -102000000 | 102000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R7.htm | Accounts payable and pharmacy claims and discounts payable | 3855000000 | 3855000000 | 2335000000 | 2335000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R7.htm | Interest paid | -2991000000 | 2991000000 | -2909000000 | 2909000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R7.htm | Income taxes paid | -2166000000 | 2166000000 | -1703000000 | 1703000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2024, 2025]; ERA-CHECK others: {'InterestExpense': [2021, 2022, 2023]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- none

## Mismatches (printed vs API)
- none beyond sign differences
