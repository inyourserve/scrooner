# ALLY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000040729-26-000005 (CIK 0000040729, filed 2026-02-25): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R11.htm
- 10-K 0000040729-16-000473 (CIK 0000040729, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, CF R7.htm
- 10-K 0000040729-24-000004 (CIK 0000040729, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R10.htm
- 10-K 0000040729-19-000010 (CIK 0000040729, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, CF R6.htm, CI R7.htm
- companyfacts CIK0000040729.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total net revenue | 7914000000 | 7914000000 | 8181000000 | 8181000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R3.htm | Total interest expense | 6408000000 | 6408000000 | 7472000000 | 7472000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income tax expense | 1051000000 | 1051000000 | 836000000 | 836000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Total income tax expense from continuing operations | 199000000 | 199000000 | 167000000 | 167000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 852000000 | 852000000 | 668000000 | 668000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income (in dollars per share) | 2.39 | 2.39 | 1.82 | 1.82 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income (in dollars per share) | 2.37 | 2.37 | 1.8 | 1.8 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic weighted-average common shares outstanding (in shares) | 310015000 | 310015000 | 306913000 | 306913000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted weighted-average common shares outstanding (in shares) | 313043000 | 313043000 | 310160000 | 310160000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Total cash and cash equivalents | 10030000000 | 10030000000 | 10292000000 | 10292000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| current_assets | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R114.htm | Other Assets - Schedule of Other Assets (Details) |  | 1150000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R114.htm 'Other Assets - Schedule of Other Assets (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| goodwill | mapped | us-gaap:Goodwill | R114.htm | Other Assets - Schedule of Other Assets (Details) |  | 190000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R114.htm 'Other Assets - Schedule of Other Assets (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 196002000000 | 196002000000 | 191836000000 | 191836000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R5.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| current_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 180504000000 | 180504000000 | 177933000000 | 177933000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total equity | 15498000000 | 15498000000 | 13903000000 | 13903000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R11.htm | Net cash provided by operating activities | 3729000000 | 3729000000 | 4528000000 | 4528000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R11.htm | Net cash (used in) provided by investing activities | -5264000000 | -5264000000 | 4991000000 | 4991000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R11.htm | Net cash provided by (used in) financing activities | 1956000000 | 1956000000 | -5566000000 | -5566000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| capex | not_presented |  | R11.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1527 tags across all 166 R pages, face and notes) of 0000040729-26-000005; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R11.htm | Depreciation and amortization | 1397000000 | 1397000000 | 1199000000 | 1199000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R151.htm | Share-based Compensation Plans - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R151.htm 'Share-based Compensation Plans - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R11.htm | Common stock dividends paid | -379000000 | 379000000 | -372000000 | 372000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R11.htm | Repurchases of common stock | -59000000 | 59000000 | -38000000 | 38000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R11.htm | Interest | 6477000000 | 6477000000 | 7354000000 | 7354000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R11.htm | Income taxes | 359000000 | 359000000 | 135000000 | 135000000 | Y | FILING-CHECKED | accn 0000040729-26-000005 R11.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R5.htm | Short-term borrowings + Long-term debt | 21765000000 | 21765000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 308492929 | 308492929 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Total net revenue (loss)' on us-gaap:Revenues = 4861000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Total interest expense' on us-gaap:InterestExpense = 2429000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Income (loss) from continuing operations before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1393000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Income tax expense (benefit) from continuing operations' on us-gaap:IncomeTaxExpenseBenefit = 496000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Net income (loss)' on us-gaap:NetIncomeLoss = 1289000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Net (loss) income, Basic' on us-gaap:EarningsPerShareBasic = -2.66 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000040729-16-000473 R2.htm prints 'Net (loss) income, Diluted' on us-gaap:EarningsPerShareDiluted = -2.66 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000040729-16-000473 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000040729-16-000473 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000040729-16-000473 R4.htm prints 'Total cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 6380000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000040729-16-000473 R4.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0000040729-16-000473 R4.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000040729-16-000473 R4.htm prints 'Total assets' on us-gaap:Assets = 158581000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000040729-16-000473 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 145142000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000040729-16-000473 R4.htm prints 'Total equity' on us-gaap:StockholdersEquity = 13439000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 5095000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -9747000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 5460000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Depreciation, Amortization and Accretion, Net' on us-gaap:DepreciationAmortizationAndAccretionNet = 2801000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000040729-16-000473 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -2571000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Payments for Repurchase of Redeemable Preferred Stock' on us-gaap:PaymentsForRepurchaseOfRedeemablePreferredStock = -559000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Interest' on us-gaap:InterestPaid = 2632000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000040729-16-000473 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 96000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000040729-24-000004 R3.htm prints 'Total interest expense' on us-gaap:InterestExpense = 6897000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000040729-19-000010 R2.htm prints 'Income from continuing operations before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1622000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | mapped-sample | agree | page value 199000000 vs printed 199000000 |
| net_income | mapped-sample | agree | page value 852000000 vs printed 852000000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | NOTE | agree | page value 1150000000 vs API 1150000000 |
| goodwill | NOTE | agree | page value 190000000 vs API 190000000 |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| capex | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | combined | agree | page value 1397000000 vs printed 1397000000 |
| sbc | NOTE | agree | value 130000000 read off its own R page (no companyfacts fact to compare) |
| total_debt | component sum | agree | page value 21765000000 vs printed 21765000000 |
| shares_outstanding | mapped-sample | agree | page value 308492929 vs printed 308492929 |
