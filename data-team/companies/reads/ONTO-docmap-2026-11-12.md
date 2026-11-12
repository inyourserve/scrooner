# ONTO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-066937 (CIK 0000704532, filed 2026-02-24): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001564590-16-013119 (CIK 0000704532, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001564590-18-003134 (CIK 0000704532, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001564590-19-004083 (CIK 0000704532, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0000704532.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Revenue | 1005263000 | 1005263000 | 987321000 | 987321000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R2.htm | Cost of revenue | 505493000 | 505493000 | 472013000 | 472013000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross profit | 499770000 | 499770000 | 515308000 | 515308000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R2.htm | Total operating expenses | 366843000 | 366843000 | 328205000 | 328205000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R2.htm | General and administrative | 107077000 | 107077000 | 79855000 | 79855000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R2.htm | Research and development | 131978000 | 131978000 | 113860000 | 113860000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income (loss) | 132927000 | 132927000 | 187103000 | 187103000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R2.htm | Interest income, net | 34971000 | 34971000 | 33489000 | 33489000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income (loss) before provision (benefit) for income taxes | 162902000 | 162902000 | 220447000 | 220447000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision (benefit) for income taxes | 26143000 | 26143000 | 18777000 | 18777000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income | 136759000 | 136759000 | 201670000 | 201670000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic | 2.78 | 2.78 | 4.09 | 4.09 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted | 2.78 | 2.78 | 4.06 | 4.06 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic | 49123000 | 49123000 | 49343000 | 49343000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted | 49273000 | 49273000 | 49660000 | 49660000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R2.htm period ..2026-01-03 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 346119000 | 346119000 | 212945000 | 212945000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable, less allowance of $2,585 at December 28, 2024 and $2,659 at December 30, 2023 | 268932000 | 268932000 | 308142000 | 308142000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories | 298264000 | 298264000 | 286979000 | 286979000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 1268035000 | 1268035000 | 1477522000 | 1477522000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property, plant and equipment, net | 127184000 | 127184000 | 123868000 | 123868000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 644015000 | 644015000 | 329980000 | 329980000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 2367741000 | 2367741000 | 2117091000 | 2117091000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 107685000 | 107685000 | 56261000 | 56261000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 218946000 | 218946000 | 170089000 | 170089000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| total_liabilities | mapped | us-gaap:Liabilities | R4.htm | Total liabilities | 267094000 | 267094000 | 191209000 | 191209000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total stockholders’ equity | 2100647000 | 2100647000 | 1925882000 | 1925882000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R4.htm period ..2026-01-03 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash and cash equivalents provided by operating activities | 328315000 | 328315000 | 245676000 | 245676000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash and cash equivalents provided by (used in) investing activities | -121568000 | -121568000 | -226547000 | -226547000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash and cash equivalents provided by (used in) financing activities | -75150000 | -75150000 | -35673000 | -35673000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Purchases of property, plant and equipment | -28513000 | 28513000 | -31903000 | 31903000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R6.htm | Depreciation + Amortization of intangibles | 60439000 | 60439000 | 62309000 | 62309000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Share-based compensation | 27617000 | 27617000 | 28577000 | 28577000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| dividends_paid | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (864 tags across all 101 R pages, face and notes) of 0001193125-26-066937; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Purchases of common stock | -75015000 | 75015000 | -25069000 | 25069000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| cash_paid_for_interest | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (864 tags across all 101 R pages, face and notes) of 0001193125-26-066937; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R6.htm | Income taxes paid (received), net | 36039000 | 36039000 | 35505000 | 35505000 | Y | FILING-CHECKED | accn 0001193125-26-066937 R6.htm period ..2026-01-03 |
| total_debt | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (864 tags across all 101 R pages, face and notes) of 0001193125-26-066937; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Common stock, shares outstanding | 49702000 | 49702000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-01-03; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Total net revenues' on us-gaap:SalesRevenueNet = 187367000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Total costs of net revenues' on us-gaap:CostOfGoodsAndServicesSold = 97700000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 89667000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 84694000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013119 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 22444000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 32701000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Income (loss) from operations' on us-gaap:OperatingIncomeLoss = 4973000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -289000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 5568000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Provision for (benefit from) income taxes' on us-gaap:IncomeTaxExpenseBenefit = 2663000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Net income (loss)' on us-gaap:NetIncomeLoss = 2905000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.12 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.12 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 24059000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013119 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 24375000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 38154000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Accounts receivable, net of allowances of $150 and $253, respectively' on us-gaap:AccountsReceivableNetCurrent = 37832000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 47749000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 178114000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 44493000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 9415000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Total assets' on us-gaap:Assets = 235540000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 11675000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 45211000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 48212000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013119 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 187328000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1571000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 1951000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 220000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1846000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 9075000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 6248000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1721000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013119 R7.htm prints 'Cash paid (refund) for income taxes, net' on us-gaap:IncomeTaxesPaidNet = -826000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-003134 R4.htm prints 'Total net revenues' on us-gaap:SalesRevenueNet = 258621000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-003134 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 20603000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-003134 R7.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -6690000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-003134 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -25558000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001564590-19-004083 R4.htm prints 'Total costs of net revenues' on us-gaap:CostOfGoodsAndServicesSold = 140429000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001564590-19-004083 R4.htm prints 'Total costs of net revenues' on us-gaap:CostOfGoodsAndServicesSold = 140429000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564590-19-004083 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -331000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564590-19-004083 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -331000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001564590-19-004083 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 110951000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 1005263000 vs printed 1005263000 |
| sga_expense | component sum | agree | page value 177032000 vs printed 177032000 |
| research_and_development | mapped-sample | agree | page value 131978000 vs printed 131978000 |
| interest_expense | combined | agree | page value 34971000 vs printed 34971000 |
| total_assets | mapped-sample | agree | page value 2367741000 vs printed 2367741000 |
| current_liabilities | mapped-sample | agree | page value 218946000 vs printed 218946000 |
| depreciation_and_amortization | component sum | agree | page value 60439000 vs printed 60439000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
