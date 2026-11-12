# RYN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000052827-26-000036 (CIK 0000052827, filed 2026-02-23): COVER R1.htm, IS R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm, CI R11.htm
- 10-K 0000052827-16-000059 (CIK 0000052827, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000052827-18-000009 (CIK 0000052827, era filing): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000052827-24-000014 (CIK 0000052827, era filing): COVER R1.htm, IS R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm, CI R11.htm
- companyfacts CIK0000052827.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | SALES (NOTE 4) | 484485000 | 484485000 | 987929000 | 987929000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | -327205000 | 327205000 | -547582000 | 547582000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Costs and Expenses | -401149000 | 401149000 | -623822000 | 623822000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling and general expenses | -66689000 | 66689000 | -74439000 | 74439000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | OPERATING INCOME | 83336000 | 83336000 | 364107000 | 364107000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense, net | -26351000 | 26351000 | -33756000 | 33756000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME FROM CONTINUING OPERATIONS BEFORE INCOME TAXES | 74594000 | 74594000 | 339838000 | 339838000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax (expense) benefit (Note 21) | -527000 | 527000 | 1022000 | -1022000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME ATTRIBUTABLE TO RAYONIER INC. | 474380000 | 474380000 | 359147000 | 359147000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net Income (in dollars per share) | 3.07 | 3.07 | 2.41 | 2.41 | Y | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net Income (in dollars per share) | 3.03 | 3.03 | 2.39 | 2.39 | Y | FILING-CHECKED | accn 0000052827-26-000036 R3.htm period ..2025-12-31 |
| weighted_basic_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_basic_shares tag/label rules; not hand-verified |
| weighted_diluted_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_diluted_shares tag/label rules; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 842944000 | 842944000 | 303065000 | 303065000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade receivables, less allowance for doubtful accounts of $209 and $401 | 9101000 | 9101000 | 8006000 | 8006000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventory (Note 16) | 6834000 | 6834000 | 30879000 | 30879000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 883755000 | 883755000 | 436893000 | 436893000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Total property, plant and equipment, net | 18528000 | 18528000 | 17432000 | 17432000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| goodwill | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 3404653000 | 3404653000 | 3474419000 | 3474419000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 12775000 | 12775000 | 16914000 | 16914000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 271281000 | 271281000 | 388710000 | 388710000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | TOTAL RAYONIER INC. SHAREHOLDERS’ EQUITY | 2209735000 | 2209735000 | 1769312000 | 1769312000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | CASH PROVIDED BY OPERATING ACTIVITIES | 256661000 | 256661000 | 261592000 | 261592000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | CASH PROVIDED BY INVESTING ACTIVITIES | 615054000 | 615054000 | 354013000 | 354013000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | CASH USED FOR FINANCING ACTIVITIES | -372866000 | -372866000 | -479360000 | -479360000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment | R9.htm | Capital expenditures | -50049000 |  | -62094000 |  | API missing | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | ryn:DepreciationDepletionAndAmortizationExcludingLargeDispositionsContinuingOperations | R9.htm | Depreciation, depletion and amortization from continuing operations | 106454000 |  | 113854000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based incentive compensation expense | 11004000 | 11004000 | 14232000 | 14232000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid on common shares | -292055000 | 292055000 | -200566000 | 200566000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common shares to pay withholding taxes on vested incentive stock awards | -2898000 | 2898000 | -4179000 | 4179000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes | 4054000 | 4054000 | 5877000 | 5877000 | Y | FILING-CHECKED | accn 0000052827-26-000036 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current maturities of long-term debt, net (Note 8) + LONG-TERM DEBT, NET (NOTE 8) | 1045317000 | 1045317000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common shares, shares outstanding (in shares) | 161425616 | 161425616 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000052827-16-000059 R2.htm prints 'SALES' on us-gaap:SalesRevenueNet = 544874000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 441099000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Costs and Expenses, Total' on us-gaap:CostsAndExpenses = 467090000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Selling and general expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 45750000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000052827-16-000059 R2.htm prints 'OPERATING INCOME BEFORE GAIN RELATED TO CONSOLIDATION OF NEW ZEALAND JOINT VENTU' on ryn:OperatingIncomeBeforeGainonConsolidationofEquityMethodInvestee = 77784000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -31699000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000052827-16-000059 R2.htm prints 'INCOME FROM CONTINUING OPERATIONS BEFORE INCOME TAXES' on ryn:IncomeLossFromContinuingOperationsBeforeIncomeTaxes = 43082000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Income tax benefit' on us-gaap:IncomeTaxExpenseBenefit = 859000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000052827-16-000059 R2.htm prints 'NET INCOME ATTRIBUTABLE TO RAYONIER INC.' on us-gaap:NetIncomeLoss = 46165000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Net Income (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.37 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000052827-16-000059 R2.htm prints 'Net income (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.37 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 51777000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Accounts receivable, less allowance for doubtful accounts of $42 and $42' on us-gaap:AccountsReceivableNetCurrent = 20222000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Inventory (Note 18)' on us-gaap:InventoryNet = 15351000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 105685000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Total property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 6742000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000052827-16-000059 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 2319263000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 21479000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000052827-16-000059 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 59457000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000052827-16-000059 R4.htm prints 'TOTAL RAYONIER INC. SHAREHOLDERS’ EQUITY' on us-gaap:StockholdersEquity = 1288084000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000052827-16-000059 R8.htm prints 'CASH PROVIDED BY OPERATING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 177164000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000052827-16-000059 R8.htm prints 'CASH USED FOR INVESTING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -166309000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000052827-16-000059 R8.htm prints 'CASH USED FOR FINANCING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -116463000 (FILING-CHECKED)
- capex: FY2015 10-K 0000052827-16-000059 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -57293000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000052827-16-000059 R8.htm prints 'Depreciation, depletion and amortization' on us-gaap:DepreciationDepletionAndAmortization = 113708000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000052827-16-000059 R8.htm prints 'Stock-based incentive compensation expense' on us-gaap:ShareBasedCompensation = 4484000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000052827-16-000059 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -124936000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000052827-16-000059 R8.htm prints 'Proceeds from repurchase of common shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -100000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000052827-16-000059 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 277000 (FILING-CHECKED)
- revenue: era 10-K 0000052827-18-000009 R2.htm prints 'SALES' on us-gaap:SalesRevenueNet = 819596000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000052827-18-000009 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 568253000 (FILING-CHECKED)
- interest_expense: era 10-K 0000052827-24-000014 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -48342000 (FILING-CHECKED)

## Mismatches (printed vs API)
- capex: API missing (us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment)
- depreciation_and_amortization: API missing (ryn:DepreciationDepletionAndAmortizationExcludingLargeDispositionsContinuingOperations)
