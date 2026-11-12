# FNB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000037808-26-000007 (CIK 0000037808, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- 10-K 0000037808-24-000006 (CIK 0000037808, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- companyfacts CIK0000037808.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the revenue tag/label rules; not hand-verified |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the cost_of_revenue tag/label rules; not hand-verified |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the sga_expense tag/label rules; not hand-verified |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_income tag/label rules; not hand-verified |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Total Interest Expense | 930000000 | 930000000 | 972000000 | 972000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income Before Income Taxes | 669000000 | 669000000 | 555000000 | 555000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income taxes | 104000000 | 104000000 | 90000000 | 90000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income | 565000000 | 565000000 | 465000000 | 465000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (USD per share) | 1.57 | 1.57 | 1.27 | 1.27 | Y | FILING-CHECKED | accn 0000037808-26-000007 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (USD per share) | 1.56 | 1.56 | 1.27 | 1.27 | Y | FILING-CHECKED | accn 0000037808-26-000007 R5.htm period ..2025-12-31 |
| weighted_basic_shares | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the weighted_basic_shares tag/label rules; not hand-verified |
| weighted_diluted_shares | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the weighted_diluted_shares tag/label rules; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and Cash Equivalents | 2498000000 | 2498000000 | 2419000000 | 2419000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the accounts_receivable tag/label rules; not hand-verified |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_assets tag/label rules; not hand-verified |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Premises and equipment, net | 568000000 | 568000000 | 536000000 | 536000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2480000000 | 2480000000 | 2478000000 | 2478000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 50229000000 | 50229000000 | 48625000000 | 48625000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the accounts_payable tag/label rules; not hand-verified |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_liabilities tag/label rules; not hand-verified |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 43470000000 | 43470000000 | 42323000000 | 42323000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Shareholders’ Equity | 6759000000 | 6759000000 | 6302000000 | 6302000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash flows provided by (used in) operating activities | 482000000 | 482000000 | 642000000 | 642000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash flows provided by (used in) investing activities | -1487000000 | -1487000000 | -1703000000 | -1703000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash flows provided by (used in) financing activities | 1084000000 | 1084000000 | 1904000000 | 1904000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Increase in premises and equipment | -106000000 | 106000000 | -139000000 | 139000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R10.htm | Depreciation, amortization and accretion | 77000000 | 77000000 | 67000000 | 67000000 | Y | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| sbc | not_presented |  | R10.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R10.htm read; no face row matched the sbc tag/label rules; not hand-verified |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Common stock | -174000000 | 174000000 | -175000000 | 175000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Repurchases of common stock | -50000000 | 50000000 | -3000000 | 3000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000037808-26-000007 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R10.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R10.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R10.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R10.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R3.htm | Short-term borrowings + Long-term borrowings | 3918000000 | 3918000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0000037808-24-000006 R5.htm prints 'Total Interest Expense' on us-gaap:InterestExpense = 656000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
