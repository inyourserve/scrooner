# RIG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001451505-26-000018 (CIK 0001451505, filed 2026-02-23): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001451505-24-000015 (CIK 0001451505, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0001451505.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Contract drilling revenues | 3965000000 | 3965000000 | 3524000000 | 3524000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Operating and maintenance | 2406000000 | 2406000000 | 2199000000 | 2199000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | mapped | us-gaap:CostsAndExpenses | R2.htm | Total costs and expenses | 3260000000 | 3260000000 | 3152000000 | 3152000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R2.htm | General and administrative | 195000000 | 195000000 | 214000000 | 214000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating loss | -2337000000 | -2337000000 | -417000000 | -417000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R2.htm | Interest expense, net of amounts capitalized | -555000000 | 555000000 | -362000000 | 362000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Loss before income taxes | -2948000000 | -2948000000 | -523000000 | -523000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income tax expense (benefit) | -33000000 | -33000000 | -11000000 | -11000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net loss attributable to controlling interest | -2915000000 | -2915000000 | -512000000 | -512000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Loss per share, basic (in dollars per share) | -3.04 | -3.04 | -0.6 | -0.6 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Loss per share, diluted (in dollars per share) | -3.04 | -3.04 | -0.76 | -0.76 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Weighted-average shares outstanding, basic (in shares) | 960000000 | 960000000 | 850000000 | 850000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Weighted-average shares outstanding, diluted (in shares) | 960000000 | 960000000 | 925000000 | 925000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 620000000 | 620000000 | 560000000 | 560000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R4.htm | Accounts receivable, net | 540000000 | 540000000 | 564000000 | 564000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| inventory | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 2081000000 | 2081000000 | 2452000000 | 2452000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property and equipment, net | 12577000000 | 12577000000 | 15831000000 | 15831000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| goodwill | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 15642000000 | 15642000000 | 19371000000 | 19371000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 242000000 | 242000000 | 255000000 | 255000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 1336000000 | 1336000000 | 1663000000 | 1663000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total controlling interest shareholders' equity | 8108000000 | 8108000000 | 10284000000 | 10284000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 749000000 | 749000000 | 447000000 | 447000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -33000000 | -33000000 | -151000000 | -151000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -660000000 | -660000000 | -350000000 | -350000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -123000000 | 123000000 | -254000000 | 254000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001451505-26-000018 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 659000000 | 659000000 | 739000000 | 739000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 35000000 | 35000000 | 47000000 | 47000000 | Y | FILING-CHECKED | accn 0001451505-26-000018 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R4.htm | Debt due within one year + Long-term debt | 5657000000 | 5657000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Shares, outstanding | 1101528481 | 1101528481 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001451505-24-000015 R2.htm prints 'Interest expense, net of amounts capitalized' on us-gaap:InterestExpense = -646000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
