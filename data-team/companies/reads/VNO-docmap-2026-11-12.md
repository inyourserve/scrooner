# VNO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000899689-26-000009 (CIK 0000899689, filed 2026-02-09): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000899689-19-000010 (CIK 0000899689, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0000899689.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 1810425000 | 1810425000 | 1787686000 | 1787686000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the cost_of_revenue tag/label rules; not hand-verified |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total expenses | -1551744000 | 1551744000 | -1541696000 | 1541696000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | -156115000 | 156115000 | -148520000 | 148520000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_income tag/label rules; not hand-verified |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 950713000 | 950713000 | 42845000 | 42845000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -13509000 | 13509000 | -22729000 | 22729000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Vornado/Vornado Realty L.P. | 904955000 | 904955000 | 70387000 | 70387000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income per common share (in dollars per share) | 4.4 | 4.4 | 0.04 | 0.04 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income per common share (in dollars per share) | 4.2 | 4.2 | 0.04 | 0.04 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average shares outstanding (in shares) | 191759000 | 191759000 | 190539000 | 190539000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average shares outstanding (in shares) | 201049000 | 201049000 | 196626000 | 196626000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 840850000 | 840850000 | 733947000 | 733947000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the accounts_receivable tag/label rules; not hand-verified |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_assets tag/label rules; not hand-verified |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the ppe_net tag/label rules; not hand-verified |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R3.htm | Assets | 15521118000 | 15521118000 | 15998608000 | 15998608000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 376190000 | 376190000 | 374013000 | 374013000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000899689-26-000009 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_liabilities tag/label rules; not hand-verified |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 8716595000 | 8716595000 | 9826739000 | 9826739000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders' / partners' equity | 5986727000 | 5986727000 | 5158242000 | 5158242000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1258385000 | 1258385000 | 537723000 | 537723000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | 115507000 | 115507000 | -597365000 | -597365000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1345965000 | -1345965000 | -252323000 | -252323000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:CapitalExpendituresIncurredButNotYetPaid | R9.htm | Accrued capital expenditures included in accounts payable and accrued expenses | 43875000 | 43875000 | 39784000 | 39784000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization (including amortization of deferred financing costs) | 481456000 | 481456000 | 469423000 | 469423000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 25479000 | 25479000 | 30172000 | 30172000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid on common shares | -141277000 | 141277000 | -141103000 | 141103000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common shares | -50991000 | 50991000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash payments for interest (excluding capitalized interest) and interest rate cap premiums | 313093000 | 313093000 | 322774000 | 322774000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash payments for income taxes | 5201000 | 5201000 | 7608000 | 7608000 | Y | FILING-CHECKED | accn 0000899689-26-000009 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:SeniorNotes | R3.htm | Senior unsecured notes, net | 747202000 | 747202000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common shares of beneficial interest: outstanding shares (in shares) | 190666367 | 190666367 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- capex: era 10-K 0000899689-19-000010 R7.htm prints 'Additions to real estate' on us-gaap:PaymentsForCapitalImprovements = -234602000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
