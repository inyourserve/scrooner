# RYAN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001849253-26-000006 (CIK 0001849253, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000950170-24-021657 (CIK 0001849253, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000950170-23-005335 (CIK 0001849253, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001849253.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenue | 3051126000 | 3051126000 | 2515710000 | 2515710000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1097 tags across all 107 R pages, face and notes) of 0001849253-26-000006; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1097 tags across all 107 R pages, face and notes) of 0001849253-26-000006; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 2557486000 | 2557486000 | 2087898000 | 2087898000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 453452000 | 453452000 | 352050000 | 352050000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1097 tags across all 107 R pages, face and notes) of 0001849253-26-000006; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | OPERATING INCOME | 493640000 | 493640000 | 427812000 | 427812000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest expense, net | 222384000 | -222384000 | 158448000 | -158448000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME BEFORE INCOME TAXES | 293184000 | 293184000 | 272554000 | 272554000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 79027000 | 79027000 | 42641000 | 42641000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME ATTRIBUTABLE TO RYAN SPECIALTY HOLDINGS, INC. | 63399000 | 63399000 | 94665000 | 94665000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in USD per share) | 0.5 |  | 0.78 |  | API missing | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in USD per share) | 0.47 |  | 0.71 |  | API missing | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 127266889 |  | 120781234 |  | API missing | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 138246414 |  | 132891487 |  | API missing | FILING-CHECKED | accn 0001849253-26-000006 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 158322000 | 158322000 | 540203000 | 540203000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Commissions and fees receivable – net | 488951000 | 488951000 | 389758000 | 389758000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1097 tags across all 107 R pages, face and notes) of 0001849253-26-000006; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 5060180000 | 5060180000 | 4788858000 | 4788858000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment – net | 69461000 | 69461000 | 50209000 | 50209000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 3225021000 | 3225021000 | 2646676000 | 2646676000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 10564171000 | 10564171000 | 9649918000 | 9649918000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued liabilities | 284403000 | 284403000 | 249200000 | 249200000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 5188748000 | 5188748000 | 4549088000 | 4549088000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | TOTAL LIABILITIES | 9310120000 | 9310120000 | 8551633000 | 8551633000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity attributable to Ryan Specialty Holdings, Inc. | 648073000 | 648073000 | 627662000 | 627662000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Total cash flows provided by operating activities | 643667000 | 643667000 | 514868000 | 514868000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Total cash flows used in investing activities | -834013000 | -834013000 | -1755738000 | -1755738000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Total cash flows provided by (used in) financing activities | 78116000 | 78116000 | 1166857000 | 1166857000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Asset acquisitions | -3014000 | 3014000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation | 13089000 | 13089000 | 9785000 | 9785000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Non-cash equity-based compensation | 69451000 | 69451000 | 78995000 | 78995000 | Y | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Class A common stock dividends and Dividend Equivalents paid | -62339000 | 62339000 | -80236000 | 80236000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001849253-26-000006 R7.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1097 tags across all 107 R pages, face and notes) of 0001849253-26-000006; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R103.htm | Supplemental Financial Information - Schedule of Supplemental Cash Flow Information (Details) |  | 196041000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R103.htm 'Supplemental Financial Information - Schedule of Supplemental Cash Flow Informat' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R95.htm | Income Taxes - Schedule of Cash Paid for Income Taxes, Net of Refunds (Details) |  | 14344000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R95.htm 'Income Taxes - Schedule of Cash Paid for Income Taxes, Net of Refunds (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt and current portion of long-term debt + Long-term debt | 3351649000 | 3351649000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 264112311 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0000950170-24-021657 R2.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 119507000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000950170-23-005335 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashEquivalentsAtCarryingValue = 992723000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0000950170-23-005335 R6.htm read; no row matched (auto)

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: API missing (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value 222384000 vs printed 222384000 |
| basic_eps | mapped-sample | agree | page value 0.5 vs printed 0.5 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 69461000 vs printed 69461000 |
| stockholders_equity | mapped-sample | agree | page value 648073000 vs printed 648073000 |
| depreciation_and_amortization | component sum | agree | page value 13089000 vs printed 13089000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 196041000 vs API 196041000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 14344000 vs API 14344000 |
| total_debt | component sum | agree | page value 3351649000 vs printed 3351649000 |
| shares_outstanding | component sum | agree | page value 264112311 vs printed 264112311 |
