# INGR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001628280-26-008603 (CIK 0001046257, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0001558370-18-000857 (CIK 0001046257, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0001046257.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 7219000000 | 7219000000 | 7430000000 | 7430000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 5391000000 | 5391000000 | 5639000000 | 5639000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1828000000 | 1828000000 | 1791000000 | 1791000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the sga_expense tag/label rules; not hand-verified |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 1016000000 | 1016000000 | 883000000 | 883000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 974000000 | 974000000 | 931000000 | 931000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 238000000 | 238000000 | 277000000 | 277000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Ingredion | 729000000 | 729000000 | 647000000 | 647000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 11.36 | 11.36 | 9.88 | 9.88 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 11.18 | 11.18 | 9.71 | 9.71 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 64200000 | 64200000 | 65500000 | 65500000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 65200000 | 65200000 | 6.66e+07 | 66600000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 1030000000 | 1030000000 | 997000000 | 997000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net | 1185000000 | 1185000000 | 1093000000 | 1093000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 1227000000 | 1227000000 | 1187000000 | 1187000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 3505000000 | 3505000000 | 3355000000 | 3355000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 2526000000 | 2526000000 | 2264000000 | 2264000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| goodwill | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 7897000000 | 7897000000 | 7444000000 | 7444000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 693000000 | 693000000 | 604000000 | 604000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1316000000 | 1316000000 | 1281000000 | 1281000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 3531000000 | 3531000000 | 3554000000 | 3554000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Ingredion stockholders’ equity | 4274000000 | 4274000000 | 3804000000 | 3804000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Cash provided by operating activities | 944000000 | 944000000 | 1436000000 | 1436000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Cash used for investing activities | -444000000 | -444000000 | -47000000 | -47000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Cash used for financing activities | -491000000 | -491000000 | -765000000 | -765000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures and mechanical stores purchases, net | -433000000 | 433000000 | -295000000 | 295000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 222000000 | 222000000 | 214000000 | 214000000 | Y | FILING-CHECKED | accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| sbc | mapped | ingr:ProceedsFromCommonStockUnderIncentiveAndShareBasedCompensationPlansNetOfSettlements | R9.htm | Common stock activity for share-based compensation, net | -12000000 |  | 46000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid, including to non-controlling interests | -211000000 | 211000000 | -210000000 | 210000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:ProceedsFromRepurchaseOfEquity | R9.htm | Repurchases of common stock, net | -224000000 | -224000000 | -216000000 | -216000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Short-term borrowings + Long-term debt | 1790000000 | 1790000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
- share_buybacks: era 10-K 0001558370-18-000857 R9.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -123000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- sbc: API missing (ingr:ProceedsFromCommonStockUnderIncentiveAndShareBasedCompensationPlansNetOfSettlements)
