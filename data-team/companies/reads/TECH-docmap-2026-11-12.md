# TECH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-100322 (CIK 0000842023, filed 2026-08-24): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R6.htm
- 10-K 0001437749-15-016645 (CIK 0000842023, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001437749-17-015711 (CIK 0000842023, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R6.htm
- 10-K 0001437749-18-016190 (CIK 0000842023, era filing): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000842023.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net sales | 1215039000 | 1215039000 | 1219635000 | 1219635000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of sales | 415968000 | 415968000 | 429363000 | 429363000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross margin | 799071000 | 799071000 | 790272000 | 790272000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R2.htm | Total operating expenses | 547181000 | 547181000 | 688017000 | 688017000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative | 452415000 | 452415000 | 588521000 | 588521000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost | R2.htm | Research and development | 94766000 | 94766000 | 99496000 | 99496000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income | 251890000 | 251890000 | 102255000 | 102255000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R2.htm | Interest expense | -9630000 | 9630000 | -8509000 | 8509000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Earnings before income taxes | 240680000 | 240680000 | 98463000 | 98463000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income taxes | 58818000 | 58818000 | 25063000 | 25063000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:ProfitLoss | R2.htm | Net earnings | 181862000 | 181862000 | 73400000 | 73400000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic (in dollars per share) | 1.17 | 1.17 | 0.47 | 0.47 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted (in dollars per share) | 1.16 | 1.16 | 0.46 | 0.46 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic (in shares) | 155963000 | 155963000 | 157521000 | 157521000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted (in shares) | 157009000 | 157009000 | 159717000 | 159717000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R2.htm period ..2026-06-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 264712000 | 264712000 | 162186000 | 162186000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, less allowances of $4,644 and $4,215, respectively | 216585000 | 216585000 | 206876000 | 206876000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 195744000 | 195744000 | 189446000 | 189446000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 744401000 | 744401000 | 608300000 | 608300000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 231836000 | 231836000 | 245719000 | 245719000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 975355000 | 975355000 | 980935000 | 980935000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2586726000 | 2586726000 | 2557868000 | 2557868000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Trade accounts payable | 26699000 | 26699000 | 25311000 | 25311000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 163700000 | 163700000 | 175849000 | 175849000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (838 tags across all 78 R pages, face and notes) of 0001104659-26-100322; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders' equity | 2108221000 | 2108221000 | 1918808000 | 1918808000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R3.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 292073000 | 292073000 | 287556000 | 287556000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -18190000 | -18190000 | -35183000 | -35183000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash used in financing activities | -169114000 | -169114000 | -253905000 | -253905000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Additions to property and equipment | -28850000 | 28850000 | -31006000 | 31006000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 97359000 | 97359000 | 109903000 | 109903000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock-based compensation expense | 41365000 | 41365000 | 40833000 | 40833000 | Y | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Cash dividends | -49916000 | 49916000 | -50391000 | 50391000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchases of common stock | -41675000 | 41675000 | -275731000 | 275731000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-100322 R6.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R49.htm | Supplemental Balance Sheet and Cash Flow Information - Supplemental Cash Flow Information (Details) |  | 14395000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R49.htm 'Supplemental Balance Sheet and Cash Flow Information - Supplemental Cash Flow In' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R49.htm | Supplemental Balance Sheet and Cash Flow Information - Supplemental Cash Flow Information (Details) |  | 64149000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R49.htm 'Supplemental Balance Sheet and Cash Flow Information - Supplemental Cash Flow In' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Long-term debt obligations | 200000000 | 200000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 156095113 | 156095113 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-06-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 452246000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 144969000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Gross margin' on us-gaap:GrossProfit = 307277000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001437749-15-016645 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 119401000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost = 40853000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 147022 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -1544000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 154162000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 46427000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 107735000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.9 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.89 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 37096000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001437749-15-016645 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 37231000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 54532000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Accounts receivable, less allowance for doubtful accounts of $555 and $487, resp' on us-gaap:AccountsReceivableNetCurrent = 70034000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 49577000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 248283000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 129749000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 390638000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Assets' on us-gaap:Assets = 1063360000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableCurrent = 13443000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 39768000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001437749-15-016645 R4.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 846935000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 139359000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -426493000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 31276000 (FILING-CHECKED)
- capex: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -19905000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 37226000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 5957000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Cash dividends' on us-gaap:PaymentsOfDividendsCommonStock = -47106000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001437749-15-016645 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001437749-15-016645 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001437749-15-016645 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001437749-17-015711 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 563003000 (FILING-CHECKED)
- cfo: era 10-K 0001437749-17-015711 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 143448000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001437749-17-015711 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -305954000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001437749-17-015711 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 189386000 (FILING-CHECKED)
- revenue: era 10-K 0001437749-18-016190 R2.htm prints 'Net sales' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 642993000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | mapped-sample | agree | page value 547181000 vs printed 547181000 |
| income_before_tax | mapped-sample | agree | page value 240680000 vs printed 240680000 |
| diluted_eps | mapped-sample | agree | page value 1.16 vs printed 1.16 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| stockholders_equity | mapped-sample | agree | page value 2108221000 vs printed 2108221000 |
| cash_paid_for_interest | NOTE | agree | page value 14395000 vs API 14395000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 64149000 vs API 64149000 |
| total_debt | component sum | agree | page value 200000000 vs printed 200000000 |
