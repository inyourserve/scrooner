# MMM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000066740-26-000014 (CIK 0000066740, filed 2026-02-03): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001558370-16-003162 (CIK 0000066740, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R9.htm
- 10-K 0000066740-24-000016 (CIK 0000066740, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R10.htm
- 10-K 0001558370-20-000581 (CIK 0000066740, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R9.htm
- companyfacts CIK0000066740.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Net sales | 24948000000 | 24948000000 | 24575000000 | 24575000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 14991000000 | 14991000000 | 14447000000 | 14447000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1223 tags across all 131 R pages, face and notes) of 0000066740-26-000014; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 20319000000 | 20319000000 | 19753000000 | 19753000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 3997000000 | 3997000000 | 4221000000 | 4221000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1223 tags across all 131 R pages, face and notes) of 0000066740-26-000014; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | 4629000000 | 4629000000 | 4822000000 | 4822000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R70.htm | Supplemental Income Statement Information (Details) |  | 946000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R70.htm 'Supplemental Income Statement Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (loss) from continuing operations before income taxes | 4213000000 | 4213000000 | 4819000000 | 4819000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision (benefit) for income taxes | 1003000000 | 1003000000 | 804000000 | 804000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (loss) attributable to 3M | 3250000000 | 3250000000 | 4173000000 | 4173000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings (loss) per share — basic (in dollars per share) | 6.05 | 6.05 | 7.58 | 7.58 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings (loss) per share — diluted (in dollars per share) | 6 | 6 | 7.55 | 7.55 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted average 3M common shares outstanding - basic (in shares) | 537400000 | 537400000 | 550800000 | 550800000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted average 3M common shares outstanding - diluted (in shares) | 541300000 | 541300000 | 552400000 | 552400000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | R5.htm | Cash and cash equivalents | 5235000000 | 5235000000 | 5600000000 | 5600000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable — net of allowances of $61 and $60 | 3533000000 | 3533000000 | 3194000000 | 3194000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Total inventories | 3661000000 | 3661000000 | 3698000000 | 3698000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 16387000000 | 16387000000 | 15884000000 | 15884000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment — net | 7101000000 | 7101000000 | 7388000000 | 7388000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 6419000000 | 6419000000 | 6281000000 | 6281000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 37733000000 | 37733000000 | 39868000000 | 39868000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2702000000 | 2702000000 | 2660000000 | 2660000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 9595000000 | 9595000000 | 11256000000 | 11256000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 32986000000 | 32986000000 | 35974000000 | 35974000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total 3M Company shareholders’ equity | 4702000000 | 4702000000 | 3842000000 | 3842000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 2306000000 | 2306000000 | 1819000000 | 1819000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | 1350000000 | 1350000000 | -3206000000 | -3206000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | -4016000000 | -4016000000 | 1098000000 | 1098000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment (PP&E) | -910000000 | 910000000 | -1181000000 | 1181000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 1308000000 | 1308000000 | 1363000000 | 1363000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 225000000 | 225000000 | 289000000 | 289000000 | Y | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid to shareholders | -1562000000 | 1562000000 | -1982000000 | 1982000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchases of treasury stock | -3251000000 | 3251000000 | -1801000000 | 1801000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000066740-26-000014 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R92.htm | Long-Term Debt and Short-Term Borrowings - Schedule of Cash Interest Payments (Details) |  | 467000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Long-Term Debt and Short-Term Borrowings - Schedule of Cash Interest Payments (D' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R77.htm | Income Taxes - Schedule of Cash Income Tax Payments (Details) |  | 800000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R77.htm 'Income Taxes - Schedule of Cash Income Tax Payments (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings and current portion of long-term debt + Long-term debt | 12602000000 | 12602000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 530279131 | 530279131 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 30274000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 15383000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 23328000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 6182000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 6946000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Interest expense' on us-gaap:InterestAndDebtExpense = 149000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 6823000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1982000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Net income attributable to 3M' on us-gaap:NetIncomeLoss = 4833000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Earnings per share attributable to 3M common shareholders - basic (in dollars pe' on us-gaap:EarningsPerShareBasic = 7.72 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Earnings per share attributable to 3M common shareholders - diluted (in dollars ' on us-gaap:EarningsPerShareDiluted = 7.58 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Weighted average 3M common shares outstanding - basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 625600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001558370-16-003162 R2.htm prints 'Weighted average 3M common shares outstanding - diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 637200000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1798000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Accounts receivable - net of allowances of $91 and $94' on us-gaap:AccountsReceivableNetCurrent = 4154000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Total inventories' on us-gaap:InventoryNet = 3518000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 10986000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Property, plant and equipment - net' on us-gaap:PropertyPlantAndEquipmentNet = 8515000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 9249000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Total assets' on us-gaap:Assets = 32718000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1694000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 7118000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 20971000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001558370-16-003162 R4.htm prints 'Total 3M Company shareholders' equity' on us-gaap:StockholdersEquity = 11708000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 6420000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -2817000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -3648000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Purchases of property, plant and equipment (PP&E)' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1461000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 1435000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 276000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -2561000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001558370-16-003162 R9.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -5238000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001558370-16-003162 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001558370-16-003162 R9.htm read; no row matched (auto)
- interest_expense: era 10-K 0000066740-24-000016 R3.htm read; no row matched (auto)
- income_before_tax: era 10-K 0001558370-20-000581 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 5712000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+mmm:ResearchDevelopmentAndRelatedExpenses+us-gaap:GainLossOnSaleOfBusiness (R3.htm): 2026-11-12 R3.htm: corrected: opex = 3,997 + 1,169 + 162 = 5,328 = 24,948 - 14,991 - 4,629
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed; the face line is custom 'Research, development and related expenses'
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R70.htm): 2026-11-12 R70.htm: agree: R70 gross interest expense 946; the face prints only 'Other expense (income), net'
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R92.htm): 2026-11-12 R92.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R77.htm): 2026-11-12 R77.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income (loss) from continuing operations before in' is the income_before_tax line, printed 4213000000 = filing XBRL 4213000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Earnings (loss) per share — basic (in dollars per ' is the basic_eps line, printed 6.05 = filing XBRL 6.05; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Weighted average 3M common shares outstanding - ba' is the weighted_basic_shares line, printed 537400000 = filing XBRL 537400000; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Accounts receivable — net of allowances of $61 and' is the accounts_receivable line, printed 3533000000 = filing XBRL 3533000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current assets' is the current_assets line, printed 16387000000 = filing XBRL 16387000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total 3M Company shareholders’ equity' is the stockholders_equity line, printed 4702000000 = filing XBRL 4702000000; agrees
