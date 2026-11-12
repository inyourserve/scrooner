# SBUX document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000829224-25-000114 (CIK 0000829224, filed 2025-11-14, FY ended 2025-09-28). Statement pages: BS R7.htm, BSP R8.htm, CF R5.htm, CI R4.htm, COVER R1.htm, EQ R6.htm, IS R3.htm.
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | IS R3.htm | Revenues | 37184400000 | 37184400000 | 36176200000 | 36176200000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | ProductionAndDistributionCosts | IS R3.htm | Product and distribution costs | 11658200000 | 11658200000 | 11180600000 | 11180600000 | Y | FILING-CHECKED | 'Product and distribution costs' 11,658.2 is the cost-of-goods line; no gross profit printed (same question as the EXPD definition call) |
| gross_profit | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 2936600000 | 2936600000 | 5408800000 | 5408800000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpense | IS R3.htm | Interest expense | -542600000 | 542600000 | -562000000 | 562000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Earnings before income taxes | 2507300000 | 2507300000 | 4969600000 | 4969600000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income tax expense | 650600000 | 650600000 | 1207300000 | 1207300000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net earnings attributable to Starbucks | 1856400000 | 1856400000 | 3760900000 | 3760900000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Earnings Per Share, Basic | 1.63 | 1.63 | 3.32 | 3.32 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Earnings/(loss) Per Share, Diluted | 1.63 | 1.63 | 3.31 | 3.31 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic | 1136000000 | 1136000000 | 1133800000 | 1133800000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted | 1139800000 | 1139800000 | 1137300000 | 1137300000 | Y | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | EQ R6.htm | Common Stock, Dividends, Per Share, Declared | 2.45 | 2.45 |  |  | Y | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive Income, Net of Tax, Attributable to Parent | 1826100000 | 1826100000 | 4.1099e+09 | 4109900000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | combined | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | BS R7.htm | Cash, Cash Equivalent, Restricted Cash, and Restricted Cash  | 3219800000 | 3219800000 | 3286200000 | 3286200000 | Y | FILING-CHECKED | label includes restricted cash (rule 9) |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R7.htm | Accounts Receivable, net | 1277500000 | 1277500000 | 1213800000 | 1213800000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R7.htm | Inventory, Net | 2185600000 | 2185600000 | 1777300000 | 1777300000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R7.htm | Assets, Current | 7382300000 | 7382300000 | 6847400000 | 6847400000 | Y | FILING-CHECKED |  |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R7.htm | Property, Plant and Equipment, Net | 8493500000 | 8493500000 | 8665500000 | 8665500000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R7.htm | Goodwill | 3368900000 | 3368900000 | 3315700000 | 3315700000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R7.htm | Assets | 32019700000 | 32019700000 | 31339300000 | 31339300000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R7.htm | Accounts Payable, Current | 1852800000 | 1852800000 | 1595500000 | 1595500000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R7.htm | Liabilities, Current | 10210400000 | 10210400000 | 9070000000 | 9070000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R7.htm | Liabilities | 40108900000 | 40108900000 | 38780900000 | 38780900000 | Y | FILING-CHECKED |  |
| total_debt | component sum | LongTermDebtCurrent+LongTermDebtNoncurrent | BS R7.htm | Long-term Debt, Current Maturities + Long-term Debt, Excludi | 16074800000 | 16074800000 | 15568400000 | 15568400000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R7.htm | Stockholders' Equity/(Deficit) Attributable to Parent | -8096600000 | -8096600000 | -7448900000 | -7448900000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 1137100000 | 1137100000 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R5.htm | Cash Provided by (Used in) Operating Activity, Including Dis | 4747500000 | 4747500000 | 6095600000 | 6095600000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R5.htm | Net cash used by investing activities | -2485400000 | -2485400000 | -2699200000 | -2699200000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R5.htm | Net cash used by financing activities | -2298000000 | -2298000000 | -3718200000 | -3718200000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R5.htm | Additions to property, plant and equipment | -2305500000 | 2305500000 | -2777500000 | 2777500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R5.htm | Depreciation and amortization | 1771500000 | 1771500000 | 1592400000 | 1592400000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R5.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R5.htm | Stock-based compensation | 318300000 | 318300000 | 308300000 | 308300000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividends | CF R5.htm | Cash dividends paid | -2771400000 | 2771400000 | -2585000000 | 2585000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R5.htm | Repurchase of common stock | 0 | 0 | -1266700000 | 1266700000 | Y | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R5.htm | Accounts receivable | -89700000 | 89700000 | 18400000 | -18400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R5.htm | Inventories | -408400000 | 408400000 | 42800000 | -42800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R5.htm | Accounts payable | 261000000 | 261000000 | 28000000 | 28000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R5.htm | Interest, net of capitalized interest | 588300000 | 588300000 | 570700000 | 570700000 | Y | FILING-CHECKED |  |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R5.htm | Income taxes, net of refunds | 715600000 | 715600000 | 1373300000 | 1373300000 | Y | FILING-CHECKED |  |

## Era checks (tag changes in the last ~5 years)
- none flagged

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- SBUX cost_of_revenue: file says (file)  (-); read says mapped us-gaap:ProductionAndDistributionCosts 'Product and distribution costs'. DECISION: FILE STANDS (map), pending the EXPD-type ruling

## Mismatches (printed vs API)
- none beyond sign differences
