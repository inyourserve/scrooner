# POOL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001193125-26-074833 (CIK 0000945841, filed 2026-02-26): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000945841.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R2.htm | Net sales | 5289396000 | 5289396000 | 5310953000 | 5310953000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R2.htm | Cost of sales | 3716938000 | 3716938000 | 3735606000 | 3735606000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross profit | 1572458000 | 1572458000 | 1575347000 | 1575347000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling and administrative expenses | 992254000 | 992254000 | 958143000 | 958143000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income | 580204000 | 580204000 | 617204000 | 617204000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R2.htm | Income before income taxes and equity in earnings | 533434000 | 533434000 | 566954000 | 566954000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 127132000 | 127132000 | 132836000 | 132836000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income | 406404000 | 406404000 | 434325000 | 434325000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic (in dollars per share) | 10.89 | 10.89 | 11.37 | 11.37 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted (in dollars per share) | 10.85 | 10.85 | 11.3 | 11.3 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic (in shares) | 37149000 | 37149000 | 38007000 | 38007000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted (in shares) | 37288000 | 37288000 | 38228000 | 38228000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash and cash equivalents | 104963000 | 104963000 | 77862000 | 77862000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net | 136063000 | 136063000 | 115835000 | 115835000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Product inventories, net | 1454672000 | 1454672000 | 1289300000 | 1289300000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1969864000 | 1969864000 | 1729114000 | 1729114000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 267065000 | 267065000 | 251324000 | 251324000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 707345000 | 707345000 | 698910000 | 698910000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 3626126000 | 3626126000 | 3368184000 | 3368184000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 652619000 | 652619000 | 525235000 | 525235000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 880285000 | 880285000 | 844186000 | 844186000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 2440897000 | 2440897000 | 2094719000 | 2094719000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity | 1185229000 | 1185229000 | 1273465000 | 1273465000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 365850000 | 365850000 | 659186000 | 659186000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -67792000 | -67792000 | -66169000 | -66169000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -273379000 | -273379000 | -576550000 | -576550000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment, net of sale proceeds | -56334000 | 56334000 | -59476000 | 59476000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation | 42678000 | 42678000 | 36784000 | 36784000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 22733000 | 22733000 | 19248000 | 19248000 | Y | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Payments of cash dividends | -184916000 | 184916000 | -179633000 | 179633000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock and payments of excise tax | -346286000 | 346286000 | -306300000 | 306300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-074833 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings and current portion of long-term debt + Long-term debt, net | 1199453000 | 1199453000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 36577686 | 36577686 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
none found in companyfacts

## Mismatches (printed vs API)
none beyond sign differences
