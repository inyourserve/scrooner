# WTRG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000078128-26-000050 (CIK 0000078128, filed 2026-02-26): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R9.htm
- 10-K 0001562762-16-000347 (CIK 0000078128, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R11.htm
- 10-K 0001562762-23-000064 (CIK 0000078128, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R9.htm
- 10-K 0000078128-19-000002 (CIK 0000078128, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R11.htm
- companyfacts CIK0000078128.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Operating revenues | 2474615000 | 2474615000 | 2086113000 | 2086113000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total operating expenses | 1553664000 | 1553664000 | 1328445000 | 1328445000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 920951000 | 920951000 | 757668000 | 757668000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | 329081000 | 329081000 | 302467000 | 302467000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 619814000 | 619814000 | 573478000 | 573478000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense (benefit) | 3445000 | 3445000 | -21836000 | -21836000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 616369000 | 616369000 | 595314000 | 595314000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 2.2 | 2.2 | 2.17 | 2.17 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 2.2 | 2.2 | 2.17 | 2.17 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 280054000 | 280054000 | 273914000 | 273914000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 280619000 | 280619000 | 274421000 | 274421000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 34778000 | 34778000 | 9156000 | 9156000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net | 217191000 | 217191000 | 166522000 | 166522000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryRawMaterialsAndSupplies | R2.htm | Inventory - materials and supplies | 51767000 | 51767000 | 48619000 | 48619000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 610396000 | 610396000 | 485911000 | 485911000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Net property, plant and equipment | 14263682000 | 14263682000 | 13143476000 | 13143476000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 2348559000 | 2348559000 | 2340713000 | 2340713000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 19464845000 | 19464845000 | 18026554000 | 18026554000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 276080000 | 276080000 | 258615000 | 258615000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 764483000 | 764483000 | 974668000 | 974668000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 6857456000 | 6857456000 | 6198809000 | 6198809000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash flows from operating activities | 1010459000 | 1010459000 | 770343000 | 770343000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash flows used in investing activities | -1510744000 | -1510744000 | -1163281000 | -1163281000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash flows from financing activities | 525907000 | 525907000 | 397482000 | 397482000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| capex | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 417471000 | 417471000 | 369552000 | 369552000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 12855000 | 12855000 | 9785000 | 9785000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid on common stock | -373821000 | 373821000 | -346392000 | 346392000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common stock | -2284000 | 2284000 | -4048000 | 4048000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest, net of amounts capitalized | 310921000 | 310921000 | 275898000 | 275898000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Income taxes | 9080000 | 9080000 | 6698000 | 6698000 | Y | FILING-CHECKED | accn 0000078128-26-000050 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent+us-gaap:LongTermDebtCurrent | R2.htm | Long-term debt, excluding current portion, net of debt issuance costs and unamortized discount on debt + Current portion | 8131989000 | 8131989000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1037 tags across all 121 R pages, face and notes) of 0000078128-26-000050; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Operating revenues' on us-gaap:Revenues = 814204000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 493104000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 321100000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 76536000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Income (Loss) from Continuing Operations before Equity Method Investments, Incom' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 216752000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 14962000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Net income attributable to common shareholders' on us-gaap:NetIncomeLoss = 201790000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 1.14 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 1.14 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 176788000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001562762-16-000347 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 177517000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3229000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Accounts receivable and unbilled revenues, net' on us-gaap:AccountsReceivableNetCurrent = 99146000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Inventory, materials and supplies' on us-gaap:InventoryNet = 12414000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 128370000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 4688925000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 33866000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Total assets' on us-gaap:Assets = 5741038000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 56452000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 193199000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001562762-16-000347 R5.htm prints 'Total Aqua America stockholders' equity' on us-gaap:StockholdersEquity = 1725930000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Net cash flows from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 370794000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Net cash flows used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -394062000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Net cash flows used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 22359000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 128737000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 5860000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -121248000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -25247000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Interest, net of amounts capitalized' on us-gaap:InterestPaidNet = 70103000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001562762-16-000347 R11.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 6902000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001562762-23-000064 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 450908000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000078128-19-000002 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3627000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1553664000 vs printed 1553664000 |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -1510744000 vs printed -1510744000 |
| capex | not_presented | agree | none of the candidate elements in MetaLinks.json |
| dividends_paid | mapped-sample | agree | page value -373821000 vs printed -373821000 |
| cash_paid_for_income_taxes | mapped-sample | agree | page value 9080000 vs printed 9080000 |
| total_debt | component sum | agree | page value 8131989000 vs printed 8131989000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
