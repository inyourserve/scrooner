# ETSY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0001370637-26-000019 (CIK 0001370637, ETSY, INC, filed 2026-02-19, FY ended 2025-12-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R3.htm BS '3BS'; R4.htm PAR '4BSp'; R5.htm IS '5IS'; R6.htm CI '6CI'; R7.htm PAR '7CIp'; R8.htm EQ '8EQ'; R9.htm CF '9CF'; R10.htm PAR '10CFp'; cover R1.htm.
- companyfacts CIK0001370637.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0001370637-22-000024 (tag-change era: interest_expense).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R5.htm | Revenue | 2883501000 | 2883501000 | 2808332000 | 2808332000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfRevenue | IS R5.htm | Cost of revenue | 817800000 | 817800000 | 774554000 | 774554000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| gross_profit | mapped | GrossProfit | IS R5.htm | Gross profit | 2065701000 | 2065701000 | 2033778000 | 2033778000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| operating_expenses | mapped | OperatingExpenses | IS R5.htm | Total operating expenses | 1799491000 | 1799491000 | 1653570000 | 1653570000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| sga_expense | component sum | SellingAndMarketingExpense+GeneralAndAdministrativeExpense | IS R5.htm+R5.htm | Marketing + General and administrative | 1247596000 | 1247596000 | 1210514000 | 1210514000 | Y | FILING-CHECKED | selling/marketing and G&A printed as separate lines: Marketing + General and administrative | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R5.htm | Product development | 450192000 | 450192000 | 443056000 | 443056000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| operating_income | mapped | OperatingIncomeLoss | IS R5.htm | Income from operations | 266210000 | 266210000 | 380208000 | 380208000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R5.htm | Interest expense | -18509000 | 18509000 | -13806000 | 13806000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| interest_income | combined | InterestAndOtherIncome | IS R5.htm | Interest and other income | 44489000 | 44489000 | 30982000 | 30982000 | Y | FILING-CHECKED | 'Interest and other income': interest and other income | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R5.htm | Total other (expense) income | -19545000 | -19545000 | 30567000 | 30567000 | Y | FILING-CHECKED | 'Total other (expense) income': total non-operating line (may include interest) | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R5.htm | Income before income taxes | 246665000 | 246665000 | 410775000 | 410775000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R5.htm | (Provision) benefit for income taxes | -83683000 | 83683000 | -107494000 | 107494000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R5.htm | Net income | 162982000 | 162982000 | 303281000 | 303281000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R5.htm | Basic (in dollars per share) | 1.59 | 1.59 | 2.64 | 2.64 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R5.htm | Diluted (in dollars per share) | 1.39 | 1.39 | 2.35 | 2.35 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R5.htm | Basic (in shares) | 102356000 | 102356000 | 114944000 | 114944000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R5.htm | Diluted (in shares) | 124114000 | 124114000 | 131721000 | 131721000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| dividends_per_share | not_presented |  | IS/CI/PAR/EQ/BS/CF R10.htm,R3.htm,R4.htm,R5.htm,R6.htm,R7.htm,R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends per share line on the face |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R6.htm | Comprehensive income | 234353000 | 234353000 | 273004000 | 273004000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R3.htm | Cash and cash equivalents | 1395836000 | 1395836000 | 811178000 | 811178000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R3.htm | Accounts receivable, net | 8690000 | 8690000 | 8702000 | 8702000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| inventory | not_presented |  | BS R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no inventory line on the face |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 1960983000 | 1960983000 | 1327691000 | 1327691000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| ppe_net | combined | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | BS R3.htm | Property and equipment, net | 229197000 | 229197000 | 236706000 | 236706000 | Y | FILING-CHECKED | 'Property and equipment, net': includes finance-lease ROU | accn 0001370637-26-000019 period ..2025-12-31 |
| goodwill | mapped | Goodwill | BS R3.htm | Goodwill | 38067000 | 38067000 | 137089000 | 137089000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R3.htm | Total assets | 2827254000 | 2827254000 | 2417782000 | 2417782000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R3.htm | Accounts payable | 28810000 | 28810000 | 25979000 | 25979000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 1363619000 | 1363619000 | 665113000 | 665113000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| total_liabilities | mapped | Liabilities | BS R3.htm | Total liabilities | 3925349000 | 3925349000 | 3176648000 | 3176648000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| total_debt | component sum | ShortTermBorrowings+FinanceLeaseLiabilityNoncurrent+LongTermDebt | BS R3.htm+R3.htm+R3.htm | Short-term debt, net + Finance lease obligations—net of curr | 3075720000 | 3075720000 | 2381565000 | 2381565000 | Y | FILING-CHECKED | BS debt lines: 'Short-term debt, net' + 'Finance lease obligations—net of current portion' + 'Long-term debt, net'; operating leases excluded | accn 0001370637-26-000019 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total stockholders' deficit | -1098095000 | -1098095000 | -758866000 | -758866000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period ..2025-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R4.htm | Common stock, shares outstanding (in shares) | 97031000 | 97031000 | 108540000 | 108540000 | Y | FILING-CHECKED | balance-sheet-date count | accn 0001370637-26-000019 period ..2025-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R9.htm | Net cash provided by operating activities | 693414000 | 693414000 | 752469000 | 752469000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R9.htm | Net cash provided by (used in) investing activities | 32081000 | 32081000 | -53101000 | -53101000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R9.htm | Net cash used in financing activities | -169875000 | -169875000 | -787168000 | -787168000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R9.htm | Purchases of property and equipment | -15386000 | 15386000 | -14208000 | 14208000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R9.htm | Depreciation and amortization expense | 101845000 | 101845000 | 108074000 | 108074000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | not_presented |  | CF/IS R5.htm,R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | ShareBasedCompensation | CF R9.htm | Stock-based compensation expense | 244745000 | 244745000 | 282847000 | 282847000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| dividends_paid | not_presented |  | CF R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends paid line on the face |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R9.htm | Repurchase of stock | -776899000 | 776899000 | -723899000 | 723899000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R9.htm | Accounts receivable | -10034000 | 10034000 | 3573000 | -3573000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cf_inventory_change | not_presented |  | CF R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no cf inventory change line on the face |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R9.htm | Accounts payable | 2496000 | 2496000 | -3511000 | -3511000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R9.htm | Cash paid for interest | 12235000 | 12235000 | 9052000 | 9052000 | Y | FILING-CHECKED | accn 0001370637-26-000019 period 2025-01-01..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | CF R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: interest_expense.
- interest_expense: era 10-K 0001370637-22-000024 R5.htm prints 'Interest expense' -9885000 on us-gaap:InterestExpense (API 9885000, period 2021-01-01..2021-12-31, match Y); latest 10-K uses InterestExpenseNonoperating

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
43 of 43 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
