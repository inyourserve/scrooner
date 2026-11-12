# ADBE document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000796343-26-000003 (CIK 0000796343, filed 2026-01-15): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0000796343-16-000224 (CIK 0000796343, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000796343-24-000006 (CIK 0000796343, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0000796343.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenue | 23769000000 | 23769000000 | 21505000000 | 21505000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 2551000000 | 2551000000 | 2358000000 | 2358000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 21218000000 | 21218000000 | 19147000000 | 19147000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 12512000000 | 12512000000 | 12406000000 | 12406000000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 1573000000 | 1573000000 | 1529000000 | 1529000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost | R5.htm | Research and development | 4294000000 | 4294000000 | 3944000000 | 3944000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 8706000000 | 8706000000 | 6741000000 | 6741000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -263000000 | 263000000 | -169000000 | 169000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 8734000000 | 8734000000 | 6931000000 | 6931000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 1604000000 | 1604000000 | 1371000000 | 1371000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 7130000000 | 7130000000 | 5560000000 | 5560000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in usd per share) | 16.73 | 16.73 | 12.43 | 12.43 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in usd per share) | 16.7 | 16.7 | 12.36 | 12.36 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Shares used to compute basic net income per share (in shares) | 426200000 | 426200000 | 447100000 | 447100000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Shares used to compute diluted net income per share (in shares) | 427000000 | 427000000 | 449700000 | 449700000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R5.htm period ..2025-11-28 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 5431000000 | 5431000000 | 7613000000 | 7613000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade receivables, net of allowances for doubtful accounts of $13 and of $14, respectively | 2344000000 | 2344000000 | 2072000000 | 2072000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (828 tags across all 93 R pages, face and notes) of 0000796343-26-000003; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 10163000000 | 10163000000 | 11232000000 | 11232000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1873000000 | 1873000000 | 1936000000 | 1936000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 12857000000 | 12857000000 | 12788000000 | 12788000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 29496000000 | 29496000000 | 30230000000 | 30230000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Trade payables | 417000000 | 417000000 | 361000000 | 361000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 10200000000 | 10200000000 | 10521000000 | 10521000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 17873000000 | 17873000000 | 16125000000 | 16125000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 11623000000 | 11623000000 | 14105000000 | 14105000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R3.htm period ..2025-11-28 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 10031000000 | 10031000000 | 8056000000 | 8056000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used for) investing activities | -1187000000 | -1187000000 | 149000000 | 149000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used for financing activities | -11060000000 | -11060000000 | -7724000000 | -7724000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -179000000 | 179000000 | -183000000 | 183000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation, amortization and accretion | 818000000 | 818000000 | 857000000 | 857000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 1942000000 | 1942000000 | 1833000000 | 1833000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (828 tags across all 93 R pages, face and notes) of 0000796343-26-000003; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -11281000000 | 11281000000 | -9500000000 | 9500000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 246000000 | 246000000 | 143000000 | 143000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes, net of refunds | 2219000000 | 2219000000 | 1727000000 | 1727000000 | Y | FILING-CHECKED | accn 0000796343-26-000003 R8.htm period ..2025-11-28 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebt | R3.htm | Debt + Debt | 6210000000 | 6210000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 413000000 | 413000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-11-28; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Total revenue' on us-gaap:Revenues = 4795511000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Total cost of revenue' on us-gaap:CostOfRevenue = 744317000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 4051194000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 3148099000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000796343-16-000224 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 531919000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost = 862730000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 903095000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -64184000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 873781000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 244230000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 629551000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Basic net income per share' on us-gaap:EarningsPerShareBasic = 1.26 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Diluted net income per share' on us-gaap:EarningsPerShareDiluted = 1.24 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Shares used to compute basic net income per share' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 498764000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000796343-16-000224 R4.htm prints 'Shares used to compute diluted net income per share' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 507164000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashEquivalentsAtCarryingValue = 876560000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Trade receivables, net of allowances for doubtful accounts of $7,293 and $7,867,' on us-gaap:AccountsReceivableNetCurrent = 672006000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4821892000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 787421000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 5366881000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Total assets' on us-gaap:Assets = 11726472000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Accounts Payable, Current' on us-gaap:AccountsPayableCurrent = 93307000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2213556000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 4724892000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000796343-16-000224 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 7001580000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1469502000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1488358000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Net cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -200687000 (FILING-CHECKED)
- capex: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -184936000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Depreciation, amortization and accretion' on us-gaap:DepreciationDepletionAndAmortization = 339473000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 335859000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -625000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaidNet = 56014000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000796343-16-000224 R7.htm prints 'Cash paid for income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 203010000 (FILING-CHECKED)
- interest_expense: era 10-K 0000796343-24-000006 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -113000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebt (R3.htm): 2026-11-12 R3.htm: agree: R3 'Debt' current 0 + 'Debt' non-current 6,210
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic net income per share (in usd per share)' is the basic_eps line, printed 16.73 = filing XBRL 16.73; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Shares used to compute basic net income per share ' is the weighted_basic_shares line, printed 426200000 = filing XBRL 426200000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current assets' is the current_assets line, printed 10163000000 = filing XBRL 10163000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Property and equipment, net' is the ppe_net line, printed 1873000000 = filing XBRL 1873000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Repurchases of common stock' is the share_buybacks line, printed -11281000000 = filing XBRL 11281000000; agrees
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Cash paid for income taxes, net of refunds' is the cash_paid_for_income_taxes line, printed 2219000000 = filing XBRL 2219000000; agrees
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: BSP R4.htm 'Common stock, shares outstanding (in shares)' is the shares_outstanding line, printed 413000000 = filing XBRL 413000000; agrees
