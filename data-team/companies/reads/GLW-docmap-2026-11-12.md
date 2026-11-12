# GLW document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000024741-26-000124 (CIK 0000024741, filed 2026-02-12, FY ended 2025-12-31). Statement pages: BS R5.htm, BSP R6.htm, CF R7.htm, CI R4.htm, COVER R1.htm, EQ R8.htm, EQP R9.htm, IS R3.htm.
- Era 10-K for interest_expense (InterestAndDebtExpense, FY2023): 0001437749-24-003735: IS R2.htm 'Interest expense' printed -329000000 API 329000000 match Y (sign differs: printed in parentheses/negated label).
- Era 10-K for cash_and_equivalents (CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents, FY2023): 0001437749-24-003735: BS R4.htm 'Cash and cash equivalents' printed 1779000000 API 1779000000 match Y.
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | IS R3.htm | Net sales | 15629000000 | 15629000000 | 13118000000 | 13118000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfRevenue | IS R3.htm | Cost of sales | 10008000000 | 10008000000 | 8842000000 | 8842000000 | Y | FILING-CHECKED | line above gross profit (rule 4) |
| gross_profit | mapped | GrossProfit | IS R3.htm | Gross margin | 5621000000 | 5621000000 | 4276000000 | 4276000000 | Y | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, general and administrative expenses | 2122000000 | 2122000000 | 1931000000 | 1931000000 | Y | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 2279000000 | 2279000000 | 1135000000 | 1135000000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | -336000000 | 336000000 | -329000000 | 329000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| interest_income | mapped | InvestmentIncomeInterest | IS R3.htm | Interest income | 38000000 | 38000000 | 47000000 | 47000000 | Y | FILING-CHECKED |  |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R3.htm | Other (expense) income, net | -79000000 | -79000000 | -123000000 | -123000000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Income before income taxes | 2052000000 | 2052000000 | 813000000 | 813000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Provision for income taxes (Note 15) | -310000000 | 310000000 | -221000000 | 221000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net income attributable to Corning Incorporated | 1596000000 | 1596000000 | 506000000 | 506000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic (Note 17) (in dollars per share) | 1.87 | 1.87 | 0.59 | 0.59 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted (Note 17) (in dollars per share) | 1.83 | 1.83 | 0.58 | 0.58 | Y | FILING-CHECKED |  |
| weighted_basic_shares | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| weighted_diluted_shares | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | EQP R9.htm | Common dividends (in dollars per share) | 1.12 | 1.12 | 1.12 | 1.12 | Y | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive income attributable to Corning Incorporated | 2034000000 | 2034000000 | 11000000 | 11000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and cash equivalents | 1526000000 | 1526000000 | 1768000000 | 1768000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R5.htm | Trade accounts receivable, net of doubtful accounts - $27 an | 2779000000 | 2779000000 | 2053000000 | 2053000000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R5.htm | Inventories (Note 5) | 3077000000 | 3077000000 | 2724000000 | 2724000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total current assets | 8936000000 | 8936000000 | 7992000000 | 7992000000 | Y | FILING-CHECKED |  |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R5.htm | Property, plant and equipment, net of accumulated depreciati | 14825000000 | 14825000000 | 13359000000 | 13359000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill (Note 7) | 2489000000 | 2489000000 | 2363000000 | 2363000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R5.htm | Total Assets | 30976000000 | 30976000000 | 27735000000 | 27735000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R5.htm | Accounts payable | 1979000000 | 1979000000 | 1472000000 | 1472000000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total current liabilities | 5628000000 | 5628000000 | 4919000000 | 4919000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R5.htm | Total liabilities | 18669000000 | 18669000000 | 16665000000 | 16665000000 | Y | FILING-CHECKED |  |
| total_debt | component sum | DebtCurrent+LongTermDebtAndCapitalLeaseObligations | BS R5.htm | Current portion of long-term debt and short-term borrowings  | 8434000000 | 8434000000 | 7211000000 | 7211000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R5.htm | Total Corning Incorporated shareholders’ equity | 11807000000 | 11807000000 | 10686000000 | 10686000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 857948109 | 857948109 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R7.htm | Net cash provided by operating activities | 2695000000 | 2695000000 | 1939000000 | 1939000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R7.htm | Net cash used in investing activities | -1243000000 | -1243000000 | -744000000 | -744000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R7.htm | Net cash used in financing activities | -1672000000 | -1672000000 | -1164000000 | -1164000000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsForCapitalImprovements | CF R7.htm | Capital expenditures | -1282000000 | 1282000000 | -965000000 | 965000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | component sum | Depreciation+AmortizationOfIntangibleAssets | CF R7.htm | Depreciation + Amortization of purchased intangibles | 1347000000 | 1347000000 | 1350000000 | 1350000000 | Y | FILING-CHECKED | printed depreciation + amortization lines (rule 13) |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | CF R7.htm | Amortization of purchased intangibles | 110000000 | 110000000 | 121000000 | 121000000 | Y | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R7.htm | Share-based compensation expense | 286000000 | 286000000 | 273000000 | 273000000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfOrdinaryDividends | CF R7.htm | Dividends paid | -999000000 | 999000000 | -986000000 | 986000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R7.htm | Purchases of common stock for treasury | -163000000 | 163000000 | -165000000 | 165000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R7.htm | Trade accounts receivable | -749000000 | 749000000 | -717000000 | 717000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R7.htm | Inventories | -243000000 | 243000000 | -171000000 | 171000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | CF R7.htm | Accounts payable and other current liabilities | 584000000 | 584000000 | 470000000 | 470000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |
| cash_paid_for_income_taxes | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2024, 2025]; ERA-CHECK others: {'InterestAndDebtExpense': [2021, 2022, 2023]}
- cash_and_equivalents: chosen tag FY[2024, 2025]; ERA-CHECK others: {'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents': [2021, 2022, 2023]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- none

## Mismatches (printed vs API)
- none beyond sign differences
