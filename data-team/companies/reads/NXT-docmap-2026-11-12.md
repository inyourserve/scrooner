# NXT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001852131-26-000017 (CIK 0001852131, filed 2026-05-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001628280-24-025460 (CIK 0001852131, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001852131-26-000017 (CIK 0001852131, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001852131.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenue | 3559390000 | 3559390000 | 2959197000 | 2959197000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of sales | 2399295000 | 2399295000 | 1950372000 | 1950372000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1160095000 | 1160095000 | 1008825000 | 1008825000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense | R5.htm | Selling, general and administrative expenses + Research and development | 462829000 | 462829000 | 369713000 | 369713000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 341920000 | 341920000 | 290321000 | 290321000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 120909000 | 120909000 | 79392000 | 79392000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 697266000 | 697266000 | 639112000 | 639112000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense | 2623000 | -2623000 | 13096000 | -13096000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 713826000 | 713826000 | 648016000 | 648016000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 127943000 | 127943000 | 130770000 | 130770000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Nextpower Inc. | 585883000 | 585883000 | 509168000 | 509168000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in USD per share) | 3.96 | 3.96 | 3.55 | 3.55 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in USD per share) | 3.84 | 3.84 | 3.47 | 3.47 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 147976256 | 147976256 | 143539344 | 143539344 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 152710033 | 152710033 | 149275950 | 149275950 | Y | FILING-CHECKED | accn 0001852131-26-000017 R5.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1094976000 | 1094976000 | 766103000 | 766103000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance of $2,078 and $1,472, respectively | 417043000 | 417043000 | 472462000 | 472462000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 262276000 | 262276000 | 209432000 | 209432000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2846556000 | 2846556000 | 2157986000 | 2157986000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 78356000 | 78356000 | 60395000 | 60395000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 488950000 | 488950000 | 371018000 | 371018000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4073212000 | 4073212000 | 3192516000 | 3192516000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 533490000 | 533490000 | 585299000 | 585299000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1163862000 | 1163862000 | 1033512000 | 1033512000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1738815000 | 1738815000 | 1564386000 | 1564386000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 2334397000 | 2334397000 | 1628130000 | 1628130000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R3.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 562911000 | 562911000 | 655794000 | 655794000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -186878000 | -186878000 | -186096000 | -186096000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -47160000 | -47160000 | -177649000 | -177649000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -49277000 | 49277000 | -33921000 | 33921000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization of intangible assets | 30602000 | 30602000 | 13407000 | 13407000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 120298000 | 120298000 | 118880000 | 118880000 | Y | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (877 tags across all 93 R pages, face and notes) of 0001852131-26-000017; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -395000 | 395000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001852131-26-000017 R8.htm period ..2026-03-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R74.htm | Supplemental cash flow disclosures (Details) |  | 0 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Supplemental cash flow disclosures (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R81.htm | Income taxes - Summary of Income Taxes Paid by Jurisdiction (Details) |  | 196158000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R81.htm 'Income taxes - Summary of Income Taxes Paid by Jurisdiction (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (877 tags across all 93 R pages, face and notes) of 0001852131-26-000017; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares, outstanding (in shares) | 149391483 |  |  |  | API missing | FILING-CHECKED | balance-sheet date 2026-03-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0001628280-24-025460 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 474054000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001852131-26-000017 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | mapped-sample | agree | page value 1160095000 vs printed 1160095000 |
| operating_expenses | component sum | agree | page value 462829000 vs printed 462829000 |
| interest_expense | combined | agree | page value 2623000 vs printed 2623000 |
| basic_eps | mapped-sample | agree | page value 3.96 vs printed 3.96 |
| diluted_eps | mapped-sample | agree | page value 3.84 vs printed 3.84 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 0 vs API 0 |
| cash_paid_for_income_taxes | NOTE | agree | page value 196158000 vs API 196158000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | mapped-sample | agree | page value 149391483 vs printed 149391483 |
