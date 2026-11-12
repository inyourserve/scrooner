# NYT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000071691-26-000011 (CIK 0000071691, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000071691-16-000023 (CIK 0000071691, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000071691-18-000004 (CIK 0000071691, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000071691-19-000003 (CIK 0000071691, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000071691.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 2824918000 | 2824918000 | 2585919000 | 2585919000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R5.htm | Cost of revenue (excluding depreciation and amortization) | 1389713000 | 1389713000 | 1309514000 | 1309514000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (976 tags across all 103 R pages, face and notes) of 0000071691-26-000011; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating costs | 2393361000 | 2393361000 | 2234823000 | 2234823000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 328064000 | 328064000 | 307930000 | 307930000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Product development | 264347000 | 264347000 | 248198000 | 248198000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating profit | 431557000 | 431557000 | 351096000 | 351096000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income and other, net | 38256000 | 38256000 | 36485000 | 36485000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 451256000 | 451256000 | 383423000 | 383423000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 107275000 | 107275000 | 89598000 | 89598000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to The New York Times Company common stockholders | 343981000 | 343981000 | 293825000 | 293825000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share attributable to The New York Times Company common stockholders (in USD per share) | 2.11 | 2.11 | 1.79 | 1.79 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share attributable to The New York Times Company common stockholders (in USD per share) | 2.09 | 2.09 | 1.77 | 1.77 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 163157000 | 163157000 | 164425000 | 164425000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 164943000 | 164943000 | 165802000 | 165802000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 255445000 | 255445000 | 199448000 | 199448000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable (net of allowances of $11,406 in 2025 and $12,118 in 2024) | 290823000 | 290823000 | 249530000 | 249530000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (976 tags across all 103 R pages, face and notes) of 0000071691-26-000011; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1028067000 | 1028067000 | 936322000 | 936322000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant and equipment, net | 462365000 | 462365000 | 488816000 | 488816000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 409212000 | 409212000 | 412173000 | 412173000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2997090000 | 2997090000 | 2841479000 | 2841479000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 135623000 | 135623000 | 123606000 | 123606000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 666695000 | 666695000 | 613529000 | 613529000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (976 tags across all 103 R pages, face and notes) of 0000071691-26-000011; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 2041363000 | 2041363000 | 1927209000 | 1927209000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 584489000 | 584489000 | 410512000 | 410512000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -221316000 | -221316000 | -306086000 | -306086000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -306139000 | -306139000 | -192715000 | -192715000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -33984000 | 33984000 | -29173000 | 29173000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 85007000 | 85007000 | 82936000 | 82936000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 74183000 | 74183000 | 67499000 | 67499000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -110363000 | 110363000 | -82855000 | 82855000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases | -165341000 | 165341000 | -85043000 | 85043000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest, net of capitalized interest | 111000 | 111000 | 716000 | 716000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income tax payments – net | 71946000 | 71946000 | 113091000 | 113091000 | Y | FILING-CHECKED | accn 0000071691-26-000011 R9.htm period ..2025-12-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (976 tags across all 103 R pages, face and notes) of 0000071691-26-000011; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R90.htm | Stockholders' Equity - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Stockholders' Equity - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1579215000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Total production costs' on us-gaap:CostOfGoodsSold = 617812000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Total operating costs' on us-gaap:CostsAndExpenses = 1393246000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Selling, general and administrative costs' on us-gaap:SellingGeneralAndAdministrativeExpense = 713837000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000071691-16-000023 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Operating profit' on us-gaap:OperatingIncomeLoss = 136585000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNet = 39050000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 96752000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Income tax expense/(benefit)' on us-gaap:IncomeTaxExpenseBenefit = 33910000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Net income attributable to The New York Times Company common stockholders' on us-gaap:NetIncomeLoss = 63246000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Net income (USD per share)' on us-gaap:EarningsPerShareBasic = 0.38 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Net income (USD per share)' on us-gaap:EarningsPerShareDiluted = 0.38 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 164390000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000071691-16-000023 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 166423000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 105776000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Accounts receivable (net of allowances of $13,485 in 2015 and $12,860 in 2014)' on us-gaap:AccountsReceivableNetCurrent = 207180000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 862532000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 632439000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 109085000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Total assets' on us-gaap:Assets = 2417690000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 96082000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 563585000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000071691-16-000023 R2.htm prints 'Total New York Times Company stockholders’ equity' on us-gaap:StockholdersEquity = 826751000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 175326000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Net cash (used in)/provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -30703000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -214211000 (FILING-CHECKED)
- capex: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -26965000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 61597000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 10588000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -26599000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -69293000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Interest, net of capitalized interest' on us-gaap:InterestPaidNet = 41449000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000071691-16-000023 R8.htm prints 'Income tax payment/(refunds) – net' on us-gaap:IncomeTaxesPaidNet = 21078000 (FILING-CHECKED)
- revenue: era 10-K 0000071691-18-000004 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1675639000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000071691-19-000003 R4.htm prints 'Total production costs' on us-gaap:CostOfGoodsSold = 654176000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 2393361000 vs printed 2393361000 |
| sga_expense | component sum | agree | page value 635148000 vs printed 635148000 |
| interest_expense | combined | agree | page value 38256000 vs printed 38256000 |
| net_income | mapped-sample | agree | page value 343981000 vs printed 343981000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 462365000 vs printed 462365000 |
| total_assets | mapped-sample | agree | page value 2997090000 vs printed 2997090000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| dividends_paid | mapped-sample | agree | page value -110363000 vs printed -110363000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | NOTE | agree | value 780724 read off its own R page (no companyfacts fact to compare) |
