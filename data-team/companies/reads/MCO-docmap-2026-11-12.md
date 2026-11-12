# MCO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-009136 (CIK 0001059556, filed 2026-02-18): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001193125-16-476427 (CIK 0001059556, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001193125-18-058986 (CIK 0001059556, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001193125-19-048576 (CIK 0001059556, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001059556.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 7718000000 | 7718000000 | 7088000000 | 7088000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Operating | 1973000000 | 1973000000 | 1945000000 | 1945000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1174 tags across all 138 R pages, face and notes) of 0001628280-26-009136; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total expenses | 4367000000 | 4367000000 | 4213000000 | 4213000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 1803000000 | 1803000000 | 1735000000 | 1735000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1174 tags across all 138 R pages, face and notes) of 0001628280-26-009136; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 3351000000 | 3351000000 | 2875000000 | 2875000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest expense, net | -213000000 | -213000000 | -237000000 | -237000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before provision for income taxes | 3130000000 | 3130000000 | 2699000000 | 2699000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 668000000 | 668000000 | 640000000 | 640000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Moody’s | 2459000000 | 2459000000 | 2058000000 | 2058000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in USD per share) | 13.73 | 13.73 | 11.32 | 11.32 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in USD per share) | 13.67 | 13.67 | 11.26 | 11.26 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 179100000 | 179100000 | 181800000 | 181800000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 179900000 | 179900000 | 182700000 | 182700000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 2384000000 | 2384000000 | 2408000000 | 2408000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowances for credit losses of $29 in 2025 and $32 in 2024 | 2024000000 | 2024000000 | 1801000000 | 1801000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1174 tags across all 138 R pages, face and notes) of 0001628280-26-009136; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 5186000000 | 5186000000 | 5290000000 | 5290000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net of accumulated depreciation of $1,572 in 2025 and $1,453 in 2024 | 722000000 | 722000000 | 656000000 | 656000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 6368000000 | 6368000000 | 5994000000 | 5994000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 15830000000 | 15830000000 | 15505000000 | 15505000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued liabilities | 1304000000 | 1304000000 | 1344000000 | 1344000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 2981000000 | 2981000000 | 3597000000 | 3597000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 11625000000 | 11625000000 | 11778000000 | 11778000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Moody’s shareholders’ equity | 4054000000 | 4054000000 | 3565000000 | 3565000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 2901000000 | 2901000000 | 2838000000 | 2838000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | 2000000 | 2000000 | -1056000000 | -1056000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -3063000000 | -3063000000 | -1446000000 | -1446000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital additions | -326000000 | 326000000 | -317000000 | 317000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 480000000 | 480000000 | 431000000 | 431000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 232000000 | 232000000 | 220000000 | 220000000 | Y | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends | -701000000 | 701000000 | -620000000 | 620000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Treasury shares | -1607000000 | 1607000000 | -1292000000 | 1292000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009136 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R122.htm | Indebtedness - Summary of Components of Interest as Presented in Consolidated Statements of Operations (Detail) |  | 235000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R122.htm 'Indebtedness - Summary of Components of Interest as Presented in Consolidated St' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R113.htm | Income Taxes - Income Taxes Paid (Details) |  | 825000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R113.htm 'Income Taxes - Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Total long-term debt | 6994000000 | 6994000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 0 |  |  |  | API missing | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Revenue' on us-gaap:Revenues = 3484500000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-476427 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 2011100000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 921300000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1473400000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -115100000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1379600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 430000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Net income attributable to Moody's' on us-gaap:NetIncomeLoss = 941300000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 4.7 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 4.63 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 200100000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-476427 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 203400000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1757400000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Accounts receivable, net of allowances of $27.5 in 2015 and $29.4 in 2014' on us-gaap:AccountsReceivableNetCurrent = 802000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3243100000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 306400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 976300000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Total assets' on us-gaap:Assets = 5123400000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 566600000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1218500000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 5456400000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-476427 R4.htm prints 'Total Moody's shareholders' (deficit)' on us-gaap:StockholdersEquity = -565000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1153600000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -92000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -461000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Capital additions' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -89000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 113500000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 87200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Dividends' on us-gaap:PaymentsOfDividends = -272100000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-476427 R6.htm prints 'Treasury shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1098100000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-476427 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-476427 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001193125-18-058986 R2.htm prints 'Revenue' on us-gaap:Revenues = 4.204e+09 (FILING-CHECKED)
- operating_expenses: era 10-K 0001193125-19-048576 R2.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 2574500000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001193125-19-048576 R6.htm prints 'Dividends' on us-gaap:PaymentsOfDividends = -337200000 (FILING-CHECKED)

## Mismatches (printed vs API)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:DepreciationAndAmortization+us-gaap:RestructuringCharges+mco:ChargesRelatedToAssetAbandonment (R3.htm): 2026-11-12 R3.htm: corrected: opex = 1,803 + 480 + 108 + 3 = 2,394 = 7,718 - 1,973 - 3,351
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R122.htm): 2026-11-12 R122.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R113.htm): 2026-11-12 R113.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Revenue' is the revenue line, printed 7718000000 = filing XBRL 7718000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Property and equipment, net of accumulated depreci' is the ppe_net line, printed 722000000 = filing XBRL 722000000; agrees
- accounts_payable: combined us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent (R5.htm): 2026-11-12 R5.htm: sample DISAGREES: 'Accounts payable and accrued liabilities' bundles accrued liabilities: combined
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current liabilities' is the current_liabilities line, printed 2981000000 = filing XBRL 2981000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Capital additions' is the capex line, printed -326000000 = filing XBRL 326000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Treasury shares' is the share_buybacks line, printed -1607000000 = filing XBRL 1607000000; agrees
- interest_expense: combined check: hand 2026-11-12 R3.htm: 'Interest expense, net' on InterestIncomeExpenseNonoperatingNet is a net line: combined
