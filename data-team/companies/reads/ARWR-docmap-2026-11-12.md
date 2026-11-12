# ARWR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0000879407-25-000029 (CIK 0000879407, ARROWHEAD PHARMACEUTICALS, INC., filed 2025-11-25, FY ended 2025-09-30); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R3.htm BS '3BS'; R4.htm PAR '4BSp'; R5.htm IS '5IS'; R6.htm EQ '6EQ'; R7.htm CF '7CF'; cover R1.htm.
- companyfacts CIK0000879407.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0001628280-22-030869 (tag-change era: research_and_development).
- Era 10-K 0001628280-23-040219 (tag-change era: interest_expense).

FY0 = 2025-09-30; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R5.htm | Revenue | 829448000 | 829448000 | 3551000 | 3551000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cost_of_revenue | not_presented |  | IS/CI R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no cost of revenue line on the face |
| gross_profit | not_presented |  | IS/CI R5.htm  |  |  |  |  |  |  | FILING-CHECKED | no gross profit line on the face |
| operating_expenses | mapped | OperatingExpenses | IS R5.htm | Total operating expenses | 731102000 | 731102000 | 604631000 | 604631000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| sga_expense | component sum | GeneralAndAdministrativeExpense | IS R5.htm | General and administrative | 123943000 | 123943000 | 98761000 | 98761000 | Y | FILING-CHECKED | only 'General and administrative' (GeneralAndAdministrativeExpense) printed; no SG&A line | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R5.htm | Research and development | 607159000 | 607159000 | 505870000 | 505870000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| operating_income | mapped | OperatingIncomeLoss | IS R5.htm | Operating income (loss) | 98346000 | 98346000 | -601080000 | -601080000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R5.htm | Interest expense | -89361000 | 89361000 | -32352000 | 32352000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| interest_income | combined | InvestmentIncomeInterestAndDividend | IS R5.htm | Interest income | 37289000 | 37289000 | 22720000 | 22720000 | Y | FILING-CHECKED | 'Interest income': interest and dividend income | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R5.htm | Other, net | 5259000 | 5259000 | -1748000 | -1748000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R5.htm | Income (loss) before income tax expense and noncontrolling i | 51533000 | 51533000 | -612460000 | -612460000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R5.htm | Income tax expense (benefit) | 21419000 | 21419000 | -2767000 | -2767000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| net_income | mapped | NetIncomeLoss | IS R5.htm | Net loss attributable to Arrowhead Pharmaceuticals, Inc. | -1631000 | -1631000 | -599493000 | -599493000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| basic_eps | mapped | EarningsPerShareBasic | IS R5.htm | Basic (in dollars per share) | -0.01 | -0.01 | -5 | -5 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R5.htm | Diluted (in dollars per share) | -0.01 | -0.01 | -5 | -5 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R5.htm | Basic (in shares) | 133758000 | 133758000 | 119784000 | 119784000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R5.htm | Diluted (in shares) | 133758000 | 133758000 | 119784000 | 119784000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| dividends_per_share | not_presented |  | IS/CI/PAR/EQ/BS/CF R3.htm,R4.htm,R5.htm,R7.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends per share line on the face |
| comprehensive_income | combined | ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest | IS R5.htm | Other comprehensive income (loss) | 31807000 | 31807000 | -601721000 | -601721000 | Y | FILING-CHECKED | 'Other comprehensive income (loss)': includes noncontrolling interests | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cash_and_equivalents | mapped | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | BS R3.htm | Cash, cash equivalents and restricted cash | 226548000 | 226548000 | 102685000 | 102685000 | Y | FILING-CHECKED | 'Cash, cash equivalents and restricted cash': BS cash line on the restricted-cash-total tag (flag) | accn 0000879407-25-000029 period ..2025-09-30 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R3.htm | Accounts receivable | 6824000 | 6824000 | 0 | 0 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| inventory | not_presented |  | BS R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no inventory line on the face |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 950639000 | 950639000 | 695471000 | 695471000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R3.htm | Property, plant and equipment, net | 382515000 | 382515000 | 386032000 | 386032000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| goodwill | not_presented |  | BS R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no goodwill line on the face |
| total_assets | mapped | Assets | BS R3.htm | Total Assets | 1385295000 | 1385295000 | 1139802000 | 1139802000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R3.htm | Accounts payable | 17674000 | 17674000 | 11388000 | 11388000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 195487000 | 195487000 | 103168000 | 103168000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| total_liabilities | not_presented |  | BS R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no total liabilities line on the face |
| total_debt | component sum | LinesOfCreditCurrent+LongTermLineOfCredit | BS R3.htm+R3.htm | Credit facility + Credit facility, net of current portion | 254883000 | 254883000 | 393183000 | 393183000 | Y | FILING-CHECKED | BS debt lines: 'Credit facility' + 'Credit facility, net of current portion'; operating leases excluded | accn 0000879407-25-000029 period ..2025-09-30 |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total Arrowhead Pharmaceuticals, Inc. stockholders' equity | 466052000 | 466052000 | 185444000 | 185444000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period ..2025-09-30 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R4.htm | Common stock, shares outstanding (in shares) | 135702000 | 135702000 | 124376000 | 124376000 | Y | FILING-CHECKED | balance-sheet-date count | accn 0000879407-25-000029 period ..2025-09-30 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R7.htm | Net cash provided by (used in) operating activities | 179552000 | 179552000 | -462851000 | -462851000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R7.htm | Net cash used in investing activities | -129294000 | -129294000 | -420072000 | -420072000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R7.htm | Net cash provided by financing activities | 74006000 | 74006000 | 870520000 | 870520000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R7.htm | Purchases of property, plant and equipment | -22666000 | 22666000 | -141469000 | 141469000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| depreciation_and_amortization | mapped | DepreciationAndAmortization | CF R7.htm | Depreciation and amortization | 23928000 | 23928000 | 18595000 | 18595000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| amortization_of_intangibles | not_presented |  | CF/IS R5.htm,R7.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | ShareBasedCompensation | CF R7.htm | Stock-based compensation | 63366000 | 63366000 | 73968000 | 73968000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| dividends_paid | not_presented |  | CF R7.htm  |  |  |  |  |  |  | FILING-CHECKED | no dividends paid line on the face |
| share_buybacks | not_presented |  | CF R7.htm  |  |  |  |  |  |  | FILING-CHECKED | no share buybacks line on the face |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R7.htm | Accounts receivable | -56967000 | 56967000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cf_inventory_change | not_presented |  | CF R7.htm  |  |  |  |  |  |  | FILING-CHECKED | no cf inventory change line on the face |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R7.htm | Accounts payable | 6286000 | 6286000 | -5536000 | -5536000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R7.htm | Interest paid | -19000 | 19000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R7.htm | Income taxes (refund) paid | 814000 | 814000 | -3744000 | -3744000 | Y | FILING-CHECKED | accn 0000879407-25-000029 period 2024-10-01..2025-09-30 |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: research_and_development, interest_expense.
- research_and_development: era 10-K 0001628280-22-030869 R5.htm prints 'Research and development' 297307000 on us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost (API 297307000, period 2021-10-01..2022-09-30, match Y); latest 10-K uses ResearchAndDevelopmentExpense
- interest_expense: era 10-K 0001628280-23-040219 R5.htm prints 'Interest expense' 0 on us-gaap:InterestExpense (API 0, period 2020-10-01..2021-09-30, match Y); latest 10-K uses InterestExpenseNonoperating

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
37 of 37 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
