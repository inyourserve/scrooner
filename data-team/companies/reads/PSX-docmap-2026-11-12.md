# PSX document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0001534701-26-000006 (CIK 0001534701, filed 2026-02-20, FY ended 2025-12-31). Statement pages: BS R5.htm, BSP R6.htm, CF R7.htm, CI R4.htm, COVER R1.htm, EQ R8.htm, IS R3.htm.
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R3.htm | Sales and other operating revenues | 132376000000 | 132376000000 | 143153000000 | 143153000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | Purchased crude oil and products | 116093000000 | 116093000000 | 129962000000 | 129962000000 | Y | FILING-CHECKED |  |
| gross_profit | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, general and administrative expenses | 2437000000 | 2437000000 | 2814000000 | 2814000000 | Y | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| interest_expense | mapped | InterestAndDebtExpense | IS R3.htm | Interest and debt expense | 1039000000 | 1039000000 | 907000000 | 907000000 | Y | FILING-CHECKED |  |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R3.htm | Other income | 438000000 | 438000000 | 243000000 | 243000000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossIncludingPortionAttributableToNoncontrollingInterest | IS R3.htm | Income before income taxes | 5420000000 | 5420000000 | 2675000000 | 2675000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income tax expense | 892000000 | 892000000 | 500000000 | 500000000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net Income Attributable to Phillips 66 | 4403000000 | 4403000000 | 2117000000 | 2117000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic (in dollars per share) | 10.82 | 10.82 | 5.01 | 5.01 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted (in dollars per share) | 10.79 | 10.79 | 4.99 | 4.99 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic (in shares) | 406008000 | 406008000 | 420174000 | 420174000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted (in shares) | 408053000 | 408053000 | 421888000 | 421888000 | Y | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareCashPaid | EQ R8.htm | Dividends Paid Per Share of Common Stock (in dollars per sha | 4.75 | 4.75 |  |  | Y | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive Income Attributable to Phillips 66 | 4643000000 | 4643000000 | 1992000000 | 1992000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and cash equivalents | 1116000000 | 1116000000 | 1738000000 | 1738000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | AccountsNotesAndLoansReceivableNetCurrent | BS R5.htm | Accounts and notes receivable (net of allowances of $68 mill | 9158 |  |  |  | no API fact (dimensioned or not in companyfacts for this accession) | FILING-CHECKED (printed only) |  |
| inventory | mapped | InventoryNet | BS R5.htm | Inventories | 5097000000 | 5097000000 | 3995000000 | 3995000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total Current Assets | 17271000000 | 17271000000 | 17910000000 | 17910000000 | Y | FILING-CHECKED |  |
| ppe_net | combined | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | BS R5.htm | Net properties, plants and equipment | 39097000000 | 39097000000 | 35264000000 | 35264000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill | 1433000000 | 1433000000 | 1575000000 | 1575000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R5.htm | Total Assets | 73680000000 | 73680000000 | 72582000000 | 72582000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R5.htm | Accounts payable | 8581 |  |  |  | no API fact (dimensioned or not in companyfacts for this accession) | FILING-CHECKED (printed only) |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total Current Liabilities | 13326000000 | 13326000000 | 15087000000 | 15087000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R5.htm | Total Liabilities | 43439000000 | 43439000000 | 44119000000 | 44119000000 | Y | FILING-CHECKED |  |
| total_debt | component sum | DebtCurrent+LongTermDebtAndCapitalLeaseObligations | BS R5.htm | Short-term debt + Long-term debt | 19716000000 | 19716000000 | 20062000000 | 20062000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R5.htm | Total Stockholders’ Equity | 29093000000 | 29093000000 | 27408000000 | 27408000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 400744022 | 400744022 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R7.htm | Net Cash Provided by Operating Activities | 4962000000 | 4962000000 | 4191000000 | 4191000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R7.htm | Net Cash Used in Investing Activities | -2097000000 | -2097000000 | -2463000000 | -2463000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R7.htm | Net Cash Used in Financing Activities | -3537000000 | -3537000000 | -3305000000 | -3305000000 | Y | FILING-CHECKED |  |
| capex | combined | psx:CapitalExpendituresAndInvestments | CF R7.htm | Capital expenditures and investments | -2233 |  |  |  | no API fact (dimensioned or not in companyfacts for this accession) | FILING-CHECKED | 'Capital expenditures and investments' (2,233) mixes capex with investments (R7) |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R7.htm | Depreciation and amortization | 3251000000 | 3251000000 | 2363000000 | 2363000000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R7.htm | Dividends paid on common stock | -1922000000 | 1922000000 | -1882000000 | 1882000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R7.htm | Repurchase of common stock | -1207000000 | 1207000000 | -3451000000 | 3451000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInReceivables | CF R7.htm | Accounts and notes receivable | -508000000 | 508000000 | 574000000 | -574000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R7.htm | Inventories | 160000000 | -160000000 | -278000000 | 278000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R7.htm | Accounts payable | -804000000 | -804000000 | -491000000 | -491000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |
| cash_paid_for_income_taxes | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |

## Era checks (tag changes in the last ~5 years)
- none flagged

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- PSX capex: file says (file)  (-); read says combined psx:CapitalExpendituresAndInvestments 'Capital expenditures and investments'. DECISION: FILE STANDS (combined)

## Mismatches (printed vs API)
- none beyond sign differences
