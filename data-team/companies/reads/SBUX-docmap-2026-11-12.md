# SBUX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000829224-25-000114 (CIK 0000829224, filed 2025-11-14): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R7.htm, BSP R8.htm
- 10-K 0000829224-15-000038 (CIK 0000829224, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000829224-17-000049 (CIK 0000829224, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000829224-21-000086 (CIK 0000829224, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, CF R4.htm, BS R6.htm, BSP R7.htm
- companyfacts CIK0000829224.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenues | 37184400000 | 37184400000 | 36176200000 | 36176200000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1149 tags across all 96 R pages, face and notes) of 0000829224-25-000114; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1149 tags across all 96 R pages, face and notes) of 0000829224-25-000114; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 34495600000 | 34495600000 | 31068600000 | 31068600000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative expenses | 2617200000 | 2617200000 | 2523300000 | 2523300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1149 tags across all 96 R pages, face and notes) of 0000829224-25-000114; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 2936600000 | 2936600000 | 5408800000 | 5408800000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | -542600000 | 542600000 | -562000000 | 562000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before income taxes | 2507300000 | 2507300000 | 4969600000 | 4969600000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 650600000 | 650600000 | 1207300000 | 1207300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings attributable to Starbucks | 1856400000 | 1856400000 | 3760900000 | 3760900000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings Per Share, Basic | 1.63 | 1.63 | 3.32 | 3.32 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings/(loss) Per Share, Diluted | 1.63 | 1.63 | 3.31 | 3.31 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic | 1136000000 | 1136000000 | 1133800000 | 1133800000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted | 1139800000 | 1139800000 | 1137300000 | 1137300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R3.htm period ..2025-09-28 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R7.htm | Cash, Cash Equivalent, Restricted Cash, and Restricted Cash Equivalent, Continuing Operation | 3219800000 | 3219800000 | 3286200000 | 3286200000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R7.htm | Accounts Receivable, net | 1277500000 | 1277500000 | 1213800000 | 1213800000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| inventory | mapped | us-gaap:InventoryNet | R7.htm | Inventory, Net | 2185600000 | 2185600000 | 1777300000 | 1777300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| current_assets | mapped | us-gaap:AssetsCurrent | R7.htm | Assets, Current | 7382300000 | 7382300000 | 6847400000 | 6847400000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R7.htm | Property, Plant and Equipment, Net | 8493500000 | 8493500000 | 8665500000 | 8665500000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| goodwill | mapped | us-gaap:Goodwill | R7.htm | Goodwill | 3368900000 | 3368900000 | 3315700000 | 3315700000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| total_assets | mapped | us-gaap:Assets | R7.htm | Assets | 32019700000 | 32019700000 | 31339300000 | 31339300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R7.htm | Accounts Payable, Current | 1852800000 | 1852800000 | 1595500000 | 1595500000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R7.htm | Liabilities, Current | 10210400000 | 10210400000 | 9070000000 | 9070000000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| total_liabilities | mapped | us-gaap:Liabilities | R7.htm | Liabilities | 40108900000 | 40108900000 | 38780900000 | 38780900000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R7.htm | Stockholders' Equity/(Deficit) Attributable to Parent | -8096600000 | -8096600000 | -7448900000 | -7448900000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R7.htm period ..2025-09-28 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R5.htm | Cash Provided by (Used in) Operating Activity, Including Discontinued Operation | 4747500000 | 4747500000 | 6095600000 | 6095600000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used by investing activities | -2485400000 | -2485400000 | -2699200000 | -2699200000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash used by financing activities | -2298000000 | -2298000000 | -3718200000 | -3718200000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R5.htm | Additions to property, plant and equipment | -2305500000 | 2305500000 | -2777500000 | 2777500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R5.htm | Depreciation and amortization | 1771500000 | 1771500000 | 1592400000 | 1592400000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Stock-based compensation | 318300000 | 318300000 | 308300000 | 308300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R5.htm | Cash dividends paid | -2771400000 | 2771400000 | -2585000000 | 2585000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R5.htm | Repurchase of common stock | 0 | 0 | -1266700000 | 1266700000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R5.htm | Interest, net of capitalized interest | 588300000 | 588300000 | 570700000 | 570700000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R5.htm | Income taxes, net of refunds | 715600000 | 715600000 | 1373300000 | 1373300000 | Y | FILING-CHECKED | accn 0000829224-25-000114 R5.htm period ..2025-09-28 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R7.htm | Long-term Debt, Current Maturities + Long-term Debt, Excluding Current Maturities | 16074800000 | 16074800000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common Stock, Shares, Outstanding | 1136900000 | 1136900000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-09-28; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Total net revenues' on us-gaap:SalesRevenueNet = 19162700000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 15811600000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000829224-15-000038 R2.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 1196700000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Operating income/(loss)' on us-gaap:OperatingIncomeLoss = 3601000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -70500000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Earnings/(loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 3903000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Income tax expense/(benefit)' on us-gaap:IncomeTaxExpenseBenefit = 1143700000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Net earnings attributable to Starbucks' on us-gaap:NetIncomeLoss = 2757400000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Earnings per share - basic' on us-gaap:EarningsPerShareBasic = 1.84 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Earnings per share - diluted' on us-gaap:EarningsPerShareDiluted = 1.82 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 1495900000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000829224-15-000038 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 1513400000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1530100000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 719000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 1306400000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4352700000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 4088300000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1575400000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000829224-15-000038 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 12446100000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 684200000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 3653500000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 6626300000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000829224-15-000038 R4.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 5818000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 3749100000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Net cash used by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1520300000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Net cash used by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2256500000 (FILING-CHECKED)
- capex: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Additions to property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1303700000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 933800000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 209800000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividends = -928600000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1436100000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Interest, net of capitalized interest' on us-gaap:InterestPaidNet = 69500000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000829224-15-000038 R6.htm prints 'Income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 1072200000 (FILING-CHECKED)
- revenue: era 10-K 0000829224-17-000049 R2.htm prints 'Total net revenues' on us-gaap:SalesRevenueNet = 22386800000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000829224-21-000086 R6.htm prints 'Cash and Cash Equivalents, at Carrying Value' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 6455700000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: review  (R3.htm): 2026-11-12 R3.htm: R3 prints 'Product and distribution costs' 11,658.2 (ProductionAndDistributionCosts) first among operating expenses, with no gross profit line: the same definition question as the EXPD call (map vs not
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: R3 prints no gross profit line; MetaLinks: GrossProfit absent
- operating_expenses: combined us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: R3 'Total operating expenses' 34,495.6 includes product and distribution costs: combined
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: no R&D line; MetaLinks: tags absent
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R7.htm): 2026-11-12 R7.htm: R7 prints current maturities 1,498.9 + long-term debt 14,575.9 = 16,074.8 = XBRL
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'Basic' is the weighted_basic_shares line, printed 1136000000 = filing XBRL 1136000000; agrees
- goodwill: mapped us-gaap:Goodwill (R7.htm): 2026-11-12 R7.htm: 10% mapped sample: BS R7.htm 'Goodwill' is the goodwill line, printed 3368900000 = filing XBRL 3368900000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R7.htm): 2026-11-12 R7.htm: 10% mapped sample: BS R7.htm 'Stockholders' Equity/(Deficit) Attributable to Par' is the stockholders_equity line, printed -8096600000 = filing XBRL -8096600000; agrees

## Gap 2026-11-13 (top-100 gap work)
- The latest 10-K on EDGAR is 0000829224-26-000162 (submissions, fetched 2026-11-13 by the sec-reads-fetch run 43368567998); this docmap reads 0000829224-25-000114 (FY2025). Every row here is one fiscal year behind until it is re-read on the new filing. The 8 data points the shared tool never emits are not added here for that reason.
