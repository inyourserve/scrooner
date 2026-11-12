# SMMT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001599298-26-000015 (CIK 0001599298, filed 2026-02-23): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0001599298-23-000034 (CIK 0001599298, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0001599298-21-000011 (CIK 0001599298, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0001599298.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, RegulatedAndUnregulatedOperatingRevenue, RegulatedOperatingRevenue in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1094424000 | 1094424000 | 225998000 | 225998000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 556750000 | 556750000 | 60214000 | 60214000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost | R5.htm | Research and development | 537674000 | 537674000 | 150777000 | 150777000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | 0 | 0 | -8686000 | 8686000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R45.htm | Income Tax - Components of Loss Before Income Taxes (Details) |  | -1079586000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R45.htm 'Income Tax - Components of Loss Before Income Taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R48.htm | Income Tax - Reconciliation of the Effective Income Tax Rate to Statutory Rate (Details) |  | 0 |  |  |  | FILING-CHECKED | not on the face statement; shown in R48.htm 'Income Tax - Reconciliation of the Effective Income Tax Rate to Statutory Rate (' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -1079586000 | -1079586000 | -221315000 | -221315000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | -1.44 | -1.44 | -0.31 | -0.31 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | -1.44 | -1.44 | -0.31 | -0.31 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 747702265 | 747702265 | 718541896 | 718541896 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 747702265 | 747702265 | 718541896 | 718541896 | Y | FILING-CHECKED | accn 0001599298-26-000015 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 225266000 | 225266000 | 104862000 | 104862000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 720301000 | 720301000 | 423750000 | 423750000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1059000 | 1059000 | 254000 | 254000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2001000 | 2001000 | 1864000 | 1864000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 751182000 | 751182000 | 435560000 | 435560000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 20292000 | 20292000 | 4636000 | 4636000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 72988000 | 72988000 | 41729000 | 41729000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 92322000 | 92322000 | 46812000 | 46812000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 658860000 | 658860000 | 388748000 | 388748000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash used in operating activities | -322930000 | -322930000 | -142106000 | -142106000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -174310000 | -174310000 | -205341000 | -205341000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 617533000 | 617533000 | 381227000 | 381227000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property and equipment | -657000 | 657000 | -139000 | 139000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R8.htm | Depreciation | 146000 | 146000 | 89000 | 89000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 732420000 | 732420000 | 50981000 | 50981000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (672 tags across all 69 R pages, face and notes) of 0001599298-26-000015; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest on related party promissory note | 0 | 0 | 8806000 | 8806000 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0001599298-26-000015 R8.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:NotesPayable | R60.htm | Promissory Note Payable to Related Parties (Details) |  |  |  |  |  | FILING-CHECKED | only component tag(s) NotesPayable in the filing (R60.htm 'Promissory Note Payable to Related Parties (Details)'); the data point itself is not reported |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 775371200 | 775371200 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- research_and_development: era 10-K 0001599298-23-000034 R5.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 51999000 (FILING-CHECKED)
- interest_expense: era 10-K 0001599298-23-000034 R5.htm read; no row matched (auto)
- cash_and_equivalents: era 10-K 0001599298-21-000011 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 66417000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | NOTE | agree | page value -1079586000 vs API -1079586000 |
| income_tax_expense | NOTE | agree | page value 0 vs API 0 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | mapped-sample | agree | page value 20292000 vs printed 20292000 |
| cash_flow_financing | mapped-sample | agree | page value 617533000 vs printed 617533000 |
| capex | mapped-sample | agree | page value -657000 vs printed -657000 |
| depreciation_and_amortization | component sum | agree | page value 146000 vs printed 146000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | component element on R60.htm |
