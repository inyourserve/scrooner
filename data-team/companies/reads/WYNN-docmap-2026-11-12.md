# WYNN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0001174922-26-000013 (CIK 0001174922, WYNN RESORTS, LIMITED, filed 2026-03-02, FY ended 2025-12-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R3.htm BS '3BS'; R4.htm PAR '4BSp'; R5.htm IS '5IS'; R6.htm CI '6CI'; R7.htm EQ '7EQ'; R8.htm CF '8CF'; cover R1.htm.
- companyfacts CIK0001174922.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0001174922-22-000031 (tag-change era: interest_expense).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerIncludingAssessedTax | IS R5.htm | Total operating revenues | 7137924000 | 7137924000 | 7127961000 | 7127961000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R5.htm | Cost of goods and services sold | 2716151000 |  | 2586960000 |  | no API value | FILING-CHECKED |  |
| gross_profit | not_presented |  | IS/CI R5.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no gross profit line on the face |
| operating_expenses | component sum | CostsAndExpenses-us-gaap:CostOfGoodsAndServicesSold | IS R5.htm | Total operating expenses less Cost of goods and services sol | 3303389000 |  | 3408270000 |  | no API value | FILING-CHECKED | no operating-expenses total; 'Total operating expenses' (CostsAndExpenses) includes cost of revenue: opex = total less cost of revenue (perimeter for Tag Expert) | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R5.htm | General and administrative | 1116952000 | 1116952000 | 1080475000 | 1080475000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| research_and_development | not_presented |  | IS/CI R5.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no research and development line on the face |
| operating_income | mapped | OperatingIncomeLoss | IS R5.htm | Operating income | 1118384000 | 1118384000 | 1132731000 | 1132731000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R5.htm | Interest expense, net of amounts capitalized | -625556000 | 625556000 | -688410000 | 688410000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| interest_income | mapped | InvestmentIncomeInterest | IS R5.htm | Interest income | 66507000 | 66507000 | 130342000 | 130342000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R5.htm | Other | -8625000 | -8625000 | 29170000 | 29170000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R5.htm | Income before income taxes | 514140000 | 514140000 | 643398000 | 643398000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R5.htm | (Provision) benefit for income taxes | -105005000 | 105005000 | -3682000 | 3682000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R5.htm | Net income attributable to Wynn Resorts, Limited | 327334000 | 327334000 | 501078000 | 501078000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R5.htm | Earnings Per Share, Basic | 3.16 | 3.16 | 4.56 | 4.56 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R5.htm | Earnings Per Share, Diluted | 3.14 | 3.14 | 4.35 | 4.35 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R5.htm | Basic (in shares) | 103697000 | 103697000 | 109966000 | 109966000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R5.htm | Diluted (in shares) | 104243000 | 104243000 | 110267000 | 110267000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| dividends_per_share | not_presented |  | IS/CI/PAR/EQ/BS/CF R3.htm,R4.htm,R5.htm,R6.htm,R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends per share line on the face |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R6.htm | Comprehensive income attributable to Wynn Resorts, Limited | 329898000 | 329898000 | 491972000 | 491972000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R3.htm | Cash and cash equivalents | 1463442000 | 1463442000 | 2426155000 | 2426155000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| accounts_receivable | mapped | ReceivablesNetCurrent | BS R3.htm | Accounts receivable, net of allowance for credit losses of $ | 402641000 | 402641000 | 324016000 | 324016000 | Y | FILING-CHECKED | wider tag us-gaap:ReceivablesNetCurrent is the single receivables line on the BS face (R3.htm 'Accounts receivable, net of allowance for credit losses of $45,645 and $37,694'): mapped per ruling 2026-11-12 | accn 0001174922-26-000013 period ..2025-12-31 |
| inventory | mapped | InventoryNet | BS R3.htm | Inventories | 88478000 | 88478000 | 75783000 | 75783000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 2683521000 | 2683521000 | 2921679000 | 2921679000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R3.htm | Property and equipment, net | 6625922000 | 6625922000 | 6521283000 | 6521283000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| goodwill | not_presented |  | BS R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no goodwill line on the face |
| total_assets | mapped | Assets | BS R3.htm | Total assets | 13108117000 | 13108117000 | 12977963000 | 12977963000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R3.htm | Accounts and construction payables | 255307000 | 255307000 | 205146000 | 205146000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 1643178000 | 1643178000 | 1539534000 | 1539534000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| total_liabilities | mapped | Liabilities | BS R3.htm | Total liabilities | 14139396000 | 14139396000 | 13946566000 | 13946566000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| total_debt | component sum | LongTermDebtCurrent+LongTermDebtNoncurrent | BS R3.htm+R3.htm | Current portion of long-term debt + Long-term debt | 10546812000 | 10546812000 | 10541734000 | 10541734000 | Y | FILING-CHECKED | BS debt lines: 'Current portion of long-term debt' + 'Long-term debt'; operating leases excluded | accn 0001174922-26-000013 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total Wynn Resorts, Limited stockholders' deficit | -275492000 | -275492000 | -224161000 | -224161000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period ..2025-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R4.htm | Common stock, shares outstanding (in shares) | 103989787 | 103989787 | 107821567 | 107821567 | Y | FILING-CHECKED | balance-sheet-date count | accn 0001174922-26-000013 period ..2025-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R8.htm | Net cash provided by operating activities | 1352653000 | 1352653000 | 1426203000 | 1426203000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R8.htm | Net cash used in investing activities | -1657161000 | -1657161000 | -83558000 | -83558000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R8.htm | Net cash used in financing activities | -653300000 | -653300000 | -1793794000 | -1793794000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R8.htm | Capital expenditures, net of construction payables and reten | -660433000 | 660433000 | -419929000 | 419929000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | mapped | DepreciationAndAmortization | CF R8.htm | Depreciation and amortization | 620633000 | 620633000 | 658895000 | 658895000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | not_presented |  | CF/IS R5.htm,R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | AllocatedShareBasedCompensationExpense | CF R8.htm | Stock-based compensation expense | 91927000 | 91927000 | 59029000 | 59029000 | Y | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| dividends_paid | combined | PaymentsOfDividends | CF R8.htm | Dividends paid | -174662000 | 174662000 | -139564000 | 139564000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Dividends paid': all dividends (may include preferred/NCI) | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R8.htm | Repurchase of common stock | -380109000 | 380109000 | -401802000 | 401802000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cf_ar_change | combined | IncreaseDecreaseInReceivables | CF R8.htm | Receivables, net | -89980000 | 89980000 | 13478000 | -13478000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Receivables, net': receivables incl. non-trade | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cf_inventory_change | not_presented |  | CF R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no cf inventory change line on the face |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R8.htm | Accounts payable and accrued expenses | 3282000 | 3282000 | -38923000 | -38923000 | Y | FILING-CHECKED | 'Accounts payable and accrued expenses': payables and accrued liabilities one line | accn 0001174922-26-000013 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | not_presented |  | CF R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for interest line on the face |
| cash_paid_for_income_taxes | not_presented |  | CF R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: interest_expense.
- interest_expense: era 10-K 0001174922-22-000031 R5.htm prints 'Interest expense, net of amounts capitalized' -605562000 on us-gaap:InterestExpense (API 605562000, period 2021-01-01..2021-12-31, match Y); latest 10-K uses InterestExpenseNonoperating

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
38 of 38 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
