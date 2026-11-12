# SMTC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000088941-26-000005 (CIK 0000088941, filed 2026-03-23): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001628280-16-013952 (CIK 0000088941, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001628280-18-003489 (CIK 0000088941, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000088941-22-000006 (CIK 0000088941, era filing): COVER R1.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000088941.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Total net sales | 1049975000 | 1049975000 | 909287000 | 909287000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Total cost of sales | 507831000 | 507831000 | 452759000 | 452759000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 542144000 | 542144000 | 456528000 | 456528000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses, net | 509579000 | 509579000 | 406594000 | 406594000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 221852000 | 221852000 | 222368000 | 222368000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Product development and engineering | 196348000 | 196348000 | 170908000 | 170908000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | 32565000 | 32565000 | 49934000 | 49934000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | -40618000 | 40618000 | -90067000 | 90067000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Loss before taxes and equity method income (loss) | -21180000 | -21180000 | -183361000 | -183361000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision (benefit) for income taxes | 19832000 | 19832000 | -22012000 | -22012000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net loss attributable to common stockholders | -40376000 | -40376000 | -161896000 | -161896000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | -0.46 | -0.46 | -2.26 | -2.26 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | -0.46 | -0.46 | -2.26 | -2.26 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 88374000 | 88374000 | 71606000 | 71606000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 88374000 | 88374000 | 71606000 | 71606000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R3.htm period ..2026-01-25 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 195179000 | 195179000 | 151743000 | 151743000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, less allowances of $7,976 and $5,248, respectively | 160552000 | 160552000 | 162523000 | 162523000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 195737000 | 195737000 | 163593000 | 163593000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 655120000 | 655120000 | 585461000 | 585461000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net of accumulated depreciation of $340,331 and $313,978, respectively | 109345000 | 109345000 | 126190000 | 126190000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 457925000 | 457925000 | 533091000 | 533091000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 1410337000 | 1410337000 | 1419264000 | 1419264000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R5.htm | Accounts payable | 84134000 | 84134000 | 59239000 | 59239000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 275936000 | 275936000 | 283034000 | 283034000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1143 tags across all 118 R pages, face and notes) of 0000088941-26-000005; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 549718000 | 549718000 | 542426000 | 542426000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R5.htm period ..2026-01-25 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by (used in) operating activities | 181168000 | 181168000 | 57987000 | 57987000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -38761000 | -38761000 | -11887000 | -11887000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) provided by financing activities | -101068000 | -101068000 | -21660000 | -21660000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property, plant and equipment | -9783000 | 9783000 | -7861000 | 7861000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| depreciation_and_amortization | mapped | smtc:DepreciationAndAmortizationExcludingRightOfUseAssets | R8.htm | Depreciation and amortization | 40807000 |  | 43499000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 57723000 | 57723000 | 68036000 | 68036000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1143 tags across all 118 R pages, face and notes) of 0000088941-26-000005; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfWarrants | R8.htm | Repurchase of warrants | -217761000 | 217761000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 16306000 | 16306000 | 72454000 | 72454000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes paid | 4076000 | 4076000 | 7979000 | 7979000 | Y | FILING-CHECKED | accn 0000088941-26-000005 R8.htm period ..2026-01-25 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Long term debt, less current portion | 491234000 | 491234000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding | 92668555 | 92668555 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-01-25; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 490219000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Cost of sales' on smtc:CostofGoodsSoldExcludingInventoryWritedown = 197109000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 293110000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Total operating costs and expenses' on us-gaap:OperatingExpenses = 263111000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 136151000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Product development and engineering' on us-gaap:ResearchAndDevelopmentExpense = 113737000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Operating income (loss)' on us-gaap:OperatingIncomeLoss = 29999000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -7819000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Income (loss) before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 20379000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Provision (benefit) for taxes' on us-gaap:IncomeTaxExpenseBenefit = 8882000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Net income (loss)' on us-gaap:ProfitLoss = 11497000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.18 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.17 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 65657000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001628280-16-013952 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 65961000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 211810000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Accounts receivable, less allowances of $7,793 at January 31, 2016 and $3,523 at' on us-gaap:AccountsReceivableNetCurrent = 44132000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 63875000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 341221000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Property, plant and equipment, net of accumulated depreciation of $143,782 at Ja' on us-gaap:PropertyPlantAndEquipmentNet = 101006000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 329703000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-16-013952 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 911517000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableTradeCurrent = 35486000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 103887000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-013952 R4.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 528051000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 102076000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -66827000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -53767000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Purchase of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -13026000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Depreciation, amortization and impairments' on smtc:DepreciationAmortizationAndImpairment = 48932000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 20468000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Repurchase of outstanding common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -57311000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 5732000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-013952 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 7924000 (FILING-CHECKED)
- revenue: era 10-K 0001628280-18-003489 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 587847000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001628280-18-003489 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 235876000 (FILING-CHECKED)
- interest_expense: 10-K 0000088941-22-000006 statement not identified (auto)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (smtc:DepreciationAndAmortizationExcludingRightOfUseAssets)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 1049975000 vs printed 1049975000 |
| total_assets | mapped-sample | agree | page value 1410337000 vs printed 1410337000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -38761000 vs printed -38761000 |
| capex | mapped-sample | agree | page value -9783000 vs printed -9783000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 491234000 vs printed 491234000 |
