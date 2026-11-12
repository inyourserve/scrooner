# EHC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000785161-26-000081 (CIK 0000785161, filed 2026-02-26): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000785161-16-000117 (CIK 0000785161, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000785161-24-000009 (CIK 0000785161, era filing): COVER R1.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000785161-20-000011 (CIK 0000785161, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000785161.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net operating revenues | 5935200000 | 5935200000 | 5373200000 | 5373200000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (962 tags across all 104 R pages, face and notes) of 0000785161-26-000081; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (962 tags across all 104 R pages, face and notes) of 0000785161-26-000081; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 4882100000 | 4882100000 | 4508700000 | 4508700000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative expenses | 236200000 | 236200000 | 209200000 | 209200000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (962 tags across all 104 R pages, face and notes) of 0000785161-26-000081; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (962 tags across all 104 R pages, face and notes) of 0000785161-26-000081; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense and amortization of debt discounts and fees | 123200000 | 123200000 | 137400000 | 137400000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income tax expense | 953000000 | 953000000 | 749600000 | 749600000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income tax expense | 192900000 | 192900000 | 150200000 | 150200000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Encompass Health | 566200000 | 566200000 | 455700000 | 455700000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income (in dollars per share) | 5.62 | 5.62 | 4.53 | 4.53 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income (in dollars per share) | 5.54 | 5.54 | 4.46 | 4.46 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 100500000 | 100500000 | 99900000 | 99900000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 102200000 | 102200000 | 102200000 | 102200000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 72200000 | 72200000 | 85400000 | 85400000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Accounts receivable | 619200000 | 619200000 | 598800000 | 598800000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (962 tags across all 104 R pages, face and notes) of 0000785161-26-000081; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 905900000 | 905900000 | 886900000 | 886900000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property and equipment, net | 4.102e+09 | 4101600000 | 3643100000 | 3643100000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 1317600000 | 1317600000 | 1284000000 | 1284000000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 7089700000 | 7089700000 | 6534700000 | 6534700000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 178200000 | 178200000 | 171000000 | 171000000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 836400000 | 836400000 | 841000000 | 841000000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3813900000 | 3813900000 | 3685500000 | 3685500000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Encompass Health shareholders’ equity | 2438200000 | 2438200000 | 2067000000 | 2067000000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R9.htm | Net cash provided by operating activities | 1175600000 | 1175600000 | 1002800000 | 1002800000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -764600000 | -764600000 | -653300000 | -653300000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -431200000 | -431200000 | -330600000 | -330600000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R9.htm | Purchases of property, equipment, and intangible assets | -736400000 | 736400000 | -642500000 | 642500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 327900000 | 327900000 | 299600000 | 299600000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 56500000 | 56500000 | 48300000 | 48300000 | Y | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid on common stock | -71100000 | 71100000 | -62800000 | 62800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock, including fees and expenses | -158000000 | 158000000 | -31100000 | 31100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | -133100000 | 133100000 | -146800000 | 146800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000785161-26-000081 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R94.htm | Income Taxes - Schedule of Income Tax Paid (Details) |  | 124000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R94.htm 'Income Taxes - Schedule of Income Tax Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt + Long-term debt, net of current portion | 2.491e+09 | 2490800000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Consolidated Statements of Shareholders' Equity |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R7.htm 'Consolidated Statements of Shareholders' Equity' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Net operating revenues' on us-gaap:HealthCareOrganizationRevenue = 3162900000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 2569000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000785161-16-000117 R2.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 1.333e+08 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Interest expense and amortization of debt discounts and fees' on us-gaap:InterestAndDebtExpense = 142900000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Income from continuing operations before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 395600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Provision for income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 141900000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Net income attributable to HealthSouth' on us-gaap:NetIncomeLoss = 183100000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Net income' on us-gaap:EarningsPerShareBasic = 2.02 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Net income' on us-gaap:EarningsPerShareDiluted = 1.91 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 89400000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000785161-16-000117 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 101000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 61600000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $39.3 in 2015; $2' on us-gaap:AccountsReceivableNetCurrent = 410500000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 598700000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1310100000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1890100000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Total assets' on us-gaap:Assets = 4606100000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 61600000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 426400000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 3705700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000785161-16-000117 R4.htm prints 'Total HealthSouth shareholders' equity' on us-gaap:StockholdersEquity = 611400000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 484800000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1129800000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 639900000 (FILING-CHECKED)
- capex: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -128400000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 139700000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 26200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -77200000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Repurchase of common stock, including fees and expenses' on us-gaap:PaymentsForRepurchaseOfCommonStock = -45300000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Interest' on us-gaap:InterestPaid = -121400000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000785161-16-000117 R7.htm prints 'Income tax payments' on us-gaap:IncomeTaxesPaid = -16800000 (FILING-CHECKED)
- interest_expense: 10-K 0000785161-24-000009 statement not identified (auto)
- ppe_net: era 10-K 0000785161-20-000011 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1959300000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 4882100000 vs printed 4882100000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | mapped-sample | agree | page value 123200000 vs printed 123200000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | mapped-sample | agree | page value 3813900000 vs printed 3813900000 |
| cash_paid_for_interest | mapped-sample | agree | page value -133100000 vs printed -133100000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 124000000 vs API 124000000 |
| total_debt | component sum | agree | page value 2490800000 = printed 2.491e+09 at 4 significant digits; fy0_printed restored to the page value |
