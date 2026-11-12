# KNX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001492691-26-000016 (CIK 0001492691, filed 2026-02-19): COVER R1.htm, BS R2.htm, CI R3.htm, CF R5.htm, BSP R7.htm
- 10-K 0001492691-16-000059 (CIK 0001492691, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001492691-24-000015 (CIK 0001492691, era filing): COVER R1.htm, BS R2.htm, CI R3.htm, CF R5.htm, BSP R7.htm
- 10-K 0001492691-21-000016 (CIK 0001492691, era filing): COVER R1.htm, BS R2.htm, CI R3.htm, CF R5.htm
- companyfacts CIK0001492691.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R59.htm | Acquisitions - Narrative (Details) |  | 7469689000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Acquisitions - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| gross_profit | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| operating_expenses | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| sga_expense | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| research_and_development | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R105.htm | Information by Segment (Summary Of Financial Information By Segments) (Detail) |  | 216062000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R105.htm 'Information by Segment (Summary Of Financial Information By Segments) (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Consolidated Statements of Comprehensive Income |  | 161795000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R3.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R73.htm | Income Taxes (Income Tax Expense (Benefit) ) (Detail) |  | 95322000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R73.htm 'Income Taxes (Income Tax Expense (Benefit) ) (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R73.htm | Income Taxes (Income Tax Expense (Benefit) ) (Detail) |  | 29768000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R73.htm 'Income Taxes (Income Tax Expense (Benefit) ) (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Consolidated Statements of Comprehensive Income |  | 65946000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R3.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Consolidated Statements of Comprehensive Income |  | 0.41 |  |  |  | FILING-CHECKED | not on the face statement; shown in R3.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Consolidated Statements of Comprehensive Income |  | 0.41 |  |  |  | FILING-CHECKED | not on the face statement; shown in R3.htm 'Consolidated Statements of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R99.htm | Weighted Average Shares Outstanding (Calculation Of Basic And Diluted Earnings Per Share Attributable To Stockholders) ( |  | 162188000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R99.htm 'Weighted Average Shares Outstanding (Calculation Of Basic And Diluted Earnings P' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R99.htm | Weighted Average Shares Outstanding (Calculation Of Basic And Diluted Earnings Per Share Attributable To Stockholders) ( |  | 162611000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R99.htm 'Weighted Average Shares Outstanding (Calculation Of Basic And Diluted Earnings P' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 220420000 | 220420000 | 218261000 | 218261000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Trade receivables, net of allowance for doubtful accounts of $30,647 and $37,797, respectively | 305324000 | 305324000 | 803696000 | 803696000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 887526000 | 887526000 | 1448741000 | 1448741000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 4717725000 | 4717725000 | 4703385000 | 4703385000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 3934741000 | 3934741000 | 3962142000 | 3962142000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 11955436000 | 11955436000 | 12698532000 | 12698532000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 200835000 | 200835000 | 329697000 | 329697000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 1031209000 | 1031209000 | 1706751000 | 1706751000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 4863570000 | 4863570000 | 5581727000 | 5581727000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total Knight-Swift stockholders' equity | 7082454000 | 7082454000 | 7108967000 | 7108967000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R5.htm | Net cash provided by operating activities | 1266647000 | 1266647000 | 799063000 | 799063000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used in investing activities | -520394000 | -520394000 | -759122000 | -759122000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash (used in) provided by financing activities | -807743000 | -807743000 | -139397000 | -139397000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireMachineryAndEquipment | R5.htm | Purchases of property and equipment | -795392000 | 795392000 | -819150000 | 819150000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R5.htm | Depreciation and amortization of property, equipment, and intangibles | 788053000 | 788053000 | 792802000 | 792802000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R92.htm | Stock-based Compensation (Stock-based Compensation Expense) (Detail) |  | 28562000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Stock-based Compensation (Stock-based Compensation Expense) (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R5.htm | Dividends paid | -117435000 | 117435000 | -104153000 | 104153000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1094 tags across all 106 R pages, face and notes) of 0001492691-26-000016; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R5.htm | Interest | 161342000 | 161342000 | 174485000 | 174485000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R5.htm | Income taxes | 50312000 | 50312000 | 9929000 | 9929000 | Y | FILING-CHECKED | accn 0001492691-26-000016 R5.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent | R2.htm | Finance lease liabilities and long-term debt – current portion | 194406000 | 194406000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R2.htm | Beginning balance, shares | 324678000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Operating revenue' on us-gaap:Revenues = 4229322000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 370104000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 38350000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 316786000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 119209000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 197577000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 1.39 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted = 1.38 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 142018000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001492691-16-000059 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 143668000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 107590000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 422421000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 705607000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Net property and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 1651100000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 253256000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Total assets' on us-gaap:Assets = 2922435000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 121827000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 398945000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2305308000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001492691-16-000059 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 617127000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 569498000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 241807000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 325233000 (FILING-CHECKED)
- capex: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = 342615000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Depreciation and amortization of property, equipment and intangibles' on us-gaap:DepreciationDepletionAndAmortization = 268549000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Non-cash equity compensation' on us-gaap:ShareBasedCompensation = 6525000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001492691-16-000059 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Interest' on us-gaap:InterestPaid = 45390000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001492691-16-000059 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 78522000 (FILING-CHECKED)
- interest_expense: 10-K 0001492691-24-000015 statement not identified (auto)
- income_before_tax: 10-K 0001492691-21-000016 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 7469689000 vs API 7469689000 |
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | NOTE | agree | page value 216062000 vs API 216062000 |
| income_before_tax | NOTE | agree | page value 95322000 vs API 95322000 |
| income_tax_expense | NOTE | agree | page value 29768000 vs API 29768000 |
| weighted_basic_shares | NOTE | agree | page value 162188000 vs API 162188000 |
| weighted_diluted_shares | NOTE | agree | page value 162611000 vs API 162611000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_assets | mapped-sample | agree | page value 11955436000 vs printed 11955436000 |
| stockholders_equity | mapped-sample | agree | page value 7082454000 vs printed 7082454000 |
| depreciation_and_amortization | mapped-sample | agree | page value 788053000 vs printed 788053000 |
| sbc | NOTE | agree | page value 28562000 vs API 28562000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 194406000 vs printed 194406000 |
| shares_outstanding | component sum | agree | page value 324678000 vs printed 324678000 |
