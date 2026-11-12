# KLAC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.

## Filings opened
- Latest 10-K 0000319201-26-000027 (CIK 0000319201, filed 2026-08-06, FY ended 2026-06-30, comparative 2025-06-30). R3 balance sheet, R4 BS parenthetical, R5 operations, R6 comprehensive income, R7/R8 equity (R8 parenthetical carries dividends per share), R9 cash flows; notes R56-R117 details (R63 other expense components, R69 intangibles, R72 debt, R75-R76 leases, R97 cash taxes).
- companyfacts: https://data.sec.gov/api/xbrl/companyfacts/CIK0000319201.json (one call). No older 10-K opened: no tag change in the last 5 FY.

FY0 = 2026-06-30; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R5.htm | Total revenues | 13579476000 | 13579476000 | 12156162000 | 12156162000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cost_of_revenue | mapped | CostOfRevenue | IS R5.htm | Costs of revenues | 5255060000 | 5255060000 | 4751867000 | 4751867000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| gross_profit | not_presented |  |   |  |  |  |  |  |  | FILING-CHECKED | no such line on the face statements (R pages read) and no consolidated fact in the fetched detail pages; auto: no tagged row on the face statements or fetched detail pages |
| operating_expenses | not_presented |  | IS R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand: KLAC prints revenues then costs and expenses with no gross profit line: no GP - OI tie: blank (Dhairya per-ticker list) | 2026-11-12 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R5.htm | Selling, general and administrative | 1131518000 | 1131518000 | 1029734000 | 1029734000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R5.htm | Research and development | 1532118000 | 1532118000 | 1360334000 | 1360334000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| operating_income | not_presented |  | IS R5.htm |  |  |  |  |  |  | FILING-CHECKED | R5 prints no operating income subtotal; no OperatingIncomeLoss element in the filing |
| interest_expense | mapped | InterestExpenseNonoperating | IS R5.htm | Interest expense | 284440000 | 284440000 | 302166000 | 302166000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| interest_income | mapped | InvestmentIncomeInterest | NOTE R63.htm | Interest income | -177055000 | 177055000 | -180276000 | 180276000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | not on the face; note R63 'Interest income' printed (177,055) as a reduction of 'Other expense (income), net' | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R5.htm | Other expense (income), net | -229585000 | 229585000 | -171487000 | 171487000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R5.htm | Income before income taxes | 5605925000 | 5605925000 | 4644448000 | 4644448000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R5.htm | Provision for income taxes | 775154000 | 775154000 | 582805000 | 582805000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| net_income | mapped | NetIncomeLoss | IS R5.htm | Net income | 4830771000 | 4830771000 | 4061643000 | 4061643000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| basic_eps | mapped | EarningsPerShareBasic | IS R5.htm | Basic (in dollars per share) | 3.68 | 3.68 | 3.05 | 3.05 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R5.htm | Diluted (in dollars per share) | 3.66 | 3.66 | 3.04 | 3.04 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R5.htm | Basic (in shares) | 1311516000 | 1311516000 | 1330299000 | 1330299000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R5.htm | Diluted (in shares) | 1319633000 | 1319633000 | 1337502000 | 1337502000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R8.htm | Cash dividends declared (in dollars per share) | 0.8 | 0.8 | 0.675 | 0.675 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R6.htm | Total comprehensive income | 4795117000 | 4795117000 | 4111919000 | 4111919000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R3.htm | Cash and cash equivalents | 1649842000 | 1649842000 | 2078908000 | 2078908000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R3.htm | Accounts receivable, net | 2889208000 | 2889208000 | 2263915000 | 2263915000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| inventory | mapped | InventoryNet | BS R3.htm | Inventories | 3648538000 | 3648538000 | 3212149000 | 3212149000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 12381790000 | 12381790000 | 10698789000 | 10698789000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R3.htm | Land, property and equipment, net | 1380550000 | 1380550000 | 1252775000 | 1252775000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| goodwill | mapped | Goodwill | BS R3.htm | Goodwill, net | 1788758000 | 1788758000 | 1792193000 | 1792193000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| total_assets | mapped | Assets | BS R3.htm | Total assets | 17951535000 | 17951535000 | 16067926000 | 16067926000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R3.htm | Accounts payable | 623668000 | 623668000 | 458509000 | 458509000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 4304927000 | 4304927000 | 4085795000 | 4085795000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| total_liabilities | mapped | Liabilities | BS R3.htm | Total liabilities | 11601715000 | 11601715000 | 11375473000 | 11375473000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| total_debt | component sum | LongTermDebt | BS R3.htm | Long-term debt | 5887415000 | 5887415000 | 5884257000 | 5884257000 | Y | FILING-CHECKED | BS prints only 'Long-term debt' (no current portion or short-term borrowings; leases R75-R77 operating only, never included); carrying value net of discount and issuance costs | accn 0000319201-26-000027 period ..2026-06-30 |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total stockholders’ equity | 6349820000 | 6349820000 | 4692453000 | 4692453000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R4.htm | Common stock, shares, outstanding (in shares) | 1306983000 | 1306983000 | 1320227000 | 1320227000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period ..2026-06-30 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R9.htm | Net cash provided by operating activities | 4143079000 | 4143079000 | 4081903000 | 4081903000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R9.htm | Net cash used in investing activities | -1190095000 | -1190095000 | -202481000 | -202481000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R9.htm | Net cash used in financing activities | -3385606000 | -3385606000 | -3785687000 | -3785687000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R9.htm | Capital expenditures | -375945000 | 375945000 | -335259000 | 335259000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R9.htm | Depreciation and amortization | 393978000 | 393978000 | 394088000 | 394088000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | NOTE R69.htm | Amortization expense | 190800000 | 190800000 | 220400000 | 220400000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| sbc | mapped | ShareBasedCompensation | CF R9.htm | Stock-based compensation expense | 310171000 | 310171000 | 265011000 | 265011000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R9.htm | Payment of dividends to stockholders | -1057832000 | 1057832000 | -904594000 | 904594000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R9.htm | Common stock repurchases | -2289769000 | 2289769000 | -2149946000 | 2149946000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cf_ar_change | mapped | klac:IncreaseDecreaseInAccountsReceivableExcludingAcquisitionRelated | CF R9.htm | Accounts receivable | -641824000 |  | -367897000 |  | n/a (custom tag: companyfacts carries no extension facts; printed = the filing XBRL value) | FILING-CHECKED | custom tag on CF 'Accounts receivable' |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R9.htm | Inventories | -465963000 | 465963000 | -155170000 | 155170000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R9.htm | Accounts payable | 172357000 | 172357000 | 33789000 | 33789000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R9.htm | Interest paid, net of capitalized interest | 282505000 | 282505000 | 292771000 | 292771000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R9.htm | Income taxes paid, net | 781409000 | 781409000 | 886937000 | 886937000 | Y | FILING-CHECKED |  | accn 0000319201-26-000027 period 2025-07-01..2026-06-30 |

## Era checks (tag changes in the last ~5 years)
Auto scan of companyfacts: every chosen tag has 10-K annual facts for all of the last 5 fiscal years; no tag change, so no older 10-K was opened. Cloud Ritwik's KLAC revenue row (SalesRevenueNet, 1312-1806, 19 filings) is an older era: the latest filing tags the top line RevenueFromContractWithCustomerExcludingAssessedTax (R5), the same printed line 'Total revenues'.

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1. KLAC IS gross_profit not_presented: AGREE (R5 has no gross profit line).
2. KLAC IS operating_income not_presented: AGREE for the latest filing (R5 goes from costs and expenses to income before income taxes; no OperatingIncomeLoss element).
3. KLAC BS StockholdersEquityIncludingPortionAttributable... map stockholders_equity (1 filing): DISAGREE for the latest filing: R3 'Total stockholders equity' is us-gaap:StockholdersEquity 6,349,820K (the parent tag). The cloud row fits only an older filing; map StockholdersEquity. Filing supports: this document read.
4. KLAC BS CashCashEquivalentsRestrictedCash... combined cash (1 filing): DISAGREE for the latest filing: R3 BS 'Cash and cash equivalents' is us-gaap:CashAndCashEquivalentsAtCarryingValue 1,649,842K (pure cash tag); the restricted-cash-total tag sits only on the CF ending-cash line (R9) and equals the BS cash, so there is no restricted cash. Cash = mapped. Filing supports: this document read.
5. KLAC IS SalesRevenueNet map revenue (1312-1806): AGREE for that era (total beats components); current era tag is RevenueFromContractWithCustomerExcludingAssessedTax.

## Mismatches (printed vs API)
none: every mapped row matches the API value for FY0 and FY1 (sign differences are printed-parentheses only).

## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)
- operating_expenses: component sum us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AssetImpairmentCharges -> not_presented  | opex never includes cost of revenue (Dhairya ruling 2026-11-12; expected not_presented)
- operating_expenses: check: hand -> not_presented | check: hand: KLAC prints revenues then costs and expenses with no gross profit line: no GP - OI tie: blank (Dhairya per-ticker list)
- 1 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
