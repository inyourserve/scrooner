# PNW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000764622-26-000011 (CIK 0000764622, filed 2026-02-25): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0000764622-16-000087 (CIK 0000764622, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000764622-18-000018 (CIK 0000764622, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000764622-24-000016 (CIK 0000764622, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0000764622.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | OPERATING REVENUES (Note 4) | 5339939000 | 5339939000 | 5124915000 | 5124915000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total | 4272309000 | 4272309000 | 4112852000 | 4112852000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | OPERATING INCOME | 1067630000 | 1067630000 | 1012063000 | 1012063000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Total | 421968000 | 421968000 | 377472000 | 377472000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Income Before Income Taxes | 738369000 | 738369000 | 736559000 | 736559000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Taxes (Note 5) | 106726000 | 106726000 | 110529000 | 110529000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R3.htm | Net Income (Loss) Attributable to Common Shareholders | 616531000 | 616531000 | 608806000 | 608806000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income attributable to common shareholders — basic (in dollars per share) | 5.15 | 5.15 | 5.35 | 5.35 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income attributable to common shareholders — diluted (in dollars per share) | 5.05 | 5.05 | 5.24 | 5.24 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted average common shares outstanding — basic (in shares) | 119687000 | 119687000 | 113846000 | 113846000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted-average common shares outstanding — diluted (in shares) | 121971000 | 121971000 | 116232000 | 116232000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 6604000 | 6604000 | 3838000 | 3838000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 1703709000 | 1703709000 | 1689404000 | 1689404000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Net | 18358275000 | 18358275000 | 16833524000 | 16833524000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| goodwill | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| total_assets | mapped | us-gaap:Assets | R6.htm | TOTAL ASSETS | 30031599000 | 30031599000 | 26102760000 | 26102760000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 680203000 | 680203000 | 485426000 | 485426000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 3161026000 | 3161026000 | 2843797000 | 2843797000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total shareholder equity | 7046458000 | 7046458000 | 6754311000 | 6754311000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1805095000 | 1805095000 | 1609823000 | 1609823000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -2378674000 | -2378674000 | -1933630000 | -1933630000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 576345000 | 576345000 | 322690000 | 322690000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Capital expenditures | -2624618000 | 2624618000 | -2249195000 | 2249195000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization including nuclear fuel | 969615000 | 969615000 | 956184000 | 956184000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock compensation | 27457000 | 27457000 | 23532000 | 23532000 | Y | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid on common stock | -422792000 | 422792000 | -394663000 | 394663000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000764622-26-000011 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R69.htm | Summary of Significant Accounting Policies - Schedule of Supplemental Cash Flow Information (Details) |  | 388540000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Summary of Significant Accounting Policies - Schedule of Supplemental Cash Flow ' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R69.htm | Summary of Significant Accounting Policies - Schedule of Supplemental Cash Flow Information (Details) |  | 22754000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Summary of Significant Accounting Policies - Schedule of Supplemental Cash Flow ' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Short-term borrowings (Note 6) + Current maturities of long-term debt (Note 6) + LONG-TERM DEBT LESS CURRENT MATURITIES  | 10562681000 | 10562681000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1428 tags across all 138 R pages, face and notes) of 0000764622-26-000011; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000764622-16-000087 R2.htm prints 'OPERATING REVENUES' on us-gaap:SalesRevenueNet = 3495443000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000764622-16-000087 R2.htm prints 'Total' on us-gaap:CostsAndExpenses = 2640841000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000764622-16-000087 R2.htm prints 'OPERATING INCOME' on us-gaap:OperatingIncomeLoss = 854602000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000764622-16-000087 R2.htm prints 'Total' on us-gaap:InterestExpense = 178705000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000764622-16-000087 R2.htm prints 'INCOME BEFORE INCOME TAXES' on us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest = 693910000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000764622-16-000087 R2.htm prints 'INCOME TAXES (Note 4)' on us-gaap:IncomeTaxExpenseBenefit = 237720000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000764622-16-000087 R2.htm prints 'NET INCOME ATTRIBUTABLE TO COMMON SHAREHOLDERS' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 437257000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000764622-16-000087 R2.htm prints 'Net income attributable to common shareholders - basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.94 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000764622-16-000087 R2.htm prints 'Net income attributable to common shareholders — diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.92 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000764622-16-000087 R2.htm prints 'Weighted Average common shares outstanding — basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 111026000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000764622-16-000087 R2.htm prints 'Weighted Average common shares outstanding — diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 111552000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 39488000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 890516000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Net' on us-gaap:PropertyPlantAndEquipmentNet = 10628138000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Total Assets' on us-gaap:Assets = 15028258000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 297480000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1442317000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000764622-16-000087 R5.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 4583917000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Net cash flow provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1094327000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Net cash flow used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1066233000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Net cash flow provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 3790000 (FILING-CHECKED)
- capex: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -1076087000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Depreciation and amortization including nuclear fuel' on us-gaap:DepreciationDepletionAndAmortization = 571664000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000764622-16-000087 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -260027000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Interest, net of amounts capitalized' on us-gaap:InterestPaidNet = 170209000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000764622-16-000087 R7.htm prints 'Income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 6550000 (FILING-CHECKED)
- revenue: era 10-K 0000764622-18-000018 R2.htm prints 'OPERATING REVENUES' on us-gaap:SalesRevenueNet = 3565296000 (FILING-CHECKED)
- interest_expense: era 10-K 0000764622-24-000016 R3.htm prints 'Total' on us-gaap:InterestExpense = 331323000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 4272309000 vs printed 4272309000 |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | mapped-sample | agree | page value 738369000 vs printed 738369000 |
| cash_and_equivalents | mapped-sample | agree | page value 6604000 vs printed 6604000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | mapped-sample | agree | page value 680203000 vs printed 680203000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 388540000 vs API 388540000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 22754000 vs API 22754000 |
| total_debt | component sum | agree | page value 10562681000 vs printed 10562681000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
