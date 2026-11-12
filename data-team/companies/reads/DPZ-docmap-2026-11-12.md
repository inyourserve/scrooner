# DPZ document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-062321 (CIK 0001286681, filed 2026-02-23): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001193125-16-476935 (CIK 0001286681, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001193125-18-049576 (CIK 0001286681, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000950170-25-025223 (CIK 0001286681, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001286681.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Revenues | 4939994000 | 4939994000 | 4706416000 | 4706416000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of sales | 2966434000 | 2966434000 | 2857914000 | 2857914000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross margin | 1973560000 | 1973560000 | 1848502000 | 1848502000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| operating_expenses | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:AdvertisingExpense+us-gaap:GainLossOnSaleOfOtherAssets | R4.htm | General and administrative + U.S. franchise advertising + Refranchising loss (gain) | 1019586000 | 1027642000 | 969503000 | 969187000 | N (printed 1019586000 vs API 1027642000) | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 464120000 | 464120000 | 459492000 | 459492000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (977 tags across all 80 R pages, face and notes) of 0001193125-26-062321; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Income from operations | 953974000 | 953974000 | 878999000 | 878999000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | -195972000 | 195972000 | -195870000 | 195870000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before provision for income taxes | 770338000 | 770338000 | 722215000 | 722215000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Provision for income taxes | 168634000 | 168634000 | 138045000 | 138045000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net Income (Loss) | 601704000 | 601704000 | 584170000 | 584170000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Common Stock - basic | 17.69 | 17.69 | 16.83 | 16.83 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Common Stock - diluted | 17.57 | 17.57 | 16.69 | 16.69 | Y | FILING-CHECKED | accn 0001193125-26-062321 R4.htm period ..2025-12-28 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R42.htm | Earnings Per Share - Summary of Computation of Basic and Diluted Earning per Share (Detail) |  | 34007071 |  |  |  | FILING-CHECKED | not on the face statement; shown in R42.htm 'Earnings Per Share - Summary of Computation of Basic and Diluted Earning per Sha' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R42.htm | Earnings Per Share - Summary of Computation of Basic and Diluted Earning per Share (Detail) |  | 34237646 |  |  |  | FILING-CHECKED | not on the face statement; shown in R42.htm 'Earnings Per Share - Summary of Computation of Basic and Diluted Earning per Sha' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 125675000 | 125675000 | 186126000 | 186126000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net of reserves of $5,805 in 2025 and $5,834 in 2024 | 315958000 | 315958000 | 309104000 | 309104000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories | 79189000 | 79189000 | 70919000 | 70919000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 894201000 | 894201000 | 905278000 | 905278000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property, plant and equipment, net | 324022000 | 324022000 | 301179000 | 301179000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 10726000 | 10726000 | 11578000 | 11578000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 1716459000 | 1716459000 | 1737013000 | 1737013000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 135029000 | 135029000 | 85898000 | 85898000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 541621000 | 541621000 | 1612462000 | 1612462000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 5617601000 | 5617601000 | 5699304000 | 5699304000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' deficit | -3901142000 | -3901142000 | -3962291000 | -3962291000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R2.htm period ..2025-12-28 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 792062000 | 792062000 | 624897000 | 624897000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -70190000 | -70190000 | -31229000 | -31229000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -752093000 | -752093000 | -532223000 | -532223000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -120558000 | 120558000 | -112885000 | 112885000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 88827000 | 88827000 | 87732000 | 87732000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Non-cash equity-based compensation expense | 44640000 | 44640000 | 43255000 | 43255000 | Y | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Payments of common stock dividends and equivalents | -236861000 | 236861000 | -209945000 | 209945000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchases of common stock | -357697000 | 357697000 | -329557000 | 329557000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-062321 R8.htm period ..2025-12-28 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R41.htm | Disclosure - Description of Business and Summary of Significant Accounting Policies - Schedule of Supplemental Disclosur |  | 185020000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R41.htm 'Disclosure - Description of Business and Summary of Significant Accounting Polic' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R36.htm | Description of Business and Summary of Significant Accounting Policies - Additional Information (Detail) |  | 161893000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R36.htm 'Description of Business and Summary of Significant Accounting Policies - Additio' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R2.htm | Current portion of long-term debt + Long-term debt, less current portion | 4816814000 | 4816814000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 33627992 | 33627992 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-28; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-476935 R4.htm prints 'Revenue' on us-gaap:Revenues = 2216528000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-476935 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 1533397000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-476935 R4.htm prints 'OPERATING MARGIN' on us-gaap:GrossProfit = 683131000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-476935 R4.htm prints 'GENERAL AND ADMINISTRATIVE' on us-gaap:GeneralAndAdministrativeExpense = 277692000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-476935 R4.htm prints 'GENERAL AND ADMINISTRATIVE' on us-gaap:GeneralAndAdministrativeExpense = 277692000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-476935 R4.htm prints 'INCOME FROM OPERATIONS' on us-gaap:OperatingIncomeLoss = 405439000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-476935 R4.htm prints 'INTEREST EXPENSE' on us-gaap:InterestExpense = -99537000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-476935 R4.htm prints 'INCOME BEFORE PROVISION FOR INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 306215000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-476935 R4.htm prints 'PROVISION FOR INCOME TAXES' on us-gaap:IncomeTaxExpenseBenefit = 113426000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-476935 R4.htm prints 'NET INCOME' on us-gaap:NetIncomeLoss = 192789000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-476935 R4.htm prints 'Common Stock - basic' on us-gaap:EarningsPerShareBasic = 3.58 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-476935 R4.htm prints 'Common Stock - diluted' on us-gaap:EarningsPerShareDiluted = 3.47 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-476935 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-476935 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 133449000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Accounts receivable, net of reserves of $2,662 in 2015 and $3,361 in 2014' on us-gaap:AccountsReceivableNetCurrent = 131582000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 36861000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 602637000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 131890000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 16097000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Total assets' on us-gaap:Assets = 799845000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 106927000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 375983000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2600096000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-476935 R2.htm prints 'Total stockholders' deficit' on us-gaap:StockholdersEquity = -1800251000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 291786000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -109292000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -80936000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -63282000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 32434000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Non-cash compensation expense' on us-gaap:ShareBasedCompensation = 17623000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-476935 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001193125-16-476935 R7.htm prints 'Purchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -738557000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-476935 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-476935 R7.htm read; no row matched (auto)
- cfo: era 10-K 0001193125-18-049576 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 339036000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-049576 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -149004000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-049576 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -197145000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000950170-25-025223 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
- operating_expenses: N (printed 1019586000 vs API 1027642000) (us-gaap:GeneralAndAdministrativeExpense+us-gaap:AdvertisingExpense+us-gaap:GainLossOnSaleOfOtherAssets)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | mapped-sample | agree | page value 1973560000 vs printed 1973560000 |
| operating_expenses | component sum | agree | page value 1019586000 vs printed 1019586000 |
| sga_expense | component sum | agree | page value 1023614000 vs printed 1023614000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| weighted_basic_shares | NOTE | agree | page value 34007071 vs API 34007071 |
| weighted_diluted_shares | NOTE | agree | page value 34237646 vs API 34237646 |
| inventory | mapped-sample | agree | page value 79189000 vs printed 79189000 |
| stockholders_equity | mapped-sample | agree | page value -3901142000 vs printed -3901142000 |
| share_buybacks | mapped-sample | agree | page value -357697000 vs printed -357697000 |
| cash_paid_for_interest | NOTE | agree | page value 185020000 vs API 185020000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 161893000 vs API 161893000 |
| total_debt | component sum | agree | page value 4816814000 vs printed 4816814000 |
