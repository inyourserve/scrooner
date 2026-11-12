# CORT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-011091 (CIK 0001088856, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001088856-16-000011 (CIK 0001088856, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001564590-18-003840 (CIK 0001088856, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001628280-19-001879 (CIK 0001088856, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- companyfacts CIK0001088856.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Product revenue, net | 761407000 | 761407000 | 675040000 | 675040000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 12977000 | 12977000 | 10882000 | 10882000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (645 tags across all 60 R pages, face and notes) of 0001628280-26-011091; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 716610000 | 716610000 | 538089000 | 538089000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 448725000 | 448725000 | 280320000 | 280320000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 254908000 | 254908000 | 246887000 | 246887000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 44797000 | 44797000 | 136951000 | 136951000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (645 tags across all 60 R pages, face and notes) of 0001628280-26-011091; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 66463000 | 66463000 | 161493000 | 161493000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax benefit (expense) | 33189000 | -33189000 | -20284000 | 20284000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 99652000 | 99652000 | 141209000 | 141209000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in dollars per share) | 0.95 | 0.95 | 1.35 | 1.35 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in dollars per share) | 0.82 | 0.82 | 1.23 | 1.23 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 103862000 | 103862000 | 103232000 | 103232000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 119987000 | 119987000 | 113480000 | 113480000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 120495000 | 120495000 | 127665000 | 127665000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade receivables, net of allowances | 59786000 | 59786000 | 53976000 | 53976000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 12868000 | 12868000 | 12412000 | 12412000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 485464000 | 485464000 | 471602000 | 471602000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1890000 | 1890000 | 2689000 | 2689000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (645 tags across all 60 R pages, face and notes) of 0001628280-26-011091; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 836651000 | 836651000 | 840553000 | 840553000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 40444000 | 40444000 | 15376000 | 15376000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 166085000 | 166085000 | 140773000 | 140773000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 188846000 | 188846000 | 160964000 | 160964000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 647805000 | 647805000 | 679589000 | 679589000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 141996000 | 141996000 | 198295000 | 198295000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided (used in) by investing activities | 69758000 | 69758000 | -177604000 | -177604000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -220366000 | -220366000 | -28349000 | -28349000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -211000 | 211000 | -2172000 | 2172000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 1149000 | 1149000 | 795000 | 795000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 84500000 | 84500000 | 61354000 | 61354000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (645 tags across all 60 R pages, face and notes) of 0001628280-26-011091; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock in connection with Stock Repurchase Program | -172915000 | 172915000 | -15664000 | 15664000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (645 tags across all 60 R pages, face and notes) of 0001628280-26-011091; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid | 12969000 | 12969000 | 60267000 | 60267000 | Y | FILING-CHECKED | accn 0001628280-26-011091 R8.htm period ..2025-12-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (645 tags across all 60 R pages, face and notes) of 0001628280-26-011091; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares, outstanding (in shares) | 105966000 | 105966000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001088856-16-000011 R4.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 1361000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 53729000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 36949000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 15419000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Loss from operations' on us-gaap:OperatingIncomeLoss = -3443000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001088856-16-000011 R4.htm read; no row matched (auto)
- income_tax_expense: FY2015 10-K 0001088856-16-000011 R4.htm read; no row matched (auto)
- net_income: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Net loss and comprehensive loss' on us-gaap:NetIncomeLoss = -6408000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Basic and diluted net loss per share' on us-gaap:EarningsPerShareBasicAndDiluted = -0.06 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001088856-16-000011 R4.htm prints 'Basic and diluted net loss per share' on us-gaap:EarningsPerShareBasicAndDiluted = -0.06 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001088856-16-000011 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001088856-16-000011 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 40435000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Trade receivables' on us-gaap:AccountsReceivableNetCurrent = 6221000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 1682000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 48980000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Property and equipment, net of accumulated depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 98000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Total assets' on us-gaap:Assets = 51937000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1325000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 20876000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001088856-16-000011 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001088856-16-000011 R2.htm prints 'Total stockholders’ equity (deficit)' on us-gaap:StockholdersEquity = 18498000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001088856-16-000011 R6.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 3130000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001088856-16-000011 R6.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -17000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001088856-16-000011 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 13074000 (FILING-CHECKED)
- capex: FY2015 10-K 0001088856-16-000011 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -17000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001088856-16-000011 R6.htm prints 'Depreciation and amortization of property and equipment' on us-gaap:DepreciationDepletionAndAmortization = 155000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001088856-16-000011 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 6013000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001088856-16-000011 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001088856-16-000011 R6.htm read; no row matched (auto)
- cost_of_revenue: era 10-K 0001564590-18-003840 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 3554000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-003840 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 60935000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-003840 R6.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -73456000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-003840 R6.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -7953000 (FILING-CHECKED)
- income_before_tax: 10-K 0001628280-19-001879 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 716610000 vs printed 716610000 |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | mapped-sample | agree | page value 66463000 vs printed 66463000 |
| weighted_basic_shares | mapped-sample | agree | page value 103862000 vs printed 103862000 |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | mapped-sample | agree | page value 40444000 vs printed 40444000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | mapped-sample | agree | page value 105966000 vs printed 105966000 |
