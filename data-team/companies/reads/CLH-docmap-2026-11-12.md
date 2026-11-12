# CLH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000822818-26-000009 (CIK 0000822818, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R8.htm
- 10-K 0000822818-16-000033 (CIK 0000822818, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CF R8.htm
- 10-K 0000822818-18-000006 (CIK 0000822818, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R8.htm
- 10-K 0000822818-21-000003 (CIK 0000822818, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0000822818.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 6030837000 | 6030837000 | 5889952000 | 5889952000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Total cost of revenues | 4144599000 | 4144599000 | 4065713000 | 4065713000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1008 tags across all 113 R pages, face and notes) of 0000822818-26-000009; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1008 tags across all 113 R pages, face and notes) of 0000822818-26-000009; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:CostsAndExpensesRelatedParty 'Third-party transaction related costs / Costs and Expenses, ' R111; us-gaap:OperatingIncomeLoss 'Income from operations / Operating Income (Loss) / The net r' R5,R111 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 752534000 | 752534000 | 739629000 | 739629000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1008 tags across all 113 R pages, face and notes) of 0000822818-26-000009; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsTaxCreditCarryforwards 'Tax credit carryforwards / Deferred Tax Assets, Tax Credit C' R91 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 673372000 | 673372000 | 670232000 | 670232000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense, net of interest income of $25,749, $19,437 and $11,930, respectively | -143104000 | -143104000 | -134964000 | -134964000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 527967000 | 527967000 | 533443000 | 533443000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 136993000 | 136993000 | 131144000 | 131144000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 390974000 | 390974000 | 402299000 | 402299000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 7.31 | 7.31 | 7.46 | 7.46 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 7.28 | 7.28 | 7.42 | 7.42 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Shares used to compute earnings per share — Basic (in shares) | 53509000 | 53509000 | 53902000 | 53902000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Shares used to compute earnings per share — Diluted (in shares) | 53716000 | 53716000 | 54199000 | 54199000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and cash equivalents | 826315000 | 826315000 | 687192000 | 687192000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances aggregating $35,991 and $47,242, respectively | 1044137000 | 1044137000 | 1015357000 | 1015357000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories and supplies | 372088000 | 372088000 | 384657000 | 384657000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2647243000 | 2647243000 | 2433796000 | 2433796000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant and equipment, net | 2541067000 | 2541067000 | 2447941000 | 2447941000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1479050000 | 1479050000 | 1477199000 | 1477199000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7624056000 | 7624056000 | 7377278000 | 7377278000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 506592000 | 506592000 | 487286000 | 487286000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1136847000 | 1136847000 | 1102666000 | 1102666000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1008 tags across all 113 R pages, face and notes) of 0000822818-26-000009; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 2745660000 | 2745660000 | 2573529000 | 2573529000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash from operating activities | 866725000 | 866725000 | 777771000 | 777771000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -425786000 | -425786000 | -903674000 | -903674000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) from financing activities | -309342000 | -309342000 | 377032000 | 377032000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Additions to property, plant and equipment | -424918000 | 424918000 | -432241000 | 432241000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 446006000 | 446006000 | 400922000 | 400922000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 32702000 | 32702000 | 27981000 | 27981000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1008 tags across all 113 R pages, face and notes) of 0000822818-26-000009; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -250002000 | 250002000 | -55178000 | 55178000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 157263000 | 157263000 | 153059000 | 153059000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid, net of refunds | 117904000 | 117904000 | 130606000 | 130606000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000822818-26-000009 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of long-term debt + Long-term debt, less current portion | 2776163000 | 2776163000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding shares (in shares) | 52870599 | 52870599 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0000822818-16-000033 statement not identified (auto)
- cost_of_revenue: 10-K 0000822818-16-000033 statement not identified (auto)
- sga_expense: 10-K 0000822818-16-000033 statement not identified (auto)
- operating_income: 10-K 0000822818-16-000033 statement not identified (auto)
- interest_expense: 10-K 0000822818-16-000033 statement not identified (auto)
- income_before_tax: 10-K 0000822818-16-000033 statement not identified (auto)
- income_tax_expense: 10-K 0000822818-16-000033 statement not identified (auto)
- net_income: 10-K 0000822818-16-000033 statement not identified (auto)
- basic_eps: 10-K 0000822818-16-000033 statement not identified (auto)
- diluted_eps: 10-K 0000822818-16-000033 statement not identified (auto)
- weighted_basic_shares: 10-K 0000822818-16-000033 statement not identified (auto)
- weighted_diluted_shares: 10-K 0000822818-16-000033 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 184708000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Accounts receivable, net of allowances aggregating $31,426 and $25,661, respecti' on us-gaap:AccountsReceivableNetCurrent = 496004000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Inventories and supplies' on us-gaap:Supplies = 149521000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 921196000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1532467000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 453105000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Total assets' on us-gaap:Assets = 3431428000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 241183000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 517120000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000822818-16-000033 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1096282000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Net cash from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 396383000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -350642000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Net cash (used in) from financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -90179000 (FILING-CHECKED)
- capex: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Additions to property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -257196000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 274194000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 8550000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -73347000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 73926000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000822818-16-000033 R8.htm prints 'Income taxes paid (received)' on us-gaap:IncomeTaxesPaidNet = 52970000 (FILING-CHECKED)
- revenue: era 10-K 0000822818-18-000006 R4.htm prints 'Total revenues' on us-gaap:Revenues = 2944978000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000822818-18-000006 R4.htm prints 'Total cost of revenues' on us-gaap:CostOfRevenue = 2062673000 (FILING-CHECKED)
- net_income: era 10-K 0000822818-18-000006 R4.htm prints 'Net income (loss)' on us-gaap:ProfitLoss = 100739000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000822818-21-000003 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 174550000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 10 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:CLH); disagree on the mapped sample: 0/3
- dividends_paid: agree (R8 financing prints no dividend line)
- goodwill: agree (R3 Goodwill 1,479,050)
- gross_profit: agree (R5 prints no gross profit line; MetaLinks has no GrossProfit)
- interest_expense: agree (R5 'Interest expense, net of interest income' = net line: combined)
- operating_expenses: agree (R5 has no total opex and no gross profit line; label leads (R111 related-party costs, operating income) are not opex)
- research_and_development: agree (no R&D line on R5; the only lead is a tax credit carryforward (R91))
- revenue: agree (R5 Total revenues 6,030,837)
- total_assets: agree (R3 Total assets 7,624,056)
- total_debt: agree (R3 current portion 12,600 + long-term 2,763,563 = 2,776,163 (thousands); no lease or other borrowing line under debt)
- total_liabilities: agree (R3 goes from total other liabilities to equity: no total liabilities line)
