# BTSG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-079454 (CIK 0001865782, filed 2026-02-27): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0001865782.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Total revenues | 12910564000 | 12910564000 | 10072214000 | 10072214000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | btsg:CostOfGoods | R4.htm | Cost of goods | 10507431000 |  | 8008501000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profit | 1517777000 | 1517777000 | 1266427000 | 1266427000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general, and administrative expenses | 1222525000 | 1222525000 | 1158473000 | 1158473000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general, and administrative expenses | 1222525000 | 1222525000 | 1158473000 | 1158473000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1200 tags across all 103 R pages, face and notes) of 0001193125-26-079454; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 295252000 | 295252000 | 107954000 | 107954000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense, net | 157311000 | 157311000 | 190546000 | 190546000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income (loss) from continuing operations before income taxes | 137941000 | 137941000 | -95318000 | -95318000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense (benefit) | 33145000 | 33145000 | -26387000 | -26387000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income (loss) attributable to BrightSpring Health Services, Inc. and subsidiaries | 190666000 | 190666000 | -18062000 | -18062000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income (loss) per share | 0.94 | 0.94 | -0.09 | -0.09 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income (loss) per share | 0.87 | 0.87 | -0.09 | -0.09 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 202564000 | 202564000 | 192997000 | 192997000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 219774000 | 219774000 | 192997000 | 192997000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 88370000 | 88370000 | 60954000 | 60954000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net of allowance for credit losses | 989719000 | 989719000 | 902782000 | 902782000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories | 815180000 | 815180000 | 636561000 | 636561000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2894050000 | 2894050000 | 1893054000 | 1893054000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net of accumulated depreciation of $404,878 and $339,892 at December 31, 2025 and 2024, respecti | 204689000 | 204689000 | 180570000 | 180570000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 2545673000 | 2545673000 | 2363884000 | 2363884000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 6413311000 | 6413311000 | 5926140000 | 5926140000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Trade accounts payable | 1217946000 | 1217946000 | 923926000 | 923926000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 1849034000 | 1849034000 | 1428333000 | 1428333000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 4526945000 | 4526945000 | 4274555000 | 4274555000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total shareholders' equity | 1875065000 | 1875065000 | 1647855000 | 1647855000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 490169000 | 490169000 | 23774000 | 23774000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -305079000 | -305079000 | -140237000 | -140237000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash (used in) provided by financing activities | -157866000 | -157866000 | 164645000 | 164645000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment | -95484000 | 95484000 | -80913000 | 80913000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 164277000 | 164277000 | 204482000 | 204482000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based compensation | 70099000 | 70099000 | 69174000 | 69174000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1200 tags across all 103 R pages, face and notes) of 0001193125-26-079454; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of shares of common stock | -43173000 | 43173000 | -650000 | 650000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest, net | 183512000 | 183512000 | 211387000 | 211387000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes, net of refunds | 26970000 | 26970000 | 24953000 | 24953000 | Y | FILING-CHECKED | accn 0001193125-26-079454 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R2.htm | Current portion of long-term debt + Long-term debt, net of current portion | 2507544000 | 2507544000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common Stock, shares outstanding | 192124125 | 192124125 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read

## Mismatches (printed vs API)
- cost_of_revenue: API missing (btsg:CostOfGoods)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 1222525000 vs printed 1222525000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value 157311000 vs printed 157311000 |
| diluted_eps | mapped-sample | agree | page value 0.87 vs printed 0.87 |
| stockholders_equity | mapped-sample | agree | page value 1875065000 vs printed 1875065000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | mapped-sample | agree | page value -43173000 vs printed -43173000 |
| cash_paid_for_income_taxes | mapped-sample | agree | page value 26970000 vs printed 26970000 |
| total_debt | component sum | agree | page value 2507544000 vs printed 2507544000 |
