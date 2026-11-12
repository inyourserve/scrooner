# FIG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-009228 (CIK 0001579878, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R9.htm
- 10-K 0001628280-26-009228 (CIK 0001579878, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R9.htm
- companyfacts CIK0001579878.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 1055788000 | 1055788000 | 749011000 | 749011000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 185527000 | 185527000 | 87514000 | 87514000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 870261000 | 870261000 | 661497000 | 661497000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 2160718000 | 2160718000 | 1538930000 | 1538930000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 555510000 | 555510000 | 315734000 | 315734000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 1029700000 | 1029700000 | 751120000 | 751120000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -1290457000 | -1290457000 | -877433000 | -877433000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R53.htm | Cash, Cash Equivalents, and Marketable Securities - Narrative (Details) |  | 62200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R53.htm 'Cash, Cash Equivalents, and Marketable Securities - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before income taxes | -1225642000 | -1225642000 | -793071000 | -793071000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | 24821000 | 24821000 | -60951000 | -60951000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) | -1250463000 | -1250463000 | -732120000 | -732120000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income (loss) per share, basic (in usd per share) | -3.71 | -3.71 | -3.74 | -3.74 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income (loss) per share, diluted (in usd per share) | -3.71 | -3.71 | -3.74 | -3.74 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted-average shares outstanding used in computing net income (loss) per share attributable to common stockholders, b | 337044000 | 337044000 | 195612000 | 195612000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted-average shares outstanding used in computing net income (loss) per share attributable to common stockholders, d | 337044000 | 337044000 | 195612000 | 195612000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 403469000 | 403469000 | 486954000 | 486954000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 247915000 | 247915000 | 131315000 | 131315000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (916 tags across all 96 R pages, face and notes) of 0001628280-26-009228; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2004700000 | 2004700000 | 1638025000 | 1638025000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 19996000 | 19996000 | 15017000 | 15017000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 101396000 | 101396000 | 11398000 | 11398000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2348207000 | 2348207000 | 1793148000 | 1793148000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 4502000 | 4502000 | 4163000 | 4163000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 776106000 | 776106000 | 446959000 | 446959000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 837566000 | 837566000 | 469095000 | 469095000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 1510641000 | 1510641000 | 1324053000 | 1324053000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 250681000 | 250681000 | -61717000 | -61717000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -371413000 | -371413000 | -784257000 | -784257000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by financing activities | 43338000 | 43338000 | 62450000 | 62450000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -4444000 | 4444000 | -1977000 | 1977000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 15594000 | 15594000 | 7691000 | 7691000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation, net of amounts capitalized | 1364133000 | 1364133000 | 947553000 | 947553000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (916 tags across all 96 R pages, face and notes) of 0001628280-26-009228; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common stock | 0 | 0 | -861000 | 861000 | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (916 tags across all 96 R pages, face and notes) of 0001628280-26-009228; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Total cash paid during the period for income taxes, net of refunds | 28639000 | 28639000 |  |  | Y | FILING-CHECKED | accn 0001628280-26-009228 R9.htm period ..2025-12-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (916 tags across all 96 R pages, face and notes) of 0001628280-26-009228; no face row matched |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 513043000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0001628280-26-009228 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 403469000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001628280-26-009228 R9.htm prints 'Total cash paid during the period for income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 28639000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| sga_expense | component sum | agree | page value 1131018000 vs printed 1131018000 |
| research_and_development | mapped-sample | agree | page value 1029700000 vs printed 1029700000 |
| interest_expense | NOTE | agree | page value 62200000 vs API 62200000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | mapped-sample | agree | page value 4502000 vs printed 4502000 |
| depreciation_and_amortization | mapped-sample | agree | page value 15594000 vs printed 15594000 |
| sbc | mapped-sample | agree | page value 1364133000 vs printed 1364133000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | component sum | agree | page value 513043000 vs printed 513043000 |
