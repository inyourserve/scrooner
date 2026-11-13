# ABT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.

## Filings opened
- Latest 10-K 0001628280-26-010185 (CIK 0000001800, filed 2026-02-20, FY ended 2025-12-31, comparative 2024-12-31). R3 statement of earnings, R4/R5 comprehensive income, R6 cash flows, R7 balance sheet, R8 BS parenthetical (shares issued/treasury), R9/R10 equity (R10 parenthetical: dividends per share).
- companyfacts CIK0000001800.json (one call).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R3.htm | Net Sales | 44328000000 | 44328000000 | 41950000000 | 41950000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | Cost of products sold, excluding amortization of intangible  | 19319000000 | 19319000000 | 18706000000 | 18706000000 | Y | FILING-CHECKED | label 'Cost of products sold, excluding amortization of intangible assets' 19,319: perimeter excludes amortization (separate line 1,682) | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| gross_profit | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | no gross profit line |
| operating_expenses | component sum | AmortizationOfIntangibleAssets+ResearchAndDevelopmentExpense+SellingGeneralAndAdministrativeExpense | IS R3.htm+R3.htm+R3.htm | Amortization of intangible assets + Research and development | 16956000000 | 16956000000 | 16419000000 | 16419000000 | Y | FILING-CHECKED | R3 'Total Operating Cost and Expenses' 36,275 (CostsAndExpenses) includes cost of products sold; opex = amortization of intangibles + R&D + SG&A = 16,956 (= total less cost of products sold): perimeter for Tag Expert | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, general and administrative | 12332000000 | 12332000000 | 11697000000 | 11697000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R3.htm | Research and development | 2942000000 | 2942000000 | 2844000000 | 2844000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating Earnings | 8053000000 | 8053000000 | 6825000000 | 6825000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | 493000000 | 493000000 | 559000000 | 559000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| interest_income | mapped | InvestmentIncomeInterest | IS R3.htm | Interest income | -308000000 | 308000000 | -344000000 | 344000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R3.htm | Other (income) expense, net | -548000000 | 548000000 | -376000000 | 376000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Other (income) expense, net' (548) = income; separate line 'Net foreign exchange (gain) loss' (50) not added | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Earnings before Taxes | 8466000000 | 8466000000 | 7013000000 | 7013000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Taxes on Earnings | 1942000000 | 1942000000 | -6389000000 | -6389000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net Earnings | 6524000000 | 6524000000 | 13402000000 | 13402000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic Earnings Per Common Share (in dollars per share) | 3.73 | 3.73 | 7.67 | 7.67 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted Earnings Per Common Share (in dollars per share) | 3.72 | 3.72 | 7.64 | 7.64 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Average Number of Common Shares Outstanding Used for Basic E | 1741000000 | 1741000000 | 1740000000 | 1740000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Average Number of Common Shares Outstanding Plus Dilutive Co | 1748000000 | 1748000000 | 1748000000 | 1748000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R10.htm | Cash dividends declared per common share (in dollars per sha | 2.4 | 2.4 | 2.24 | 2.24 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive Income | 8429000000 | 8429000000 | 13335000000 | 13335000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R7.htm | Cash and cash equivalents | 8522000000 | 8522000000 | 7616000000 | 7616000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R7.htm | Trade receivables, less allowances of — 2025: $490; 2024: $4 | 7929000000 | 7929000000 | 6925000000 | 6925000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| inventory | mapped | InventoryNet | BS R7.htm | Total inventories | 6488000000 | 6488000000 | 6194000000 | 6194000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| current_assets | mapped | AssetsCurrent | BS R7.htm | Total current assets | 25996000000 | 25996000000 | 23656000000 | 23656000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R7.htm | Net property and equipment | 11816000000 | 11816000000 | 10658000000 | 10658000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| goodwill | mapped | Goodwill | BS R7.htm | Goodwill | 24035000000 | 24035000000 | 23108000000 | 23108000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R7.htm | Total Assets | 86713000000 | 86713000000 | 81414000000 | 81414000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| accounts_payable | mapped | AccountsPayableTradeCurrent | BS R7.htm | Trade accounts payable | 4240000000 | 4240000000 | 4195000000 | 4195000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R7.htm | Total current liabilities | 16496000000 | 16496000000 | 14157000000 | 14157000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| total_liabilities | not_presented |  | BS R7.htm |  |  |  |  |  |  | FILING-CHECKED | no total liabilities line |
| total_debt | component sum | LongTermDebtCurrent+LongTermDebtNoncurrent | BS R7.htm+R7.htm | Current portion of long-term debt + Long-term debt | 12929000000 | 12929000000 | 14125000000 | 14125000000 | Y | FILING-CHECKED | BS 'Current portion of long-term debt' + 'Long-term debt'; no short-term borrowings line this year; no finance lease liability fact found in fetched pages | accn 0001628280-26-010185 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R7.htm | Total Abbott Shareholders’ Investment | 52130000000 | 52130000000 | 47664000000 | 47664000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period ..2025-12-31 |
| shares_outstanding | not_presented |  | BS R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand R8 (BS parenthetical) prints shares issued 1,996,795,525 and treasury 260,196,074 only; no BS-date outstanding count is printed (instants never summed); dei never used | 2026-11-12 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R6.htm | Net Cash From Operating Activities | 9566000000 | 9566000000 | 8558000000 | 8558000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R6.htm | Net Cash From (Used in) Investing Activities | -2422000000 | -2422000000 | -2338000000 | -2338000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R6.htm | Net Cash From (Used in) Financing Activities | -6309000000 | -6309000000 | -5404000000 | -5404000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R6.htm | Acquisitions of property and equipment | -2171000000 | 2171000000 | -2207000000 | 2207000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | component sum | Depreciation+AmortizationOfIntangibleAssets | CF R6.htm+R6.htm | Depreciation + Amortization of intangible assets | 3116000000 | 3116000000 | 3218000000 | 3218000000 | Y | FILING-CHECKED | two printed CF lines: Depreciation 1,434 + Amortization of intangible assets 1,682 | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | CF R6.htm | Amortization of intangible assets | 1682000000 | 1682000000 | 1878000000 | 1878000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| sbc | mapped | ShareBasedCompensation | CF R6.htm | Share-based compensation | 664000000 | 664000000 | 673000000 | 673000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R6.htm | Dividends paid | -4116000000 | 4116000000 | -3836000000 | 3836000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R6.htm | Purchases of common shares | -893000000 | 893000000 | -1295000000 | 1295000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R6.htm | Trade receivables | -652000000 | 652000000 | -691000000 | 691000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R6.htm | Inventories | 195000000 | -195000000 | -58000000 | 58000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R6.htm | Trade accounts payable and other liabilities | 954000000 | 954000000 | 356000000 | 356000000 | Y | FILING-CHECKED | 'Trade accounts payable and other liabilities' = combined | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R6.htm | Interest paid | 545000000 | 545000000 | 604000000 | 604000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R6.htm | Income taxes paid | 1933000000 | 1933000000 | 1723000000 | 1723000000 | Y | FILING-CHECKED |  | accn 0001628280-26-010185 period 2025-01-01..2025-12-31 |

## Era checks (tag changes in the last ~5 years)
Auto scan flagged interest_expense (InterestExpenseNonoperating FY2022+, InterestExpense FY2021-23); see the ERA-CHECK in the CSV row. Dividend-per-share tag starts FY2022 in companyfacts (no alternative tag).

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1. ABT BS not_presented total_liabilities (51): AGREE (R7 prints no total liabilities line; it goes Total current liabilities / Long-term debt / Post-employment obligations ... to equity).
2. ABT IS not_presented gross_profit (51): AGREE (R3 has no gross profit line; cost of products sold 'excluding amortization of intangible assets' then a separate amortization line).
No other ABT rows in the cloud file.

## Mismatches (printed vs API)
none beyond sign differences (R3 prints interest income and other (income) as negatives within expense).

## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)
- shares_outstanding: mapped dei:EntityCommonStockSharesOutstanding -> not_presented  | shares_outstanding = BS-date count, never dei (Dhairya ruling 2026-11-12)
- shares_outstanding: check: hand -> not_presented | check: hand R8 (BS parenthetical) prints shares issued 1,996,795,525 and treasury 260,196,074 only; no BS-date outstanding count is printed 
- 0 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
