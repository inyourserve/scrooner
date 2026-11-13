# MLM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-059193 (CIK 0000916076, filed 2026-02-19): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001193125-16-473754 (CIK 0000916076, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001193125-18-055887 (CIK 0000916076, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000916076.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Revenues | 6150000000 | 6150000000 | 5662000000 | 5662000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of revenues | 4261000000 | 4261000000 | 4026000000 | 4026000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross Profit | 1889000000 | 1889000000 | 1636000000 | 1636000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+mlm:BusinessCombinationAcquisitionDivestitureAndIntegrationRelatedCosts+us-gaap:OtherOperatingIncomeExpenseNet | R2.htm | Selling, general and administrative expenses + Acquisition, divestiture and integration expenses + Other operating incom | 452000000 |  | -843000000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001193125-26-059193 R2.htm period ..2025-12-31 / check: hand R2.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 443000000 | 443000000 | 429000000 | 429000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1191 tags across all 124 R pages, face and notes) of 0001193125-26-059193; no face row matched / check: hand R2.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Earnings from Operations | 1437000000 | 1437000000 | 2479000000 | 2479000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R2.htm | Interest expense | 230000000 | 230000000 | 169000000 | 169000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Earnings from continuing operations before income tax expense | 1226000000 | 1226000000 | 2366000000 | 2366000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income tax expense | 236000000 | 236000000 | 550000000 | 550000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net Earnings Attributable to Martin Marietta | 1137000000 | 1137000000 | 1995000000 | 1995000000 | Y | FILING-CHECKED | accn 0001193125-26-059193 R2.htm period ..2025-12-31 / check: hand R2.htm agree |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Total basic attributable to common shareholders | 18.81 | 18.81 | 32.5 | 32.5 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Total diluted attributable to common shareholders | 18.77 | 18.77 | 32.41 | 32.41 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic | 60500000 | 60500000 | 61400000 | 61400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted | 60600000 | 60600000 | 61600000 | 61600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 67000000 | 67000000 | 670000000 | 670000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 723000000 | 723000000 | 678000000 | 678000000 | Y | FILING-CHECKED | accn 0001193125-26-059193 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories, net | 1078000000 | 1078000000 | 1018000000 | 1018000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total Current Assets | 3193000000 | 3193000000 | 2449000000 | 2449000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 10290000000 | 10290000000 | 9660000000 | 9660000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 3614000000 | 3614000000 | 3393000000 | 3393000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 18711000000 | 18711000000 | 18170000000 | 18170000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 389000000 | 389000000 | 375000000 | 375000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total Current Liabilities | 895000000 | 895000000 | 1002000000 | 1002000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total Liabilities | 8677000000 | 8677000000 | 8714000000 | 8714000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Shareholders’ Equity | 10032000000 | 10032000000 | 9453000000 | 9453000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net Cash Provided by Operating Activities | 1785000000 | 1785000000 | 1459000000 | 1459000000 | Y | FILING-CHECKED | accn 0001193125-26-059193 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash (Used for) Provided by Investing Activities | -1588000000 | -1588000000 | -2444000000 | -2444000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net Cash (Used for) Provided by Financing Activities | -800000000 | -800000000 | 373000000 | 373000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Additions to property, plant and equipment | -807000000 | 807000000 | -855000000 | 855000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation, depletion and amortization | 637000000 | 637000000 | 573000000 | 573000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 46000000 | 46000000 | 58000000 | 58000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -197000000 | 197000000 | -189000000 | 189000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock | -450000000 | 450000000 | -450000000 | 450000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-059193 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R121.htm | Supplemental Cash Flow Information - Supplemental Disclosures of Cash Flow Information (Detail) | 229000000 | 229000000 | 158000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R121.htm 'Supplemental Cash Flow Information - Supplemental Disclosures of Cash Flow Infor' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R121.htm corrected: Note R121 prints 'Cash paid for interest, net of amount capitalized' InterestPaidNet 229 / 158; printed values were blank. |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R83.htm | Income Taxes - Summary of the Amounts of Income Taxes Paid (Refunded) by the Company (Detail) | 192000000 | 192000000 | 382000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R83.htm 'Income Taxes - Summary of the Amounts of Income Taxes Paid (Refunded) by the Com' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R83.htm corrected: Note R83 prints 'Income taxes paid, net of amounts refunded' IncomeTaxesPaidNet 192 / 382; printed values were blank. |
| total_debt | component_in_note | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiability | R5.htm | Current maturities of long-term debt + Long-term debt | 5625000000 |  | 5616000000 |  |  | FILING-CHECKED | BS debt 5,323 (R5) + finance lease liabilities 302 (R105, current 15 in other current liabilities, noncurrent 287 in other noncurrent liabilities); FY1 5,413 + 203 / check: hand R105.htm corrected: BS R5 debt lines 30 + 5,293 = 5,323 (FY1 125 + 5,288 = 5,413); finance lease liabilities 302 / 203 sit inside other current/noncurrent liabilities per lease note R105, so added: 5,625 / 5,616. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding | 60309739 | 60309739 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 3539570000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Total cost of revenues' on us-gaap:CostOfGoodsAndServicesSold = 2817803000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Gross Profit' on us-gaap:GrossProfit = 721767000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Selling, general and administrative expenses + Acquisition-related expenses, net' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:BusinessCombinationAcquisitionRelatedCosts+us-gaap:OtherOperating = 242351000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 218234000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Earnings from Operations' on us-gaap:OperatingIncomeLoss = 479416000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 76287000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Earnings from continuing operations before taxes on income' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 413801000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Taxes on income' on us-gaap:IncomeTaxExpenseBenefit = 124863000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Net Earnings Attributable to Martin Marietta' on us-gaap:NetIncomeLoss = 288792000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Earnings Per Share, Basic, Total' on us-gaap:EarningsPerShareBasic = 4.31 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Earnings Per Share, Diluted, Total' on us-gaap:EarningsPerShareDiluted = 4.29 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 66770000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-473754 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 67020000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 168409000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 410921000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Inventories, net' on us-gaap:InventoryNet = 469141000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 1082168000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 3156000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Goodwill' on us-gaap:Goodwill = 2068235000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Total Assets' on us-gaap:Assets = 6961732000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 164718000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 367191000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Total Liabilities' on us-gaap:Liabilities = 2901555000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-473754 R6.htm prints 'Total Shareholders’ Equity' on us-gaap:StockholdersEquity = 4057284000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 573151000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Net Cash Provided By (Used for) Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 88546000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Net Cash Used for Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -601939000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Additions to property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -318232000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Depreciation, depletion and amortization' on us-gaap:DepreciationDepletionAndAmortization = 263587000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 13589000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -107462000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -519962000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 71011000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-473754 R8.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 46774000 (FILING-CHECKED)
- revenue: era 10-K 0001193125-18-055887 R2.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 3965594000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001193125-18-055887 R7.htm read; no row matched (auto)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+mlm:BusinessCombinationAcquisitionDivestitureAndIntegrationRelatedCosts+us-gaap:OtherOperatingIncomeExpenseNet)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 8 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 3.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
