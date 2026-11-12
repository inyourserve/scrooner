# ASTS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001780312-26-000006 (CIK 0001780312, filed 2026-03-02): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001213900-21-012253 (CIK 0001780312, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R8.htm
- 10-K 0000950170-22-005212 (CIK 0001780312, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, IS R5.htm, CF R8.htm
- companyfacts CIK0001780312.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R4.htm | Revenues | 70918000 | 70918000 | 4418000 | 4418000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Cost of revenues | 33032000 |  | 0 |  | API missing | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1051 tags across all 76 R pages, face and notes) of 0001780312-26-000006; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Total operating expenses | 358631000 | 358631000 | 247180000 | 247180000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative costs | 101679000 | 101679000 | 61566000 | 61566000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development costs | 28115000 | 28115000 | 28783000 | 28783000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1051 tags across all 76 R pages, face and notes) of 0001780312-26-000006; no face row matched |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R4.htm | Other (expense) income, net | -114408000 | -114408000 | 1867000 | 1867000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Loss before income tax expense | -457113000 | -457113000 | -525002000 | -525002000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | -3898000 | 3898000 | -1328000 | 1328000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net loss attributable to common stockholders | -341940000 | -341940000 | -300083000 | -300083000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | -1.34 |  | -1.94 |  | API missing | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | -1.34 |  | -1.94 |  | API missing | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted-average number of shares outstanding - basic | 255982592 | 255982592 | 154501344 | 154501344 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted-average number of shares outstanding - diluted | 255982592 | 255982592 | 154501344 | 154501344 | Y | FILING-CHECKED | accn 0001780312-26-000006 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 2335683000 | 2335683000 | 564988000 | 564988000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net (includes related party accounts receivable of $2,091 and $0 at December 31, 2025 and 2024, res | 37726000 | 37726000 | 1400000 | 1400000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventory | 12007000 | 12007000 | 1062000 | 1062000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2458512000 | 2458512000 | 600246000 | 600246000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 1398761000 | 1398761000 | 337669000 | 337669000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| goodwill | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1051 tags across all 76 R pages, face and notes) of 0001780312-26-000006; no face row matched |
| total_assets | mapped | us-gaap:Assets | R2.htm | TOTAL ASSETS | 5014387000 | 5014387000 | 954561000 | 954561000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 46763000 | 46763000 | 17004000 | 17004000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 150344000 | 150344000 | 75942000 | 75942000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 2622062000 | 2622062000 | 285415000 | 285415000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R2.htm | Total stockholders' equity | 2392325000 | 2392325000 | 669146000 | 669146000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001780312-26-000006 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash used in operating activities | -71517000 | -71517000 | -126143000 | -126143000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -1541138000 | -1541138000 | -174127000 | -174127000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by financing activities | 3827488000 | 3827488000 | 779967000 | 779967000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchase of property and equipment | -1064741000 | 1064741000 | -174127000 | 174127000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 51111000 | 51111000 | 63340000 | 63340000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 47490000 | 47490000 | 32039000 | 32039000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1051 tags across all 76 R pages, face and notes) of 0001780312-26-000006; no face row matched |
| share_buybacks | mapped | us-gaap:ProceedsFromConvertibleDebt | R9.htm | Proceeds from share issuances to repurchase 2032 4.25% Convertible Notes | 1010887000 | 1010887000 | 0 | 0 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 7855000 | 7855000 | 11988000 | 11988000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes, net | 6798000 | 6798000 | 1669000 | 1669000 | Y | FILING-CHECKED | accn 0001780312-26-000006 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R2.htm | Current portion of long-term debt + Long-term debt, net | 2219582000 | 2219582000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R3.htm | Common Stock, Shares, Outstanding | 374840281 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- accounts_payable: era 10-K 0001213900-21-012253 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 634286 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0000950170-22-005212 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfRevenue)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value -114408000 vs printed -114408000 |
| weighted_basic_shares | mapped-sample | agree | page value 255982592 vs printed 255982592 |
| ppe_net | mapped-sample | agree | page value 1398761000 vs printed 1398761000 |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_assets | mapped-sample | agree | page value 5014387000 vs printed 5014387000 |
| sbc | mapped-sample | agree | page value 47490000 vs printed 47490000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 2219582000 vs printed 2219582000 |
| shares_outstanding | component sum | agree | page value 374840281 vs printed 374840281 |
