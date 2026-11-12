# IONQ document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-071562 (CIK 0001824920, filed 2026-02-25): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001193125-22-086738 (CIK 0001824920, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001824920.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Revenue | 130016000 | 130016000 | 43073000 | 43073000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R4.htm | Cost of revenue (excluding depreciation and amortization) | 77488000 | 77488000 | 20597000 | 20597000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1058 tags across all 114 R pages, face and notes) of 0001193125-26-071562; no face row matched |
| operating_expenses | combined | us-gaap:OperatingCostsAndExpenses | R4.htm | Total operating costs and expenses | 763731000 | 763731000 | 275528000 | 275528000 | Y | FILING-CHECKED | printed total includes cost of revenue: combined, never opex / accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 245087000 | 245087000 | 71055000 | 71055000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 305705000 | 305705000 | 136827000 | 136827000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Loss from operations | -633715000 | -633715000 | -232455000 | -232455000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (1058 tags across all 114 R pages, face and notes) of 0001193125-26-071562; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Total net loss before income taxes | -556693000 | -556693000 | -331588000 | -331588000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax benefit (expense) | 44572000 | -44572000 | -59000 | 59000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net loss attributable to IonQ, Inc. | -510378000 | -510378000 | -331647000 | -331647000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net loss per share attributable to IonQ, Inc. common stockholders-basic | -1.82 | -1.82 | -1.56 | -1.56 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net loss per share attributable to IonQ, Inc. common stockholders-diluted | -1.82 | -1.82 | -1.56 | -1.56 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average shares used in computing net loss per share attributable to IonQ, Inc. common stockholders-basic | 280345046 | 280345046 | 213029365 | 213029365 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average shares used in computing net loss per share attributable to IonQ, Inc. common stockholders-diluted | 280345046 | 280345046 | 213029365 | 213029365 | Y | FILING-CHECKED | accn 0001193125-26-071562 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 1030865000 | 1030865000 | 54393000 | 54393000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net | 66532000 | 66532000 | 10188000 | 10188000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R76.htm | Other Balance Sheet Accounts - Summary of Prepaid Expenses and Other Current Assets (Detail) |  | 10310000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R76.htm 'Other Balance Sheet Accounts - Summary of Prepaid Expenses and Other Current Ass' (MetaLinks.json presentation); value from companyfacts same accession |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2586439000 | 2586439000 | 378802000 | 378802000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 120145000 | 120145000 | 52761000 | 52761000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1963584000 | 1963584000 | 9904000 | 9904000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total Assets | 6570358000 | 6570358000 | 508388000 | 508388000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 26138000 | 26138000 | 5230000 | 5230000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 166825000 | 166825000 | 36085000 | 36085000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 2756666000 | 2756666000 | 124526000 | 124526000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total IonQ, Inc. stockholders' equity | 3799517000 | 3799517000 | 383862000 | 383862000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used in) operating activities | -283187000 | -283187000 | -105683000 | -105683000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | -2095088000 | -2095088000 | 82730000 | 82730000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | 3358602000 | 3358602000 | 41687000 | 41687000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -16417000 | 16417000 | -17992000 | 17992000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-071562 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 82004000 | 82004000 | 18654000 | 18654000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 312032000 | 312032000 | 106878000 | 106878000 | Y | FILING-CHECKED | accn 0001193125-26-071562 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1058 tags across all 114 R pages, face and notes) of 0001193125-26-071562; no face row matched |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1058 tags across all 114 R pages, face and notes) of 0001193125-26-071562; no face row matched |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (1058 tags across all 114 R pages, face and notes) of 0001193125-26-071562; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R103.htm | Income Tax - Additional Information (Detail) |  | 0 |  |  |  | FILING-CHECKED | not on the face statement; shown in R103.htm 'Income Tax - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (1058 tags across all 114 R pages, face and notes) of 0001193125-26-071562; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 362592722 | 362592722 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- basic_eps: era 10-K 0001193125-22-086738 R4.htm prints 'Net loss per share attributable to common stockholders—basic and diluted' on us-gaap:EarningsPerShareBasicAndDiluted = -0.77 (FILING-CHECKED)
- diluted_eps: era 10-K 0001193125-22-086738 R4.htm prints 'Net loss per share attributable to common stockholders—basic and diluted' on us-gaap:EarningsPerShareBasicAndDiluted = -0.77 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 130016000 vs printed 130016000 |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 763731000 vs printed 763731000 |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | mapped-sample | agree | page value 44572000 vs printed 44572000 |
| inventory | NOTE | agree | page value 10310000 vs API 10310000 |
| cfo | mapped-sample | agree | page value -283187000 vs printed -283187000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 0 vs API 0 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
