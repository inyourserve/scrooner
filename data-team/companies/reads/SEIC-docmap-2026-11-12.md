# SEIC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000350894-26-000013 (CIK 0000350894, filed 2026-02-23): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- 10-K 0000350894-16-000102 (CIK 0000350894, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0000350894-24-000024 (CIK 0000350894, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- 10-K 0000350894-19-000012 (CIK 0000350894, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0000350894.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenue | 2297381000 | 2297381000 | 2125151000 | 2125151000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (979 tags across all 106 R pages, face and notes) of 0000350894-26-000013; no face row matched |
| gross_profit | mapped | us-gaap:GrossProfit | R86.htm | Business Segment Information - Schedule of Financial Information about Business Segments (Details) |  | 808134000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R86.htm 'Business Segment Information - Schedule of Financial Information about Business ' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total expenses | 1670070000 | 1670070000 | 1573410000 | 1573410000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R87.htm | Business Segment Information - Reconciliation of Total Operating Profit Reported for Business Segments to Income from Op |  | 180878000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R87.htm 'Business Segment Information - Reconciliation of Total Operating Profit Reported' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (979 tags across all 106 R pages, face and notes) of 0000350894-26-000013; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 627311000 | 627311000 | 551741000 | 551741000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -609000 | 609000 | -563000 | 563000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 916333000 | 916333000 | 746757000 | 746757000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income taxes | 198783000 | 198783000 | 165566000 | 165566000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to SEI Investments Company | 715305000 | 715305000 | 581191000 | 581191000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per common share (in USD per share) | 5.76 | 5.76 | 4.47 | 4.47 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per common share (in USD per share) | 5.63 | 5.63 | 4.41 | 4.41 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| weighted_basic_shares | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of WeightedAverageNumberOfSharesOutstandingBasic in MetaLinks.json (979 tags across all 106 R pages, face and notes) of 0000350894-26-000013; no face row matched |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Shares used to compute diluted earnings per share (in shares) | 127076000 | 127076000 | 131727000 | 131727000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 399804000 | 399804000 | 840193000 | 840193000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Receivables, net of allowance for doubtful accounts of $1,916 and $1,435 | 709748000 | 709748000 | 567634000 | 567634000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (979 tags across all 106 R pages, face and notes) of 0000350894-26-000013; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total Current Assets | 1273337000 | 1273337000 | 1551810000 | 1551810000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and Equipment, net of accumulated depreciation of $468,700 and $493,219 | 150434000 | 150434000 | 159643000 | 159643000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill, net | 354989000 | 354989000 | 170287000 | 170287000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Assets of Consolidated Variable Interest Entities | 183994000 |  | 0 |  | API missing | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 5404000 | 5404000 | 13081000 | 13081000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total Current Liabilities | 387211000 | 387211000 | 380513000 | 380513000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Liabilities of Consolidated Variable Interest Entities | 108504000 |  | 0 |  | API missing | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Equity, Attributable to Parent, Total | 2447784000 | 2447784000 | 2252112000 | 2252112000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided by operating activities | 607662000 | 607662000 | 622343000 | 622343000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash used in investing activities | -399092000 | -399092000 | -117302000 | -117302000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash used in financing activities | -589498000 | -589498000 | -494401000 | -494401000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Additions to property and equipment | -22644000 | 22644000 | -32226000 | 32226000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | component_in_note | us-gaap:AmortizationOfIntangibleAssets+us-gaap:DepreciationNonproduction | R97.htm | Goodwill and Intangible Assets - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | only component tag(s) AmortizationOfIntangibleAssets, DepreciationNonproduction in the filing (R97.htm 'Goodwill and Intangible Assets - Narrative (Details)'); the data point itself is not reported |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R10.htm | Stock-based compensation | 53555000 | 53555000 | 58626000 | 58626000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R10.htm | Payment of dividends | -124198000 | 124198000 | -120346000 | 120346000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Purchase and retirement of common stock | -628135000 | 628135000 | -500061000 | 500061000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Interest paid | 578000 | 578000 | 563000 | 563000 | Y | FILING-CHECKED | accn 0000350894-26-000013 R10.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R85.htm | Income Taxes - Income Taxes Paid (Details) |  | 169907000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R85.htm 'Income Taxes - Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component_in_note | us-gaap:NotesPayable | R91.htm | Business Acquisitions and Divestitures - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | only component tag(s) NotesPayable in the filing (R91.htm 'Business Acquisitions and Divestitures - Narrative (Details)'); the data point itself is not reported |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 122232251 | 122232251 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1334208000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000350894-16-000102 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Total expenses' on us-gaap:CostsAndExpenses = 975995000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000350894-16-000102 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 358213000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -483000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 500480000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 168825000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Net income attributable to SEI Investments Company' on us-gaap:NetIncomeLoss = 331655000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Basic earnings per common share' on us-gaap:EarningsPerShareBasic = 2 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Diluted earnings per common share' on us-gaap:EarningsPerShareDiluted = 1.96 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000350894-16-000102 R4.htm prints 'Shares used to compute diluted earnings per share' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 169598000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 679661000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Receivables, net of allowance for doubtful accounts of $649 and $784' on us-gaap:ReceivablesNetCurrent = 223023000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 1003724000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Property and Equipment, net of accumulated depreciation of $259,501 and $241,295' on us-gaap:PropertyPlantAndEquipmentNet = 143977000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000350894-16-000102 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Total Assets' on us-gaap:Assets = 1588628000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 4511000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 224483000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 298908000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000350894-16-000102 R2.htm prints 'Total Shareholders' Equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1289720000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 391460000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -78015000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -289805000 (FILING-CHECKED)
- capex: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -44465000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000350894-16-000102 R9.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Stock-based compensation' on us-gaap:AllocatedShareBasedCompensationExpense = 17312000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Payment of dividends' on us-gaap:PaymentsOfDividends = -80030000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Purchase and retirement of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -291374000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Interest paid' on us-gaap:InterestPaid = 460000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000350894-16-000102 R9.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 159605000 (FILING-CHECKED)
- interest_expense: era 10-K 0000350894-24-000024 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -583000 (FILING-CHECKED)
- accounts_receivable: era 10-K 0000350894-19-000012 R2.htm prints 'Receivables, net of allowance for doubtful accounts of $718 and $695' on us-gaap:ReceivablesNetCurrent = 315336000 (FILING-CHECKED)

## Mismatches (printed vs API)
- total_assets: API missing (us-gaap:Assets)
- total_liabilities: API missing (us-gaap:Liabilities)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 2297381000 vs printed 2297381000 |
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | NOTE | agree | page value 808134000 vs API 808134000 |
| operating_expenses | combined | agree | page value 1670070000 vs printed 1670070000 |
| sga_expense | NOTE | agree | page value -180878000 vs API 180878000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| weighted_basic_shares | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | mapped-sample | agree | page value 108504000 vs printed 108504000 |
| depreciation_and_amortization | NOTE | agree | component element on R97.htm |
| sbc | mapped-sample | agree | page value 53555000 vs printed 53555000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 169907000 vs API 169907000 |
| total_debt | NOTE | agree | component element on R91.htm |
