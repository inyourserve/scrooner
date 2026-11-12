# ESNT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001448893-26-000009 (CIK 0001448893, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001628280-16-011882 (CIK 0001448893, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R8.htm
- 10-K 0001448893-24-000015 (CIK 0001448893, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001448893-18-000023 (CIK 0001448893, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R8.htm
- companyfacts CIK0001448893.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| cost_of_revenue | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| gross_profit | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| operating_expenses | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| sga_expense | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| research_and_development | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| operating_income | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| interest_expense | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| income_before_tax | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| income_tax_expense | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| net_income | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| basic_eps | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| diluted_eps | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| weighted_basic_shares | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| weighted_diluted_shares | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | AUTO: statement page not identified in FilingSummary; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:Cash | R3.htm | Cash | 123049000 | 123049000 | 131480000 | 131480000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:NotesReceivableNet | R3.htm | Accounts receivable | 51267000 | 51267000 | 55564000 | 55564000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_assets tag/label rules; not hand-verified |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, equipment and software (at cost, less accumulated depreciation of $71,466 in 2025 and $72,270 in 2024) | 49189000 | 49189000 | 41871000 | 41871000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R3.htm | Goodwill and acquired intangible assets, net | 78153000 | 78153000 | 79556000 | 79556000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7441003000 | 7441003000 | 7111649000 | 7111649000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the accounts_payable tag/label rules; not hand-verified |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the current_liabilities tag/label rules; not hand-verified |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1684276000 | 1684276000 | 1507991000 | 1507991000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 5756727000 | 5756727000 | 5603658000 | 5603658000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 856053000 | 856053000 | 861532000 | 861532000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -154738000 | -154738000 | -706926000 | -706926000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -709746000 | -709746000 | -164913000 | -164913000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment and capitalization of internal-use software | -7364000 | 7364000 | -6766000 | 6766000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 5233000 | 5233000 | 5783000 | 5783000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 20847000 | 20847000 | 24778000 | 24778000 | Y | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid | -122067000 | 122067000 | -118042000 | 118042000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury stock acquired | -587679000 | 587679000 | -111543000 | 111543000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest payments | -31250000 | 31250000 | -17196000 | 17196000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income tax payments | -91151000 | 91151000 | -92517000 | 92517000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001448893-26-000009 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:SeniorNotes | R3.htm | Senior notes due 2029, net | 495301000 | 495301000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common shares, outstanding (in shares) | 95456000 | 95456000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- cash_and_equivalents: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Cash' on us-gaap:Cash = 24606000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-16-011882 R2.htm prints 'Accounts receivable' on us-gaap:AccountsReceivableNet = 16637000 (FILING-CHECKED)
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
- ppe_net: era 10-K 0001448893-24-000015 R3.htm prints 'Property and equipment (at cost, less accumulated depreciation of $71,168 in 202' on us-gaap:PropertyPlantAndEquipmentNet = 41304000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001448893-18-000023 R8.htm prints 'Interest payments' on us-gaap:InterestPaid = -4685000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
