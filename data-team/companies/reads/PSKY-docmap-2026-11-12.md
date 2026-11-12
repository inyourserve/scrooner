# PSKY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0002041610-26-000011 (CIK 0002041610, filed 2026-02-25): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0002041610.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 29213000000 | 29213000000 | 29652000000 | 29652000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1352 tags across all 129 R pages, face and notes) of 0002041610-26-000011; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1352 tags across all 129 R pages, face and notes) of 0002041610-26-000011; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total segment expenses | 34482000000 | 34482000000 | 30103000000 | 30103000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 6658000000 | 6658000000 | 7245000000 | 7245000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1352 tags across all 129 R pages, face and notes) of 0002041610-26-000011; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | -5269000000 | -5269000000 | -451000000 | -451000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -860000000 | 860000000 | -920000000 | 920000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Earnings (loss) from continuing operations before income taxes and equity in loss of investee companies | -6177000000 | -6177000000 | -1253000000 | -1253000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Benefit from income taxes | 305000000 | -305000000 | 361000000 | -361000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net loss attributable to Parent | -6190000000 | -6190000000 | -608000000 | -608000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net loss (in dollars per share) | -9.34 | -9.34 | -1.02 | -1.02 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net loss (in dollars per share) | -9.34 | -9.34 | -1.02 | -1.02 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 664000000 | 664000000 | 652000000 | 652000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 664000000 | 664000000 | 652000000 | 652000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R3.htm period ..2024-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 3274000000 | 3274000000 | 2661000000 | 2661000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables, net | 6615000000 | 6615000000 | 6920000000 | 6920000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| inventory | mapped | psky:FilmCapitalizedCostCurrent | R5.htm | Programming and other inventory | 1461000000 |  | 1429000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 13320000000 | 13320000000 | 12542000000 | 12542000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 2195000000 | 2195000000 | 1566000000 | 1566000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 1600000000 | 1600000000 | 10508000000 | 10508000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 43342000000 | 43342000000 | 46172000000 | 46172000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 906000000 | 906000000 | 953000000 | 953000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 10599000000 | 10599000000 | 9631000000 | 9631000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R89.htm | VARIABLE INTEREST ENTITIES (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R89.htm 'VARIABLE INTEREST ENTITIES (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Parent stockholders’ equity | 11693000000 | 11693000000 | 16320000000 | 16320000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash flow provided by operating activities | 752000000 | 752000000 | 475000000 | 475000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash flow (used for) provided by investing activities | 12000000 | 12000000 | 942000000 | 942000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash flow used for financing activities | -507000000 | -507000000 | -1841000000 | -1841000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -263000000 | 263000000 | -328000000 | 328000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 392000000 | 392000000 | 418000000 | 418000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 245000000 | 245000000 | 177000000 | 177000000 | Y | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid on common stock | -139000000 | 139000000 | -389000000 | 389000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002041610-26-000011 R7.htm period ..2024-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1352 tags across all 129 R pages, face and notes) of 0002041610-26-000011; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R126.htm | SUPPLEMENTAL FINANCIAL INFORMATION - Schedule of Supplemental Cash Flow Information (Details) |  | 833000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R126.htm 'SUPPLEMENTAL FINANCIAL INFORMATION - Schedule of Supplemental Cash Flow Informat' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R104.htm | INCOME TAXES - Schedule of Income Taxes Paid (Details) |  | 184000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R104.htm 'INCOME TAXES - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Debt + Long-term debt | 13658000000 | 13658000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R91.htm | STOCKHOLDERS’ EQUITY - Schedule of Paramount Skydance Issued And Outstanding Stock After Completion Of Transactions (Det |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'STOCKHOLDERS’ EQUITY - Schedule of Paramount Skydance Issued And Outstanding Sto' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read

## Mismatches (printed vs API)
- inventory: API missing (psky:FilmCapitalizedCostCurrent)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 34482000000 vs printed 34482000000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value -5269000000 vs printed -5269000000 |
| cash_and_equivalents | mapped-sample | agree | page value 3274000000 vs printed 3274000000 |
| inventory | mapped-sample | agree | page value 1461000000 vs printed 1461000000 |
| total_liabilities | NOTE | agree | value 311000000 read off its own R page (no companyfacts fact to compare) |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | DISAGREE | page value 296000000 vs API 833000000 |
| cash_paid_for_income_taxes | NOTE | DISAGREE | page value 70000000 vs API 184000000 |
| total_debt | component sum | agree | page value 13658000000 vs printed 13658000000 |
| shares_outstanding | NOTE | agree | fixed to not_presented: no period-end value on any presenting page |
