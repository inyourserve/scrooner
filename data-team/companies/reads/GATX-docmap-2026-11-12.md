# GATX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000040211-26-000018 (CIK 0000040211, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000040211-16-000064 (CIK 0000040211, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm
- 10-K 0000040211-25-000024 (CIK 0000040211, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000040211-17-000012 (CIK 0000040211, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm
- companyfacts CIK0000040211.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R77.htm | Revenues | 1740400000 | 1740400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R77.htm 'Investments in Affiliated Companies (Operating Results, Affiliates) (Details 4)' (MetaLinks.json presentation) |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:OperatingCostsAndExpenses 'Operating Costs and Expenses / Operating Costs and Expenses ' R130 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:CostsAndExpenses 'Total Expenses / Costs and Expenses / Total costs of sales a' R6; us-gaap:OperatingCostsAndExpenses 'Operating Costs and Expenses / Operating Costs and Expenses ' R130 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R130.htm | Selling, general and administrative | 252600000 | 252600000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R130.htm 'Financial Data of Busines Segments (Details)' (MetaLinks.json presentation) |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; label search over every tag in the filing (custom included) found no candidate |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; HAND REVIEW: 4 label candidate(s) incl. custom tags: gmt:NonoperatingIncomeResidualSharingIncome 'Residual sharing income / Nonoperating Income, Residual Shar' R130,R58; us-gaap:OtherNonoperatingIncomeExpense 'Other expense / Other Nonoperating Income (Expense) / Other ' R6,R92,R94; us-gaap:OtherOperatingIncome 'Other Operating Income / Other Operating Income / The total ' R6,R130; us-gaap:SegmentReportingReconcilingItemForOperatingProfitLossFromSegmentToConsolidatedLineItems 'Segment Reporting, Reconciling Item for Operating Profit (Lo' R130,R129 |
| interest_expense | mapped | us-gaap:InterestExpense | R79.htm | Interest expense, net | -391500000 | 391500000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R79.htm 'Investments in Affiliated Companies (Summarized Financial Data-RRPF) (Details 6)' (MetaLinks.json presentation) |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R6.htm | Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | 279100000 | 279100000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R6.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation) |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R79.htm | Income Taxes | -63100000 | 63100000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R79.htm 'Investments in Affiliated Companies (Summarized Financial Data-RRPF) (Details 6)' (MetaLinks.json presentation) |
| net_income | mapped | us-gaap:ProfitLoss | R5.htm | Net Income | 333300000 | 333300000 | 284200000 | 284200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R120.htm | Basic earnings per share (in dollars per share) | 9140000 | 9.14 |  |  | N (printed 9140000 vs API 9.14) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R120.htm | Diluted earnings per share (in dollars per share) | 9120000 | 9.12 |  |  | N (printed 9120000 vs API 9.12) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R120.htm | Denominator for basic earnings per share — weighted average shares | 35800000 | 35800000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R120.htm | Denominator for diluted earnings per share — adjusted weighted average and assumed conversion | 35900000 | 35900000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R120.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and Cash Equivalents | 743000000 | 743000000 | 401600000 | 401600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Receivables, net | 207200000 | 207200000 | 199100000 | 199100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:LineOfCreditFacilityCapacityAvailableForTradePurchases 'Line of Credit Facility, Capacity Available for Trade Purcha' R85,R87; us-gaap:OtherInventory 'Inventory / Other Inventory, Gross / Amount before valuation' R123 |
| current_assets | mapped | us-gaap:AssetsCurrent | R78.htm | Current assets | 521500000 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R78.htm 'Investments in Affiliated Companies (Balance Sheet, Affiliates) (Details 5)' (MetaLinks.json presentation) |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Net operating assets and facilities | 11410900000 | 11410900000 | 10449700000 | 10449700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 126300000 | 126300000 | 114100000 | 114100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 17999500000 | 17999500000 | 12296500000 | 12296500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts Payable and Accrued Expenses | 318400000 | 318400000 | 217100000 | 217100000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R78.htm | Current liabilities | 883400000 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R78.htm 'Investments in Affiliated Companies (Balance Sheet, Affiliates) (Details 5)' (MetaLinks.json presentation) |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 14364400000 | 14364400000 | 9857600000 | 9857600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Equity | 2750500000 | 2750500000 | 2438900000 | 2438900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 648100000 | 648100000 | 602100000 | 602100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1016800000 | -1016800000 | -1416700000 | -1416700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used in) provided by financing activities | 4944800000 | 4944800000 | 770500000 | 770500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| capex | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1149 tags across all 132 R pages, face and notes) of 0000040211-26-000018; label search over every tag in the filing (custom included) found no candidate |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 452300000 | 452300000 | 421400000 | 421400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R7.htm | Share-based compensation expense | 25000000 | 25000000 | 23000000 | 23000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends | -89800000 | 89800000 | -84800000 | 84800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Stock repurchases | -65000000 | 65000000 | -21900000 | 21900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest Paid, Excluding Capitalized Interest, Operating Activity | 413200000 | 413200000 | 350100000 | 350100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000040211-26-000018 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R117.htm | Total | 14500000 | 14500000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R117.htm 'Income Taxes - Income taxes Paid (Details)' (MetaLinks.json presentation) |
| total_debt | mapped | us-gaap:LongTermDebt | R81.htm | Total debt principal | 12505600000 | 12505600000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R81.htm 'Investments in Affiliated Companies (Future Debt Maturities) (Details 8)' (MetaLinks.json presentation) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Outstanding shares (in shares) | 35400021 | 35400021 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0000040211-16-000064 statement not identified (auto)
- sga_expense: 10-K 0000040211-16-000064 statement not identified (auto)
- interest_expense: 10-K 0000040211-16-000064 statement not identified (auto)
- income_before_tax: 10-K 0000040211-16-000064 statement not identified (auto)
- income_tax_expense: 10-K 0000040211-16-000064 statement not identified (auto)
- net_income: 10-K 0000040211-16-000064 statement not identified (auto)
- basic_eps: 10-K 0000040211-16-000064 statement not identified (auto)
- diluted_eps: 10-K 0000040211-16-000064 statement not identified (auto)
- weighted_basic_shares: 10-K 0000040211-16-000064 statement not identified (auto)
- weighted_diluted_shares: 10-K 0000040211-16-000064 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 202400000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Rent and other receivables' on us-gaap:AccountsReceivableGrossCurrent = 69400000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000040211-16-000064 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Operating assets and facilities, net' on us-gaap:PropertyPlantAndEquipmentNet = 5698400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 79700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Assets' on us-gaap:Assets = 6894200000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Accounts Payable and Accrued Expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 170900000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000040211-16-000064 R2.htm read; no row matched (auto)
- total_liabilities: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 5614000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000040211-16-000064 R2.htm prints 'Total Shareholders’ Equity' on us-gaap:StockholdersEquity = 1280200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 5.343e+08 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -307600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -229000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Share-based Compensation' on us-gaap:ShareBasedCompensation = 11600000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Dividends' on us-gaap:PaymentsOfDividends = -68200000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000040211-16-000064 R5.htm prints 'Stock repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -125400000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000040211-16-000064 R5.htm read; no row matched (auto)
- net_income: 10-K 0000040211-25-000024 statement not identified (auto)
- cash_paid_for_interest: era 10-K 0000040211-17-000012 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
- basic_eps: N (printed 9140000 vs API 9.14) (us-gaap:EarningsPerShareBasic)
- diluted_eps: N (printed 9120000 vs API 9.12) (us-gaap:EarningsPerShareDiluted)
- current_assets: API missing (us-gaap:AssetsCurrent)
- current_liabilities: API missing (us-gaap:LiabilitiesCurrent)
