# AGNC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001423689-26-000043 (CIK 0001423689, filed 2026-02-23): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- 10-K 0001423689-24-000005 (CIK 0001423689, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- 10-K 0001423689-21-000011 (CIK 0001423689, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- companyfacts CIK0001423689.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, RegulatedAndUnregulatedOperatingRevenue, RegulatedOperatingRevenue in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| cost_of_revenue | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| gross_profit | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Consolidated Statements Of Comprehensive Income |  | 127000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | Consolidated Statements Of Comprehensive Income |  | 40000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| operating_income | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R4.htm | Consolidated Statements Of Comprehensive Income |  | 2848000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments, IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| income_tax_expense | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxExpenseBenefit in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Consolidated Statements Of Comprehensive Income |  | 1670000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R60.htm | Net Income (Loss) Per Common Share (Details) |  | 1.48 |  |  |  | FILING-CHECKED | not on the face statement; shown in R60.htm 'Net Income (Loss) Per Common Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R60.htm | Net Income (Loss) Per Common Share (Details) |  | 1.47 |  |  |  | FILING-CHECKED | not on the face statement; shown in R60.htm 'Net Income (Loss) Per Common Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R60.htm | Net Income (Loss) Per Common Share (Details) |  | 1020000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R60.htm 'Net Income (Loss) Per Common Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R60.htm | Net Income (Loss) Per Common Share (Details) |  | 1023700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R60.htm 'Net Income (Loss) Per Common Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 450000000 | 450000000 | 505000000 | 505000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Consolidated Balance Sheets |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R2.htm 'Consolidated Balance Sheets' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| ppe_net | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R2.htm | Goodwill and other intangible assets, net | 526000000 | 526000000 | 526000000 | 526000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001423689-26-000043 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 115077000000 | 115077000000 | 88015000000 | 88015000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 102684000000 | 102684000000 | 78253000000 | 78253000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 12393000000 | 12393000000 | 9762000000 | 9762000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by (used in) operating activities | 653000000 | 653000000 | 86000000 | 86000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -25864000000 | -25864000000 | -11169000000 | -11169000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by financing activities | 25182000000 | 25182000000 | 11083000000 | 11083000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| capex | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| depreciation_and_amortization | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of DepreciationDepletionAndAmortization, DepreciationAndAmortization, DepreciationAmortizationAndAccretionNet, Depreciation, AmortizationOfIntangibleAssets, DepreciationNonproduction in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock based compensation | 26000000 | 26000000 | 18000000 | 18000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R6.htm | Cash dividends paid | -1601000000 | 1601000000 | -1241000000 | 1241000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:ProceedsFromPaymentsForSecuritiesPurchasedUnderAgreementsToResell | R6.htm | Net proceeds from (payments on) reverse repurchase agreements | 1407000000 | 1407000000 | -4793000000 | -4793000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R6.htm | Interest Paid, Including Capitalized Interest, Operating and Investing Activities | 2793000000 | 2793000000 | 2899000000 | 2899000000 | Y | FILING-CHECKED | accn 0001423689-26-000043 R6.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R6.htm | Consolidated Statements Of Cash Flows |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R6.htm 'Consolidated Statements Of Cash Flows' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| total_debt | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (906 tags across all 71 R pages, face and notes) of 0001423689-26-000043; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common Stock, Shares, Outstanding | 1107600000 | 1107600000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: 10-K 0001423689-24-000005 statement not identified (auto)
- cash_and_equivalents: era 10-K 0001423689-21-000011 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1017000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (1). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| basic_eps | NOTE | agree | page value 1.48 vs API 1.48 |
| diluted_eps | NOTE | agree | page value 1.47 vs API 1.47 |
| weighted_basic_shares | NOTE | agree | page value 1020000000 vs API 1020000000 |
| weighted_diluted_shares | NOTE | agree | page value 1023700000 vs API 1023700000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| capex | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | PaymentsForRepurchaseOfCommonStock presented but with no 2025-12-31 value on any presenting page: nothing to read for this period |
| cash_paid_for_interest | combined | agree | page value 2793000000 vs printed 2793000000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | mapped-sample | agree | page value 1107600000 vs printed 1107600000 |
