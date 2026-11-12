# WCC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000929008-26-000008 (CIK 0000929008, filed 2026-02-13): COVER R1.htm, BS R3.htm, IS R4.htm, BSP R6.htm, CF R7.htm
- 10-K 0000929008-16-000049 (CIK 0000929008, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000929008-18-000004 (CIK 0000929008, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000929008-22-000009 (CIK 0000929008, era filing): COVER R1.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0000929008.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Net sales | 23510900000 | 23510900000 | 21818800000 | 21818800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of goods sold (excluding depreciation and amortization below) | 18538900000 | 18538900000 | 17106200000 | 17106200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1188 tags across all 91 R pages, face and notes) of 0000929008-26-000008; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1188 tags across all 91 R pages, face and notes) of 0000929008-26-000008; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:OperatingIncomeLoss 'Income from operations / Operating Income (Loss) / The net r' R4 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative expense | 3541400000 | 3541400000 | 3306200000 | 3306200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1188 tags across all 91 R pages, face and notes) of 0000929008-26-000008; label search over every tag in the filing (custom included) found no candidate |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Income from operations | 1233000000 | 1233000000 | 1223200000 | 1223200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R4.htm | Interest expense, net | 386700000 | -386700000 | 364900000 | -364900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 855900000 | 855900000 | 951000000 | 951000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Provision for income taxes | 213400000 | 213400000 | 231600000 | 231600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net Income attributable to WESCO International, Inc. | 640200000 | 640200000 | 717600000 | 717600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 13.26 | 13.26 | 13.26 | 13.26 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 13.05 | 13.05 | 13.05 | 13.05 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R71.htm | Weighted average common shares outstanding used in computing basic earnings per share | 48700000000000 | 48700000 |  |  | N (printed 48700000000000 vs API 48700000) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R71.htm 'EARNINGS PER SHARE - SCHEDULE OF EARNINGS PER SHARE, BASIC AND DILUTED (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R71.htm | Weighted average common shares outstanding and common share equivalents used in computing diluted earnings per share | 49500000000000 | 49500000 |  |  | N (printed 49500000000000 vs API 49500000) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R71.htm 'EARNINGS PER SHARE - SCHEDULE OF EARNINGS PER SHARE, BASIC AND DILUTED (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and cash equivalents | 604800000 | 604800000 | 702600000 | 702600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade accounts receivable | 4069600000 | 4069600000 | 3454400000 | 3454400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 4008800000 | 4008800000 | 3501700000 | 3501700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 9456200000 | 9456200000 | 8351400000 | 8351400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, buildings and equipment, net | 466800000 | 466800000 | 442900000 | 442900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 3343400000 | 3343400000 | 3280100000 | 3280100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1.649e+10 | 16494900000 | 15061400000 | 15061400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 3030500000 | 3030500000 | 2670600000 | 2670600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4296800000 | 4296800000 | 3804000000 | 3804000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 11468500000 | 11468500000 | 10095900000 | 10095900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 5031600000 | 5031600000 | 4970700000 | 4970700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 125000000 | 125000000 | 1101200000 | 1101200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -140700000 | -140700000 | 40400000 | 40400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided (used) by financing activities | -92700000 | -92700000 | -928300000 | -928300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -99800000 | 99800000 | -94700000 | 94700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 197600000 | 197600000 | 183200000 | 183200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 40500000 | 40500000 | 28900000 | 28900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Payment of common stock dividends | -88400000 | 88400000 | -81500000 | 81500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock | -75000000 | 75000000 | -425000000 | 425000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 357400000 | 357400000 | 331200000 | 331200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R7.htm | Cash paid for taxes | 237800000 | 237800000 | 253300000 | 253300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000929008-26-000008 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Short-term debt and current portion of long-term debt + Long-term Debt, Excluding Current Maturities | 5781400000 | 5781400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R8.htm | Common stock, shares outstanding | 48658333 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R8.htm 'CONSOLIDATED BALANCE SHEETS (Parenthetical)' (MetaLinks.json presentation) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 7518487000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Cost of goods sold (excluding depreciation and amortization below)' on us-gaap:CostOfGoodsAndServicesSold = 6024826000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Selling, general and administrative expense' on us-gaap:SellingGeneralAndAdministrativeExpense = 1054951000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 373742000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = 69832000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 303910000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 95537000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Net Income attributable to WESCO International, Inc.' on us-gaap:NetIncomeLoss = 210687000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 4.85 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000929008-16-000049 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 4.18 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000929008-16-000049 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000929008-16-000049 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 160279000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Trade accounts receivable, net of allowance for doubtful accounts of $19,309 and' on us-gaap:AccountsReceivableNetCurrent = 1075257000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 810067000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2257534000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Property, buildings and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 166739000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1681662000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Total assets' on us-gaap:Assets = 4587425000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 715519000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 947801000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2813554000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000929008-16-000049 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1776672000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 283049000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -170230000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -67815000 (FILING-CHECKED)
- capex: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -21658000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 64968000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 12899000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000929008-16-000049 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -155805000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 66342000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000929008-16-000049 R7.htm prints 'Cash paid for taxes' on us-gaap:IncomeTaxesPaid = 74213000 (FILING-CHECKED)
- revenue: era 10-K 0000929008-18-000004 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 7679021000 (FILING-CHECKED)
- cash_and_equivalents: 10-K 0000929008-22-000009 statement not identified (auto)

## Mismatches (printed vs API)
- weighted_basic_shares: N (printed 48700000000000 vs API 48700000) (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: N (printed 49500000000000 vs API 49500000) (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 10 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:WCC); disagree on the mapped sample: 0/3
- cash_paid_for_interest: agree (R7 'Cash paid for interest' InterestPaidNet 357.4)
- gross_profit: agree (R4 prints cost of goods sold then SG&A, no gross profit line)
- interest_expense: agree (R4 'Interest expense, net' InterestIncomeExpenseNonoperatingNet = net line: combined)
- inventory: agree (R3 Inventories 4,008.8)
- operating_expenses: agree (R4 has no total opex line and no gross profit line; the only lead is operating income)
- research_and_development: agree (no R&D line on R4)
- total_debt: agree (R3 25.0 + 5,756.4 = 5,781.4 ($M); no other borrowing line)
- total_liabilities: agree (R3 Total liabilities 11,468.5)
- weighted_basic_shares: disagree (R71 prints 48,700,000 shares ('$ in Millions' scales dollars only); the tool multiplied shares by the dollar scale)
- weighted_diluted_shares: disagree (R71 prints 49,500,000 shares ('$ in Millions' scales dollars only); the tool multiplied shares by the dollar scale)
