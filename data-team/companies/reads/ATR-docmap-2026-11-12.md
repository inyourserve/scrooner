# ATR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0000896622-26-000007 (CIK 0000896622, AptarGroup, Inc, filed 2026-02-06, FY ended 2025-12-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R3.htm IS '3IS'; R4.htm CI '4CI'; R5.htm BS '5BS'; R6.htm PAR '6BSp'; R7.htm EQ '7EQ'; R8.htm CF '8CF'; cover R1.htm.
- companyfacts CIK0000896622.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0000896622-22-000006 (tag-change era: interest_expense).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | IS R3.htm | Net Sales | 3777181000 | 3777181000 | 3582890000 | 3582890000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | IS R3.htm | Cost of Sales (exclusive of depreciation and amortization): | 2372446000 | 2372446000 | 2227381000 | 2227381000 | Y | FILING-CHECKED | 'Cost of Sales (exclusive of depreciation and amortization):': excludes D&A | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| gross_profit | not_presented |  | IS/CI R3.htm,R4.htm  |  |  |  |  |  |  | FILING-CHECKED | no gross profit line on the face |
| operating_expenses | component sum | CostsAndExpenses-us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | IS R3.htm | Total Operating Expenses less Cost of Sales (exclusive of de | 903697000 | 903697000 | 859012000 | 859012000 | Y | FILING-CHECKED | no operating-expenses total; 'Total Operating Expenses' (CostsAndExpenses) includes cost of revenue: opex = total less cost of revenue (perimeter for Tag Expert) | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| sga_expense | not_presented |  | IS/CI R3.htm,R4.htm  |  |  |  |  |  |  | FILING-CHECKED | no sga expense line on the face |
| research_and_development | not_presented |  | IS/CI R3.htm,R4.htm  |  |  |  |  |  |  | FILING-CHECKED | no research and development line on the face |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating Income | 501038000 | 501038000 | 496497000 | 496497000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | -52737000 | 52737000 | -43898000 | 43898000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| interest_income | mapped | InvestmentIncomeInterest | IS R3.htm | Interest income | 11676000 | 11676000 | 12101000 | 12101000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R3.htm | Miscellaneous (expense) income, net | -2027000 | -2027000 | 3265000 | 3265000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Income before Income Taxes | 491378000 | 491378000 | 469765000 | 469765000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Provision for Income Taxes | 98881000 | 98881000 | 95587000 | 95587000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net Income Attributable to AptarGroup, Inc. | 392789000 | 392789000 | 374541000 | 374541000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic (in dollars per share) | 5.97 | 5.97 | 5.65 | 5.65 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted (in dollars per share) | 5.89 | 5.89 | 5.53 | 5.53 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | not_presented |  | IS/CI R3.htm,R4.htm  |  |  |  |  |  |  | FILING-CHECKED | no weighted basic shares line on the face |
| weighted_diluted_shares | not_presented |  | IS/CI R3.htm,R4.htm  |  |  |  |  |  |  | FILING-CHECKED | no weighted diluted shares line on the face |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | IS R3.htm | Dividends per Common Share (in dollars per share) | 1.83 | 1.83 | 1.72 | 1.72 | Y | FILING-CHECKED | printed on R3.htm (3IS) | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive Income Attributable to AptarGroup, Inc. | 635892000 | 635892000 | 254035000 | 254035000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and equivalents | 402424000 | 402424000 | 223844000 | 223844000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| accounts_receivable | mapped | AccountsNotesAndLoansReceivableNetCurrent | BS R5.htm | Accounts and notes receivable, less current expected credit  | 803830000 | 803830000 | 658057000 | 658057000 | Y | FILING-CHECKED | wider tag us-gaap:AccountsNotesAndLoansReceivableNetCurrent is the single receivables line on the BS face (R5.htm 'Accounts and notes receivable, less current expected credit loss ("CECL") of $17,732 in 2025 and $15,785 in 2024'): mapped per ruling 2026-11-12 | accn 0000896622-26-000007 period ..2025-12-31 |
| inventory | mapped | InventoryNet | BS R5.htm | Inventories | 537845000 | 537845000 | 461807000 | 461807000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total Current Assets | 1893562000 | 1893562000 | 1478383000 | 1478383000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| ppe_net | combined | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | BS R5.htm | ​Property, Plant and Equipment, Net | 1676479000 | 1676479000 | 1447150000 | 1447150000 | Y | FILING-CHECKED | '​Property, Plant and Equipment, Net': includes finance-lease ROU | accn 0000896622-26-000007 period ..2025-12-31 |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill | 1077898000 | 1077898000 | 936256000 | 936256000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R5.htm | Total Assets | 5252719000 | 5252719000 | 4432278000 | 4432278000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| accounts_payable | mapped | atr:AccountsPayableAccruedLiabilitiesAndDerivativeLiabilitiesCurrent | BS R5.htm | Accounts payable, accrued and other liabilities | 822913000 |  | 729996000 |  | no API value | FILING-CHECKED (R page only) | custom extension tag atr:AccountsPayableAccruedLiabilitiesAndDerivativeLiabilitiesCurrent for 'Accounts payable, accrued and other liabilities': companyfacts carries no extension facts, checked against the R page only |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total Current Liabilities | 1166444000 | 1166444000 | 1068281000 | 1068281000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| total_liabilities | not_presented |  | BS R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no total liabilities line on the face |
| total_debt | component sum | ShortTermBorrowings+LongTermDebtAndCapitalLeaseObligationsCurrent+LongTermDebtAndCapitalLeaseObligations | BS R5.htm+R5.htm+R5.htm | Short-term obligations + Current maturities of long-term obl | 1482964000 | 1482964000 | 1026351000 | 1026351000 | Y | FILING-CHECKED | BS debt lines: 'Short-term obligations' + 'Current maturities of long-term obligations, net of unamortized debt issuance costs' + 'Long-Term Obligations, net of unamortized debt issuance costs'; operating leases excluded | accn 0000896622-26-000007 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R5.htm | Total AptarGroup, Inc. Stockholders’ Equity | 2668096000 | 2668096000 | 2471888000 | 2471888000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period ..2025-12-31 |
| shares_outstanding | not_presented |  | BS/PAR  |  |  |  |  |  |  | FILING-CHECKED | no balance-sheet-date outstanding count (CommonStockSharesOutstanding) printed (BS prints issued 72,800,000, treasury 8,600,000); cover count 64,379,735 as of 2026-02-02 not used (ruling 2026-11-12) |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R8.htm | Net Cash Provided by Operations | 569999000 | 569999000 | 643413000 | 643413000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R8.htm | Net Cash Used by Investing Activities | -331426000 | -331426000 | -396721000 | -396721000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R8.htm | Net Cash Used by Financing Activities | -77471000 | -77471000 | -225344000 | -225344000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R8.htm | Capital expenditures | -270419000 | 270419000 | -276481000 | 276481000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | mapped | Depreciation | CF R8.htm | Depreciation | 242312000 | 242312000 | 219667000 | 219667000 | Y | FILING-CHECKED | printed CF lines: Depreciation | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | not_presented |  | CF/IS R3.htm,R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | ShareBasedCompensation | CF R8.htm | Stock-based compensation | 43941000 | 43941000 | 47650000 | 47650000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R8.htm | Dividends paid | -120784000 | 120784000 | -114055000 | 114055000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R8.htm | Purchase of treasury stock | -365005000 | 365005000 | -68638000 | 68638000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cf_ar_change | combined | IncreaseDecreaseInAccountsAndOtherReceivables | CF R8.htm | Accounts and other receivables | -73888000 | 73888000 | -18079000 | 18079000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Accounts and other receivables': accounts and other receivables | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R8.htm | Inventories | -10646000 | 10646000 | 21901000 | -21901000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R8.htm | Accounts payable, accrued and other liabilities | -18274000 | -18274000 | -23705000 | -23705000 | Y | FILING-CHECKED | 'Accounts payable, accrued and other liabilities': payables and accrued liabilities one line | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R8.htm | Interest paid | 49972000 | 49972000 | 43520000 | 43520000 | Y | FILING-CHECKED | accn 0000896622-26-000007 period 2025-01-01..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | CF R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: interest_expense.
- interest_expense: era 10-K 0000896622-22-000006 R3.htm prints 'Interest expense' -30284000 on us-gaap:InterestExpense (API 30284000, period 2021-01-01..2021-12-31, match Y); latest 10-K uses InterestExpenseNonoperating

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
37 of 37 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
