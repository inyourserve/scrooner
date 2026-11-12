# ELS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008722 (CIK 0000895417, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0000895417-16-000082 (CIK 0000895417, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000895417-19-000012 (CIK 0000895417, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000895417-23-000008 (CIK 0000895417, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- companyfacts CIK0000895417.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 1531382000 | 1531382000 | 1526166000 | 1526166000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of services | 60335000 |  | 84771000 |  | API missing | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total expenses | 1140033000 | 1140033000 | 1145484000 | 1145484000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 37510000 | 37510000 | 38483000 | 38483000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income before taxes and other items | 391349000 | 391349000 | 380682000 | 380682000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R5.htm | Interest and related amortization | 131005000 | 131005000 | 137710000 | 137710000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income before taxes and other items | 391349000 | 391349000 | 380682000 | 380682000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax benefit | 3273000 | -3273000 | 354000 | -354000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R5.htm | Net income available for Common Stockholders | 386492000 | 386492000 | 366998000 | 366998000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Earnings per Common Share – Basic (usd per share) | 2.01 | 2.01 | 1.96 | 1.96 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Earnings per Common Share – Fully Diluted (usd per share) | 2.01 | 2.01 | 1.96 | 1.96 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average Common Shares outstanding – Basic (in shares) | 192137000 | 192137000 | 187439000 | 187439000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average Common Shares outstanding – Fully Diluted (in shares) | 200114000 | 200114000 | 196636000 | 196636000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and restricted cash | 26132000 | 26132000 | 24576000 | 24576000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:NotesReceivableNet | R3.htm | Notes receivable, net | 93358000 | 93358000 | 50726000 | 50726000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-008722 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R41.htm | Summary of Significant Accounting Policies - Additional Information (Details) |  | 17600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R41.htm 'Summary of Significant Accounting Policies - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 5745393000 | 5745393000 | 5645652000 | 5645652000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and other liabilities | 152536000 | 152536000 | 159225000 | 159225000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-008722 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 3930567000 | 3930567000 | 3821866000 | 3821866000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Stockholders’ Equity | 1756275000 | 1756275000 | 1740716000 | 1740716000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 571148000 | 571148000 | 596721000 | 596721000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -277083000 | -277083000 | -217838000 | -217838000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -292509000 | -292509000 | -384244000 | -384244000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsForCapitalImprovements | R7.htm | Capital improvements | -237091000 | 237091000 | -241279000 | 241279000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | els:DepreciationAmortizationAndAccretionIncludingCorporateAssetsNet | R7.htm | Depreciation and amortization | 213743000 |  | 209398000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Compensation expense related to incentive plans | 7252000 | 7252000 | 9372000 | 9372000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Common Stockholders | -387963000 | 387963000 | -350598000 | 350598000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest, net | 129968000 | 129968000 | 139975000 | 139975000 | Y | FILING-CHECKED | accn 0001628280-26-008722 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (1247 tags across all 81 R pages, face and notes) of 0001628280-26-008722; no face row matched |
| total_debt | mapped | us-gaap:LongTermDebt | R57.htm | Borrowing Arrangements - Fair Value of Mortgage Debt (Details) |  | 3345866000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R57.htm 'Borrowing Arrangements - Fair Value of Mortgage Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 193835561 | 193835561 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Total revenues' on us-gaap:Revenues = 821654000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000895417-16-000082 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Total expenses' on us-gaap:CostsAndExpenses = 675231000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000895417-16-000082 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 30644000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000895417-16-000082 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Interest and related amortization' on us-gaap:InterestExpenseDebt = 105731000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Income from continuing operations before equity in income of unconsolidated join' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 146423000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000895417-16-000082 R4.htm read; no row matched (auto)
- net_income: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Consolidated net income' on us-gaap:ProfitLoss = 150512000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Net income available for Common Stockholders' on us-gaap:EarningsPerShareBasic = 1.55 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Net income available for Common Stockholders' on us-gaap:EarningsPerShareDiluted = 1.54 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Weighted average Common Shares outstanding – basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 84031000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000895417-16-000082 R4.htm prints 'Weighted average Common Shares outstanding – fully diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 91907000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000895417-16-000082 R2.htm prints 'Cash' on us-gaap:Cash = 80258000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000895417-16-000082 R2.htm prints 'Notes receivable, net' on us-gaap:NotesReceivableNet = 35463000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000895417-16-000082 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000895417-16-000082 R2.htm prints 'Total Assets' on us-gaap:Assets = 3420061000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000895417-16-000082 R2.htm read; no row matched (auto)
- total_liabilities: FY2015 10-K 0000895417-16-000082 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 2427370000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000895417-16-000082 R2.htm prints 'Total Stockholders’ Equity' on us-gaap:StockholdersEquity = 925068000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 352882000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -120707000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -225631000 (FILING-CHECKED)
- capex: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Capital improvements' on us-gaap:PaymentsForCapitalImprovements = -93799000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000895417-16-000082 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Amortization of stock-related compensation' on us-gaap:ShareBasedCompensation = 8582000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Common Stockholders' on us-gaap:PaymentsOfDividendsCommonStock = -122077000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000895417-16-000082 R6.htm prints 'Cash paid during the period for interest' on us-gaap:InterestPaid = 106423000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000895417-19-000012 R4.htm prints 'Income before equity in income of unconsolidated joint ventures' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 221447000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000895417-23-000008 R5.htm prints 'Income before equity in income of unconsolidated joint ventures' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 295462000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- depreciation_and_amortization: API missing (els:DepreciationAmortizationAndAccretionIncludingCorporateAssetsNet)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1140033000 vs printed 1140033000 |
| sga_expense | component sum | agree | page value 53579000 vs printed 53579000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value 391349000 vs printed 391349000 |
| weighted_diluted_shares | mapped-sample | agree | page value 200114000 vs printed 200114000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | NOTE | agree | page value 17600000 vs API 17600000 |
| total_assets | mapped-sample | agree | page value 5745393000 vs printed 5745393000 |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | combined | agree | page value 213743000 vs printed 213743000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | page value 3345866000 vs API 3345866000 |
