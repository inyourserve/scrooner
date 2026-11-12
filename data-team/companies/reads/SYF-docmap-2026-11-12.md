# SYF document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001601712-26-000006 (CIK 0001601712, filed 2026-02-06): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001601712-16-000069 (CIK 0001601712, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001601712-24-000047 (CIK 0001601712, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001601712-18-000107 (CIK 0001601712, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0001601712.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, RegulatedAndUnregulatedOperatingRevenue, RegulatedOperatingRevenue in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R3.htm | Total interest expense | 4135000000 | 4135000000 | 4634000000 | 4634000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before provision for income taxes | 4621000000 | 4621000000 | 4553000000 | 4553000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes (Note 15) | 1069000000 | 1069000000 | 1054000000 | 1054000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 3552000000 | 3552000000 | 3499000000 | 3499000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in usd per share) | 9.38 | 9.38 | 8.64 | 8.64 | Y | FILING-CHECKED | accn 0001601712-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in usd per share) | 9.28 | 9.28 | 8.55 | 8.55 | Y | FILING-CHECKED | accn 0001601712-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R81.htm | Earnings Per Share - Basic and Diluted Earnings Per Share (Details) |  | 369900000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R81.htm 'Earnings Per Share - Basic and Diluted Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R81.htm | Earnings Per Share - Basic and Diluted Earnings Per Share (Details) |  | 373900000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R81.htm 'Earnings Per Share - Basic and Diluted Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and equivalents | 14973000000 | 14973000000 | 14711000000 | 14711000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| current_assets | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| ppe_net | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 1363000000 | 1363000000 | 1274000000 | 1274000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 119095000000 | 119095000000 | 119463000000 | 119463000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R5.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| current_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 102329000000 | 102329000000 | 102883000000 | 102883000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total equity | 16766000000 | 16766000000 | 16580000000 | 16580000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Cash provided from (used for) operating activities | 9851000000 | 9851000000 | 9848000000 | 9848000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Cash provided from (used for) investing activities | -4854000000 | -4854000000 | -8903000000 | -8903000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Cash provided from (used for) financing activities | -4735000000 | -4735000000 | -611000000 | -611000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 514000000 | 514000000 | 481000000 | 481000000 | Y | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| sbc | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ShareBasedCompensation, AllocatedShareBasedCompensationExpense in MetaLinks.json (924 tags across all 97 R pages, face and notes) of 0001601712-26-000006; no face row matched |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid on common stock | -427000000 | 427000000 | -398000000 | 398000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchases of treasury stock | -2941000000 | 2941000000 | -1008000000 | 1008000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid during the year for interest | -4162000000 | 4162000000 | -4662000000 | 4662000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001601712-26-000006 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R88.htm | Income Taxes - Schedule of Income Taxes Paid (Details) |  | 710000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R88.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:SeniorNotes+us-gaap:LongTermDebt | R5.htm | Senior and subordinated unsecured notes + Total borrowings | 21949000000 | 21949000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock shares outstanding (in shares) | 347000000 | 347000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- interest_expense: FY2015 10-K 0001601712-16-000069 R2.htm prints 'Total interest expense' on us-gaap:InterestExpense = 1135000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001601712-16-000069 R2.htm prints 'Earnings before benefit from income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 3531000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001601712-16-000069 R2.htm prints 'Provision for income taxes (Note 14)' on us-gaap:IncomeTaxExpenseBenefit = 1317000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001601712-16-000069 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 2214000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001601712-16-000069 R2.htm prints 'Basic (in usd per share)' on us-gaap:EarningsPerShareBasic = 2.66 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001601712-16-000069 R2.htm prints 'Diluted (in usd per share)' on us-gaap:EarningsPerShareDiluted = 2.65 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001601712-16-000069 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001601712-16-000069 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001601712-16-000069 R4.htm prints 'Cash and equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 12325000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001601712-16-000069 R4.htm prints 'Goodwill (Note 6)' on us-gaap:Goodwill = 949000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001601712-16-000069 R4.htm prints 'Total assets' on us-gaap:Assets = 84135000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001601712-16-000069 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 71531000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001601712-16-000069 R4.htm prints 'Total equity' on us-gaap:StockholdersEquity = 12604000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001601712-16-000069 R7.htm prints 'Net Cash Provided by (Used in) Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 6184000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001601712-16-000069 R7.htm prints 'Net Cash Provided by (Used in) Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -10803000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001601712-16-000069 R7.htm prints 'Net Cash Provided by (Used in) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 5116000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001601712-16-000069 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 174000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001601712-16-000069 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001601712-16-000069 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001601712-16-000069 R7.htm prints 'Cash paid during the year for interest' on us-gaap:InterestPaid = -1040000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001601712-16-000069 R7.htm prints 'Cash paid during the year for income taxes' on us-gaap:IncomeTaxesPaidNet = -1219000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001601712-24-000047 R2.htm prints 'Total interest expense' on us-gaap:InterestExpense = 3711000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001601712-18-000107 R7.htm prints 'Cash paid during the year for interest' on us-gaap:InterestPaid = -1350000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
