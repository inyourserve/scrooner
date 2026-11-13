# ESNT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001448893-26-000009 (CIK 0001448893, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001628280-16-011882 (CIK 0001448893, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R8.htm
- 10-K 0001448893-24-000015 (CIK 0001448893, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001448893-21-000021 (CIK 0001448893, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- companyfacts CIK0001448893.json (one call); submissions CIK0001448893.json (SIC 6351).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 1260935000 | 1260935000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R5.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation) |
| cost_of_revenue | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6351; Dhairya OUT ruling main @020ebb29); was: not_presented |
| gross_profit | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6351; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_expenses | combined | us-gaap:BenefitsLossesAndExpenses | R5.htm | Total losses and expenses | 439073000 |  |  |  |  | FILING-CHECKED | check: hand / Insurer face has no operating-expenses total; expenses appear only in 'Total losses and expenses' ($439,073K, includes loss provision and $32,696K interest) or as the narrower 'Other underwriting and operating expenses'  / pages opened: R5, R102, R105, R14, R26, R39 |
| sga_expense | combined | esnt:OtherUnderwritingAndOperatingExpenses | R5.htm | Other underwriting and operating expenses | 257040000 |  |  |  |  | FILING-CHECKED | check: hand / No SG&A line; SG&A-type cost is only inside 'Other underwriting and operating expenses' ($257,040K); its compensation/other split is given only in the segment schedule. / pages opened: R5, R102, R105, R14, R22, R27 |
| research_and_development | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6351; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_income | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | check: hand / Insurer reports income before income taxes only; no operating income subtotal on face or segment pages. / pages opened: R26, R49, R101, R102 |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Interest Expense, Operating | 32696000 | 32696000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R5.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation) |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R85.htm | Income (loss) before income taxes | 821862000 | 821862000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R85.htm 'Income Taxes - Pre Tax Income (Loss) (Details)' (MetaLinks.json presentation) |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R84.htm | Total income tax provision (benefit) | 131893000 | 131893000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R84.htm 'Income Taxes - Schedule of Income Tax Expense (Details)' (MetaLinks.json presentation) |
| net_income | mapped | us-gaap:NetIncomeLoss | R90.htm | Net income | 689969000 | 689969000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R90.htm 'Earnings per Share (EPS) - Schedule of Reconciliation of Net Income and Weighted' (MetaLinks.json presentation) |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R90.htm | Basic earnings per share (in dollars per share) | 6.97 | 6.97 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R90.htm 'Earnings per Share (EPS) - Schedule of Reconciliation of Net Income and Weighted' (MetaLinks.json presentation) |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R90.htm | Diluted earnings per share (in dollars per share) | 6.9 | 6.9 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R90.htm 'Earnings per Share (EPS) - Schedule of Reconciliation of Net Income and Weighted' (MetaLinks.json presentation) |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R90.htm | Basic weighted average shares outstanding (in shares) | 98999000 | 98999000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R90.htm 'Earnings per Share (EPS) - Schedule of Reconciliation of Net Income and Weighted' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R90.htm | Diluted weighted average shares outstanding (in shares) | 100023000 | 100023000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R90.htm 'Earnings per Share (EPS) - Schedule of Reconciliation of Net Income and Weighted' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:Cash | R3.htm | Cash | 123049000 | 123049000 | 131480000 | 131480000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R63.htm | Accounts receivable, net | 51267000 |  |  |  |  | FILING-CHECKED | check: hand / Accounts Receivable note gives undimensioned Accounts receivable, net $51,267K (premiums 44,700 + other 6,567) at 2025-12-31, equal to the face 'Accounts receivable' line (tagged NotesReceivableNet). / pages opened: R3, R8, R50, R63, R104, R12 |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6351; Dhairya OUT ruling main @020ebb29); was: not_presented |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6351; Dhairya OUT ruling main @020ebb29); was: not_presented |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, equipment and software (at cost, less accumulated depreciation of $71,466 in 2025 and $72,270 in 2024) | 49189000 | 49189000 | 41871000 | 41871000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R3.htm | Goodwill and acquired intangible assets, net | 78153000 | 78153000 | 79556000 | 79556000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7441003000 | 7441003000 | 7111649000 | 7111649000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet has no accounts payable line (only 'Other accrued liabilities', whose label does not mention payables); listed notes have none. / pages opened: R76, R89, R94, R96, R100, R3 |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6351; Dhairya OUT ruling main @020ebb29); was: not_presented |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1684276000 | 1684276000 | 1507991000 | 1507991000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 5756727000 | 5756727000 | 5603658000 | 5603658000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 856053000 | 856053000 | 861532000 | 861532000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -154738000 | -154738000 | -706926000 | -706926000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -709746000 | -709746000 | -164913000 | -164913000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment and capitalization of internal-use software | -7364000 | 7364000 | -6766000 | 6766000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 5233000 | 5233000 | 5783000 | 5783000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 20847000 | 20847000 | 24778000 | 24778000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid | -122067000 | 122067000 | -118042000 | 118042000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury stock acquired | -587679000 | 587679000 | -111543000 | 111543000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest payments | -31250000 | 31250000 | -17196000 | 17196000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income tax payments | -91151000 | 91151000 | -92517000 | 92517000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:SeniorNotes | R3.htm | Senior notes due 2029, net | 495301000 | 495301000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common shares, outstanding (in shares) | 95456000 | 95456000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0001628280-16-011882 statement not identified (auto)
- interest_expense: 10-K 0001628280-16-011882 statement not identified (auto)
- income_before_tax: 10-K 0001628280-16-011882 statement not identified (auto)
- income_tax_expense: 10-K 0001628280-16-011882 statement not identified (auto)
- net_income: 10-K 0001628280-16-011882 statement not identified (auto)
- basic_eps: 10-K 0001628280-16-011882 statement not identified (auto)
- diluted_eps: 10-K 0001628280-16-011882 statement not identified (auto)
- weighted_basic_shares: 10-K 0001628280-16-011882 statement not identified (auto)
- weighted_diluted_shares: 10-K 0001628280-16-011882 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Cash' on us-gaap:Cash = 24606000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Property and equipment (at cost, less accumulated depreciation of $42,479 in 201' on us-gaap:PropertyPlantAndEquipmentNet = 9021000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-16-011882 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Total assets' on us-gaap:Assets = 1469099000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 349858000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1119241000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 224139000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -220712000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -3232000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Purchase of property and equipment, net' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -4960000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 3219000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 13633000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001628280-16-011882 R8.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Treasury stock acquired' on us-gaap:PaymentsForRepurchaseOfCommonStock = -5168000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001628280-16-011882 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-011882 R8.htm prints 'Income tax payments' on us-gaap:IncomeTaxesPaidNet = -15500000 (FILING-CHECKED)
- interest_expense: 10-K 0001448893-24-000015 statement not identified (auto)
- ppe_net: era 10-K 0001448893-24-000015 R3.htm prints 'Property and equipment (at cost, less accumulated depreciation of $71,168 in 202' on us-gaap:PropertyPlantAndEquipmentNet = 41304000 (FILING-CHECKED)
- income_before_tax: 10-K 0001448893-21-000021 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences
