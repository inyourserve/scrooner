# LII document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001069202-26-000028 (CIK 0001069202, filed 2026-02-17): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001069202-16-000014 (CIK 0001069202, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001069202-18-000004 (CIK 0001069202, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001069202.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenues | 5195300000 | 5195300000 | 5341300000 | 5341300000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 3460500000 | 3460500000 | 3563800000 | 3563800000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1734800000 | 1734800000 | 1777500000 | 1777500000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1100 tags across all 145 R pages, face and notes) of 0001069202-26-000028; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 681400000 | 681400000 | 730600000 | 730600000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R93.htm | Supplemental Information (Expenses) (Details) |  | 103400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R93.htm 'Supplemental Information (Expenses) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1041500000 | 1041500000 | 1040400000 | 1040400000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest expense, net | 40900000 | 40900000 | 38700000 | 38700000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 996800000 | 996800000 | 999400000 | 999400000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 191000000 | 191000000 | 188300000 | 188300000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 805800000 | 805800000 | 811100000 | 811100000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic Earnings (Loss) per Share (in usd per share) | 22.89 | 22.89 | 22.78 | 22.78 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted Earnings (Loss) per Share (in usd per share) | 22.79 | 22.79 | 22.66 | 22.66 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 35200000 | 35200000 | 35600000 | 35600000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 35400000 | 35400000 | 35800000 | 35800000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 34200000 | 34200000 | 415100000 | 415100000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Accounts and notes receivable, net of allowances | 578800000 | 578800000 | 661100000 | 661100000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, net | 1152600000 | 1152600000 | 853000000 | 853000000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1903800000 | 1903800000 | 2032400000 | 2032400000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Total property, plant and equipment, net | 887200000 | 887200000 | 800100000 | 800100000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 497200000 | 497200000 | 220000000 | 220000000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4081800000 | 4081800000 | 3620000000 | 3620000000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 438000000 | 438000000 | 490000000 | 490000000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1191800000 | 1191800000 | 1313300000 | 1313300000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2918700000 | 2918700000 | 2657900000 | 2657900000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 1163100000 | 1163100000 | 962100000 | 962100000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 757600000 | 757600000 | 945700000 | 945700000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -655600000 | -655600000 | -174400000 | -174400000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -465700000 | -465700000 | -418600000 | -418600000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment | -118800000 | 118800000 | -163600000 | 163600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 112500000 | 112500000 | 95100000 | 95100000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 29100000 | 29100000 | 28500000 | 28500000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends paid | -173000000 | 173000000 | -160300000 | 160300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -482300000 | 482300000 | -53600000 | 53600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 46500000 | 46500000 | 45200000 | 45200000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid (net of refunds) | 103800000 | 103800000 | 231900000 | 231900000 | Y | FILING-CHECKED | accn 0001069202-26-000028 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:CommercialPaper+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Commercial paper + Current maturities of long-term debt + Long-term debt | 1.388e+09 | 1388400000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1100 tags across all 145 R pages, face and notes) of 0001069202-26-000028; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3467400000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsAndServicesSold = 2520000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 947400000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 580500000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001069202-16-000014 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Operational income from continuing operations' on us-gaap:OperatingIncomeLoss = 305400000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 23600000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 282600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 95400000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 186600000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Net income (in usd per share)' on us-gaap:EarningsPerShareBasic = 4.16 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Net income (in usd per share)' on us-gaap:EarningsPerShareDiluted = 4.09 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 44900000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001069202-16-000014 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 45600000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 38900000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Accounts and notes receivable, net of allowances of $6.3 and $7.9 in 2015 and 20' on us-gaap:ReceivablesNetCurrent = 422800000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 418800000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 938200000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 339600000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 195100000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Total assets' on us-gaap:Assets = 1680200000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 320100000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 824000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1578600000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001069202-16-000014 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 101600000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 331200000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -69800000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -248700000 (FILING-CHECKED)
- capex: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -69900000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 62800000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 26600000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -59300000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Interest, net' on us-gaap:InterestPaidNet = 23700000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001069202-16-000014 R8.htm prints 'Income taxes (net of refunds)' on us-gaap:IncomeTaxesPaidNet = 83200000 (FILING-CHECKED)
- revenue: era 10-K 0001069202-18-000004 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3839600000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 5195300000 vs printed 5195300000 |
| cost_of_revenue | mapped-sample | agree | page value 3460500000 vs printed 3460500000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | NOTE | agree | page value 103400000 vs API 103400000 |
| interest_expense | combined | agree | page value 40900000 vs printed 40900000 |
| total_assets | mapped-sample | agree | page value 4081800000 vs printed 4081800000 |
| cash_paid_for_interest | mapped-sample | agree | page value 46500000 vs printed 46500000 |
| total_debt | component sum | agree | page value 1388400000 = printed 1.388e+09 at 4 significant digits; fy0_printed restored to the page value |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
