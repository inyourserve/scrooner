# ENSG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001125376-26-000007 (CIK 0001125376, filed 2026-02-04): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0001125376-16-000142 (CIK 0001125376, filed FY2015 era): COVER R1.htm, BS R2.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001125376-22-000019 (CIK 0001125376, era filing): COVER R1.htm, IS R5.htm, CF R8.htm
- 10-K 0001125376-18-000028 (CIK 0001125376, era filing): COVER R1.htm, BS R2.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001125376.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | TOTAL REVENUE | 5057841000 | 5057841000 | 4260485000 | 4260485000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of services | 4019076000 | 4019076000 | 3376884000 | 3376884000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (869 tags across all 93 R pages, face and notes) of 0001125376-26-000007; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | TOTAL EXPENSES | 4632535000 | 4632535000 | 3902181000 | 3902181000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative expense | 269820000 | 269820000 | 225143000 | 225143000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (869 tags across all 93 R pages, face and notes) of 0001125376-26-000007; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 425306000 | 425306000 | 358304000 | 358304000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -7988000 | 7988000 | -8286000 | 8286000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 455622000 | 455622000 | 386094000 | 386094000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 111358000 | 111358000 | 87636000 | 87636000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME ATTRIBUTABLE TO THE ENSIGN GROUP, INC. | 343971000 | 343971000 | 297973000 | 297973000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 6 | 6 | 5.26 | 5.26 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 5.84 | 5.84 | 5.12 | 5.12 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 57306000 | 57306000 | 56655000 | 56655000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 58873000 | 58873000 | 58240000 | 58240000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 503881000 | 503881000 | 464598000 | 464598000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable—less allowance for doubtful accounts of $7,805 and $8,435 at December 31, 2025 and 2024, respectivel | 636985000 | 636985000 | 569897000 | 569897000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (869 tags across all 93 R pages, face and notes) of 0001125376-26-000007; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1272304000 | 1272304000 | 1157632000 | 1157632000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1696863000 | 1696863000 | 1291354000 | 1291354000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 97981000 | 97981000 | 97981000 | 97981000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 5462970000 | 5462970000 | 4669356000 | 4669356000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 97327000 | 97327000 | 98947000 | 98947000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 894346000 | 894346000 | 743428000 | 743428000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | TOTAL LIABILITIES | 3228146000 | 3228146000 | 2828928000 | 2828928000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Ensign Group, Inc. stockholders' equity | 2231725000 | 2231725000 | 1837111000 | 1837111000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | NET CASH PROVIDED BY OPERATING ACTIVITIES | 564270000 | 564270000 | 347186000 | 347186000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | NET CASH USED IN INVESTING ACTIVITIES | -513177000 | -513177000 | -390052000 | -390052000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | NET CASH USED IN FINANCING ACTIVITIES | -11810000 | -11810000 | -2162000 | -2162000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| capex | mapped | ensg:PaymentsToAcquirePropertyAndEquipment | R8.htm | Purchase of property and equipment | -193557000 |  | -158240000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 104327000 | 104327000 | 84138000 | 84138000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 48299000 | 48299000 | 36226000 | 36226000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends paid | -14410000 | 14410000 | -13671000 | 13671000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of shares of common stock (Note 19) | -20000000 | 20000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 6907000 | 6907000 | 7063000 | 7063000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes | 116202000 | 116202000 | 96337000 | 96337000 | Y | FILING-CHECKED | accn 0001125376-26-000007 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent | R3.htm | Current maturities of long-term debt | 4227000 | 4227000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common shares outstanding (in shares) | 58085000 | 58085000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Revenue' on us-gaap:SalesRevenueServicesNet = 1341826000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Cost of services (exclusive of facility rent, general and administrative and dep' on ensg:CostOfServicesExclusiveOfFacilityRentAndDepreciationAndAmortizationShownSeparatelyBelow = 1067694000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Total expenses' on us-gaap:CostsAndExpenses = 1248744000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001125376-16-000142 R4.htm prints 'General and administrative expense' on us-gaap:GeneralAndAdministrativeExpense = 64163000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 93082000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -2828000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 91099000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 35182000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Net income attributable to The Ensign Group, Inc.' on us-gaap:NetIncomeLoss = 55432000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Net income attributable to The Ensign Group, Inc.' on us-gaap:EarningsPerShareBasic = 1.1 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Net income attributable to The Ensign Group, Inc.' on us-gaap:EarningsPerShareDiluted = 1.06 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 50316000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001125376-16-000142 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 52210000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 41569000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Accounts receivable—less allowance for doubtful accounts of $30,308 and $20,438 ' on us-gaap:AccountsReceivableNetCurrent = 209026000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 294970000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 299633000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 40886000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Total assets' on us-gaap:Assets = 747759000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 36029000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 179866000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 320774000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001125376-16-000142 R2.htm prints 'Total Ensign Group, Inc. stockholders’ equity' on us-gaap:StockholdersEquity = 427324000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 33369000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -168538000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 126330000 (FILING-CHECKED)
- capex: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Purchase of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -60018000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Depreciation and amortization' on ensg:DepreciationAndAmortizationIncludingDiscontinuedOperations = 28111000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 6677000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -7494000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001125376-16-000142 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Interest' on us-gaap:InterestPaid = 2773000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001125376-16-000142 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 35490000 (FILING-CHECKED)
- revenue: era 10-K 0001125376-22-000019 R5.htm prints 'Total revenue' on us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax = 2627461000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001125376-18-000028 R4.htm prints 'Cost of services' on us-gaap:CostOfServices = 1497703000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001125376-18-000028 R6.htm prints 'Interest' on us-gaap:InterestPaid = 13284000 (FILING-CHECKED)

## Mismatches (printed vs API)
- capex: API missing (ensg:PaymentsToAcquirePropertyAndEquipment)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 5057841000 vs printed 5057841000 |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 4632535000 vs printed 4632535000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | mapped-sample | agree | page value 111358000 vs printed 111358000 |
| cash_and_equivalents | mapped-sample | agree | page value 503881000 vs printed 503881000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_assets | mapped-sample | agree | page value 5462970000 vs printed 5462970000 |
| total_debt | component sum | agree | page value 4227000 vs printed 4227000 |
