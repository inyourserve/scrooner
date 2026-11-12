# BURL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-116001 (CIK 0001579298, filed 2026-03-19): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001564590-16-014854 (CIK 0001579298, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001564590-18-006339 (CIK 0001579298, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000950170-25-040472 (CIK 0001579298, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001579298.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R2.htm | Total revenue | 11566910000 | 11566910000 | 10634823000 | 10634823000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of sales | 6486922000 | 6486922000 | 6025272000 | 6025272000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (997 tags across all 99 R pages, face and notes) of 0001193125-26-116001; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R2.htm | Total costs and expenses | 10750792000 | 10750792000 | 9960009000 | 9960009000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 3817180000 | 3817180000 | 3546967000 | 3546967000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (997 tags across all 99 R pages, face and notes) of 0001193125-26-116001; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsTaxCreditCarryforwards 'Deferred Tax Assets, Tax Credit Carryforwards, Total / Tax c' R87 |
| operating_income | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (997 tags across all 99 R pages, face and notes) of 0001193125-26-116001; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:OtherNonoperatingIncomeExpense 'Other Nonoperating Income (Expense), Total / Other income - ' R46,R2 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R2.htm | Interest expense | 71041000 | 71041000 | 69522000 | 69522000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income tax expense | 816118000 | 816118000 | 674814000 | 674814000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income tax expense | 205965000 | 205965000 | 171175000 | 171175000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income | 610153000 | 610153000 | 503639000 | 503639000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Net income per common share - basic | 9.69 | 9.69 | 7.91 | 7.91 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Net income per common share - diluted | 9.51 | 9.51 | 7.8 | 7.8 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Weighted average number of common stock - basic | 62984000 | 62984000 | 63634000 | 63634000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Weighted average number of common stock - diluted | 64126000 | 64126000 | 64595000 | 64595000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R2.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 1232525000 | 1232525000 | 994698000 | 994698000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable-net of allowance for doubtful accounts of $1,611 and $2,959, respectively | 105296000 | 105296000 | 88079000 | 88079000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Merchandise inventories | 1311903000 | 1311903000 | 1250775000 | 1250775000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 2771532000 | 2771532000 | 2628803000 | 2628803000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property and equipment—net | 3164218000 | 3164218000 | 2369720000 | 2369720000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 47064000 | 47064000 | 47064000 | 47064000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 9919057000 | 9919057000 | 8770413000 | 8770413000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 1019152000 | 1019152000 | 1038148000 | 1038148000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 2249211000 | 2249211000 | 2272511000 | 2272511000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (997 tags across all 99 R pages, face and notes) of 0001193125-26-116001; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total stockholders' equity | 1807259000 | 1807259000 | 1370496000 | 1370496000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R4.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 1231382000 | 1231382000 | 863376000 | 863376000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -1055050000 | -1055050000 | -882254000 | -882254000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used in) financing activities | 61495000 | 61495000 | 88217000 | 88217000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Cash paid for property and equipment | -1059793000 | 1059793000 | -880384000 | 880384000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 417871000 | 417871000 | 347575000 | 347575000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Non-cash stock compensation expense | 106732000 | 106732000 | 87572000 | 87572000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| dividends_paid | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (997 tags across all 99 R pages, face and notes) of 0001193125-26-116001; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Purchase of treasury shares | -278422000 | 278422000 | -256293000 | 256293000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Interest paid | 73076000 | 73076000 | 84614000 | 84614000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R6.htm | Income tax payments - net | 170886000 | 170886000 | 170259000 | 170259000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-116001 R6.htm period ..2026-01-31 |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R4.htm | Current maturities of long term debt and other current debt + Long term debt | 2082326000 | 2082326000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Common Stock, Shares Outstanding | 62717720 | 62717720 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-01-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Total revenue' on us-gaap:Revenues = 5129843000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 3059641000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Total cost and expenses' on us-gaap:CostsAndExpenses = 4890967000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1597718000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Interest expense (inclusive of gain (loss) on interest rate cap agreements)' on us-gaap:InterestIncomeExpenseNonoperatingNet = 58999000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Income before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 238876000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 88394000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 150482000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Net income (loss) per share - basic' on us-gaap:EarningsPerShareBasic = 2.03 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Net income (loss) per share - diluted' on us-gaap:EarningsPerShareDiluted = 1.99 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Weighted average number of shares - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 74111000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-014854 R4.htm prints 'Weighted average number of shares - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 75443000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 20915000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Accounts receivable—net of allowance for doubtful accounts of $272 and $111 at J' on us-gaap:AccountsReceivableNetCurrent = 38571000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Merchandise inventories' on us-gaap:InventoryNet = 783528000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 932982000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Property and equipment—net of accumulated depreciation and amortization' on us-gaap:PropertyPlantAndEquipmentNet = 1018570000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 47064000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Total assets' on us-gaap:Assets = 2580147000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 598199000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 886588000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-014854 R2.htm prints 'Total stockholders' deficit' on us-gaap:StockholdersEquity = -99022000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 327461000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -194732000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -137163000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Cash paid for property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -201787000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 172099000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Non-cash stock compensation expense' on us-gaap:ShareBasedCompensation = 11161000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Purchase of treasury shares' on burl:PaymentsForRepurchaseOfTreasuryStock = -201670000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 57376000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-014854 R7.htm prints 'Income tax payments - net' on us-gaap:IncomeTaxesPaidNet = 84676000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001564590-18-006339 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 3559158000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-006339 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 607250000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-006339 R6.htm prints 'Net cash (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -262208000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-006339 R6.htm prints 'Net cash (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -293353000 (FILING-CHECKED)
- interest_expense: era 10-K 0000950170-25-040472 R2.htm prints 'Interest expense' on us-gaap:InterestIncomeExpenseNonoperatingNet = 69522000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 10 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:BURL); disagree on the mapped sample: 0/3
- cash_flow_investing: agree (R6 -1,055,050)
- cost_of_revenue: agree (R2 Cost of sales 6,486,922)
- dividends_paid: agree (R6 prints no dividend line)
- gross_profit: agree (R2 prints no gross profit line)
- inventory: agree (R4 Merchandise inventories 1,311,903)
- operating_expenses: agree (R2 'Total costs and expenses' CostsAndExpenses 10,750,792 includes cost of sales 6,486,922: combined, never opex)
- operating_income: agree (R2 prints no operating income line (costs and expenses then income before tax); the lead is other nonoperating income)
- research_and_development: agree (no R&D line; the lead is a tax credit carryforward (R87))
- total_debt: agree (R4 current maturities of long term debt and other current debt 70,591 + long term debt 2,011,735 = 2,082,326 (thousands); finance-lease rule checked: debt lines are LongTermDebtAndCapitalLeaseObligations(Current) and R52 lists FinanceLeaseLiability inside long-term debt: nothing added)
- total_liabilities: agree (R4 prints no total liabilities line; Liabilities is not in the filing)
