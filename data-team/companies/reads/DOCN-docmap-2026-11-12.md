# DOCN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001582961-26-000019 (CIK 0001582961, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001582961-24-000031 (CIK 0001582961, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001582961-23-000009 (CIK 0001582961, era filing): COVER R1.htm, BS R3.htm, IS R4.htm, CI R5.htm, CF R7.htm, BSP R8.htm
- companyfacts CIK0001582961.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 901427000 | 901427000 | 780615000 | 780615000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 361835000 | 361835000 | 314672000 | 314672000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 539592000 | 539592000 | 465943000 | 465943000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 382603000 | 382603000 | 374936000 | 374936000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 138549000 | 138549000 | 160867000 | 160867000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 161621000 | 161621000 | 142499000 | 142499000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 156989000 | 156989000 | 91007000 | 91007000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -17940000 | 17940000 | -9113000 | 9113000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before taxes | 206662000 | 206662000 | 97699000 | 97699000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax benefit (expense) | 52600000 | -52600000 | -13207000 | 13207000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to common stockholders | 259262000 | 259262000 | 84492000 | 84492000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 2.83 | 2.83 | 0.92 | 0.92 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 2.52 | 2.52 | 0.89 | 0.89 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 91481000 | 91481000 | 91634000 | 91634000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 105343000 | 105343000 | 94503000 | 94503000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 254475000 | 254475000 | 428446000 | 428446000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, less allowance for credit losses of $6,374 and $5,940, respectively | 90908000 | 90908000 | 72486000 | 72486000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (909 tags across all 94 R pages, face and notes) of 0001582961-26-000019; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 426981000 | 426981000 | 541718000 | 541718000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 589094000 | 589094000 | 432544000 | 432544000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 348674000 | 348674000 | 348674000 | 348674000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1837705000 | 1837705000 | 1639015000 | 1639015000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 38836000 | 38836000 | 54565000 | 54565000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 619464000 | 619464000 | 220955000 | 220955000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1866395000 | 1866395000 | 1841970000 | 1841970000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ deficit | -28690000 | -28690000 | -202955000 | -202955000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 309604000 | 309604000 | 282725000 | 282725000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash (used in) provided by investing activities | -268285000 | -268285000 | -94805000 | -94805000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -216909000 | -216909000 | -76446000 | -76446000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures - property and equipment | -129086000 | 129086000 | -178167000 | 178167000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 137449000 | 137449000 | 130052000 | 130052000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 80315000 | 80315000 | 90545000 | 90545000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (909 tags across all 94 R pages, face and notes) of 0001582961-26-000019; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase and retirement of common stock including related costs | -82124000 | 82124000 | -59788000 | 59788000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 9688000 | 9688000 | 1048000 | 1048000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for taxes, net of refunds | 6282000 | 6282000 | 19667000 | 19667000 | Y | FILING-CHECKED | accn 0001582961-26-000019 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Debt, current + Debt, long-term | 1295762000 | 1295762000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 91947614 | 91947614 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001582961-24-000031 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -8945000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001582961-23-000009 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 140772000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| sga_expense | component sum | agree | page value 220982000 vs printed 220982000 |
| income_tax_expense | mapped-sample | agree | page value 52600000 vs printed 52600000 |
| cash_and_equivalents | mapped-sample | agree | page value 254475000 vs printed 254475000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | mapped-sample | agree | page value 9688000 vs printed 9688000 |
| total_debt | component sum | agree | page value 1426276000 vs printed 1426276000 |
