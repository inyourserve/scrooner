# UHS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-071676 (CIK 0000352915, filed 2026-02-25): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001564590-16-013375 (CIK 0000352915, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001564590-18-003808 (CIK 0000352915, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001564590-19-004919 (CIK 0000352915, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000352915.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net revenues | 17364829000 | 17364829000 | 15827935000 | 15827935000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1271 tags across all 105 R pages, face and notes) of 0001193125-26-071676; no face row matched |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1271 tags across all 105 R pages, face and notes) of 0001193125-26-071676; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R2.htm | Operating Expenses, Total | 15370814000 | 15370814000 | 14146121000 | 14146121000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1271 tags across all 105 R pages, face and notes) of 0001193125-26-071676; no face row matched |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1271 tags across all 105 R pages, face and notes) of 0001193125-26-071676; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Income from operations | 1994015000 | 1994015000 | 1681814000 | 1681814000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R2.htm | Interest expense, net | 156068000 | 156068000 | 186109000 | 186109000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income taxes | 1972141000 | 1972141000 | 1497936000 | 1497936000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 460959000 | 460959000 | 334827000 | 334827000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income attributable to UHS | 1488796000 | 1488796000 | 1142097000 | 1142097000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic earnings per share attributable to UHS | 23.42 | 23.42 | 17.16 | 17.16 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted earnings per share attributable to UHS | 23.1 | 23.1 | 16.82 | 16.82 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Weighted average number of common shares—basic | 63581000 | 63581000 | 66554000 | 66554000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Weighted average number of common shares and equivalents—diluted | 64462000 | 64462000 | 67896000 | 67896000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 137797000 | 137797000 | 125983000 | 125983000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable, net | 2602434000 | 2602434000 | 2177751000 | 2177751000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| inventory | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1271 tags across all 105 R pages, face and notes) of 0001193125-26-071676; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 3407915000 | 3407915000 | 2816288000 | 2816288000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property, plant and equipment, net, Total | 7008097000 | 7008097000 | 6572225000 | 6572225000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 3990213000 | 3990213000 | 3932879000 | 3932879000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total Assets | 15527593000 | 15527593000 | 14469749000 | 14469749000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 750134000 | 750134000 | 632001000 | 632001000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 3239601000 | 3239601000 | 2210406000 | 2210406000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1271 tags across all 105 R pages, face and notes) of 0001193125-26-071676; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Universal Health Services, Inc. common stockholders’ equity | 7275792000 | 7275792000 | 6666207000 | 6666207000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1864397000 | 1864397000 | 2067101000 | 2067101000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -1070617000 | -1070617000 | -911109000 | -911109000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -749727000 | -749727000 | -1144877000 | -1144877000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Property and equipment additions | -1015152000 | 1015152000 | -943810000 | 943810000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R102.htm | Segment Reporting (Detail) |  | 618743000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R102.htm 'Segment Reporting (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 95688000 | 95688000 | 99349000 | 99349000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid | -51267000 | 51267000 | -53346000 | 53346000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common shares | -967951000 | 967951000 | -670754000 | 670754000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 156041000 | 156041000 | 168274000 | 168274000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid, net of refunds | 470865000 | 470865000 | 325430000 | 325430000 | Y | FILING-CHECKED | accn 0001193125-26-071676 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R4.htm | Current maturities of long-term debt + Long-term debt | 4752551000 | 4752551000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R5.htm | Common Stock, shares outstanding | 61064008 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 9043451000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Operating Expenses, Total' on us-gaap:OperatingExpenses = 7784056000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 1259395000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 113494000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1145901000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 395203000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Net income attributable to UHS' on us-gaap:NetIncomeLoss = 680528000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Basic earnings per share attributable to UHS' on us-gaap:EarningsPerShareBasic = 6.89 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Diluted earnings per share attributable to UHS' on us-gaap:EarningsPerShareDiluted = 6.76 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Weighted average number of common shares—basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 98797000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013375 R2.htm prints 'Weighted average number of common shares and equivalents—diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 100694000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 61228000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 1302429000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1718304000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Property, plant and equipment, net, Total' on us-gaap:PropertyPlantAndEquipmentNet = 3835978000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 3596114000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Total assets' on us-gaap:Assets = 9634113000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 366238000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1100406000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013375 R4.htm prints 'Universal Health Services, Inc. common stockholders’ equity' on us-gaap:StockholdersEquity = 4249647000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1020898000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -912885000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -77245000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Property and equipment additions, net of disposals' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -379321000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Depreciation & amortization' on us-gaap:DepreciationDepletionAndAmortization = 398618000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 39971000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -39532000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Repurchase of common shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -209782000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Interest paid, including early redemption premium and original issue discount wr' on us-gaap:InterestPaidNet = 107054000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013375 R8.htm prints 'Income taxes paid, net of refunds' on us-gaap:IncomeTaxesPaidNet = 380658000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-003808 R2.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 10409865000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001564590-19-004919 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -37342000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value 156068000 vs printed 156068000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 7008097000 vs printed 7008097000 |
| total_assets | mapped-sample | agree | page value 15527593000 vs printed 15527593000 |
| accounts_payable | mapped-sample | agree | page value 750134000 vs printed 750134000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | NOTE | agree | page value 618743000 vs API 618743000 |
| total_debt | component sum | agree | page value 4843672000 vs printed 4843672000 |
| shares_outstanding | component sum | agree | page value 61064008 vs printed 61064008 |
