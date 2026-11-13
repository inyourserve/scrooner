# CINF document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000020286-26-000008 (CIK 0000020286, filed 2026-02-23): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000020286-16-000055 (CIK 0000020286, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000020286-17-000013 (CIK 0000020286, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000020286-21-000013 (CIK 0000020286, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000020286.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 12631000000 | 12631000000 | 11337000000 | 11337000000 | Y | FILING-CHECKED | accn 0000020286-26-000008 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| cost_of_revenue | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | insurer: cost of revenue not applicable (rule 15) / check: hand R5.htm corrected: Insurer; no cost-of-revenue line: OUT per rule 15. |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | insurer: gross profit not applicable (rule 15) / check: hand R5.htm corrected: Insurer; no gross profit line: OUT per rule 15. |
| operating_expenses | combined | us-gaap:BenefitsLossesAndExpenses | R5.htm | Total benefits and expenses | 9651000000 |  | 8479000000 |  |  | FILING-CHECKED | insurer total includes losses and contract holders' benefits 6,640 and interest expense 53; combined, never opex / check: hand R5.htm corrected: IS prints 'Total benefits and expenses' 9,651 / 8,479 (us-gaap:BenefitsLossesAndExpenses), a total that includes insurance losses (the insurer's cost of revenue) and interest expense 53: combined, not opex, but not absent. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1175 tags across all 125 R pages, face and notes) of 0000020286-26-000008; no face row matched / check: hand R5.htm agree |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | insurer: R&D not applicable (rule 15) / check: hand R5.htm corrected: Insurer; no R&D line: OUT per rule 15. |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1175 tags across all 125 R pages, face and notes) of 0000020286-26-000008; no face row matched / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest expense | 53000000 | 53000000 | 53000000 | 53000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income Before Income Taxes | 2980000000 | 2980000000 | 2858000000 | 2858000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Total provision for income taxes | 587000000 | 587000000 | 566000000 | 566000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income | 2393000000 | 2393000000 | 2292000000 | 2292000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income—basic | 15.32 | 15.32 | 14.65 | 14.65 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income—diluted | 15.17 | 15.17 | 14.53 | 14.53 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R100.htm | Net Income Per Common Share (Calculations For Basic And Diluted Earnings Per Share) (Details) | 156100000 | 156100000 | 156400000 |  | Y | FILING-CHECKED | not on face IS; R100 EPS note 156.1 / 156.4 million / check: hand R100.htm corrected: Not on the face IS; R100 Basic weighted-average common shares 156.1 / 156.4 million. |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R100.htm | Net Income Per Common Share (Calculations For Basic And Diluted Earnings Per Share) (Details) | 157700000 | 157700000 | 157800000 |  | Y | FILING-CHECKED | not on face IS; R100 EPS note 157.7 / 157.8 million / check: hand R100.htm corrected: Not on the face IS; R100 Diluted weighted-average shares 157.7 / 157.8 million. |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsFairValueDisclosure | R3.htm | Cash and cash equivalents | 1431000000 | 1431000000 | 983000000 | 983000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000020286-26-000008 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1175 tags across all 125 R pages, face and notes) of 0000020286-26-000008; no face row matched / check: hand R3.htm agree |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | insurer: inventory not applicable (rule 15) / check: hand R3.htm corrected: Insurer; no inventory line: OUT per rule 15. |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | insurer: unclassified balance sheet (rule 15) / check: hand R3.htm corrected: Insurer unclassified BS: OUT per rule 15. |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Land, building and equipment, net, for company use (accumulated depreciation: 2025—$367; 2024—$347) | 219000000 | 219000000 | 214000000 | 214000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R51.htm | Summary Of Significant Accounting Policies (Narrative) (Details) | 30000000 |  | 30000000 |  |  | FILING-CHECKED | not on face BS; R51 policies note Goodwill $30,000,000 / $30,000,000 / check: hand R51.htm corrected: No goodwill line on the BS (inside Other assets); R51 accounting policies note prints Goodwill $30,000,000 at both Dec 31 2025 and 2024. |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 41002000000 | 41002000000 | 36501000000 | 36501000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1175 tags across all 125 R pages, face and notes) of 0000020286-26-000008; no face row matched / check: hand R3.htm agree |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | insurer: unclassified balance sheet (rule 15) / check: hand R3.htm corrected: Insurer unclassified BS: OUT per rule 15. |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 25091000000 | 25091000000 | 22566000000 | 22566000000 | Y | FILING-CHECKED | accn 0000020286-26-000008 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders' equity | 15911000000 | 15911000000 | 13935000000 | 13935000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 3112000000 | 3112000000 | 2649000000 | 2649000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -1691000000 | -1691000000 | -1696000000 | -1696000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -973000000 | -973000000 | -877000000 | -877000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Investment in buildings and equipment | -20000000 | 20000000 | -22000000 | 22000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | cinf:DepreciationAmortizationAndOther | R9.htm | Depreciation, amortization and other | 168000000 |  | 130000000 |  | API missing | FILING-CHECKED | CF line 'Depreciation, amortization and other' (company extension) includes other non-cash items; combined / check: hand R9.htm corrected: CF line is 'Depreciation, amortization and other' 168 / 130 (cinf extension): includes 'other', so combined, not pure D&A (R51 depreciation expense alone is 36 / 34). |
| sbc | mapped | cinf:NonCashShareBasedCompensation | R9.htm | Share-based compensation | 37000000 |  | 51000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000020286-26-000008 R9.htm period ..2025-12-31 / check: hand R9.htm agree |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Payment of cash dividends to shareholders | -525000000 | 525000000 | -490000000 | 490000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Shares acquired - share repurchase authorization | -205000000 | 205000000 | -126000000 | 126000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 53000000 | 53000000 | 53000000 | 53000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid | 220000000 | 220000000 | 395000000 | 395000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000020286-26-000008 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:NotesPayable+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Long-Term Debt and Lease Obligation | 886000000 |  | 875000000 |  |  | FILING-CHECKED | Note payable (short-term) + Long-Term Debt and Lease Obligation (includes finance leases by tag, not added again) / check: hand R3.htm corrected: BS prints Note payable 25 and Long-Term Debt and Lease Obligation 861 (finance leases inside by tag); machine omitted the note payable. 25 + 861 = 886; FY1 25 + 850 = 875. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R8.htm | Consolidated Statements Of Shareholders' Equity |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R8.htm 'Consolidated Statements Of Shareholders' Equity' (MetaLinks.json presentation); HAND REVIEW: no period-end value row found on the R page (only roll-forward or dimensioned rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Total revenues' on us-gaap:Revenues = 5142000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 53000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 881000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Total provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 247000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Net Income' on us-gaap:NetIncomeLoss = 634000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Net income—basic (in usd per share)' on us-gaap:EarningsPerShareBasic = 3.87 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000020286-16-000055 R4.htm prints 'Net income—diluted (in usd per share)' on us-gaap:EarningsPerShareDiluted = 3.83 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000020286-16-000055 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000020286-16-000055 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000020286-16-000055 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 544000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000020286-16-000055 R2.htm prints 'Land, building and equipment, net, for company use (accumulated depreciation: 20' on us-gaap:PropertyPlantAndEquipmentNet = 185000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000020286-16-000055 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000020286-16-000055 R2.htm prints 'Total assets' on us-gaap:Assets = 18888000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000020286-16-000055 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 12461000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000020286-16-000055 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 6427000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1064000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -624000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -487000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Investment in buildings and equipment, net' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -10000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 52000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 20000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Payment of cash dividends to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -366000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Shares acquired - share repurchase authorization' on us-gaap:PaymentsForRepurchaseOfCommonStock = -53000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 52000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000020286-16-000055 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 245000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000020286-17-000013 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 812000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000020286-21-000013 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1499000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- goodwill: API missing (us-gaap:Goodwill)
- depreciation_and_amortization: API missing (cinf:DepreciationAmortizationAndOther)
- sbc: API missing (cinf:NonCashShareBasedCompensation)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 20 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 12.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
