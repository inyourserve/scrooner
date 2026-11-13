# ADI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.

## Filings opened
- Latest 10-K 0000006281-25-000153 (CIK 0000006281, filed 2025-11-25, FY ended 2025-11-01, comparative 2024-11-02). R3 income statement, R4 comprehensive income, R5 CI parenthetical, R6 balance sheet, R7 BS parenthetical (shares outstanding), R8/R9 equity (R9 parenthetical: dividends per share), R10 cash flows; notes R40 supplemental cash flow, R71-R73 leases, R84-R85 income taxes (see CSV rows for the pages actually used).
- companyfacts CIK0000006281.json (one call).

FY0 = 2025-11-01; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R3.htm | Revenue | 11019707000 | 11019707000 | 9427157000 | 9427157000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | Cost of sales | 4246229000 | 4246229000 | 4045814000 | 4045814000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| gross_profit | mapped | GrossProfit | IS R3.htm | Gross margin | 6773478000 | 6773478000 | 5381343000 | 5381343000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| operating_expenses | mapped | OperatingExpenses | IS R3.htm | Total operating expenses | 3840982000 | 3840982000 | 3348545000 | 3348545000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, marketing, general and administrative | 1255339000 | 1255339000 | 1068640000 | 1068640000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R3.htm | Research and development | 1766001000 | 1766001000 | 1487863000 | 1487863000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 2932496000 | 2932496000 | 2032798000 | 2032798000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | 317716000 | 317716000 | 322227000 | 322227000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| interest_income | mapped | InvestmentIncomeInterest | IS R3.htm | Interest income | -105266000 | 105266000 | -78817000 | 78817000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R3.htm | Other, net | 7934000 | -7934000 | 12048000 | -12048000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Other, net' 7,934 is printed as an expense inside 'Total nonoperating expense (income)' (fact -7,934) | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Income before income taxes | 2712112000 | 2712112000 | 1777340000 | 1777340000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Provision for income taxes | 444770000 | 444770000 | 142067000 | 142067000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net income | 2267342000 | 2267342000 | 1635273000 | 1635273000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic earnings per common share (in dollars per share) | 4.59 | 4.59 | 3.3 | 3.3 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted earnings per common share (in dollars per share) | 4.56 | 4.56 | 3.28 | 3.28 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Shares used to compute earnings per common share — basic (in | 494381000 | 494381000 | 496166000 | 496166000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Shares used to compute earnings per common share — diluted ( | 496709000 | 496709000 | 498697000 | 498697000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R9.htm | Dividends declared (in dollars per share) | 3.89 | 3.89 | 3.62 | 3.62 | Y | FILING-CHECKED | equity statement parenthetical 'Dividends declared' 3.89 / 3.62 (CashPaid twin exists) | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive income | 2298016000 | 2298016000 | 1638319000 | 1638319000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R6.htm | Cash and cash equivalents | 2499406000 | 2499406000 | 1991342000 | 1991342000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R6.htm | Accounts receivable less allowances of $5,441 ($7,160 in 202 | 1436075000 | 1436075000 | 1336331000 | 1336331000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| inventory | mapped | InventoryNet | BS R6.htm | Inventories | 1656323000 | 1656323000 | 1447687000 | 1447687000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| current_assets | mapped | AssetsCurrent | BS R6.htm | Total current assets | 7108061000 | 7108061000 | 5484654000 | 5484654000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R6.htm | Net property, plant and equipment | 3315696000 | 3315696000 | 3415550000 | 3415550000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| goodwill | mapped | Goodwill | BS R6.htm | Goodwill | 26945180000 | 26945180000 | 26909775000 | 26909775000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| total_assets | mapped | Assets | BS R6.htm | TOTAL ASSETS | 47992712000 | 47992712000 | 48228277000 | 48228277000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R6.htm | Accounts payable | 543760000 | 543760000 | 487457000 | 487457000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R6.htm | Total current liabilities | 3245801000 | 3245801000 | 2988280000 | 2988280000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| total_liabilities | not_presented |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED | R6 prints no total liabilities line (instants are never summed) |
| total_debt | component sum | LongTermDebtCurrent+CommercialPaper+LongTermDebtNoncurrent | BS R6.htm+R6.htm+R6.htm | Debt, current + Commercial paper notes + Long-term debt | 8591705000 | 8591705000 | 7581687000 | 7581687000 | Y | FILING-CHECKED | BS 'Debt, current' + 'Commercial paper notes' + 'Long-term debt'; finance lease liabilities: checked in leases note if fetched (see below) | accn 0000006281-25-000153 period ..2025-11-01 |
| stockholders_equity | mapped | StockholdersEquity | BS R6.htm | Total shareholders’ equity | 33815755000 | 33815755000 | 35176317000 | 35176317000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R7.htm | Common stock, shares outstanding (in shares) | 489654097 | 489654097 | 496296854 | 496296854 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period ..2025-11-01 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R10.htm | Net cash provided by operating activities | 4812202000 | 4812202000 | 3852529000 | 3852529000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R10.htm | Net cash used for investing activities | -1321521000 | -1321521000 | -1104858000 | -1104858000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R10.htm | Net cash used for financing activities | -2982617000 | -2982617000 | -1714390000 | -1714390000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R10.htm | Additions to property, plant and equipment, net | -533552000 | 533552000 | -730463000 | 730463000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| depreciation_and_amortization | component sum | Depreciation+AmortizationOfIntangibleAssets | CF R10.htm+R10.htm | Depreciation + Amortization of intangibles | 1998845000 | 1998845000 | 2104316000 | 2104316000 | Y | FILING-CHECKED | two printed CF lines: Depreciation 406,801 + Amortization of intangibles 1,592,044 | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | CF R10.htm | Amortization of intangibles | 1592044000 | 1592044000 | 1741545000 | 1741545000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| sbc | mapped | ShareBasedCompensation | CF R10.htm | Stock-based compensation expense | 321560000 | 321560000 | 262710000 | 262710000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R10.htm | Dividend payments to shareholders | -1924413000 | 1924413000 | -1795459000 | 1795459000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R10.htm | Repurchase of common stock | -2164638000 | 2164638000 | -615590000 | 615590000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R10.htm | Accounts receivable | -90960000 | 90960000 | 133402000 | -133402000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R10.htm | Inventories | -208636000 | 208636000 | 191170000 | -191170000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R10.htm | Accounts payable and accrued liabilities | 657305000 | 657305000 | -133758000 | -133758000 | Y | FILING-CHECKED |  | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cash_paid_for_interest | mapped | InterestPaid | NOTE R40.htm | Interest | 255637000 | 255637000 | 268192000 | 268192000 | Y | FILING-CHECKED | not on the CF face; note R40 supplemental cash flow 'Interest' 255,637 / 268,192 (InterestPaid) | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaid | NOTE R40.htm | Income taxes | 568137000 | 568137000 | 414838000 | 414838000 | Y | FILING-CHECKED | note R40 'Income taxes' 568,137 / 414,838 (IncomeTaxesPaid, not the Net tag) | accn 0000006281-25-000153 period 2024-11-03..2025-11-01 |

## Era checks (tag changes in the last ~5 years)
Auto scan flagged interest_expense (InterestExpenseNonoperating FY2022-FY2025; InterestExpense FY2021-FY2023) and dividends_per_share (Declared FY2022-FY2025; CashPaid FY2021-FY2025). Older-10-K confirmation: see ERA-CHECK in the CSV.

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1. ADI IS IncomeLossFromContinuingOperationsPerBasicShare map basic_eps (1710-2110, 5 filings) and ...PerDilutedShare map diluted_eps: older era; the latest 10-K R3 prints 'Basic earnings per common share' 4.59 on EarningsPerShareBasic and 'Diluted' 4.56 on EarningsPerShareDiluted. No conflict for the latest filing.
2. ADI BS not_presented total_liabilities (51): AGREE (R6 has no total liabilities line).

## Mismatches (printed vs API)
none beyond sign differences (interest income printed (105,266) as a credit in 'nonoperating expense (income)'; other, net printed 7,934 expense = fact -7,934).

## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)

- 0 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
