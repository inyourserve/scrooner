# NET document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001477333-26-000016 (CIK 0001477333, filed 2026-02-26): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001477333-24-000013 (CIK 0001477333, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001477333-21-000009 (CIK 0001477333, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001477333.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 2167937000 | 2167937000 | 1669626000 | 1669626000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 552525000 | 552525000 | 378702000 | 378702000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1615412000 | 1615412000 | 1290924000 | 1290924000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1822617000 | 1822617000 | 1445685000 | 1445685000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 389311000 | 389311000 | 278520000 | 278520000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 512489000 | 512489000 | 421374000 | 421374000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -207205000 | -207205000 | -154761000 | -154761000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -8766000 | 8766000 | -5196000 | 5196000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -92706000 | -92706000 | -70871000 | -70871000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 9561000 | 9561000 | 7929000 | 7929000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -102267000 | -102267000 | -78800000 | -78800000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net loss per share attributable to common stockholders, basic (in dollars per share) | -0.29 | -0.29 | -0.23 | -0.23 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net loss per share attributable to common stockholders, diluted (in dollars per share) | -0.29 | -0.29 | -0.23 | -0.23 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted-average shares used in computing net loss per share attributable to common stockholders, basic (in shares) | 348421000 | 348421000 | 341411000 | 341411000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted-average shares used in computing net loss per share attributable to common stockholders, diluted (in shares) | 348421000 | 348421000 | 341411000 | 341411000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 943536000 | 943536000 | 147691000 | 147691000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 382488000 | 382488000 | 316753000 | 316753000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (918 tags across all 90 R pages, face and notes) of 0001477333-26-000016; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4644837000 | 4644837000 | 2268997000 | 2268997000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 618691000 | 618691000 | 467420000 | 467420000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 226563000 | 226563000 | 181087000 | 181087000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 6036256000 | 6036256000 | 3301162000 | 3301162000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 84115000 | 84115000 | 105807000 | 105807000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 2350563000 | 2350563000 | 793654000 | 793654000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4577133000 | 4577133000 | 2254961000 | 2254961000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 1459123000 | 1459123000 | 1046201000 | 1046201000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 603114000 | 603114000 | 380429000 | 380429000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -1806700000 | -1806700000 | -330224000 | -330224000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 2003729000 | 2003729000 | 12785000 | 12785000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -315617000 | 315617000 | -185037000 | 185037000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization expense | 189742000 | 189742000 | 127722000 | 127722000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 451454000 | 451454000 | 338461000 | 338461000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (918 tags across all 90 R pages, face and notes) of 0001477333-26-000016; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of unvested common stock | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 29000 | 29000 | 75000 | 75000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes, net of refunds | 7767000 | 7767000 | 4995000 | 4995000 | Y | FILING-CHECKED | accn 0001477333-26-000016 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R63.htm | Financing Arrangements - Schedule of Net Carrying Amount of Notes (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Financing Arrangements - Schedule of Net Carrying Amount of Notes (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 351887000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001477333-24-000013 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -5872000 (FILING-CHECKED)
- basic_eps: era 10-K 0001477333-21-000009 R4.htm prints 'Net loss per share attributable to common stockholders, basic and diluted (in do' on us-gaap:EarningsPerShareBasicAndDiluted = -0.4 (FILING-CHECKED)
- diluted_eps: era 10-K 0001477333-21-000009 R4.htm prints 'Net loss per share attributable to common stockholders, basic and diluted (in do' on us-gaap:EarningsPerShareBasicAndDiluted = -0.4 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001477333-21-000009 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 108895000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:ConvertibleDebtCurrent+us-gaap:ConvertibleDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: corrected: both convertible lines are printed on the BS face (1,291,281 + 1,974,120 = 3,265,401k); the tool's NOTE row had no value
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: Class A 317,319k + Class B 34,568k at the BS date (R4)
- net_income: mapped us-gaap:NetIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Net loss' is the net_income line, printed -102267000 = filing XBRL -102267000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Net loss per share attributable to common stockhol' is the basic_eps line, printed -0.29 = filing XBRL -0.29; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts receivable, net' is the accounts_receivable line, printed 382488000 = filing XBRL 382488000; agrees
- accounts_payable: mapped us-gaap:AccountsPayableCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts payable' is the accounts_payable line, printed 84115000 = filing XBRL 84115000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current liabilities' is the current_liabilities line, printed 2350563000 = filing XBRL 2350563000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Purchases of property and equipment' is the capex line, printed -315617000 = filing XBRL 315617000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Repurchases of unvested common stock' is the share_buybacks line, printed 0 = filing XBRL 0; agrees
