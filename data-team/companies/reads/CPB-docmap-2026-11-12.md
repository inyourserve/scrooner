# CPB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000016732-26-000026 (CIK 0000016732, filed 2026-09-24): COVER R1.htm, IS R4.htm, CI R5.htm, BS R6.htm, CF R7.htm
- 10-K 0000016732-15-000034 (CIK 0000016732, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, CF R5.htm
- 10-K 0000016732-18-000062 (CIK 0000016732, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, CF R5.htm
- 10-K 0000016732-21-000103 (CIK 0000016732, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, CF R5.htm
- companyfacts CIK0000016732.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Net sales | 9744000000 | 9744000000 | 10253000000 | 10253000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of products sold | 7002000000 | 7002000000 | 7134000000 | 7134000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total costs and expenses | 8892000000 | 8892000000 | 9129000000 | 9129000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | Administrative expenses | 646000000 | 646000000 | 674000000 | 674000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost | R4.htm | Research and development expenses | 99000000 | 99000000 | 100000000 | 100000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Earnings before interest and taxes | 852000000 | 852000000 | 1124000000 | 1124000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | 331000000 | 331000000 | 345000000 | 345000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Earnings before taxes | 529000000 | 529000000 | 796000000 | 796000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Taxes on earnings | 124000000 | 124000000 | 194000000 | 194000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net earnings attributable to The Campbell's Company | 403000000 | 403000000 | 602000000 | 602000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net earnings attributable to The Campbell's Company common shareholders - Basic | 1.34 | 1.34 | 2.02 | 2.02 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net earnings attributable to The Campbell's Company common shareholders - Diluted | 1.31 | 1.31 | 2.01 | 2.01 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average shares outstanding - basic | 298000000 | 298000000 | 298000000 | 298000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average shares outstanding - assuming dilution | 300000000 | 300000000 | 300000000 | 300000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R4.htm period ..2026-08-02 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 394000000 | 394000000 | 132000000 | 132000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R6.htm | Accounts receivable, net | 578000000 | 578000000 | 583000000 | 583000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 1612000000 | 1612000000 | 1424000000 | 1424000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 2720000000 | 2720000000 | 2232000000 | 2232000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Plant assets, net of depreciation | 2868000000 | 2868000000 | 2767000000 | 2767000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 5321000000 | 5321000000 | 4991000000 | 4991000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 15648000000 | 15648000000 | 14896000000 | 14896000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 1377000000 | 1377000000 | 1332000000 | 1332000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 3336000000 | 3336000000 | 2906000000 | 2906000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 11492000000 | 11492000000 | 10992000000 | 10992000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total The Campbell Company's shareholders' equity | 3850000000 | 3850000000 | 3902000000 | 3902000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R6.htm period ..2026-08-02 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1039000000 | 1039000000 | 1131000000 | 1131000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -357000000 | -357000000 | -187000000 | -187000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -419000000 | -419000000 | -919000000 | -919000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of plant assets | -361000000 | 361000000 | -426000000 | 426000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 413000000 | 413000000 | 434000000 | 434000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 56000000 | 56000000 | 57000000 | 57000000 | Y | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -470000000 | 470000000 | -459000000 | 459000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Treasury stock purchases | -26000000 | 26000000 | -62000000 | 62000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000016732-26-000026 R7.htm period ..2026-08-02 |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations+us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Short-term borrowings + Long-term debt + Short-term borrowings + Long-term debt | 7242000000 | 14274000000 |  |  | N | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 8082000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 5277000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 6987000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 593000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Research and development expenses' on us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost = 113000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Earnings before interest and taxes' on us-gaap:OperatingIncomeLoss = 1095000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 108000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Earnings before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 990000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Taxes on earnings' on us-gaap:IncomeTaxExpenseBenefit = 299000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Net earnings attributable to Campbell Soup Company' on us-gaap:NetIncomeLoss = 691000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Net earnings attributable to Campbell Soup Company' on us-gaap:EarningsPerShareBasic = 2.21 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Net earnings attributable to Campbell Soup Company' on us-gaap:EarningsPerShareDiluted = 2.21 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Weighted average shares outstanding - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 312000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000016732-15-000034 R2.htm prints 'Weighted average shares outstanding - assuming dilution' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 313000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 253000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 647000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 993000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2092000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Plant assets, net of depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 2347000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 2344000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Total assets' on us-gaap:Assets = 8089000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Payable to suppliers and others' on us-gaap:AccountsPayableCurrent = 544000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2806000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 6713000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000016732-15-000034 R4.htm prints 'Total Campbell Soup Company shareholders' equity' on us-gaap:StockholdersEquity = 1380000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1182000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -603000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -526000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Purchases of plant assets' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -380000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 303000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 57000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -394000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000016732-15-000034 R5.htm prints 'Treasury stock purchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -244000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000016732-18-000062 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 5869000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000016732-21-000103 R2.htm prints 'Earnings before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1336000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- total_debt: N (us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations+us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations)
