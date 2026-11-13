# VRSK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001437749-26-004452 (CIK 0001442145, filed 2026-02-18): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001442145-16-000057 (CIK 0001442145, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001442145-18-000008 (CIK 0001442145, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001437749-24-004939 (CIK 0001442145, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001442145.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Revenues | 3072700000 | 3072700000 | 2881700000 | 2881700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Cost of revenues (exclusive of items shown separately below) | 925500000 | 925500000 | 901100000 | 901100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1041 tags across all 112 R pages, face and notes) of 0001437749-26-004452; no face row matched / check: hand R4.htm agree |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:DepreciationAndAmortization+us-gaap:AmortizationOfIntangibleAssets+us-gaap:GainLossOnSalesOfAssetsAndAssetImpairmentCharges | R4.htm | Total operating expenses | 803300000 |  | 726700000 |  |  | FILING-CHECKED | every non-COGS face line in Total operating expenses; ties to revenue - cost of revenues - OI; CostsAndExpenses 1,728.8 includes COGS / check: hand R4.htm corrected: 'Total operating expenses' 1,728.8 (CostsAndExpenses) includes Cost of revenues 925.5; the non-COGS face lines SG&A 458.2 + D&A of fixed assets 259.2 + amortization of intangibles 67.5 + loss on sale 18.4 = 803.3 = revenue 3,072.7 - COGS 925.5 - OI 1,343.9 -> component sum. |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative | 458200000 | 458200000 | 408700000 | 408700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R55.htm | Note 2 - Basis of Presentation and Summary of Significant Accounting Policies (Details Textual) | 40900000 | 40900000 | 35300000 |  | Y | FILING-CHECKED | not on the face statement; shown in R55.htm 'Note 2 - Basis of Presentation and Summary of Significant Accounting Policies (D' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R55.htm corrected: Note 2 details R55 print Research and Development Expense 40.9M (FY1 35.3M). |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 1343900000 | 1343900000 | 1253900000 | 1253900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestExpenseNonoperating | R4.htm | Interest expense, net | -170900000 | 170900000 | -124600000 | 124600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Total income before income taxes | 1171300000 | 1171300000 | 1228600000 | 1228600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Provision for income taxes | -263000000 | 263000000 | -277900000 | 277900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to Verisk | 908300000 | 908300000 | 958200000 | 958200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic net income per share attributable to Verisk: (in dollars per share) | 6.5 | 6.5 | 6.74 | 6.74 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted net income per share attributable to Verisk: (in dollars per share) | 6.48 | 6.48 | 6.71 | 6.71 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 139667160 | 139667160 | 142154655 | 142154655 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 140082773 | 140082773 | 142842261 | 142842261 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 2178200000 | 2178200000 | 291200000 | 291200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net | 422200000 | 422200000 | 434400000 | 434400000 | Y | FILING-CHECKED | accn 0001437749-26-004452 R2.htm period ..2025-12-31 / check: hand R2.htm agree |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1041 tags across all 112 R pages, face and notes) of 0001437749-26-004452; no face row matched / check: hand R2.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2765400000 | 2765400000 | 911600000 | 911600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R2.htm | Fixed assets, net | 582800000 | 582800000 | 605900000 | 605900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1878200000 | 1878200000 | 1726600000 | 1726600000 | Y | FILING-CHECKED | accn 0001437749-26-004452 R2.htm period ..2025-12-31 / check: hand R2.htm agree |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 6195500000 | 6195500000 | 4264700000 | 4264700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R2.htm | Accounts payable and accrued liabilities | 319100000 | 319100000 | 249800000 | 249800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 2300300000 | 2300300000 | 1238900000 | 1238900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 5885700000 | 5885700000 | 4159700000 | 4159700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total Verisk stockholders' equity | 309000000 | 309000000 | 100100000 | 100100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1436000000 | 1436000000 | 1144000000 | 1144000000 | Y | FILING-CHECKED | accn 0001437749-26-004452 R9.htm period ..2025-12-31 / check: hand R9.htm agree |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -358100000 | -358100000 | -124800000 | -124800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 795200000 | 795200000 | -1028500000 | -1028500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -244100000 | 244100000 | -223900000 | 223900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization of fixed assets | 259200000 | 259200000 | 233600000 | 233600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 54200000 | 54200000 | 47900000 | 47900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid | -251100000 | 251100000 | -221300000 | 221300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -624000000 | 624000000 | -1005000000 | 1005000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 150300000 | 150300000 | 131600000 | 131600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Income taxes paid | 218000000 | 218000000 | 287700000 | 287700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001437749-26-004452 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R2.htm | Short-term debt and current portion of long-term debt + Long-term debt | 4737200000 | 4737200000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R89.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock outstanding (in shares) | 138397709 | 138397709 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Revenues' on us-gaap:SalesRevenueServicesNet = 2068010000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Cost of revenues (exclusive of items shown separately below)' on us-gaap:CostOfServices = 803274000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Total expenses' on us-gaap:CostsAndExpenses = 1331448000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 312690000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001442145-16-000057 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 736562000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -121316000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 717436000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -209859000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 507577000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Basic net income per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.07 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Diluted net income per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.01 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 165090380 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001442145-16-000057 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 168451343 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 138348000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 320099000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 604569000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 418168000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 3134826000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Total assets' on us-gaap:Assets = 5615927000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 245664000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1479257000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 4243916000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001442145-16-000057 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 1372011000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 623687000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -3006317000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 2481013000 (FILING-CHECKED)
- capex: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -166138000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Depreciation and amortization of fixed assets' on us-gaap:DepreciationDepletionAndAmortization = 120620000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Stock based compensation' on us-gaap:ShareBasedCompensation = 30542000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001442145-16-000057 R9.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -20456000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Interest paid' on us-gaap:InterestPaid = 106098000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001442145-16-000057 R9.htm prints 'Taxes paid' on us-gaap:IncomeTaxesPaid = 158494000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001442145-18-000008 R4.htm prints 'Cost of revenues (exclusive of items shown separately below)' on us-gaap:CostOfServices = 783800000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001442145-18-000008 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 113900000 (FILING-CHECKED)
- interest_expense: era 10-K 0001437749-24-004939 R4.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -115500000 (FILING-CHECKED)
- ppe_net: era 10-K 0001437749-24-004939 R2.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 604900000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 8 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
