# NVT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008608 (CIK 0001720635, filed 2026-02-17): COVER R1.htm, IS R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001720635-19-000008 (CIK 0001720635, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- 10-K 0001720635-20-000009 (CIK 0001720635, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- companyfacts CIK0001720635.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 3893100000 | 3893100000 | 3006100000 | 3006100000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods sold(1) | 2424000000 | 2424000000 | 1797000000 | 1797000000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1469100000 | 1469100000 | 1209100000 | 1209100000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense | R3.htm | Selling, general and administrative + Research and development | 852300000 | 852300000 | 682000000 | 682000000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 773800000 | 773800000 | 615900000 | 615900000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 78500000 | 78500000 | 6.61e+07 | 66100000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 616800000 | 616800000 | 527100000 | 527100000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (960 tags across all 117 R pages, face and notes) of 0001628280-26-008608; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 550000000 | 550000000 | 429200000 | 429200000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision (benefit) for income taxes | 121500000 | 121500000 | 188400000 | 188400000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 710200000 | 710200000 | 331800000 | 331800000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (dollars per share) | 4.36 | 4.36 | 2 | 2 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (dollars per share) | 4.31 | 4.31 | 1.97 | 1.97 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (shares) | 162400000 | 162400000 | 165500000 | 165500000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (shares) | 164600000 | 164600000 | 168200000 | 168200000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash and cash equivalents | 237500000 | 237500000 | 1.312e+08 | 131200000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndNotesReceivableNet | R5.htm | Accounts and notes receivable, net of allowances of $13.7 and $14.3, respectively | 693000000 | 693000000 | 473100000 | 473100000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 471900000 | 471900000 | 360300000 | 360300000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1639600000 | 1639600000 | 1389300000 | 1389300000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 434500000 | 434500000 | 347900000 | 347900000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2678000000 | 2678000000 | 2221800000 | 2221800000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 6851900000 | 6851900000 | 6734900000 | 6734900000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 358900000 | 358900000 | 280100000 | 280100000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1003500000 | 1003500000 | 801600000 | 801600000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3121700000 | 3121700000 | 3497300000 | 3497300000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R5.htm period ..2025-12-31 |
| stockholders_equity | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of StockholdersEquity in MetaLinks.json (960 tags across all 117 R pages, face and notes) of 0001628280-26-008608; no face row matched |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used for) operating activities of continuing operations | 465200000 | 465200000 | 643100000 | 643100000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used for) investing activities | 5.208e+08 | 520800000 | -758400000 | -758400000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used for) financing activities | -968400000 | -968400000 | 146200000 | 146200000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -93300000 | 93300000 | -74000000 | 74000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R7.htm | Depreciation + Intangible asset amortization | 207800000 | 207800000 | 146000000 | 146000000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 37500000 | 37500000 | 27300000 | 27300000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -130400000 | 130400000 | -126800000 | 126800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of ordinary shares | -253100000 | 253100000 | -100000000 | 100000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest, net | 106200000 | 106200000 | 134800000 | 134800000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes, net | 283300000 | 283300000 | 120200000 | 120200000 | Y | FILING-CHECKED | accn 0001628280-26-008608 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current maturities of long-term debt and short-term borrowings + Long-term debt | 1559800000 | 1559800000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (960 tags across all 117 R pages, face and notes) of 0001628280-26-008608; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cost_of_revenue: era 10-K 0001720635-19-000008 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 1337500000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001720635-20-000009 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 106400000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
