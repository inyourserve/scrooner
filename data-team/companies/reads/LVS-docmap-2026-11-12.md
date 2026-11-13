# LVS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001300514-26-000013 (CIK 0001300514, filed 2026-02-06): COVER R1.htm, BS R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001300514-16-000023 (CIK 0001300514, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001300514-18-000022 (CIK 0001300514, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001300514-23-000021 (CIK 0001300514, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001300514.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Net revenues | 13017000000 | 13017000000 | 11298000000 | 11298000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| cost_of_revenue | component sum | us-gaap:CostOfRevenue | R4.htm | Cost of revenue | 6536000000 |  | 5777000000 |  |  | FILING-CHECKED | sum of the five printed member rows of CostOfRevenue (casino, rooms, food and beverage, mall, convention/retail/other); ties into Total operating expenses 10,199 / check: hand R4.htm corrected: 5,268 is the casino member row only; cost of revenue printed per revenue type (casino 5,268, rooms 352, F&B 562, mall 92, convention/other 262) with no total; revenues tie (9,789+1,422+644+801+361 = 13,017) -> component sum 6,536 (FY1 5,777). |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1120 tags across all 101 R pages, face and notes) of 0001300514-26-000013; no face row matched / check: hand R4.htm agree |
| operating_expenses | component sum | us-gaap:ProvisionForDoubtfulAccounts+us-gaap:SellingGeneralAndAdministrativeExpense+lvs:CorporateExpense+us-gaap:PreOpeningCosts+us-gaap:ResearchAndDevelopmentExpense+us-gaap:DepreciationAndAmortization+lvs:AmortizationOfLeaseholdInterestsInLand+us-gaap:GainLossOnSalesOfAssetsAndAssetImpairmentCharges | R4.htm | Total operating expenses | 3663000000 |  | 3119000000 |  |  | FILING-CHECKED | every non-COGS line of Total operating expenses; ties to revenue - cost of revenue - OI / check: hand R4.htm corrected: Total operating expenses 10,199 includes cost of revenue 6,536; non-COGS lines provision 85 + G&A 1,188 + corporate 310 + pre-opening 24 + development 269 + D&A 1,464 + leasehold amortization 76 + loss on disposal 247 = 3,663 = 13,017 - 6,536 - OI 2,818 -> component sum. |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | General and administrative | 1188000000 | 1188000000 | 1150000000 | 1150000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Development | 269000000 | 269000000 | 228000000 | 228000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 2818000000 | 2818000000 | 2402000000 | 2402000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense, net of amounts capitalized | -746000000 | 746000000 | -727000000 | 727000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001300514-26-000013 R4.htm period ..2025-12-31 / check: hand R4.htm agree |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 2213000000 | 2213000000 | 1960000000 | 1960000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | -347000000 | 347000000 | -208000000 | 208000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to Las Vegas Sands Corp. | 1627000000 | 1627000000 | 1446000000 | 1446000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (in usd per share) | 2.35 | 2.35 | 1.97 | 1.97 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (in usd per share) | 2.35 | 2.35 | 1.96 | 1.96 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 691000000 | 691000000 | 735000000 | 735000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 693000000 | 693000000 | 737000000 | 737000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 3841000000 | 3841000000 | 3650000000 | 3650000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of provision for credit losses of $225 and $186 | 742000000 | 742000000 | 417000000 | 417000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 46000000 | 46000000 | 41000000 | 41000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4832000000 | 4832000000 | 4290000000 | 4290000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 11673000000 | 11673000000 | 11993000000 | 11993000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| goodwill | combined | us-gaap:IntangibleAssetsNetIncludingGoodwill | R3.htm | Goodwill and intangible assets, net | 573000000 | 573000000 | 545000000 | 545000000 | Y | FILING-CHECKED | single BS line 'Goodwill and intangible assets, net' combines goodwill with other intangibles; no separate goodwill line / check: hand R3.htm corrected: Face line is 'Goodwill and intangible assets, net' 573 (IntangibleAssetsNetIncludingGoodwill): goodwill combined with intangibles -> combined. |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 21920000000 | 21920000000 | 20666000000 | 20666000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 190000000 | 190000000 | 164000000 | 164000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4222000000 | 4222000000 | 5801000000 | 5801000000 | Y | FILING-CHECKED | accn 0001300514-26-000013 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 19986000000 | 19986000000 | 17506000000 | 17506000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Las Vegas Sands Corp. stockholders’ equity | 1590000000 | 1590000000 | 2884000000 | 2884000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash generated from operating activities | 3023000000 | 3023000000 | 3204000000 | 3204000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1217000000 | -1217000000 | -1579000000 | -1579000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -1643000000 | -1643000000 | -3060000000 | -3060000000 | Y | FILING-CHECKED | accn 0001300514-26-000013 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -1168000000 | 1168000000 | -1567000000 | 1567000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 1464000000 | 1464000000 | 1308000000 | 1308000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 54000000 | 54000000 | 55000000 | 55000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid and noncontrolling interest payments | -833000000 | 833000000 | -590000000 | 590000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -2217000000 | 2217000000 | -1750000000 | 1750000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash payments for interest, net of amounts capitalized | 710000000 | 710000000 | 650000000 | 650000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001300514-26-000013 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R78.htm | Income Taxes - Schedule of Cash Taxes Paid (Details) | 271000000 | 271000000 | 222000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R78.htm 'Income Taxes - Schedule of Cash Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R78.htm corrected: Tax note R78 prints Income taxes paid, net 271M (FY1 222M). |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of debt + Debt | 15784000000 | 15784000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 675000000 | 675000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 11688461000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001300514-16-000023 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 8846986000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001300514-16-000023 R4.htm prints 'General and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 1267415000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Development' on us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost = 10372000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 2841475000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Interest expense, net of amounts capitalized' on us-gaap:InterestExpense = -265220000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 2621882000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -236185000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Net income attributable to Las Vegas Sands Corp.' on us-gaap:NetIncomeLoss = 1966236000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Basic (in usd per share)' on us-gaap:EarningsPerShareBasic = 2.47 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Diluted (in usd per share)' on us-gaap:EarningsPerShareDiluted = 2.47 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 796785900 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001300514-16-000023 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 797596082 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2179490000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 1267848000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 42573000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3609250000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 15731638000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001300514-16-000023 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Total assets' on us-gaap:Assets = 20987421000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 110408000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2464135000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 12569434000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001300514-16-000023 R2.htm prints 'Total Las Vegas Sands Corp. stockholders’ equity' on us-gaap:StockholdersEquity = 6816741000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Net cash generated from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 3449971000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1528466000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -3206398000 (FILING-CHECKED)
- capex: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1528642000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 998919000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 45804000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Dividends paid' on lvs:PaymentsOfDividendsCash = -2692882000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001300514-16-000023 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -205084000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001300514-16-000023 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001300514-16-000023 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001300514-18-000022 R4.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 12882000000 (FILING-CHECKED)
- cfo: era 10-K 0001300514-18-000022 R7.htm prints 'Net cash generated from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 4543000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001300514-18-000022 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -823000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001300514-18-000022 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -3487000000 (FILING-CHECKED)
- research_and_development: era 10-K 0001300514-23-000021 R5.htm prints 'Development' on us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost = 143000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfRevenue)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 9 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 4.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
