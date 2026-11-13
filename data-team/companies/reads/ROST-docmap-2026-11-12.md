# ROST document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000745732-26-000006 (CIK 0000745732, filed 2026-03-31): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000745732-16-000037 (CIK 0000745732, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000745732-18-000004 (CIK 0000745732, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000745732-21-000017 (CIK 0000745732, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000745732.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Sales | 22750559000 | 22750559000 | 21129219000 | 21129219000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods sold | 16447256000 | 16447256000 | 15260506000 | 15260506000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (647 tags across all 67 R pages, face and notes) of 0000745732-26-000006; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (647 tags across all 67 R pages, face and notes) of 0000745732-26-000006; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 3595946000 | 3595946000 | 3283127000 | 3283127000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (647 tags across all 67 R pages, face and notes) of 0000745732-26-000006; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 2707357000 | 2707357000 | 2585586000 | 2585586000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (647 tags across all 67 R pages, face and notes) of 0000745732-26-000006; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before taxes | 2842157000 | 2842157000 | 2757154000 | 2757154000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for taxes on earnings | 697113000 | 697113000 | 666424000 | 666424000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 2145044000 | 2145044000 | 2090730000 | 2090730000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 6.66 | 6.66 | 6.36 | 6.36 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 6.61 | 6.61 | 6.32 | 6.32 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 322220000 | 322220000 | 328593000 | 328593000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 324416000 | 324416000 | 330984000 | 330984000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R3.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 4594392000 | 4594392000 | 4730744000 | 4730744000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Accounts receivable | 181301000 | 181301000 | 144482000 | 144482000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Merchandise inventory | 2630970000 | 2630970000 | 2444513000 | 2444513000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 7640097000 | 7640097000 | 7538696000 | 7538696000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 4088760000 | 4088760000 | 3792403000 | 3792403000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| goodwill | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (647 tags across all 67 R pages, face and notes) of 0000745732-26-000006; no face row matched |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 15548737000 | 15548737000 | 14905332000 | 14905332000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2386418000 | 2386418000 | 2126317000 | 2126317000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 4827180000 | 4827180000 | 4661825000 | 4661825000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (647 tags across all 67 R pages, face and notes) of 0000745732-26-000006; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 6187443000 | 6187443000 | 5509195000 | 5509195000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R5.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 3026883000 | 3026883000 | 2356988000 | 2356988000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -819275000 | -819275000 | -637462000 | -637462000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -2342097000 | -2342097000 | -1858505000 | -1858505000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Additions to property and equipment | -819275000 | 819275000 | -720104000 | 720104000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 509391000 | 509391000 | 446788000 | 446788000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 175354000 | 175354000 | 156298000 | 156298000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -528085000 | 528085000 | -488721000 | 488721000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common stock | -1050021000 | 1050021000 | -1049979000 | 1049979000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 55778000 | 55778000 | 80316000 | 80316000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid, net | 605565000 | 605565000 | 703079000 | 703079000 | Y | FILING-CHECKED | accn 0000745732-26-000006 R9.htm period ..2026-01-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Long-term debt | 1517606000 | 1517606000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 322333000 | 322333000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-01-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Sales' on us-gaap:SalesRevenueNet = 11939999000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 8576873000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 1738755000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000745732-16-000037 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Earnings before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1611759000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Provision for taxes on earnings' on us-gaap:IncomeTaxExpenseBenefit = 591098000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 1020661000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.53 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.51 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 403034000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000745732-16-000037 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 406405000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 761602000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Accounts receivable' on us-gaap:ReceivablesNetCurrent = 73627000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Merchandise inventory' on us-gaap:InventoryNet = 1419104000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2372195000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2342906000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Total assets' on us-gaap:Assets = 4869119000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 945559000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1602847000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000745732-16-000037 R4.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 2471991000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1326252000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -362509000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -898749000 (FILING-CHECKED)
- capex: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -366960000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 274828000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 70937000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -192312000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -700000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 18035000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000745732-16-000037 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 523597000 (FILING-CHECKED)
- revenue: era 10-K 0000745732-18-000004 R2.htm prints 'Sales' on us-gaap:SalesRevenueNet = 14134732000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000745732-18-000004 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 10042638000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000745732-21-000017 R2.htm prints 'Earnings before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 106297000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: corrected: the only face line between cost of goods sold and OI: 22,750,559 - 16,447,256 - 2,707,357 = 3,595,946 (thousands)
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- interest_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed; R3 prints 'Interest income, net' only
- goodwill: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating income' is the operating_income line, printed 2707357000 = filing XBRL 2707357000; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Cash and cash equivalents' is the cash_and_equivalents line, printed 4594392000 = filing XBRL 4594392000; agrees
- total_assets: mapped us-gaap:Assets (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total assets' is the total_assets line, printed 15548737000 = filing XBRL 15548737000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current liabilities' is the current_liabilities line, printed 4827180000 = filing XBRL 4827180000; agrees
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash provided by operating activities' is the cfo line, printed 3026883000 = filing XBRL 3026883000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Dividends paid' is the dividends_paid line, printed -528085000 = filing XBRL 528085000; agrees
