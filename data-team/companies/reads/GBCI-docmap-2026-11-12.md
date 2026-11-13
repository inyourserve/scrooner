# GBCI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000868671-26-000023 (CIK 0000868671, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000868671-16-000137 (CIK 0000868671, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000868671-24-000042 (CIK 0000868671, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000868671-21-000037 (CIK 0000868671, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000868671.json (one call); submissions CIK0000868671.json (SIC 6022).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | component_in_note | us-gaap:InterestAndDividendIncomeOperating | R5.htm | Total interest income / Total non-interest income |  |  |  |  |  | FILING-CHECKED | check: hand / Bank prints Total interest income 1,295,797k and Total non-interest income 141,385k but no total revenue line; R59's 101,072k covers only contract-with-customer revenue and R116 is parent-only. / pages opened: R5, R9, R59, R63, R86, R107 |
| cost_of_revenue | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the bank template (SIC 6022; Dhairya OUT ruling main @020ebb29); was: not_presented |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the bank template (SIC 6022; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total non-interest expense | 668777000 |  |  |  |  | FILING-CHECKED | check: hand / Bank's total non-interest expense is its operating expense total. / pages opened: R5, R107, R116, R25, R51, R80 |
| sga_expense | component_in_note | us-gaap:LaborAndRelatedExpense | R5.htm | Compensation and employee benefits | 393295000 |  |  |  |  | FILING-CHECKED | check: hand / Bank presents non-interest expense by nature (compensation 393,295k, occupancy, advertising, data processing, other); no SG&A line. / pages opened: R5, R15, R25, R27, R42, R51, R53 |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the bank template (SIC 6022; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Bank income statement runs from net interest income after provision through non-interest income and expense to income before taxes; no operating income line. / pages opened: R5 |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Total interest expense | 406757000 | 406757000 | 435218000 | 435218000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income Before Income Taxes | 290248000 | 290248000 | 226304000 | 226304000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Federal and state income tax expense | 51220000 | 51220000 | 36160000 | 36160000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income | 239028000 | 239028000 | 190144000 | 190144000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share (in dollars per share) | 2 | 2 | 1.68 | 1.68 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share (in dollars per share) | 1.99 | 1.99 | 1.68 | 1.68 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Average outstanding shares - basic (in shares) | 119753227 | 119753227 | 113170157 | 113170157 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Average outstanding shares - diluted (in shares) | 119935056 | 119935056 | 113243427 | 113243427 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash on hand and in banks | 321526000 | 321526000 | 268746000 | 268746000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Only loans receivable and accrued interest receivable (financing/interest receivables) appear; no trade accounts receivable. / pages opened: R3, R9, R59, R60, R64, R67 |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the bank template (SIC 6022; Dhairya OUT ruling main @020ebb29); was: not_presented |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the bank template (SIC 6022; Dhairya OUT ruling main @020ebb29); was: not_presented |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R76.htm | Net premises and equipment | 486184000 | 486184000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R76.htm 'Premises and Equipment - Net of Accumulated Depreciation (Details)' (MetaLinks.json presentation) |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1378283000 | 1378283000 | 1051318000 | 1051318000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 31978063000 | 31978063000 | 27902987000 | 27902987000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Bank balance sheet has deposits, borrowings, accrued interest payable and other liabilities but no accounts payable line in the face or listed notes. / pages opened: R3, R30, R31, R56, R57, R79, R110 |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the bank template (SIC 6022; Dhairya OUT ruling main @020ebb29); was: not_presented |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 27764242000 | 27764242000 | 24679133000 | 24679133000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 4213821000 | 4213821000 | 3223854000 | 3223854000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 374399000 | 374399000 | 258037000 | 258037000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | 1064425000 | 1064425000 | 493141000 | 493141000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash (used in) provided by financing activities | -1051971000 | -1051971000 | -1257112000 | -1257112000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Net additions to premises and equipment | -26848000 | 26848000 | -48277000 | 48277000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationNonproduction | R9.htm | Depreciation and amortization | 33027000 | 33027000 | 28907000 | 28907000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation, net of tax benefits | 6345000 | 6345000 | 5694000 | 5694000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends paid | -162736000 | 162736000 | -150034000 | 150034000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:ProceedsFromPaymentsForInSecuritiesSoldUnderAgreementsToRepurchase | R9.htm | Net increase in securities sold under agreements to repurchase | 285744000 | 285744000 | 286320000 | 286320000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid during the period for interest | 413593000 | 413593000 | 528911000 | 528911000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid during the period for income taxes | 32160000 | 32160000 | 15604000 | 15604000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000868671-26-000023 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:FinanceLeaseLiability | R3.htm | Finance lease liabilities | 28808000 | 28808000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; the only debt lines on the BS face carry finance lease tags (summed); operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Number of common stock shares outstanding (in shares) | 129971712 | 129971712 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- interest_expense: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 29275000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 150126000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Federal and state income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 33999000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Net Income' on us-gaap:NetIncomeLoss = 116127000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 1.54 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted = 1.54 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Average outstanding shares - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 75542455 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000868671-16-000137 R4.htm prints 'Average outstanding shares - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 75595581 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000868671-16-000137 R2.htm prints 'Cash on hand and in banks' on us-gaap:CashAndDueFromBanks = 117137000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000868671-16-000137 R2.htm prints 'Premises and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 194030000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000868671-16-000137 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 140638000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000868671-16-000137 R2.htm prints 'Total assets' on us-gaap:Assets = 9089232000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000868671-16-000137 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 8012582000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000868671-16-000137 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 1076650000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 171466000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -676571000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 255949000 (FILING-CHECKED)
- capex: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Net addition of premises and equipment and other real estate owned' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -18224000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000868671-16-000137 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Stock-based compensation expense, net of tax benefits' on us-gaap:ShareBasedCompensation = 1087000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -79456000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Net increase in securities sold under agreements to repurchase' on us-gaap:ProceedsFromPaymentsForInSecuritiesSoldUnderAgreementsToRepurchase = 24951000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Cash paid during the period for interest' on us-gaap:InterestPaid = 30103000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000868671-16-000137 R8.htm prints 'Cash paid during the period for income taxes' on us-gaap:IncomeTaxesPaid = 39622000 (FILING-CHECKED)
- interest_expense: era 10-K 0000868671-24-000042 R5.htm prints 'Total interest expense' on us-gaap:InterestExpense = 325973000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000868671-21-000037 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 328040000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
