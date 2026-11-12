# MOD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0001104659-26-066795 (CIK 0000067347, MODINE MANUFACTURING CO, filed 2026-05-27, FY ended 2026-03-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R2.htm IS '2IS'; R3.htm CI '3CI'; R4.htm BS '4BS'; R5.htm PAR '5BSp'; R6.htm CF '6CF'; R7.htm EQ '7EQ'; cover R1.htm.
- companyfacts CIK0000067347.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0001140361-23-026536 (tag-change era: interest_expense).

FY0 = 2026-03-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R2.htm | Net sales | 3181100000 | 3181100000 | 2583500000 | 2583500000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R2.htm | Cost of sales | 2450000000 | 2450000000 | 1939700000 | 1939700000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| gross_profit | mapped | GrossProfit | IS R2.htm | Gross profit | 731100000 | 731100000 | 643800000 | 643800000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| operating_expenses | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no operating expenses line on the face |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R2.htm | Selling, general and administrative expenses | 360100000 | 360100000 | 332100000 | 332100000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| research_and_development | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no research and development line on the face |
| operating_income | mapped | OperatingIncomeLoss | IS R2.htm | Operating income | 342400000 | 342400000 | 283500000 | 283500000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R2.htm | Interest expense | -31600000 | 31600000 | -26400000 | 26400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| interest_income | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no interest income line on the face |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R2.htm | Other expense - net | -8200000 | -8200000 | -3100000 | -3100000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R2.htm | Earnings before income taxes | 186500000 | 186500000 | 254000000 | 254000000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R2.htm | Provision for income taxes | -63200000 | 63200000 | -68500000 | 68500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| net_income | mapped | NetIncomeLoss | IS R2.htm | Net earnings attributable to Modine | 121500000 | 121500000 | 184000000 | 184000000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R2.htm | Basic (in dollars per share) | 2.3 | 2.3 | 3.5 | 3.5 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R2.htm | Diluted (in dollars per share) | 2.26 | 2.26 | 3.42 | 3.42 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R2.htm | Basic (in shares) | 52800000 | 52800000 | 52600000 | 52600000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R2.htm | Diluted (in shares) | 53800000 | 53800000 | 53900000 | 53900000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| dividends_per_share | not_presented |  | IS/CI/PAR/EQ/BS/CF R2.htm,R3.htm,R4.htm,R5.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends per share line on the face |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R3.htm | Comprehensive income attributable to Modine | 265700000 | 265700000 | 166100000 | 166100000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R4.htm | Cash and cash equivalents | 73500000 | 73500000 | 71600000 | 71600000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R4.htm | Trade accounts receivable - net | 731000000 | 731000000 | 478900000 | 478900000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| inventory | mapped | InventoryNet | BS R4.htm | Inventories | 506100000 | 506100000 | 340900000 | 340900000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| current_assets | mapped | AssetsCurrent | BS R4.htm | Total current assets | 1416100000 | 1416100000 | 961200000 | 961200000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R4.htm | Property, plant and equipment - net | 520900000 | 520900000 | 390500000 | 390500000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| goodwill | mapped | Goodwill | BS R4.htm | Goodwill | 292100000 | 292100000 | 233900000 | 233900000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| total_assets | mapped | Assets | BS R4.htm | Total assets | 2674600000 | 2674600000 | 1917600000 | 1917600000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R4.htm | Accounts payable | 464800000 | 464800000 | 290800000 | 290800000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R4.htm | Total current liabilities | 728900000 | 728900000 | 541000000 | 541000000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| total_liabilities | mapped | Liabilities | BS R4.htm | Total liabilities | 1471800000 | 1471800000 | 999400000 | 999400000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| total_debt | component sum | ShortTermBorrowings+LongTermDebtAndCapitalLeaseObligationsCurrent+LongTermDebtAndCapitalLeaseObligations | BS R4.htm+R4.htm+R4.htm | Short-term debt + Long-term debt - current portion + Long-te | 436300000 | 436300000 | 350800000 | 350800000 | Y | FILING-CHECKED | BS debt lines: 'Short-term debt' + 'Long-term debt - current portion' + 'Long-term debt'; operating leases excluded | accn 0001104659-26-066795 period ..2026-03-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R4.htm | Total Modine shareholders' equity | 1194500000 | 1194500000 | 910200000 | 910200000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period ..2026-03-31 |
| shares_outstanding | not_presented |  | BS/PAR  |  |  |  |  |  |  | FILING-CHECKED | no balance-sheet-date outstanding count (CommonStockSharesOutstanding) printed (BS prints issued 57,000,000, treasury 4,200,000); cover count 52,815,785 as of 2026-05-22 not used (ruling 2026-11-12) |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R6.htm | Net cash provided by operating activities | 248700000 | 248700000 | 213300000 | 213300000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R6.htm | Net cash used for investing activities | -321300000 | -321300000 | -86600000 | -86600000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R6.htm | Net cash provided by (used for) financing activities | 73100000 | 73100000 | -113600000 | -113600000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R6.htm | Expenditures for property, plant and equipment | -143300000 | 143300000 | -84000000 | 84000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R6.htm | Depreciation and amortization | 79700000 | 79700000 | 77700000 | 77700000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| amortization_of_intangibles | not_presented |  | CF/IS R2.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | ShareBasedCompensation | CF R6.htm | Stock-based compensation expense | 22100000 | 22100000 | 26400000 | 26400000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| dividends_paid | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends paid line on the face |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R6.htm | Purchases of treasury stock | -7000000 | 7000000 | -30900000 | 30900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R6.htm | Trade accounts receivable | -222600000 | 222600000 | -61200000 | 61200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R6.htm | Inventories | -125100000 | 125100000 | 13600000 | -13600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R6.htm | Accounts payable | 151100000 | 151100000 | 10500000 | 10500000 | Y | FILING-CHECKED | accn 0001104659-26-066795 period 2025-04-01..2026-03-31 |
| cash_paid_for_interest | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for interest line on the face |
| cash_paid_for_income_taxes | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: interest_expense.
- interest_expense: era 10-K 0001140361-23-026536 R2.htm prints 'Interest expense' -20700000 on us-gaap:InterestExpense (API 20700000, period 2022-04-01..2023-03-31, match Y); latest 10-K uses InterestExpenseNonoperating

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
39 of 39 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
