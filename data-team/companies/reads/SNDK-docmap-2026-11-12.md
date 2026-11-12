# SNDK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.

## Filings opened
- Latest 10-K 0001628280-26-057406 (CIK 0002023554, filed 2026-08-17, FY ended 2026-07-03, comparative 2025-06-27). R3 balance sheet (accounts payable printed by related-party axis), R4 BS parenthetical (shares outstanding), R5 operations, R6 comprehensive income, R7 cash flows, R8 equity. Sandisk was spun from Western Digital in Feb 2025; only two 10-Ks exist, so no older-10-K era check is possible beyond the FY2025 10-K (first 10-K).
- companyfacts CIK0002023554.json (one call).

FY0 = 2026-07-03; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R5.htm | Revenue, net | 20248000000 | 20248000000 | 7355000000 | 7355000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R5.htm | Cost of revenue | 5776000000 | 5776000000 | 5143000000 | 5143000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| gross_profit | mapped | GrossProfit | IS R5.htm | Gross profit | 14472000000 | 14472000000 | 2212000000 | 2212000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| operating_expenses | mapped | OperatingExpenses | IS R5.htm | Total operating expenses | 2083000000 | 2083000000 | 3589000000 | 3589000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R5.htm | Selling, general and administrative | 676000000 | 676000000 | 573000000 | 573000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | IS R5.htm | Research and development | 1328000000 | 1328000000 | 1132000000 | 1132000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| operating_income | mapped | OperatingIncomeLoss | IS R5.htm | Operating income (loss) | 12389000000 | 12389000000 | -1377000000 | -1377000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| interest_expense | mapped | InterestExpenseNonoperating | IS R5.htm | Interest expense | -73000000 | 73000000 | -63000000 | 63000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | R5 'Interest expense' printed (73,000,000); fact +73,000,000 | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| interest_income | mapped | InvestmentIncomeInterest | IS R5.htm | Interest income | 70000000 | 70000000 | 22000000 | 22000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R5.htm | Other income (expense), net | -177000000 | -177000000 | -59000000 | -59000000 | Y | FILING-CHECKED | R5 'Other income (expense), net' (177,000,000); the subtotal 'Total interest and other income (expense), net' 628,000,000 (NonoperatingIncomeExpense) includes interest and equity-security gains | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R5.htm | Income (loss) before taxes | 13017000000 | 13017000000 | -1479000000 | -1479000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R5.htm | Income tax expense | 1584000000 | 1584000000 | 162000000 | 162000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| net_income | mapped | NetIncomeLoss | IS R5.htm | Net income (loss) | 11433000000 | 11433000000 | -1641000000 | -1641000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| basic_eps | mapped | EarningsPerShareBasic | IS R5.htm | Basic (in dollars per share) | 77.78 | 77.78 | -11.32 | -11.32 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R5.htm | Diluted (in dollars per share) | 73.76 | 73.76 | -11.32 | -11.32 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R5.htm | Basic (in shares) | 147000000 | 147000000 | 145000000 | 145000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R5.htm | Diluted (in shares) | 155000000 | 155000000 | 145000000 | 145000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| dividends_per_share | not_presented |  | PAR  |  |  |  |  |  |  | FILING-CHECKED | no dividends declared or paid (R7 has no dividends line; R8 equity has no per-share dividend) |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R6.htm | Total comprehensive income (loss) | 11426000000 | 11426000000 | -1428000000 | -1428000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R3.htm | Cash and cash equivalents | 4762000000 | 4762000000 | 1481000000 | 1481000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R3.htm | Accounts receivable, net | 4708000000 | 4708000000 | 1068000000 | 1068000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| inventory | mapped | InventoryNet | BS R3.htm | Inventories | 2698000000 | 2698000000 | 2079000000 | 2079000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 12780000000 | 12780000000 | 5086000000 | 5086000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R3.htm | Property, plant and equipment, net | 674000000 | 674000000 | 619000000 | 619000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| goodwill | mapped | Goodwill | BS R3.htm | Goodwill | 4994000000 | 4994000000 | 4999000000 | 4999000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| total_assets | mapped | Assets | BS R3.htm | Total assets | 22507000000 | 22507000000 | 12985000000 | 12985000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| accounts_payable | not_presented |  | BS R3.htm |  |  |  |  |  |  | FILING-CHECKED | R3 prints accounts payable only by related-party axis: 'Accounts payable' non-related 516 / 366 and related party 460 / 400 (both dimensioned); no total accounts payable line or undimensioned fact (instants are never summed; no segment/component served as consolidated) |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 5581000000 | 5581000000 | 1427000000 | 1427000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| total_liabilities | mapped | Liabilities | BS R3.htm | Total liabilities | 6771000000 | 6771000000 | 3769000000 | 3769000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| total_debt | component sum | LongTermDebtCurrent+LongTermDebtNoncurrent | BS R3.htm+R3.htm | Current portion of long-term debt + Long-term debt | 0 | 0 | 1849000000 | 1849000000 | Y | FILING-CHECKED | BS 'Current portion of long-term debt' + 'Long-term debt'; both 0 at FY2026 (term loan repaid); FY2025 20 + 1,829 million; no finance lease fact found in fetched pages | accn 0001628280-26-057406 period ..2026-07-03 |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total shareholders’ equity | 15736000000 | 15736000000 | 9216000000 | 9216000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R4.htm | Shares outstanding (in shares) | 146000000 | 146000000 | 146000000 | 146000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period ..2026-07-03 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R7.htm | Net cash provided by (used in) operating activities | 11671000000 | 11671000000 | 84000000 | 84000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R7.htm | Net cash provided by (used in) investing activities | -1386000000 | -1386000000 | 556000000 | 556000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R7.htm | Net cash provided by (used in) financing activities | -7001000000 | -7001000000 | 518000000 | 518000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R7.htm | Purchases of property, plant and equipment | -177000000 | 177000000 | -204000000 | 204000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| depreciation_and_amortization | mapped | DepreciationAndAmortization | CF R7.htm | Depreciation and amortization | 149000000 | 149000000 | 163000000 | 163000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| amortization_of_intangibles | not_presented |  | NOTE  |  |  |  |  |  |  | FILING-CHECKED | no such line on the face statements (R pages read) and no consolidated fact in the fetched detail pages; no amortization-of-intangibles line on R7 (D&A 149M combined) or in the fetched detail pages |
| sbc | mapped | ShareBasedCompensation | CF R7.htm | Stock-based compensation | 232000000 | 232000000 | 182000000 | 182000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| dividends_paid | not_presented |  | CF R7.htm |  |  |  |  |  |  | FILING-CHECKED | no dividends paid line on R7 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R7.htm | Repurchases of common stock | -4524000000 | 4524000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R7.htm | Accounts receivable, net | -3640000000 | 3640000000 | -100000000 | 100000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R7.htm | Inventories | -619000000 | 619000000 | -160000000 | 160000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayableTrade | CF R7.htm | Accounts payable | 109000000 | 109000000 | 93000000 | 93000000 | Y | FILING-CHECKED | CF 'Accounts payable' (trade) 109,000,000; a separate 'Accounts payable to related parties' 60,000,000 line exists: the mapped line excludes related-party payables | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R7.htm | Cash paid for interest | 116000000 | 116000000 | 139000000 | 139000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R7.htm | Cash paid for income taxes | 146000000 | 146000000 | 50000000 | 50000000 | Y | FILING-CHECKED |  | accn 0001628280-26-057406 period 2025-06-28..2026-07-03 |

## Era checks (tag changes in the last ~5 years)
Only two annual periods exist as a separate registrant (FY2025, FY2026; FY2024 values in the FY2025/FY2026 10-K are carve-out comparatives). No tag change across them (auto scan clean; shares_outstanding tag exists from FY2025 only). No older 10-K to open.

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1. SNDK IS IncomeLossFromEquityMethodInvestments exclude dividends_paid (9): AGREE (R7 'Equity loss in investees, net of dividends received' is not a dividend line).
2. SNDK CF not_presented dividends_paid (9): AGREE (R7 has no dividends paid line; no dividends declared). dividends_per_share also not_presented (no dividend), not in the cloud file.

## Mismatches (printed vs API)
none beyond sign differences (interest expense printed (73,000,000) with positive fact).
