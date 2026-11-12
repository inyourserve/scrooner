# BSY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001031308-26-000007 (CIK 0001031308, filed 2026-02-26): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001628280-22-004474 (CIK 0001031308, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001628280-21-003727 (CIK 0001031308, era filing): COVER R1.htm, BS R2.htm, IS R3.htm, CI R4.htm, CF R6.htm, BSP R7.htm
- companyfacts CIK0001031308.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 1501779000 | 1501779000 | 1353095000 | 1353095000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenues | 277530000 | 277530000 | 257767000 | 257767000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1224249000 | 1224249000 | 1095328000 | 1095328000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 861628000 | 861628000 | 793178000 | 793178000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 217332000 | 217332000 | 210374000 | 210374000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 307576000 | 307576000 | 281247000 | 281247000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 362621000 | 362621000 | 302150000 | 302150000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense, net | -12435000 | -12435000 | -22044000 | -22044000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before income taxes | 350733000 | 350733000 | 293055000 | 293055000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | (Provision) benefit for income taxes | -72977000 | 72977000 | -58726000 | 58726000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Bentley Systems | 277861000 | 277861000 | 234787000 | 234787000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (USD per share) | 0.88 | 0.88 | 0.75 | 0.75 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (USD per share) | 0.85 | 0.85 | 0.72 | 0.72 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 314690707 | 314690707 | 314886615 | 314886615 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 333089213 | 333089213 | 333774167 | 333774167 | Y | FILING-CHECKED | accn 0001031308-26-000007 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 123278000 | 123278000 | 64009000 | 64009000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableGrossCurrent | R3.htm | Accounts receivable | 350299000 | 350299000 | 322862000 | 322862000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1036 tags across all 120 R pages, face and notes) of 0001031308-26-000007; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 539033000 | 539033000 | 442073000 | 442073000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 36031000 | 36031000 | 33798000 | 33798000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2482154000 | 2482154000 | 2367179000 | 2367179000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3555167000 | 3555167000 | 3399807000 | 3399807000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 26952000 | 26952000 | 16479000 | 16479000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 960210000 | 960210000 | 814334000 | 814334000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2365675000 | 2365675000 | 2358687000 | 2358687000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Bentley Systems stockholders’ equity | 1189413000 | 1189413000 | 1040987000 | 1040987000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 538464000 | 538464000 | 435292000 | 435292000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -112309000 | -112309000 | -143267000 | -143267000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -376298000 | -376298000 | -289850000 | -289850000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment and investment in capitalized software | -18255000 | 18255000 | -14046000 | 14046000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | bsy:DepreciationAmortizationAndImpairment | R9.htm | Depreciation, amortization, and impairment | 65880000 |  | 64608000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 72576000 | 72576000 | 74417000 | 74417000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Payments of dividends | -84963000 | 84963000 | -72115000 | 72115000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of Class B common stock under approved program | -125057000 | 125057000 | -64359000 | 64359000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 7846000 | 7846000 | 17202000 | 17202000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid for income taxes | 61488000 | 61488000 | 59745000 | 59745000 | Y | FILING-CHECKED | accn 0001031308-26-000007 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of long-term debt + Long-term debt | 1248912000 | 1248912000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock shares outstanding (in shares) | 302355097 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0001628280-22-004474 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 329337000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001628280-21-003727 R6.htm prints 'Interest paid' on us-gaap:InterestPaid = 8012000 (FILING-CHECKED)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (bsy:DepreciationAmortizationAndImpairment)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | mapped-sample | agree | page value 861628000 vs printed 861628000 |
| sga_expense | component sum | agree | page value 506875000 vs printed 506875000 |
| research_and_development | mapped-sample | agree | page value 307576000 vs printed 307576000 |
| interest_expense | combined | agree | page value -12435000 vs printed -12435000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_assets | mapped-sample | agree | page value 3555167000 vs printed 3555167000 |
| depreciation_and_amortization | combined | agree | page value 65880000 vs printed 65880000 |
| share_buybacks | mapped-sample | agree | page value -125057000 vs printed -125057000 |
| total_debt | component sum | agree | page value 1248912000 vs printed 1248912000 |
| shares_outstanding | component sum | agree | page value 302355097 vs printed 302355097 |
