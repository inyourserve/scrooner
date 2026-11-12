# FROG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-051382 (CIK 0001800667, filed 2026-02-13): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000950170-22-001123 (CIK 0001800667, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001193125-21-041470 (CIK 0001800667, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001800667.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Total subscription revenue | 531840000 | 531840000 | 428488000 | 428488000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Total cost of revenue—subscription | 123453000 | 123453000 | 98300000 | 98300000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profit | 408387000 | 408387000 | 330188000 | 330188000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Total operating expenses | 500240000 | 500240000 | 421286000 | 421286000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 81219000 | 81219000 | 70021000 | 70021000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 195089000 | 195089000 | 160864000 | 160864000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating loss | -91853000 | -91853000 | -91098000 | -91098000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (863 tags across all 99 R pages, face and notes) of 0001193125-26-051382; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Loss before income taxes | -66037000 | -66037000 | -65820000 | -65820000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | 5782000 | 5782000 | 3416000 | 3416000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net loss | -71819000 | -71819000 | -69236000 | -69236000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net loss per share, basic | -0.62 | -0.62 | -0.63 | -0.63 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net loss per share, diluted | -0.62 | -0.62 | -0.63 | -0.63 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted-average shares used in computing net loss per share, basic | 116200900 | 116200900 | 109691100 | 109691100 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted-average shares used in computing net loss per share, diluted | 116200900 | 116200900 | 109691100 | 109691100 | Y | FILING-CHECKED | accn 0001193125-26-051382 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 75840000 | 75840000 | 49869000 | 49869000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net | 119948000 | 119948000 | 90712000 | 90712000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (863 tags across all 99 R pages, face and notes) of 0001193125-26-051382; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 873011000 | 873011000 | 649227000 | 649227000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 5536000 | 5536000 | 5668000 | 5668000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 371512000 | 371512000 | 371512000 | 371512000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 1341377000 | 1341377000 | 1129906000 | 1129906000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 14168000 | 14168000 | 10649000 | 10649000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 407522000 | 407522000 | 317515000 | 317515000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 453930000 | 453930000 | 356380000 | 356380000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total shareholders' equity | 887447000 | 887447000 | 773526000 | 773526000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 145729000 | 145729000 | 110924000 | 110924000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -152268000 | -152268000 | -165356000 | -165356000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by financing activities | 31210000 | 31210000 | 21231000 | 21231000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -3460000 | 3460000 | -3143000 | 3143000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051382 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 24503000 | 24503000 | 21460000 | 21460000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 156657000 | 156657000 | 131106000 | 131106000 | Y | FILING-CHECKED | accn 0001193125-26-051382 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (863 tags across all 99 R pages, face and notes) of 0001193125-26-051382; no face row matched |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (863 tags across all 99 R pages, face and notes) of 0001193125-26-051382; no face row matched |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (863 tags across all 99 R pages, face and notes) of 0001193125-26-051382; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R92.htm | Income Taxes - Summary of Cash Paid for Income Taxes, Net of Refunds (Details) |  | 7944000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Income Taxes - Summary of Cash Paid for Income Taxes, Net of Refunds (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (863 tags across all 99 R pages, face and notes) of 0001193125-26-051382; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock Outstanding | 119615355 | 119615355 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- basic_eps: era 10-K 0000950170-22-001123 R4.htm prints 'Net loss per share attributable to ordinary shareholders, basic and diluted' on us-gaap:EarningsPerShareBasicAndDiluted = -0.68 (FILING-CHECKED)
- diluted_eps: era 10-K 0000950170-22-001123 R4.htm prints 'Net loss per share attributable to ordinary shareholders, basic and diluted' on us-gaap:EarningsPerShareBasicAndDiluted = -0.68 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001193125-21-041470 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashEquivalentsAtCarryingValue = 164461000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | mapped-sample | agree | page value 500240000 vs printed 500240000 |
| sga_expense | component sum | agree | page value 305151000 vs printed 305151000 |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | mapped-sample | agree | page value -66037000 vs printed -66037000 |
| net_income | mapped-sample | agree | page value -71819000 vs printed -71819000 |
| cash_and_equivalents | mapped-sample | agree | page value 75840000 vs printed 75840000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 7944000 vs API 7944000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
