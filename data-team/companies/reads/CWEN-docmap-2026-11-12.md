# CWEN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001628280-26-010952 (CIK 0001567683, filed 2026-02-24): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001567683-24-000007 (CIK 0001567683, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001628280-26-010952 (CIK 0001567683, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0001567683.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total operating revenues | 1429000000 | 1429000000 | 1371000000 | 1371000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the cost_of_revenue tag/label rules; not hand-verified |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | mapped | us-gaap:CostsAndExpenses | R3.htm | Total operating costs and expenses | 1269000000 | 1269000000 | 1175000000 | 1175000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 41000000 | 41000000 | 39000000 | 39000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 160000000 | 160000000 | 196000000 | 196000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -387000000 | 387000000 | -307000000 | 307000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Loss Before Income Taxes | -175000000 | -175000000 | -33000000 | -33000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense (benefit) | 56000000 | 56000000 | 30000000 | 30000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Clearway Energy, Inc. | 169000000 | 169000000 | 88000000 | 88000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings per weighted average common share - basic (in dollars per share) | 1.43 |  | 0.75 |  | API missing | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings per weighted average common share - diluted (in dollars per share) | 1.43 |  | 0.75 |  | API missing | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted average number of shares outstanding - basic (in shares) | 35000000 |  | 35000000 |  | API missing | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted average number of common shares outstanding - diluted (in shares) | 35000000 | 35000000 | 35000000 | 35000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 231000000 | 231000000 | 332000000 | 332000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable | 162000000 |  | 164000000 |  | API missing | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventory | 75000000 | 75000000 | 64000000 | 64000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 1152000000 | 1152000000 | 1067000000 | 1067000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment | 11596000000 | 11596000000 | 9944000000 | 9944000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| goodwill | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total Assets | 16655000000 | 16655000000 | 14329000000 | 14329000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable — trade | 95000000 |  | 82000000 |  | API missing | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1018000000 | 1018000000 | 718000000 | 718000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total Liabilities | 10741000000 | 10741000000 | 8765000000 | 8765000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R6.htm | Total Stockholders’ Equity | 5811000000 | 5811000000 | 5564000000 | 5564000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-010952 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net Cash Provided by Operating Activities | 688000000 | 688000000 | 770000000 | 770000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net Cash Used in Investing Activities | -803000000 | -803000000 | -725000000 | -725000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net Cash Provided by (Used in) Financing Activities | 200000000 | 200000000 | -363000000 | -363000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -319000000 | 319000000 | -287000000 | 287000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R8.htm | Depreciation, amortization and accretion | 682000000 | 682000000 | 627000000 | 627000000 | Y | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| sbc | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the sbc tag/label rules; not hand-verified |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid, net of amount capitalized | -348000000 | 348000000 | -324000000 | 324000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid, net of refunds received | -1000000 | 1000000 | -1000000 | 1000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010952 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Current portion of long-term debt + Long-term debt | 8606000000 | 8606000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 407547348 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001567683-24-000007 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -337000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001567683-24-000007 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = -31000000 (FILING-CHECKED)
- net_income: era 10-K 0001628280-26-010952 R3.htm prints 'Net income attributable to Clearway Energy, Inc.' on us-gaap:NetIncomeLoss = 169000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- accounts_receivable: API missing (us-gaap:AccountsReceivableNetCurrent)
- accounts_payable: API missing (us-gaap:AccountsPayableCurrent)
