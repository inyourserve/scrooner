# BLK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.

## Filings opened
- Latest 10-K 0001193125-26-071966 (BlackRock, Inc., CIK 0002012383, filed 2026-02-25, FY ended 2025-12-31, comparative 2024-12-31). R2 statements of financial condition, R3 BS parenthetical (shares outstanding), R4 income statement, R5/R6 comprehensive income, R7/R8 equity (R8: dividends per share), R9 cash flows; note R138 capital stock (dividends). Sector template: asset manager (broker/AM): gross profit OUT; current assets/liabilities OUT candidate (unclassified balance sheet).
- companyfacts CIK0002012383.json (one call). The registrant is the post-GIP-merger BlackRock, Inc. (new CIK); older history sits under CIK 0001364742.

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R4.htm | Total revenue | 24216000000 | 24216000000 | 20407000000 | 20407000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cost_of_revenue | OUT |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED | asset manager: no cost of revenue line |
| gross_profit | OUT |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED | no gross profit line |
| operating_expenses | combined | OperatingExpenses | IS R4.htm | Total expense | 17171000000 | 17171000000 | 12833000000 | 12833000000 | Y | FILING-CHECKED | check: hand R4: 'Total expense' 17,171 (OperatingExpenses) is an asset manager's full expense base (distribution and direct fund expense included); no gross profit line: combined; the template decides (Dhairya per-ticker list) | 2026-11-12 |
| sga_expense | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED | only 'General and administration expense' 2,731 (G&A component, never SG&A); no selling line |
| research_and_development | OUT |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED | no R&D |
| operating_income | mapped | OperatingIncomeLoss | IS R4.htm | Operating income | 7045000000 | 7045000000 | 7574000000 | 7574000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R4.htm | Interest expense | -614000000 | 614000000 | -538000000 | 538000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| interest_income | combined | InvestmentIncomeInterestAndDividend | IS R4.htm | Interest and dividend income | 554000000 | 554000000 | 767000000 | 767000000 | Y | FILING-CHECKED | 'Interest and dividend income' 554 = combined (interest + dividends) | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R4.htm | Total nonoperating income (expense) | 574000000 | 574000000 | 721000000 | 721000000 | Y | FILING-CHECKED | 'Total nonoperating income (expense)' 574 = net gains on investments 634 + interest and dividend income 554 - interest expense 614 (own total line) | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R4.htm | Income before income taxes | 7619000000 | 7619000000 | 8295000000 | 8295000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R4.htm | Income tax expense | 1677000000 | 1677000000 | 1783000000 | 1783000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R4.htm | Net income attributable to BlackRock, Inc. | 5553000000 | 5553000000 | 6369000000 | 6369000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R4.htm | Basic | 35.83 | 35.83 | 42.45 | 42.45 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R4.htm | Diluted | 35.31 | 35.31 | 42.01 | 42.01 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R4.htm | Basic | 154984319 | 154984319 | 150042269 | 150042269 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R4.htm | Diluted (including Subco Units) | 160866521 | 160866521 | 151615085 | 151615085 | Y | FILING-CHECKED | label 'Diluted (including Subco Units)' | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R8.htm | Dividends declared, amount per share | 20.84 | 20.84 | 20.4 | 20.4 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R5.htm | Comprehensive income attributable to BlackRock, Inc. | 6159000000 | 6159000000 | 6031000000 | 6031000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R2.htm | Cash and cash equivalents | 11468000000 | 11468000000 | 12762000000 | 12762000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| accounts_receivable | mapped | AccountsReceivableNet | BS R2.htm | Accounts receivable | 5158000000 | 5158000000 | 4304000000 | 4304000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| inventory | OUT |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED | no inventory |
| current_assets | OUT |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED | unclassified balance sheet |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R2.htm | Property and equipment (net of accumulated depreciation and  | 1256000000 | 1256000000 | 1103000000 | 1103000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| goodwill | mapped | Goodwill | BS R2.htm | Goodwill | 35283000000 | 35283000000 | 25949000000 | 25949000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R2.htm | Total assets | 169998000000 | 169998000000 | 138615000000 | 138615000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| accounts_payable | combined | AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | BS R2.htm | Accounts payable and accrued liabilities | 1740000000 | 1740000000 | 1536000000 | 1536000000 | Y | FILING-CHECKED | 'Accounts payable and accrued liabilities' = combined | accn 0001193125-26-071966 period ..2025-12-31 |
| current_liabilities | OUT |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED | unclassified balance sheet |
| total_liabilities | mapped | Liabilities | BS R2.htm | Total liabilities | 108456000000 | 108456000000 | 89260000000 | 89260000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| total_debt | component sum | LongTermDebt | BS R2.htm | Borrowings | 12768000000 | 12768000000 | 12314000000 | 12314000000 | Y | FILING-CHECKED | BS prints one line 'Borrowings' 12,768 (no current portion or short-term line); no finance lease fact found; separate account collateral liabilities and operating leases excluded | accn 0001193125-26-071966 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R2.htm | Total BlackRock, Inc. stockholders’ equity | 55888000000 | 55888000000 | 47495000000 | 47495000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R3.htm | Common stock, shares outstanding | 155069171 | 155069171 | 154947813 | 154947813 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period ..2025-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R9.htm | Net cash provided by/(used in) operating activities | 3927000000 | 3927000000 | 4956000000 | 4956000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R9.htm | Net cash provided by/(used in) investing activities | -4418000000 | -4418000000 | -3004000000 | -3004000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R9.htm | Net cash provided by/(used in) financing activities | -1127000000 | -1127000000 | 2236000000 | 2236000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R9.htm | Purchases of property and equipment | -375000000 | 375000000 | -255000000 | 255000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | combined | DepreciationAmortizationAndAccretionNet | CF R9.htm | Depreciation and amortization | 1126000000 | 1126000000 | 529000000 | 529000000 | Y | FILING-CHECKED | D&A that includes accretion: combined (Dhairya ruling 2026-11-12) | FIX 2026-11-12
| amortization_of_intangibles | combined | blk:AmortizationAndImpairmentOfIntangibleAssets | IS R4.htm | Amortization and impairment of intangible assets | 775000000 |  | 291000000 |  | n/a (custom tag: companyfacts carries no extension facts; printed = the filing XBRL value) | FILING-CHECKED | R4 own line 'Amortization and impairment of intangible assets' 775 (custom): amortization combined with impairment; no pure amortization line on the face |
| sbc | mapped | ShareBasedCompensation | CF R9.htm | Stock-based compensation | 1307000000 | 1307000000 | 753000000 | 753000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| dividends_paid | combined | blk:DividendsOrSubcoDistributionsPaid | CF R9.htm | Dividends/Subco distributions paid | -3347000000 |  | -3101000000 |  | n/a (custom tag: companyfacts carries no extension facts; printed = the filing XBRL value) | FILING-CHECKED | 'Dividends/Subco distributions paid' (3,347)/(3,101): combined with Subco units distributions; note R138 aggregate dividends 3,265 / 3,101 not confirmed as the cash paid common-only amount |
| share_buybacks | combined | blk:SharesOrSubcoUnitRepurchased | CF R9.htm | Shares/Subco Units repurchased | -1951 |  | -1930 |  | n/a (custom tag: companyfacts carries no extension facts; printed = the filing XBRL value) | FILING-CHECKED | 'Shares/Subco Units repurchased' (1,951)/(1,930): combined with Subco units |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R9.htm | Accounts receivable | -619000000 | 619000000 | -443000000 | 443000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cf_inventory_change | not_presented |  |   |  |  |  |  |  |  | FILING-CHECKED | no such line on the face statements (R pages read) and no consolidated fact in the fetched detail pages; auto: no tagged row on the face statements or fetched detail pages |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R9.htm | Accounts payable and accrued liabilities | 75000000 | 75000000 | 259000000 | 259000000 | Y | FILING-CHECKED | 'Accounts payable and accrued liabilities' = combined | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R9.htm | Interest | 482000000 | 482000000 | 289000000 | 289000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R9.htm | Income taxes (net of refunds) | 2298000000 | 2298000000 | 1699000000 | 1699000000 | Y | FILING-CHECKED |  | accn 0001193125-26-071966 period 2025-01-01..2025-12-31 |

## Era checks (tag changes in the last ~5 years)
The new CIK has few fiscal years in companyfacts, so the 5-year scan is thin; see ERA-CHECK notes for revenue: cloud's BLK revenue row (RevenuesExcludingInterestAndDividends, 1403-1803, 17 filings) is the older era; the latest 10-K tags 'Total revenue' RevenueFromContractWithCustomerExcludingAssessedTax (R4).

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1. BLK IS RevenuesExcludingInterestAndDividends map revenue (1403-1803, 17): older era; the latest 10-K R4 'Total revenue' 24,216 is on RevenueFromContractWithCustomerExcludingAssessedTax (same printed line). BLK IS InvestmentAdvisoryFees exclude revenue (17): AGREE (component).
2. BLK CF c:DividendsOrSubcoDistributionsPaid combined dividends_paid (2509-2606, 4) and c:SharesOrSubcoUnitRepurchased combined share_buybacks: AGREE (R9 'Dividends/Subco distributions paid' (3,347) and 'Shares/Subco Units repurchased' (1,951)). The equity note R138 prints 'Aggregate dividends' 3,265 / 3,101 (DividendsCash) and 'Dividends cash per common share' 20.84 / 20.40: 3,101 equals the FY2024 CF line, 3,265 differs from the FY2025 CF line 3,347 by 82, so the note amount is not the same quantity as cash paid: kept combined, note amount flagged for Tag Expert.
3. BLK IS template_out_pending_read cost_of_revenue;gross_profit (50): CONFIRMED OUT (R4 prints no cost of revenue or gross profit line: expense lines are compensation, sales/asset/account expense, G&A, amortization).
4. BLK BS template_out_pending_read current_assets;current_liabilities (50): CONFIRMED OUT (R2 unclassified: no total current assets or liabilities).

## Mismatches (printed vs API)
none beyond sign differences.

## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)
- operating_expenses: mapped us-gaap:OperatingExpenses -> mapped us-gaap:OperatingExpenses | opex never includes cost of revenue (Dhairya ruling 2026-11-12; expected combined); RE-READ SAYS mapped: read the R page
- depreciation_and_amortization: mapped us-gaap:DepreciationAmortizationAndAccretionNet -> combined us-gaap:DepreciationAmortizationAndAccretionNet | D&A that includes accretion is combined (Dhairya ruling 2026-11-12)
- operating_expenses: check: hand -> combined | check: hand R4: 'Total expense' 17,171 (OperatingExpenses) is an asset manager's full expense base (distribution and direct fund expense inc
- 1 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
