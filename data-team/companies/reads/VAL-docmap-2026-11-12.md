# VAL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000314808-26-000029 (CIK 0000314808, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000314808-16-000258 (CIK 0000314808, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000314808-22-000011 (CIK 0000314808, era filing): COVER R1.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0000314808-21-000007 (CIK 0000314808, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0000314808.json (one call); submissions CIK0000314808.json (SIC 1381).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total operating revenues | 2369000000 | 2369000000 | 2362600000 | 2362600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of Product and Service Sold | 1629700000 | 1629700000 | 1760900000 | 1760900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Income statement lists revenues and operating expense lines (contract drilling, reimbursable, depreciation, G&A) to operating income with no gross profit line; revenue and segment pages have none. / pages opened: R3, R9, R20, R28, R38, R42, R43 |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 1900400000 | 1900400000 | 1999300000 | 1999300000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 97100000 | 97100000 | 116300000 | 116300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No R&D expense anywhere in the filing; listed pages are tax, debt, compensation, lease and maintenance details. / pages opened: R70, R71, R53, R58, R76, R88 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | OPERATING INCOME | 477000000 | 477000000 | 352300000 | 352300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestExpenseOther | R3.htm | Interest expense, net | 98800000 | 98800000 | 84800000 | 84800000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME BEFORE INCOME TAXES | 552300000 | 552300000 | 370200000 | 370200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Total provision for income taxes | -426800000 | -426800000 | 400000 | 400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME ATTRIBUTABLE TO VALARIS | 982800000 | 982800000 | 373400000 | 373400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic | 13.92 | 13.92 | 5.18 | 5.18 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted | 13.86 | 13.86 | 5.12 | 5.12 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic | 70600000 | 70600000 | 72100000 | 72100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted | 70900000 | 70900000 | 72900000 | 72900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 599400000 | 599400000 | 368200000 | 368200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Accounts receivable, net | 474800000 | 474800000 | 571200000 | 571200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet has no inventory or materials line and there are no listed pages. / pages opened: R5 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1225300000 | 1225300000 | 1078700000 | 1078700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 2088800000 | 2088800000 | 1932900000 | 1932900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| goodwill | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet has no goodwill; listed pages (policies, ARO investee, PP&E, segments) report none for Valaris. / pages opened: R5, R7, R40, R46, R50, R80 |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 5304800000 | 5304800000 | 4419800000 | 4419800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable - trade | 348200000 | 348200000 | 328500000 | 328500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Liabilities, Current | 691600000 | 691600000 | 679500000 | 679500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Liabilities | 2133100000 | 2133100000 | 2175500000 | 2175500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Valaris shareholders' equity | 3169600000 | 3169600000 | 2238500000 | 2238500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 546200000 | 546200000 | 355400000 | 355400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash Provided by (Used in) Investing Activities, Total | -205600000 | -205600000 | -452300000 | -452300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -103600000 | -103600000 | -158300000 | -158300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Additions to property and equipment | -343500000 | 343500000 | -455100000 | 455100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation expense | 146300000 | 146300000 | 122100000 | 122100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 25200000 | 25200000 | 27700000 | 27700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No common dividends in the cash flow statement or equity note; ARO pages concern the investee and are excluded. / pages opened: R7, R10, R14, R29, R33, R45, R46 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Payments for Repurchase of Common Stock | -100000000 | 100000000 | -126400000 | 126400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R94.htm | Interest, net of amounts capitalized | 90500000 | 90500000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R94.htm 'Supplemental Financial Information (Cash Paid For Interest And Income Taxes) (De' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R91.htm | Income Taxes Paid, Net | 61500000 | 61500000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R91.htm 'Supplemental Financial Information (Cash Taxes Paid) (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | LONG-TERM DEBT | 1086000000 | 1086000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common Stock, Shares, Outstanding | 69200000 | 69200000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000314808-16-000258 R2.htm prints 'OPERATING REVENUES' on us-gaap:RevenueOilAndGasServices = 4063400000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000314808-16-000258 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 5306900000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000314808-16-000258 R2.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 118400000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000314808-16-000258 R2.htm prints 'OPERATING INCOME' on us-gaap:OperatingIncomeLoss = -1243500000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -216300000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000314808-16-000258 R2.htm prints 'INCOME FROM CONTINUING OPERATIONS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -1471200000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Total provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -13900000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000314808-16-000258 R2.htm prints 'NET INCOME ATTRIBUTABLE TO ENSCO' on us-gaap:NetIncomeLoss = -1594800000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Total earnings per share - basic' on us-gaap:EarningsPerShareBasic = -6.88 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Total earnings per share - diluted' on us-gaap:EarningsPerShareDiluted = -6.88 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 232200000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000314808-16-000258 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 232200000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 121300000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 582000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2285100000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 11087800000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000314808-16-000258 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 13637000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Accounts payable - trade' on us-gaap:AccountsPayableCurrent = 224600000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 775500000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000314808-16-000258 R4.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0000314808-16-000258 R4.htm prints 'Total Ensco shareholders' equity' on us-gaap:StockholdersEquity = 6512900000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000314808-16-000258 R6.htm prints 'Net cash provided by operating activities of continuing operations' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1697900000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000314808-16-000258 R6.htm prints 'Net cash used in investing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -2040600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000314808-16-000258 R6.htm prints 'Net cash (used in) provided by financing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -191800000 (FILING-CHECKED)
- capex: FY2015 10-K 0000314808-16-000258 R6.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1619500000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000314808-16-000258 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000314808-16-000258 R6.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 40200000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000314808-16-000258 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000314808-16-000258 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000314808-16-000258 R6.htm read; no row matched (auto)
- interest_expense: 10-K 0000314808-22-000011 statement not identified (auto)
- cash_paid_for_income_taxes: era 10-K 0000314808-22-000011 R8.htm read; no row matched (auto)
- income_before_tax: era 10-K 0000314808-21-000007 R2.htm prints 'LOSS FROM CONTINUING OPERATIONS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -5117000000 (FILING-CHECKED)
- basic_eps: era 10-K 0000314808-21-000007 R2.htm prints 'Total earnings per share - basic' on us-gaap:EarningsPerShareBasicAndDiluted = -24.42 (FILING-CHECKED)
- diluted_eps: era 10-K 0000314808-21-000007 R2.htm prints 'Total earnings per share - basic' on us-gaap:EarningsPerShareBasicAndDiluted = -24.42 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
