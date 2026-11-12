# MOS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001285785-26-000017 (CIK 0001285785, filed 2026-02-27): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001285785-26-000017 (CIK 0001285785, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001285785.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net sales to external customers | 12052400000 | 12052400000 | 11122800000 | 11122800000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of goods sold | 10150500000 | 10150500000 | 9610900000 | 9610900000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross margin | 1901900000 | 1901900000 | 1511900000 | 1511900000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GainLossOnSalesOfAssetsAndAssetImpairmentCharges+us-gaap:GoodwillImpairmentLoss+us-gaap:OtherOperatingIncomeExpenseNet | R2.htm | Selling, general and administrative expenses + Loss (gain) on assets sold and to be sold + Impairment of goodwill + Othe | 1080400000 | 187200000 | 890400000 | 103400000 | N (printed 1080400000 vs API 187200000) | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 533900000 | 533900000 | 496900000 | 496900000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating earnings | 821500000 | 821500000 | 621500000 | 621500000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNet | R2.htm | Interest expense, net | -187700000 | -187700000 | -182800000 | -182800000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R2.htm | Earnings from consolidated companies before income taxes | 1212900000 | 1212900000 | 315400000 | 315400000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 639800000 | 639800000 | 186700000 | 186700000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net earnings attributable to Mosaic | 540700000 | 540700000 | 174900000 | 174900000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic net earnings per share attributable to Mosaic | 1.7 | 1.7 | 0.55 | 0.55 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted net earnings per share attributable to Mosaic | 1.7 | 1.7 | 0.55 | 0.55 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic weighted average number of shares outstanding (in shares) | 317300000 | 317300000 | 319800000 | 319800000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted weighted average number of shares outstanding (in shares) | 318900000 | 318900000 | 320700000 | 320700000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 276600000 | 276600000 | 272800000 | 272800000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R4.htm | Receivables, net | 1078600000 | 1078600000 | 1113300000 | 1113300000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories | 3363000000 | 3363000000 | 2548400000 | 2548400000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 5237500000 | 5237500000 | 4498300000 | 4498300000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property, plant and equipment, net | 13982600000 | 13982600000 | 13352600000 | 13352600000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 1005100000 | 1005100000 | 1.061e+09 | 1061100000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 24480100000 | 24480100000 | 22924000000 | 22924000000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 1171900000 | 1171900000 | 1156500000 | 1156500000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 3982800000 | 3982800000 | 4171300000 | 4171300000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total Mosaic stockholders’ equity | 12084900000 | 12084900000 | 11482400000 | 11482400000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 824800000 | 824800000 | 1299200000 | 1299200000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -1309500000 | -1309500000 | -1261000000 | -1261000000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used in) financing activities | 452000000 | 452000000 | -131900000 | -131900000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Capital expenditures | -1359400000 | 1359400000 | -1251800000 | 1251800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation, depletion and amortization | 1.05e+09 | 1049900000 | 1025500000 | 1025500000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Share-based compensation expense | 30700000 | 30700000 | 31800000 | 31800000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Cash dividends paid | -280400000 | 280400000 | -270700000 | 270700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchases of stock | 0 | 0 | -235400000 | 235400000 | Y | FILING-CHECKED | accn 0001285785-26-000017 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R4.htm | Current maturities of long-term debt + Long-term debt, less current maturities | 4294000000 | 4294000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 317408647 | 317408647 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001285785-26-000017 R2.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNet = -187700000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: N (printed 1080400000 vs API 187200000) (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GainLossOnSalesOfAssetsAndAssetImpairmentCharges+us-gaap:GoodwillImpairmentLoss+us-gaap:OtherOperatingIncomeExpenseNet)
