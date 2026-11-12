# OSCR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001568651-26-000011 (CIK 0001568651, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001568651-24-000006 (CIK 0001568651, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001568651-22-000011 (CIK 0001568651, era filing): COVER R1.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001568651.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenue | 11701427000 | 11701427000 | 9177564000 | 9177564000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| operating_expenses | mapped | us-gaap:BenefitsLossesAndExpenses | R3.htm | Total operating expenses | 12097784000 | 12097784000 | 9120299000 | 9120299000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general, and administrative | 2049867000 | 2049867000 | 1755565000 | 1755565000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Earnings (loss) from operations | -396357000 | -396357000 | 57265000 | 57265000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 17601000 | 17601000 | 23734000 | 23734000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings (loss) before income taxes | -437297000 | -437297000 | 33426000 | 33426000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 5606000 | 5606000 | 7305000 | 7305000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (loss) attributable to Oscar Health, Inc. | -443151000 | -443151000 | 25432000 | 25432000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | -1.69 | -1.69 | 0.11 | 0.11 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | -1.69 | -1.69 | 0.1 | 0.1 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 262388000 | 262388000 | 240386000 | 240386000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 262388000 | 262388000 | 265853000 | 265853000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 2774151000 | 2774151000 | 1527186000 | 1527186000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 4613404000 | 4613404000 | 2845174000 | 2845174000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, equipment, and capitalized software, net | 88350000 | 88350000 | 66793000 | 66793000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| goodwill | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 6325411000 | 6325411000 | 4840496000 | 4840496000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and other liabilities | 649720000 | 649720000 | 432428000 | 432428000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 4862587000 | 4862587000 | 3463234000 | 3463234000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 5344676000 | 5344676000 | 3824071000 | 3824071000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Oscar Health, Inc. stockholders’ equity | 977648000 | 977648000 | 1013586000 | 1013586000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash (used in) provided by operating activities | 1094854000 | 1094854000 | 978193000 | 978193000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash (used in) provided by investing activities | -241060000 | -241060000 | -1387434000 | -1387434000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 399211000 | 399211000 | 68388000 | 68388000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Purchase of property, equipment and capitalized software | -36372000 | 36372000 | -27897000 | 27897000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization expense | 28892000 | 28892000 | 32145000 | 32145000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 87654000 | 87654000 | 109824000 | 109824000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (838 tags across all 97 R pages, face and notes) of 0001568651-26-000011; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest payments | 12783000 | 12783000 | 33691000 | 33691000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income tax payments | 17516000 | 17516000 | 674000 | 674000 | Y | FILING-CHECKED | accn 0001568651-26-000011 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | Long-term debt | 430095000 | 430095000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 297689000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- sga_expense: era 10-K 0001568651-24-000006 R5.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 339716000 (FILING-CHECKED)
- interest_expense: era 10-K 0001568651-24-000006 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = 24603000 (FILING-CHECKED)
- cash_and_equivalents: 10-K 0001568651-22-000011 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | mapped-sample | agree | page value -437297000 vs printed -437297000 |
| income_tax_expense | mapped-sample | agree | page value 5606000 vs printed 5606000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | mapped-sample | agree | page value 5344676000 vs printed 5344676000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 430095000 vs printed 430095000 |
| shares_outstanding | component sum | agree | page value 297689000 vs printed 297689000 |
