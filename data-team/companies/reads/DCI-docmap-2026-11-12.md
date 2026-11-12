# DCI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000029644-26-000085 (CIK 0000029644, filed 2026-09-25): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0000897101-15-001507 (CIK 0000029644, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000029644-18-000024 (CIK 0000029644, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000029644-17-000019 (CIK 0000029644, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000029644.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Net sales | 3885600000 | 3885600000 | 3690900000 | 3690900000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 2539700000 | 2539700000 | 2404700000 | 2404700000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1345900000 | 1345900000 | 1286200000 | 1286200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Operating expenses | 746000000 | 746000000 | 790800000 | 790800000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 679200000 | 679200000 | 642200000 | 642200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 76100000 | 76100000 | 87800000 | 87800000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 599900000 | 599900000 | 495400000 | 495400000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 36000000 | 36000000 | 24200000 | 24200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before income taxes | 585800000 | 585800000 | 492200000 | 492200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 132000000 | 132000000 | 125200000 | 125200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 453800000 | 453800000 | 367000000 | 367000000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net earnings per share – basic (in usd per share) | 3.92 | 3.92 | 3.09 | 3.09 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net earnings per share – diluted (in usd per share) | 3.85 | 3.85 | 3.05 | 3.05 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted average shares – basic (in shares) | 115800000 | 115800000 | 118700000 | 118700000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted average shares – diluted (in shares) | 117900000 | 117900000 | 120400000 | 120400000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R3.htm period ..2026-07-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 250400000 | 250400000 | 180400000 | 180400000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, less allowances of $3.2 and $2.9, respectively | 758100000 | 758100000 | 662200000 | 662200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories, net | 538700000 | 538700000 | 513600000 | 513600000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 1669700000 | 1669700000 | 1461700000 | 1461700000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 633300000 | 633300000 | 644500000 | 644500000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1086800000 | 1086800000 | 493600000 | 493600000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 3986800000 | 3986800000 | 2977200000 | 2977200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 378600000 | 378600000 | 368600000 | 368600000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 804100000 | 804100000 | 757200000 | 757200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 2222400000 | 2222400000 | 1523700000 | 1523700000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders’ equity | 1764400000 | 1764400000 | 1453500000 | 1453500000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R6.htm period ..2026-07-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 493700000 | 493700000 | 418800000 | 418800000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -879500000 | -879500000 | -150400000 | -150400000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 451600000 | 451600000 | -321700000 | -321700000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, plant and equipment | -67400000 | 67400000 | -78900000 | 78900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 106000000 | 106000000 | 99500000 | 99500000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 24700000 | 24700000 | 24000000 | 24000000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid | -141200000 | 141200000 | -131900000 | 131900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchase of treasury stock | -111200000 | 111200000 | -331500000 | 331500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 33100000 | 33100000 | 22200000 | 22200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid | 160900000 | 160900000 | 176200000 | 176200000 | Y | FILING-CHECKED | accn 0000029644-26-000085 R8.htm period ..2026-07-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Short-term borrowings + Current maturities of long-term debt + Long-term debt | 1324800000 | 1324800000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1017 tags across all 111 R pages, face and notes) of 0000029644-26-000085; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 2371213000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 1562629000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 808584000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Selling, general, and administrative + Research and development' on us-gaap:OtherSellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense = 520274000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Selling, general, and administrative' on us-gaap:OtherSellingGeneralAndAdministrativeExpense = 460045000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 60229000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 288310000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 15157000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 288603000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 80492000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 208111000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Net earnings per share - basic' on us-gaap:EarningsPerShareBasic = 1.51 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Net earnings per share - diluted' on us-gaap:EarningsPerShareDiluted = 1.49 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Weighted average shares - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 137750158 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000897101-15-001507 R2.htm prints 'Weighted average shares - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 139381940 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 189898000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Accounts receivable, less allowance of $6,747 and $6,763' on us-gaap:AccountsReceivableNetCurrent = 460027000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Inventories, net' on us-gaap:InventoryNet = 264955000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1030716000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Property, plant, and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 470611000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 223732000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Total assets' on us-gaap:Assets = 1809534000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableCurrent = 179174000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 560647000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 1030883000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000897101-15-001507 R5.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 778651000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 212843000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -111728000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -179034000 (FILING-CHECKED)
- capex: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Purchases of property, plant, and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -93739000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 74298000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Stock compensation plan expense' on us-gaap:ShareBasedCompensation = 10694000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -91220000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -256267000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Interest' on us-gaap:InterestPaidNet = 14735000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000897101-15-001507 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 85568000 (FILING-CHECKED)
- revenue: era 10-K 0000029644-18-000024 R2.htm prints 'Net sales' on us-gaap:Revenues = 2734200000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000029644-17-000019 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 1548800000 (FILING-CHECKED)
- cfo: era 10-K 0000029644-17-000019 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 310300000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000029644-17-000019 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -95700000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000029644-17-000019 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -157700000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| interest_expense | mapped-sample | agree | page value 36000000 vs printed 36000000 |
| diluted_eps | mapped-sample | agree | page value 3.85 vs printed 3.85 |
| weighted_diluted_shares | mapped-sample | agree | page value 117900000 vs printed 117900000 |
| sbc | mapped-sample | agree | page value 24700000 vs printed 24700000 |
| total_debt | component sum | agree | page value 1324800000 vs printed 1324800000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
