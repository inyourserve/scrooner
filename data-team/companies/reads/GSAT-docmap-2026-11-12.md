# GSAT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001366868-26-000012 (CIK 0001366868, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R10.htm
- 10-K 0001366868-16-000113 (CIK 0001366868, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001366868-18-000007 (CIK 0001366868, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001366868-21-000016 (CIK 0001366868, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001366868.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 272986000 | 272986000 | 250349000 | 250349000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods and services | 83181000 |  | 73160000 |  | API missing | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (906 tags across all 88 R pages, face and notes) of 0001366868-26-000012; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 265556000 | 265556000 | 251298000 | 251298000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Marketing, general and administrative | 51428000 | 51428000 | 43434000 | 43434000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R45.htm | Summary of Significant Accounting Policies - Narrative (Details) |  | 6100000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R45.htm 'Summary of Significant Accounting Policies - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income (loss) from operations | 7430000 | 7430000 | -949000 | -949000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income and expense, net of amounts capitalized | -40920000 | -40920000 | -13562000 | -13562000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -2773000 | -2773000 | -61029000 | -61029000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 5878000 | 5878000 | 2135000 | 2135000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -8651000 | -8651000 | -63164000 | -63164000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | -0.15 | -0.15 | -0.59 | -0.59 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | -0.15 | -0.15 | -0.59 | -0.59 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 126757000 | 126757000 | 125877000 | 125877000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 126757000 | 126757000 | 125877000 | 125877000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 447471000 | 447471000 | 391164000 | 391164000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for credit losses of $1,468 and $1,504, respectively | 19976000 | 19976000 | 26952000 | 26952000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 9614000 | 9614000 | 10741000 | 10741000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 496728000 | 496728000 | 447571000 | 447571000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 1305458000 | 1305458000 | 673632000 | 673632000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R64.htm | Intangible and Other Assets - Narrative (Details) |  | 30600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'Intangible and Other Assets - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2326265000 | 2326265000 | 1710237000 | 1710237000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 56022000 | 56022000 | 29677000 | 29677000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 205486000 | 205486000 | 141485000 | 141485000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1970536000 | 1970536000 | 1351354000 | 1351354000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 355729000 | 355729000 | 358883000 | 358883000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided by operating activities | 621650000 | 621650000 |  | 439192000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash used in investing activities | -550383000 | -550383000 |  | -260570000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash (used in) provided by financing activities | -16180000 | -16180000 |  | 157181000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R73.htm | Commitments and Contingencies (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R73.htm 'Commitments and Contingencies (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R10.htm | Depreciation, amortization and accretion | 87401000 | 87401000 |  | 88986000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation expense | 23413000 | 23413000 |  | 35548000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R10.htm | Dividends paid on Series A Preferred Stock | -10605000 | 10605000 |  | 10634000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R10.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (906 tags across all 88 R pages, face and notes) of 0001366868-26-000012; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Interest | 0 | 0 |  | 15666000 | Y | FILING-CHECKED | accn 0001366868-26-000012 R10.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R79.htm | Taxes - Schedule of Payments for Income Taxes, Net of Refund Received (Details) |  | 6476000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R79.htm 'Taxes - Schedule of Payments for Income Taxes, Net of Refund Received (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of long-term debt + Long-term debt | 483788000 | 483788000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 128050400 |  |  |  | API missing | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Total revenue' on us-gaap:Revenues = 90490000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Cost of subscriber equipment sales' on us-gaap:CostOfGoodsSold = 11814000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 157094000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Marketing, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 37418000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001366868-16-000113 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Loss from operations' on us-gaap:OperatingIncomeLoss = -66604000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Interest income and expense, net of amounts capitalized' on us-gaap:InterestIncomeExpenseNonoperatingNet = -35854000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 73714000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 1392000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Net income (loss)' on us-gaap:NetIncomeLoss = 72322000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Basic (USD per share)' on us-gaap:EarningsPerShareBasic = 0.07 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Diluted (USD per share)' on us-gaap:EarningsPerShareDiluted = 0.07 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 1020149000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001366868-16-000113 R4.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 1230394000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 7476000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Accounts receivable, net of allowance of $5,270 and $4,788, respectively' on us-gaap:AccountsReceivableNetCurrent = 14536000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 12023000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 38491000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1077560000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001366868-16-000113 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Total assets' on us-gaap:Assets = 1232921000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 8693000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 107031000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001366868-16-000113 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001366868-16-000113 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 237131000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2162000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -33478000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 33276000 (FILING-CHECKED)
- capex: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Property and equipment additions' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -5523000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Depreciation, amortization and accretion' on us-gaap:DepreciationAmortizationAndAccretionNet = 77247000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 2955000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001366868-16-000113 R8.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 19683000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001366868-16-000113 R8.htm prints 'Cash paid for: Income taxes' on us-gaap:IncomeTaxesPaid = 445000 (FILING-CHECKED)
- revenue: era 10-K 0001366868-18-000007 R4.htm prints 'Total revenue' on us-gaap:Revenues = 112660000 (FILING-CHECKED)
- accounts_payable: era 10-K 0001366868-18-000007 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 6048000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001366868-18-000007 R8.htm prints 'Interest' on us-gaap:InterestPaid = 24075000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001366868-21-000016 R4.htm prints '(Loss) income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -108977000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 265556000 vs printed 265556000 |
| research_and_development | NOTE | agree | page value 6100000 vs API 6100000 |
| interest_expense | combined | agree | page value -40920000 vs printed -40920000 |
| accounts_receivable | mapped-sample | agree | page value 19976000 vs printed 19976000 |
| goodwill | NOTE | agree | page value 30600000 vs API 30600000 |
| stockholders_equity | mapped-sample | agree | page value 355729000 vs printed 355729000 |
| cfo | mapped-sample | agree | page value 621650000 vs printed 621650000 |
| capex | NOTE | agree | fixed to not_presented: no period-end value on any presenting page |
| depreciation_and_amortization | combined | agree | page value 87401000 vs printed 87401000 |
| dividends_paid | not_presented | agree | fixed: PaymentsOfDividends read off R10.htm (-10605000) |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 6476000 vs API 6476000 |
| total_debt | component sum | agree | page value 483788000 vs printed 483788000 |
