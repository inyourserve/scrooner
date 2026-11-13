# CTSH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001058290-26-000008 (CIK 0001058290, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001058290-16-000049 (CIK 0001058290, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001058290-18-000009 (CIK 0001058290, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001058290-24-000017 (CIK 0001058290, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001058290.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenues | 21108000000 | 21108000000 | 19736000000 | 19736000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R5.htm | Cost of revenues (exclusive of depreciation and amortization expense shown separately below) | 13991000000 | 13991000000 | 12958000000 | 12958000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001058290-26-000008 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (890 tags across all 99 R pages, face and notes) of 0001058290-26-000008; no face row matched / check: hand R5.htm agree |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringCharges+us-gaap:DepreciationAndAmortization+us-gaap:GainLossOnSaleOfPropertyPlantEquipment | R5.htm | SG&A + Restructuring charges + Depreciation and amortization expense + Gain on sale of property and equipment | 3728000000 |  | 3886000000 |  |  | FILING-CHECKED | every face line between cost of revenues and income from operations; gain on sale (62) reduces; ties exactly to revenue - cost of revenues - operating income both years / check: hand R5.htm corrected: Row pointed at R96 segment 'Less: unallocated costs' (96), not opex. No total opex line; face lines between cost of revenues and Income from operations: SG&A 3,240 + Restructuring 0 + D&A 550 + Gain on sale of property (62) = 3,728 = 21,108 - 13,991 - 3,389; FY1 3,223 + 134 + 529 = 3,886 = 19,736 - 12,958 - 2,892. |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 3240000000 | 3240000000 | 3223000000 | 3223000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (890 tags across all 99 R pages, face and notes) of 0001058290-26-000008; no face row matched / check: hand R5.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 3389000000 | 3389000000 | 2892000000 | 2892000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -37000000 | 37000000 | -54000000 | 54000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before provision for income taxes | 3479000000 | 3479000000 | 2938000000 | 2938000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | -1258000000 | 1258000000 | -713000000 | 713000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001058290-26-000008 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 2230000000 | 2230000000 | 2240000000 | 2240000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share | 4.57 | 4.57 | 4.52 | 4.52 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share | 4.56 | 4.56 | 4.51 | 4.51 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average number of common shares outstanding—Basic | 488000000 | 488000000 | 496000000 | 496000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average number of common shares outstanding—Diluted | 489000000 | 489000000 | 497000000 | 497000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1901000000 | 1901000000 | 2231000000 | 2231000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade accounts receivable, net | 4439000000 | 4439000000 | 4059000000 | 4059000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (890 tags across all 99 R pages, face and notes) of 0001058290-26-000008; no face row matched / check: hand R3.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 7818000000 | 7818000000 | 7504000000 | 7504000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 933000000 | 933000000 | 994000000 | 994000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 7106000000 | 7106000000 | 6953000000 | 6953000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 20692000000 | 20692000000 | 19966000000 | 19966000000 | Y | FILING-CHECKED | accn 0001058290-26-000008 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 308000000 | 308000000 | 340000000 | 340000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 3659000000 | 3659000000 | 3585000000 | 3585000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 5677000000 | 5677000000 | 5558000000 | 5558000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 15015000000 | 15015000000 | 14408000000 | 14408000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 2883000000 | 2883000000 | 2124000000 | 2124000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash (used in) investing activities | -230000000 | -230000000 | -1646000000 | -1646000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) financing activities | -2272000000 | -2272000000 | -915000000 | -915000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -288000000 | 288000000 | -297000000 | 297000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001058290-26-000008 R8.htm period ..2025-12-31 / check: hand R8.htm agree |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 550000000 | 550000000 | 542000000 | 542000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 181000000 | 181000000 | 175000000 | 175000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid | -610000000 | 610000000 | -600000000 | 600000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -1378000000 | 1378000000 | -605000000 | 605000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash interest paid during the year | 36000000 | 36000000 | 53000000 | 53000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income taxes during the year | 985000000 | 985000000 | 1120000000 | 1120000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001058290-26-000008 R8.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent | R3.htm | Short-term debt + Long-term debt | 598000000 |  | 931000000 |  |  | FILING-CHECKED | BS debt 33 + 543 plus finance lease liabilities 10 + 12 from note R61 (carried inside accrued expenses and other noncurrent liabilities) / check: hand R3.htm corrected: Face prints Short-term debt 33 / 33 and Long-term debt 543 / 875; lease note R61 prints finance lease liabilities current 10 / 8 (in accrued expenses) and noncurrent 12 / 15 (in other noncurrent liabilities); total 598 / 931. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Class A common stock, shares outstanding | 479000000 | 479000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Revenues' on us-gaap:SalesRevenueNet = 12416000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Cost of revenues (exclusive of depreciation and amortization expense shown separ' on us-gaap:CostOfServicesExcludingDepreciationDepletionAndAmortization = 7440200000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001058290-16-000049 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 2508600000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 2142000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -17700000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 2163600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 540000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 1623600000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 2.67 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted = 2.65 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Weighted average number of common shares outstanding—Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 609100000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001058290-16-000049 R4.htm prints 'Weighted average number of common shares outstanding—Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 613300000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2.125e+09 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Trade accounts receivable, net of allowances of $39.0 and $36.9, respectively' on us-gaap:AccountsReceivableNetCurrent = 2252600000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 7908600000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1271400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 2404700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Total assets' on us-gaap:Assets = 13065400000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 165300000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2713700000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 3787300000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001058290-16-000049 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 9278100000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2153300000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Net cash (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1370600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -648100000 (FILING-CHECKED)
- capex: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -272800000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 330000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 192000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001058290-16-000049 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -460000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Cash interest paid during the year' on us-gaap:InterestPaid = 14400000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001058290-16-000049 R7.htm prints 'Cash paid for income taxes during the year' on us-gaap:IncomeTaxesPaid = 578600000 (FILING-CHECKED)
- revenue: era 10-K 0001058290-18-000009 R4.htm prints 'Revenues' on us-gaap:SalesRevenueNet = 14810000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001058290-24-000017 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -41000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:OperatingExpenses)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 9 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
