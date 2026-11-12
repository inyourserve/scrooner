# LEA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000842162-26-000011 (CIK 0000842162, filed 2026-02-13): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000842162-24-000008 (CIK 0000842162, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0000842162.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 23259100000 | 23259100000 | 23306000000 | 23306000000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 21754700000 | 21754700000 | 21666700000 | 21666700000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no total opex line and no gross profit / operating income pair to tie components; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 707600000 | 707600000 | 702500000 | 702500000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_income tag/label rules; not hand-verified |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense, net | 100800000 | 100800000 | 106200000 | 106200000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Consolidated income before provision for income taxes and equity in net income of affiliates | 625100000 | 625100000 | 732900000 | 732900000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 150000000 | 150000000 | 191100000 | 191100000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Lear | 436800000 | 436800000 | 506600000 | 506600000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share attributable to Lear (in dollars per share) | 8.22 | 8.22 | 9.02 | 9.02 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share attributable to Lear (in dollars per share) | 8.15 | 8.15 | 8.97 | 8.97 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Average common shares outstanding (in shares) | 53168252 | 53168252 | 56140962 | 56140962 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Average diluted shares outstanding (in shares) | 53590776 | 53590776 | 56476105 | 56476105 | Y | FILING-CHECKED | accn 0000842162-26-000011 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1033000000 | 1033000000 | 1.053e+09 | 1052900000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable | 3902800000 | 3902800000 | 3589300000 | 3589300000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 1693200000 | 1693200000 | 1601100000 | 1601100000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 7663000000 | 7663000000 | 7184100000 | 7184100000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 2913100000 | 2913100000 | 2833400000 | 2833400000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1777800000 | 1777800000 | 1699200000 | 1699200000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 14843100000 | 14843100000 | 14027500000 | 14027500000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable and drafts | 3416500000 | 3416500000 | 3250500000 | 3250500000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 5667100000 | 5667100000 | 5447000000 | 5447000000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Lear Corporation shareholders' equity | 5035100000 | 5035100000 | 4451700000 | 4451700000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1088800000 | 1088800000 | 1120100000 | 1120100000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -5.168e+08 | -516800000 | -543000000 | -543000000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -618500000 | -618500000 | -693900000 | -693900000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Additions to property, plant and equipment | -561600000 | 561600000 | -558700000 | 558700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 604100000 | 604100000 | 620700000 | 620700000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 66200000 | 66200000 | 6.44e+07 | 64400000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid to Lear Corporation shareholders | -164800000 | 164800000 | -173700000 | 173700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -325200000 | 325200000 | -416700000 | 416700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 114100000 | 114100000 | 115700000 | 115700000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash paid for income taxes, net of refunds received of $29.5 million in 2025, $24.1 million in 2024 and $15.7 million in | 276800000 | 276800000 | 267500000 | 267500000 | Y | FILING-CHECKED | accn 0000842162-26-000011 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Short-term borrowings + Current portion of long-term debt + Long-term debt | 2743100000 | 2743100000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0000842162-24-000008 R5.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 101100000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
