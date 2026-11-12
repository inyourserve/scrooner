# OGE document-first map 2026-11-12 (rank 705, read-only)

Evidence: FILING-CHECKED unless a row says otherwise. Printed values come from the R pages of the 10-K on sec.gov; tags from each R-page row's element reference; API = SEC companyfacts (undimensioned, same accession, same period); FSN = our fsn.line rows for the same filing and report.

Company: OGE ENERGY CORP. (CIK 0001021635); sector shape read from the face: general.

## Filings opened
- Latest 10-K 0001193125-26-055414 (index from FSN store (fsn.filing, fsn.report)): R2.htm CONSOLIDATED STATEMENTS OF INCOME AND COMPREHENSIVE INCOME [IS], R3.htm CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME [CI], R4.htm CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (Parenthetical) [CIP], R5.htm CONSOLIDATED STATEMENTS OF CASH FLOWS [CF], R7.htm CONSOLIDATED BALANCE SHEETS [BS], R8.htm CONSOLIDATED BALANCE SHEETS (Parenthetical) [BSP], R10.htm CONSOLIDATED STATEMENTS OF CAPITALIZATION (Parenthetical) [EQP].
- Era 10-K 0001021635-16-000172 (FY2015): R2.htm CONSOLIDATED STATEMENTS OF INCOME, R3.htm CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME, R5.htm CONSOLIDATED STATEMENTS OF CASH FLOWS, R6.htm CONSOLIDATED BALANCE SHEETS, R9.htm CONSOLIDATED STATEMENTS OF CAPITALIZATION (Parenthetical).
- Era 10-K 0001021635-13-000018 (FY2017): .
- Era 10-K 0000950170-23-003858 (FY2022): R2.htm CONSOLIDATED STATEMENTS OF INCOME, R3.htm CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME, R5.htm CONSOLIDATED STATEMENTS OF CASH FLOWS, R7.htm CONSOLIDATED BALANCE SHEETS, R10.htm CONSOLIDATED STATEMENTS OF CAPITALIZATION (Parenthetical).
- Era 10-K 0001021635-22-000037 (FY2021): R4.htm CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME, R6.htm CONSOLIDATED STATEMENTS OF CASH FLOWS, R7.htm CONSOLIDATED BALANCE SHEETS.
- companyfacts: one call to data.sec.gov.
- sec.gov requests for this company: 0.

FY0 = the latest fiscal-year column, FY1 = the prior year. Values in full units (printed value × the R-page scale); EPS per share; shares in shares.

## Data points (the CSV holds exactly these rows)
| data point | status | tag(s) | R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match |
|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | R2.htm | Operating revenues | 3260100000 | 3260100000 | 2985300000 | 2985300000 | Y |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | R2.htm | FUEL, PURCHASED POWER AND DIRECT TRANSMISSION EXPENSE | 1259900000 | 1259900000 | 1076400000 | 1076400000 | Y |
| gross_profit | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| operating_expenses | mapped | OperatingExpenses | R2.htm | Operating expenses | 1200800000 | 1200800000 | 1163600000 | 1163600000 | Y |
| sga_expense | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| research_and_development | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| operating_income | mapped | OperatingIncomeLoss | R2.htm | OPERATING INCOME | 799400000 | 799400000 | 745300000 | 745300000 | Y |
| interest_expense | mapped | InterestExpense | R2.htm | Interest expense | 270300000 | 270300000 | 254500000 | 254500000 | Y |
| interest_income | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| other_income_expense_net | mapped | NonoperatingIncomeExpense | R2.htm | Net other income | 31400000 | 31400000 | 29800000 | 29800000 | Y |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | INCOME BEFORE TAXES | 560500000 | 560500000 | 520600000 | 520600000 | Y |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R2.htm | INCOME TAX EXPENSE | 89800000 | 89800000 | 79100000 | 79100000 | Y |
| net_income | mapped | NetIncomeLoss | R2.htm | NET INCOME | 470700000 | 470700000 | 441500000 | 441500000 | Y |
| basic_eps | mapped | EarningsPerShareBasic | R2.htm | BASIC EARNINGS PER AVERAGE COMMON SHARE | 2.33 | 2.33 | 2.2 | 2.2 | Y |
| diluted_eps | mapped | EarningsPerShareDiluted | R2.htm | DILUTED EARNINGS PER AVERAGE COMMON SHARE | 2.32 | 2.32 | 2.19 | 2.19 | Y |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | BASIC AVERAGE COMMON SHARES OUTSTANDING | 201900000 | 201900000 | 200800000 | 200800000 | Y |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | DILUTED AVERAGE COMMON SHARES OUTSTANDING | 202500000 | 202500000 | 201300000 | 201300000 | Y |
| dividends_per_share | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R3.htm | Comprehensive income | 470800000 | 470800000 | 446000000 | 446000000 | Y |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | R7.htm | Cash and cash equivalents | 200000 | 200000 | 600000 | 600000 | Y |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | R7.htm | Accounts receivable | 347800000 | 347800000 | 240600000 | 240600000 | Y |
| inventory | mapped | InventoryNet | R7.htm | Fuel inventories | 112000000 | 112000000 | 148300000 | 148300000 | Y |
| current_assets | mapped | AssetsCurrent | R7.htm | Total current assets | 857900000 | 857900000 | 895100000 | 895100000 | Y |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | R7.htm | Net property, plant and equipment | 12730400000 | 12730400000 | 12086600000 | 12086600000 | Y |
| goodwill | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| total_assets | mapped | Assets | R7.htm | TOTAL ASSETS | 14370500000 | 14370500000 | 13716000000 | 13716000000 | Y |
| accounts_payable | mapped | AccountsPayableCurrent | R7.htm | Accounts payable | 350600000 | 350600000 | 305700000 | 305700000 | Y |
| current_liabilities | mapped | LiabilitiesCurrent | R7.htm | Total current liabilities | 1094100000 | 1094100000 | 1229800000 | 1229800000 | Y |
| total_liabilities | mapped | Liabilities | R7.htm | Total liabilities | 9393200000 | 9393200000 | 9075100000 | 9075100000 | Y |
| total_debt | component sum | ShortTermBorrowings;LongTermDebtCurrent;LongTermDebtNoncurrent | R7.htm | Short-term debt + Long-term debt due within one year + LONG-TERM DEBT | 5661200000 | 5661200000 | 5522600000 | 5522600000 | Y |
| stockholders_equity | mapped | StockholdersEquity | R7.htm | Total stockholder's equity | 4977300000 | 4977300000 | 4640900000 | 4640900000 | Y |
| shares_outstanding | mapped | CommonStockSharesOutstanding | R10.htm | Common Stock, Shares, Outstanding | 206100000 |  |  |  | no companyfacts fact |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R5.htm | Net cash provided from operating activities | 1137100000 | 1137100000 | 812800000 | 812800000 | Y |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used in investing activities | -1126600000 | -1126600000 | -1161200000 | -1161200000 | Y |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash (used in) provided from financing activities | -10900000 | -10900000 | 348800000 | 348800000 | Y |
| capex | mapped | PaymentsToAcquireProductiveAssets | R5.htm | Capital expenditures (less allowance for equity funds used during cons | -1054400000 | 1054400000 | -1090900000 | 1090900000 | Y (sign differs: printed in parentheses/negated label) |
| depreciation_and_amortization | mapped | DepreciationAmortizationAndAccretionNet | R5.htm | Depreciation and amortization | 559800000 | 559800000 | 539500000 | 539500000 | Y |
| amortization_of_intangibles | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| sbc | mapped | ShareBasedCompensation | R5.htm | Stock-based compensation expense | 14000000 | 14000000 | 11700000 | 11700000 | Y |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | R5.htm | Dividends paid on common stock | -341900000 | 341900000 | -338500000 | 338500000 | Y (sign differs: printed in parentheses/negated label) |
| share_buybacks | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | R5.htm | Accounts receivable and accrued unbilled revenues, net | -108800000 | 108800000 | -33600000 | 33600000 | Y (sign differs: printed in parentheses/negated label) |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | R5.htm | Fuel, materials and supplies inventories | 81900000 | -81900000 | 25700000 | -25700000 | Y (sign differs: printed in parentheses/negated label) |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | R5.htm | Accounts payable | 34900000 | 34900000 | -14700000 | -14700000 | Y |
| cash_paid_for_interest | mapped | InterestPaidNet | R5.htm | Interest (net of interest capitalized) | 268700000 | 268700000 | 251100000 | 251100000 | Y |
| cash_paid_for_income_taxes | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| net_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| total_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_expense | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| provision_for_credit_losses | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| deposits | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| loans_net | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |

Sector lines also on the face (not in the graded vocabulary): net_income_incl_nci = ProfitLoss 'Net income' 470700000.

## Eras FY2015 to FY2025 (every data point; companyfacts tag per original 10-K, and the era 10-Ks opened: FY2015 always, plus the last 10-K of each earlier era)
| data point | latest status | eras (companyfacts) | era 10-K reads (FILING-CHECKED) | coverage |
|---|---|---|---|---|
| revenue | mapped | FY2015-FY2015: Revenues; FY2016-FY2017: no standard tag; FY2018-FY2025: Revenues | FY2015 10-K 0001021635-16-000172 R2.htm 'Total operating revenues' Revenues (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'Operating revenues' Revenues (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cost_of_revenue | mapped | FY2015-FY2015: CostOfGoodsAndServicesSold; FY2016-FY2017: no standard tag; FY2018-FY2025: CostOfGoodsAndServicesSold | FY2015 10-K 0001021635-16-000172 R2.htm 'Total cost of sales' CostOfGoodsAndServicesSold (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'FUEL, PURCHASED POWER AND DIRECT TRANSMI' CostOfGoodsAndServicesSold (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| operating_expenses | mapped | FY2015-FY2015: OperatingExpenses; FY2016-FY2017: no standard tag; FY2018-FY2025: OperatingExpenses | FY2015 10-K 0001021635-16-000172 R2.htm 'Total operating expenses' OperatingExpenses (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'Operating expenses' OperatingExpenses (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| operating_income | mapped | FY2015-FY2015: OperatingIncomeLoss; FY2016-FY2017: no standard tag; FY2018-FY2025: OperatingIncomeLoss | FY2015 10-K 0001021635-16-000172 R2.htm 'Operating income (loss)' OperatingIncomeLoss (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'OPERATING INCOME' OperatingIncomeLoss (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| interest_expense | mapped | FY2015-FY2015: InterestExpense; FY2016-FY2017: no standard tag; FY2018-FY2025: InterestExpense | FY2015 10-K 0001021635-16-000172 R2.htm 'Interest expense' InterestExpense (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'Interest expense' InterestExpense (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| other_income_expense_net | mapped | FY2015-FY2015: OtherNonoperatingIncomeExpense; FY2016-FY2017: no standard tag; FY2018-FY2025: OtherNonoperatingIncomeExpense | FY2015 10-K 0001021635-16-000172 R2.htm 'Net other income' NonoperatingIncomeExpense (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'Net other income (expense)' NonoperatingIncomeExpense (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| income_before_tax | mapped | FY2015-FY2015: IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest; FY2016-FY2017: no standard tag; FY2018-FY2025: IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | FY2015 10-K 0001021635-16-000172 R2.htm 'INCOME BEFORE TAXES' IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'INCOME (LOSS) BEFORE TAXES' IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| income_tax_expense | mapped | FY2015-FY2015: IncomeTaxExpenseBenefit; FY2016-FY2017: no standard tag; FY2018-FY2025: IncomeTaxExpenseBenefit | FY2015 10-K 0001021635-16-000172 R2.htm 'INCOME TAX EXPENSE' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'INCOME TAX EXPENSE (BENEFIT)' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| net_income | mapped | FY2015-FY2015: NetIncomeLoss; FY2016-FY2017: no standard tag; FY2018-FY2022: ProfitLoss; FY2023-FY2025: NetIncomeLoss | FY2015 10-K 0001021635-16-000172 R2.htm 'NET INCOME ATTRIBUTABLE TO OGE ENERGY' NetIncomeLoss (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'NET INCOME (LOSS)' ProfitLoss (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R4.htm 'Net income (loss)' ProfitLoss (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| basic_eps | mapped | FY2015-FY2015: EarningsPerShareBasic; FY2016-FY2017: no standard tag; FY2018-FY2025: EarningsPerShareBasic | FY2015 10-K 0001021635-16-000172 R2.htm 'BASIC EARNINGS PER AVERAGE COMMON SHARE ' EarningsPerShareBasic (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'BASIC EARNINGS (LOSS) PER AVERAGE COMMON' EarningsPerShareBasic (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| diluted_eps | mapped | FY2015-FY2015: EarningsPerShareDiluted; FY2016-FY2017: no standard tag; FY2018-FY2025: EarningsPerShareDiluted | FY2015 10-K 0001021635-16-000172 R2.htm 'DILUTED EARNINGS PER AVERAGE COMMON SHAR' EarningsPerShareDiluted (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'DILUTED EARNINGS (LOSS) PER AVERAGE COMM' EarningsPerShareDiluted (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| weighted_basic_shares | mapped | FY2015-FY2015: WeightedAverageNumberOfSharesOutstandingBasic; FY2016-FY2017: no standard tag; FY2018-FY2025: WeightedAverageNumberOfSharesOutstandingBasic | FY2015 10-K 0001021635-16-000172 R2.htm 'BASIC AVERAGE COMMON SHARES OUTSTANDING' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'BASIC AVERAGE COMMON SHARES OUTSTANDING' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| weighted_diluted_shares | mapped | FY2015-FY2015: WeightedAverageNumberOfDilutedSharesOutstanding; FY2016-FY2017: no standard tag; FY2018-FY2025: WeightedAverageNumberOfDilutedSharesOutstanding | FY2015 10-K 0001021635-16-000172 R2.htm 'DILUTED AVERAGE COMMON SHARES OUTSTANDIN' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R2.htm 'DILUTED AVERAGE COMMON SHARES OUTSTANDIN' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| comprehensive_income | mapped | FY2015-FY2015: ComprehensiveIncomeNetOfTax; FY2016-FY2017: no standard tag; FY2018-FY2021: ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest; FY2022-FY2025: ComprehensiveIncomeNetOfTax | FY2015 10-K 0001021635-16-000172 R3.htm 'Total comprehensive income attributable ' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R3.htm 'Comprehensive income (loss)' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R4.htm 'Comprehensive income (loss)' ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cash_and_equivalents | mapped | FY2015-FY2015: CashAndCashEquivalentsAtCarryingValue; FY2016-FY2017: no standard tag; FY2018-FY2025: CashAndCashEquivalentsAtCarryingValue | FY2015 10-K 0001021635-16-000172 R6.htm 'Cash and cash equivalents' CashAndCashEquivalentsAtCarryingValue (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Cash and cash equivalents' CashAndCashEquivalentsAtCarryingValue (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Cash and cash equivalents' CashAndCashEquivalentsAtCarryingValue (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| accounts_receivable | mapped | FY2015-FY2015: AccountsReceivableNetCurrent; FY2016-FY2017: no standard tag; FY2018-FY2025: AccountsReceivableNetCurrent | FY2015 10-K 0001021635-16-000172 R6.htm 'Accounts receivable, less reserve of $1.' AccountsReceivableNetCurrent (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Accounts receivable' AccountsReceivableNetCurrent (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Accounts receivable, after allowance for' AccountsReceivableNetCurrent (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| inventory | mapped | FY2015-FY2015: InventoryNet; FY2016-FY2017: no standard tag; FY2018-FY2025: InventoryNet | FY2015 10-K 0001021635-16-000172 R6.htm 'Fuel inventories' InventoryNet (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Fuel inventories' InventoryNet (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Fuel inventories' InventoryNet (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| current_assets | mapped | FY2015-FY2015: AssetsCurrent; FY2016-FY2017: no standard tag; FY2018-FY2025: AssetsCurrent | FY2015 10-K 0001021635-16-000172 R6.htm 'Total current assets' AssetsCurrent (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Total current assets' AssetsCurrent (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Total current assets' AssetsCurrent (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| ppe_net | mapped | FY2015-FY2015: PropertyPlantAndEquipmentNet; FY2016-FY2017: no standard tag; FY2018-FY2025: PropertyPlantAndEquipmentNet | FY2015 10-K 0001021635-16-000172 R6.htm 'Net property, plant and equipment' PropertyPlantAndEquipmentNet (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Net property, plant and equipment' PropertyPlantAndEquipmentNet (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Net property, plant and equipment' PropertyPlantAndEquipmentNet (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| total_assets | mapped | FY2015-FY2015: Assets; FY2016-FY2017: no standard tag; FY2018-FY2025: Assets | FY2015 10-K 0001021635-16-000172 R6.htm 'TOTAL ASSETS' Assets (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'TOTAL ASSETS' Assets (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'TOTAL ASSETS' Assets (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| accounts_payable | mapped | FY2015-FY2015: AccountsPayableCurrent; FY2016-FY2017: no standard tag; FY2018-FY2025: AccountsPayableCurrent | FY2015 10-K 0001021635-16-000172 R6.htm 'Accounts payable' AccountsPayableCurrent (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Accounts payable' AccountsPayableCurrent (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Accounts payable' AccountsPayableCurrent (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| current_liabilities | mapped | FY2015-FY2015: LiabilitiesCurrent; FY2016-FY2017: no standard tag; FY2018-FY2025: LiabilitiesCurrent | FY2015 10-K 0001021635-16-000172 R6.htm 'Total current liabilities' LiabilitiesCurrent (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Total current liabilities' LiabilitiesCurrent (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Total current liabilities' LiabilitiesCurrent (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| total_liabilities | mapped | FY2015-FY2015: Liabilities; FY2016-FY2017: no standard tag; FY2018-FY2025: Liabilities | FY2015 10-K 0001021635-16-000172 R6.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| total_debt | component sum | FY2015-FY2015: ShortTermBorrowings+LongTermDebtCurrent+LongTermDebtNoncurrent+LongTermDebt+LineOfCredit; FY2016-FY2017: no standard tag; FY2018-FY2025: ShortTermBorrowings+LongTermDebtCurrent+LongTermDebtNoncurrent+LongTermDebt+LineOfCredit | FY2015 10-K 0001021635-16-000172 R6.htm 'Short-term debt' ShortTermBorrowings;LongTermDebtCurrent;LongTermDebtNoncurrent (component sum) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Short-term debt' ShortTermBorrowings;LongTermDebtCurrent;LongTermDebtNoncurrent (component sum) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Short-term debt' ShortTermBorrowings;LongTermDebtCurrent;LongTermDebtNoncurrent (component sum) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| stockholders_equity | mapped | FY2015-FY2015: StockholdersEquity; FY2016-FY2017: no standard tag; FY2018-FY2025: StockholdersEquity | FY2015 10-K 0001021635-16-000172 R6.htm 'Total stockholders' equity' StockholdersEquity (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R7.htm 'Total stockholders' equity' StockholdersEquity (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R7.htm 'Stockholders' Equity Attributable to Par' StockholdersEquity (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| shares_outstanding | mapped | FY2015-FY2015: CommonStockSharesOutstanding; FY2016-FY2017: no standard tag; FY2018-FY2025: CommonStockSharesOutstanding | FY2015 10-K 0001021635-16-000172: no face line; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858: no face line; FY2021 10-K 0001021635-22-000037: no face line | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cfo | mapped | FY2015-FY2015: NetCashProvidedByUsedInOperatingActivities; FY2016-FY2017: no standard tag; FY2018-FY2025: NetCashProvidedByUsedInOperatingActivities | FY2015 10-K 0001021635-16-000172 R5.htm 'Net Cash Provided from Operating Activit' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Net cash provided from (used in) operati' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Net cash (used in) provided from operati' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cash_flow_investing | mapped | FY2015-FY2015: NetCashProvidedByUsedInInvestingActivities; FY2016-FY2017: no standard tag; FY2018-FY2025: NetCashProvidedByUsedInInvestingActivities | FY2015 10-K 0001021635-16-000172 R5.htm 'Net Cash Used in Investing Activities' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Net cash used in investing activities' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Net cash used in investing activities' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cash_flow_financing | mapped | FY2015-FY2015: NetCashProvidedByUsedInFinancingActivities; FY2016-FY2017: no standard tag; FY2018-FY2025: NetCashProvidedByUsedInFinancingActivities | FY2015 10-K 0001021635-16-000172 R5.htm 'Net Cash (Used in) Provided From Financi' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Net cash (used in) provided from financi' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Net cash provided from (used in) financi' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| capex | mapped | FY2015-FY2015: PaymentsToAcquireProductiveAssets; FY2016-FY2017: no standard tag; FY2018-FY2025: PaymentsToAcquireProductiveAssets | FY2015 10-K 0001021635-16-000172 R5.htm 'Capital expenditures (less allowance for' PaymentsToAcquireProductiveAssets (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Capital expenditures (less allowance for' PaymentsToAcquireProductiveAssets (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Capital expenditures (less allowance for' PaymentsToAcquireProductiveAssets (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| depreciation_and_amortization | mapped | FY2015-FY2015: DepreciationAndAmortization; FY2016-FY2017: no standard tag; FY2018-FY2025: DepreciationAndAmortization | FY2015 10-K 0001021635-16-000172 R5.htm 'Depreciation and amortization' DepreciationAmortizationAndAccretionNet (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Depreciation and amortization' DepreciationAmortizationAndAccretionNet (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Depreciation and amortization' DepreciationAmortizationAndAccretionNet (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| sbc | mapped | FY2015-FY2015: ShareBasedCompensation; FY2016-FY2017: no standard tag; FY2018-FY2025: ShareBasedCompensation | FY2015 10-K 0001021635-16-000172 R5.htm 'Stock-based compensation' ShareBasedCompensation (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Stock-based compensation expense' ShareBasedCompensation (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Stock-based compensation expense' ShareBasedCompensation (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| dividends_paid | mapped | FY2015-FY2015: PaymentsOfDividendsCommonStock; FY2016-FY2017: no standard tag; FY2018-FY2025: PaymentsOfDividendsCommonStock | FY2015 10-K 0001021635-16-000172 R5.htm 'Dividends paid on common stock' PaymentsOfDividendsCommonStock (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Dividends paid on common stock' PaymentsOfDividendsCommonStock (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Dividends paid on common stock' PaymentsOfDividendsCommonStock (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cf_ar_change | mapped | FY2015-FY2015: IncreaseDecreaseInAccountsReceivable; FY2016-FY2017: no standard tag; FY2018-FY2025: IncreaseDecreaseInAccountsReceivable | FY2015 10-K 0001021635-16-000172 R5.htm 'Accounts receivable, net' IncreaseDecreaseInAccountsReceivable (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Accounts receivable and accrued unbilled' IncreaseDecreaseInAccountsReceivable (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Accounts receivable and accrued unbilled' IncreaseDecreaseInAccountsReceivable (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cf_inventory_change | mapped | FY2015-FY2015: IncreaseDecreaseInInventories; FY2016-FY2017: no standard tag; FY2018-FY2025: IncreaseDecreaseInInventories | FY2015 10-K 0001021635-16-000172 R5.htm 'Fuel, materials and supplies inventories' IncreaseDecreaseInInventories (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Fuel, materials and supplies inventories' IncreaseDecreaseInInventories (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Fuel, materials and supplies inventories' IncreaseDecreaseInInventories (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cf_ap_change | mapped | FY2015-FY2015: IncreaseDecreaseInAccountsPayable; FY2016-FY2017: no standard tag; FY2018-FY2025: IncreaseDecreaseInAccountsPayable | FY2015 10-K 0001021635-16-000172 R5.htm 'Accounts payable' IncreaseDecreaseInAccountsPayable (mapped) FILING-CHECKED; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Accounts payable' IncreaseDecreaseInAccountsPayable (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Accounts payable' IncreaseDecreaseInAccountsPayable (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cash_paid_for_interest | mapped | FY2015-FY2015: InterestPaidNet; FY2016-FY2017: no standard tag; FY2018-FY2025: InterestPaidNet | FY2015 10-K 0001021635-16-000172: no face line; FY2017 10-K 0001021635-13-000018: no face line; FY2022 10-K 0000950170-23-003858 R5.htm 'Interest (net of interest capitalized)' InterestPaidNet (mapped) FILING-CHECKED; FY2021 10-K 0001021635-22-000037 R6.htm 'Interest (net of interest capitalized)' InterestPaidNet (mapped) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2016,2017 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |

## Quirks and mismatches (the filing decides)
- [era_change] net_income: NetIncomeLoss -> ProfitLoss 'NET INCOME' — tag switch between the FY2015 10-K (0001021635-16-000172) and the FY2018 10-K (0000950170-23-003858) (0001021635-16-000172  FY2015 -> FY2018)
- [era_change] net_income: ProfitLoss -> NetIncomeLoss 'NET INCOME' — tag switch between the FY2022 10-K (0000950170-23-003858) and the FY2023 10-K (0001193125-26-055414) (0000950170-23-003858  FY2022 -> FY2023)
- [era_change] comprehensive_income: ComprehensiveIncomeNetOfTax -> ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest 'Comprehensive income' — tag switch between the FY2015 10-K (0001021635-16-000172) and the FY2018 10-K (0001021635-22-000037) (0001021635-16-000172  FY2015 -> FY2018)
- [era_change] comprehensive_income: ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest -> ComprehensiveIncomeNetOfTax 'Comprehensive income' — tag switch between the FY2021 10-K (0001021635-22-000037) and the FY2022 10-K (0001193125-26-055414) (0001021635-22-000037  FY2021 -> FY2022)
- [fsn_line_missing] : OtherComprehensiveIncomeAmortizationOfDefinedBenefitPensionPlansNetPriorServiceCostRecognizedinNetPeriodicPensionCostTax;OtherComprehensiveIncomeDefinedBenefitPlansNetUnamortizedGainLossArisingDuringPeriodTax;OtherComprehensiveIncomeFinalizationOfPensionAndNonPensionPostretirementPlanValuationTax;Ot '' — 7 R-page line(s) whose tag is not an FSN line of the same report (fsn.line) (0001193125-26-055414 R4.htm )

## Every face line (printed page → tag → FSN → companyfacts)
| R | stmt | # | label | tag | member | FY0 printed | FY0 API | match | in FSN |
|---|---|---|---|---|---|---|---|---|---|
| R2.htm | IS | 1 | Revenues from contracts with customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |  | 3190900000 | 3190900000 | Y | Y |
| R2.htm | IS | 2 | Other revenues | oge:RevenuesfromAlternativeRevenuePrograms |  | 69200000 |  | custom | Y |
| R2.htm | IS | 3 | Operating revenues | us-gaap:Revenues |  | 3260100000 | 3260100000 | Y | Y |
| R2.htm | IS | 4 | FUEL, PURCHASED POWER AND DIRECT TRANSMISSION EXPENSE | us-gaap:CostOfGoodsAndServicesSold |  | 1259900000 | 1259900000 | Y | Y |
| R2.htm | IS | 5 | Other operation and maintenance | us-gaap:OtherCostAndExpenseOperating |  | 531600000 | 531600000 | Y | Y |
| R2.htm | IS | 6 | Depreciation and amortization | us-gaap:DepreciationAndAmortization |  | 559800000 | 559800000 | Y | Y |
| R2.htm | IS | 7 | Taxes other than income | us-gaap:TaxesExcludingIncomeAndExciseTaxes |  | 109400000 | 109400000 | Y | Y |
| R2.htm | IS | 8 | Operating expenses | us-gaap:OperatingExpenses |  | 1200800000 | 1200800000 | Y | Y |
| R2.htm | IS | 9 | OPERATING INCOME | us-gaap:OperatingIncomeLoss |  | 799400000 | 799400000 | Y | Y |
| R2.htm | IS | 10 | Allowance for equity funds used during construction | us-gaap:PublicUtilitiesAllowanceForFundsUsedDuringConstructionCapitalizedCostOfEquity |  | 26000000 | 26000000 | Y | Y |
| R2.htm | IS | 11 | Other net periodic benefit (expense) income | us-gaap:PensionAndOtherPostretirementBenefitExpense |  | -11000000 | 11000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R2.htm | IS | 12 | Other income | us-gaap:OtherNonoperatingIncome |  | 39400000 | 39400000 | Y | Y |
| R2.htm | IS | 13 | Other expense | us-gaap:OtherNonoperatingExpense |  | -23000000 | 23000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R2.htm | IS | 14 | Net other income | us-gaap:NonoperatingIncomeExpense |  | 31400000 | 31400000 | Y | Y |
| R2.htm | IS | 15 | Interest on long-term debt | us-gaap:InterestExpenseLongTermDebt |  | 261000000 | 261000000 | Y | Y |
| R2.htm | IS | 16 | Allowance for borrowed funds used during construction | us-gaap:PublicUtilitiesAllowanceForFundsUsedDuringConstructionAdditions |  | -15800000 | 15800000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R2.htm | IS | 17 | Interest on short-term debt and other interest charges | us-gaap:InterestExpenseShortTermBorrowings |  | 25100000 | 25100000 | Y | Y |
| R2.htm | IS | 18 | Interest expense | us-gaap:InterestExpense |  | 270300000 | 270300000 | Y | Y |
| R2.htm | IS | 19 | INCOME BEFORE TAXES | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |  | 560500000 | 560500000 | Y | Y |
| R2.htm | IS | 20 | INCOME TAX EXPENSE | us-gaap:IncomeTaxExpenseBenefit |  | 89800000 | 89800000 | Y | Y |
| R2.htm | IS | 21 | NET INCOME | us-gaap:NetIncomeLoss |  | 470700000 | 470700000 | Y | Y |
| R2.htm | IS | 22 | BASIC AVERAGE COMMON SHARES OUTSTANDING | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic |  | 201900000 | 201900000 | Y | Y |
| R2.htm | IS | 23 | DILUTED AVERAGE COMMON SHARES OUTSTANDING | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding |  | 202500000 | 202500000 | Y | Y |
| R2.htm | IS | 24 | BASIC EARNINGS PER AVERAGE COMMON SHARE | us-gaap:EarningsPerShareBasic |  | 2.33 | 2.33 | Y | Y |
| R2.htm | IS | 25 | DILUTED EARNINGS PER AVERAGE COMMON SHARE | us-gaap:EarningsPerShareDiluted |  | 2.32 | 2.32 | Y | Y |
| R2.htm | IS | 26 | Other comprehensive income, net of tax | us-gaap:OtherComprehensiveIncomeLossNetOfTax |  | 100000 | 100000 | Y | Y |
| R2.htm | IS | 27 | Comprehensive income | us-gaap:ComprehensiveIncomeNetOfTax |  | 470800000 | 470800000 | Y | Y |
| R2.htm | IS | 28 | Revenues from contracts with customers | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | oge_OgAndEMember | 3190900000 |  | dimensional | Y |
| R2.htm | IS | 29 | Other revenues | oge:RevenuesfromAlternativeRevenuePrograms | oge_OgAndEMember | 69200000 |  | custom | Y |
| R2.htm | IS | 30 | Operating revenues | us-gaap:Revenues | oge_OgAndEMember | 3260100000 |  | dimensional | Y |
| R2.htm | IS | 31 | FUEL, PURCHASED POWER AND DIRECT TRANSMISSION EXPENSE | us-gaap:CostOfGoodsAndServicesSold | oge_OgAndEMember | 1259900000 |  | dimensional | Y |
| R2.htm | IS | 32 | Other operation and maintenance | us-gaap:OtherCostAndExpenseOperating | oge_OgAndEMember | 531000000 |  | dimensional | Y |
| R2.htm | IS | 33 | Depreciation and amortization | us-gaap:DepreciationAndAmortization | oge_OgAndEMember | 559800000 |  | dimensional | Y |
| R2.htm | IS | 34 | Taxes other than income | us-gaap:TaxesExcludingIncomeAndExciseTaxes | oge_OgAndEMember | 109400000 |  | dimensional | Y |
| R2.htm | IS | 35 | Operating expenses | us-gaap:OperatingExpenses | oge_OgAndEMember | 1200200000 |  | dimensional | Y |
| R2.htm | IS | 36 | OPERATING INCOME | us-gaap:OperatingIncomeLoss | oge_OgAndEMember | 800000000 |  | dimensional | Y |
| R2.htm | IS | 37 | Allowance for equity funds used during construction | us-gaap:PublicUtilitiesAllowanceForFundsUsedDuringConstructionCapitalizedCostOfEquity | oge_OgAndEMember | 26000000 |  | dimensional | Y |
| R2.htm | IS | 38 | Other net periodic benefit (expense) income | us-gaap:PensionAndOtherPostretirementBenefitExpense | oge_OgAndEMember | -10300000 |  | dimensional | Y |
| R2.htm | IS | 39 | Other income | us-gaap:OtherNonoperatingIncome | oge_OgAndEMember | 17300000 |  | dimensional | Y |
| R2.htm | IS | 40 | Other expense | us-gaap:OtherNonoperatingExpense | oge_OgAndEMember | -2600000 |  | dimensional | Y |
| R2.htm | IS | 41 | Net other income | us-gaap:NonoperatingIncomeExpense | oge_OgAndEMember | 30400000 |  | dimensional | Y |
| R2.htm | IS | 42 | Interest on long-term debt | us-gaap:InterestExpenseLongTermDebt | oge_OgAndEMember | 237800000 |  | dimensional | Y |
| R2.htm | IS | 43 | Allowance for borrowed funds used during construction | us-gaap:PublicUtilitiesAllowanceForFundsUsedDuringConstructionAdditions | oge_OgAndEMember | -15800000 |  | dimensional | Y |
| R2.htm | IS | 44 | Interest on short-term debt and other interest charges | us-gaap:InterestExpenseShortTermBorrowings | oge_OgAndEMember | 3500000 |  | dimensional | Y |
| R2.htm | IS | 45 | Interest expense | us-gaap:InterestExpense | oge_OgAndEMember | 225500000 |  | dimensional | Y |
| R2.htm | IS | 46 | INCOME BEFORE TAXES | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | oge_OgAndEMember | 604900000 |  | dimensional | Y |
| R2.htm | IS | 47 | INCOME TAX EXPENSE | us-gaap:IncomeTaxExpenseBenefit | oge_OgAndEMember | 105100000 |  | dimensional | Y |
| R2.htm | IS | 48 | NET INCOME | us-gaap:NetIncomeLoss | oge_OgAndEMember | 499800000 |  | dimensional | Y |
| R2.htm | IS | 49 | Other comprehensive income, net of tax | us-gaap:OtherComprehensiveIncomeLossNetOfTax | oge_OgAndEMember | 0 |  | dimensional | Y |
| R2.htm | IS | 50 | Comprehensive income | us-gaap:ComprehensiveIncomeNetOfTax | oge_OgAndEMember | 499800000 |  | dimensional | Y |
| R3.htm | CI | 1 | Net income | us-gaap:ProfitLoss |  | 470700000 | 470700000 | Y | Y |
| R3.htm | CI | 2 | Amortization of prior service cost, net of tax of $0.1, $0.1 | us-gaap:OtherComprehensiveIncomeLossAmortizationAdjustmentFromAOCIPensionAndOtherPostretirementBenefitPlansForNetPriorServiceCostCreditNetOfTax |  | 200000 | -200000 | Y | Y |
| R3.htm | CI | 3 | Amortization of deferred net loss, net of tax of $0.1, $0.1  | us-gaap:OtherComprehensiveIncomeLossReclassificationAdjustmentFromAOCIPensionAndOtherPostretirementBenefitPlansForNetGainLossNetOfTax |  | 300000 | -300000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R3.htm | CI | 4 | Net (loss) gain arising during the period, net of tax of $(0 | us-gaap:OtherComprehensiveIncomeDefinedBenefitPlansNetUnamortizedGainLossArisingDuringPeriodNetOfTax |  | -1700000 | -1700000 | Y | Y |
| R3.htm | CI | 5 | Regulatory classification of certain pension costs, net of t | oge:OtherComprehensiveIncomeRegulatoryClassificationOfCertainPensionCostNetOfTax |  | 0 |  | custom | Y |
| R3.htm | CI | 6 | Settlement cost, net of tax of $0.0, $0.0 and $0.4, respecti | us-gaap:OtherComprehensiveIncomeLossFinalizationOfPensionAndNonPensionPostretirementPlanValuationNetOfTax |  | 0 | 0 | Y | Y |
| R3.htm | CI | 7 | Amortization of deferred net gain, net of tax of $(0.1), $(0 | oge:OtherComprehensiveIncomeReclassificationOfDefinedBenefitPostretirementPlansNetGainLossRecognizedInNetPeriodicBenefitCostNetOfTax |  | -100000 |  | custom | Y |
| R3.htm | CI | 8 | Net gain (loss) arising during the period, net of tax of $0. | oge:OtherComprehensiveIncomePostretirementPlansNetUnamortizedGainLossArisingDuringPeriodNetOfTax |  | 1400000 |  | custom | Y |
| R3.htm | CI | 9 | Other comprehensive income, net of tax | us-gaap:OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent |  | 100000 | 100000 | Y | Y |
| R3.htm | CI | 10 | Comprehensive income | us-gaap:ComprehensiveIncomeNetOfTax |  | 470800000 | 470800000 | Y | Y |
| R4.htm | CI | 1 | Amortization of prior service cost, net of tax of $0.1, $0.1 | oge:OtherComprehensiveIncomeAmortizationOfDefinedBenefitPensionPlansNetPriorServiceCostRecognizedinNetPeriodicPensionCostTax | oge_PensionPlansMember | 100000 |  | custom | N |
| R4.htm | CI | 2 | Amortization of deferred net loss, net of tax of $0.1, $0.1  | us-gaap:OtherComprehensiveIncomeLossReclassificationAdjustmentFromAOCIPensionAndOtherPostretirementBenefitPlansForNetGainLossTax | oge_PensionPlansMember | 100000 |  | dimensional | N |
| R4.htm | CI | 3 | Net (loss) gain arising during the period, net of tax of $(0 | us-gaap:OtherComprehensiveIncomeDefinedBenefitPlansNetUnamortizedGainLossArisingDuringPeriodTax | oge_PensionPlansMember | -500000 |  | dimensional | N |
| R4.htm | CI | 4 | Regulatory classification of certain pension costs, net of t | oge:OtherComprehensiveIncomeRegulatoryClassificationOfCertainPensionCostsTax | oge_PensionPlansMember | 0 |  | custom | N |
| R4.htm | CI | 5 | Settlement cost, net of tax of $0.0, $0.0 and $0.4, respecti | us-gaap:OtherComprehensiveIncomeFinalizationOfPensionAndNonPensionPostretirementPlanValuationTax | oge_PensionPlansMember | 0 |  | dimensional | N |
| R4.htm | CI | 6 | Amortization of deferred net gain, net of tax of $(0.1), ($0 | oge:OtherComprehensiveIncomeReclassificationOfDefinedBenefitPostretirementPlansNetGainLossRecognizedInNetPeriodicBenefitCostTax | us-gaap_OtherPostretirementBenefitPlansDefinedBenefitMember | -100000 |  | custom | N |
| R4.htm | CI | 7 | Net gain (loss) arising during the period, net of tax of $0. | oge:OtherComprehensiveIncomePostretirementPlansNetUnamortizedGainLossArisingDuringPeriodTax | us-gaap_OtherPostretirementBenefitPlansDefinedBenefitMember | 400000 |  | custom | N |
| R5.htm | CF | 1 | Net income | us-gaap:ProfitLoss |  | 470700000 | 470700000 | Y | Y |
| R5.htm | CF | 2 | Depreciation and amortization | us-gaap:DepreciationAmortizationAndAccretionNet |  | 559800000 | 559800000 | Y | Y |
| R5.htm | CF | 3 | Deferred income taxes and other tax credits, net | us-gaap:DeferredIncomeTaxesAndTaxCredits |  | 59500000 | 59500000 | Y | Y |
| R5.htm | CF | 4 | Allowance for equity funds used during construction | us-gaap:PublicUtilitiesAllowanceForFundsUsedDuringConstructionCapitalizedCostOfEquity |  | -26000000 | 26000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 5 | Stock-based compensation expense | us-gaap:ShareBasedCompensation |  | 14000000 | 14000000 | Y | Y |
| R5.htm | CF | 6 | Regulatory assets | us-gaap:IncreaseDecreaseInOtherRegulatoryAssets |  | -66900000 | 66900000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 7 | Regulatory liabilities | us-gaap:IncreaseDecreaseInRegulatoryLiabilities |  | 500000 | 500000 | Y | Y |
| R5.htm | CF | 8 | Other assets | us-gaap:IncreaseDecreaseInOtherNoncurrentAssets |  | -32500000 | 32500000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 9 | Other liabilities | us-gaap:IncreaseDecreaseInOtherNoncurrentLiabilities |  | 39400000 | 39400000 | Y | Y |
| R5.htm | CF | 10 | Other | us-gaap:OtherOperatingActivitiesCashFlowStatement |  | -8700000 | -8700000 | Y | Y |
| R5.htm | CF | 11 | Accounts receivable and accrued unbilled revenues, net | us-gaap:IncreaseDecreaseInAccountsReceivable |  | -108800000 | 108800000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 12 | Income taxes receivable | us-gaap:IncreaseDecreaseInIncomeTaxesReceivable |  | -37300000 | 37300000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 13 | Fuel, materials and supplies inventories | us-gaap:IncreaseDecreaseInInventories |  | 81900000 | -81900000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 14 | Fuel recoveries | us-gaap:IncreaseDecreaseInDeferredFuelCosts |  | 130500000 | -130500000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 15 | Other current assets | us-gaap:IncreaseDecreaseInOtherCurrentAssets |  | 17100000 | -17100000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 16 | Accounts payable | us-gaap:IncreaseDecreaseInAccountsPayable |  | 34900000 | 34900000 | Y | Y |
| R5.htm | CF | 17 | Other current liabilities | us-gaap:IncreaseDecreaseInOtherCurrentLiabilities |  | 9000000 | 9000000 | Y | Y |
| R5.htm | CF | 18 | Net cash provided from operating activities | us-gaap:NetCashProvidedByUsedInOperatingActivities |  | 1137100000 | 1137100000 | Y | Y |
| R5.htm | CF | 19 | Capital expenditures (less allowance for equity funds used d | us-gaap:PaymentsToAcquireProductiveAssets |  | -1054400000 | 1054400000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 20 | Cost of removal and other | oge:CostOfRemovalAndOther |  | -72200000 |  | custom | Y |
| R5.htm | CF | 21 | Net cash used in investing activities | us-gaap:NetCashProvidedByUsedInInvestingActivities |  | -1126600000 | -1126600000 | Y | Y |
| R5.htm | CF | 22 | Proceeds from long-term debt | us-gaap:ProceedsFromIssuanceOfLongTermDebt |  | 344400000 | 344400000 | Y | Y |
| R5.htm | CF | 23 | Payment of long-term debt | us-gaap:RepaymentsOfLongTermDebt |  | -32600000 | 32600000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 24 | (Decrease) increase in short-term debt | us-gaap:ProceedsFromRepaymentsOfShortTermDebt |  | -177300000 | -177300000 | Y | Y |
| R5.htm | CF | 25 | Dividends paid on common stock | us-gaap:PaymentsOfDividendsCommonStock |  | -341900000 | 341900000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 26 | Proceeds (costs) from issuance of common stock | us-gaap:ProceedsFromIssuanceOfCommonStock |  | 203800000 | 203800000 | Y | Y |
| R5.htm | CF | 27 | Cash paid for employee equity-based compensation | us-gaap:ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions |  | -7300000 | 7300000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | CF | 28 | Net cash (used in) provided from financing activities | us-gaap:NetCashProvidedByUsedInFinancingActivities |  | -10900000 | -10900000 | Y | Y |
| R5.htm | CF | 29 | NET CHANGE IN CASH AND CASH EQUIVALENTS | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect |  | -400000 | -400000 | Y | Y |
| R5.htm | CF | 30 | CASH AND CASH EQUIVALENTS AT BEGINNING OF YEAR | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations |  | 600000 |  |  | Y |
| R5.htm | CF | 31 | CASH AND CASH EQUIVALENTS AT END OF YEAR | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations |  | 200000 |  |  | Y |
| R5.htm | CF | 32 | Interest (net of interest capitalized) | us-gaap:InterestPaidNet |  | 268700000 | 268700000 | Y | Y |
| R5.htm | CF | 33 | Federal income taxes (net of income tax refunds) | us-gaap:IncomeTaxPaidFederalAfterRefundReceived |  | 73900000 | 73900000 | Y | Y |
| R5.htm | CF | 34 | State income taxes (net of income tax refunds) | us-gaap:IncomeTaxPaidStateAndLocalAfterRefundReceived |  | 1200000 | 1200000 | Y | Y |
| R5.htm | CF | 35 | Power plant long-term service agreement | oge:PowerPlantLongTermServiceAgreement |  | 3400000 |  | custom | Y |
| R5.htm | CF | 36 | Tinker Air Force Base distribution assets purchase | us-gaap:FairValueOfAssetsAcquired |  | 0 | 0 | Y | Y |
| R5.htm | CF | 37 | Net income | us-gaap:ProfitLoss | oge_OgAndEMember | 499800000 |  | dimensional | Y |
| R5.htm | CF | 38 | Depreciation and amortization | us-gaap:DepreciationAmortizationAndAccretionNet | oge_OgAndEMember | 559800000 |  | dimensional | Y |
| R5.htm | CF | 39 | Deferred income taxes and other tax credits, net | us-gaap:DeferredIncomeTaxesAndTaxCredits | oge_OgAndEMember | 61700000 |  | dimensional | Y |
| R5.htm | CF | 40 | Allowance for equity funds used during construction | us-gaap:PublicUtilitiesAllowanceForFundsUsedDuringConstructionCapitalizedCostOfEquity | oge_OgAndEMember | -26000000 |  | dimensional | Y |
| R5.htm | CF | 41 | Stock-based compensation expense | us-gaap:ShareBasedCompensation | oge_OgAndEMember | 14000000 |  | dimensional | Y |
| R5.htm | CF | 42 | Regulatory assets | us-gaap:IncreaseDecreaseInOtherRegulatoryAssets | oge_OgAndEMember | -66900000 |  | dimensional | Y |
| R5.htm | CF | 43 | Regulatory liabilities | us-gaap:IncreaseDecreaseInRegulatoryLiabilities | oge_OgAndEMember | 500000 |  | dimensional | Y |
| R5.htm | CF | 44 | Other assets | us-gaap:IncreaseDecreaseInOtherNoncurrentAssets | oge_OgAndEMember | -37900000 |  | dimensional | Y |
| R5.htm | CF | 45 | Other liabilities | us-gaap:IncreaseDecreaseInOtherNoncurrentLiabilities | oge_OgAndEMember | 36800000 |  | dimensional | Y |
| R5.htm | CF | 46 | Accounts receivable and accrued unbilled revenues, net | us-gaap:IncreaseDecreaseInAccountsReceivable | oge_OgAndEMember | -108700000 |  | dimensional | Y |
| R5.htm | CF | 47 | Fuel, materials and supplies inventories | us-gaap:IncreaseDecreaseInInventories | oge_OgAndEMember | 81900000 |  | dimensional | Y |
| R5.htm | CF | 48 | Fuel recoveries | us-gaap:IncreaseDecreaseInDeferredFuelCosts | oge_OgAndEMember | 130500000 |  | dimensional | Y |
| R5.htm | CF | 49 | Other current assets | us-gaap:IncreaseDecreaseInOtherCurrentAssets | oge_OgAndEMember | 11700000 |  | dimensional | Y |
| R5.htm | CF | 50 | Accounts payable | us-gaap:IncreaseDecreaseInAccountsPayable | oge_OgAndEMember | 66400000 |  | dimensional | Y |
| R5.htm | CF | 51 | Income taxes payable - parent | us-gaap:IncreaseDecreaseInAccruedIncomeTaxesPayable | oge_OgAndEMember | -47600000 |  | dimensional | Y |
| R5.htm | CF | 52 | Other current liabilities | us-gaap:IncreaseDecreaseInOtherCurrentLiabilities | oge_OgAndEMember | 15200000 |  | dimensional | Y |
| R5.htm | CF | 53 | Net cash provided from operating activities | us-gaap:NetCashProvidedByUsedInOperatingActivities | oge_OgAndEMember | 1191200000 |  | dimensional | Y |
| R5.htm | CF | 54 | Capital expenditures (less allowance for equity funds used d | us-gaap:PaymentsToAcquireProductiveAssets | oge_OgAndEMember | -1054400000 |  | dimensional | Y |
| R5.htm | CF | 55 | Cost of removal | us-gaap:PaymentsForRemovalCosts | oge_OgAndEMember | -70300000 |  | dimensional | Y |
| R5.htm | CF | 56 | Net cash used in investing activities | us-gaap:NetCashProvidedByUsedInInvestingActivities | oge_OgAndEMember | -1124700000 |  | dimensional | Y |
| R5.htm | CF | 57 | Proceeds from long-term debt | us-gaap:ProceedsFromIssuanceOfLongTermDebt | oge_OgAndEMember | 344400000 |  | dimensional | Y |
| R5.htm | CF | 58 | Payment of long-term debt | us-gaap:RepaymentsOfLongTermDebt | oge_OgAndEMember | -32600000 |  | dimensional | Y |
| R5.htm | CF | 59 | Changes In advances with parent | oge:ChangesInAdvancesWithParent | oge_OgAndEMember | -148300000 |  | custom | Y |
| R5.htm | CF | 60 | Capital contribution from OGE Energy | us-gaap:ProceedsFromContributionsFromParent | oge_OgAndEMember | 150000000 |  | dimensional | Y |
| R5.htm | CF | 61 | Dividends paid on common stock | us-gaap:PaymentsOfDividendsCommonStock | oge_OgAndEMember | -380000000 |  | dimensional | Y |
| R5.htm | CF | 62 | Net cash (used in) provided from financing activities | us-gaap:NetCashProvidedByUsedInFinancingActivities | oge_OgAndEMember | -66500000 |  | dimensional | Y |
| R5.htm | CF | 63 | NET CHANGE IN CASH AND CASH EQUIVALENTS | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect | oge_OgAndEMember | 0 |  | dimensional | Y |
| R5.htm | CF | 64 | CASH AND CASH EQUIVALENTS AT BEGINNING OF YEAR | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | oge_OgAndEMember | 200000 |  | dimensional | Y |
| R5.htm | CF | 65 | CASH AND CASH EQUIVALENTS AT END OF YEAR | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | oge_OgAndEMember | 200000 |  | dimensional | Y |
| R5.htm | CF | 66 | Interest (net of interest capitalized) | us-gaap:InterestPaidNet | oge_OgAndEMember | 216900000 |  | dimensional | Y |
| R5.htm | CF | 67 | Federal income taxes (net of income tax refunds) | us-gaap:IncomeTaxPaidFederalAfterRefundReceived | oge_OgAndEMember | 90700000 |  | dimensional | Y |
| R5.htm | CF | 68 | State income taxes (net of income tax refunds) | us-gaap:IncomeTaxPaidStateAndLocalAfterRefundReceived | oge_OgAndEMember | 1200000 |  | dimensional | Y |
| R5.htm | CF | 69 | Power plant long-term service agreement | oge:PowerPlantLongTermServiceAgreement | oge_OgAndEMember | 3400000 |  | custom | Y |
| R5.htm | CF | 70 | Tinker Air Force Base distribution assets purchase | us-gaap:FairValueOfAssetsAcquired | oge_OgAndEMember | 0 |  | dimensional | Y |
| R7.htm | BS | 1 | Cash and cash equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue |  | 200000 | 200000 | Y | Y |
| R7.htm | BS | 2 | Accounts receivable | us-gaap:AccountsReceivableNetCurrent |  | 347800000 | 347800000 | Y | Y |
| R7.htm | BS | 3 | Accrued unbilled revenues | us-gaap:UnbilledReceivablesCurrent |  | 76200000 | 76200000 | Y | Y |
| R7.htm | BS | 4 | Income taxes receivable | us-gaap:IncomeTaxesReceivable |  | 37300000 | 37300000 | Y | Y |
| R7.htm | BS | 5 | Fuel inventories | us-gaap:InventoryNet |  | 112000000 | 112000000 | Y | Y |
| R7.htm | BS | 6 | Materials and supplies, at average cost | us-gaap:OtherInventorySupplies |  | 212700000 | 212700000 | Y | Y |
| R7.htm | BS | 7 | Fuel clause under recoveries | us-gaap:DeferredFuelCost |  | 0 | 0 | Y | Y |
| R7.htm | BS | 8 | Other | us-gaap:OtherAssetsCurrent |  | 71700000 | 71700000 | Y | Y |
| R7.htm | BS | 9 | Total current assets | us-gaap:AssetsCurrent |  | 857900000 | 857900000 | Y | Y |
| R7.htm | BS | 10 | Other | us-gaap:OtherLongTermInvestments |  | 129400000 | 129400000 | Y | Y |
| R7.htm | BS | 11 | Total other property and investments | us-gaap:OtherInvestments |  | 129400000 | 129400000 | Y | Y |
| R7.htm | BS | 12 | In service | us-gaap:PublicUtilitiesPropertyPlantAndEquipmentPlantInService |  | 17203000000 | 17203000000 | Y | Y |
| R7.htm | BS | 13 | Construction work in progress | us-gaap:ConstructionInProgressGross |  | 744900000 | 744900000 | Y | Y |
| R7.htm | BS | 14 | Total property, plant and equipment | us-gaap:PropertyPlantAndEquipmentGross |  | 17947900000 | 17947900000 | Y | Y |
| R7.htm | BS | 15 | Less: accumulated depreciation | us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment |  | 5217500000 | 5217500000 | Y | Y |
| R7.htm | BS | 16 | Net property, plant and equipment | us-gaap:PropertyPlantAndEquipmentNet |  | 12730400000 | 12730400000 | Y | Y |
| R7.htm | BS | 17 | Regulatory assets | us-gaap:RegulatoryAssetsNoncurrent |  | 557200000 | 557200000 | Y | Y |
| R7.htm | BS | 18 | Other | us-gaap:OtherAssetsMiscellaneousNoncurrent |  | 95600000 | 95600000 | Y | Y |
| R7.htm | BS | 19 | Total deferred charges and other assets | us-gaap:OtherAssetsNoncurrent |  | 652800000 | 652800000 | Y | Y |
| R7.htm | BS | 20 | TOTAL ASSETS | us-gaap:Assets |  | 14370500000 | 14370500000 | Y | Y |
| R7.htm | BS | 21 | Short-term debt | us-gaap:ShortTermBorrowings |  | 292000000 | 292000000 | Y | Y |
| R7.htm | BS | 22 | Accounts payable | us-gaap:AccountsPayableCurrent |  | 350600000 | 350600000 | Y | Y |
| R7.htm | BS | 23 | Dividends payable | us-gaap:DividendsPayableCurrent |  | 87600000 | 87600000 | Y | Y |
| R7.htm | BS | 24 | Customer deposits | us-gaap:ContractWithCustomerLiabilityCurrent |  | 127200000 | 127200000 | Y | Y |
| R7.htm | BS | 25 | Accrued taxes | us-gaap:TaxesPayableCurrent |  | 53000000 | 53000000 | Y | Y |
| R7.htm | BS | 26 | Accrued interest | us-gaap:InterestPayableCurrent |  | 68800000 | 68800000 | Y | Y |
| R7.htm | BS | 27 | Accrued compensation | us-gaap:EmployeeRelatedLiabilitiesCurrent |  | 54300000 | 54300000 | Y | Y |
| R7.htm | BS | 28 | Long-term debt due within one year | us-gaap:LongTermDebtCurrent |  | 0 | 0 | Y | Y |
| R7.htm | BS | 29 | Fuel clause over recoveries | us-gaap:CustomerRefundLiabilityCurrent |  | 27100000 | 27100000 | Y | Y |
| R7.htm | BS | 30 | Other | us-gaap:OtherLiabilitiesCurrent |  | 33500000 | 33500000 | Y | Y |
| R7.htm | BS | 31 | Total current liabilities | us-gaap:LiabilitiesCurrent |  | 1094100000 | 1094100000 | Y | Y |
| R7.htm | BS | 32 | LONG-TERM DEBT | us-gaap:LongTermDebtNoncurrent |  | 5369200000 | 5369200000 | Y | Y |
| R7.htm | BS | 33 | Accrued benefit obligations | us-gaap:PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent |  | 164400000 | 164400000 | Y | Y |
| R7.htm | BS | 34 | Deferred income taxes | us-gaap:DeferredIncomeTaxLiabilitiesNet |  | 1489300000 | 1489300000 | Y | Y |
| R7.htm | BS | 35 | Deferred investment tax credits | us-gaap:AccumulatedDeferredInvestmentTaxCredit |  | 9800000 | 9800000 | Y | Y |
| R7.htm | BS | 36 | Regulatory liabilities | us-gaap:RegulatoryLiabilityNoncurrent |  | 957100000 | 957100000 | Y | Y |
| R7.htm | BS | 37 | Other | us-gaap:OtherLiabilitiesNoncurrent |  | 309300000 | 309300000 | Y | Y |
| R7.htm | BS | 38 | Total deferred credits and other liabilities | us-gaap:LiabilitiesOtherThanLongtermDebtNoncurrent |  | 2929900000 | 2929900000 | Y | Y |
| R7.htm | BS | 39 | Total liabilities | us-gaap:Liabilities |  | 9393200000 | 9393200000 | Y | Y |
| R7.htm | BS | 40 | COMMITMENTS AND CONTINGENCIES (NOTE 13) | us-gaap:CommitmentsAndContingencies |  |  |  |  | Y |
| R7.htm | BS | 41 | Common stockholder's equity | us-gaap:CommonStocksIncludingAdditionalPaidInCapital |  | 1378400000 | 1378400000 | Y | Y |
| R7.htm | BS | 42 | Retained earnings | us-gaap:RetainedEarningsAccumulatedDeficit |  | 3601500000 | 3601500000 | Y | Y |
| R7.htm | BS | 43 | Accumulated other comprehensive loss, net of tax | us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax |  | -2600000 | -2600000 | Y | Y |
| R7.htm | BS | 44 | Total stockholder's equity | us-gaap:StockholdersEquity |  | 4977300000 | 4977300000 | Y | Y |
| R7.htm | BS | 45 | TOTAL LIABILITIES AND STOCKHOLDER'S EQUITY | us-gaap:LiabilitiesAndStockholdersEquity |  | 14370500000 | 14370500000 | Y | Y |
| R7.htm | BS | 46 | Cash and cash equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue | oge_OgAndEMember | 200000 |  | dimensional | Y |
| R7.htm | BS | 47 | Accounts receivable | us-gaap:AccountsReceivableNetCurrent | oge_OgAndEMember | 347200000 |  | dimensional | Y |
| R7.htm | BS | 48 | Accrued unbilled revenues | us-gaap:UnbilledReceivablesCurrent | oge_OgAndEMember | 76200000 |  | dimensional | Y |
| R7.htm | BS | 49 | Advances to parent | oge:AdvancesToParent | oge_OgAndEMember | 78300000 |  | custom | Y |
| R7.htm | BS | 50 | Fuel inventories | us-gaap:InventoryNet | oge_OgAndEMember | 112000000 |  | dimensional | Y |
| R7.htm | BS | 51 | Materials and supplies, at average cost | us-gaap:OtherInventorySupplies | oge_OgAndEMember | 212700000 |  | dimensional | Y |
| R7.htm | BS | 52 | Fuel clause under recoveries | us-gaap:DeferredFuelCost | oge_OgAndEMember | 0 |  | dimensional | Y |
| R7.htm | BS | 53 | Other | us-gaap:OtherAssetsCurrent | oge_OgAndEMember | 71500000 |  | dimensional | Y |
| R7.htm | BS | 54 | Total current assets | us-gaap:AssetsCurrent | oge_OgAndEMember | 898100000 |  | dimensional | Y |
| R7.htm | BS | 55 | Total other property and investments | us-gaap:OtherInvestments | oge_OgAndEMember | 4100000 |  | dimensional | Y |
| R7.htm | BS | 56 | In service | us-gaap:PublicUtilitiesPropertyPlantAndEquipmentPlantInService | oge_OgAndEMember | 17196900000 |  | dimensional | Y |
| R7.htm | BS | 57 | Construction work in progress | us-gaap:ConstructionInProgressGross | oge_OgAndEMember | 744900000 |  | dimensional | Y |
| R7.htm | BS | 58 | Total property, plant and equipment | us-gaap:PropertyPlantAndEquipmentGross | oge_OgAndEMember | 17941800000 |  | dimensional | Y |
| R7.htm | BS | 59 | Less: accumulated depreciation | us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment | oge_OgAndEMember | 5217500000 |  | dimensional | Y |
| R7.htm | BS | 60 | Net property, plant and equipment | us-gaap:PropertyPlantAndEquipmentNet | oge_OgAndEMember | 12724300000 |  | dimensional | Y |
| R7.htm | BS | 61 | Regulatory assets | us-gaap:RegulatoryAssetsNoncurrent | oge_OgAndEMember | 557200000 |  | dimensional | Y |
| R7.htm | BS | 62 | Other | us-gaap:OtherAssetsMiscellaneousNoncurrent | oge_OgAndEMember | 93800000 |  | dimensional | Y |
| R7.htm | BS | 63 | Total deferred charges and other assets | us-gaap:OtherAssetsNoncurrent | oge_OgAndEMember | 651000000 |  | dimensional | Y |
| R7.htm | BS | 64 | TOTAL ASSETS | us-gaap:Assets | oge_OgAndEMember | 14277500000 |  | dimensional | Y |
| R7.htm | BS | 65 | Accounts payable | us-gaap:AccountsPayableCurrent | oge_OgAndEMember | 348700000 |  | dimensional | Y |
| R7.htm | BS | 66 | Advances from parent | oge:AdvancesFromParent | oge_OgAndEMember | 0 |  | custom | Y |
| R7.htm | BS | 67 | Customer deposits | us-gaap:ContractWithCustomerLiabilityCurrent | oge_OgAndEMember | 127200000 |  | dimensional | Y |
| R7.htm | BS | 68 | Accrued taxes | us-gaap:TaxesPayableCurrent | oge_OgAndEMember | 52300000 |  | dimensional | Y |
| R7.htm | BS | 69 | Accrued interest | us-gaap:InterestPayableCurrent | oge_OgAndEMember | 66400000 |  | dimensional | Y |
| R7.htm | BS | 70 | Accrued compensation | us-gaap:EmployeeRelatedLiabilitiesCurrent | oge_OgAndEMember | 54300000 |  | dimensional | Y |
| R7.htm | BS | 71 | Long-term debt due within one year | us-gaap:LongTermDebtCurrent | oge_OgAndEMember | 0 |  | dimensional | Y |
| R7.htm | BS | 72 | Fuel clause over recoveries | us-gaap:CustomerRefundLiabilityCurrent | oge_OgAndEMember | 27100000 |  | dimensional | Y |
| R7.htm | BS | 73 | Other | us-gaap:OtherLiabilitiesCurrent | oge_OgAndEMember | 33500000 |  | dimensional | Y |
| R7.htm | BS | 74 | Total current liabilities | us-gaap:LiabilitiesCurrent | oge_OgAndEMember | 709500000 |  | dimensional | Y |
| R7.htm | BS | 75 | LONG-TERM DEBT | us-gaap:LongTermDebtNoncurrent | oge_OgAndEMember | 4961700000 |  | dimensional | Y |
| R7.htm | BS | 76 | Accrued benefit obligations | us-gaap:PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent | oge_OgAndEMember | 93200000 |  | dimensional | Y |
| R7.htm | BS | 77 | Deferred income taxes | us-gaap:DeferredIncomeTaxLiabilitiesNet | oge_OgAndEMember | 1531300000 |  | dimensional | Y |
| R7.htm | BS | 78 | Deferred investment tax credits | us-gaap:AccumulatedDeferredInvestmentTaxCredit | oge_OgAndEMember | 9800000 |  | dimensional | Y |
| R7.htm | BS | 79 | Regulatory liabilities | us-gaap:RegulatoryLiabilityNoncurrent | oge_OgAndEMember | 957100000 |  | dimensional | Y |
| R7.htm | BS | 80 | Other | us-gaap:OtherLiabilitiesNoncurrent | oge_OgAndEMember | 274700000 |  | dimensional | Y |
| R7.htm | BS | 81 | Total deferred credits and other liabilities | us-gaap:LiabilitiesOtherThanLongtermDebtNoncurrent | oge_OgAndEMember | 2866100000 |  | dimensional | Y |
| R7.htm | BS | 82 | Total liabilities | us-gaap:Liabilities | oge_OgAndEMember | 8537300000 |  | dimensional | Y |
| R7.htm | BS | 83 | COMMITMENTS AND CONTINGENCIES (NOTE 13) | us-gaap:CommitmentsAndContingencies | oge_OgAndEMember |  |  | dimensional | Y |
| R7.htm | BS | 84 | Common stockholder's equity | us-gaap:CommonStocksIncludingAdditionalPaidInCapital | oge_OgAndEMember | 1753500000 |  | dimensional | Y |
| R7.htm | BS | 85 | Retained earnings | us-gaap:RetainedEarningsAccumulatedDeficit | oge_OgAndEMember | 3986700000 |  | dimensional | Y |
| R7.htm | BS | 86 | Total stockholder's equity | us-gaap:StockholdersEquity | oge_OgAndEMember | 5740200000 |  | dimensional | Y |
| R7.htm | BS | 87 | TOTAL LIABILITIES AND STOCKHOLDER'S EQUITY | us-gaap:LiabilitiesAndStockholdersEquity | oge_OgAndEMember | 14277500000 |  | dimensional | Y |
| R8.htm | BSP | 1 | Accounts Receivable, Allowance for Credit Loss | us-gaap:AllowanceForDoubtfulAccountsReceivable |  | 4100000 | 4100000 | Y | N |
| R8.htm | BSP | 2 | Accounts Receivable, Allowance for Credit Loss | us-gaap:AllowanceForDoubtfulAccountsReceivable | oge_OgAndEMember | 4100000 |  | dimensional | N |
| R10.htm | EQP | 1 | Common Stock, Par or Stated Value Per Share | us-gaap:CommonStockParOrStatedValuePerShare |  | 0.01 |  |  | N |
| R10.htm | EQP | 2 | Common Stock, Shares Authorized | us-gaap:CommonStockSharesAuthorized |  | 450 |  |  | N |
| R10.htm | EQP | 3 | Common Stock, Shares, Outstanding | us-gaap:CommonStockSharesOutstanding |  | 206100000 |  |  | N |
| R10.htm | EQP | 4 | Common Stock, Shares, Issued | us-gaap:CommonStockSharesIssued |  | 206100000 |  |  | N |
| R10.htm | EQP | 5 | Common Stock, Par or Stated Value Per Share | us-gaap:CommonStockParOrStatedValuePerShare | oge_OgAndEMember | 2.5 |  | dimensional | N |
| R10.htm | EQP | 6 | Common Stock, Shares Authorized | us-gaap:CommonStockSharesAuthorized | oge_OgAndEMember | 100 |  | dimensional | N |
| R10.htm | EQP | 7 | Common Stock, Shares, Outstanding | us-gaap:CommonStockSharesOutstanding | oge_OgAndEMember | 40400000 |  | dimensional | N |
| R10.htm | EQP | 8 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_MuskogeeIndustrialAuthorityBondDue2025Member |  |  | dimensional | N |
| R10.htm | EQP | 9 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_MuskogeeIndustrialAuthorityBondDue2025Member |  |  | dimensional | N |
| R10.htm | EQP | 10 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_MuskogeeIndustrialAuthorityBondDue2025Member |  |  | dimensional | N |
| R10.htm | EQP | 11 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_MuskogeeIndustrialAuthorityBondDue2027Member |  |  | dimensional | N |
| R10.htm | EQP | 12 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_MuskogeeIndustrialAuthorityBondDue2027Member |  |  | dimensional | N |
| R10.htm | EQP | 13 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_GarfieldIndustrialAuthorityBondMember |  |  | dimensional | N |
| R10.htm | EQP | 14 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_GarfieldIndustrialAuthorityBondMember |  |  | dimensional | N |
| R10.htm | EQP | 15 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 16 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 17 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 18 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 19 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 20 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 21 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 22 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 23 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 24 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 25 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 26 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 27 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 28 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 29 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 30 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 31 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 32 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 33 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 34 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 35 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 36 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 37 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 38 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 39 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 40 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 41 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 42 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 43 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 44 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 45 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 46 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 47 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 48 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 49 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 50 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_SeniorNotesMember |  |  | dimensional | N |
| R10.htm | EQP | 51 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | oge_TermLoanMember |  |  | dimensional | N |
| R10.htm | EQP | 52 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | oge_TermLoanMember |  |  | dimensional | N |
| R10.htm | EQP | 53 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | oge_TermLoanMember |  |  | dimensional | N |
| R10.htm | EQP | 54 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_LongTermDebtMember |  |  | dimensional | N |
| R10.htm | EQP | 55 | Debt Instrument, Maturity Date | us-gaap:DebtInstrumentMaturityDate | us-gaap_LongTermDebtMember |  |  | dimensional | N |
| R10.htm | EQP | 56 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 57 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 58 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 59 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 60 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 61 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 62 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |
| R10.htm | EQP | 63 | Debt Instrument, Interest Rate, Stated Percentage | us-gaap:DebtInstrumentInterestRateStatedPercentage | us-gaap_DebenturesSubjectToMandatoryRedemptionMember |  |  | dimensional | N |

Totals: 222 IS/BS/CF/CI face lines with an FY0 value; 109 equal companyfacts, 0 differ, 113 without a companyfacts fact (15 custom-tag, 105 dimensional).

## Hand check vs the shared reader (data-team/companies/reads/tools/docmap.py @558f2f15, origin/work/reads/901-1000)
36 data points agree; 2 differ. The value kept is the one printed on the R page.

| data point | shared reader | this read (kept) | why |
|---|---|---|---|
| operating_expenses | combined OperatingExpenses 1200800000 | mapped OperatingExpenses 1200800000 | ruling 2026-11-12 (operating expenses never include cost of revenue) |
| sga_expense | mapped SellingGeneralAndAdministrativeExpense  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
