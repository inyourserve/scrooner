# HST document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001070750-26-000054 (CIK 0001070750, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001564590-16-012990 (CIK 0001070750, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001564590-18-003330 (CIK 0001070750, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001070750-24-000081 (CIK 0001070750, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001070750.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 6114000000 | 6114000000 | 5684000000 | 5684000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Expenses | 906000000 |  | 849000000 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1053 tags across all 95 R pages, face and notes) of 0001070750-26-000054; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating costs and expenses | 5259000000 | 5259000000 | 4809000000 | 4809000000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | Corporate and other expenses | 124000000 | 124000000 | 123000000 | 123000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1053 tags across all 95 R pages, face and notes) of 0001070750-26-000054; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R73; us-gaap:IncomeTaxReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R73 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | OPERATING PROFIT | 855000000 | 855000000 | 875000000 | 875000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -235000000 | 235000000 | -215000000 | 215000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | INCOME BEFORE INCOME TAXES | 818000000 | 818000000 | 721000000 | 721000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | -42000000 | 42000000 | -14000000 | 14000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME ATTRIBUTABLE TO HOST HOTELS & RESORTS, INC. | 765000000 | 765000000 | 697000000 | 697000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per common share (in dollars per share) | 1.11 | 1.11 | 0.99 | 0.99 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per common share (in dollars per share) | 1.1 | 1.1 | 0.99 | 0.99 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R54.htm | Basic weighted average shares outstanding (in shares) | 691400000 | 691400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R54.htm 'Summary of Significant Accounting Policies - Summary of Host Inc. Earnings Per C' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R54.htm | Diluted weighted average shares outstanding (in shares) | 694100000 | 694100000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R54.htm 'Summary of Significant Accounting Policies - Summary of Host Inc. Earnings Per C' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 768000000 | 768000000 | 554000000 | 554000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndNotesReceivableNet | R3.htm | Notes receivable | 114000000 | 114000000 | 79000000 | 79000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1053 tags across all 95 R pages, face and notes) of 0001070750-26-000054; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:IncreaseDecreaseInInventoriesAndOtherOperatingAssets 'Decrease in inventory for units sold / Increase (Decrease) i' R8,R15; us-gaap:IncreaseDecreaseInInventoryForLongTermContractsOrPrograms 'Payments for inventory costs / Payments for inventory costs ' R8,R15 |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1053 tags across all 95 R pages, face and notes) of 0001070750-26-000054; label search over every tag in the filing (custom included) found no candidate |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 10636000000 | 10636000000 | 10906000000 | 10906000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1053 tags across all 95 R pages, face and notes) of 0001070750-26-000054; label search over every tag in the filing (custom included) found no candidate |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 13049000000 | 13049000000 | 13048000000 | 13048000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 355000000 | 355000000 | 351000000 | 351000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1053 tags across all 95 R pages, face and notes) of 0001070750-26-000054; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:LineOfCredit 'Credit facility, including the term loans of $999 and $998, ' R3,R10,R11 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 6317000000 | 6317000000 | 6271000000 | 6271000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total equity of Host Hotels & Resorts, Inc. stockholders | 6558000000 | 6558000000 | 6609000000 | 6609000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1510000000 | 1510000000 | 1498000000 | 1498000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -507000000 | -507000000 | -2040000000 | -2040000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -868000000 | -868000000 | -13000000 | -13000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsForCapitalImprovements | R8.htm | Return on investment | -282000000 | 282000000 | -260000000 | 260000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 795000000 | 795000000 | 762000000 | 762000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Non-cash stock-based compensation expense | 26000000 | 26000000 | 24000000 | 24000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends on common stock | -623000000 | 623000000 | -737000000 | 737000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Common stock repurchases | -205000000 | 205000000 | -107000000 | 107000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001070750-26-000054 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R65.htm | Interest paid | 241000000 | 241000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R65.htm 'Debt - Reconciliation between Interest Expense and Cash Interest Paid (Detail)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R74.htm | Total cash taxes | 11400000 | 11400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R74.htm 'Income Taxes - Cash Taxes Activity For Continuing Operations (Detail)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:SeniorNotes | R3.htm | Senior notes | 3986000000 | 3986000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 687800000 | 687800000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Total revenues' on us-gaap:Revenues = 5387000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-012990 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Total operating costs and expenses' on us-gaap:CostsAndExpenses = 4737000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Corporate and other expenses' on us-gaap:GeneralAndAdministrativeExpense = 94000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-012990 R4.htm prints 'OPERATING PROFIT' on us-gaap:OperatingIncomeLoss = 650000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -234000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-012990 R4.htm prints 'INCOME BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 580000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -9000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-012990 R4.htm prints 'NET INCOME ATTRIBUTABLE TO REPORTING ENTITY' on us-gaap:NetIncomeLoss = 558000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Basic earnings per common share/unit' on us-gaap:EarningsPerShareBasic = 0.74 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-012990 R4.htm prints 'Diluted earnings per common share/unit' on us-gaap:EarningsPerShareDiluted = 0.74 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-012990 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-012990 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-16-012990 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 239000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-012990 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001564590-16-012990 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 10661000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-012990 R2.htm prints 'Total assets' on us-gaap:Assets = 11784000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-012990 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 243000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-012990 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 4559000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-012990 R2.htm prints 'Total equity of Host Hotels & Resorts, Inc. stockholders' on us-gaap:StockholdersEquity = 7064000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1171000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -736000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -865000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Renewals and replacements' on us-gaap:PaymentsToAcquireProductiveAssets = -388000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 716000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Stock compensation expense' on us-gaap:ShareBasedCompensation = 11000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Dividends on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -646000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-012990 R7.htm prints 'Common stock repurchase' on us-gaap:PaymentsForRepurchaseOfCommonStock = -675000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-012990 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-012990 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001564590-18-003330 R4.htm prints 'Total revenues' on us-gaap:Revenues = 5387000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-003330 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -267000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-003330 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -402000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001564590-18-003330 R7.htm read; no row matched (auto)
- interest_expense: era 10-K 0001070750-24-000081 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -191000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 15 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:HST); disagree on the mapped sample: 1/3
- capex: disagree (R8 prints two capital expenditure lines under 'Capital expenditures:': Renewals and replacements 362 (PaymentsToAcquireOtherProductiveAssets) + Return on investment 282 (PaymentsForCapitalImprovements) = 644; API 362 + 282 = 644)
- cash_and_equivalents: agree (R3 Cash and cash equivalents 768)
- cash_paid_for_income_taxes: agree (R74 'Total cash taxes' IncomeTaxesPaidNet 11.4)
- cash_paid_for_interest: agree (R65 'Interest paid' InterestPaidNet 241)
- current_assets: agree (R3 is unclassified: no total current assets)
- current_liabilities: agree (R3 is unclassified: no total current liabilities; the lead is the credit facility line)
- goodwill: agree (R3 prints no goodwill line)
- gross_profit: agree (R5 prints no gross profit line (hotel REIT))
- inventory: agree (R3 prints no inventory line; leads are cash-flow changes (R8, R15))
- operating_expenses: disagree (Dhairya 2026-11-13 (blind-grade key_error): R5 'Total operating costs and expenses' 5,259 = the departmental cost lines (CostOfGoodsAndServicesSold, product/service members) 4,364 + the lines after them, which tie: Depreciation and amortization 795 + Corporate and other expenses 124 + Net gain on insurance settlements -24 = 895 (FY1 762 + 123 - 110 = 775); companyfacts the same)
- research_and_development: agree (no R&D line; leads are tax credit reconciliation items (R73))
- total_debt: disagree (R3 prints 'Total debt' (DebtAndCapitalLeaseObligations) 5,077 = senior notes 3,986 + credit facility 996 + mortgage and other debt 95; the machine summed senior notes only)
- total_liabilities: agree (R3 Total liabilities 6,317)
- weighted_basic_shares: agree (R54 691.4 million shares)
- weighted_diluted_shares: agree (R54 694.1 million shares)
