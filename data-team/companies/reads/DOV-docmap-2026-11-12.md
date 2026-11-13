# DOV document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000029905-26-000009 (CIK 0000029905, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000029905-16-000064 (CIK 0000029905, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000029905-18-000013 (CIK 0000029905, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000029905-19-000019 (CIK 0000029905, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000029905.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 8092571000 | 8092571000 | 7745909000 | 7745909000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods and services | 4874402000 | 4874402000 | 4787288000 | 4787288000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 3218169000 | 3218169000 | 2958621000 | 2958621000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 1844808000 | 1844808000 | 1752266000 | 1752266000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000029905-26-000009 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 1844808000 | 1844808000 | 1752266000 | 1752266000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R56.htm | Description of Business and Summary of Significant Accounting Policies (Details) | 165342000 | 165342000 | 149601000 |  | Y | FILING-CHECKED | not on face IS; R56 accounting policies note R&D expense 165,342,000 / 149,601,000 / check: hand R56.htm corrected: Not on the face IS (inside SG&A/COGS); R56 'Research and development expense' $165,342,000 / $149,601,000. |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating earnings | 1373361000 | 1373361000 | 1206355000 | 1206355000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 109772000 | 109772000 | 131171000 | 131171000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossAttributableToParent | R3.htm | Earnings before provision for income taxes | 1374252000 | 1374252000 | 1757016000 |  | Y | FILING-CHECKED | face IS line tagged IncomeLossAttributableToParent (tag quirk); same value as IncomeLossFromContinuingOperationsBeforeIncomeTaxes... in R56 note / check: hand R3.htm corrected: The face IS does print 'Earnings before provision for income taxes' 1,374,252 / 1,757,016 $K, tagged us-gaap:IncomeLossAttributableToParent (unusual tag); so mapped on the face, not note-only. |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 276823000 | 276823000 | 357048000 | 357048000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 1093956000 | 1093956000 | 2697126000 | 2697126000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 7.99 | 7.99 | 19.58 | 19.58 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 7.94 | 7.94 | 19.45 | 19.45 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 136935000 | 136935000 | 137735000 | 137735000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 137777000 | 137777000 | 138696000 | 138696000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R6.htm | Cash and cash equivalents | 1676808000 | 1676808000 | 1844877000 | 1844877000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Receivables, net | 1371352000 | 1371352000 | 1354225000 | 1354225000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories, net | 1272784000 | 1272784000 | 1144838000 | 1144838000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 4506940000 | 4506940000 | 4484497000 | 4484497000 | Y | FILING-CHECKED | accn 0000029905-26-000009 R6.htm period ..2025-12-31 / check: hand R6.htm agree |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R6.htm | Property, plant and equipment, net | 1119623000 | 1119623000 | 987924000 | 987924000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 5430038000 | 5430038000 | 4905702000 | 4905702000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 13422423000 | 13422423000 | 12509160000 | 12509160000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 875678000 | 875678000 | 848006000 | 848006000 | Y | FILING-CHECKED | accn 0000029905-26-000009 R6.htm period ..2025-12-31 / check: hand R6.htm agree |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 2518489000 | 2518489000 | 2196527000 | 2196527000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| total_liabilities | component sum | us-gaap:LiabilitiesCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:DeferredIncomeTaxLiabilitiesNet+us-gaap:AccruedIncomeTaxesNoncurrent+us-gaap:OtherLiabilitiesNoncurrent | R6.htm | Total current liabilities + noncurrent liability lines | 6017217000 |  | 5555164000 |  |  | FILING-CHECKED | sum of printed liability lines; ties to total liabilities and stockholders' equity less equity (no NCI) / check: hand R6.htm corrected: No total liabilities line; Total current liabilities 2,518,489 + Long-term debt 2,621,295 + Deferred income taxes 394,368 + Non-current income tax payable 0 + Other liabilities 483,065 = 6,017,217 = Total L&SE 13,422,423 - equity 7,405,206; FY1 2,196,527 + 2,529,346 + 352,006 + 6,158 + 471,127 = 5,555,164. |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders' equity | 7405206000 | 7405206000 | 6953996000 | 6953996000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R10.htm | Net cash provided by operating activities | 1338005000 | 1338005000 | 1087833000 | 1087833000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations | R10.htm | Net cash used in investing activities | -886594000 | -886594000 | -26983000 | -26983000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash used in financing activities | -624870000 | -624870000 | -1271673000 | -1271673000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Additions to property, plant and equipment | -220263000 | 220263000 | -167533000 | 167533000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000029905-26-000009 R10.htm period ..2025-12-31 / check: hand R10.htm agree |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation and amortization | 379577000 | 379577000 | 337842000 | 337842000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation expense | 43981000 | 43981000 | 40359000 | 40359000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Dividends paid to stockholders | -283007000 | 283007000 | -283117000 | 283117000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Repurchase of common stock, including payment under accelerated share repurchase program | -540700000 | 540700000 | -500000000 | 500000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Interest | 103892000 | 103892000 | 126434000 | 126434000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R10.htm | Income taxes | 307068000 | 307068000 | 907791000 | 907791000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000029905-26-000009 R10.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiability | R6.htm | Short-term borrowings and current portion of long-term debt + Long-term debt | 3337621000 |  | 2938548000 |  |  | FILING-CHECKED | BS debt lines (R6) + total finance lease liabilities 9,649 / 9,146 from leases note R69 (carried in other accrued expenses and other liabilities) / check: hand R69.htm corrected: ST borrowings and current LTD 706,677 + Long-term debt 2,621,295 = 3,327,972; finance lease liabilities sit in Other accrued expenses / Other liabilities (R69: 4,504 + 5,145 = 9,649), so added: 3,337,621; FY1 400,056 + 2,529,346 + 9,146 = 2,938,548 $K. |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1114 tags across all 124 R pages, face and notes) of 0000029905-26-000009; no face row matched / check: hand R7.htm agree |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 6956311000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Cost of goods and services' on us-gaap:CostOfGoodsAndServicesSold = 4388167000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 2568144000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Selling and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1647382000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Selling and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1647382000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000029905-16-000064 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Operating earnings' on us-gaap:OperatingIncomeLoss = 920762000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Interest expense, net' on us-gaap:InterestRevenueExpenseNet = 127257000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Earnings before provision for income taxes and discontinued operations' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 800610000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 204729000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 869829000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Net earnings (in dollars per basic share)' on us-gaap:EarningsPerShareBasic = 5.52 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Net earnings (in dollars per diluted share)' on us-gaap:EarningsPerShareDiluted = 5.46 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Weighted average shares outstanding - basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 157619000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000029905-16-000064 R2.htm prints 'Weighted average shares outstanding - diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 159172000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 362185000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Receivables, net of allowances' on us-gaap:AccountsReceivableNetCurrent = 1120490000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Inventories, net' on us-gaap:InventoryNet = 802895000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2420779000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 854269000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 3737389000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Total assets' on us-gaap:Assets = 8619763000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 650880000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1367182000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000029905-16-000064 R4.htm prints 'Total liabilities and stockholders' equity' on us-gaap:LiabilitiesAndStockholdersEquity = 8619763000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Net cash provided by operating activities of continuing operations' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 949059000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Net cash used in investing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -34578000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Net cash provided by (used in) financing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -1091886000 (FILING-CHECKED)
- capex: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Additions to property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -154251000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 327089000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 30697000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Dividends to stockholders' on us-gaap:PaymentsOfDividendsCommonStock = -257969000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Purchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -600164000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Interest' on us-gaap:InterestPaid = 128151000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000029905-16-000064 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 346382000 (FILING-CHECKED)
- revenue: era 10-K 0000029905-18-000013 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 7830436000 (FILING-CHECKED)
- revenue: era 10-K 0000029905-19-000019 R2.htm prints 'Revenue' on us-gaap:Revenues = 6992118000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000029905-19-000019 R6.htm prints 'Interest' on us-gaap:InterestPaid = 131823000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 9 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 4.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
