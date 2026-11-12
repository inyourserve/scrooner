# MGY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001698990-26-000005 (CIK 0001698990, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- companyfacts CIK0001698990.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 1311845000 | 1311845000 | 1315886000 | 1315886000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the cost_of_revenue tag/label rules; not hand-verified |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | mapped | us-gaap:OperatingCostsAndExpenses | R5.htm | Total operating expenses | 872664000 | 872664000 | 803898000 | 803898000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative expenses | 97038000 | 97038000 | 88733000 | 88733000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | OPERATING INCOME | 439181000 | 439181000 | 511988000 | 511988000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense, net | -21617000 | -21617000 | -14371000 | -14371000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | INCOME BEFORE INCOME TAXES | 417411000 | 417411000 | 493143000 | 493143000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 80132000 | 80132000 | 95813000 | 95813000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME ATTRIBUTABLE TO CLASS A COMMON STOCK | 325252000 | 325252000 | 366027000 | 366027000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.73 |  | 1.94 |  | API missing | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.73 |  | 1.94 |  | API missing | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 185581000 | 185581000 | 186465000 | 186465000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 185593000 | 185593000 | 186492000 | 186492000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 266785000 | 266785000 | 260049000 | 260049000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade receivables | 116530000 | 116530000 | 123762000 | 123762000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 442435000 | 442435000 | 410824000 | 410824000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:OilAndGasPropertySuccessfulEffortMethodNet | R3.htm | Total property, plant and equipment, net | 2424152000 | 2424152000 | 2306034000 | 2306034000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 2903092000 | 2903092000 | 2820835000 | 2820835000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 177568000 | 177568000 | 181073000 | 181073000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 288030000 | 288030000 | 290261000 | 290261000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the stockholders_equity tag/label rules; not hand-verified |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 878639000 | 878639000 | 920850000 | 920850000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -540747000 | -540747000 | -655122000 | -655122000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -331156000 | -331156000 | -406800000 | -406800000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the capex tag/label rules; not hand-verified |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation, depletion and amortization | 437757000 | 437757000 | 414487000 | 414487000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock based compensation | 27256000 | 27256000 | 18663000 | 18663000 | Y | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid | -113096000 | 113096000 | -97620000 | 97620000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Common stock repurchase and cancellations | -205471000 |  | -183375000 |  | API missing | FILING-CHECKED | accn 0001698990-26-000005 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Long-term debt, net | 393251000 | 393251000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 186753000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era checks (tag changes in the last ~5 years)
none found in companyfacts

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- share_buybacks: API missing (us-gaap:PaymentsForRepurchaseOfCommonStock)
