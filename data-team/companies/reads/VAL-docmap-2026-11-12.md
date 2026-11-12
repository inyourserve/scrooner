# VAL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000314808-26-000029 (CIK 0000314808, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000314808-22-000011 (CIK 0000314808, era filing): COVER R1.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0000314808.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total operating revenues | 2369000000 | 2369000000 | 2362600000 | 2362600000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of Product and Service Sold | 1629700000 | 1629700000 | 1760900000 | 1760900000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 1900400000 | 1900400000 | 1999300000 | 1999300000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 97100000 | 97100000 | 116300000 | 116300000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | OPERATING INCOME | 477000000 | 477000000 | 352300000 | 352300000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseOther | R3.htm | Interest expense, net | 98800000 | 98800000 | 84800000 | 84800000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME BEFORE INCOME TAXES | 552300000 | 552300000 | 370200000 | 370200000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Total provision for income taxes | -426800000 | -426800000 | 400000 | 400000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME ATTRIBUTABLE TO VALARIS | 982800000 | 982800000 | 373400000 | 373400000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic | 13.92 | 13.92 | 5.18 | 5.18 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted | 13.86 | 13.86 | 5.12 | 5.12 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic | 70600000 | 70600000 | 72100000 | 72100000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted | 70900000 | 70900000 | 72900000 | 72900000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 599400000 | 599400000 | 368200000 | 368200000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Accounts receivable, net | 474800000 | 474800000 | 571200000 | 571200000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1225300000 | 1225300000 | 1078700000 | 1078700000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 2.089e+09 | 2088800000 | 1932900000 | 1932900000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| goodwill | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 5304800000 | 5304800000 | 4419800000 | 4419800000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable - trade | 348200000 | 348200000 | 328500000 | 328500000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Liabilities, Current | 691600000 | 691600000 | 679500000 | 679500000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Liabilities | 2133100000 | 2133100000 | 2175500000 | 2175500000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Valaris shareholders' equity | 3169600000 | 3169600000 | 2238500000 | 2238500000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 546200000 | 546200000 | 355400000 | 355400000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash Provided by (Used in) Investing Activities, Total | -205600000 | -205600000 | -452300000 | -452300000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -103600000 | -103600000 | -158300000 | -158300000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Additions to property and equipment | -343500000 | 343500000 | -455100000 | 455100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation expense | 146300000 | 146300000 | 122100000 | 122100000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 25200000 | 25200000 | 27700000 | 27700000 | Y | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Payments for Repurchase of Common Stock | -100000000 | 100000000 | -126400000 | 126400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000314808-26-000029 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | LONG-TERM DEBT | 1086000000 | 1086000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common Stock, Shares, Outstanding | 69200000 | 69200000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0000314808-22-000011 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences
