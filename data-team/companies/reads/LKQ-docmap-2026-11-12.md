# LKQ document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001065696-26-000012 (CIK 0001065696, filed 2026-02-19): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001065696-16-000076 (CIK 0001065696, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001065696-19-000010 (CIK 0001065696, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001065696-20-000008 (CIK 0001065696, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001065696.json (one call); submissions CIK0001065696.json (SIC 5010).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenues | 13651000000 | 13651000000 | 13823000000 | 13823000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods sold | 8386000000 | 8386000000 | 8439000000 | 8439000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross margin | 5265000000 | 5265000000 | 5384000000 | 5384000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+lkq:RestructuringChargesAndBusinessCombinationAcquisitionRelatedCosts+us-gaap:GoodwillImpairmentLoss+us-gaap:DepreciationAndAmortization | R3.htm | Selling, general and administrative expenses + Restructuring and transaction related expenses + Impairment of goodwill + | 4272000000 |  | 4239000000 |  | API missing | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 3813000000 | 3813000000 | 3758000000 | 3758000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1104 tags across all 123 R pages, face and notes) of 0001065696-26-000012; HAND REVIEW: 3 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsTaxCreditCarryforwards 'Deferred Tax Assets, Tax Credit Carryforwards / Deferred Tax' R112; us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R111; us-gaap:IncomeTaxReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R111 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 993000000 | 993000000 | 1145000000 | 1145000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 224000000 | -224000000 | 238000000 | -238000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income from continuing operations before provision for income taxes | 800000000 | 800000000 | 926000000 | 926000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Effective tax rate | 204000000 | 204000000 | 265000000 | 265000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:ProfitLoss | R3.htm | Net income | 608000000 | 608000000 | 693000000 | 693000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income attributable to LKQ stockholders | 2.36 | 2.36 | 2.62 | 2.62 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income attributable to LKQ stockholders | 2.35 | 2.35 | 2.62 | 2.62 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R80.htm | Denominator for basic earnings per share—Weighted-average shares outstanding | 257500000 | 257500000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R80.htm 'Schedule of Earnings Per Share, Basic and Diluted (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R80.htm | Denominator for diluted earnings per share—Adjusted weighted-average shares outstanding | 257800000 | 257800000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R80.htm 'Schedule of Earnings Per Share, Basic and Diluted (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 319000000 | 319000000 | 234000000 | 234000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net of allowance for credit losses | 1204000000 | 1204000000 | 1113000000 | 1113000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 3426000000 | 3426000000 | 3183000000 | 3183000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 5248000000 | 5248000000 | 4906000000 | 4906000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 1452000000 | 1452000000 | 1409000000 | 1409000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 5414000000 | 5414000000 | 5174000000 | 5174000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 15137000000 | 15137000000 | 14955000000 | 14955000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2108000000 | 2108000000 | 1797000000 | 1797000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 3137000000 | 3137000000 | 2862000000 | 2862000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1104 tags across all 123 R pages, face and notes) of 0001065696-26-000012; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Company stockholders' equity | 6537000000 | 6537000000 | 6017000000 | 6017000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1063000000 | 1063000000 | 1121000000 | 1121000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | 185000000 | 185000000 | -406000000 | -406000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used in) provided by financing activities | -1191000000 | -1191000000 | -746000000 | -746000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Purchases of property, plant and equipment | -216000000 | 216000000 | -311000000 | 311000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 418000000 | 418000000 | 406000000 | 406000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R7.htm | Stock-based compensation expense | 34000000 | 34000000 | 30000000 | 30000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid to LKQ stockholders | -310000000 | 310000000 | -318000000 | 318000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchase of treasury stock | -159000000 | 159000000 | -360000000 | 360000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest | 230000000 | 230000000 | 230000000 | 230000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes, net of refunds | 300000000 | 300000000 | 322000000 | 322000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001065696-26-000012 R7.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:NotesPayable | R83.htm | Schedule of Long-Term Obligations (Details) |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / only component tag(s) NotesPayable in the filing (R83.htm 'Schedule of Long-Term Obligations (Details)'); the data point itself is not reported |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Common Stock, Shares, Outstanding | 255000000 | 255000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 7192633000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsAndServicesSold = 4359104000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Gross margin' on us-gaap:GrossProfit = 2833529000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001065696-16-000076 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 828333000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 704627000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Interest expense' on us-gaap:InterestAndDebtExpense = -57860000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 649030000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 219703000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 423223000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Basic' on us-gaap:IncomeLossFromContinuingOperationsPerBasicShare = 1.39 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001065696-16-000076 R4.htm prints 'Diluted' on us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare = 1.38 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001065696-16-000076 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001065696-16-000076 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Cash and equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 87397000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 590160000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 1556552000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 2340712000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Property and Equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 696567000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 2319246000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Total Assets' on us-gaap:Assets = 5647837000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 415588000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 751970000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001065696-16-000076 R2.htm prints 'Total Stockholders' Equity' on us-gaap:StockholdersEquity = 3114682000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 529837000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -329993000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -224092000 (FILING-CHECKED)
- capex: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquireProductiveAssets = -170490000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 128192000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Stock-based compensation expense' on us-gaap:AllocatedShareBasedCompensationExpense = 21336000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001065696-16-000076 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001065696-16-000076 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Interest' on us-gaap:InterestPaidNet = 54917000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001065696-16-000076 R6.htm prints 'Income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 180126000 (FILING-CHECKED)
- revenue: era 10-K 0001065696-19-000010 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 11876674000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001065696-19-000010 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 331761000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001065696-19-000010 R6.htm prints 'Interest' on us-gaap:InterestPaidNet = 137866000 (FILING-CHECKED)
- interest_expense: era 10-K 0001065696-20-000008 R2.htm prints 'Interest expense' on us-gaap:InterestAndDebtExpense = 138504000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+lkq:RestructuringChargesAndBusinessCombinationAcquisitionRelatedCosts+us-gaap:GoodwillImpairmentLoss+us-gaap:DepreciationAndAmortization)
