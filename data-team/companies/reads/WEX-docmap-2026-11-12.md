# WEX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001309108-26-000010 (CIK 0001309108, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0001309108.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenues | 2660800000 | 2660800000 | 2628100000 | 2628100000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Total cost of services | 1100600000 | 1100600000 | 1037800000 | 1037800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 330200000 | 330200000 | 375800000 | 375800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 663900000 | 663900000 | 686300000 | 686300000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 420200000 | 420200000 | 417800000 | 417800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax provision | 116100000 | 116100000 | 108200000 | 108200000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to shareholders | 304100000 | 304100000 | 309600000 | 309600000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 8.57 | 8.57 | 7.59 | 7.59 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 8.47 | 8.47 | 7.5 | 7.5 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 35500000 | 35500000 | 40800000 | 40800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 35900000 | 35900000 | 41300000 | 41300000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 905800000 | 905800000 | 595800000 | 595800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the accounts_receivable tag/label rules; not hand-verified |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 9713000000 | 9713000000 | 8515500000 | 8515500000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, equipment and capitalized software | 253700000 | 253700000 | 261200000 | 261200000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 3015300000 | 3015300000 | 2983400000 | 2983400000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 14399500000 | 14399500000 | 13321600000 | 13321600000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrentAndNoncurrent | R5.htm | Accounts payable | 1.07e+09 | 1070400000 | 1090900000 | 1090900000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 9286600000 | 9286600000 | 8.327e+09 | 8327300000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 13165000000 | 13165000000 | 11832800000 | 11832800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 1234500000 | 1234500000 | 1488800000 | 1488800000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 454300000 | 454300000 | 481400000 | 481400000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -696900000 | -696900000 | -960600000 | -960600000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used for) financing activities | 418900000 | 418900000 | -260300000 | -260300000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, equipment and capitalized software | -140600000 | 140600000 | -147300000 | 147300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 331100000 | 331100000 | 321300000 | 321300000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 100300000 | 100300000 | 112200000 | 112200000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -799800000 | 799800000 | -652000000 | 652000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 333600000 | 333600000 | 328500000 | 328500000 | Y | FILING-CHECKED | accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt, net + Long-term debt, net | 4858400000 | 4858400000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 34300000 | 34300000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
none found in companyfacts

## Mismatches (printed vs API)
none beyond sign differences
