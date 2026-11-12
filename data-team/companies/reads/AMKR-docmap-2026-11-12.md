# AMKR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001047127-26-000014 (CIK 0001047127, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001047127-16-000049 (CIK 0001047127, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001047127-18-000009 (CIK 0001047127, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001047127-20-000006 (CIK 0001047127, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0001047127.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 6707981000 | 6707981000 | 6317692000 | 6317692000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 5769382000 | 5769382000 | 5384480000 | 5384480000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 938599000 | 938599000 | 933212000 | 933212000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 471214000 | 471214000 | 494757000 | 494757000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 304471000 | 304471000 | 331806000 | 331806000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 166743000 | 166743000 | 162951000 | 162951000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 467385000 | 467385000 | 438455000 | 438455000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 75444000 | 75444000 | 64945000 | 64945000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before taxes | 444619000 | 444619000 | 431016000 | 431016000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Total tax provision and effective tax rate | 68503000 | 68503000 | 75481000 | 75481000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Amkor | 373895000 | 373895000 | 354012000 | 354012000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 1.51 | 1.51 | 1.44 | 1.44 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 1.5 | 1.5 | 1.43 | 1.43 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 247082000 | 247082000 | 246344000 | 246344000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 248454000 | 248454000 | 247818000 | 247818000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1378347000 | 1378347000 | 1133553000 | 1133553000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowances of $1,028 and $1,318, respectively | 1354825000 | 1354825000 | 1055013000 | 1055013000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 437797000 | 437797000 | 310910000 | 310910000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 3884761000 | 3884761000 | 3073472000 | 3073472000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, plant and equipment, net | 3870808000 | 3870808000 | 3576148000 | 3576148000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 18003000 | 18003000 | 17947000 | 17947000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 8136309000 | 8136309000 | 6944328000 | 6944328000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Trade accounts payable | 912766000 | 912766000 | 712887000 | 712887000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1711972000 | 1711972000 | 1455275000 | 1455275000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3630022000 | 3630022000 | 2761163000 | 2761163000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Amkor stockholders’ equity | 4471106000 | 4471106000 | 4149545000 | 4149545000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1095606000 | 1095606000 | 1088868000 | 1088868000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -885044000 | -885044000 | -800324000 | -800324000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 98700000 | 98700000 | -260432000 | -260432000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Payments for property, plant and equipment | -904614000 | 904614000 | -743796000 | 743796000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 642008000 | 642008000 | 594663000 | 594663000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based compensation | 20099000 | 20099000 | 18371000 | 18371000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Payments of dividends | -81946000 | 81946000 | -178605000 | 178605000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1045 tags across all 106 R pages, face and notes) of 0001047127-26-000014; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 73598000 | 73598000 | 60263000 | 60263000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Income taxes | 75721000 | 75721000 | 82617000 | 82617000 | Y | FILING-CHECKED | accn 0001047127-26-000014 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings and current portion of long-term debt + Long-term debt | 1445246000 | 1445246000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 247303000 | 247303000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 2884603000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 2405338000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 479265000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 314426000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 232409000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 82017000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 164839000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 81407000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Income before taxes and equity in earnings of unconsolidated affiliate' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 67535000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 28035000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Net income attributable to Amkor' on us-gaap:NetIncomeLoss = 56812000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.24 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.24 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 236850000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047127-16-000049 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 237170000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 523172000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Accounts receivable, net of allowances of $3,158 and $1,377' on us-gaap:AccountsReceivableNetCurrent = 526143000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 238205000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1317480000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2579017000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 19443000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Total assets' on us-gaap:Assets = 4031300000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableCurrent = 434222000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1018184000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 2806167000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047127-16-000049 R4.htm prints 'Total Amkor stockholders’ equity' on us-gaap:StockholdersEquity = 1207883000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 577945000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -514362000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 9643000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Payments for property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -537975000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 494200000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 3852000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Subsidiary dividends paid to noncontrolling interest' on us-gaap:PaymentsOfDividendsMinorityInterest = -246000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Interest' on us-gaap:InterestPaid = 96227000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047127-16-000049 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 35084000 (FILING-CHECKED)
- revenue: era 10-K 0001047127-18-000009 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 4186497000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001047127-18-000009 R7.htm prints 'Interest' on us-gaap:InterestPaid = 83808000 (FILING-CHECKED)
- revenue: era 10-K 0001047127-20-000006 R2.htm prints 'Net sales' on us-gaap:Revenues = 4052650000 (FILING-CHECKED)
- ppe_net: era 10-K 0001047127-20-000006 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet =  (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cash_and_equivalents | mapped-sample | agree | page value 1378347000 vs printed 1378347000 |
| accounts_receivable | mapped-sample | agree | page value 1354825000 vs printed 1354825000 |
| cfo | mapped-sample | agree | page value 1095606000 vs printed 1095606000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | mapped-sample | agree | page value 73598000 vs printed 73598000 |
| total_debt | component sum | agree | page value 1594327000 vs printed 1594327000 |
