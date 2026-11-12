# AVAV document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-078906 (CIK 0001368622, filed 2026-06-29): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001047469-15-005880 (CIK 0001368622, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001558370-18-005457 (CIK 0001368622, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001558370-25-008838 (CIK 0001368622, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001368622.json (one call); submissions CIK0001368622.json (SIC 3721).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Revenue | 1976845000 | 1976845000 | 820627000 | 820627000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of sales | 1476203000 | 1476203000 | 501991000 | 501991000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Total gross margin | 500642000 | 500642000 | 318636000 | 318636000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:GoodwillImpairmentLoss | R4.htm | Selling, general and administrative + Research and development + Impairment of goodwill | 811637000 | 811637000 | 277841000 | 277841000 | Y | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative | 443251000 | 443251000 | 158753000 | 158753000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 127678000 | 127678000 | 100729000 | 100729000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | (Loss) income from operations | -310995000 | -310995000 | 40795000 | 40795000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R4.htm | Interest expense, net | -5613000 | -5613000 | -2188000 | -2188000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R4.htm | (Loss) income before income taxes | -305622000 | -305622000 | 39664000 | 39664000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | (Benefit from) provision for income taxes | -23059000 | -23059000 | 882000 | 882000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| net_income | mapped | us-gaap:ProfitLoss | R4.htm | Net (loss) income | -265122000 | -265122000 | 43619000 | 43619000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (in dollars per share) | -5.4 | -5.4 | 1.56 | 1.56 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (in dollars per share) | -5.4 | -5.4 | 1.55 | 1.55 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 49087346 | 49087346 | 28018656 | 28018656 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 49087346 | 49087346 | 28173488 | 28173488 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 377325000 | 377325000 | 40862000 | 40862000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net of allowance for credit losses of $1,961 at April 30, 2026 and $203 at April 30, 2025 | 316167000 | 316167000 | 101967000 | 101967000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories, net | 312856000 | 312856000 | 144090000 | 144090000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 1890423000 | 1890423000 | 606516000 | 606516000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 166719000 | 166719000 | 50704000 | 50704000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 2493678000 | 2493678000 | 256781000 | 256781000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 5716742000 | 5716742000 | 1120567000 | 1120567000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 160507000 | 160507000 | 72462000 | 72462000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 439237000 | 439237000 | 172161000 | 172161000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| total_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1093 tags across all 114 R pages, face and notes) of 0001104659-26-078906; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R2.htm | Total stockholders' equity | 4400400000 | 4400400000 | 886507000 | 886507000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash (used in) provided by operating activities | -78404000 | -78404000 | -1318000 | -1318000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -1232671000 | -1232671000 | -28490000 | -28490000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 1647178000 | 1647178000 | -2856000 | -2856000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Acquisition of property and equipment | -62544000 | 62544000 | -19547000 | 19547000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 265037000 | 265037000 | 40998000 | 40998000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 38334000 | 38334000 | 21461000 | 21461000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends, PaymentsOfOrdinaryDividends, PaymentsOfCapitalDistribution in MetaLinks.json (1093 tags across all 114 R pages, face and notes) of 0001104659-26-078906; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1093 tags across all 114 R pages, face and notes) of 0001104659-26-078906; HAND REVIEW: 6 label candidate(s) incl. custom tags: us-gaap:CommonStockSharesIssued 'Common Stock, Shares, Issued / Common stock, Issued shares /' R3; us-gaap:CommonStockValue 'Common Stock, Value, Issued / Issued and outstanding shares-' R2; us-gaap:InvestmentTypeExtensibleEnumeration 'Investment, Type [Extensible Enumeration] / Indicates type o' R68; us-gaap:PreferredStockSharesIssued 'Preferred Stock, Shares Issued / Preferred stock, issued sha' R3; us-gaap:PreferredStockSharesOutstanding 'Preferred Stock, Shares Outstanding / Preferred stock, outst' R3; us-gaap:PreferredStockValue 'Preferred Stock, Value, Issued / Authorized shares-10,000,00' R2 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 12847000 | 12847000 | 1757000 | 1757000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes | 3606000 | 3606000 | 24631000 | 24631000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R2.htm | Long-term debt | 728967000 | 728967000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, outstanding shares | 50610514 | 50610514 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-04-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Total revenue' on us-gaap:Revenues = 259398000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Total cost of sales' on us-gaap:CostOfRevenue = 155130000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Gross margin' on us-gaap:GrossProfit = 104268000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Selling, general and administrative + Research and development' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense = 102254000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 55763000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 46491000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 2014000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-15-005880 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1893000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -1002000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Net income' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 2895000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.13 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.13 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 22868733 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-15-005880 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 23145997 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 143410000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $606 at April 30,' on us-gaap:AccountsReceivableNetCurrent = 33607000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 39414000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 329032000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 13499000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-15-005880 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Total assets' on us-gaap:Assets = 397467000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 19243000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 46735000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-15-005880 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 348912000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 39413000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -23820000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 848000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Acquisition of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -5279000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 8366000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 3768000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-15-005880 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-15-005880 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 700000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-18-005457 R4.htm prints 'Total revenue' on us-gaap:Revenues = 271052000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001558370-18-005457 R4.htm prints 'Total cost of sales' on us-gaap:CostOfRevenue = 162164000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-25-008838 R4.htm prints 'Revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 820627000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
