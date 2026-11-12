# GMED document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-011209 (CIK 0001237831, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001237831-16-000075 (CIK 0001237831, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001237831-18-000012 (CIK 0001237831, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001562762-21-000036 (CIK 0001237831, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001237831.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Net sales | 2938931000 | 2938931000 | 2519355000 | 2519355000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales (exclusive of amortization of intangibles) | 957802000 | 957802000 | 1035479000 | 1035479000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (963 tags across all 108 R pages, face and notes) of 0001628280-26-011209; no face row matched |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (963 tags across all 108 R pages, face and notes) of 0001628280-26-011209; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1178498000 | 1178498000 | 981362000 | 981362000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 147246000 | 147246000 | 163754000 | 163754000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income/(loss) | 479816000 | 479816000 | 165991000 | 165991000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income/(expense), net | 7141000 | 7141000 | -4189000 | -4189000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income/(loss) before income taxes | 605068000 | 605068000 | 120722000 | 120722000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision/(benefit) | 67200000 | 67200000 | 17738000 | 17738000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income/(loss) | 537868000 | 537868000 | 102984000 | 102984000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in USD per share) | 3.98 | 3.98 | 0.76 | 0.76 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in USD per share) | 3.92 | 3.92 | 0.75 | 0.75 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 135215000 | 135215000 | 135726000 | 135726000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 137056000 | 137056000 | 137863000 | 137863000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 526156000 | 526156000 | 784438000 | 784438000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances of $33,434 and $15,505, respectively | 678938000 | 678938000 | 557697000 | 557697000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 759277000 | 759277000 | 659233000 | 659233000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2125611000 | 2125611000 | 2177260000 | 2177260000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 564452000 | 564452000 | 561909000 | 561909000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1435033000 | 1435033000 | 1432387000 | 1432387000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 5302761000 | 5302761000 | 5251750000 | 5251750000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 98852000 | 98852000 | 75118000 | 75118000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 498499000 | 498499000 | 855913000 | 855913000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 729511000 | 729511000 | 1074417000 | 1074417000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total equity | 4573250000 | 4573250000 | 4177333000 | 4177333000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by/(used in) operating activities | 753447000 | 753447000 | 520638000 | 520638000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by/(used in) investing activities | -355014000 | -355014000 | -176051000 | -176051000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by/(used in) financing activities | -679160000 | -679160000 | -27696000 | -27696000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -164679000 | 164679000 | -115429000 | 115429000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 276842000 | 276842000 | 253389000 | 253389000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 49779000 | 49779000 | 54191000 | 54191000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (963 tags across all 108 R pages, face and notes) of 0001628280-26-011209; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -300451000 | 300451000 | -85787000 | 85787000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (963 tags across all 108 R pages, face and notes) of 0001628280-26-011209; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid, net | 98916000 | 98916000 | 158508000 | 158508000 | Y | FILING-CHECKED | accn 0001628280-26-011209 R7.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R74.htm | DEBT - Schedule of Convertible Notes (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'DEBT - Schedule of Convertible Notes (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 135055223 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Sales' on us-gaap:SalesRevenueNet = 544753000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 132803000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 214014000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 36982000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 172222000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001237831-16-000075 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 172805000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 60021000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 112784000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 1.19 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 1.17 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 95046000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001237831-16-000075 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 96073000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 60152000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Accounts receivable, net of allowances of $2,513 and $1,647, respectively' on us-gaap:AccountsReceivableNetCurrent = 77681000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 105260000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 544799000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Property and equipment, net of accumulated depreciation of $139,114 and $118,544' on us-gaap:PropertyPlantAndEquipmentNet = 114743000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 91964000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Total assets' on us-gaap:Assets = 834100000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 15971000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 82691000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 118776000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001237831-16-000075 R2.htm prints 'Total equity' on us-gaap:StockholdersEquity = 715324000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 121957000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -150550000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 6327000 (FILING-CHECKED)
- capex: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -50760000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 24084000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 9639000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001237831-16-000075 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001237831-16-000075 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 57100000 (FILING-CHECKED)
- revenue: era 10-K 0001237831-18-000012 R4.htm prints 'Sales' on us-gaap:SalesRevenueNet = 635977000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001237831-18-000012 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 150453000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001562762-21-000036 R4.htm prints 'Income/(loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 125899000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value 479816000 vs printed 479816000 |
| interest_expense | combined | agree | page value 7141000 vs printed 7141000 |
| net_income | mapped-sample | agree | page value 537868000 vs printed 537868000 |
| cash_and_equivalents | mapped-sample | agree | page value 526156000 vs printed 526156000 |
| capex | mapped-sample | agree | page value -164679000 vs printed -164679000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | page value 784000 vs printed 784000 |
| shares_outstanding | component sum | agree | page value 135055223 vs printed 135055223 |
