# ELAN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001739104-26-000012 (CIK 0001739104, filed 2026-02-24): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001739104-24-000009 (CIK 0001739104, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001739104-19-000006 (CIK 0001739104, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001739104.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 4715000000 | 4715000000 | 4439000000 | 4439000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 2122000000 | 2122000000 | 2003000000 | 2003000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross Profit | 2593000000 | 2593000000 | 2436000000 | 2436000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (978 tags across all 111 R pages, face and notes) of 0001739104-26-000012; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Marketing, selling and administrative | 1430000000 | 1430000000 | 1314000000 | 1314000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 368000000 | 368000000 | 344000000 | 344000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (978 tags across all 111 R pages, face and notes) of 0001739104-26-000012; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R3.htm | Interest expense, net of capitalized interest | 220000000 | 220000000 | 235000000 | 235000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | (Loss) income before income taxes | -224000000 | -224000000 | 488000000 | 488000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 8000000 | 8000000 | 150000000 | 150000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net (loss) income | -232000000 | -232000000 | 338000000 | 338000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (usd per share) | -0.47 | -0.47 | 0.68 | 0.68 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (usd per share) | -0.47 | -0.47 | 0.68 | 0.68 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 496400000 | 496400000 | 494000000 | 494000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 496400000 | 496400000 | 497300000 | 497300000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 545000000 | 545000000 | 468000000 | 468000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 873000000 | 873000000 | 805000000 | 805000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1737000000 | 1737000000 | 1574000000 | 1574000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 3458000000 | 3458000000 | 3215000000 | 3215000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property and equipment, net | 1409000000 | 1409000000 | 993000000 | 993000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 4779000000 | 4779000000 | 4414000000 | 4414000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 13358000000 | 13358000000 | 12614000000 | 12614000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 368000000 | 368000000 | 296000000 | 296000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1597000000 | 1597000000 | 1315000000 | 1315000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 6811000000 | 6811000000 | 6518000000 | 6518000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total equity | 6547000000 | 6547000000 | 6096000000 | 6096000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net Cash Provided by Operating Activities | 560000000 | 560000000 | 541000000 | 541000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net Cash (Used for) Provided by Investing Activities | -279000000 | -279000000 | 1158000000 | 1158000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net Cash Used for Financing Activities | -275000000 | -275000000 | -1492000000 | -1492000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Net purchases of property and equipment and software | -276000000 | 276000000 | -147000000 | 147000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001739104-26-000012 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 680000000 | 680000000 | 662000000 | 662000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 68000000 | 68000000 | 55000000 | 55000000 | Y | FILING-CHECKED | accn 0001739104-26-000012 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (978 tags across all 111 R pages, face and notes) of 0001739104-26-000012; no face row matched |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (978 tags across all 111 R pages, face and notes) of 0001739104-26-000012; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R65.htm | Debt and Finance Lease Liability - Schedule of Cash Payments of Income Taxes (Details) |  | 206000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Debt and Finance Lease Liability - Schedule of Cash Payments of Income Taxes (De' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R91.htm | Income Taxes - Narrative (Details) |  | 225000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt and finance lease liability + Long-term debt and finance lease liability | 4017000000 | 4017000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock outstanding (in shares) | 496975154 | 496975154 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001739104-24-000009 R3.htm prints 'Interest expense, net of capitalized interest' on us-gaap:InterestExpense = 277000000 (FILING-CHECKED)
- basic_eps: era 10-K 0001739104-19-000006 R2.htm prints 'Basic and diluted (usd per share)' on us-gaap:EarningsPerShareBasicAndDiluted = 0.28 (FILING-CHECKED)
- diluted_eps: era 10-K 0001739104-19-000006 R2.htm prints 'Basic and diluted (usd per share)' on us-gaap:EarningsPerShareBasicAndDiluted = 0.28 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 4715000000 vs printed 4715000000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| net_income | mapped-sample | agree | page value -232000000 vs printed -232000000 |
| cash_and_equivalents | mapped-sample | agree | page value 545000000 vs printed 545000000 |
| depreciation_and_amortization | mapped-sample | agree | page value 680000000 vs printed 680000000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 206000000 vs API 206000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 225000000 vs API 225000000 |
| total_debt | component sum | agree | page value 4017000000 vs printed 4017000000 |
