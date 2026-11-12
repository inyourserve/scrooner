# AES document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000874761-26-000063 (CIK 0000874761, filed 2026-03-02): COVER R1.htm, BS R3.htm, IS R4.htm, BSP R5.htm, CI R6.htm, CF R8.htm
- 10-K 0000874761-16-000077 (CIK 0000874761, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R10.htm
- companyfacts CIK0000874761.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Revenues | 12233000000 | 12233000000 | 12278000000 | 12278000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of Product and Service Sold | 10022000000 | 10022000000 | 9964000000 | 9964000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Operating margin | 2211000000 | 2211000000 | 2314000000 | 2314000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (2538 tags across all 185 R pages, face and notes) of 0000874761-26-000063; no face row matched |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative expenses | -241000000 | 241000000 | -288000000 | 288000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (2538 tags across all 185 R pages, face and notes) of 0000874761-26-000063; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (2538 tags across all 185 R pages, face and notes) of 0000874761-26-000063; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | -1407000000 | 1407000000 | -1485000000 | 1485000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R4.htm | INCOME FROM CONTINUING OPERATIONS BEFORE TAXES AND EQUITY IN EARNINGS OF AFFILIATES | 75000000 | 75000000 | 894000000 | 894000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax benefit (expense) | 181000000 | -181000000 | -59000000 | 59000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | NET INCOME ATTRIBUTABLE TO THE AES CORPORATION | 910000000 | 910000000 | 1679000000 | 1679000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | NET INCOME AVAILABLE TO THE AES CORPORATION COMMON STOCKHOLDERS | 1.26 | 1.26 | 2.38 | 2.38 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | NET INCOME AVAILABLE TO THE AES CORPORATION COMMON STOCKHOLDERS | 1.26 | 1.26 | 2.36 | 2.36 | Y | FILING-CHECKED | accn 0000874761-26-000063 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R169.htm | Earnings Per Share (Schedule of Earnings Per Share, Basic and Diluted) (Details) |  | 712000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R169.htm 'Earnings Per Share (Schedule of Earnings Per Share, Basic and Diluted) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R169.htm | Earnings Per Share (Schedule of Earnings Per Share, Basic and Diluted) (Details) |  | 714000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R169.htm 'Earnings Per Share (Schedule of Earnings Per Share, Basic and Diluted) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1382000000 | 1382000000 | 1524000000 | 1524000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance of $39 and $52, respectively | 1683000000 | 1683000000 | 1646000000 | 1646000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 612000000 | 612000000 | 593000000 | 593000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 6502000000 | 6502000000 | 6831000000 | 6831000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, Plant and Equipment, Net, Total | 37818000000 | 37818000000 | 33166000000 | 33166000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 342000000 | 342000000 | 345000000 | 345000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 51768000000 | 51768000000 | 47406000000 | 47406000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 1980000000 | 1980000000 | 1654000000 | 1654000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 8492000000 | 8492000000 | 8571000000 | 8571000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (2538 tags across all 185 R pages, face and notes) of 0000874761-26-000063; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total AES Corporation stockholders’ equity | 4063000000 | 4063000000 | 3644000000 | 3644000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 4306000000 | 4306000000 | 2752000000 | 2752000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -6210000000 | -6210000000 | -7700000000 | -7700000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 1975000000 | 1975000000 | 4963000000 | 4963000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -5929000000 | 5929000000 | -7392000000 | 7392000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation, amortization, and accretion of AROs | 1457000000 | 1457000000 | 1264000000 | 1264000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R145.htm | Share-Based Compensation (Stock Option Compensation Expense) (Details) |  | 14000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R145.htm 'Share-Based Compensation (Stock Option Compensation Expense) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid on AES common stock | -501000000 | 501000000 | -483000000 | 483000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (2538 tags across all 185 R pages, face and notes) of 0000874761-26-000063; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash payments for interest, net of amounts capitalized | 1210000000 | 1210000000 | 1268000000 | 1268000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash payments for income taxes, net of refunds (see Note 24) | 227000000 | 227000000 | 345000000 | 345000000 | Y | FILING-CHECKED | accn 0000874761-26-000063 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R108.htm | Debt (Non-Recourse Debt Carrying Amounts and Terms) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R108.htm 'Debt (Non-Recourse Debt Carrying Amounts and Terms) (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R183.htm | Accounting Changes and Error Corrections (Details) |  | 712201777 |  |  |  | FILING-CHECKED | not on the face statement; shown in R183.htm 'Accounting Changes and Error Corrections (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000874761-16-000077 R4.htm prints 'Total revenue' on us-gaap:ElectricUtilityRevenue = 14963000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000874761-16-000077 R4.htm prints 'Total cost of sales' on us-gaap:CostOfGoodsSoldElectric = -12097000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000874761-16-000077 R4.htm prints 'Operating margin' on us-gaap:GrossProfit = 2866000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000874761-16-000077 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = -196000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000874761-16-000077 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -1436000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000874761-16-000077 R4.htm prints 'INCOME FROM CONTINUING OPERATIONS BEFORE TAXES AND EQUITY IN EARNINGS OF AFFILIA' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1122000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000874761-16-000077 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -465000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000874761-16-000077 R4.htm prints 'NET INCOME ATTRIBUTABLE TO THE AES CORPORATION' on us-gaap:NetIncomeLoss = 306000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000874761-16-000077 R4.htm prints 'NET INCOME ATTRIBUTABLE TO THE AES CORPORATION COMMON STOCKHOLDERS' on us-gaap:EarningsPerShareBasic = 0.45 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000874761-16-000077 R4.htm prints 'NET INCOME ATTRIBUTABLE TO THE AES CORPORATION COMMON STOCKHOLDERS' on us-gaap:EarningsPerShareDiluted = 0.44 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000874761-16-000077 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000874761-16-000077 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1262000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $95 and $96, resp' on us-gaap:AccountsReceivableNetCurrent = 2473000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 675000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 6866000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 22816000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1157000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000874761-16-000077 R2.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 36850000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1721000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 6950000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000874761-16-000077 R2.htm prints 'Total AES Corporation stockholders’ equity' on us-gaap:StockholdersEquity = 3149000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2134000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -2366000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 28000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -2308000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 1144000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000874761-16-000077 R10.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Dividends paid on AES common stock' on us-gaap:PaymentsOfDividendsCommonStock = -276000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Cash payments for interest, net of amounts capitalized' on us-gaap:InterestPaidNet = 1265000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000874761-16-000077 R10.htm prints 'Cash payments for income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 388000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| weighted_basic_shares | NOTE | agree | page value 712000000 vs API 712000000 |
| weighted_diluted_shares | NOTE | agree | page value 714000000 vs API 714000000 |
| inventory | mapped-sample | agree | page value 612000000 vs printed 612000000 |
| ppe_net | mapped-sample | agree | page value 37818000000 vs printed 37818000000 |
| total_assets | mapped-sample | agree | page value 51768000000 vs printed 51768000000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | combined | agree | page value 1457000000 vs printed 1457000000 |
| sbc | NOTE | agree | page value 14000000 vs API 14000000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | value 10500000000 read off its own R page (no companyfacts fact to compare) |
| shares_outstanding | NOTE | agree | page value 712201777 vs API 712201777 |
