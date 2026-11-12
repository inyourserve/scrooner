# GNRC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001437749-26-004568 (CIK 0001474735, filed 2026-02-18): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- 10-K 0001437749-16-026187 (CIK 0001474735, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- 10-K 0001437749-18-003334 (CIK 0001474735, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- companyfacts CIK0001474735.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R62.htm | Note 7 - Segment Reporting - Net Sales by Products and Services (Details) |  | 4209147000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R62.htm 'Note 7 - Segment Reporting - Net Sales by Products and Services (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R63.htm | Note 7 - Segment Reporting - Segment Information (Details) |  | 2597410000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Note 7 - Segment Reporting - Segment Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| gross_profit | mapped | us-gaap:GrossProfit | R63.htm | Note 7 - Segment Reporting - Segment Information (Details) |  | 1611737000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Note 7 - Segment Reporting - Segment Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R63.htm | Note 7 - Segment Reporting - Segment Information (Details) |  | 1322546000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Note 7 - Segment Reporting - Segment Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | Consolidated Statements of Comprehensive Income |  | 422211000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R48.htm | Note 2 - Summary of Accounting Policies 1 (Details Textual) |  | 243470000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R48.htm 'Note 2 - Summary of Accounting Policies 1 (Details Textual)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Consolidated Statements of Comprehensive Income |  | 289191000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpense | R63.htm | Note 7 - Segment Reporting - Segment Information (Details) |  | 70697000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Note 7 - Segment Reporting - Segment Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R63.htm | Note 7 - Segment Reporting - Segment Information (Details) |  | 199060000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Note 7 - Segment Reporting - Segment Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R92.htm | Note 15 - Income Taxes - Provision for Income Taxes (Details) |  | 37706000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Note 15 - Income Taxes - Provision for Income Taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R90.htm | Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per Share (Details) |  | 159554000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per ' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R90.htm | Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per Share (Details) |  | 2.73 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per ' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R90.htm | Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per Share (Details) |  | 2.69 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per ' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R90.htm | Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per Share (Details) |  | 58523642 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per ' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R90.htm | Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per Share (Details) |  | 59275781 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Note 14 - Earnings Per Share - Reconciliation of Basic and Diluted Earnings Per ' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 341413000 | 341413000 | 281277000 | 281277000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, less allowance for credit losses of $34,504 and $35,465 as of December 31, 2025 and 2024, respectiv | 602739000 | 602739000 | 612107000 | 612107000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories | 1248867000 | 1248867000 | 1031647000 | 1031647000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2462478000 | 2462478000 | 2032170000 | 2032170000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property, Plant and Equipment, Net | 813605000 | 813605000 | 690023000 | 690023000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1467094000 | 1467094000 | 1436261000 | 1436261000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 5573679000 | 5573679000 | 5109331000 | 5109331000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 436583000 | 436583000 | 458693000 | 458693000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 1215346000 | 1215346000 | 1033152000 | 1033152000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 2934633000 | 2934633000 | 2611888000 | 2611888000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Stockholders’ equity attributable to Generac Holdings Inc. | 2632422000 | 2632422000 | 2494278000 | 2494278000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 437978000 | 437978000 |  | 741301000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -172904000 | -172904000 |  | -208712000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -212719000 | -212719000 |  | -448835000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Expenditures for property and equipment | -169850000 | 169850000 |  | 136733000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:Depreciation | R7.htm | Depreciation and finance lease amortization | 93328000 | 93328000 |  | 74025000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 49947000 | 49947000 |  | 49248000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to noncontrolling interest of subsidiary | -293000 | 293000 |  | 273000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Stock repurchases | -147917000 | 147917000 |  | 152743000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest | 75874000 | 75874000 |  | 89420000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes | 89415000 | 89415000 |  | 148828000 | Y | FILING-CHECKED | accn 0001437749-26-004568 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R2.htm | Short-term borrowings + Long-Term Debt and Lease Obligation, Current + Long-Term Debt and Lease Obligation | 1333066000 | 1333066000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (918 tags across all 104 R pages, face and notes) of 0001437749-26-004568; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0001437749-16-026187 statement not identified (auto)
- cost_of_revenue: 10-K 0001437749-16-026187 statement not identified (auto)
- gross_profit: 10-K 0001437749-16-026187 statement not identified (auto)
- operating_expenses: 10-K 0001437749-16-026187 statement not identified (auto)
- sga_expense: 10-K 0001437749-16-026187 statement not identified (auto)
- research_and_development: 10-K 0001437749-16-026187 statement not identified (auto)
- operating_income: 10-K 0001437749-16-026187 statement not identified (auto)
- interest_expense: 10-K 0001437749-16-026187 statement not identified (auto)
- income_before_tax: 10-K 0001437749-16-026187 statement not identified (auto)
- income_tax_expense: 10-K 0001437749-16-026187 statement not identified (auto)
- net_income: 10-K 0001437749-16-026187 statement not identified (auto)
- basic_eps: 10-K 0001437749-16-026187 statement not identified (auto)
- diluted_eps: 10-K 0001437749-16-026187 statement not identified (auto)
- weighted_basic_shares: 10-K 0001437749-16-026187 statement not identified (auto)
- weighted_diluted_shares: 10-K 0001437749-16-026187 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 115857000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Accounts receivable, less allowance for doubtful accounts of $2,494 at December ' on us-gaap:AccountsReceivableNetCurrent = 182185000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 325375000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 661372000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 184213000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 669719000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Total assets' on us-gaap:Assets = 1792816000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 108332000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 213224000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1326945000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001437749-16-026187 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 465871000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 188619000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -104328000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -154483000 (FILING-CHECKED)
- capex: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Expenditures for property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -30651000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001437749-16-026187 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 8241000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -1436000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Stock repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -99942000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Interest' on us-gaap:InterestPaid = 39524000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001437749-16-026187 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 6087000 (FILING-CHECKED)
- revenue: 10-K 0001437749-18-003334 statement not identified (auto)
- cost_of_revenue: 10-K 0001437749-18-003334 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 4209147000 vs API 4209147000 |
| cost_of_revenue | NOTE | agree | page value 2597410000 vs API 2597410000 |
| gross_profit | NOTE | agree | page value 1611737000 vs API 1611737000 |
| operating_expenses | NOTE | agree | page value 1322546000 vs API 1322546000 |
| sga_expense | component sum | agree | page value 977569000 vs printed 977569000 |
| research_and_development | NOTE | agree | page value 243470000 vs API 243470000 |
| interest_expense | NOTE | agree | page value -70697000 vs API 70697000 |
| income_before_tax | NOTE | agree | page value 199060000 vs API 199060000 |
| income_tax_expense | NOTE | agree | page value 37706000 vs API 37706000 |
| net_income | NOTE | agree | page value 159554000 vs API 159554000 |
| basic_eps | NOTE | agree | page value 2.73 vs API 2.73 |
| diluted_eps | NOTE | agree | page value 2.69 vs API 2.69 |
| weighted_basic_shares | NOTE | agree | page value 58523642 vs API 58523642 |
| weighted_diluted_shares | NOTE | agree | page value 59275781 vs API 59275781 |
| total_assets | mapped-sample | agree | page value 5573679000 vs printed 5573679000 |
| stockholders_equity | mapped-sample | agree | page value 2632422000 vs printed 2632422000 |
| cfo | mapped-sample | agree | page value 437978000 vs printed 437978000 |
| total_debt | component sum | agree | page value 1333066000 vs printed 1333066000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
