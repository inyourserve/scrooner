# TRV document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000086312-26-000065 (CIK 0000086312, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001047469-16-010107 (CIK 0000086312, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000086312.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenues | 48828000000 | 48828000000 | 46423000000 | 46423000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | General and administrative expenses | 6120000000 | 6120000000 | 5819000000 | 5819000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | 425000000 | 425000000 | 392000000 | 392000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 7796000000 | 7796000000 | 6180000000 | 6180000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 1508000000 | 1508000000 | 1181000000 | 1181000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 6288000000 | 6288000000 | 4999000000 | 4999000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 27.83 | 27.83 | 21.76 | 21.76 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 27.43 | 27.43 | 21.47 | 21.47 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 224200000 | 224200000 | 228000000 | 228000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 227600000 | 227600000 | 231100000 | 231100000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:Cash | R5.htm | Cash (including restricted cash of $132 and $131) | 842000000 | 842000000 | 699000000 | 699000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| current_assets | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| ppe_net | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 4066000000 | 4066000000 | 4233000000 | 4233000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 143708000000 | 143708000000 | 133189000000 | 133189000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R5.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| current_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 110814000000 | 110814000000 | 105325000000 | 105325000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders’ equity | 32894000000 | 32894000000 | 27864000000 | 27864000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 10606000000 | 10606000000 | 9074000000 | 9074000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -7652000000 | -7652000000 | -7264000000 | -7264000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -2663000000 | -2663000000 | -1747000000 | -1747000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1272 tags across all 130 R pages, face and notes) of 0000086312-26-000065; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 680000000 | 680000000 | 715000000 | 715000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation | R8.htm | Treasury stock acquired — net employee share-based compensation | -127000000 | 127000000 | -114000000 | 114000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid to shareholders | -979000000 | 979000000 | -951000000 | 951000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury stock acquired — share repurchase authorizations | -3004000000 | 3004000000 | -1003000000 | 1003000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 393000000 | 393000000 | 390000000 | 390000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid | 1274000000 | 1274000000 | 1310000000 | 1310000000 | Y | FILING-CHECKED | accn 0000086312-26-000065 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:DebtLongtermAndShorttermCombinedAmount | R89.htm | Debt (Details) |  | 9267000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R89.htm 'Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 217500000 | 217500000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Total revenues' on us-gaap:Revenues = 26800000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-16-010107 R2.htm prints 'General and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 4079000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 373000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4740000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 1301000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 3439000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 10.99 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 10.88 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 310600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-010107 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 313900000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-16-010107 R5.htm prints 'Cash' on us-gaap:Cash = 380000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-16-010107 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 3573000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-010107 R5.htm prints 'Total assets' on us-gaap:Assets = 100184000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047469-16-010107 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 76586000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-010107 R5.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 23598000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 3434000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 317000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -3733000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Depreciation and amortization' on trv:DepreciationAndAmortizationExcludingDeferredPolicyAcquisitionCostAmortizationExpense = 818000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Treasury stock acquired - net employee share-based compensation' on us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation = -74000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -739000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Treasury stock acquired - share repurchase authorization' on us-gaap:PaymentsForRepurchaseOfCommonStock = -3150000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 365000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-16-010107 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 1207000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the insurer template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- gross_profit: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the insurer template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_expenses: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the insurer template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- accounts_receivable: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- inventory: OUT  (R5.htm): 2026-11-12 R5.htm: OUT of the insurer template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- current_assets: OUT  (R5.htm): 2026-11-12 R5.htm: OUT of the insurer template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- ppe_net: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- accounts_payable: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- current_liabilities: OUT  (R5.htm): 2026-11-12 R5.htm: OUT of the insurer template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- capex: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: mapped us-gaap:DebtLongtermAndShorttermCombinedAmount (R5.htm): 2026-11-12 R5.htm: corrected: 'Debt' 9,267 is printed on the BS face (R5), not only in note R89
- revenue: mapped us-gaap:Revenues (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Total revenues' is the revenue line, printed 48828000000 = filing XBRL 48828000000; agrees
- interest_expense: mapped us-gaap:InterestExpense (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Interest expense' is the interest_expense line, printed 425000000 = filing XBRL 425000000; agrees
- total_liabilities: mapped us-gaap:Liabilities (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total liabilities' is the total_liabilities line, printed 110814000000 = filing XBRL 110814000000; agrees
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Net cash provided by operating activities' is the cfo line, printed 10606000000 = filing XBRL 10606000000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Dividends paid to shareholders' is the dividends_paid line, printed -979000000 = filing XBRL 979000000; agrees
