# AKAM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001086222-26-000022 (CIK 0001086222, filed 2026-02-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001086222-16-000245 (CIK 0001086222, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001086222-18-000052 (CIK 0001086222, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001086222-24-000040 (CIK 0001086222, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001086222.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R5.htm | Revenue | 4208175000 | 4208175000 | 3991168000 | 3991168000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue (exclusive of amortization of acquired intangible assets shown below) | 1727513000 | 1727513000 | 1620793000 | 1620793000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (935 tags across all 116 R pages, face and notes) of 0001086222-26-000022; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and operating expenses | 3641231000 | 3641231000 | 3457757000 | 3457757000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 656739000 | 656739000 | 621785000 | 621785000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 513560000 | 513560000 | 470876000 | 470876000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 566944000 | 566944000 | 533411000 | 533411000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -30759000 | 30759000 | -27117000 | 27117000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before provision for income taxes | 602405000 | 602405000 | 587013000 | 587013000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | -150374000 | 150374000 | -82095000 | 82095000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 452031000 | 452031000 | 504918000 | 504918000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 3.11 | 3.11 | 3.34 | 3.34 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 3.07 | 3.07 | 3.27 | 3.27 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 145402000 | 145402000 | 151392000 | 151392000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 147023000 | 147023000 | 154346000 | 154346000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 930231000 | 930231000 | 517707000 | 517707000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of reserves of $7,706 and $3,522 at December 31, 2025 and 2024, respectively | 793666000 | 793666000 | 727687000 | 727687000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (935 tags across all 116 R pages, face and notes) of 0001086222-26-000022; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2286680000 | 2286680000 | 2578097000 | 2578097000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| ppe_net | mapped | akam:PropertyPlantAndEquipmentAndCapitalizedSoftwareNet | R3.htm | Property and equipment, net | 2333462000 |  | 1995071000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 3206525000 | 3206525000 | 3151077000 | 3151077000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 11479643000 | 11479643000 | 10368785000 | 10368785000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 125054000 | 125054000 | 130447000 | 130447000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 967518000 | 967518000 | 2091323000 | 2091323000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 6502272000 | 6502272000 | 5490428000 | 5490428000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 4977371000 | 4977371000 | 4878357000 | 4878357000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1518765000 | 1518765000 | 1519171000 | 1519171000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -540743000 | -540743000 | -798679000 | -798679000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) provided by financing activities | -588036000 | -588036000 | -679635000 | -679635000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -507786000 | 507786000 | -390433000 | 390433000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 708611000 | 708611000 | 648410000 | 648410000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 459402000 | 459402000 | 393378000 | 393378000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (935 tags across all 116 R pages, face and notes) of 0001086222-26-000022; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -799963000 | 799963000 | -557468000 | 557468000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest expense | 23293000 | 23293000 | 20420000 | 20420000 | Y | FILING-CHECKED | accn 0001086222-26-000022 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R112.htm | Income Taxes - Schedule of Income Taxes Paid (Details) |  | 143546000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R112.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | mapped | us-gaap:LongTermDebt | R83.htm | Debt- Schedule of Convertible Senior Notes (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R83.htm 'Debt- Schedule of Convertible Senior Notes (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 144711094 | 144711094 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Revenue' on us-gaap:Revenues = 2197448000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Cost of revenue (exclusive of amortization of acquired intangible assets shown b' on us-gaap:CostOfRevenue = 725620000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Total costs and operating expenses' on us-gaap:CostsAndExpenses = 1731298000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001086222-16-000245 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 388265000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 148591000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 466150000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -18525000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 456624000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 135218000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 321406000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.8 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.78 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 178391000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001086222-16-000245 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 180415000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 289473000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Accounts receivable, net of reserves of $7,364 and $9,023 at December 31, 2015 a' on us-gaap:AccountsReceivableNetCurrent = 380399000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1253188000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Property and equipment, net' on akam:PropertyPlantAndEquipmentAndCapitalizedSoftwareNet = 753180000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1150244000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Total assets' on us-gaap:Assets = 4187925000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 61982000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 332440000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1067047000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001086222-16-000245 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 3120878000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 764151000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Net cash used in by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -435564000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -267728000 (FILING-CHECKED)
- capex: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -311676000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 299563000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 126677000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -302606000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001086222-16-000245 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001086222-16-000245 R7.htm prints 'Cash paid for income taxes, net of refunds received in the year ended December 3' on us-gaap:IncomeTaxesPaid = 75033000 (FILING-CHECKED)
- revenue: era 10-K 0001086222-18-000052 R4.htm prints 'Revenue' on us-gaap:Revenues = 2502996000 (FILING-CHECKED)
- interest_expense: era 10-K 0001086222-24-000040 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -17709000 (FILING-CHECKED)

## Mismatches (printed vs API)
- ppe_net: API missing (akam:PropertyPlantAndEquipmentAndCapitalizedSoftwareNet)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 3641231000 vs printed 3641231000 |
| sga_expense | mapped-sample | agree | page value 656739000 vs printed 656739000 |
| weighted_basic_shares | mapped-sample | agree | page value 145402000 vs printed 145402000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -540743000 vs printed -540743000 |
| sbc | mapped-sample | agree | page value 459402000 vs printed 459402000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 143546000 vs API 143546000 |
| total_debt | NOTE | agree | value 4105355000 read off its own R page (no companyfacts fact to compare) |
