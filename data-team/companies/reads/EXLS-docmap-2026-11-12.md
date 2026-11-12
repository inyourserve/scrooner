# EXLS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001297989-26-000008 (CIK 0001297989, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001297989-18-000002 (CIK 0001297989, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001297989-24-000003 (CIK 0001297989, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R9.htm
- companyfacts CIK0001297989.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues, net | 2087679000 | 2087679000 | 1838372000 | 1838372000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R5.htm | Cost of revenues | 1286603000 | 1286603000 | 1147359000 | 1147359000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 801076000 | 801076000 | 691013000 | 691013000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 487326000 | 487326000 | 427393000 | 427393000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative expenses | 255308000 | 255308000 | 225672000 | 225672000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 313750000 | 313750000 | 263620000 | 263620000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -17611000 | 17611000 | -19256000 | 19256000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before income tax expense and earnings from equity affiliates | 315052000 | 315052000 | 261347000 | 261347000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 63728000 | 63728000 | 62936000 | 62936000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 251019000 | 251019000 | 198297000 | 198297000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.56 | 1.56 | 1.22 | 1.22 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.54 | 1.54 | 1.21 | 1.21 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 161028312 | 161028312 | 162718840 | 162718840 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 162481586 | 162481586 | 164321656 | 164321656 | Y | FILING-CHECKED | accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 146326000 | 146326000 | 153355000 | 153355000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 343105000 | 343105000 | 304322000 | 304322000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 829957000 | 829957000 | 795189000 | 795189000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 111821000 | 111821000 | 101837000 | 101837000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 419654000 | 419654000 | 420387000 | 420387000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1702235000 | 1702235000 | 1618403000 | 1618403000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 4753000 | 4753000 | 5884000 | 5884000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 324125000 | 324125000 | 290116000 | 290116000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 789530000 | 789530000 | 688541000 | 688541000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 912705000 | 912705000 | 929862000 | 929862000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 350717000 | 350717000 | 268525000 | 268525000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -49260000 | -49260000 | -119099000 | -119099000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used for financing activities | -312764000 | -312764000 | -119101000 | -119101000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -52598000 | 52598000 | -46262000 | 46262000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization expense | 59248000 | 59248000 | 55221000 | 55221000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 79469000 | 79469000 | 72658000 | 72658000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Acquisition of treasury stock | -328490000 | 328490000 | -207926000 | 207926000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 16958000 | 16958000 | 19604000 | 19604000 | Y | FILING-CHECKED | accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of long-term borrowings + Long-term borrowings, less current portion | 298598000 | 298598000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 156430028 | 156430028 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- cost_of_revenue: era 10-K 0001297989-18-000002 R4.htm prints 'Cost of revenues (exclusive of depreciation and amortization)' on us-gaap:CostOfServices = 495586000 (FILING-CHECKED)
- interest_expense: era 10-K 0001297989-24-000003 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -13180000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
