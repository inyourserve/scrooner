# DECK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-037664 (CIK 0000910521, filed 2026-05-22): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000910521-15-000018 (CIK 0000910521, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- 10-K 0000910521-18-000015 (CIK 0000910521, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- 10-K 0000910521-17-000008 (CIK 0000910521, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- companyfacts CIK0000910521.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R43.htm | Revenue Recognition and Business Concentrations - Schedule of Net Sales by Channel and Geography (Details) (Details) |  | 5472296000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R43.htm 'Revenue Recognition and Business Concentrations - Schedule of Net Sales by Chann' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R79.htm | Reportable Operating Segments - Schedule of Operating Segment Information (Details) |  | 2314570000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R79.htm 'Reportable Operating Segments - Schedule of Operating Segment Information (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| gross_profit | mapped | us-gaap:GrossProfit | R79.htm | Reportable Operating Segments - Schedule of Operating Segment Information (Details) |  | 3157726000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R79.htm 'Reportable Operating Segments - Schedule of Operating Segment Information (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (804 tags across all 82 R pages, face and notes) of 0001628280-26-037664; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME |  | 1894823000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R5.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R40.htm | General - Narrative (Details) |  | 68899000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'General - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME |  | 1262903000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R5.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME |  | 2530000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R5.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic | R51.htm | Income Taxes - Schedule of Income Before Income Taxes (Details) |  | 1084446000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R51.htm 'Income Taxes - Schedule of Income Before Income Taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R52.htm | Income Taxes - Schedule of Components of Income Tax Expense (Benefit) (Details) |  | 302285000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R52.htm 'Income Taxes - Schedule of Components of Income Tax Expense (Benefit) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME |  | 1024071000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R5.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME |  | 7.04 |  |  |  | FILING-CHECKED | not on the face statement; shown in R5.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME |  | 7.02 |  |  |  | FILING-CHECKED | not on the face statement; shown in R5.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R77.htm | Basic and Diluted Shares (Details) |  | 145498000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R77.htm 'Basic and Diluted Shares (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R77.htm | Basic and Diluted Shares (Details) |  | 145805000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R77.htm 'Basic and Diluted Shares (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1907249000 | 1907249000 | 1889188000 | 1889188000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade accounts receivable, net of allowances ($38,198 and $32,883 as of March 31, 2026, and March 31, 2025, respectively | 318978000 | 318978000 | 332872000 | 332872000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 487018000 | 487018000 | 495226000 | 495226000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2850420000 | 2850420000 | 2860475000 | 2860475000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net of accumulated depreciation ($457,173 and $402,964 as of March 31, 2026, and March 31, 2025, | 337782000 | 337782000 | 325599000 | 325599000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill (Note 1) | 13990000 | 13990000 | 13990000 | 13990000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3687765000 | 3687765000 | 3570252000 | 3570252000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R3.htm | Trade accounts payable | 384529000 | 384529000 | 417955000 | 417955000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 804074000 | 804074000 | 769941000 | 769941000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (804 tags across all 82 R pages, face and notes) of 0001628280-26-037664; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 2499638000 | 2499638000 | 2513013000 | 2513013000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R3.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1181955000 | 1181955000 | 1044523000 | 1044523000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -84612000 | -84612000 | -75003000 | -75003000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -1084044000 | -1084044000 | -581334000 | -581334000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -84623000 | 84623000 | -86171000 | 86171000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation, amortization, and accretion | 75773000 | 75773000 | 69353000 | 69353000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 44835000 | 44835000 | 37943000 | 37943000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (804 tags across all 82 R pages, face and notes) of 0001628280-26-037664; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock | -1075100000 | 1075100000 | -567002000 | 567002000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest | 2492000 | 2492000 | 1789000 | 1789000 | Y | FILING-CHECKED | accn 0001628280-26-037664 R7.htm period ..2026-03-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R54.htm | Income Taxes - Schedule of Cash Paid For Income Taxes, Net of Refunds (Details) |  | 234314000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R54.htm 'Income Taxes - Schedule of Cash Paid For Income Taxes, Net of Refunds (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (804 tags across all 82 R pages, face and notes) of 0001628280-26-037664; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding shares (in shares) | 139978000 | 139978000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-03-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0000910521-15-000018 statement not identified (auto)
- cost_of_revenue: 10-K 0000910521-15-000018 statement not identified (auto)
- gross_profit: 10-K 0000910521-15-000018 statement not identified (auto)
- sga_expense: 10-K 0000910521-15-000018 statement not identified (auto)
- research_and_development: 10-K 0000910521-15-000018 statement not identified (auto)
- operating_income: 10-K 0000910521-15-000018 statement not identified (auto)
- interest_expense: 10-K 0000910521-15-000018 statement not identified (auto)
- income_before_tax: 10-K 0000910521-15-000018 statement not identified (auto)
- income_tax_expense: 10-K 0000910521-15-000018 statement not identified (auto)
- net_income: 10-K 0000910521-15-000018 statement not identified (auto)
- basic_eps: 10-K 0000910521-15-000018 statement not identified (auto)
- diluted_eps: 10-K 0000910521-15-000018 statement not identified (auto)
- weighted_basic_shares: 10-K 0000910521-15-000018 statement not identified (auto)
- weighted_diluted_shares: 10-K 0000910521-15-000018 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- accounts_receivable: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- inventory: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- accounts_payable: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- current_liabilities: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0000910521-15-000018 R2.htm read; no row matched (auto)
- cfo: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- cash_flow_investing: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- cash_flow_financing: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- capex: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000910521-15-000018 R6.htm read; no row matched (auto)
- cost_of_revenue: 10-K 0000910521-18-000015 statement not identified (auto)
- cfo: era 10-K 0000910521-17-000008 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 198677000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000910521-17-000008 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -44499000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000910521-17-000008 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -103070000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 5472296000 vs API 5472296000 |
| cost_of_revenue | NOTE | agree | page value 2314570000 vs API 2314570000 |
| gross_profit | NOTE | agree | page value 3157726000 vs API 3157726000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | mapped-sample | agree | page value 1894823000 vs API 1894823000 |
| research_and_development | NOTE | agree | page value 68899000 vs API 68899000 |
| income_before_tax | NOTE | agree | page value 1084446000 vs API 1084446000 |
| income_tax_expense | NOTE | agree | page value 302285000 vs API 302285000 |
| weighted_basic_shares | NOTE | agree | page value 145498000 vs API 145498000 |
| weighted_diluted_shares | NOTE | agree | page value 145805000 vs API 145805000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_financing | mapped-sample | agree | page value -1084044000 vs printed -1084044000 |
| depreciation_and_amortization | combined | agree | page value 75773000 vs printed 75773000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | mapped-sample | agree | page value 2492000 vs printed 2492000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 234314000 vs API 234314000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
