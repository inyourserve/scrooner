# ERIE document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-010666 (CIK 0000922621, filed 2026-02-23): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000922621-16-000067 (CIK 0000922621, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000922621-18-000016 (CIK 0000922621, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000922621-19-000008 (CIK 0000922621, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000922621.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Total operating revenue | 4067258000 | 4067258000 | 3795115000 | 3795115000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 3350074000 | 3350074000 | 3118660000 | 3118660000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 717184000 | 717184000 | 676455000 | 676455000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 710603000 | 710603000 | 757279000 | 757279000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 151268000 | 151268000 | 156965000 | 156965000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 559335000 | 559335000 | 600314000 | 600314000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Common stock - basic (in dollars per share) | 12.01 |  | 12.89 |  | API missing | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Common stock - diluted (in dollars per share) | 10.69 |  | 11.48 |  | API missing | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Common stock - basic (in shares) | 46189024 |  | 46189044 |  | API missing | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Common stock - diluted (in shares) | 52305424 |  | 52306266 |  | API missing | FILING-CHECKED | accn 0001628280-26-010666 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash and cash equivalents (includes restricted cash of $30,189 and $23,559, respectively) | 345874000 | 345874000 | 298397000 | 298397000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables from Erie Insurance Exchange and affiliates, net | 735589000 | 735589000 | 707060000 | 707060000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1199173000 | 1199173000 | 1145032000 | 1145032000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| ppe_net | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| goodwill | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 3355481000 | 3355481000 | 2888614000 | 2888614000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued liabilities | 200701000 | 200701000 | 190028000 | 190028000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 945587000 | 945587000 | 802512000 | 802512000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 1072107000 | 1072107000 | 901356000 | 901356000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders' equity | 2283374000 | 2283374000 | 1987258000 | 1987258000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 686657000 | 686657000 | 611249000 | 611249000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -439328000 | -439328000 | -226912000 | -226912000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -199852000 | -199852000 | -229995000 | -229995000 | Y | FILING-CHECKED | accn 0001628280-26-010666 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R9.htm | Purchase of fixed assets | -115692000 | 115692000 | -124845000 | 124845000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010666 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R68.htm | Fixed Assets - Narrative (Details) |  | 69450000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R68.htm 'Fixed Assets - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R84.htm | Incentive and Deferred Compensation Plans - Total Compensation Cost and Tax Benefit (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'Incentive and Deferred Compensation Plans - Total Compensation Cost and Tax Bene' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid to shareholders | -254275000 | 254275000 | -237508000 | 237508000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010666 R9.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid | -104000000 | 104000000 | -159873000 | 159873000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010666 R9.htm period ..2025-12-31 |
| total_debt | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (947 tags across all 97 R pages, face and notes) of 0001628280-26-010666; no face row matched |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 46191610 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Total operating revenue' on us-gaap:Revenues = 1505508000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 1272967000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Net revenue from operations' on us-gaap:OperatingIncomeLoss = 232541000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 266249000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 91571000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 174678000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Common stock - basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.75 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Common stock - diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.33 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Common stock - basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 46186671 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000922621-16-000067 R2.htm prints 'Common stock - diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 52498811 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 182889000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Receivables from Erie Insurance Exchange and affiliates' on us-gaap:AccountsReceivableRelatedPartiesCurrent = 348055000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 635146000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Total assets' on us-gaap:Assets = 1407296000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 46526000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 445699000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 637793000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000922621-16-000067 R4.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 769503000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000922621-16-000067 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 217378000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000922621-16-000067 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 622000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000922621-16-000067 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -126858000 (FILING-CHECKED)
- capex: FY2015 10-K 0000922621-16-000067 R8.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0000922621-16-000067 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000922621-16-000067 R8.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000922621-16-000067 R8.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -126858000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000922621-16-000067 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = -106347000 (FILING-CHECKED)
- revenue: era 10-K 0000922621-18-000016 R2.htm prints 'Total operating revenue' on us-gaap:Revenues = 1691774000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000922621-19-000008 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 266417000 (FILING-CHECKED)

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: API missing (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | mapped-sample | agree | page value 3350074000 vs printed 3350074000 |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | mapped-sample | agree | page value 151268000 vs printed 151268000 |
| cash_and_equivalents | mapped-sample | agree | page value 345874000 vs printed 345874000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | NOTE | agree | page value 69450000 vs API 69450000 |
| sbc | NOTE | agree | value 663000 read off its own R page (no companyfacts fact to compare) |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | component sum | agree | page value 46191610 vs printed 46191610 |
