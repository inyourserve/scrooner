# SNAP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001564408-26-000013 (CIK 0001564408, filed 2026-02-05): COVER R1.htm, CF R3.htm, IS R4.htm, CI R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0001564590-18-002721 (CIK 0001564408, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001564408-24-000019 (CIK 0001564408, era filing): COVER R1.htm, CF R3.htm, IS R4.htm, CI R5.htm, BS R6.htm, BSP R7.htm
- companyfacts CIK0001564408.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Revenue | 5931447000 | 5931447000 | 5361398000 | 5361398000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Cost of revenue | 2669575000 | 2669575000 | 2474237000 | 2474237000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (899 tags across all 96 R pages, face and notes) of 0001564408-26-000013; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total costs and expenses | 6463614000 | 6463614000 | 6148692000 | 6148692000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 979133000 | 979133000 | 919097000 | 919097000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 1793601000 | 1793601000 | 1691683000 | 1691683000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating loss | -532167000 | -532167000 | -787294000 | -787294000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R4.htm | Interest expense | -121998000 | 121998000 | -21552000 | 21552000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Loss before income taxes | -451136000 | -451136000 | -672226000 | -672226000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax benefit (expense) | -9353000 | 9353000 | -25630000 | 25630000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net loss | -460489000 | -460489000 | -697856000 | -697856000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (in usd per share) | -0.27 | -0.27 | -0.42 | -0.42 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (in usd per share) | -0.27 | -0.27 | -0.42 | -0.42 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 1694598000 | 1694598000 | 1659147000 | 1659147000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 1694598000 | 1694598000 | 1659147000 | 1659147000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 1030435000 | 1030435000 | 1046534000 | 1046534000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net of allowance | 1372237000 | 1372237000 | 1348472000 | 1348472000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (899 tags across all 96 R pages, face and notes) of 0001564408-26-000013; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 4584874000 | 4584874000 | 4906757000 | 4906757000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property and equipment, net | 578075000 | 578075000 | 489088000 | 489088000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1720769000 | 1720769000 | 1689785000 | 1689785000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 7677802000 | 7677802000 | 7936348000 | 7936348000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 219793000 | 219793000 | 173197000 | 173197000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1286868000 | 1286868000 | 1243548000 | 1243548000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 5396307000 | 5396307000 | 5485587000 | 5485587000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders’ equity | 2281495000 | 2281495000 | 2450761000 | 2450761000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R3.htm | Net cash provided by (used in) operating activities | 656170000 | 656170000 | 413480000 | 413480000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R3.htm | Net cash provided by (used in) investing activities | 173118000 | 173118000 | -717084000 | -717084000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R3.htm | Net cash provided by (used in) financing activities | -848125000 | -848125000 | -428624000 | -428624000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R3.htm | Purchases of property and equipment | -218981000 | 218981000 | -194826000 | 194826000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R3.htm | Depreciation and amortization | 163633000 | 163633000 | 158074000 | 158074000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R3.htm | Stock-based compensation | 1016825000 | 1016825000 | 1041023000 | 1041023000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (899 tags across all 96 R pages, face and notes) of 0001564408-26-000013; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R3.htm | Repurchases of Class A non-voting common stock | -750866000 | 750866000 | -311069000 | 311069000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R3.htm | Cash paid for interest | 65060000 | 65060000 | 10284000 | 10284000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R3.htm | Cash paid for income taxes, net | 26716000 | 26716000 | 24686000 | 24686000 | Y | FILING-CHECKED | accn 0001564408-26-000013 R3.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent | R6.htm | Short-term debt, net + Long-term debt, net | 3536829000 | 3536829000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, outstanding (in shares) | 3467776622 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- revenue: era 10-K 0001564590-18-002721 R4.htm prints 'Revenue' on us-gaap:Revenues = 824949000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-002721 R7.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -734667000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-002721 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1346739000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-002721 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 2265348000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001564590-18-002721 R7.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 6226000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564408-24-000019 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -22024000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 6463614000 vs printed 6463614000 |
| sga_expense | component sum | agree | page value 2000438000 vs printed 2000438000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | mapped-sample | agree | page value 4584874000 vs printed 4584874000 |
| ppe_net | mapped-sample | agree | page value 578075000 vs printed 578075000 |
| stockholders_equity | mapped-sample | agree | page value 2281495000 vs printed 2281495000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 3536829000 vs printed 3536829000 |
| shares_outstanding | component sum | agree | page value 3467776622 vs printed 3467776622 |
