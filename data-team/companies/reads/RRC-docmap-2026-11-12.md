# RRC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-067292 (CIK 0000315852, filed 2026-02-24): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001564590-16-013402 (CIK 0000315852, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0000315852.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total revenues and other income | 3115515000 | 3115515000 | 2417084000 | 2417084000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Brokered natural gas and marketing | 185554000 | 185554000 | 140545000 | 140545000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total costs and expenses | 2283825000 | 2283825000 | 2166479000 | 2166479000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 178315000 | 178315000 | 172139000 | 172139000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest | 104897000 | 104897000 | 118758000 | 118758000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:ResultsOfOperationsIncomeBeforeIncomeTaxes | R4.htm | Income before income taxes | 831690000 | 831690000 | 250605000 | 250605000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense (benefit) | 173666000 | 173666000 | -15735000 | -15735000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 658024000 | 658024000 | 266340000 | 266340000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 2.76 | 2.76 | 1.1 | 1.1 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 2.74 | 2.74 | 1.09 | 1.09 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 237943000 | 237943000 | 240689000 | 240689000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 239789000 | 239789000 | 242745000 | 242745000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 204000 | 204000 | 304490000 | 304490000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, less allowance for doubtful accounts of $248 and $255 | 358687000 | 358687000 | 302212000 | 302212000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 444480000 | 444480000 | 721461000 | 721461000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Other property and equipment, net | 4935000 | 4935000 | 2465000 | 2465000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| goodwill | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 7421948000 | 7421948000 | 7347675000 | 7347675000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 164352000 | 164352000 | 133132000 | 133132000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 661152000 | 661152000 | 1274070000 | 1274070000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 3103267000 | 3103267000 | 3411018000 | 3411018000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 4318681000 | 4318681000 | 3936657000 | 3936657000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided from operating activities | 1171324000 | 1171324000 | 944514000 | 944514000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -641393000 | -641393000 | -623833000 | -623833000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash used in financing activities | -834217000 | -834217000 | -228165000 | -228165000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R6.htm period ..2025-12-31 |
| capex | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depletion, depreciation and amortization | 370462000 | 370462000 | 358356000 | 358356000 | Y | FILING-CHECKED | accn 0001193125-26-067292 R6.htm period ..2025-12-31 |
| sbc | mapped | rrc:ShareBasedCompensationIncludingDeferredAmounts | R6.htm | Deferred and stock-based compensation | 48153000 |  | 53864000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-067292 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Dividends paid | -85680000 | 85680000 | -77463000 | 77463000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-067292 R6.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R85.htm | Supplemental Cash Flow Information - Supplemental Cash Flow Information (Detail) |  | 104719000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R85.htm 'Supplemental Cash Flow Information - Supplemental Cash Flow Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (1011 tags across all 105 R pages, face and notes) of 0001193125-26-067292; no face row matched |
| total_debt | component sum | us-gaap:LongTermDebtCurrent | R2.htm | Current maturities of long-term debt | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R83.htm | Capital Stock - Schedule of Changes in Number of Common Shares Outstanding (Detail) |  | 235458212 |  |  |  | FILING-CHECKED | not on the face statement; shown in R83.htm 'Capital Stock - Schedule of Changes in Number of Common Shares Outstanding (Deta' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Total revenues and other income' on us-gaap:Revenues = 1598068000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-013402 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 2650430000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013402 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 194015000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Interest' on us-gaap:InterestExpense = 166439000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013402 R4.htm prints '(Loss) income before income taxes' on us-gaap:ResultsOfOperationsIncomeBeforeIncomeTaxes = -1052362000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Total income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -338677000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Net (loss) income' on us-gaap:NetIncomeLoss = -713685000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = -4.29 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = -4.29 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 166389000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013402 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 166389000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 471000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Accounts receivable, less allowance for doubtful accounts of $4,994 and $2,719' on us-gaap:AccountsReceivableNetCurrent = 123842000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 439074000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Other Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 19455000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Total assets' on us-gaap:Assets = 6900031000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 117346000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 351720000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 4140373000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013402 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 2759658000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013402 R7.htm prints 'Net cash provided from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 683700000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013402 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -218772000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013402 R7.htm prints 'Net cash (used in) provided from financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -464905000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013402 R7.htm prints 'Depletion, depreciation and amortization and impairment' on us-gaap:DepreciationDepletionAndAmortization = 1171329000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013402 R7.htm prints 'Deferred and stock-based compensation' on rrc:ShareBasedCompensationIncludingDeferredAmounts = -20411000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-013402 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -27083000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013402 R7.htm read; no row matched (auto)

## Mismatches (printed vs API)
- sbc: API missing (rrc:ShareBasedCompensationIncludingDeferredAmounts)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 2283825000 vs printed 2283825000 |
| sga_expense | component sum | agree | page value 363869000 vs printed 363869000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | mapped-sample | agree | page value 104897000 vs printed 104897000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | mapped-sample | agree | page value 444480000 vs printed 444480000 |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| capex | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sbc | mapped-sample | agree | page value 48153000 vs printed 48153000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value -104719000 vs API 104719000 |
| cash_paid_for_income_taxes | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 0 vs printed 0 |
| shares_outstanding | NOTE | DISAGREE | page value 240669354 vs API 235458212 |
