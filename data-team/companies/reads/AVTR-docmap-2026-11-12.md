# AVTR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-007118 (CIK 0001722482, filed 2026-02-11): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001722482-24-000012 (CIK 0001722482, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001722482-21-000040 (CIK 0001722482, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001722482.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Net sales | 6552200000 | 6552200000 | 6783600000 | 6783600000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 4412800000 | 4412800000 | 4504300000 | 4504300000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2139400000 | 2139400000 | 2279300000 | 2279300000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AssetImpairmentCharges+us-gaap:GainLossOnSaleOfBusiness | R5.htm | Selling, general and administrative expenses + Impairment charges + Gain on sale of business | 2385600000 | 2375400000 | 1194500000 | 2087700000 | N (printed 2385600000 vs API 2375400000) | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 1595500000 | 1595500000 | 1641100000 | 1641100000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1046 tags across all 122 R pages, face and notes) of 0001628280-26-007118; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating (loss) income | -246200000 | -246200000 | 1084800000 | 1084800000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense, net | -169800000 | 169800000 | -218800000 | 218800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | (Loss) income before income taxes | -441300000 | -441300000 | 853900000 | 853900000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -88900000 | 88900000 | -142400000 | 142400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:ProfitLoss | R5.htm | Net (loss) income | -5.302e+08 | -530200000 | 711500000 | 711500000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | -0.78 | -0.78 | 1.05 | 1.05 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted Basic (in dollars per share) | -0.78 | -0.78 | 1.04 | 1.04 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 680600000 | 680600000 | 679600000 | 679600000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 680600000 | 680600000 | 681900000 | 681900000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 365400000 | 365400000 | 2.619e+08 | 261900000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances of $29.6 and $30.2 | 1074600000 | 1074600000 | 1034500000 | 1034500000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 818200000 | 818200000 | 731500000 | 731500000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2451200000 | 2451200000 | 2146600000 | 2146600000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net (see note 10) | 766800000 | 766800000 | 708100000 | 708100000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill, net (see note 11) | 4986900000 | 4986900000 | 5539200000 | 5539200000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 11794700000 | 11794700000 | 12114500000 | 12114500000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 741700000 | 741700000 | 662800000 | 662800000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1378900000 | 1378900000 | 2007500000 | 2007500000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 6229700000 | 6229700000 | 6157800000 | 6157800000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 5565000000 | 5565000000 | 5956700000 | 5956700000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 623800000 | 623800000 | 840800000 | 840800000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -130500000 | -130500000 | 438900000 | 438900000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -409400000 | -409400000 | -1281200000 | -1281200000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -1.288e+08 | 128800000 | -148800000 | 148800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Amortization | 410200000 | 410200000 | 405500000 | 405500000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 46400000 | 46400000 | 46800000 | 46800000 | Y | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1046 tags across all 122 R pages, face and notes) of 0001628280-26-007118; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Payments for repurchase of common stock | -75100000 | 75100000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007118 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R70.htm | Supplemental disclosures of cash flow information (Details) |  | 161300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R70.htm 'Supplemental disclosures of cash flow information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R70.htm | Supplemental disclosures of cash flow information (Details) |  | 145000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R70.htm 'Supplemental disclosures of cash flow information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of debt + Debt, net of current portion | 3946300000 | 3946300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares, outstanding (in shares) | 682000000 | 682000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001722482-24-000012 R5.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -284800000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001722482-21-000040 R4.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 62300000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001722482-21-000040 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 286600000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001722482-21-000040 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
- operating_expenses: N (printed 2385600000 vs API 2375400000) (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AssetImpairmentCharges+us-gaap:GainLossOnSaleOfBusiness)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 2385600000 vs printed 2385600000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value -246200000 vs printed -246200000 |
| interest_expense | combined | agree | page value -169800000 vs printed -169800000 |
| weighted_diluted_shares | mapped-sample | agree | page value 680600000 vs printed 680600000 |
| capex | mapped-sample | agree | page value -128800000 = printed -1.288e+08 at 4 significant digits; fy0_printed restored to the page value |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 161300000 vs API 161300000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 145000000 vs API 145000000 |
| total_debt | component sum | agree | page value 3946300000 vs printed 3946300000 |
