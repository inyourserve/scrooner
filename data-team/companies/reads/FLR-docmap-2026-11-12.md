# FLR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001124198-26-000007 (CIK 0001124198, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001047469-16-010220 (CIK 0001124198, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001047469-18-000900 (CIK 0001124198, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001628280-24-005451 (CIK 0001124198, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0001124198.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenue | 15503000000 | 15503000000 | 16315000000 | 16315000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of revenue | -15623000000 | 15623000000 | -15741000000 | 15741000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit (loss) | -120000000 | -120000000 | 574000000 | 574000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:ForeignCurrencyTransactionGainLossBeforeTax | R3.htm | G&A + Foreign currency gain (loss) | -258000000 | 134000000 | -111000000 | 295000000 | N (printed -258000000 vs API 134000000) | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | G&A | -196000000 | 196000000 | -203000000 | 203000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (776 tags across all 85 R pages, face and notes) of 0001124198-26-000007; label search over every tag in the filing (custom included) found no candidate |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating profit (loss) | -378000000 | -378000000 | 463000000 | 463000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -42000000 | 42000000 | -46000000 | 46000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Earnings (loss) before taxes | -311000000 | -311000000 | 613000000 | 613000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax benefit (expense) (including $92 million and $(376) million attributable to equity method earnings in 2025 an | 39000000 | -39000000 | -634000000 | 634000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings (loss) attributable to Fluor | -51000000 | -51000000 | 2145000000 | 2145000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic EPS available to Fluor common stockholders (in dollars per share) | -0.31 | -0.31 | 12.48 | 12.48 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted EPS available to Fluor common stockholders (in dollars per share) | -0.31 | -0.31 | 12.3 | 12.3 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R49.htm | Weighted average common shares outstanding (in shares) | 164000000000000 | 164000000 |  |  | N (printed 164000000000000 vs API 164000000) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R49.htm 'Earnings Per Share - Schedule of Calculations of Basic and Diluted EPS (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R49.htm | Weighted average diluted shares outstanding (in shares) | 164000000000000 | 164000000 |  |  | N (printed 164000000000000 vs API 164000000) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R49.htm 'Earnings Per Share - Schedule of Calculations of Basic and Diluted EPS (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents ($328 and $333 related to VIEs) | 2135000000 | 2135000000 | 2829000000 | 2829000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsNotesAndLoansReceivableNetCurrent | R6.htm | Accounts receivable, net ($142 and $92 related to VIEs) | 1073000000 | 1073000000 | 921000000 | 921000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (776 tags across all 85 R pages, face and notes) of 0001124198-26-000007; label search over every tag in the filing (custom included) found no candidate |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 6442000000 | 6442000000 | 5175000000 | 5175000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | PP&E, net ($41 and $46 related to VIEs) | 464000000 | 464000000 | 494000000 | 494000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R51.htm | Goodwill | 200000000 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R51.htm 'Operating Information by Segment and Geographic Area - External Revenue and Segm' (MetaLinks.json presentation) |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 8236000000 | 8236000000 | 9143000000 | 9143000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable ($205 and $233 related to VIEs) | 1482000000 | 1482000000 | 1220000000 | 1220000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 3378000000 | 3378000000 | 3071000000 | 3071000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (776 tags across all 85 R pages, face and notes) of 0001124198-26-000007; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total shareholders' equity | 3244000000 | 3244000000 | 3949000000 | 3949000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Operating cash flow | -387000000 | -387000000 | 828000000 | 828000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Investing cash flow | 437000000 | 437000000 | -333000000 | -333000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Financing cash flow | -797000000 | -797000000 | -116000000 | -116000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -50000000 | 50000000 | -164000000 | 164000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 68000000 | 68000000 | 73000000 | 73000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 30000000 | 30000000 | 31000000 | 31000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsPreferredStockAndPreferenceStock | R8.htm | Dividends paid on CPS | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -754000000 | 754000000 | -125000000 | 125000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R63.htm | Interest | 40000000 | 40000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R63.htm 'Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R62.htm | Income taxes (net of refunds) | 213000000 | 213000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R62.htm 'Income Taxes - Schedule of Cash paid for income taxes net of refunds (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R6.htm | Long-term debt | 1070000000 | 1070000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock shares outstanding (in shares) | 152047739 | 152047739 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-010220 R2.htm prints 'TOTAL REVENUE' on us-gaap:Revenues = 18114048000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-16-010220 R2.htm prints 'TOTAL COST OF REVENUE' on us-gaap:CostOfServices = 17019352000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-16-010220 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001047469-16-010220 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001047469-16-010220 R2.htm prints 'Corporate general and administrative expense' on us-gaap:GeneralAndAdministrativeExpense = 168329000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047469-16-010220 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001047469-16-010220 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 44770000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047469-16-010220 R2.htm prints 'EARNINGS FROM CONTINUING OPERATIONS BEFORE TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 726552000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-16-010220 R2.htm prints 'INCOME TAX EXPENSE' on us-gaap:IncomeTaxExpenseBenefit = 245888000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-16-010220 R2.htm prints 'NET EARNINGS ATTRIBUTABLE TO FLUOR CORPORATION' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 412512000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-010220 R2.htm prints 'Net earnings (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.85 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-010220 R2.htm prints 'Net earnings (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.81 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-010220 R2.htm prints 'BASIC (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 144805000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-010220 R2.htm prints 'DILUTED (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 146722000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Cash and cash equivalents ($289,991 and $352,996 related to variable interest en' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1949886000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Accounts and notes receivable, net ($186,833 and $193,565 related to VIEs)' on us-gaap:AccountsNotesAndLoansReceivableNetCurrent = 1203024000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 5278287000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Net property, plant and equipment ( $70,247 and $77,579 related to VIEs)' on us-gaap:PropertyPlantAndEquipmentNet = 892340000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 111646000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-010220 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 7631506000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Trade accounts payable ($178,139 and $213,837 related to VIEs)' on us-gaap:AccountsPayableCurrent = 1266509000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2935352000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-010220 R4.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 2997347000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 849132000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Cash utilized by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -66507000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Cash utilized by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -728230000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -240220000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-010220 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Amortization of stock-based awards' on us-gaap:ShareBasedCompensation = 61053000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -125204000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-16-010220 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -509658000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-16-010220 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-16-010220 R6.htm read; no row matched (auto)
- cost_of_revenue: era 10-K 0001047469-18-000900 R2.htm prints 'TOTAL COST OF REVENUE' on us-gaap:CostOfServices = 18902480000 (FILING-CHECKED)
- net_income: era 10-K 0001047469-18-000900 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 191377000 (FILING-CHECKED)
- interest_expense: era 10-K 0001628280-24-005451 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -60000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001628280-24-005451 R3.htm prints 'Earnings (loss) from Cont Ops before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 315000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: N (printed -258000000 vs API 134000000) (us-gaap:GeneralAndAdministrativeExpense+us-gaap:ForeignCurrencyTransactionGainLossBeforeTax)
- weighted_basic_shares: N (printed 164000000000000 vs API 164000000) (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: N (printed 164000000000000 vs API 164000000) (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)
- goodwill: API missing (us-gaap:Goodwill)
