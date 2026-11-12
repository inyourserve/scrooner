# MDGL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-009514 (CIK 0001157601, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001047469-16-011140 (CIK 0001157601, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001193125-23-045575 (CIK 0001157601, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001628280-25-007980 (CIK 0001157601, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001157601.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Product revenue, net | 958403000 | 958403000 | 180133000 | 180133000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:OperatingCostsAndExpenses | R5.htm | Cost of sales | 56148000 | 56148000 | 6233000 | 6233000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (669 tags across all 70 R pages, face and notes) of 0001628280-26-009514; no face row matched |
| operating_expenses | combined | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1258500000 | 1258500000 | 678008000 | 678008000 | Y | FILING-CHECKED | printed total includes cost of revenue: combined, never opex / accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 813827000 | 813827000 | 435057000 | 435057000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost | R5.htm | Research and development | 388525000 | 388525000 | 236718000 | 236718000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -300097000 | -300097000 | -497875000 | -497875000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -22309000 | 22309000 | -14671000 | 14671000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic | R65.htm | Income Taxes - Narrative (Details) |  | -158500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R68.htm | Income Taxes - Effective Income Tax Rate (Details) |  | 0 |  |  |  | FILING-CHECKED | not on the face statement; shown in R68.htm 'Income Taxes - Effective Income Tax Rate (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -288284000 | -288284000 | -465892000 | -465892000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net loss per common share (in dollars per share) | -12.85 | -12.85 | -21.9 | -21.9 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net loss per common share (in dollars per share) | -12.85 | -12.85 | -21.9 | -21.9 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted average number of common shares outstanding (in shares) | 22434310 | 22434310 | 21272962 | 21272962 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted average number of common shares outstanding (in shares) | 22434310 | 22434310 | 21272962 | 21272962 | Y | FILING-CHECKED | accn 0001628280-26-009514 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 198693000 | 198693000 | 100019000 | 100019000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade receivables, net | 134476000 | 134476000 | 53822000 | 53822000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 74841000 | 74841000 | 34068000 | 34068000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1245770000 | 1245770000 | 1032927000 | 1032927000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1499000 | 1499000 | 2190000 | 2190000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (669 tags across all 70 R pages, face and notes) of 0001628280-26-009514; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1259589000 | 1259589000 | 1042247000 | 1042247000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 48878000 | 48878000 | 43599000 | 43599000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 310288000 | 310288000 | 169277000 | 169277000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 656900000 | 656900000 | 287864000 | 287864000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 602689000 | 602689000 | 754383000 | 754383000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash used in operating activities | -189553000 | -189553000 | -455572000 | -455572000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | 32320000 | 32320000 | -274386000 | -274386000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 255984000 | 255984000 | 735062000 | 735062000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment, net of disposals | -467000 | 467000 | -1462000 | 1462000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009514 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization expense | 1506000 | 1506000 | 1096000 | 1096000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 98130000 | 98130000 | 79880000 | 79880000 | Y | FILING-CHECKED | accn 0001628280-26-009514 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (669 tags across all 70 R pages, face and notes) of 0001628280-26-009514; no face row matched |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (669 tags across all 70 R pages, face and notes) of 0001628280-26-009514; no face row matched |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (669 tags across all 70 R pages, face and notes) of 0001628280-26-009514; no face row matched |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (669 tags across all 70 R pages, face and notes) of 0001628280-26-009514; no face row matched |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Loan payable, net of discount | 339881000 | 339881000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (shares) | 22842073 | 22842073 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-011140 R4.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001047469-16-011140 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 67610000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-16-011140 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 13392000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost = 54218000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Loss from operations' on us-gaap:OperatingIncomeLoss = -67610000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -1061000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047469-16-011140 R4.htm read; no row matched (auto)
- income_tax_expense: FY2015 10-K 0001047469-16-011140 R4.htm read; no row matched (auto)
- net_income: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Net loss' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = -68671000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Basic and diluted net loss per common share (in dollars per share)' on us-gaap:EarningsPerShareBasicAndDiluted = -0.53 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-011140 R4.htm prints 'Basic and diluted net loss per common share (in dollars per share)' on us-gaap:EarningsPerShareBasicAndDiluted = -0.53 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-011140 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-011140 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 34966000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-16-011140 R2.htm read; no row matched (auto)
- inventory: FY2015 10-K 0001047469-16-011140 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 67775000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 420000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Total assets' on us-gaap:Assets = 68195000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1299000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 17788000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 17788000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-011140 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 50407000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-011140 R7.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -71444000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-011140 R7.htm prints 'Net cash provided by (used) in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 20000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-011140 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 40386000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-16-011140 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -58000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-011140 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 662000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-16-011140 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 4300000 (FILING-CHECKED)
- revenue: era 10-K 0001193125-23-045575 R4.htm read; no row matched (auto)
- cost_of_revenue: era 10-K 0001628280-25-007980 R5.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 6233000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1258500000 vs printed 1258500000 |
| income_before_tax | NOTE | agree | page value 158500000 vs API -158500000 |
| income_tax_expense | NOTE | agree | page value 0 vs API 0 |
| diluted_eps | mapped-sample | agree | page value -12.85 vs printed -12.85 |
| weighted_basic_shares | mapped-sample | agree | page value 22434310 vs printed 22434310 |
| ppe_net | mapped-sample | agree | page value 1499000 vs printed 1499000 |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 339881000 vs printed 339881000 |
