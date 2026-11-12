# WSO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-082486 (CIK 0000105016, filed 2026-02-27): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001193125-16-484870 (CIK 0000105016, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001193125-18-067229 (CIK 0000105016, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001193125-21-060167 (CIK 0000105016, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000105016.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R2.htm | Revenues | 7239290000 | 7239290000 | 7618317000 | 7618317000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of sales | 5208826000 | 5208826000 | 5573604000 | 5573604000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross profit | 2030464000 | 2030464000 | 2044713000 | 2044713000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (959 tags across all 93 R pages, face and notes) of 0001193125-26-082486; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 1337882000 | 1337882000 | 1293439000 | 1293439000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (959 tags across all 93 R pages, face and notes) of 0001193125-26-082486; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income | 720347000 | 720347000 | 781775000 | 781775000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (959 tags across all 93 R pages, face and notes) of 0001193125-26-082486; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income taxes | 737676000 | 737676000 | 802644000 | 802644000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income taxes | 150088000 | 150088000 | 166904000 | 166904000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income attributable to Watsco, Inc. | 496994000 | 496994000 | 536286000 | 536286000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic | 12.27 | 12.27 | 13.34 | 13.34 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted | 12.25 | 12.25 | 13.3 | 13.3 | Y | FILING-CHECKED | accn 0001193125-26-082486 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R57.htm | Earnings Per Share - Schedule of Basic and Diluted Earnings per Common Share (Detail) |  | 37835054 |  |  |  | FILING-CHECKED | not on the face statement; shown in R57.htm 'Earnings Per Share - Schedule of Basic and Diluted Earnings per Common Share (De' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R57.htm | Earnings Per Share - Schedule of Basic and Diluted Earnings per Common Share (Detail) |  | 37899859 |  |  |  | FILING-CHECKED | not on the face statement; shown in R57.htm 'Earnings Per Share - Schedule of Basic and Diluted Earnings per Common Share (De' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 433283000 | 433283000 | 526271000 | 526271000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable, net | 796181000 | 796181000 | 877935000 | 877935000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories, net | 1386317000 | 1386317000 | 1385436000 | 1385436000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 2954506000 | 2954506000 | 3079981000 | 3079981000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property and equipment, net | 136012000 | 136012000 | 140535000 | 140535000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 462509000 | 462509000 | 451858000 | 451858000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 4414805000 | 4414805000 | 4479523000 | 4479523000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 350425000 | 350425000 | 490879000 | 490879000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 717742000 | 717742000 | 983901000 | 983901000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (959 tags across all 93 R pages, face and notes) of 0001193125-26-082486; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total Watsco, Inc. shareholders' equity | 2781376000 | 2781376000 | 2656990000 | 2656990000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 569613000 | 569613000 | 773102000 | 773102000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -98122000 | -98122000 | -290670000 | -290670000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -568116000 | -568116000 | -158530000 | -158530000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -34550000 | 34550000 | -30090000 | 30090000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 43752000 | 43752000 | 40822000 | 40822000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 35344000 | 35344000 | 35022000 | 35022000 | Y | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends on common stock | -473765000 | 473765000 | -423521000 | 423521000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation | R8.htm | Repurchases of common stock to satisfy employee withholding tax obligations | -3657000 | 3657000 | -39673000 | 39673000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-082486 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R92.htm | Supplemental Cash Flow Information (Detail) |  | 697000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Supplemental Cash Flow Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R67.htm | Income Taxes - Additional Information (Detail) |  | 164733000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R67.htm 'Income Taxes - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R4.htm | Current portion of lease liabilities + Total long-term obligations | 478788000 | 478788000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R5.htm | Common stock, shares outstanding | 44642861 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Revenues' on us-gaap:Revenues = 4113239000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 3105882000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1007357000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 670609000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 336748000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 331201000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 104677000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Net income attributable to Watsco, Inc.' on us-gaap:NetIncomeLoss = 172929000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 4.91 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-484870 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 4.9 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-484870 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-484870 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 35229000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 451079000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 673967000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1181265000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 62715000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 378310000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Total assets' on us-gaap:Assets = 1788442000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 145162000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 270301000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-484870 R4.htm prints 'Total Watsco, Inc. shareholders' equity' on us-gaap:StockholdersEquity = 957310000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 221383000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -22938000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -186320000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -23698000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 19117000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 12596000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-484870 R8.htm prints 'Dividends on Common and Class B common stock' on us-gaap:PaymentsOfDividendsCommonStock = -98532000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-484870 R8.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-484870 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-484870 R8.htm read; no row matched (auto)
- cfo: era 10-K 0001193125-18-067229 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 306520000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-067229 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -81308000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-067229 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -202145000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001193125-21-060167 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 7239290000 vs printed 7239290000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | mapped-sample | agree | page value 737676000 vs printed 737676000 |
| weighted_basic_shares | NOTE | agree | page value 37835054 vs API 37835054 |
| weighted_diluted_shares | NOTE | agree | page value 37899859 vs API 37899859 |
| total_assets | mapped-sample | agree | page value 4414805000 vs printed 4414805000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 697000 vs API 697000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 164733000 vs API 164733000 |
| total_debt | component sum | agree | page value 478788000 vs printed 478788000 |
| shares_outstanding | component sum | agree | page value 44642861 vs printed 44642861 |
