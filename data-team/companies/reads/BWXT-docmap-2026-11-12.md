# BWXT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001486957-26-000007 (CIK 0001486957, filed 2026-02-23): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0001193125-16-475979 (CIK 0001486957, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001486957-18-000007 (CIK 0001486957, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001486957-24-000011 (CIK 0001486957, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- companyfacts CIK0001486957.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 3198425000 | 3198425000 | 2703654000 | 2703654000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of operations | 2465566000 | 2465566000 | 2048447000 | 2048447000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R66.htm | Equity Method Investments - Summary of Combined Income Statement Information (Detail) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R66.htm 'Equity Method Investments - Summary of Combined Income Statement Information (De' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total Costs and Expenses | 2868877000 | 2868877000 | 2378978000 | 2378978000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 394416000 | 394416000 | 318663000 | 318663000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development costs | 13867000 | 13867000 | 7478000 | 7478000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 404459000 | 404459000 | 380607000 | 380607000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -44207000 | 44207000 | -39475000 | 39475000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Total before tax | 398120000 | 398120000 | 348720000 | 348720000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for Income Taxes | 68259000 | 68259000 | 66422000 | 66422000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income Attributable to BWX Technologies, Inc. | 328945000 | 328945000 | 281941000 | 281941000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net Income Attributable to BWX Technologies, Inc. (USD per share) | 3.59 | 3.59 | 3.08 | 3.08 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net Income Attributable to BWX Technologies, Inc. (USD per share) | 3.58 | 3.58 | 3.07 | 3.07 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 91566280 | 91566280 | 91572674 | 91572674 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 91856013 | 91856013 | 91859732 | 91859732 | Y | FILING-CHECKED | accn 0001486957-26-000007 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 499779000 | 499779000 | 74109000 | 74109000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable – trade, net | 220391000 | 220391000 | 99112000 | 99112000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 46537000 | 46537000 | 40288000 | 40288000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total Current Assets | 1560354000 | 1560354000 | 929997000 | 929997000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, Plant and Equipment, Net | 1585136000 | 1585136000 | 1278161000 | 1278161000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 500860000 | 500860000 | 287362000 | 287362000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | TOTAL ASSETS | 4271495000 | 4271495000 | 2869924000 | 2869924000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 141289000 | 141289000 | 158077000 | 158077000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total Current Liabilities | 672017000 | 672017000 | 474201000 | 474201000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total Liabilities | 3038483000 | 3038483000 | 1789520000 | 1789520000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Stockholders' Equity – BWX Technologies, Inc. | 1232487000 | 1232487000 | 1080680000 | 1080680000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | NET CASH PROVIDED BY OPERATING ACTIVITIES | 479848000 | 479848000 | 408428000 | 408428000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | NET CASH USED IN INVESTING ACTIVITIES | -742109000 | -742109000 | -154561000 | -154561000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | NET CASH PROVIDED BY (USED IN) FINANCING ACTIVITIES | 693640000 | 693640000 | -252785000 | -252785000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Purchases of property, plant and equipment | -184557000 | 184557000 | -153647000 | 153647000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation and amortization | 109186000 | 109186000 | 85862000 | 85862000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation expense | 26072000 | 26072000 | 21680000 | 21680000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Dividends paid to common shareholders | -92467000 | 92467000 | -88349000 | 88349000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Repurchases of common stock | -30000000 | 30000000 | -20000000 | 20000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Interest | 65163000 | 65163000 | 72426000 | 72426000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R10.htm | Income taxes (net of refunds) | 47892000 | 47892000 | 45508000 | 45508000 | Y | FILING-CHECKED | accn 0001486957-26-000007 R10.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current maturities of long-term debt + Long-Term Debt | 2015983000 | 2015983000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001486957-26-000007; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Revenues' on us-gaap:Revenues = 1415529000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Cost of operations' on us-gaap:CostOfRevenue = 1027437000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-475979 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Total Costs and Expenses' on us-gaap:CostsAndExpenses = 1222984000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 207761000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Research and development costs' on us-gaap:ResearchAndDevelopmentExpense = 10537000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 205941000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -10181000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Income from continuing operations before Provision for Income Taxes and noncontr' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 221065000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 80416000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Net income (loss) attributable to BWX Technologies, Inc.' on us-gaap:NetIncomeLoss = 131465000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Net Income Attributable to BWX Technologies, Inc.' on us-gaap:EarningsPerShareBasic = 1.23 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Net Income Attributable to BWX Technologies, Inc.' on us-gaap:EarningsPerShareDiluted = 1.22 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 106703145 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-475979 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 107583022 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 154729000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Accounts receivable - trade, net' on us-gaap:AccountsReceivableNetCurrent = 153326000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 7311000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 647294000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Net Property, Plant and Equipment' on us-gaap:PropertyPlantAndEquipmentNet = 268844000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 168434000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-475979 R2.htm prints 'TOTAL' on us-gaap:Assets = 1382139000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 74130000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 353780000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-475979 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001193125-16-475979 R2.htm prints 'Stockholders' Equity - BWX Technologies, Inc.' on us-gaap:StockholdersEquity = 265716000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-475979 R9.htm prints 'NET CASH PROVIDED BY OPERATING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 330164000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-475979 R9.htm prints 'NET CASH PROVIDED BY (USED IN) INVESTING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -71887000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-475979 R9.htm prints 'NET CASH PROVIDED BY (USED IN) FINANCING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -409430000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -68335000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 78621000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Stock-based compensation and thrift plan expense' on us-gaap:ShareBasedCompensation = 31699000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Dividends paid to common shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -34479000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Repurchase of common shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -69747000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Interest' on us-gaap:InterestPaidNet = 6647000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-475979 R9.htm prints 'Income taxes (net of refunds)' on us-gaap:IncomeTaxesPaidNet = 117753000 (FILING-CHECKED)
- revenue: era 10-K 0001486957-18-000007 R4.htm prints 'Revenues' on us-gaap:Revenues = 1687738000 (FILING-CHECKED)
- interest_expense: era 10-K 0001486957-24-000011 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -47036000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | NOTE | agree | value 231036000 read off its own R page (no companyfacts fact to compare) |
| operating_expenses | combined | agree | page value 2868877000 vs printed 2868877000 |
| income_before_tax | mapped-sample | agree | page value 398120000 vs printed 398120000 |
| capex | mapped-sample | agree | page value -184557000 vs printed -184557000 |
| sbc | mapped-sample | agree | page value 26072000 vs printed 26072000 |
| cash_paid_for_income_taxes | mapped-sample | agree | page value 47892000 vs printed 47892000 |
| total_debt | component sum | agree | page value 2015983000 vs printed 2015983000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
