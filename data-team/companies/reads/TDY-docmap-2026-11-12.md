# TDY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001094285-26-000017 (CIK 0001094285, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0001094285-16-000177 (CIK 0001094285, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001094285-21-000066 (CIK 0001094285, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001094285-24-000044 (CIK 0001094285, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- companyfacts CIK0001094285.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 6115400000 | 6115400000 | 5670000000 | 5670000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 3500600000 | 3500600000 | 3235200000 | 3235200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1007 tags across all 106 R pages, face and notes) of 0001094285-26-000017; no face row matched / check: hand R3.htm agree |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:ImpairmentOfIntangibleAssetsExcludingGoodwill | R3.htm | SG&A + R&D + acquired intangible amortization + impairment | 1465000000 |  | 1445700000 |  |  | FILING-CHECKED | every face line between cost of sales and operating income; ties exactly; CostsAndExpenses includes COGS / check: hand R3.htm corrected: No opex total excluding COGS ('Total costs and expenses' 4,965.6 includes cost of sales). Non-COGS face lines SG&A 931.1 + R&D 317.3 + amortization 216.6 + impairment 0.0 = 1,465.0 = net sales 6,115.4 - cost of sales 3,500.6 - OI 1,149.8; FY1 902.6+292.6+198.0+52.5 = 1,445.7 ties. |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 931100000 | 931100000 | 902600000 | 902600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 317300000 | 317300000 | 292600000 | 292600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | 1149800000 | 1149800000 | 989100000 | 989100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| interest_expense | combined | us-gaap:InterestExpenseNonoperating | R3.htm | Interest and debt expense, net | -59600000 | 59600000 | -57900000 | 57900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | printed line is net interest and debt expense (rule 6); no gross interest expense printed / check: hand R3.htm corrected: R3 label is 'Interest and debt expense, net' (59.6), and debt note R70 calls it 'Net interest expense': a net line (rule 6), though tagged InterestExpenseNonoperating. |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (loss) before income taxes | 1094500000 | 1094500000 | 937900000 | 937900000 | Y | FILING-CHECKED | accn 0001094285-26-000017 R3.htm period ..2025-12-28 / check: hand R3.htm agree |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision (benefit) for income taxes | 198800000 | 198800000 | 117200000 | 117200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (loss) attributable to Teledyne | 894800000 | 894800000 | 819200000 | 819200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per common share (in USD per share) | 19.12 | 19.12 | 17.43 | 17.43 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per common share (in USD per share) | 18.88 | 18.88 | 17.21 | 17.21 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted average common shares outstanding (in shares) | 46800000 | 46800000 | 47000000 | 47000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted average diluted common shares outstanding (in shares) | 47400000 | 47400000 | 47600000 | 47600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R3.htm period ..2025-12-28 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 352400000 | 352400000 | 649800000 | 649800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net | 992400000 | 992400000 | 901100000 | 901100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories, net | 1043300000 | 1043300000 | 914400000 | 914400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total Current Assets | 3055600000 | 3055600000 | 2944600000 | 2944600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R6.htm | Property, plant and equipment, net | 839100000 | 839100000 | 745200000 | 745200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 8687600000 | 8687600000 | 7990500000 | 7990500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total Assets | 15285300000 | 15285300000 | 14200500000 | 14200500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 486600000 | 486600000 | 416400000 | 416400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total Current Liabilities | 1860100000 | 1860100000 | 1261600000 | 1261600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total Liabilities | 4771400000 | 4771400000 | 4645100000 | 4645100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Stockholders’ Equity | 10513900000 | 10513900000 | 9549400000 | 9549400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R6.htm period ..2025-12-28 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 1191300000 | 1191300000 | 1191900000 | 1191900000 | Y | FILING-CHECKED | accn 0001094285-26-000017 R9.htm period ..2025-12-28 / check: hand R9.htm agree |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -937900000 | -937900000 | -207200000 | -207200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R9.htm period ..2025-12-28 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | -555200000 | -555200000 | -945800000 | -945800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R9.htm period ..2025-12-28 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment | -117300000 | 117300000 | -83700000 | 83700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R9.htm period ..2025-12-28 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 336300000 | 336300000 | 309900000 | 309900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R9.htm period ..2025-12-28 |
| sbc | mapped | us-gaap:StockOptionPlanExpense | R9.htm | Stock-based compensation | 39600000 | 39600000 | 37700000 | 37700000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001094285-26-000017 R9.htm period ..2025-12-28 / check: hand R9.htm agree |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1007 tags across all 106 R pages, face and notes) of 0001094285-26-000017; no face row matched / check: hand R9.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchase of treasury stock, including excise tax | -402900000 | 402900000 | -354000000 | 354000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001094285-26-000017 R9.htm period ..2025-12-28 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R70.htm | Long-Term Debt - Narrative (Details) | 71300000 | 71300000 | 73400000 |  | Y | FILING-CHECKED | R70 line includes credit facility fees / check: hand R70.htm corrected: Debt note R70 'Cash payments for interest and credit facility fees' InterestPaidNet 71.3M / 73.4M; printed values were blank. |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R76.htm | Income Taxes - Narrative (Details) | 280200000 | 280200000 | 213200000 |  | Y | FILING-CHECKED | not on the face statement; shown in R76.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R76.htm corrected: Tax note R76 'Cash payments for federal, foreign and state income taxes' IncomeTaxesPaidNet 280.2 / 213.2; printed values were blank. |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current portion of long-term debt and other debt + Long-term debt | 2475400000 | 2475400000 | 2649000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R6.htm corrected: R6 'Current portion of long-term debt and other debt' 450.1 + 'Long-term debt' 2,025.3 = 2,475.4 (FY1 0.3 + 2,648.7 = 2,649.0); no finance lease tags in filing. FY1 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 46185578 | 46185578 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-28; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueNet = 2298100000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 1427800000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 2016400000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 588600000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001094285-16-000177 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 281700000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001094285-16-000177 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 258200000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 62700000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Net income attributable to Teledyne' on us-gaap:NetIncomeLoss = 195800000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Basic earnings per common share (in USD per share)' on us-gaap:EarningsPerShareBasic = 5.55 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Diluted earnings per common share (in USD per share)' on us-gaap:EarningsPerShareDiluted = 5.44 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Weighted average common shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 35300000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001094285-16-000177 R2.htm prints 'Weighted average diluted common shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 36000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Cash' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 85100000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 373000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Inventories, net' on us-gaap:InventoryNet = 309200000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 828200000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 321300000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Goodwill, net' on us-gaap:Goodwill = 1140200000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Total Assets' on us-gaap:Assets = 2718500000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 136500000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 393600000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Total Liabilities' on us-gaap:Liabilities = 1374400000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001094285-16-000177 R5.htm prints 'Total Teledyne Stockholders’ Equity' on us-gaap:StockholdersEquity = 1344100000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001094285-16-000177 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 210200000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001094285-16-000177 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -109900000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001094285-16-000177 R8.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -145000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001094285-16-000177 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -47000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001094285-16-000177 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 90300000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001094285-16-000177 R8.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001094285-16-000177 R8.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -243800000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001094285-16-000177 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001094285-16-000177 R8.htm read; no row matched (auto)
- interest_expense: era 10-K 0001094285-21-000066 R2.htm read; no row matched (auto)
- income_before_tax: era 10-K 0001094285-21-000066 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 469700000 (FILING-CHECKED)
- interest_expense: era 10-K 0001094285-24-000044 R3.htm prints 'Interest and debt expense, net' on us-gaap:InterestExpense = -77300000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 10 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 5.
- Random mapped sample: 3 rows, 1 disagreements (33.3%).
