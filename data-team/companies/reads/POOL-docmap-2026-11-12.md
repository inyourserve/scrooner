# POOL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-074833 (CIK 0000945841, filed 2026-02-26): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000945841-16-000190 (CIK 0000945841, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000945841-18-000020 (CIK 0000945841, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000945841-19-000013 (CIK 0000945841, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000945841.json (one call); submissions CIK0000945841.json (SIC 5090).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R2.htm | Net sales | 5289396000 | 5289396000 | 5310953000 | 5310953000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R2.htm | Cost of sales | 3716938000 | 3716938000 | 3735606000 | 3735606000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross profit | 1572458000 | 1572458000 | 1575347000 | 1575347000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling and administrative expenses | 992254000 | 992254000 | 958143000 | 958143000 | Y | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling and administrative expenses | 992254000 | 992254000 | 958143000 | 958143000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Distributor with no R&D line on tax, intangibles, SBC, lease or segment pages. / pages opened: R76, R53, R69, R72, R83, R92 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income | 580204000 | 580204000 | 617204000 | 617204000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:NonoperatingIncomeExpense | R2.htm | Interest and other non-operating expenses, net | 46770000 |  |  |  |  | FILING-CHECKED | check: hand / Interest is printed only inside the net line 'Interest and other non-operating expenses, net'; no gross interest expense elsewhere on listed pages. / pages opened: R2, R80, R94, R18, R30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R2.htm | Income before income taxes and equity in earnings | 533434000 | 533434000 | 566954000 | 566954000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 127132000 | 127132000 | 132836000 | 132836000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income | 406404000 | 406404000 | 434325000 | 434325000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic (in dollars per share) | 10.89 | 10.89 | 11.37 | 11.37 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted (in dollars per share) | 10.85 | 10.85 | 11.3 | 11.3 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic (in shares) | 37149000 | 37149000 | 38007000 | 38007000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted (in shares) | 37288000 | 37288000 | 38228000 | 38228000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash and cash equivalents | 104963000 | 104963000 | 77862000 | 77862000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net | 136063000 | 136063000 | 115835000 | 115835000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Product inventories, net | 1454672000 | 1454672000 | 1289300000 | 1289300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1969864000 | 1969864000 | 1729114000 | 1729114000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 267065000 | 267065000 | 251324000 | 251324000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 707345000 | 707345000 | 698910000 | 698910000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 3626126000 | 3626126000 | 3368184000 | 3368184000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 652619000 | 652619000 | 525235000 | 525235000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 880285000 | 880285000 | 844186000 | 844186000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 2440897000 | 2440897000 | 2094719000 | 2094719000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity | 1185229000 | 1185229000 | 1273465000 | 1273465000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 365850000 | 365850000 | 659186000 | 659186000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -67792000 | -67792000 | -66169000 | -66169000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -273379000 | -273379000 | -576550000 | -576550000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment, net of sale proceeds | -56334000 | 56334000 | -59476000 | 59476000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AdjustmentForAmortization | R7.htm | Depreciation + Amortization | 51605000 | 51605000 | 45481000 | 45481000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 22733000 | 22733000 | 19248000 | 19248000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Payments of cash dividends | -184916000 | 184916000 | -179633000 | 179633000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock and payments of excise tax | -346286000 | 346286000 | -306300000 | 306300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R48.htm | Interest | 47670000 | 47670000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R48.htm 'Organization and Summary of Significant Accounting Policies - Supplemental Cash ' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R48.htm | Income taxes, net of refunds | 180473000 | 180473000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R48.htm 'Organization and Summary of Significant Accounting Policies - Supplemental Cash ' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings and current portion of long-term debt + Long-term debt, net | 1199453000 | 1199453000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 36577686 | 36577686 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 2363139000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 1687495000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 675644000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Selling and administrative expenses + Goodwill impairment' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GoodwillImpairmentLoss = 459422000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Selling and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 459422000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 216222000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Income before income taxes and equity earnings' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 208150000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 80137000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Net income attributable to Pool Corporation' on us-gaap:NetIncomeLoss = 128275000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.98 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.9 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 43105000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000945841-16-000190 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 44254000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 13237000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 54173000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Inventory, net' on us-gaap:InventoryNet = 474275000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 661744000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 69854000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 172761000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Total assets' on us-gaap:Assets = 936031000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 246554000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 304845000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 677623000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000945841-16-000190 R5.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 255743000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 146050000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -37793000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -107804000 (FILING-CHECKED)
- capex: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Purchases of property and equipment, net of sale proceeds' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -29095000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000945841-16-000190 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 9543000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Payments of cash dividends' on us-gaap:PaymentsOfDividends = -43117000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000945841-16-000190 R7.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -99219000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000945841-16-000190 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000945841-16-000190 R7.htm read; no row matched (auto)
- revenue: era 10-K 0000945841-18-000020 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 2788188000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000945841-19-000013 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 16358000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000945841-19-000013 R7.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences
