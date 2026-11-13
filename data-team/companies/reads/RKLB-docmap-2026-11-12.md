# RKLB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001819994-26-000013 (CIK 0001819994, filed 2026-02-26): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001628280-25-008724 (CIK 0001819994, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0000950170-23-006499 (CIK 0001819994, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001819994.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 601799000 | 601799000 | 436214000 | 436214000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenues | 394618000 | 394618000 | 320065000 | 320065000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 207181000 | 207181000 | 116149000 | 116149000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 436019000 | 436019000 | 305950000 | 305950000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 165303000 | 165303000 | 131556000 | 131556000 | Y | FILING-CHECKED | accn 0001819994-26-000013 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development, net | 270716000 | 270716000 | 174394000 | 174394000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating loss | -228838000 | -228838000 | -189801000 | -189801000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -26489000 | 26489000 | -26179000 | 26179000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -225897000 | -225897000 | -189411000 | -189411000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Benefit (provision) for income taxes | 27688000 | -27688000 | -764000 | 764000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -198209000 | -198209000 | -190175000 | -190175000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | -0.37 | -0.37 | -0.38 | -0.38 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | -0.37 | -0.37 | -0.38 | -0.38 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 530664781 | 530664781 | 495929861 | 495929861 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 530664781 | 530664781 | 495929861 | 495929861 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 828660000 | 828660000 | 271042000 | 271042000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 39001000 | 39001000 | 36440000 | 36440000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 158407000 | 158407000 | 119074000 | 119074000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1365544000 | 1365544000 | 692621000 | 692621000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 319473000 | 319473000 | 194838000 | 194838000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 205750000 | 205750000 | 71020000 | 71020000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2324478000 | 2324478000 | 1184342000 | 1184342000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Trade payables | 72699000 | 72699000 | 53059000 | 53059000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 334476000 | 334476000 | 339525000 | 339525000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 602624000 | 602624000 | 801889000 | 801889000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 1721854000 | 1721854000 | 382453000 | 382453000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash used in operating activities | -165521000 | -165521000 | -48890000 | -48890000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash (used in) provided by investing activities | -347397000 | -347397000 | -98327000 | -98327000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by financing activities | 1071271000 | 1071271000 | 256682000 | 256682000 | Y | FILING-CHECKED | accn 0001819994-26-000013 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property, equipment and software | -156285000 | 156285000 | -67093000 | 67093000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001819994-26-000013 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 43935000 | 43935000 | 33655000 | 33655000 | Y | FILING-CHECKED | accn 0001819994-26-000013 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 71099000 | 71099000 | 56816000 | 56816000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1051 tags across all 110 R pages, face and notes) of 0001819994-26-000013; no face row matched / check: hand R7.htm agree |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1051 tags across all 110 R pages, face and notes) of 0001819994-26-000013; no face row matched / check: hand R7.htm agree |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 24548000 | 24548000 | 16287000 | 16287000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes | 854000 | 854000 | 269000 | 269000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001819994-26-000013 R7.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebt+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent | R3.htm | Current installments of long-term borrowings + Convertible senior notes, net + Long-term borrowings, net, excluding curr | 169081000 |  | 416724000 |  |  | FILING-CHECKED | BS debt lines 0 + 152,395 + 1,716 plus non-current finance lease liabilities 14,653 (BS face) and current finance lease liabilities 317 (note R88) / check: hand R3.htm corrected: Face debt: current installments 0 / 12,045 + Convertible senior notes 152,395 / 345,392 + Long-term borrowings 1,716 / 44,049 = 154,111 / 401,486; plus finance leases: non-current 14,653 / 14,970 on the face and current 317 / 268 from note R88 (in other current liabilities); total 169,081 / 416,724. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, share outstanding (in shares) | 543574552 | 543574552 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001628280-25-008724 R5.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -3954000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000950170-23-006499 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 242515000 (FILING-CHECKED)
- sbc: era 10-K 0000950170-23-006499 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 55649000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 1.
- Random mapped sample: 4 rows, 0 disagreements (0.0%).
