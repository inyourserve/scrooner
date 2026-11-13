# AXON document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-011360 (CIK 0001069183, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001069183-16-000148 (CIK 0001069183, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001069183-18-000020 (CIK 0001069183, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001069183-25-000019 (CIK 0001069183, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- companyfacts CIK0001069183.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 2779536000 | 2779536000 | 2082526000 | 2082526000 | Y | FILING-CHECKED | accn 0001628280-26-011360 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 1121411000 | 1121411000 | 841146000 | 841146000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross margin | 1658125000 | 1658125000 | 1241380000 | 1241380000 | Y | FILING-CHECKED | accn 0001628280-26-011360 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1720201000 | 1720201000 | 1182840000 | 1182840000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1035893000 | 1035893000 | 741247000 | 741247000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 684308000 | 684308000 | 441593000 | 441593000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income (loss) from operations | -62076000 | -62076000 | 58540000 | 58540000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -94238000 | 94238000 | -7098000 | 7098000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 18974000 | 18974000 | 381504000 | 381504000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | -105682000 | -105682000 | 4470000 | 4470000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 124656000 | 124656000 | 377034000 | 377034000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.6 | 1.6 | 4.98 | 4.98 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.51 | 1.51 | 4.8 | 4.8 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 78081000 | 78081000 | 75748000 | 75748000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 82370000 | 82370000 | 78558000 | 78558000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1201147000 | 1201147000 | 454844000 | 454844000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| accounts_receivable | combined | us-gaap:AccountsNotesAndLoansReceivableNetCurrent | R3.htm | Accounts and notes receivable, net | 777486000 |  | 547572000 |  |  | FILING-CHECKED | single face receivables line combines trade accounts and current notes receivable; notes are never AR, so combined / check: hand R3.htm corrected: Face prints a single receivables line 'Accounts and notes receivable, net' 777,486 / 547,572 on AccountsNotesAndLoansReceivableNetCurrent; it includes notes receivable, so keyed combined rather than not_presented. |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 341811000 | 341811000 | 265316000 | 265316000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 3713052000 | 3713052000 | 2297481000 | 2297481000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 330979000 | 330979000 | 247324000 | 247324000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1370189000 | 1370189000 | 756838000 | 756838000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7000313000 | 7000313000 | 4474588000 | 4474588000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 139086000 | 139086000 | 71955000 | 71955000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1470147000 | 1470147000 | 1677875000 | 1677875000 | Y | FILING-CHECKED | accn 0001628280-26-011360 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3757655000 | 3757655000 | 2146923000 | 2146923000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 3242658000 | 3242658000 | 2327665000 | 2327665000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 211339000 | 211339000 | 408312000 | 408312000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | -724930000 | -724930000 | -490573000 | -490573000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | 1252465000 | 1252465000 | -45437000 | -45437000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -136258000 | 136258000 | -78785000 | 78785000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 83161000 | 83161000 | 48425000 | 48425000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 634231000 | 634231000 | 382604000 | 382604000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1031 tags across all 111 R pages, face and notes) of 0001628280-26-011360; no face row matched / check: hand R7.htm agree |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | no share repurchase line in R7; prior match was a debt issuance cost line; tax withholding excluded by rule 13 / check: hand R7.htm corrected: Row keyed on PaymentsOfDebtIssuanceCosts 'Payments to third parties for debt issuance, amendment and repurchase activity' (26,994): debt costs, not a share buyback; the only other equity outflow is net-settlement tax withholding (350,981), never a buyback; no repurchase line. |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 57173000 | 57173000 | 3450000 | 3450000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes, net of refunds | 51121000 | 51121000 | 67845000 | 67845000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011360 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:NotesPayableCurrent+us-gaap:LongTermNotesPayable | R3.htm | Current portion of notes payable, net + Long-term notes payable, net | 1810722000 | 1810722000 | 680289000 |  | Y | FILING-CHECKED | sum of face debt lines; equals R71 LongTermDebt 1,810,722,000; no finance-lease tags in filing / check: hand R3.htm corrected: Face prints Current portion of notes payable, net 80,552 / 680,289 and Long-term notes payable, net 1,730,170 / 0; sum 1,810,722 / 680,289 ties to R71 Total carrying amount (LongTermDebt); no finance leases. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 80211537 | 80211537 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 197892000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Cost of products sold and services delivered' on us-gaap:CostOfGoodsAndServicesSold = 69245000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Gross margin' on us-gaap:GrossProfit = 128647000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 93312000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Sales, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 69698000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 23614000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 35335000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Interest and other income (expense), net' on us-gaap:InterestIncomeExpenseNonoperatingNet = 26000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 35361000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 15428000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 19933000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.37 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.36 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 53548000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001069183-16-000148 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 54638000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 59526000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 15763000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 161409000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 21848000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 9596000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Total assets' on us-gaap:Assets = 229881000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 7333000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 38140000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 72877000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001069183-16-000148 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 157004000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 46445000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -36009000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 603000 (FILING-CHECKED)
- capex: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -6003000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 3291000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 7263000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001069183-16-000148 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -7556000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001069183-16-000148 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001069183-16-000148 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001069183-18-000020 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 343798000 (FILING-CHECKED)
- interest_expense: era 10-K 0001069183-25-000019 R5.htm prints 'Interest income, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = 36595000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 3.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
