# POWL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000080420-25-000152 (CIK 0000080420, filed 2025-11-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000080420-21-000045 (CIK 0000080420, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000080420.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues | 1104318000 | 1104318000 | 1012356000 | 1012356000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 779937000 | 779937000 | 739268000 | 739268000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 324381000 | 324381000 | 273088000 | 273088000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no total opex line and no gross profit / operating income pair to tie components; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 95401000 | 95401000 | 84888000 | 84888000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development expenses | 11008000 | 11008000 | 9427000 | 9427000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 217860000 | 217860000 | 178773000 | 178773000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income, net | -15690000 | 15690000 | -17315000 | 17315000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 233550000 | 233550000 | 196088000 | 196088000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | 52803000 | 52803000 | 46240000 | 46240000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 180747000 | 180747000 | 149848000 | 149848000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 14.98 | 14.98 | 12.51 | 12.51 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 14.86 | 14.86 | 12.29 | 12.29 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 12062000 | 12062000 | 11982000 | 11982000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 12167000 | 12167000 | 12188000 | 12188000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 450739000 | 450739000 | 315331000 | 315331000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, less allowance for credit losses of $368 and $414, respectively | 217065000 | 217065000 | 214405000 | 214405000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 84719000 | 84719000 | 85873000 | 85873000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total Current Assets | 931716000 | 931716000 | 776481000 | 776481000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 111049000 | 111049000 | 103421000 | 103421000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 6125000 | 6125000 | 1003000 | 1003000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 1108984000 | 1108984000 | 928180000 | 928180000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 67080000 | 67080000 | 73633000 | 73633000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total Current Liabilities | 446387000 | 446387000 | 428015000 | 428015000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 468214000 | 468214000 | 445107000 | 445107000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Stockholders’ Equity | 640770000 | 640770000 | 483073000 | 483073000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 167937000 | 167937000 | 108661000 | 108661000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -8342000 | -8342000 | -21874000 | -21874000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -25117000 | -25117000 | -19252000 | -19252000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment | -13149000 | 13149000 | -11983000 | 11983000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 7265000 | 7265000 | 6871000 | 6871000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 4635000 | 4635000 | 4747000 | 4747000 | Y | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -12869000 | 12869000 | -12653000 | 12653000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: no standard debt line on the BS face; not hand-verified |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 12070178 | 12070178 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-09-30; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0000080420-21-000045 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 204000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
