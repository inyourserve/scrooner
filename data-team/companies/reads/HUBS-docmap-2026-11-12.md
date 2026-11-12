# HUBS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-046646 (CIK 0001404655, filed 2026-02-11): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-16-013204 (CIK 0001404655, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-18-001962 (CIK 0001404655, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0000950170-24-015277 (CIK 0001404655, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0001404655.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Total revenue | 3131266000 | 3131266000 | 2627543000 | 2627543000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Total cost of revenue | 508487000 | 508487000 | 393265000 | 393265000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profit | 2622779000 | 2622779000 | 2234278000 | 2234278000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Total operating expenses | 2615400000 | 2615400000 | 2301880000 | 2301880000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 326045000 | 326045000 | 300332000 | 300332000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 905943000 | 905943000 | 778714000 | 778714000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Income (loss) from operations | 7379000 | 7379000 | -67602000 | -67602000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R4.htm | Interest expense | -876000 | 876000 | -3721000 | 3721000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income (loss) before income tax expense | 69463000 | 69463000 | 28677000 | 28677000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | -23552000 | 23552000 | -24049000 | 24049000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income (loss) | 45911000 | 45911000 | 4628000 | 4628000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income (loss) per share, basic | 0.88 | 0.88 | 0.09 | 0.09 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income (loss) per share, diluted | 0.86 | 0.86 | 0.09 | 0.09 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average common shares used in computing basic net income (loss) per share: | 52455000 | 52455000 | 51178000 | 51178000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average common shares used in computing diluted net income (loss) per share: | 53194000 | 53194000 | 51819000 | 51819000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 882242000 | 882242000 | 512667000 | 512667000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable - net of allowance for credit losses of $6,825 and $6,088 at December 31, 2025 and 2024, respectivel | 419146000 | 419146000 | 334829000 | 334829000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1023 tags across all 107 R pages, face and notes) of 0001193125-26-046646; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2449735000 | 2449735000 | 2633603000 | 2633603000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 141869000 | 141869000 | 114165000 | 114165000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 291452000 | 291452000 | 209508000 | 209508000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 3854151000 | 3854151000 | 3795833000 | 3795833000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 24764000 | 24764000 | 3649000 | 3649000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 1467471000 | 1467471000 | 1573399000 | 1573399000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 1787907000 | 1787907000 | 1887547000 | 1887547000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders’ equity | 2066244000 | 2066244000 | 1908286000 | 1908286000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash and cash equivalents provided by operating activities | 760717000 | 760717000 | 598599000 | 598599000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash and cash equivalents provided by (used in) investing activities | 491773000 | 491773000 | -515861000 | -515861000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash and cash equivalents (used in) provided by financing activities | -910009000 | -910009000 | 53495000 | 53495000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -53165000 | 53165000 | -37939000 | 37939000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 136295000 | 136295000 | 96828000 | 96828000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 528153000 | 528153000 | 504770000 | 504770000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1023 tags across all 107 R pages, face and notes) of 0001193125-26-046646; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -500019000 | 500019000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 422000 | 422000 | 1721000 | 1721000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income taxes | 19311000 | 19311000 | 12187000 | 12187000 | Y | FILING-CHECKED | accn 0001193125-26-046646 R8.htm period ..2025-12-31 |
| total_debt | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (1023 tags across all 107 R pages, face and notes) of 0001193125-26-046646; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 52555000 | 52555000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Total revenue' on us-gaap:Revenues = 181943000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Total cost of revenues' on us-gaap:CostOfRevenue = 47923000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 134020000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 180494000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013204 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 35408000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 32457000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Loss from operations' on us-gaap:OperatingIncomeLoss = -46474000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -185000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Loss before income tax (provision) benefit' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -45641000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Income tax (provision) benefit' on us-gaap:IncomeTaxExpenseBenefit = -412000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Net loss' on us-gaap:NetIncomeLoss = -46053000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Net loss attributable to common stockholders per common share, basic and diluted' on us-gaap:EarningsPerShareBasicAndDiluted = -1.39 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013204 R4.htm prints 'Net loss attributable to common stockholders per common share, basic and diluted' on us-gaap:EarningsPerShareBasicAndDiluted = -1.39 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013204 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013204 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 55580000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Accounts receivable—net of allowance for doubtful accounts of $371 and $218 at D' on us-gaap:AccountsReceivableNetCurrent = 25142000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 145754000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 18161000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 9773000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Total assets' on us-gaap:Assets = 220379000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 2588000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 91307000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 98671000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013204 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 121708000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Net cash and cash equivalents used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -423000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Net cash and cash equivalents used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -104104000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Net cash and cash equivalents provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 36939000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -8427000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 7343000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 21308000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-013204 R8.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 185000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013204 R8.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 215000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-001962 R4.htm prints 'Total revenue' on us-gaap:Revenues = 375612000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001564590-18-001962 R4.htm prints 'Total cost of revenue' on us-gaap:CostOfRevenue = 75729000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-001962 R9.htm prints 'Net cash and cash equivalents provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 49614000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-001962 R9.htm prints 'Net cash and cash equivalents used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -401197000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-001962 R9.htm prints 'Net cash and cash equivalents provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 376806000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001564590-18-001962 R9.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 762000 (FILING-CHECKED)
- interest_expense: era 10-K 0000950170-24-015277 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -3801000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| sga_expense | component sum | agree | page value 1705421000 vs printed 1705421000 |
| income_before_tax | mapped-sample | agree | page value 69463000 vs printed 69463000 |
| income_tax_expense | mapped-sample | agree | page value -23552000 vs printed -23552000 |
| basic_eps | mapped-sample | agree | page value 0.88 vs printed 0.88 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
| shares_outstanding | mapped-sample | agree | page value 52555000 vs printed 52555000 |
