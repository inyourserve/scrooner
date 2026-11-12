# ABNB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001559720-26-000004 (CIK 0001559720, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001559720-22-000006 (CIK 0001559720, era filing): COVER R1.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001559720-24-000006 (CIK 0001559720, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001559720.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 12241000000 | 12241000000 | 11102000000 | 11102000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 2086000000 | 2086000000 | 1878000000 | 1878000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (857 tags across all 87 R pages, face and notes) of 0001559720-26-000004; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 9697000000 | 9697000000 | 8549000000 | 8549000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 1342000000 | 1342000000 | 1185000000 | 1185000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Product development | 2354000000 | 2354000000 | 2056000000 | 2056000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 2544000000 | 2544000000 | 2553000000 | 2553000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (857 tags across all 87 R pages, face and notes) of 0001559720-26-000004; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 3137000000 | 3137000000 | 3331000000 | 3331000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | 626000000 | 626000000 | 683000000 | 683000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 2511000000 | 2511000000 | 2648000000 | 2648000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerBasicShare | R5.htm | Basic (in USD per share) | 4.1 | 4.1 | 4.19 | 4.19 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare | R5.htm | Diluted (in USD per share) | 4.03 | 4.03 | 4.11 | 4.11 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 613000000 | 613000000 | 632000000 | 632000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in Shares) | 623000000 | 623000000 | 645000000 | 645000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 6560000000 | 6560000000 | 6864000000 | 6864000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:FundsHeldForClients | R3.htm | Funds receivable and amounts held on behalf of customers | 6959000000 | 6959000000 | 5931000000 | 5931000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (857 tags across all 87 R pages, face and notes) of 0001559720-26-000004; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 18797000000 | 18797000000 | 17180000000 | 17180000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R47.htm | Supplemental Financial Statement Information - Schedule of Supplemental Balance Sheet Information (Details) |  | 107000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R47.htm 'Supplemental Financial Statement Information - Schedule of Supplemental Balance ' (MetaLinks.json presentation); value from companyfacts same accession |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R3.htm | Goodwill and intangible assets, net | 770000000 | 770000000 | 777000000 | 777000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 22208000000 | 22208000000 | 20959000000 | 20959000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accrued expenses, accounts payable, and other current liabilities | 2948000000 | 2948000000 | 2614000000 | 2614000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 13649000000 | 13649000000 | 10161000000 | 10161000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 14009000000 | 14009000000 | 12547000000 | 12547000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 8199000000 | 8199000000 | 8412000000 | 8412000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 4646000000 | 4646000000 | 4518000000 | 4518000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -748000000 | -748000000 | -616000000 | -616000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -3827000000 | -3827000000 | -3572000000 | -3572000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (857 tags across all 87 R pages, face and notes) of 0001559720-26-000004; no face row matched |
| depreciation_and_amortization | component_in_note | us-gaap:Depreciation | R61.htm | Property and Equipment, Net - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | only component tag(s) Depreciation in the filing (R61.htm 'Property and Equipment, Net - Narrative (Details)'); the data point itself is not reported |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 1592000000 | 1592000000 | 1407000000 | 1407000000 | Y | FILING-CHECKED | accn 0001559720-26-000004 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (857 tags across all 87 R pages, face and notes) of 0001559720-26-000004; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Share repurchases | -3789000000 | 3789000000 | -3430000000 | 3430000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001559720-26-000004 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R46.htm | Supplemental Financial Statement Information - Schedule of Supplemental Disclosures of Cash Flow Information (Details) |  | 2000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R46.htm 'Supplemental Financial Statement Information - Schedule of Supplemental Disclosu' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R46.htm | Supplemental Financial Statement Information - Schedule of Supplemental Disclosures of Cash Flow Information (Details) |  | 232000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R46.htm 'Supplemental Financial Statement Information - Schedule of Supplemental Disclosu' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of long-term debt + Long-term debt | 1999000000 | 1999000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock outstanding (in shares) | 602000000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: 10-K 0001559720-22-000006 statement not identified (auto)
- goodwill: era 10-K 0001559720-24-000006 R3.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum abnb:OperationsAndSupportExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingAndMarketingExpense+us-gaap:GeneralAndAdministrativeExpense (R5.htm): 2026-11-12 R5.htm: corrected: opex never includes COR; every face line after cost of revenue: 1,327 + 2,354 + 2,588 + 1,342 = 7,611 = 12,241 - 2,086 - 2,544 (FY2024 6,671 ties too)
- interest_expense: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed; R5 prints interest income only
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R47.htm): 2026-11-12 R47.htm: agree: PP&E is not on the BS face; R47 note value 107,000,000
- capex: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: CF R8 prints no capex line (only investments and 'Other investing activities, net')
- depreciation_and_amortization: component_in_note us-gaap:Depreciation (R61.htm): 2026-11-12 R61.htm: agree: CF R8 prints no D&A line; depreciation only in the note
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R46.htm): 2026-11-12 R46.htm: agree: value in the note is the full data point; agree
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R46.htm): 2026-11-12 R46.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: agree: R3 1,999 + 0
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: Class A 426,000,000 + Class B 176,000,000 + 0 at the BS date (R4)
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Revenue' is the revenue line, printed 12241000000 = filing XBRL 12241000000; agrees
- operating_income: mapped us-gaap:OperatingIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Income from operations' is the operating_income line, printed 2544000000 = filing XBRL 2544000000; agrees
- basic_eps: mapped us-gaap:IncomeLossFromContinuingOperationsPerBasicShare (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in USD per share)' is the basic_eps line, printed 4.1 = filing XBRL 4.1; agrees
- accounts_payable: combined us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: 'Accrued expenses, accounts payable, and other current liabilities' bundles accrued and other liabilities with AP: combined, not AP
- sbc: mapped us-gaap:ShareBasedCompensation (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Stock-based compensation expense' is the sbc line, printed 1592000000 = filing XBRL 1592000000; agrees
