# CART document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001579091-26-000018 (CIK 0001579091, filed 2026-02-26): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001579091-24-000027 (CIK 0001579091, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001579091-25-000015 (CIK 0001579091, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001579091.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 3742000000 | 3742000000 | 3378000000 | 3378000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenue | 984000000 | 984000000 | 836000000 | 836000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2758000000 | 2758000000 | 2542000000 | 2542000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R84.htm | Related Party Transactions (Details) |  | 2259000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'Related Party Transactions (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 482000000 | 482000000 | 363000000 | 363000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 650000000 | 650000000 | 604000000 | 604000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income (loss) from operations | 498000000 | 498000000 | 489000000 | 489000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income | 57000000 | 57000000 | 66000000 | 66000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before provision for (benefit from) income taxes | 556000000 | 556000000 | 552000000 | 552000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | 109000000 | 109000000 | 95000000 | 95000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) | 447000000 | 447000000 | 457000000 | 457000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.68 | 1.68 | 1.69 | 1.69 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.6 | 1.6 | 1.58 | 1.58 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 261353000 | 261353000 | 264640000 | 264640000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 279621000 | 279621000 | 289158000 | 289158000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 637000000 | 637000000 | 1278000000 | 1278000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance of $4 and $3, respectively | 1127000000 | 1127000000 | 1014000000 | 1014000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (827 tags across all 88 R pages, face and notes) of 0001579091-26-000018; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2199000000 | 2199000000 | 2697000000 | 2697000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 218000000 | 218000000 | 200000000 | 200000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 393000000 | 393000000 | 317000000 | 317000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3687000000 | 3687000000 | 4115000000 | 4115000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 70000000 | 70000000 | 80000000 | 80000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 917000000 | 917000000 | 798000000 | 798000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 974000000 | 974000000 | 836000000 | 836000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 2518000000 | 2518000000 | 3093000000 | 3093000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 971000000 | 971000000 | 687000000 | 687000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -208000000 | -208000000 | -107000000 | -107000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1391000000 | -1391000000 | -1413000000 | -1413000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment, including capitalized internal-use software | -61000000 | 61000000 | -64000000 | 64000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization expense | 91000000 | 91000000 | 56000000 | 56000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 352000000 | 352000000 | 300000000 | 300000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (827 tags across all 88 R pages, face and notes) of 0001579091-26-000018; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -1386000000 | 1386000000 | -1402000000 | 1402000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (827 tags across all 88 R pages, face and notes) of 0001579091-26-000018; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash paid for income taxes, net of tax refunds | 43000000 | 43000000 | 13000000 | 13000000 | Y | FILING-CHECKED | accn 0001579091-26-000018 R9.htm period ..2025-12-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (827 tags across all 88 R pages, face and notes) of 0001579091-26-000018; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares, outstanding (in shares) | 242867000 | 242867000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0001579091-24-000027 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2137000000 (FILING-CHECKED)
- sbc: era 10-K 0001579091-25-000015 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 300000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | NOTE | agree | page value 2259000000 vs API 2259000000 |
| operating_income | mapped-sample | agree | page value 498000000 vs printed 498000000 |
| interest_expense | combined | agree | page value 57000000 vs printed 57000000 |
| diluted_eps | mapped-sample | agree | page value 1.6 vs printed 1.6 |
| cash_and_equivalents | mapped-sample | agree | page value 637000000 vs printed 637000000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_assets | mapped-sample | agree | page value 3687000000 vs printed 3687000000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
