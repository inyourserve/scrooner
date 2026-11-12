# PAYC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-059372 (CIK 0001590955, filed 2026-02-19): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- 10-K 0001564590-16-013001 (CIK 0001590955, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001564590-18-002088 (CIK 0001590955, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001590955.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 2051700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 345400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| gross_profit | mapped | us-gaap:GrossProfit | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 1706300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (904 tags across all 77 R pages, face and notes) of 0001193125-26-059372; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 1139100000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 283400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 567200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpense | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 3400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R75.htm | Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for Each Reportable Segment Consistant with  |  | 619400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Segment Reporting - Schedule of Company 's Revenues Expenses and Net (Loss) for ' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R68.htm | Income Taxes - Components of Income Tax Expense (Detail) |  | 166000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R68.htm 'Income Taxes - Components of Income Tax Expense (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R9.htm | Pay vs Performance Disclosure |  | 453400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R9.htm 'Pay vs Performance Disclosure' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R59.htm | Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (Detail) |  | 8.13 |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (De' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R59.htm | Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (Detail) |  | 8.08 |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (De' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R59.htm | Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (Detail) |  | 55765000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (De' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R59.htm | Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (Detail) |  | 56116000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Earnings Per Share - Computation of Basic and Diluted Net Earnings Per Share (De' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 370000000 | 370000000 | 402000000 | 402000000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable | 44900000 | 44900000 | 39200000 | 39200000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventory | 1700000 | 1700000 | 1400000 | 1400000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 5838800000 | 5838800000 | 4304800000 | 4304800000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| ppe_net | mapped | payc:PropertyPlantAndEquipmentNetIncludingLandAndConstructionInProgress | R2.htm | Property and equipment, net | 687300000 |  | 561400000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 51900000 | 51900000 | 51900000 | 51900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 7598700000 | 7598700000 | 5859900000 | 5859900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 6600000 | 6600000 | 23900000 | 23900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 5368400000 | 5368400000 | 3906800000 | 3906800000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 5867200000 | 5867200000 | 4284000000 | 4284000000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders’ equity | 1731500000 | 1731500000 | 1575900000 | 1575900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 678900000 | 678900000 | 533900000 | 533900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -611200000 | -611200000 | -22200000 | -22200000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | 1022000000 | 1022000000 | 1108300000 | 1108300000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -270900000 | 270900000 | -192900000 | 192900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 176300000 | 176300000 | 145900000 | 145900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 118700000 | 118700000 | -22900000 | -22900000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid | -84800000 | 84800000 | -84800000 | 84800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock | -325500000 | 325500000 | -122800000 | 122800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest, net of amounts capitalized | 2100000 | 2100000 | 2000000 | 2000000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes, net of income tax refunds | 78100000 | 78100000 | 134800000 | 134800000 | Y | FILING-CHECKED | accn 0001193125-26-059372 R7.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R52.htm | Long-Term Debt - Additional Information (Detail) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R52.htm 'Long-Term Debt - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 54800000 | 54800000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Total revenues' on us-gaap:Revenues = 224653000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Total cost of revenues' on us-gaap:CostOfRevenue = 35473000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-16-013001 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Total administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 154745000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 8627000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 34435000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -1427000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 33525000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 12580000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Net income attributable to the Company' on us-gaap:NetIncomeLoss = 20945000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Net income per share, basic' on us-gaap:EarningsPerShareBasic = 0.37 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Net income per share, diluted' on us-gaap:EarningsPerShareDiluted = 0.36 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 56495170 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013001 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 57919700 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 50714000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Accounts receivable' on us-gaap:AccountsReceivableNetCurrent = 2354000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 1093000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 761138000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 58858000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 51889000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Total assets' on us-gaap:Assets = 876773000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 4899000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 727534000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013001 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001564590-16-013001 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 98314000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 42972000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -52324000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 34922000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -16549000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 9421000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 3010000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-013001 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001564590-16-013001 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Cash paid for interest, net of amounts capitalized' on us-gaap:InterestPaidNet = 1271000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013001 R6.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 19205000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-002088 R4.htm prints 'Total revenues' on us-gaap:Revenues = 433047000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-002088 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 130600000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-002088 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -290346000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-002088 R6.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 145665000 (FILING-CHECKED)

## Mismatches (printed vs API)
- ppe_net: API missing (payc:PropertyPlantAndEquipmentNetIncludingLandAndConstructionInProgress)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 2.052e+09 vs API 2051700000 |
| cost_of_revenue | NOTE | agree | page value 345400000 vs API 345400000 |
| gross_profit | NOTE | agree | page value 1706300000 vs API 1706300000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | NOTE | agree | page value 1139100000 vs API 1139100000 |
| research_and_development | NOTE | agree | page value 283400000 vs API 283400000 |
| operating_income | NOTE | agree | page value 567200000 vs API 567200000 |
| interest_expense | NOTE | agree | page value -3400000 vs API 3400000 |
| income_before_tax | NOTE | agree | page value 619400000 vs API 619400000 |
| income_tax_expense | NOTE | agree | page value 166000000 vs API 166000000 |
| net_income | NOTE | agree | page value 453400000 vs API 453400000 |
| basic_eps | NOTE | agree | page value 8.13 vs API 8.13 |
| diluted_eps | NOTE | agree | page value 8.08 vs API 8.08 |
| weighted_basic_shares | NOTE | agree | page value 55765000 vs API 55765000 |
| weighted_diluted_shares | NOTE | agree | page value 56116000 vs API 56116000 |
| ppe_net | mapped-sample | agree | page value 687300000 vs printed 687300000 |
| total_assets | mapped-sample | agree | page value 7598700000 vs printed 7598700000 |
| capex | mapped-sample | agree | page value -270900000 vs printed -270900000 |
| total_debt | NOTE | agree | value 0 read off its own R page (no companyfacts fact to compare) |
