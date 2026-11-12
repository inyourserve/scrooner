# ZWS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0001628280-26-006372 (CIK 0001439288, ZURN ELKAY WATER SOLUTIONS CORPORATION, filed 2026-02-09, FY ended 2025-12-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R3.htm BS '3BS'; R4.htm PAR '4BSp'; R5.htm IS '5IS'; R6.htm CI '6CI'; R7.htm EQ '7EQ'; R8.htm PAR '8EQp'; R9.htm CF '9CF'; cover R1.htm.
- companyfacts CIK0001439288.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).
- Era 10-K 0001439288-22-000032 (tag-change era: interest_expense).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R5.htm | Net sales | 1695900000 | 1695900000 | 1566500000 | 1566500000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R5.htm | Cost of sales | 931100000 | 931100000 | 859500000 | 859500000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| gross_profit | mapped | GrossProfit | IS R5.htm | Gross profit | 764800000 | 764800000 | 707000000 | 707000000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| operating_expenses | not_presented |  | IS/CI R5.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no operating expenses line on the face |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R5.htm | Selling, general and administrative expenses | 417600000 | 417600000 | 389800000 | 389800000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| research_and_development | not_presented |  | IS/CI R5.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no research and development line on the face |
| operating_income | mapped | OperatingIncomeLoss | IS R5.htm | Income from operations | 278900000 | 278900000 | 244600000 | 244600000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| interest_expense | combined | InterestExpenseNonoperating | IS R5.htm | Interest expense, net | -28600000 | 28600000 | -33100000 | 33100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | KEY FIX 2026-11-12: net line 'Interest expense, net' (0001628280-26-006372 R5.htm) is combined per ruling; accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| interest_income | not_presented |  | IS/CI R5.htm,R6.htm  |  |  |  |  |  |  | FILING-CHECKED | no interest income line on the face |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R5.htm | Other income (expense), net | 5500000 | 5500000 | -5900000 | -5900000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R5.htm | Income before income taxes | 256300000 | 256300000 | 207000000 | 207000000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R5.htm | Provision for income taxes | -63900000 | 63900000 | -48100000 | 48100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R5.htm | Net income | 198000000 | 198000000 | 160200000 | 160200000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R5.htm | Net income (in dollars per share) | 1.17 | 1.17 | 0.93 | 0.93 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R5.htm | Net income (in dollars per share) | 1.15 | 1.15 | 0.92 | 0.92 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R5.htm | Basic (in shares) | 168659000 | 168659000 | 171686000 | 171686000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R5.htm | Diluted (in shares) | 171258000 | 171258000 | 174659000 | 174659000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R8.htm | Common stock dividend to be paid (in dollars per share) | 0.38 | 0.38 | 0.33 | 0.33 | Y | FILING-CHECKED | printed on R8.htm (8EQp) | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R6.htm | Total comprehensive income | 195700000 | 195700000 | 153500000 | 153500000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R3.htm | Cash and cash equivalents | 300500000 | 300500000 | 198000000 | 198000000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R3.htm | Receivables, net | 184800000 | 184800000 | 202200000 | 202200000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| inventory | mapped | InventoryNet | BS R3.htm | Inventories, net | 274400000 | 274400000 | 272600000 | 272600000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 811700000 | 811700000 | 722100000 | 722100000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| ppe_net | combined | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | BS R3.htm | Property, plant and equipment, net | 157600000 | 157600000 | 164000000 | 164000000 | Y | FILING-CHECKED | 'Property, plant and equipment, net': includes finance-lease ROU | accn 0001628280-26-006372 period ..2025-12-31 |
| goodwill | mapped | Goodwill | BS R3.htm | Goodwill | 795000000 | 795000000 | 794200000 | 794200000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R3.htm | Total assets | 2679400000 | 2679400000 | 2648500000 | 2648500000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R3.htm | Trade payables | 65200000 | 65200000 | 71700000 | 71700000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 259400000 | 259400000 | 247800000 | 247800000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| total_liabilities | mapped | Liabilities | BS R3.htm | Total liabilities | 1076100000 | 1076100000 | 1061700000 | 1061700000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| total_debt | component sum | LongTermDebtCurrent+LongTermDebtNoncurrent | BS R3.htm+R3.htm | Current maturities of debt + Long-term debt | 496500000 | 496500000 | 495600000 | 495600000 | Y | FILING-CHECKED | BS debt lines: 'Current maturities of debt' + 'Long-term debt'; operating leases excluded | accn 0001628280-26-006372 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total stockholders' equity | 1603300000 | 1603300000 | 1586800000 | 1586800000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period ..2025-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R4.htm | Common stock, shares outstanding (in shares) | 166981602 | 166981602 | 170308023 | 170308023 | Y | FILING-CHECKED | balance-sheet-date count | accn 0001628280-26-006372 period ..2025-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R9.htm | Cash provided by operating activities | 346500000 | 346500000 | 293500000 | 293500000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R9.htm | Cash used for investing activities | -29900000 | -29900000 | -20200000 | -20200000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R9.htm | Cash used for financing activities | -217300000 | -217300000 | -207500000 | -207500000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| capex | not_presented |  | CF R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no capex line on the face |
| depreciation_and_amortization | mapped | Depreciation | CF R9.htm | Depreciation | 30000000 | 30000000 | 29200000 | 29200000 | Y | FILING-CHECKED | printed CF lines: Depreciation | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | IS R5.htm | Amortization of intangible assets | 58700000 | 58700000 | 59100000 | 59100000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| sbc | mapped | ShareBasedCompensation | CF R9.htm | Stock-based compensation expense | 40600000 | 40600000 | 37900000 | 37900000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R9.htm | Payment of common stock dividends | -63900000 | 63900000 | -56600000 | 56600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R9.htm | Repurchase of common stock | -159900000 | 159900000 | -150200000 | 150200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cf_ar_change | combined | IncreaseDecreaseInReceivables | CF R9.htm | Receivables, net | 18400000 | -18400000 | 6300000 | -6300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Receivables, net': receivables incl. non-trade | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R9.htm | Inventories, net | -100000 | 100000 | 2700000 | -2700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R9.htm | Accounts payable | -6800000 | -6800000 | 15800000 | 15800000 | Y | FILING-CHECKED | accn 0001628280-26-006372 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | not_presented |  | CF R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for interest line on the face |
| cash_paid_for_income_taxes | not_presented |  | CF R9.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
Auto scan (companyfacts 10-K annual values, last 5 FY, other candidate tags of the same data point) flagged: interest_expense.
- interest_expense: era 10-K 0001439288-22-000032 R5.htm prints 'Interest expense, net' -34700000 on us-gaap:InterestExpense (API 34700000, period 2021-01-01..2021-12-31, match Y); latest 10-K uses InterestExpenseNonoperating

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
41 of 41 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
