# GATX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000040211-26-000018 (CIK 0000040211, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000040211-16-000064 (CIK 0000040211, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm
- 10-K 0000040211-25-000024 (CIK 0000040211, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000040211-17-000012 (CIK 0000040211, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm
- companyfacts CIK0000040211.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the revenue tag/label rules; not hand-verified |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the cost_of_revenue tag/label rules; not hand-verified |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no total opex line and no gross profit / operating income pair to tie components; not hand-verified |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the sga_expense tag/label rules; not hand-verified |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_income tag/label rules; not hand-verified |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the income_before_tax tag/label rules; not hand-verified |
| income_tax_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the income_tax_expense tag/label rules; not hand-verified |
| net_income | mapped | us-gaap:ProfitLoss | R5.htm | Net Income | 333300000 | 333300000 | 284200000 | 284200000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R5.htm period ..2025-12-31 |
| basic_eps | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the basic_eps tag/label rules; not hand-verified |
| diluted_eps | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the diluted_eps tag/label rules; not hand-verified |
| weighted_basic_shares | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the weighted_basic_shares tag/label rules; not hand-verified |
| weighted_diluted_shares | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the weighted_diluted_shares tag/label rules; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and Cash Equivalents | 743000000 | 743000000 | 401600000 | 401600000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Receivables, net | 207200000 | 207200000 | 199100000 | 199100000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_assets tag/label rules; not hand-verified |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Net operating assets and facilities | 11410900000 | 11410900000 | 10449700000 | 10449700000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 126300000 | 126300000 | 114100000 | 114100000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 17999500000 | 17999500000 | 12296500000 | 12296500000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts Payable and Accrued Expenses | 318400000 | 318400000 | 217100000 | 217100000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_liabilities tag/label rules; not hand-verified |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 14364400000 | 14364400000 | 9857600000 | 9857600000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Equity | 2750500000 | 2750500000 | 2438900000 | 2438900000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 648100000 | 648100000 | 602100000 | 602100000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1016800000 | -1016800000 | -1416700000 | -1416700000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used in) provided by financing activities | 4944800000 | 4944800000 | 770500000 | 770500000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| capex | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the capex tag/label rules; not hand-verified |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 452300000 | 452300000 | 421400000 | 421400000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R7.htm | Share-based compensation expense | 25000000 | 25000000 | 23000000 | 23000000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends | -89800000 | 89800000 | -84800000 | 84800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Stock repurchases | -65000000 | 65000000 | -21900000 | 21900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest Paid, Excluding Capitalized Interest, Operating Activity | 413200000 | 413200000 | 350100000 | 350100000 | Y | FILING-CHECKED | accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: no standard debt line on the BS face; not hand-verified |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Outstanding shares (in shares) | 35400021 | 35400021 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- net_income: 10-K 0000040211-16-000064 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 202400000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Rent and other receivables' on us-gaap:AccountsReceivableGrossCurrent = 69400000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Operating assets and facilities, net' on us-gaap:PropertyPlantAndEquipmentNet = 5698400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 79700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Assets' on us-gaap:Assets = 6894200000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Accounts Payable and Accrued Expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 170900000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 5614000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Shareholders’ Equity' on us-gaap:StockholdersEquity = 1280200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 5.343e+08 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -307600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -229000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Share-based Compensation' on us-gaap:ShareBasedCompensation = 11600000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Dividends' on us-gaap:PaymentsOfDividends = -68200000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Stock repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -125400000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- net_income: 10-K 0000040211-25-000024 statement not identified (auto)
- cash_paid_for_interest: era 10-K 0000040211-17-000012 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences
