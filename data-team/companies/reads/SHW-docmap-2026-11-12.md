# SHW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000089800-26-000008 (CIK 0000089800, filed 2026-02-19): COVER R1.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000089800-16-000026 (CIK 0000089800, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000089800-20-000005 (CIK 0000089800, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000089800-19-000004 (CIK 0000089800, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000089800.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R121.htm | REPORTABLE SEGMENT INFORMATION - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R121.htm 'REPORTABLE SEGMENT INFORMATION - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R122.htm | REPORTABLE SEGMENT INFORMATION - Reportable Segment Financial Information (Details) |  | 12058800000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R122.htm 'REPORTABLE SEGMENT INFORMATION - Reportable Segment Financial Information (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | STATEMENTS OF CONSOLIDATED INCOME |  | 11515500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R3.htm 'STATEMENTS OF CONSOLIDATED INCOME' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1161 tags across all 123 R pages, face and notes) of 0000089800-26-000008; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R122.htm | REPORTABLE SEGMENT INFORMATION - Reportable Segment Financial Information (Details) |  | 7695000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R122.htm 'REPORTABLE SEGMENT INFORMATION - Reportable Segment Financial Information (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R57.htm | SIGNIFICANT ACCOUNTING POLICIES - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R57.htm 'SIGNIFICANT ACCOUNTING POLICIES - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| operating_income | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1161 tags across all 123 R pages, face and notes) of 0000089800-26-000008; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R122.htm | REPORTABLE SEGMENT INFORMATION - Reportable Segment Financial Information (Details) |  | 465000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R122.htm 'REPORTABLE SEGMENT INFORMATION - Reportable Segment Financial Information (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R115.htm | INCOME TAXES - Schedule of Significant Components of Income Before Income Taxes as Used for Income Tax Purposes (Details |  | 3338200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R115.htm 'INCOME TAXES - Schedule of Significant Components of Income Before Income Taxes ' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R113.htm | INCOME TAXES - Schedule of Significant Components of the Provisions for Income Taxes (Details) |  | 769700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R113.htm 'INCOME TAXES - Schedule of Significant Components of the Provisions for Income T' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R120.htm | NET INCOME PER SHARE (Details) |  | 2568500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R120.htm 'NET INCOME PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R120.htm | NET INCOME PER SHARE (Details) |  | 10.37 |  |  |  | FILING-CHECKED | not on the face statement; shown in R120.htm 'NET INCOME PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R120.htm | NET INCOME PER SHARE (Details) |  | 10.26 |  |  |  | FILING-CHECKED | not on the face statement; shown in R120.htm 'NET INCOME PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R120.htm | NET INCOME PER SHARE (Details) |  | 247600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R120.htm 'NET INCOME PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R120.htm | NET INCOME PER SHARE (Details) |  | 250400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R120.htm 'NET INCOME PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 207200000 | 207200000 | 210400000 | 210400000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 2791200000 | 2791200000 | 2388800000 | 2388800000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 2318200000 | 2318200000 | 2288100000 | 2288100000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 6007400000 | 6007400000 | 5400800000 | 5400800000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 4137400000 | 4137400000 | 3533200000 | 3533200000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 8036600000 | 8036600000 | 7580100000 | 7580100000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 25901700000 | 25901700000 | 23632600000 | 23632600000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2354200000 | 2354200000 | 2253200000 | 2253200000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 6920300000 | 6920300000 | 6808700000 | 6808700000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1161 tags across all 123 R pages, face and notes) of 0000089800-26-000008; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders’ equity | 4598300000 | 4598300000 | 4051200000 | 4051200000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net operating cash | 3451600000 | 3451600000 | 3153200000 | 3153200000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net investing cash | -2066300000 | -2066300000 | -1196300000 | -1196300000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net financing cash | -1378600000 | -1378600000 | -2017100000 | -2017100000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -797600000 | 797600000 | -1070000000 | 1070000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R7.htm | Depreciation + Amortization of intangible assets | 676900000 | 676900000 | 624000000 | 624000000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 123500000 | 123500000 | 138100000 | 138100000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Payments of cash dividends | -789800000 | 789800000 | -723400000 | 723400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1161 tags across all 123 R pages, face and notes) of 0000089800-26-000008; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | 453000000 | 453000000 | 406900000 | 406900000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R7.htm | Income taxes paid | 592700000 | 592700000 | 779800000 | 779800000 | Y | FILING-CHECKED | accn 0000089800-26-000008 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings + Current portion of long-term debt + Long-term debt | 1.087e+10 | 10871300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 247700000 | 247700000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 11339304000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfRevenue = 5780078000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 5559226000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 3913518000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000089800-16-000026 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 61791000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1548966000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 495117000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 1053849000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 11.38 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000089800-16-000026 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 11.16 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000089800-16-000026 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000089800-16-000026 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 205744000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Accounts receivable, less allowance' on us-gaap:AccountsReceivableNetCurrent = 1114275000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Total inventory' on us-gaap:InventoryNet = 1018530000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2658874000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Total net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 1041862000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1143333000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Total Assets' on us-gaap:Assets = 5791855000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1157561000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2141859000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000089800-16-000026 R4.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 867910000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Net operating cash' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1447463000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Net investing cash' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -288633000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Net financing cash' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -980353000 (FILING-CHECKED)
- capex: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -234340000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000089800-16-000026 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 72342000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Payments of cash dividends' on us-gaap:PaymentsOfDividends = -249647000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Interest paid on debt' on us-gaap:InterestPaid = 48644000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000089800-16-000026 R6.htm prints 'Taxes paid on income' on us-gaap:IncomeTaxesPaid = 335119000 (FILING-CHECKED)
- revenue: era 10-K 0000089800-20-000005 R2.htm prints 'Net sales' on us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax = 17900800000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000089800-19-000004 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfRevenue = 10115931000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000089800-19-000004 R6.htm prints 'Interest paid on debt' on us-gaap:InterestPaid = 368045000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R3.htm): 2026-11-12 R3.htm: corrected (tool error: the IS title 'STATEMENTS OF CONSOLIDATED INCOME' uses non-breaking spaces and was missed): R3 face
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServicesSold (R3.htm): 2026-11-12 R3.htm: corrected: R3 face (IS title missed by the tool)
- operating_expenses: not_presented  (): 2026-11-12 : agree: R3 prints no operating income line, so no tie is possible
- sga_expense: mapped us-gaap:SellingGeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R57.htm): 2026-11-12 R57.htm: decided by R57: 'Research and development costs' 224.8, all charged to cost of goods sold: the total R&D
- operating_income: not_presented  (): 2026-11-12 : agree: R3 prints no operating income line
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- diluted_eps: mapped us-gaap:EarningsPerShareDiluted (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R3.htm): 2026-11-12 R3.htm: corrected: R3 face
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets (R7.htm): 2026-11-12 R7.htm: agree: CF R7 depreciation + amortization of intangible assets
- share_buybacks: not_presented  (R7.htm): 2026-11-12 R7.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Accounts receivable, net' is the accounts_receivable line, printed 2791200000 = filing XBRL 2791200000; agrees
- inventory: mapped us-gaap:InventoryNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Inventories' is the inventory line, printed 2318200000 = filing XBRL 2318200000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Net investing cash' is the cash_flow_investing line, printed -2066300000 = filing XBRL -2066300000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Stock-based compensation expense' is the sbc line, printed 123500000 = filing XBRL 123500000; agrees
- total_debt: corrected per finance-lease ruling (founder 2026-11-04 item 5): R83.htm: finance leases sit in 'Other accruals' (0.7) and 'Other long-term liabilities' (194.7), outside the debt lines: 1,200.5 + 350.1 + 9,320.7 + 0.7 + 194.7 = 11,066.7
