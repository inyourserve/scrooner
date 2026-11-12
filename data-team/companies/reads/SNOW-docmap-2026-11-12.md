# SNOW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001640147-26-000008 (CIK 0001640147, filed 2026-03-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001640147-24-000101 (CIK 0001640147, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001640147-21-000073 (CIK 0001640147, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001640147.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 4683946000 | 4683946000 | 3626396000 | 3626396000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenue | 1537805000 | 1537805000 | 1214673000 | 1214673000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 3146141000 | 3146141000 | 2411723000 | 2411723000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 4581306000 | 4581306000 | 3867733000 | 3867733000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 549697000 | 549697000 | 412262000 | 412262000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 1969472000 | 1969472000 | 1783379000 | 1783379000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating loss | -1435165000 | -1435165000 | -1456010000 | -1456010000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -8298000 | 8298000 | -2759000 | 2759000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -1311910000 | -1311910000 | -1285099000 | -1285099000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | 17125000 | 17125000 | 4113000 | 4113000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss attributable to Snowflake Inc. | -1331616000 | -1331616000 | -1285640000 | -1285640000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net loss per share attributable to Snowflake Inc. common stockholders—basic (in dollars per share) | -3.95 | -3.95 | -3.86 | -3.86 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net loss per share attributable to Snowflake Inc. common stockholders—diluted (in dollars per share) | -3.95 | -3.95 | -3.86 | -3.86 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted-average shares used in computing net loss per share attributable to Snowflake Inc. common stockholders—basic (i | 337493000 | 337493000 | 332707000 | 332707000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted-average shares used in computing net loss per share attributable to Snowflake Inc. common stockholders—diluted  | 337493000 | 337493000 | 332707000 | 332707000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R5.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2828163000 | 2828163000 | 2628798000 | 2628798000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 1303740000 | 1303740000 | 922805000 | 922805000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1015 tags across all 98 R pages, face and notes) of 0001640147-26-000008; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 5742612000 | 5742612000 | 5869372000 | 5869372000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 248611000 | 248611000 | 296393000 | 296393000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1194367000 | 1194367000 | 1056559000 | 1056559000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9132495000 | 9132495000 | 9033938000 | 9033938000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 145559000 | 145559000 | 169767000 | 169767000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4421691000 | 4421691000 | 3301183000 | 3301183000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 7208393000 | 7208393000 | 6027295000 | 6027295000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Snowflake Inc. stockholders’ equity | 1924102000 | 1924102000 | 2999929000 | 2999929000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R3.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1221942000 | 1221942000 | 959764000 | 959764000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by investing activities | 312241000 | 312241000 | 190646000 | 190646000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1385390000 | -1385390000 | -226523000 | -226523000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment | -101628000 | 101628000 | -46279000 | 46279000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 220443000 | 220443000 | 182508000 | 182508000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation, net of amounts capitalized | 1599547000 | 1599547000 | 1479314000 | 1479314000 | Y | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1015 tags across all 98 R pages, face and notes) of 0001640147-26-000008; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -873537000 | 873537000 | -1932333000 | 1932333000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001640147-26-000008 R9.htm period ..2026-01-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (1015 tags across all 98 R pages, face and notes) of 0001640147-26-000008; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R92.htm | Income Taxes - Income Taxes Paid (Details) |  | 13319000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Income Taxes - Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | mapped | us-gaap:LongTermDebt | R70.htm | Convertible Senior Notes - Carrying Amounts and Fair Values of Convertible Notes (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R70.htm 'Convertible Senior Notes - Carrying Amounts and Fair Values of Convertible Notes' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 343918000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2026-01-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001640147-24-000101 R5.htm prints 'Interest income' on us-gaap:InterestIncomeExpenseNonoperatingNet = 200663000 (FILING-CHECKED)
- basic_eps: era 10-K 0001640147-21-000073 R4.htm prints 'Net loss per share attributable to Class A and Class B common stockholders - bas' on us-gaap:EarningsPerShareBasicAndDiluted = -3.81 (FILING-CHECKED)
- diluted_eps: era 10-K 0001640147-21-000073 R4.htm prints 'Net loss per share attributable to Class A and Class B common stockholders - bas' on us-gaap:EarningsPerShareBasicAndDiluted = -3.81 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001640147-21-000073 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 820177000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R9.htm): 2026-11-12 R9.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: not_presented  (R9.htm): 2026-11-12 R9.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R92.htm): 2026-11-12 R92.htm: agree: value in the note is the full data point; agree
- total_debt: mapped us-gaap:ConvertibleDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: corrected: the debt is printed on the BS face (R3 'Convertible senior notes, net' 2,279,827k); no current debt line; the tool's NOTE row had no value
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: class rows 343,918,000 + 0 at the BS date (R4)
- net_income: mapped us-gaap:NetIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Net loss attributable to Snowflake Inc.' is the net_income line, printed -1331616000 = filing XBRL -1331616000; agrees
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Weighted-average shares used in computing net loss' is the weighted_diluted_shares line, printed 337493000 = filing XBRL 337493000; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts receivable, net' is the accounts_receivable line, printed 1303740000 = filing XBRL 1303740000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Property and equipment, net' is the ppe_net line, printed 248611000 = filing XBRL 248611000; agrees
- accounts_payable: mapped us-gaap:AccountsPayableCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts payable' is the accounts_payable line, printed 145559000 = filing XBRL 145559000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash used in financing activities' is the cash_flow_financing line, printed -1385390000 = filing XBRL -1385390000; agrees
