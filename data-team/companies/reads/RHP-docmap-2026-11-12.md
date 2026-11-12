# RHP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0001104659-26-019035 (CIK 0001040829, RYMAN HOSPITALITY PROPERTIES, INC., filed 2026-02-24, FY ended 2025-12-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R2.htm BS '2BS'; R3.htm PAR '3BSp'; R4.htm IS '4IS'; R5.htm CI '5CI'; R6.htm CF '6CF'; R7.htm PAR '7CFp'; R8.htm EQ '8EQ'; R9.htm PAR '9EQp'; cover R1.htm.
- companyfacts CIK0001040829.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0001558370-22-002101 (tag-change era: interest_expense).
- Era 10-K 0001558370-23-002012 (tag-change era: net_income).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R4.htm | Total revenues | 2577061000 | 2577061000 | 2339226000 | 2339226000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R4.htm | Total hotel operating expenses | 1441052000 | 1441052000 | 1324752000 | 1324752000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| gross_profit | not_presented |  | IS/CI R4.htm,R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no gross profit line on the face |
| operating_expenses | component sum | CostsAndExpenses-us-gaap:CostOfGoodsAndServicesSold | IS R4.htm | Total operating expenses less Total hotel operating expenses | 648997000 | 648997000 | 523640000 | 523640000 | Y | FILING-CHECKED | no operating-expenses total; 'Total operating expenses' (CostsAndExpenses) includes cost of revenue: opex = total less cost of revenue (perimeter for Tag Expert) | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | IS | Corporate | 42771000 | 42771000 | 41819000 | 41819000 | Y | FILING-CHECKED | KEY FIX 2026-11-12: 0001104659-26-019035 R4.htm prints 'Corporate' 42,771K on GeneralAndAdministrativeExpense and no selling/marketing line: mapped (not a one-part component sum) / accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| research_and_development | not_presented |  | IS/CI R4.htm,R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no research and development line on the face |
| operating_income | mapped | OperatingIncomeLoss | IS R4.htm | Operating income | 487012000 | 487012000 | 490834000 | 490834000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R4.htm | Interest expense | -241270000 | 241270000 | -225395000 | 225395000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| interest_income | mapped | InvestmentIncomeInterest | IS R4.htm | Interest income | 20299000 | 20299000 | 27977000 | 27977000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| other_income_expense_net | not_presented |  | IS/CI R4.htm,R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no other income expense net line on the face |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R4.htm | Income before income taxes | 254634000 | 254634000 | 294026000 | 294026000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R4.htm | (Provision) benefit for income taxes | -7324000 | 7324000 | -13836000 | 13836000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R4.htm | Net income available to common stockholders | 243425000 | 243425000 | 271638000 | 271638000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R4.htm | Basic income per share available to common stockholders | 3.94 | 3.94 | 4.54 | 4.54 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R4.htm | Diluted income per share available to common stockholders | 3.77 | 3.77 | 4.38 | 4.38 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | not_presented |  | IS/CI R4.htm,R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no weighted basic shares line on the face |
| weighted_diluted_shares | not_presented |  | IS/CI R4.htm,R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no weighted diluted shares line on the face |
| dividends_per_share | not_presented |  | IS/CI/PAR/EQ/BS/CF R2.htm,R3.htm,R4.htm,R5.htm,R6.htm,R7.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends per share line on the face |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R5.htm | Comprehensive income available to common stockholders | 245488000 | 245488000 | 275686000 | 275686000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R2.htm | Cash and cash equivalents - unrestricted | 471421000 | 471421000 | 477694000 | 477694000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period ..2025-12-31 |
| accounts_receivable | mapped | AccountsReceivableNet | BS R2.htm | Trade receivables, net | 105903000 | 105903000 | 94184000 | 94184000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period ..2025-12-31 |
| inventory | not_presented |  | BS R2.htm  |  |  |  |  |  |  | FILING-CHECKED | no inventory line on the face |
| current_assets | not_presented |  | BS R2.htm  |  |  |  |  |  |  | FILING-CHECKED | no current assets line on the face |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R2.htm | Property and equipment, net | 4970429000 | 4970429000 | 4124382000 | 4124382000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period ..2025-12-31 |
| goodwill | not_presented |  | BS R2.htm  |  |  |  |  |  |  | FILING-CHECKED | no goodwill line on the face |
| total_assets | mapped | Assets | BS R2.htm | Total assets | 6181183000 | 6181183000 | 5217573000 | 5217573000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period ..2025-12-31 |
| accounts_payable | not_presented |  | BS R2.htm  |  |  |  |  |  |  | FILING-CHECKED | no accounts payable line on the face |
| current_liabilities | not_presented |  | BS R2.htm  |  |  |  |  |  |  | FILING-CHECKED | no current liabilities line on the face |
| total_liabilities | mapped | Liabilities | BS R2.htm | Total liabilities | 4969407000 | 4969407000 | 4282991000 | 4282991000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period ..2025-12-31 |
| total_debt | mapped | DebtAndCapitalLeaseObligations | BS R2.htm | Debt and finance lease obligations | 3976913000 | 3976913000 | 3378396000 | 3378396000 | Y | FILING-CHECKED | BS debt lines: 'Debt and finance lease obligations'; operating leases excluded | accn 0001104659-26-019035 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R2.htm | Total stockholders' equity | 750152000 | 750152000 | 548980000 | 548980000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period ..2025-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R3.htm | Common stock, shares outstanding (in shares) | 63006000 | 63006000 | 59903000 | 59903000 | Y | FILING-CHECKED | balance-sheet-date count | accn 0001104659-26-019035 period ..2025-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R6.htm | Net cash flows provided by operating activities | 590629000 | 590629000 | 576506000 | 576506000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R6.htm | Net cash flows used in investing activities | -1233972000 | -1233972000 | -410402000 | -410402000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R6.htm | Net cash flows provided by (used in) financing activities | 567295000 | 567295000 | -290317000 | -290317000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsForCapitalImprovements | CF R6.htm | Purchases of property and equipment | -358235000 | 358235000 | -407905000 | 407905000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | mapped | DepreciationAndAmortization | CF R6.htm | Depreciation and amortization | 278100000 | 278100000 | 235626000 | 235626000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | not_presented |  | CF/IS R4.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | ShareBasedCompensation | CF R6.htm | Equity-based compensation expense | 14061000 | 14061000 | 13891000 | 13891000 | Y | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R6.htm | Payment of distributions | -285576000 | 285576000 | -266114000 | 266114000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| share_buybacks | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no share buybacks line on the face |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R6.htm | Trade receivables | 2162000 | -2162000 | 15845000 | -15845000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| cf_inventory_change | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no cf inventory change line on the face |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R6.htm | Accounts payable and accrued liabilities | 12292000 | 12292000 | 13860000 | 13860000 | Y | FILING-CHECKED | 'Accounts payable and accrued liabilities': payables and accrued liabilities one line | accn 0001104659-26-019035 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for interest line on the face |
| cash_paid_for_income_taxes | not_presented |  | CF R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: interest_expense, net_income.
- interest_expense: era 10-K 0001558370-22-002101 R4.htm prints 'Interest expense' -125347000 on us-gaap:InterestExpense (API 125347000, period 2021-01-01..2021-12-31, match Y); latest 10-K uses InterestExpenseNonoperating
- net_income: era 10-K 0001558370-23-002012 R4.htm prints 'Net income (loss) available to common stockholders' 128993000 on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic (API 128993000, period 2022-01-01..2022-12-31, match Y); latest 10-K uses NetIncomeLoss

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
29 of 29 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
