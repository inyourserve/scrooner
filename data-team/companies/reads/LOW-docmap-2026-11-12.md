# LOW document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000060667-26-000029 (CIK 0000060667, filed 2026-03-23, FY ended 2026-01-30). Statement pages: BS R5.htm, BSP R6.htm, CF R9.htm, CI R4.htm, COVER R1.htm, EQ R7.htm, EQP R8.htm, IS R3.htm.
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R3.htm | Net sales | 86286000000 | 86286000000 | 83674000000 | 83674000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | Cost of sales | 57401000000 | 57401000000 | 55797000000 | 55797000000 | Y | FILING-CHECKED | line above gross profit (rule 4) |
| gross_profit | mapped | GrossProfit | IS R3.htm | Gross margin | 28885000000 | 28885000000 | 27877000000 | 27877000000 | Y | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, general and administrative | 16791000000 | 16791000000 | 15682000000 | 15682000000 | Y | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 10153000000 | 10153000000 | 10466000000 | 10466000000 | Y | FILING-CHECKED | 'Operating income' printed |
| interest_expense | combined | InterestIncomeExpenseNonoperatingNet | IS R3.htm | Interest – net | 1406000000 | -1406000000 | 1313000000 | -1313000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | printed line is net of interest income or other items |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Pre-tax earnings | 8747000000 | 8747000000 | 9153000000 | 9153000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income tax provision | 2093000000 | 2093000000 | 2196000000 | 2196000000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net earnings | 6654000000 | 6654000000 | 6957000000 | 6957000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic earnings per common share (in dollars per share) | 11.87 | 11.87 | 12.25 | 12.25 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted earnings per common share (in dollars per share) | 11.85 | 11.85 | 12.23 | 12.23 | Y | FILING-CHECKED |  |
| weighted_basic_shares | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| weighted_diluted_shares | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | EQP R8.htm | Cash dividends declared (in dollars per share) | 4.75 | 4.75 | 4.55 | 4.55 | Y | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive income | 6637000000 | 6637000000 | 6945000000 | 6945000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and cash equivalents | 982000000 | 982000000 | 1761000000 | 1761000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | ReceivablesNetCurrent | BS R5.htm | Receivables - net | 1090000000 | 1090000000 | 94000000 | 94000000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R5.htm | Merchandise inventory - net | 17300000000 | 17300000000 | 17409000000 | 17409000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total current assets | 20955000000 | 20955000000 | 20358000000 | 20358000000 | Y | FILING-CHECKED |  |
| ppe_net | combined | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | BS R5.htm | Property, less accumulated depreciation | 18362000000 | 18362000000 | 17649000000 | 17649000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill | 3945000000 | 3945000000 | 311000000 | 311000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R5.htm | Total assets | 54144000000 | 54144000000 | 43102000000 | 43102000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R5.htm | Accounts payable | 9762000000 | 9762000000 | 9290000000 | 9290000000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total current liabilities | 19463000000 | 19463000000 | 18757000000 | 18757000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R5.htm | Total liabilities | 64061000000 | 64061000000 | 57333000000 | 57333000000 | Y | FILING-CHECKED |  |
| total_debt | component sum | LongTermDebtAndCapitalLeaseObligationsCurrent+LongTermDebtAndCapitalLeaseObligations | BS R5.htm | Current maturities of long-term debt + Long-term debt, exclu | 39921000000 | 39921000000 | 35487000000 | 35487000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R5.htm | Total shareholders’ deficit | -9917000000 | -9917000000 | -14231000000 | -14231000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 560063429 | 560063429 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R9.htm | Net cash provided by operating activities | 9864000000 | 9864000000 | 9625000000 | 9625000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R9.htm | Net cash used in investing activities | -12264000000 | -12264000000 | -1738000000 | -1738000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R9.htm | Net cash provided by/(used in) financing activities | 1621000000 | 1621000000 | -7047000000 | -7047000000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R9.htm | Capital expenditures | -2213000000 | 2213000000 | -1927000000 | 1927000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R9.htm | Depreciation and amortization | 2194000000 | 2194000000 | 1972000000 | 1972000000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R9.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R9.htm | Share-based payment expense | 247000000 | 247000000 | 221000000 | 221000000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R9.htm | Cash dividend payments | -2636000000 | 2636000000 | -2566000000 | 2566000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R9.htm | Repurchases of common stock | -211000000 | 211000000 | -4053000000 | 4053000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ar_change | not_presented |  | CF R9.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R9.htm | Merchandise inventory – net | 703000000 | -703000000 | -514000000 | 514000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayableTrade | CF R9.htm | Accounts payable | 73000000 | 73000000 | 633000000 | 633000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | not_presented |  | CF R9.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |
| cash_paid_for_income_taxes | not_presented |  | CF R9.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |

## Era checks (tag changes in the last ~5 years)
- none flagged

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- LOW operating_income: file says (file)  (-); read says mapped us-gaap:OperatingIncomeLoss 'Operating income'. DECISION: AGREE: the file's not_presented row covers older filings only; the latest 10-K prints the line (a map row is added for the latest era)

## Mismatches (printed vs API)
- none beyond sign differences
