# MRSH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000062709-26-000022 (CIK 0000062709, filed 2026-02-09): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000062709-16-000040 (CIK 0000062709, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000062709-24-000016 (CIK 0000062709, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000062709-23-000014 (CIK 0000062709, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000062709.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 26981000000 | 26981000000 | 24458000000 | 24458000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1153 tags across all 107 R pages, face and notes) of 0000062709-26-000022; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1153 tags across all 107 R pages, face and notes) of 0000062709-26-000022; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Operating expenses | 20758000000 | 20758000000 | 18641000000 | 18641000000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1153 tags across all 107 R pages, face and notes) of 0000062709-26-000022; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1153 tags across all 107 R pages, face and notes) of 0000062709-26-000022; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 6223000000 | 6223000000 | 5817000000 | 5817000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -960000000 | 960000000 | -700000000 | 700000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 5539000000 | 5539000000 | 5480000000 | 5480000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 1305000000 | 1305000000 | 1363000000 | 1363000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to the Company | 4160000000 | 4160000000 | 4060000000 | 4060000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 8.48 | 8.48 | 8.26 | 8.26 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 8.43 | 8.43 | 8.18 | 8.18 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 491000000 | 491000000 | 492000000 | 492000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 494000000 | 494000000 | 496000000 | 496000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 2687000000 | 2687000000 | 2398000000 | 2398000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Net receivables | 7670000000 | 7670000000 | 7156000000 | 7156000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1153 tags across all 107 R pages, face and notes) of 0000062709-26-000022; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 23200000000 | 23200000000 | 22117000000 | 22117000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Fixed assets, net | 829000000 | 829000000 | 859000000 | 859000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 24337000000 | 24337000000 | 23306000000 | 23306000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 58710000000 | 58710000000 | 56481000000 | 56481000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued liabilities | 3652000000 | 3652000000 | 3402000000 | 3402000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 21060000000 | 21060000000 | 19518000000 | 19518000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1153 tags across all 107 R pages, face and notes) of 0000062709-26-000022; no face row matched |
| stockholders_equity | mapped | us-gaap:LiabilitiesAndStockholdersEquity | R5.htm | Total liabilities and stockholders' equity | 58710000000 | 58710000000 | 56481000000 | 56481000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000062709-26-000022 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used for) operations | 5292000000 | 5292000000 | 4302000000 | 4302000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used for) investing activities | -845000000 | -845000000 | -8821000000 | -8821000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used for) financing activities | -4634000000 | -4634000000 | 4455000000 | 4455000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -291000000 | 291000000 | -316000000 | 316000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:Depreciation | R7.htm | Depreciation and amortization of fixed assets and capitalized software | 361000000 | 361000000 | 369000000 | 369000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 394000000 | 394000000 | 368000000 | 368000000 | Y | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -1699000000 | 1699000000 | -1513000000 | 1513000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchase of treasury shares | -2012000000 | 2012000000 | -900000000 | 900000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000062709-26-000022 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R52.htm | Supplemental Disclosures to the Consolidated Statements of Cash Flows (Schedule of Supplemental Cash Flow Disclosures) ( |  | 885000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R52.htm 'Supplemental Disclosures to the Consolidated Statements of Cash Flows (Schedule ' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R53.htm | Supplemental Disclosures to the Consolidated Statements of Cash Flows (Schedule of Income Taxes Paid) (Details) |  | 1292000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R53.htm 'Supplemental Disclosures to the Consolidated Statements of Cash Flows (Schedule ' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt + Long-term debt | 19587000000 | 19587000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | CONSOLIDATED STATEMENTS OF INCOME |  | 485000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R3.htm 'CONSOLIDATED STATEMENTS OF INCOME' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Revenue' on us-gaap:SalesRevenueServicesNet = 12893000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Operating expenses' on us-gaap:OperatingExpenses = 10474000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 2419000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -163000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 2307000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 671000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Net income attributable to the Company' on us-gaap:NetIncomeLoss = 1599000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Net income attributable to the Company (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.01 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Net income attributable to the Company (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.98 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 531000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000062709-16-000040 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 536000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1374000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Net receivables' on us-gaap:ReceivablesNetCurrent = 3471000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 5044000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 773000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Goodwill' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 7889000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Total assets' on us-gaap:Assets = 18216000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 1886000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 3708000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000062709-16-000040 R4.htm prints 'Total liabilities and stockholders' equity' on us-gaap:LiabilitiesAndStockholdersEquity = 18216000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Net cash provided by operations' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1888000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1265000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Net cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -906000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -325000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Depreciation and amortization of fixed assets and capitalized software' on us-gaap:Depreciation = 314000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 88000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -632000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000062709-16-000040 R6.htm prints 'Purchase of treasury shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1400000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000062709-16-000040 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000062709-16-000040 R6.htm read; no row matched (auto)
- revenue: era 10-K 0000062709-24-000016 R3.htm prints 'Revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 22736000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000062709-24-000016 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -578000000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000062709-23-000014 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1442000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- sga_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R52.htm): 2026-11-12 R52.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R53.htm): 2026-11-12 R53.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating income' is the operating_income line, printed 6223000000 = filing XBRL 6223000000; agrees
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Interest expense' is the interest_expense line, printed -960000000 = filing XBRL 960000000; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net income attributable to the Company' is the net_income line, printed 4160000000 = filing XBRL 4160000000; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic (in shares)' is the weighted_basic_shares line, printed 491000000 = filing XBRL 491000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Fixed assets, net' is the ppe_net line, printed 829000000 = filing XBRL 829000000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Dividends paid' is the dividends_paid line, printed -1699000000 = filing XBRL 1699000000; agrees
