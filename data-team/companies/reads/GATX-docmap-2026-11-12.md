# GATX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000040211-26-000018 (CIK 0000040211, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000040211-16-000064 (CIK 0000040211, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm
- 10-K 0000040211-25-000024 (CIK 0000040211, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000040211-17-000012 (CIK 0000040211, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm
- companyfacts CIK0000040211.json (one call); submissions CIK0000040211.json (SIC 4700).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R127.htm | Revenues | 1740400000 | 1740400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R127.htm 'Foreign Operations (Details)' (MetaLinks.json presentation) |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Lessor face (R6) lists maintenance, depreciation, operating lease and other operating expense separately with no cost-of-revenue line; the only subtotal is the segment-table 'Operating Costs and Expenses' $953.7M (R130/R / pages opened: R130, R33, R54, R68, R100, R102, R6 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Costs-and-expenses format; no gross profit or gross margin on face or segment pages. / pages opened: R33, R54, R129, R130 |
| operating_expenses | mapped | us-gaap:CostsAndExpenses | R6.htm | Total Expenses | 1206300000 |  |  |  |  | FILING-CHECKED | check: hand / Face (R6) prints Total Expenses $1,206.3M (maintenance, depreciation, lease, other operating, SG&A) for FY2025. / pages opened: R6, R130, R13, R14, R33, R40 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R6.htm | Selling, general and administrative | 252600000 | 252600000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R6.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation) |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No pages listed; consolidated income statement (R6) has no R&D line for this railcar lessor. / pages opened: R6 |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Face goes from Total Expenses to other income/expense and pre-tax income with no operating income subtotal; segment profit (after interest) is not operating income. / pages opened: R6, R58, R92, R93, R94, R129 |
| interest_expense | mapped | us-gaap:InterestExpense | R92.htm | Interest Expense, Operating and Nonoperating | -391500000 | 391500000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R92.htm 'Fair Value Disclosure Fair Value Disclosure - Amounts Recorded on Balance Sheet ' (MetaLinks.json presentation) |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R6.htm | Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | 279100000 | 279100000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R6.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation) |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R114.htm | Income tax benefit | 63100000 | 63100000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R114.htm 'Income Taxes (Details 2)' (MetaLinks.json presentation) |
| net_income | mapped | us-gaap:ProfitLoss | R5.htm | Net Income | 333300000 | 333300000 | 284200000 | 284200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R120.htm | Basic earnings per share (in dollars per share) | 9.14 | 9.14 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R120.htm | Diluted earnings per share (in dollars per share) | 9.12 | 9.12 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R120.htm | Denominator for basic earnings per share — weighted average shares | 35800000 | 35800000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R120.htm | Denominator for diluted earnings per share — adjusted weighted average and assumed conversion | 35900000 | 35900000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and Cash Equivalents | 743000000 | 743000000 | 401600000 | 401600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Receivables, net | 207200000 | 207200000 | 199100000 | 199100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:OtherInventory | R123.htm | Inventory | 84000000 |  |  |  |  | FILING-CHECKED | check: hand / Other assets note (components of other assets on the consolidated balance sheet) reports undimensioned Inventory $84.0M at 2025-12-31. / pages opened: R85, R87, R123 |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / GATX balance sheet is unclassified; the only current-assets figures are for equity-method investees (RRPF), which cannot be used. / pages opened: R78, R79, R87 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Net operating assets and facilities | 11410900000 | 11410900000 | 10449700000 | 10449700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 126300000 | 126300000 | 114100000 | 114100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 17999500000 | 17999500000 | 12296500000 | 12296500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts Payable and Accrued Expenses | 318400000 | 318400000 | 217100000 | 217100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Unclassified balance sheet; current liabilities appear only in investee summarized financial data. / pages opened: R78, R79 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 14364400000 | 14364400000 | 9857600000 | 9857600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Equity | 2750500000 | 2750500000 | 2438900000 | 2438900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 648100000 | 648100000 | 602100000 | 602100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1016800000 | -1016800000 | -1416700000 | -1416700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used in) provided by financing activities | 4944800000 | 4944800000 | 770500000 | 770500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| capex | combined | gmt:PaymentstoAcquireInvestmentsandPropertyPlantandEquipment | R7.htm | Portfolio investments and capital additions | 1316700000 |  |  |  |  | FILING-CHECKED | check: hand / Capex is printed only inside the broader cash-flow line 'Portfolio investments and capital additions' ($1,316.7M), which also includes portfolio investments. / pages opened: R7, R94 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 452300000 | 452300000 | 421400000 | 421400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R7.htm | Share-based compensation expense | 25000000 | 25000000 | 23000000 | 23000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends | -89800000 | 89800000 | -84800000 | 84800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Stock repurchases | -65000000 | 65000000 | -21900000 | 21900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest Paid, Excluding Capitalized Interest, Operating Activity | 413200000 | 413200000 | 350100000 | 350100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R117.htm | Total | 14500000 | 14500000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R117.htm 'Income Taxes - Income taxes Paid (Details)' (MetaLinks.json presentation) |
| total_debt | mapped | us-gaap:LongTermDebt | R85.htm | Total debt principal | -12505600000 | 12505600000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R85.htm 'Debt (Details)' (MetaLinks.json presentation) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Outstanding shares (in shares) | 35400021 | 35400021 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0000040211-16-000064 statement not identified (auto)
- sga_expense: 10-K 0000040211-16-000064 statement not identified (auto)
- interest_expense: 10-K 0000040211-16-000064 statement not identified (auto)
- income_before_tax: 10-K 0000040211-16-000064 statement not identified (auto)
- income_tax_expense: 10-K 0000040211-16-000064 statement not identified (auto)
- net_income: 10-K 0000040211-16-000064 statement not identified (auto)
- basic_eps: 10-K 0000040211-16-000064 statement not identified (auto)
- diluted_eps: 10-K 0000040211-16-000064 statement not identified (auto)
- weighted_basic_shares: 10-K 0000040211-16-000064 statement not identified (auto)
- weighted_diluted_shares: 10-K 0000040211-16-000064 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 202400000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Rent and other receivables' on us-gaap:AccountsReceivableGrossCurrent = 69400000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Operating assets and facilities, net' on us-gaap:PropertyPlantAndEquipmentNet = 5698400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 79700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Assets' on us-gaap:Assets = 6894200000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Accounts Payable and Accrued Expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 170900000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 5614000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Shareholders’ Equity' on us-gaap:StockholdersEquity = 1280200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 534300000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -307600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -229000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Share-based Compensation' on us-gaap:ShareBasedCompensation = 11600000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Dividends' on us-gaap:PaymentsOfDividends = -68200000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Stock repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -125400000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- net_income: 10-K 0000040211-25-000024 statement not identified (auto)
- cash_paid_for_interest: era 10-K 0000040211-17-000012 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences
