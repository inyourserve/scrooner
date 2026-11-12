# TXRH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-021292 (CIK 0001289460, filed 2026-02-27): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001558370-16-003617 (CIK 0001289460, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R8.htm
- 10-K 0001558370-18-001026 (CIK 0001289460, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R8.htm
- companyfacts CIK0001289460.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Total revenue | 5878075000 | 5878075000 | 5373332000 | 5373332000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (744 tags across all 82 R pages, face and notes) of 0001104659-26-021292; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (744 tags across all 82 R pages, face and notes) of 0001104659-26-021292; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total costs and expenses | 5403335000 | 5403335000 | 4856813000 | 4856813000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 227328000 | 227328000 | 223264000 | 223264000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (744 tags across all 82 R pages, face and notes) of 0001104659-26-021292; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Income from operations | 474740000 | 474740000 | 516519000 | 516519000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R4.htm | Interest income, net | 3137000 | 3137000 | 6774000 | 6774000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before taxes | 480756000 | 480756000 | 524490000 | 524490000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | 66421000 | 66421000 | 80145000 | 80145000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R4.htm | Net income attributable to Texas Roadhouse, Inc. and subsidiaries | 405554000 | 405554000 | 433592000 | 433592000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 6.11 | 6.11 | 6.5 | 6.5 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 6.1 | 6.1 | 6.47 | 6.47 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 66324000 | 66324000 | 66752000 | 66752000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 66511000 | 66511000 | 67011000 | 67011000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R4.htm period ..2025-12-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 134709000 | 134709000 | 245225000 | 245225000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Receivables, net of allowance for doubtful accounts of $12 at December 30, 2025 and $7 at December 31, 2024 | 214511000 | 214511000 | 193170000 | 193170000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories, net | 45560000 | 45560000 | 40756000 | 40756000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 451476000 | 451476000 | 516568000 | 516568000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net of accumulated depreciation of $1,379,207 at December 30, 2025 and $1,223,064 at December 31 | 1803841000 | 1803841000 | 1617673000 | 1617673000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 242220000 | 242220000 | 169684000 | 169684000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 3549472000 | 3549472000 | 3190779000 | 3190779000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 163421000 | 163421000 | 144791000 | 144791000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 908837000 | 908837000 | 828130000 | 828130000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 2067770000 | 2067770000 | 1817056000 | 1817056000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total Texas Roadhouse, Inc. and subsidiaries stockholders' equity | 1460820000 | 1460820000 | 1358347000 | 1358347000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R2.htm period ..2025-12-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 730067000 | 730067000 | 753629000 | 753629000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -482814000 | -482814000 | -336901000 | -336901000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -357769000 | -357769000 | -275749000 | -275749000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures-property and equipment | -387996000 | 387996000 | -354341000 | 354341000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 206640000 | 206640000 | 178157000 | 178157000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 47765000 | 47765000 | 47055000 | 47055000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to shareholders | -180262000 | 180262000 | -162864000 | 162864000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of shares of common stock, including excise taxes as applicable | -150437000 | 150437000 | -80003000 | 80003000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | 981000 | 981000 | 891000 | 891000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid | 75094000 | 75094000 | 87333000 | 87333000 | Y | FILING-CHECKED | accn 0001104659-26-021292 R7.htm period ..2025-12-30 |
| total_debt | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (744 tags across all 82 R pages, face and notes) of 0001104659-26-021292; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 65943730 | 65943730 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 1807368000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 1662803000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001558370-16-003617 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 92336000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 144565000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 1959000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Income before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 144247000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 42986000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Net income attributable to Texas Roadhouse, Inc. and subsidiaries' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 96894000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.38 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.37 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 70032000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001558370-16-003617 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 70747000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 59334000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Receivables, net of allowance for doubtful accounts of $6 at December 29, 2015 a' on us-gaap:AccountsReceivableNetCurrent = 45421000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 15633000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 133813000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Property and equipment, net of accumulated depreciation of $395,886 at December ' on us-gaap:PropertyPlantAndEquipmentNet = 751288000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 116571000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Total assets' on us-gaap:Assets = 1032706000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 50996000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 256642000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 355524000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001558370-16-003617 R2.htm prints 'Total Texas Roadhouse, Inc. and subsidiaries stockholders' equity' on us-gaap:StockholdersEquity = 669662000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 227941000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -173203000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -81526000 (FILING-CHECKED)
- capex: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Capital expenditures-property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -173475000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 69694000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 22825000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -46176000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Repurchase of shares of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -11397000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Interest paid, net of amounts capitalized' on us-gaap:InterestPaidNet = 2321000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001558370-16-003617 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 39581000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-18-001026 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 2219531000 (FILING-CHECKED)
- interest_expense: era 10-K 0001558370-18-001026 R4.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 1577000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 5403335000 vs printed 5403335000 |
| sga_expense | mapped-sample | agree | page value 227328000 vs printed 227328000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value 3137000 vs printed 3137000 |
| basic_eps | mapped-sample | agree | page value 6.11 vs printed 6.11 |
| cash_paid_for_income_taxes | mapped-sample | agree | page value 75094000 vs printed 75094000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
