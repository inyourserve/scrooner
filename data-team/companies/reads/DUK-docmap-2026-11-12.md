# DUK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001326160-26-000014 (CIK 0001326160, filed 2026-02-26): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001326160-16-000221 (CIK 0001326160, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001326160-17-000016 (CIK 0001326160, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001326160-23-000073 (CIK 0001326160, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0001326160.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RegulatedAndUnregulatedOperatingRevenue | R3.htm | Total operating revenues | 32237000000 | 32237000000 | 30357000000 | 30357000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 8058000000 |  | 9206000000 |  | API missing | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1839 tags across all 209 R pages, face and notes) of 0001326160-26-000014; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 23656000000 | 23656000000 | 22457000000 | 22457000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1839 tags across all 209 R pages, face and notes) of 0001326160-26-000014; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1839 tags across all 209 R pages, face and notes) of 0001326160-26-000014; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 8626000000 | 8626000000 | 7926000000 | 7926000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest Expense | 3634000000 | 3634000000 | 3384000000 | 3384000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income From Continuing Operations Before Income Taxes | 5712000000 | 5712000000 | 5194000000 | 5194000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Tax Expense From Continuing Operations | 642000000 | 642000000 | 590000000 | 590000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income | 4968000000 | 4968000000 | 4524000000 | 4524000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (usd per share) | 6.31 | 6.31 | 5.71 | 5.71 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (usd per share) | 6.31 | 6.31 | 5.71 | 5.71 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 777000000 | 777000000 | 772000000 | 772000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 777000000 | 777000000 | 772000000 | 772000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 245000000 | 245000000 | 314000000 | 314000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Receivables (net of allowance for doubtful accounts) | 16000000 | 16000000 | 1889000000 | 1889000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:PublicUtilitiesInventory | R6.htm | Inventory (includes $669 at 2025 and $494 at 2024 related to VIEs) | 4569000000 | 4569000000 | 4496000000 | 4496000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 11613000000 | 11613000000 | 12950000000 | 12950000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PublicUtilitiesPropertyPlantAndEquipmentNet | R6.htm | Net property, plant and equipment | 129959000000 | 129959000000 | 121626000000 | 121626000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 19010000000 | 19010000000 | 19010000000 | 19010000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total Assets | 195736000000 | 195736000000 | 186343000000 | 186343000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 5223000000 | 5223000000 | 5436000000 | 5436000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 21047000000 | 21047000000 | 19357000000 | 19357000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1839 tags across all 209 R pages, face and notes) of 0001326160-26-000014; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Duke Energy Corporation stockholders' equity | 51842000000 | 51842000000 | 50127000000 | 50127000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 12330000000 | 12330000000 | 12328000000 | 12328000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -14338000000 | -14338000000 | -13123000000 | -13123000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 1950000000 | 1950000000 | 859000000 | 859000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -14024000000 | 14024000000 | -12280000000 | 12280000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation, amortization and accretion (including amortization of nuclear fuel) | 7704000000 | 7704000000 | 6419000000 | 6419000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R187.htm | Stock-Based Compensation (Schedule of Stock-Based Compensation Expense) (Details) |  | 102000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R187.htm 'Stock-Based Compensation (Schedule of Stock-Based Compensation Expense) (Details' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfOrdinaryDividends | R8.htm | Dividends paid | -3300000000 | 3300000000 | -3213000000 | 3213000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1839 tags across all 209 R pages, face and notes) of 0001326160-26-000014; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest, net of amount capitalized | 3590000000 | 3590000000 | 3284000000 | 3284000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash (received from) paid for income taxes, net (includes transferable tax credit sale proceeds) | -625000000 | -625000000 | -400000000 | -400000000 | Y | FILING-CHECKED | accn 0001326160-26-000014 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Notes payable and commercial paper + Current maturities of long-term debt + Long-Term Debt (includes amounts related to  | 93262000000 | 177048000000 |  |  | N | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 778000000 | 778000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Total operating revenues' on us-gaap:SalesRevenueNet = 23459000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001326160-16-000221 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 18127000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Operating Income (Loss)' on us-gaap:OperatingIncomeLoss = 5367000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Interest Expense' on us-gaap:InterestExpense = 1613000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Income (Loss) From Continuing Operations Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4137000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Income Tax Expense (Benefit) from Continuing Operations' on us-gaap:IncomeTaxExpenseBenefit = 1326000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Net Income (Loss) Attributable to Parent' on us-gaap:NetIncomeLoss = 2816000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 4.05 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 4.05 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 694000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001326160-16-000221 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 694000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 857000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Receivables (net of allowance for doubtful accounts)' on us-gaap:ReceivablesNetCurrent = 703000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Inventory' on us-gaap:PublicUtilitiesInventory = 3810000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 8322000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 75709000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 16343000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Total Assets' on us-gaap:Assets = 121156000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 2400000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 11400000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001326160-16-000221 R5.htm prints 'Total Common Shareholders' Equity' on us-gaap:StockholdersEquity = 39727000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 6676000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -5277000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2578000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -6766000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Depreciation, amortization and accretion (including amortization of nuclear fuel' on us-gaap:DepreciationDepletionAndAmortization = 3613000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001326160-16-000221 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -2254000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Cash paid for interest, net of amount capitalized' on us-gaap:InterestPaidNet = 1607000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001326160-16-000221 R7.htm prints 'Cash paid for (received from) income taxes' on us-gaap:IncomeTaxesPaidNet = 170000000 (FILING-CHECKED)
- accounts_receivable: era 10-K 0001326160-17-000016 R5.htm prints 'Receivables (net of allowance for doubtful accounts)' on us-gaap:ReceivablesNetCurrent = 751000000 (FILING-CHECKED)
- ppe_net: era 10-K 0001326160-17-000016 R5.htm prints 'Net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 82520000000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001326160-23-000073 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -3179000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- total_debt: N (us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: combined us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: agree: total includes fuel and purchased power: combined
- sga_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R187.htm): 2026-11-12 R187.htm: agree: value in the note is the full data point; agree
- share_buybacks: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R6.htm): 2026-11-12 R6.htm: corrected: the tool (and my read) also added the VIE rows (118 + 3,308), which are already inside the face lines: double count; 2,624 + 7,104 + 80,108
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income Tax Expense From Continuing Operations' is the income_tax_expense line, printed 642000000 = filing XBRL 642000000; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net Income' is the net_income line, printed 4968000000 = filing XBRL 4968000000; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic (in shares)' is the weighted_basic_shares line, printed 777000000 = filing XBRL 777000000; agrees
- total_assets: mapped us-gaap:Assets (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total Assets' is the total_assets line, printed 195736000000 = filing XBRL 195736000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total Duke Energy Corporation stockholders' equity' is the stockholders_equity line, printed 51842000000 = filing XBRL 51842000000; agrees
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Cash (received from) paid for income taxes, net (i' is the cash_paid_for_income_taxes line, printed -625000000 = filing XBRL -625000000; agrees
- total_debt: finance-lease ruling (founder 2026-11-04 item 5, Dhairya 2026-11-12): R138 places finance leases inside 'Current maturities of long-term debt' and long-term debt; R139 'Total debt' 89,836 equals this sum, so no lease is added
