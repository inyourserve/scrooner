# SAIL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0002030781-26-000003 (CIK 0002030781, filed 2026-03-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0002030781-26-000003 (CIK 0002030781, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- companyfacts CIK0002030781.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 1071416000 | 1071416000 | 861611000 | 861611000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenue | 380625000 | 380625000 | 305733000 | 305733000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 690791000 | 690791000 | 555878000 | 555878000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 998277000 | 998277000 | 744612000 | 744612000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 200470000 | 200470000 | 107979000 | 107979000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 222961000 | 222961000 | 169730000 | 169730000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -307486000 | -307486000 | -188734000 | -188734000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -24635000 | 24635000 | -186652000 | 186652000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -325999000 | -325999000 | -376629000 | -376629000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax benefit | 55945000 | -55945000 | 60799000 | -60799000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -270054000 | -270054000 | -315830000 | -315830000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net Loss per share attributable to common stockholders and Class B unitholders, basic (in dollars per share) | -0.54 | -0.54 | -12.91 | -12.91 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net Loss per share attributable to common stockholders and Class B unitholders, diluted (in dollars per share) | -0.54 | -0.54 | -12.91 | -12.91 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average shares and Class B Units outstanding, basic (in shares) | 544159000 | 544159000 | 83716000 | 83716000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average shares and Class B Units outstanding, diluted (in shares) | 544159000 | 544159000 | 83716000 | 83716000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R5.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 358144000 | 358144000 | 121293000 | 121293000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance | 335001000 | 335001000 | 254050000 | 254050000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (827 tags across all 86 R pages, face and notes) of 0002030781-26-000003; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 850695000 | 850695000 | 512382000 | 512382000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 35178000 | 35178000 | 22879000 | 22879000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5151668000 | 5151668000 | 5151668000 | 5151668000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7597561000 | 7597561000 | 7411916000 | 7411916000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 5824000 | 5824000 | 3515000 | 3515000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 643295000 | 643295000 | 574693000 | 574693000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 751330000 | 751330000 | 1804215000 | 1804215000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity / partners' deficit | 6846231000 | 6846231000 | -5588440000 | -5588440000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R3.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used in) operating activities | 70580000 | 70580000 | -106391000 | -106391000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -35556000 | -35556000 | -28944000 | -28944000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by financing activities | 201972000 | 201972000 | 41257000 | 41257000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchase of property and equipment | -5980000 | 5980000 | -5362000 | 5362000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization expense | 210774000 | 210774000 | 237248000 | 237248000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Equity-based compensation expense, net of amounts capitalized | 254872000 | 254872000 | 31714000 | 31714000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (827 tags across all 86 R pages, face and notes) of 0002030781-26-000003; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfEquity | R7.htm | Repurchase of units | 0 | 0 | -6172000 | 6172000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 37069000 | 37069000 | 152171000 | 152171000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Total cash paid during the period for income taxes | 6892000 | 6892000 | 12948000 | 12948000 | Y | FILING-CHECKED | accn 0002030781-26-000003 R7.htm period ..2026-01-31 |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Long-term debt, net | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock outstanding (in shares) | 563781636 | 563781636 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-01-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0002030781-26-000003 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 358144000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| sga_expense | component sum | agree | page value 775316000 vs printed 775316000 |
| basic_eps | mapped-sample | agree | page value -0.54 vs printed -0.54 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 35178000 vs printed 35178000 |
| goodwill | mapped-sample | agree | page value 5151668000 vs printed 5151668000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | mapped-sample | agree | page value 37069000 vs printed 37069000 |
| total_debt | component sum | agree | page value 0 vs printed 0 |
