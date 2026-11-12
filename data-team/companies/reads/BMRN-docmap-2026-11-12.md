# BMRN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001048477-26-000004 (CIK 0001048477, filed 2026-02-26): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0001564590-16-013653 (CIK 0001048477, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-18-003114 (CIK 0001048477, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001048477-24-000016 (CIK 0001048477, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001048477.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Total revenues | 3221253000 | 3221253000 | 2853915000 | 2853915000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 717442000 | 717442000 | 580235000 | 580235000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (968 tags across all 109 R pages, face and notes) of 0001048477-26-000004; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 2811775000 | 2811775000 | 2369701000 | 2369701000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 1153017000 | 1153017000 | 1009025000 | 1009025000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 921930000 | 921930000 | 747184000 | 747184000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | INCOME FROM OPERATIONS | 409478000 | 409478000 | 484214000 | 484214000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -10899000 | 10899000 | -12666000 | 12666000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME BEFORE INCOME TAXES | 482480000 | 482480000 | 541763000 | 541763000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 133579000 | 133579000 | 114904000 | 114904000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME | 348901000 | 348901000 | 426859000 | 426859000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | EARNINGS PER SHARE, BASIC (in dollars per share) | 1.82 | 1.82 | 2.25 | 2.25 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | EARNINGS PER SHARE, DILUTED (in dollars per share) | 1.8 | 1.8 | 2.21 | 2.21 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted-average common shares outstanding, basic (in shares) | 191787000 | 191787000 | 190027000 | 190027000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted average common shares outstanding, diluted (in shares) | 197394000 | 197394000 | 196708000 | 196708000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 1311679000 | 1311679000 | 942842000 | 942842000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net | 908214000 | 908214000 | 660535000 | 660535000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventory | 1298883000 | 1298883000 | 1232653000 | 1232653000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 3953490000 | 3953490000 | 3232427000 | 3232427000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 952508000 | 952508000 | 1043041000 | 1043041000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 196199000 | 196199000 | 196199000 | 196199000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 7594022000 | 7594022000 | 6988940000 | 6988940000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R6.htm | Accounts payable and accrued liabilities | 759031000 | 759031000 | 606988000 | 606988000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 759031000 | 759031000 | 606988000 | 606988000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 1507023000 | 1507023000 | 1330950000 | 1330950000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders’ equity | 6086999000 | 6086999000 | 5657990000 | 5657990000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 827994000 | 827994000 | 572841000 | 572841000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -414242000 | -414242000 | 136491000 | 136491000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -42394000 | -42394000 | -526447000 | -526447000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment | -103038000 | 103038000 | -85424000 | 85424000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 79557000 | 79557000 | 96426000 | 96426000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 181409000 | 181409000 | 201571000 | 201571000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (968 tags across all 109 R pages, face and notes) of 0001048477-26-000004; no face row matched |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (968 tags across all 109 R pages, face and notes) of 0001048477-26-000004; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 7245000 | 7245000 | 10361000 | 10361000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid for income taxes | 96205000 | 96205000 | 57269000 | 57269000 | Y | FILING-CHECKED | accn 0001048477-26-000004 R9.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:DebtInstrumentCarryingAmount | R74.htm | DEBT - Narrative (Details) |  | 600000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'DEBT - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 192300101 | 192300101 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Total revenues' on us-gaap:Revenues = 889895000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Cost of sales (excludes amortization of intangible assets)' on us-gaap:CostOfRevenue = 152008000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 1000597000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 402271000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 634806000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013653 R4.htm prints 'LOSS FROM OPERATIONS' on us-gaap:OperatingIncomeLoss = -110702000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -38244000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013653 R4.htm prints 'LOSS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -154724000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013653 R4.htm prints 'Provision for (benefit from) income taxes' on us-gaap:IncomeTaxExpenseBenefit = 17075000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013653 R4.htm prints 'NET LOSS' on us-gaap:NetIncomeLoss = -171799000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013653 R4.htm prints 'NET LOSS PER SHARE, BASIC AND DILUTED' on us-gaap:EarningsPerShareBasicAndDiluted = -1.07 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013653 R4.htm prints 'NET LOSS PER SHARE, BASIC AND DILUTED' on us-gaap:EarningsPerShareBasicAndDiluted = -1.07 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013653 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013653 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 397040000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Accounts receivable, net (allowance for doubtful accounts: $93 and $490, at Dece' on us-gaap:AccountsReceivableNetCurrent = 164959000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 271683000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1089639000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 704207000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 197039000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Total assets' on us-gaap:Assets = 3729368000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 392511000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 445457000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1328521000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013653 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 2400847000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -221689000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1179598000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 927913000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -227653000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Depreciation and amortization expense' on us-gaap:DepreciationDepletionAndAmortization = 47187000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 111525000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Cash paid for interest, net of interest capitalized into fixed assets' on us-gaap:InterestPaidNet = 9307000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013653 R8.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 16084000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-003114 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1313646000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-003114 R8.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -8757000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-003114 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -305459000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-003114 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 507145000 (FILING-CHECKED)
- interest_expense: era 10-K 0001048477-24-000016 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -17335000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 2811775000 vs printed 2811775000 |
| weighted_diluted_shares | mapped-sample | agree | page value 197394000 vs printed 197394000 |
| accounts_receivable | mapped-sample | agree | page value 908214000 vs printed 908214000 |
| current_assets | mapped-sample | agree | page value 3953490000 vs printed 3953490000 |
| current_liabilities | mapped-sample | agree | page value 759031000 vs printed 759031000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | page value 600000000 vs API 600000000 |
