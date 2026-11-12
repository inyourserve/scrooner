# FDS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-066391 (CIK 0001013237, filed 2026-10-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001437749-15-019227 (CIK 0001013237, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001437749-18-019028 (CIK 0001013237, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001437749-19-020894 (CIK 0001013237, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001013237.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 2476256000 | 2476256000 | 2321748000 | 2321748000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of services | 1223146000 | 1223146000 | 1097782000 | 1097782000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (799 tags across all 89 R pages, face and notes) of 0001628280-26-066391; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 1776299000 | 1776299000 | 1573445000 | 1573445000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 553153000 | 553153000 | 475663000 | 475663000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R44.htm | SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES (Details) |  | 346100000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R44.htm 'SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 699957000 | 699957000 | 748303000 | 748303000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -54684000 | 54684000 | -56324000 | 56324000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 649716000 | 649716000 | 720958000 | 720958000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 116235000 | 116235000 | 123918000 | 123918000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 533481000 | 533481000 | 597040000 | 597040000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per common share (in USD per share) | 14.63 | 14.63 | 15.74 | 15.74 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per common share (in USD per share) | 14.57 | 14.57 | 15.55 | 15.55 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic weighted average common shares (in shares) | 36467000 | 36467000 | 37924000 | 37924000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted weighted average common shares (in shares) | 36612000 | 36612000 | 38385000 | 38385000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R3.htm period ..2026-08-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 233339000 | 233339000 | 337651000 | 337651000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net of reserves of $13,584 at August 31, 2026 and $13,789 at August 31, 2025 | 298619000 | 298619000 | 270684000 | 270684000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (799 tags across all 89 R pages, face and notes) of 0001628280-26-066391; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 651893000 | 651893000 | 729759000 | 729759000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, equipment and leasehold improvements, net | 79246000 | 79246000 | 85203000 | 85203000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1283025000 | 1283025000 | 1284708000 | 1284708000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | TOTAL ASSETS | 4140023000 | 4140023000 | 4304272000 | 4304272000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R6.htm | Accounts payable and accrued expenses | 136104000 | 136104000 | 135262000 | 135262000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1089502000 | 1089502000 | 521306000 | 521306000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | TOTAL LIABILITIES | 2138157000 | 2138157000 | 2117859000 | 2117859000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | TOTAL STOCKHOLDERS’ EQUITY | 2001866000 | 2001866000 | 2186413000 | 2186413000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R6.htm period ..2026-08-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 822200000 | 822200000 | 726260000 | 726260000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | -132504000 | -132504000 | -392773000 | -392773000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | -799447000 | -799447000 | -407821000 | -407821000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Purchases of property, equipment, leasehold improvements and capitalized internal-use software | -114720000 | 114720000 | -108806000 | 108806000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 180830000 | 180830000 | 157691000 | 157691000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 84099000 | 84099000 | 61229000 | 61229000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividend payments | -164184000 | 164184000 | -159973000 | 159973000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -643961000 | 643961000 | -300457000 | 300457000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid during the year for interest | 51760000 | 51760000 | 54813000 | 54813000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid during the year for income taxes, net of refunds | 122731000 | 122731000 | 103167000 | 103167000 | Y | FILING-CHECKED | accn 0001628280-26-066391 R8.htm period ..2026-08-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current debt + Long-term debt | 1370022000 | 1370022000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, outstanding (in shares) | 35257384 | 35257384 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-08-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Revenues' on us-gaap:Revenues = 1006768000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Cost of services' on us-gaap:CostOfServices = 405339000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 674850000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 269511000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001437749-15-019227 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 331918000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001437749-15-019227 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 333754000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 92703000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 241051000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Basic earnings per common share (in Dollars per share)' on us-gaap:EarningsPerShareBasic = 5.8 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Diluted earnings per common share (in Dollars per share)' on us-gaap:EarningsPerShareDiluted = 5.71 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Weighted average common shares (Basic) (in Shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 41572000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001437749-15-019227 R2.htm prints 'Weighted average common shares (Diluted) (in Shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 42235000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 158914000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Accounts receivable, net of reserves of $1,580 and $1,662 at August 31, 2015 and' on us-gaap:AccountsReceivableNetCurrent = 95064000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 304174000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Property, equipment and leasehold improvements, net' on us-gaap:PropertyPlantAndEquipmentNet = 59264000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 308287000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001437749-15-019227 R5.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 736671000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 33880000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001437749-15-019227 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 139780000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001437749-15-019227 R5.htm prints 'TOTAL LIABILITIES' on us-gaap:Liabilities = 205087000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001437749-15-019227 R5.htm prints 'TOTAL STOCKHOLDERS’ EQUITY' on us-gaap:StockholdersEquity = 531584000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 306442000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -64877000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -187326000 (FILING-CHECKED)
- capex: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Purchases of property, equipment and leasehold improvements, net of proceeds fro' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -25682000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 31349000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 26371000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Dividend payments' on us-gaap:PaymentsOfDividends = -66551000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -256217000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001437749-15-019227 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001437749-15-019227 R7.htm prints 'Cash paid during the year for income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 64750000 (FILING-CHECKED)
- revenue: era 10-K 0001437749-18-019028 R2.htm prints 'Revenues' on us-gaap:Revenues = 1350145000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001437749-18-019028 R2.htm prints 'Cost of services' on us-gaap:CostOfRevenue = 659296000 (FILING-CHECKED)
- operating_expenses: era 10-K 0001437749-18-019028 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 983941000 (FILING-CHECKED)
- interest_expense: era 10-K 0001437749-18-019028 R2.htm prints 'Interest (expense), net of interest income' on us-gaap:InterestIncomeExpenseNonoperatingNet = -14366000 (FILING-CHECKED)
- revenue: era 10-K 0001437749-19-020894 R2.htm prints 'Revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 1435351000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1776299000 vs printed 1776299000 |
| research_and_development | NOTE | agree | page value 346100000 vs API 346100000 |
| weighted_basic_shares | mapped-sample | agree | page value 36467000 vs printed 36467000 |
| weighted_diluted_shares | mapped-sample | agree | page value 36612000 vs printed 36612000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 79246000 vs printed 79246000 |
| dividends_paid | mapped-sample | agree | page value -164184000 vs printed -164184000 |
| total_debt | component sum | agree | page value 1370022000 vs printed 1370022000 |
