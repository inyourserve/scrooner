# MAR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001048286-26-000007 (CIK 0001048286, filed 2026-02-10): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, CF R6.htm, BSP R7.htm
- 10-K 0001628280-16-011346 (CIK 0001048286, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, CF R5.htm
- 10-K 0001628280-24-004372 (CIK 0001048286, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, CF R6.htm, BSP R7.htm
- 10-K 0001628280-25-004818 (CIK 0001048286, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, CF R6.htm, BSP R7.htm
- companyfacts CIK0001048286.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenue | 26186000000 | 26186000000 | 25100000000 | 25100000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Operating costs | 1461000000 |  | 1329000000 |  | API missing | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (749 tags across all 77 R pages, face and notes) of 0001048286-26-000007; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Costs and expenses | 22045000000 | 22045000000 | 21333000000 | 21333000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 870000000 | 870000000 | 945000000 | 945000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (749 tags across all 77 R pages, face and notes) of 0001048286-26-000007; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | OPERATING INCOME | 4141000000 | 4141000000 | 3767000000 | 3767000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -809000000 | 809000000 | -695000000 | 695000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME BEFORE INCOME TAXES | 3394000000 | 3394000000 | 3151000000 | 3151000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | -793000000 | 793000000 | -776000000 | 776000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME | 2601000000 | 2601000000 | 2375000000 | 2375000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings per share - basic (in USD per share) | 9.53 | 9.53 | 8.36 | 8.36 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings per share - diluted (in USD per share) | 9.51 | 9.51 | 8.33 | 8.33 | Y | FILING-CHECKED | accn 0001048286-26-000007 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R44.htm | EARNINGS PER SHARE (Details) |  | 272900000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R44.htm 'EARNINGS PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R44.htm | EARNINGS PER SHARE (Details) |  | 273600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R44.htm 'EARNINGS PER SHARE (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and equivalents | 358000000 | 358000000 | 396000000 | 396000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (749 tags across all 77 R pages, face and notes) of 0001048286-26-000007; no face row matched |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (749 tags across all 77 R pages, face and notes) of 0001048286-26-000007; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 3584000000 | 3584000000 | 3485000000 | 3485000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 1954000000 | 1954000000 | 1833000000 | 1833000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 8907000000 | 8907000000 | 8731000000 | 8731000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 27540000000 | 27540000000 | 26182000000 | 26182000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R5.htm | Accounts payable | 814000000 | 814000000 | 763000000 | 763000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 8398000000 | 8398000000 | 8649000000 | 8649000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (749 tags across all 77 R pages, face and notes) of 0001048286-26-000007; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Stockholders’ deficit | -3771000000 | -3771000000 | -2992000000 | -2992000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 3212000000 | 3212000000 | 2749000000 | 2749000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -948000000 | -948000000 | -734000000 | -734000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash used in financing activities | -2318000000 | -2318000000 | -1956000000 | -1956000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R6.htm | Capital and technology expenditures | -604000000 | 604000000 | -750000000 | 750000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | mar:DepreciationAmortizationAndOther | R6.htm | Depreciation, amortization, and other (including depreciation and amortization classified in reimbursed expenses) | 599000000 |  | 492000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock-based compensation | 236000000 | 236000000 | 237000000 | 237000000 | Y | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Dividends paid | -718000000 | 718000000 | -682000000 | 682000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Purchase of treasury stock | -3300000000 | 3300000000 | -3762000000 | 3762000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048286-26-000007 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R64.htm | LONG-TERM DEBT - Additional Information (Details) |  | 698000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'LONG-TERM DEBT - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R51.htm | INCOME TAXES - Additional Information (Details) |  | 1070000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R51.htm 'INCOME TAXES - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt + Long-term debt | 16204000000 | 16204000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R8.htm | CONSOLIDATED STATEMENTS OF STOCKHOLDERS’ DEFICIT |  | 265864771 |  |  |  | FILING-CHECKED | not on the face statement; shown in R8.htm 'CONSOLIDATED STATEMENTS OF STOCKHOLDERS’ DEFICIT' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-16-011346 R2.htm prints 'Total revenue' on us-gaap:Revenues = 14486000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001628280-16-011346 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001628280-16-011346 R2.htm prints 'Costs and Expenses, Total' on us-gaap:CostsAndExpenses = 13136000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-16-011346 R2.htm prints 'General, administrative, and other' on us-gaap:GeneralAndAdministrativeExpense = 634000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-16-011346 R2.htm prints 'OPERATING INCOME' on us-gaap:OperatingIncomeLoss = 1350000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001628280-16-011346 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -167000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001628280-16-011346 R2.htm prints 'INCOME BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1255000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-16-011346 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -396000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-16-011346 R2.htm prints 'NET INCOME' on us-gaap:NetIncomeLoss = 859000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-16-011346 R2.htm prints 'Earnings per share - basic (in USD per share)' on us-gaap:EarningsPerShareBasic = 3.22 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-16-011346 R2.htm prints 'Earnings per share - diluted (in USD per share)' on us-gaap:EarningsPerShareDiluted = 3.15 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-16-011346 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001628280-16-011346 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Cash and equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 96000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Assets, current, total' on us-gaap:AssetsCurrent = 1384000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1029000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 943000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Total assets' on us-gaap:Assets = 6082000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableTradeCurrent = 593000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Liabilities, current, total' on us-gaap:LiabilitiesCurrent = 3233000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-011346 R4.htm prints 'Stockholders' deficit' on us-gaap:StockholdersEquity = -3590000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1430000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 367000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -1805000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -305000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Depreciation, amortization, and other' on mar:DepreciationDepletionAmortizationAndOther = 139000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 113000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -253000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001628280-16-011346 R5.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1917000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001628280-16-011346 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-011346 R5.htm read; no row matched (auto)
- interest_expense: era 10-K 0001628280-24-004372 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -565000000 (FILING-CHECKED)
- capex: era 10-K 0001628280-25-004818 R6.htm prints 'Capital and technology expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -750000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfRevenue)
- depreciation_and_amortization: API missing (mar:DepreciationAmortizationAndOther)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: combined us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: agree: 'Costs and expenses' includes reimbursed costs and owned/leased direct costs: combined
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R44.htm): 2026-11-12 R44.htm: agree: value in the note is the full data point; agree
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R44.htm): 2026-11-12 R44.htm: agree: value in the note is the full data point; agree
- accounts_receivable: mapped us-gaap:AccountsNotesAndLoansReceivableNetCurrent (R5.htm): 2026-11-12 R5.htm: corrected: the single BS receivables line (wider tag allowed when it is the only receivables line, as TT)
- inventory: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R64.htm): 2026-11-12 R64.htm: agree: value in the note is the full data point; agree
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R51.htm): 2026-11-12 R51.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: agree: R5 1,209 + 14,995
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'INCOME BEFORE INCOME TAXES' is the income_before_tax line, printed 3394000000 = filing XBRL 3394000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Stockholders’ deficit' is the stockholders_equity line, printed -3771000000 = filing XBRL -3771000000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: CF R6.htm 'Net cash used in investing activities' is the cash_flow_investing line, printed -948000000 = filing XBRL -948000000; agrees
- capex: mapped us-gaap:PaymentsToAcquireProductiveAssets (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: CF R6.htm 'Capital and technology expenditures' is the capex line, printed -604000000 = filing XBRL 604000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: CF R6.htm 'Purchase of treasury stock' is the share_buybacks line, printed -3300000000 = filing XBRL 3300000000; agrees
