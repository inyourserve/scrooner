# BALL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-017410 (CIK 0000009389, filed 2026-02-19): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001104659-16-097390 (CIK 0000009389, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001558370-18-001345 (CIK 0000009389, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001558370-20-001005 (CIK 0000009389, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000009389.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R2.htm | Net sales | 13161000000 | 13161000000 | 11795000000 | 11795000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R2.htm | Cost of sales (excluding depreciation and amortization) | -10583000000 | 10583000000 | -9354000000 | 9354000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1162 tags across all 116 R pages, face and notes) of 0001104659-26-017410; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1162 tags across all 116 R pages, face and notes) of 0001104659-26-017410; label search over every tag in the filing (custom included) found no candidate |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative | -566000000 | 566000000 | -647000000 | 647000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1162 tags across all 116 R pages, face and notes) of 0001104659-26-017410; HAND REVIEW: 3 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsInProcessResearchAndDevelopment 'Deferred Tax Asset, In-Process Research and Development / Ca' R88; us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits 'Effective Income Tax Rate Reconciliation, Tax Credit, Percen' R61,R84; us-gaap:IncomeTaxReconciliationTaxCredits 'Effective Income Tax Rate Reconciliation, Tax Credit, Amount' R84 |
| operating_income | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1162 tags across all 116 R pages, face and notes) of 0001104659-26-017410; HAND REVIEW: 1 label candidate(s) incl. custom tags: ball:IncomeLossFromContinuingOperationsBeforeRestructuringAndOtherActivities 'Represents the net amount of revenues less costs and expense' R58 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R2.htm | Interest expense | -314000000 | 314000000 | -293000000 | 293000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R2.htm | Earnings before taxes | 1128000000 | 1128000000 | 535000000 | 535000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Tax (provision) benefit | -240000000 | 240000000 | -133000000 | 133000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R2.htm | Net earnings attributable to Ball Corporation | 912000000 | 912000000 | 4008000000 | 4008000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Total basic earnings per share (in dollars per share) | 3.33 | 3.33 | 13.12 | 13.12 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Total diluted earnings per share (in dollars per share) | 3.3 | 3.3 | 13 | 13 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic (in shares) | 274263000 | 274263000 | 305459000 | 305459000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted (in shares) | 275972000 | 275972000 | 308206000 | 308206000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 1212000000 | 1212000000 | 885000000 | 885000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R4.htm | Receivables, net | 2606000000 | 2606000000 | 2166000000 | 2166000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories, net | 2013000000 | 2013000000 | 1477000000 | 1477000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 6113000000 | 6113000000 | 4841000000 | 4841000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R4.htm | Property, plant and equipment, net | 6656000000 | 6656000000 | 6173000000 | 6173000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 4379000000 | 4379000000 | 4172000000 | 4172000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 19524000000 | 19524000000 | 17628000000 | 17628000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 4452000000 | 4452000000 | 3418000000 | 3418000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 5487000000 | 5487000000 | 4847000000 | 4847000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R4.htm | Total liabilities | 14103000000 | 14103000000 | 11698000000 | 11698000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total Ball Corporation shareholders' equity | 5421000000 | 5421000000 | 5862000000 | 5862000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Cash provided by (used in) operating activities | 1262000000 | 1262000000 |  | 115000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Cash provided by (used in) investing activities | -656000000 | -656000000 |  | 5003000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Cash provided by (used in) financing activities | -344000000 | -344000000 |  | -4790000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Capital expenditures | -474000000 | 474000000 |  | 484000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | ball:DepreciationAndAmortizationForSegment | R6.htm | Depreciation and amortization | 622000000 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / company extension tag, matched by printed label / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R110.htm | Share based compensation expense | 28000000 | 28000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R110.htm 'Stock-Based Compensation Programs - Compensation expense (Details)' (MetaLinks.json presentation) |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Common stock dividends | -220000000 | 220000000 |  | 244000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Acquisitions of treasury stock | -1321000000 | 1321000000 |  | 1712000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-017410 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R82.htm | Interest paid during period | 317000000 | 317000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R82.htm 'Debt and Interest Costs - FV, Maturities, etc. (Details)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R86.htm | Net income tax payments | 374000000 | 374000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R86.htm 'Taxes on Income - Foreign subsidiaries (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R4.htm | Short-term debt and current portion of long-term debt + Long-term debt | 7012000000 | 7012000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1162 tags across all 116 R pages, face and notes) of 0001104659-26-017410; HAND REVIEW: 6 label candidate(s) incl. custom tags: us-gaap:CommonStockSharesIssued 'Common Stock, Shares, Issued / Common stock, shares issued /' R5; dei:EntityCommonStockSharesOutstanding 'Entity Common Stock, Shares Outstanding / Indicate number of' R1; us-gaap:SharesOutstanding 'Shares, Outstanding / Balance at end of period (in shares) /' R8; us-gaap:WeightedAverageNumberDilutedSharesOutstandingAdjustment 'Weighted Average Number of Shares Outstanding, Diluted, Adju' R111; us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding 'Weighted Average Number of Shares Outstanding, Diluted / Dil' R111,R2; us-gaap:WeightedAverageNumberOfSharesOutstandingBasic 'Weighted Average Number of Shares Outstanding, Basic / Basic' R111,R2 |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 7997000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Cost of sales (excluding depreciation and amortization)' on us-gaap:CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization = -6460300000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = -451300000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Total interest expense' on us-gaap:InterestExpense = -259700000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Earnings before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 345500000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Tax (provision) benefit' on us-gaap:IncomeTaxExpenseBenefit = -47000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Net earnings attributable to Ball Corporation' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 280900000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Total basic earnings per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.05 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Total diluted earnings per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.99 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 137300000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001104659-16-097390 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 140984000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 224000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 885400000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Inventories, net' on us-gaap:InventoryNet = 898400000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2184000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2685900000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 2176500000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Total assets' on us-gaap:Assets = 9777000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1500800000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2141600000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 8.516e+09 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001104659-16-097390 R4.htm prints 'Total Ball Corporation shareholders' equity' on us-gaap:StockholdersEquity = 1251300000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Total cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1006700000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -2720700000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1737100000 (FILING-CHECKED)
- capex: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -527900000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 285500000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001104659-16-097390 R6.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Common dividends' on us-gaap:PaymentsOfDividendsCommonStock = -71800000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001104659-16-097390 R6.htm prints 'Acquisitions of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -135500000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001104659-16-097390 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001104659-16-097390 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001558370-18-001345 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet =  (FILING-CHECKED)
- ppe_net: era 10-K 0001558370-20-001005 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 4470000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (ball:DepreciationAndAmortizationForSegment)

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 12 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:BALL); disagree on the mapped sample: 0/3
- cash_flow_investing: agree (R6 -656)
- cash_paid_for_income_taxes: agree (R86 'Net income tax payments' IncomeTaxesPaidNet 374)
- cash_paid_for_interest: disagree (R82 'Interest paid during period' is us-gaap:InterestPaid (includes capitalized interest); the data point is InterestPaidNet (net of capitalized, DQC_0065): combined)
- gross_profit: agree (R2 prints no gross profit line)
- interest_expense: agree (R2 'Interest expense' InterestExpenseDebt 314: gross charge)
- operating_expenses: agree (R2 prints no total opex and no gross profit line)
- operating_income: agree (R2 prints no operating income line; the lead ball:IncomeLossFromContinuingOperationsBeforeRestructuringAndOtherActivities (R58) is a segment measure)
- ppe_net: agree (R4 Property, plant and equipment, net 6,656)
- research_and_development: agree (no R&D line; leads are deferred-tax IPR&D and tax-credit rate items (R88, R61))
- sbc: agree (not on the R6 face; R110 'Share based compensation expense' AllocatedShareBasedCompensationExpense 28)
- shares_outstanding: agree (no CommonStockSharesOutstanding at the BS date (R4/R5 print issued shares; the equity roll uses SharesOutstanding; cover count never used): not_presented)
- total_debt: agree (R4 short-term debt and current portion 21 + long-term debt 6,991 = 7,012 (USD millions); finance-lease rule checked: R80 long-term debt includes 'Finance lease obligations' and short-term debt includes 'Short-term finance leases': leases already inside, nothing added)
