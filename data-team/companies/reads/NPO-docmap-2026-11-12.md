# NPO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001628280-26-009798 (CIK 0001164863, filed 2026-02-19): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0001164863-24-000015 (CIK 0001164863, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0001164863-25-000009 (CIK 0001164863, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- companyfacts CIK0001164863.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Net sales | 1143300000 | 1143300000 | 1048700000 | 1048700000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 655800000 | 655800000 | 603900000 | 603900000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 487500000 | 487500000 | 444800000 | 444800000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 325900000 | 325900000 | 302500000 | 302500000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 323400000 | 323400000 | 296300000 | 296300000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 161600000 | 161600000 | 142300000 | 142300000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -34000000 | 34000000 | -40900000 | 40900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 57600000 | 57600000 | 94400000 | 94400000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | -17100000 | 17100000 | -21500000 | 21500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 40500000 | 40500000 | 72900000 | 72900000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income per share (in dollars per share) | 1.92 | 1.92 | 3.48 | 3.48 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income per share (in dollars per share) | 1.91 | 1.91 | 3.45 | 3.45 | Y | FILING-CHECKED | accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| weighted_basic_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_basic_shares tag/label rules; not hand-verified |
| weighted_diluted_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_diluted_shares tag/label rules; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 114700000 | 114700000 | 236300000 | 236300000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndNotesReceivableNet | R6.htm | Accounts receivable, less allowance for doubtful accounts of $2.0 in 2025 and of $1.0 in 2024 | 134100000 | 134100000 | 115900000 | 115900000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 153800000 | 153800000 | 138800000 | 138800000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 437700000 | 437700000 | 5.123e+08 | 512300000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 221500000 | 221500000 | 193200000 | 193200000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1064800000 | 1064800000 | 896200000 | 896200000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 2663000000 | 2663000000 | 2491500000 | 2491500000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 71600000 | 71600000 | 66000000 | 66000000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 188700000 | 188700000 | 198000000 | 198000000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 1119100000 | 1119100000 | 1.063e+09 | 1062900000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total shareholders’ equity | 1543900000 | 1543900000 | 1428600000 | 1428600000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R5.htm | Net cash provided by operating activities of continuing operations | 201200000 | 201200000 | 162900000 | 162900000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used in investing activities of continuing operations | -316900000 | -316900000 | -241500000 | -241500000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash used in financing activities of continuing operations | -17400000 | -17400000 | -50500000 | -50500000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R5.htm | Purchases of property, plant and equipment | -42000000 | 42000000 | -29100000 | 29100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R5.htm | Depreciation | 24700000 | 24700000 | 23900000 | 23900000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Stock-based compensation | 13500000 | 13500000 | 12000000 | 12000000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R5.htm | Dividends paid | -26200000 | 26200000 | -25300000 | 25300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R5.htm | Interest | 33500000 | 33500000 | 38900000 | 38900000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R5.htm | Income taxes, net of refunds received | 41400000 | 41400000 | 36100000 | 36100000 | Y | FILING-CHECKED | accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current maturities of long-term debt + Long-term debt | 6.553e+08 | 655300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001164863-24-000015 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -45000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001164863-25-000009 R5.htm prints 'Net cash provided by (used in) investing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -241500000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
