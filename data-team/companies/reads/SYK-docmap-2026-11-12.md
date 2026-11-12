# SYK document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000310764-26-000010 (CIK 0000310764, filed 2026-02-11, FY ended 2025-12-31). Statement pages: BS R5.htm, BSP R6.htm, CF R8.htm, CI R4.htm, COVER R1.htm, EQ R7.htm, IS R3.htm.
- Era 10-K for interest_expense (InterestExpenseDebt, FY2024): 0000310764-25-000023: tag not on the statement pages (note or dimensioned).
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | IS R3.htm | Net sales | 25116000000 | 25116000000 | 22595000000 | 22595000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfRevenue | IS R3.htm | Cost of sales | 9051000000 | 9051000000 | 8155000000 | 8155000000 | Y | FILING-CHECKED | line above gross profit (rule 4) |
| gross_profit | mapped | GrossProfit | IS R3.htm | Gross profit | 16065000000 | 16065000000 | 14440000000 | 14440000000 | Y | FILING-CHECKED |  |
| operating_expenses | mapped | OperatingExpenses | IS R3.htm | Total operating expenses | 11176000000 | 11176000000 | 10751000000 | 10751000000 | Y | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, general and administrative expenses | 8651000000 | 8651000000 | 7685000000 | 7685000000 | Y | FILING-CHECKED |  |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R3.htm | Research, development and engineering expenses | 1623000000 | 1623000000 | 1466000000 | 1466000000 | Y | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 4889000000 | 4889000000 | 3689000000 | 3689000000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | -607000000 | 607000000 | -409000000 | 409000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Interest expense' printed (FY2025 tag; companyfacts has it for FY2025 only) |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R3.htm | Other income | 232000000 | 232000000 | 212000000 | 212000000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Earnings before income taxes | 4514000000 | 4514000000 | 3492000000 | 3492000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income taxes | 1268000000 | 1268000000 | 499000000 | 499000000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net earnings | 3246000000 | 3246000000 | 2993000000 | 2993000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic net earnings per share of common stock (in dollars per | 8.49 | 8.49 | 7.86 | 7.86 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted net earnings per share of common stock (in dollars p | 8.4 | 8.4 | 7.76 | 7.76 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic (in shares) | 382200000 | 382200000 | 381000000 | 381000000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted (in shares) | 386500000 | 386500000 | 385600000 | 385600000 | Y | FILING-CHECKED |  |
| dividends_per_share | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive income | 2852000000 | 2852000000 | 3116000000 | 3116000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and cash equivalents | 4011000000 | 4011000000 | 3652000000 | 3652000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R5.htm | Accounts receivable, less allowance of $216 ($213 in 2024) | 4039000000 | 4039000000 | 3987000000 | 3987000000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R5.htm | Total inventories | 5310000000 | 5310000000 | 4774000000 | 4774000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total current assets | 14755000000 | 14755000000 | 14847000000 | 14847000000 | Y | FILING-CHECKED |  |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R5.htm | Property, plant and equipment, net | 3876000000 | 3876000000 | 3448000000 | 3448000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill | 19291000000 | 19291000000 | 15855000000 | 15855000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R5.htm | Total assets | 47844000000 | 47844000000 | 42971000000 | 42971000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableTradeCurrent | BS R5.htm | Accounts payable | 1799000000 | 1799000000 | 1679000000 | 1679000000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total current liabilities | 7794000000 | 7794000000 | 7616000000 | 7616000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R5.htm | Total liabilities | 25424000000 | 25424000000 | 22337000000 | 22337000000 | Y | FILING-CHECKED | 'Total liabilities' printed |
| total_debt | component sum | DebtCurrent+LongTermDebtNoncurrent | BS R5.htm | Current maturities of debt + Long-term debt, excluding curre | 15859000000 | 15859000000 | 13597000000 | 13597000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | BS R5.htm | Total shareholders' equity | 22420000000 | 22420000000 | 20634000000 | 20634000000 | Y | FILING-CHECKED | incl-NCI tag, no NCI line printed: parent equity (rule 8) |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 382688675 | 382688675 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R8.htm | Net cash provided by operating activities | 5044000000 | 5044000000 | 4242000000 | 4242000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R8.htm | Net cash used in investing activities | -4866000000 | -4866000000 | -3000000000 | -3000000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R8.htm | Net cash provided by (used in) financing activities | 113000000 | 113000000 | -525000000 | -525000000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R8.htm | Purchases of property, plant and equipment | -761000000 | 761000000 | -755000000 | 755000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | mapped | Depreciation | CF R8.htm | Depreciation | 461000000 | 461000000 | 427000000 | 427000000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | IS R3.htm | Amortization of intangible assets | 732000000 | 732000000 | 623000000 | 623000000 | Y | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R8.htm | Share-based compensation | 243000000 | 243000000 | 229000000 | 229000000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividends | CF R8.htm | Payments of dividends | -1284000000 | 1284000000 | -1219000000 | 1219000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R8.htm | Accounts receivable | 127000000 | -127000000 | -321000000 | 321000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R8.htm | Inventories | -297000000 | 297000000 | -206000000 | 206000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayableTrade | CF R8.htm | Accounts payable | 94000000 | 94000000 | 192000000 | 192000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R8.htm | Cash paid for interest on debt | 582000000 | 582000000 | 396000000 | 396000000 | Y | FILING-CHECKED |  |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R8.htm | Cash paid for income taxes, net of refunds | 1002000000 | 1002000000 | 989000000 | 989000000 | Y | FILING-CHECKED |  |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2025]; ERA-CHECK others: {'InterestExpenseDebt': [2021, 2022, 2023, 2024]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- SYK interest_expense: file says not_presented  (-); read says mapped us-gaap:InterestExpenseNonoperating 'Interest expense'. DECISION: AGREE: the file's not_presented row covers older filings only; the latest 10-K prints the line (a map row is added for the latest era)
- SYK total_liabilities: file says (file)  (-); read says mapped us-gaap:Liabilities 'Total liabilities'. DECISION: AGREE: the file's not_presented row covers older filings only; the latest 10-K prints the line (a map row is added for the latest era)

## Mismatches (printed vs API)
- none beyond sign differences
