# DASH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001792789-26-000013 (CIK 0001792789, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001628280-21-004032 (CIK 0001792789, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001792789.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 13717000000 | 13717000000 | 10722000000 | 10722000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R5.htm | Cost of revenue, exclusive of depreciation and amortization shown separately below | 6738000000 | 6738000000 | 5542000000 | 5542000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (934 tags across all 107 R pages, face and notes) of 0001792789-26-000013; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 12994000000 | 12994000000 | 10760000000 | 10760000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 1600000000 | 1600000000 | 1452000000 | 1452000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 1431000000 | 1431000000 | 1168000000 | 1168000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income (loss) from operations | 723000000 | 723000000 | -38000000 | -38000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (934 tags across all 107 R pages, face and notes) of 0001792789-26-000013; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before income taxes | 939000000 | 939000000 | 156000000 | 156000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 7000000 | 7000000 | 39000000 | 39000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) attributable to DoorDash, Inc. common stockholders | 935000000 | 935000000 | 123000000 | 123000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in $ per share) | 2.19 | 2.19 | 0.3 | 0.3 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in $ per share) | 2.13 | 2.13 | 0.29 | 0.29 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 427043000 | 427043000 | 411551000 | 411551000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 439686000 | 439686000 | 430242000 | 430242000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 4378000000 | 4378000000 | 4019000000 | 4019000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 1108000000 | 1108000000 | 732000000 | 732000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (934 tags across all 107 R pages, face and notes) of 0001792789-26-000013; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 8643000000 | 8643000000 | 7386000000 | 7386000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 1067000000 | 1067000000 | 778000000 | 778000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5519000000 | 5519000000 | 2315000000 | 2315000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 19659000000 | 19659000000 | 12845000000 | 12845000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 397000000 | 397000000 | 321000000 | 321000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 6147000000 | 6147000000 | 4438000000 | 4438000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 9613000000 | 9613000000 | 5035000000 | 5035000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 10033000000 | 10033000000 | 7803000000 | 7803000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 2431000000 | 2431000000 | 2132000000 | 2132000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -4391000000 | -4391000000 | -444000000 | -444000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 2360000000 | 2360000000 | -204000000 | -204000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -257000000 | 257000000 | -104000000 | 104000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 747000000 | 747000000 | 561000000 | 561000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 1051000000 | 1051000000 | 1099000000 | 1099000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (934 tags across all 107 R pages, face and notes) of 0001792789-26-000013; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | 0 | 0 | -224000000 | 224000000 | Y | FILING-CHECKED | accn 0001792789-26-000013 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (934 tags across all 107 R pages, face and notes) of 0001792789-26-000013; no face row matched |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (934 tags across all 107 R pages, face and notes) of 0001792789-26-000013; no face row matched |
| total_debt | mapped | us-gaap:LongTermDebt | R84.htm | Convertible Notes, Net-Schedule of Convertible Debt (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'Convertible Notes, Net-Schedule of Convertible Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 434247000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- income_before_tax: era 10-K 0001628280-21-004032 R4.htm prints 'Loss before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -458000000 (FILING-CHECKED)
- basic_eps: era 10-K 0001628280-21-004032 R4.htm prints 'Net loss per share attributabe to common stockholders, basic and diluted ($ per ' on us-gaap:EarningsPerShareBasicAndDiluted = -7.39 (FILING-CHECKED)
- diluted_eps: era 10-K 0001628280-21-004032 R4.htm prints 'Net loss per share attributabe to common stockholders, basic and diluted ($ per ' on us-gaap:EarningsPerShareBasicAndDiluted = -7.39 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001628280-21-004032 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 4345000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingAndMarketingExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:GeneralAndAdministrativeExpense+us-gaap:DepreciationDepletionAndAmortization+us-gaap:RestructuringCharges (R5.htm): 2026-11-12 R5.htm: corrected: 2,476 + 1,431 + 1,600 + 747 + 2 = 6,256 = 13,717 - 6,738 - 723
- interest_expense: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_income_taxes: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: mapped us-gaap:ConvertibleLongTermNotesPayable (R3.htm): 2026-11-12 R3.htm: corrected: the debt is on the BS face (R3); the NOTE row had no value; no finance-lease facts
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: class rows at the BS date (R4)
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Provision for income taxes' is the income_tax_expense line, printed 7000000 = filing XBRL 7000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in $ per share)' is the basic_eps line, printed 2.19 = filing XBRL 2.19; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Cash and cash equivalents' is the cash_and_equivalents line, printed 4378000000 = filing XBRL 4378000000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current liabilities' is the current_liabilities line, printed 6147000000 = filing XBRL 6147000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Purchases of property and equipment' is the capex line, printed -257000000 = filing XBRL 257000000; agrees
- depreciation_and_amortization: mapped us-gaap:DepreciationDepletionAndAmortization (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Depreciation and amortization' is the depreciation_and_amortization line, printed 747000000 = filing XBRL 747000000; agrees
