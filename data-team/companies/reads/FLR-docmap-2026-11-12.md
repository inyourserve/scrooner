# FLR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001124198-26-000007 (CIK 0001124198, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001628280-24-005451 (CIK 0001124198, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001628280-21-003360 (CIK 0001124198, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001124198.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenue | 15503000000 | 15503000000 | 16315000000 | 16315000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of revenue | -15623000000 | 15623000000 | -15741000000 | 15741000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit (loss) | -120000000 | -120000000 | 574000000 | 574000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | G&A | -196000000 | 196000000 | -203000000 | 203000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating profit (loss) | -378000000 | -378000000 | 463000000 | 463000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -42000000 | 42000000 | -46000000 | 46000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Earnings (loss) before taxes | -311000000 | -311000000 | 613000000 | 613000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax benefit (expense) (including $92 million and $(376) million attributable to equity method earnings in 2025 an | 39000000 | -39000000 | -634000000 | 634000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings (loss) attributable to Fluor | -51000000 | -51000000 | 2145000000 | 2145000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic EPS available to Fluor common stockholders (in dollars per share) | -0.31 | -0.31 | 12.48 | 12.48 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted EPS available to Fluor common stockholders (in dollars per share) | -0.31 | -0.31 | 12.3 | 12.3 | Y | FILING-CHECKED | accn 0001124198-26-000007 R3.htm period ..2025-12-31 |
| weighted_basic_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_basic_shares tag/label rules; not hand-verified |
| weighted_diluted_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_diluted_shares tag/label rules; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents ($328 and $333 related to VIEs) | 2135000000 | 2135000000 | 2829000000 | 2829000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsNotesAndLoansReceivableNetCurrent | R6.htm | Accounts receivable, net ($142 and $92 related to VIEs) | 1073000000 | 1073000000 | 921000000 | 921000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 6442000000 | 6442000000 | 5175000000 | 5175000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | PP&E, net ($41 and $46 related to VIEs) | 464000000 | 464000000 | 494000000 | 494000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| goodwill | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 8236000000 | 8236000000 | 9143000000 | 9143000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable ($205 and $233 related to VIEs) | 1482000000 | 1482000000 | 1220000000 | 1220000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 3378000000 | 3378000000 | 3071000000 | 3071000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total shareholders' equity | 3244000000 | 3244000000 | 3949000000 | 3949000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Operating cash flow | -387000000 | -387000000 | 828000000 | 828000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Investing cash flow | 437000000 | 437000000 | -333000000 | -333000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Financing cash flow | -797000000 | -797000000 | -116000000 | -116000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -50000000 | 50000000 | -164000000 | 164000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 68000000 | 68000000 | 73000000 | 73000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 30000000 | 30000000 | 31000000 | 31000000 | Y | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsPreferredStockAndPreferenceStock | R8.htm | Dividends paid on CPS | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -754000000 | 754000000 | -125000000 | 125000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001124198-26-000007 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R6.htm | Long-term debt | 1070000000 | 1070000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock shares outstanding (in shares) | 152047739 | 152047739 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001628280-24-005451 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -60000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001628280-24-005451 R3.htm prints 'Earnings (loss) from Cont Ops before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 315000000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001628280-21-003360 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -28720000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
