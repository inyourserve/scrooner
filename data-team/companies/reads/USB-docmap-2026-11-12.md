# USB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000036104-26-000011 (CIK 0000036104, filed 2026-02-23): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001193125-16-478568 (CIK 0000036104, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000036104-24-000018 (CIK 0000036104, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001193125-18-053893 (CIK 0000036104, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0000036104.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R149.htm | Business Segments - Results by Business Segment (Details) |  | 28656000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R149.htm 'Business Segments - Results by Business Segment (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R152.htm | U.S. Bancorp (Parent Company) - Condensed Income Statement (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R152.htm 'U.S. Bancorp (Parent Company) - Condensed Income Statement (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R4.htm | Total interest expense | 14321000000 | 14321000000 | 15377000000 | 15377000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 9517000000 | 9517000000 | 7909000000 | 7909000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Applicable income taxes | 1921000000 | 1921000000 | 1580000000 | 1580000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income (loss) attributable to U.S. Bancorp | 7570000000 | 7570000000 | 6299000000 | 6299000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Earnings per common share (in dollars per share) | 4.62 | 4.62 | 3.79 | 3.79 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted earnings per common share (in dollars per share) | 4.62 | 4.62 | 3.79 | 3.79 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Average common shares outstanding (in shares) | 1557000000 | 1557000000 | 1560000000 | 1560000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Average diluted common shares outstanding (in shares) | 1558000000 | 1558000000 | 1561000000 | 1561000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R2.htm | Cash and due from banks | 46890000000 | 46890000000 | 56502000000 | 56502000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| ppe_net | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 12635000000 | 12635000000 | 12536000000 | 12536000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 692345000000 | 692345000000 | 678318000000 | 678318000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 626694000000 | 626694000000 | 619278000000 | 619278000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total U.S. Bancorp shareholders’ equity | 65193000000 | 65193000000 | 58578000000 | 58578000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 7970000000 | 7970000000 | 11350000000 | 11350000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash (used in) provided by investing activities | -20538000000 | -20538000000 | -24534000000 | -24534000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 2250000000 | 2250000000 | 8821000000 | 8821000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1606 tags across all 155 R pages, face and notes) of 0000036104-26-000011; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationNonproduction | R8.htm | Depreciation and amortization of premises and equipment | 377000000 | 377000000 | 370000000 | 370000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R117.htm | Stock-Based Compensation - Additional Information (Details) |  | 235000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R117.htm 'Stock-Based Compensation - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Cash dividends paid on common stock | -3168000000 | 3168000000 | -3092000000 | 3092000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -489000000 | 489000000 | -173000000 | 173000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 14388000000 | 14388000000 | 15382000000 | 15382000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income taxes | 544000000 | 544000000 | 499000000 | 499000000 | Y | FILING-CHECKED | accn 0000036104-26-000011 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings | R2.htm | Short-term borrowings | 17162000000 | 17162000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R101.htm | Shareholders' Equity - Additional Information (Details) |  | 1600000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R101.htm 'Shareholders' Equity - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-478568 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001193125-16-478568 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 1401000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 8030000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Applicable income taxes' on us-gaap:IncomeTaxExpenseBenefit = 2097000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Net income attributable to U.S. Bancorp' on us-gaap:NetIncomeLoss = 5879000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Earnings per common share' on us-gaap:EarningsPerShareBasic = 3.18 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Diluted earnings per common share' on us-gaap:EarningsPerShareDiluted = 3.16 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Average common shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 1764000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-478568 R4.htm prints 'Average diluted common shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 1772000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-478568 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 11147000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-478568 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 9361000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-478568 R2.htm prints 'Total assets' on us-gaap:Assets = 421853000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-478568 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 375036000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-478568 R2.htm prints 'Total U.S. Bancorp shareholders' equity' on us-gaap:StockholdersEquity = 46131000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 8782000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -21150000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 12861000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Depreciation and amortization of premises and equipment' on us-gaap:DepreciationNonproduction = 307000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-478568 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Cash dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -1777000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2190000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 1434000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-478568 R7.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 742000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000036104-24-000018 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 12611000000 (FILING-CHECKED)
- cfo: era 10-K 0001193125-18-053893 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 6472000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-053893 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -12126000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-053893 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 9454000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001193125-18-053893 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 2086000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- revenue: mapped us-gaap:Revenues (R149.htm): 2026-11-12 R149.htm: agree: R149 consolidated net revenue 28,656,000,000 (bank top line, non-dimensional)
- cost_of_revenue: OUT  (R4.htm): 2026-11-12 R4.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- gross_profit: OUT  (R4.htm): 2026-11-12 R4.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:NoninterestExpense (R4.htm): 2026-11-12 R4.htm: corrected: the tool took the parent-company-only statement (R152); bank opex = total noninterest expense on the face (C, SCHW precedent)
- sga_expense: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: OUT  (R4.htm): 2026-11-12 R4.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_income: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- accounts_receivable: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- inventory: OUT  (R2.htm): 2026-11-12 R2.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- current_assets: OUT  (R2.htm): 2026-11-12 R2.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- ppe_net: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- accounts_payable: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- current_liabilities: OUT  (R2.htm): 2026-11-12 R2.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- capex: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R117.htm): 2026-11-12 R117.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities (R2.htm): 2026-11-12 R2.htm: corrected: the tool left out 'Long-term debt' (60,764); 17,162 + 60,764
- shares_outstanding: not_presented  (R101.htm): 2026-11-12 R101.htm: decided by R101: the only count is a rounded narrative 1,600,000,000 (scaled in billions); no exact BS-date outstanding count is printed; the cover count is never used
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: IS R4.htm 'Earnings per common share (in dollars per share)' is the basic_eps line, printed 4.62 = filing XBRL 4.62; agrees
- cash_and_equivalents: mapped us-gaap:CashAndDueFromBanks (R2.htm): 2026-11-12 R2.htm: 20% mapped sample: BS R2.htm 'Cash and due from banks' is the cash_and_equivalents line, printed 46890000000 = filing XBRL 46890000000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Net cash provided by (used in) financing activitie' is the cash_flow_financing line, printed 2250000000 = filing XBRL 2250000000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Cash dividends paid on common stock' is the dividends_paid line, printed -3168000000 = filing XBRL 3168000000; agrees
