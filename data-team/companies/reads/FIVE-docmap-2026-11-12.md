# FIVE document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001177609-26-000010 (CIK 0001177609, filed 2026-03-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001628280-16-012961 (CIK 0001177609, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001177609-19-000010 (CIK 0001177609, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001177609-21-000011 (CIK 0001177609, era filing): COVER R1.htm, BS R2.htm, IS R3.htm, CF R5.htm
- companyfacts CIK0001177609.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 4764147000 | 4764147000 | 3876527000 | 3876527000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold (exclusive of items shown separately below) | 3049461000 | 3049461000 | 2523865000 | 2523865000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (600 tags across all 68 R pages, face and notes) of 0001177609-26-000010; no face row matched |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (600 tags across all 68 R pages, face and notes) of 0001177609-26-000010; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 1065164000 | 1065164000 | 861398000 | 861398000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (600 tags across all 68 R pages, face and notes) of 0001177609-26-000010; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 457399000 | 457399000 | 323817000 | 323817000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income and other income, net | -22972000 | 22972000 | -14848000 | 14848000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 480371000 | 480371000 | 338665000 | 338665000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 121730000 | 121730000 | 85054000 | 85054000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 358641000 | 358641000 | 253611000 | 253611000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic income per common share (dollars per share) | 6.51 | 6.51 | 4.61 | 4.61 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted income per common share (dollars per share) | 6.47 | 6.47 | 4.6 | 4.6 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic shares | 55112281 | 55112281 | 55055064 | 55055064 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted shares | 55436972 | 55436972 | 55156342 | 55156342 | Y | FILING-CHECKED | accn 0001177609-26-000010 R5.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and cash equivalents | 723699000 | 723699000 | 331718000 | 331718000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:PrepaidTaxes | R3.htm | Prepaid income taxes and tax receivable | 5210000 | 5210000 | 4649000 | 4649000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 846609000 | 846609000 | 659500000 | 659500000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1916723000 | 1916723000 | 1351367000 | 1351367000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1234331000 | 1234331000 | 1261728000 | 1261728000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (600 tags across all 68 R pages, face and notes) of 0001177609-26-000010; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4937019000 | 4937019000 | 4339574000 | 4339574000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 368381000 | 368381000 | 260343000 | 260343000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 954006000 | 954006000 | 756442000 | 756442000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2743729000 | 2743729000 | 2531247000 | 2531247000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders’ equity | 2193290000 | 2193290000 | 1808327000 | 1808327000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R3.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 586428000 | 586428000 | 430648000 | 430648000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -186176000 | -186176000 | -232938000 | -232938000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -8271000 | -8271000 | -45741000 | -45741000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -174741000 | 174741000 | -323994000 | 323994000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 192123000 | 192123000 | 167447000 | 167447000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 34680000 | 34680000 | 15589000 | 15589000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (600 tags across all 68 R pages, face and notes) of 0001177609-26-000010; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase and retirement of common stock | 0 | 0 | -40213000 | 40213000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | 475000 | 475000 | 420000 | 420000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R7.htm | Income taxes paid | 127613000 | 127613000 | 81656000 | 81656000 | Y | FILING-CHECKED | accn 0001177609-26-000010 R7.htm period ..2026-01-31 |
| total_debt | component sum | us-gaap:LinesOfCreditCurrent | R3.htm | Line of credit | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 55228735 | 55228735 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-01-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 831954000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 540020000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 198993000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 92941000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Interest (income) expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -40000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 92656000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 34976000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 57680000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Basic (loss) income per common share (dollars per share)' on us-gaap:EarningsPerShareBasic = 1.06 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Diluted (loss) income per common share (dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.05 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Basic shares' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 54513622 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001628280-16-012961 R4.htm prints 'Diluted shares' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 54793301 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 53081000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-16-012961 R2.htm read; no row matched (auto)
- inventory: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 148370000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 264745000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 119784000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Total assets' on us-gaap:Assets = 393294000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 58225000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 102196000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 148813000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-012961 R2.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 244481000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 87913000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -99394000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 1376000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -53059000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 22227000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 11172000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Payments for Repurchase of Common Stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -322000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Interest paid' on us-gaap:InterestPaid = 25000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-012961 R6.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 36897000 (FILING-CHECKED)
- revenue: era 10-K 0001177609-19-000010 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 1559563000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001177609-19-000010 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 994478000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001177609-19-000010 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 251748000 (FILING-CHECKED)
- cfo: era 10-K 0001177609-19-000010 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 184133000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001177609-19-000010 R6.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -5582000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001177609-19-000010 R6.htm prints 'Interest paid' on us-gaap:InterestPaid = 3000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001177609-21-000011 R3.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 153067000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 4764147000 vs printed 4764147000 |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value -22972000 vs printed -22972000 |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | mapped-sample | agree | page value 2743729000 vs printed 2743729000 |
| sbc | mapped-sample | agree | page value 34680000 vs printed 34680000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 0 vs printed 0 |
| shares_outstanding | mapped-sample | agree | page value 55228735 vs printed 55228735 |
