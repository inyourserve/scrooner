# WMG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001319161-25-000034 (CIK 0001319161, filed 2025-11-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R8.htm
- 10-K 0001564590-15-011396 (CIK 0001319161, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R7.htm
- 10-K 0001564590-17-024528 (CIK 0001319161, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R7.htm
- 10-K 0001319161-23-000036 (CIK 0001319161, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R8.htm
- companyfacts CIK0001319161.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 6707000000 | 6707000000 | 6426000000 | 6426000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenue | -3632000000 | 3632000000 | -3355000000 | 3355000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (951 tags across all 97 R pages, face and notes) of 0001319161-25-000034; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | -6013000000 | 6013000000 | -5635000000 | 5635000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | -1889000000 | 1889000000 | -1879000000 | 1879000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (951 tags across all 97 R pages, face and notes) of 0001319161-25-000034; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsTaxCreditCarryforwards 'Tax attribute carryforwards / Deferred Tax Assets, Tax Credi' R78; us-gaap:IncomeTaxReconciliationTaxCredits 'Federal research and development credits / Tax benefit relat' R77,R76 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 694000000 | 694000000 | 823000000 | 823000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense, net | -162000000 | -162000000 | -161000000 | -161000000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 490000000 | 490000000 | 601000000 | 601000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -120000000 | 120000000 | -123000000 | 123000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Warner Music Group Corp. | 365000000 | 365000000 | 435000000 | 435000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 0.69 |  | 0.83 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 0.69 |  | 0.83 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 145128000 |  | 140882000 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 145128000 |  | 140882000 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R5.htm period ..2025-09-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and equivalents | 532000000 | 532000000 | 694000000 | 694000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances of $27 million and $26 million | 1340000000 | 1340000000 | 1255000000 | 1255000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 62000000 | 62000000 | 99000000 | 99000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2770000000 | 2770000000 | 2643000000 | 2643000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 441000000 | 441000000 | 481000000 | 481000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2061000000 | 2061000000 | 2021000000 | 2021000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9829000000 | 9829000000 | 9155000000 | 9155000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 257000000 | 257000000 | 289000000 | 289000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4201000000 | 4201000000 | 3897000000 | 3897000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 9072000000 | 9072000000 | 8480000000 | 8480000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Warner Music Group Corp. equity | 647000000 | 647000000 | 518000000 | 518000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R3.htm period ..2025-09-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 678000000 | 678000000 | 754000000 | 754000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -340000000 | -340000000 | -311000000 | -311000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -497000000 | -497000000 | -396000000 | -396000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -139000000 | 139000000 | -116000000 | 116000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 376000000 | 376000000 | 327000000 | 327000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| sbc | mapped | us-gaap:EmployeeBenefitsAndShareBasedCompensationNoncash | R8.htm | Non-cash stock-based compensation expense | 54000000 | 54000000 | 52000000 | 52000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends paid | -383000000 | 383000000 | -361000000 | 361000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Common stock repurchased and retired | -16000000 | 16000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001319161-25-000034 R8.htm period ..2025-09-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R94.htm | Interest payments | 167000000 | 167000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R94.htm 'Additional Financial Information - Narrative (Details)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R94.htm | Income and withholding taxes paid | 181000000 | 181000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R94.htm 'Additional Financial Information - Narrative (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Acquisition corp. long-term debt | 4063000000 | 4063000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock outstanding (in shares) | 522286000 |  |  |  |  | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-09-30; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Revenues' on us-gaap:Revenues =  (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Cost of revenue' on us-gaap:CostOfRevenue =  (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses =  (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense =  (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss =  (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet =  (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Loss before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest =  (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Income tax (expense) benefit' on us-gaap:IncomeTaxExpenseBenefit =  (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-15-011396 R4.htm prints 'Net loss attributable to Warner Music Group Corp.' on us-gaap:NetIncomeLoss =  (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-15-011396 R4.htm read; no row matched (auto)
- diluted_eps: FY2015 10-K 0001564590-15-011396 R4.htm read; no row matched (auto)
- weighted_basic_shares: FY2015 10-K 0001564590-15-011396 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001564590-15-011396 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Cash and equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 246000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Accounts receivable, net of allowances of $56 million and $65 million' on us-gaap:AccountsReceivableNetCurrent = 349000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 42000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 879000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 220000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1632000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Total assets' on us-gaap:Assets = 5671000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 173000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1857000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 5432000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-15-011396 R2.htm prints 'Total Warner Music Group Corp. equity' on us-gaap:StockholdersEquity = 221000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-15-011396 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 159000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-15-011396 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -808000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-15-011396 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 511000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-15-011396 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -34000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-15-011396 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 258000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-15-011396 R7.htm prints 'Non-cash share-based compensation expense' on us-gaap:ShareBasedCompensation = 19000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-15-011396 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001564590-15-011396 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001564590-15-011396 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-15-011396 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001564590-17-024528 R4.htm prints 'Revenues' on us-gaap:Revenues =  (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001564590-17-024528 R4.htm prints 'Cost of revenue' on us-gaap:CostOfRevenue =  (FILING-CHECKED)
- cfo: era 10-K 0001564590-17-024528 R7.htm prints 'Net cash (used in) provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 535000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-17-024528 R7.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -126000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-17-024528 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -128000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001564590-17-024528 R7.htm read; no row matched (auto)
- capex: era 10-K 0001319161-23-000036 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -127000000 (FILING-CHECKED)
- sbc: era 10-K 0001319161-23-000036 R8.htm prints 'Non-cash stock-based compensation expense' on us-gaap:ShareBasedCompensation = 49000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: API missing (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 11 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:WMG); disagree on the mapped sample: 1/3
- basic_eps: agree (R5 basic EPS 0.69 for each class (two-class presentation, same value))
- cash_paid_for_income_taxes: agree (R94 'Income and withholding taxes paid' IncomeTaxesPaidNet 181)
- cash_paid_for_interest: agree (R94 'Interest payments' InterestPaidNet 167)
- gross_profit: agree (R5 prints no gross profit line)
- interest_expense: agree (R5 'Interest expense, net' = net line: combined)
- operating_expenses: agree (R5 'Total costs and expenses' CostsAndExpenses 6,013 includes cost of revenues: combined, never opex)
- research_and_development: agree (no R&D line; leads are tax credit items (R77, R78))
- sga_expense: agree (R5 SG&A 1,889)
- shares_outstanding: agree (R4 Class A 146,906,000 + Class B 375,380,000 = 522,286,000 at 2025-09-30)
- total_debt: disagree (R3 prints two debt lines: Acquisition corp. long-term debt 4,063 (LongTermDebtNoncurrent) + Asset-based long-term debt 302 (wmg:LongTermDebtExcludingCurrentMaturitiesAssetBased) = 4,365; FY1 4,014 + 0)
- weighted_basic_shares: disagree (R5 prints basic weighted shares per class: Class A 145,128,000 + Class B 375,380,000 = 520,508,000 (FY1 140,882,000 + 376,641,000 = 517,523,000); the machine kept Class A only)
