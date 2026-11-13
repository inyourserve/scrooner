# LPLA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-010705 (CIK 0001397911, filed 2026-02-23): COVER R1.htm, IS R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001397911-16-000219 (CIK 0001397911, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001397911-21-000029 (CIK 0001397911, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R6.htm
- 10-K 0001397911-19-000018 (CIK 0001397911, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0001397911.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total net revenues | 16989479000 | 16989479000 | 12385107000 | 12385107000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R3.htm agree |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R3.htm agree |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total expense | 15839972000 | 15839972000 | 10992215000 | 10992215000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-010705 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R3.htm agree |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R3.htm agree |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R3.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R3.htm | Interest Expense, Debt | 403406000 | 403406000 | 274181000 | 274181000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | INCOME BEFORE PROVISION FOR INCOME TAXES | 1149507000 | 1149507000 | 1392892000 | 1392892000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Effective income tax rate | 286483000 | 286483000 | 334276000 | 334276000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME | 863024000 | 863024000 | 1058616000 | 1058616000 | Y | FILING-CHECKED | accn 0001628280-26-010705 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings Per Share, Basic | 10.97 | 10.97 | 14.17 | 14.17 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings Per Share, Diluted | 10.92 | 10.92 | 14.03 | 14.03 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted-average shares outstanding, basic | 78681000 | 78681000 | 74713000 | 74713000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted-average shares outstanding, diluted | 79061000 | 79061000 | 75427000 | 75427000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and equivalents | 1037378000 | 1037378000 | 967079000 | 967079000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R4.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R4.htm agree |
| inventory | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R4.htm agree |
| current_assets | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R4.htm agree |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R4.htm | Property and equipment, net | 1409376000 | 1409376000 | 1210027000 | 1210027000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 2644723000 | 2644723000 | 2172873000 | 2172873000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 18492753000 | 18492753000 | 13317404000 | 13317404000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R4.htm period ..2025-12-31 |
| accounts_payable | combined | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R4.htm | Accounts payable and accrued liabilities | 821641000 | 821641000 | 588450000 | 588450000 | Y | FILING-CHECKED | face line 'Accounts payable and accrued liabilities' combines AP and accrued liabilities; no separate AP line / check: hand R4.htm corrected: Single line 'Accounts payable and accrued liabilities' 821,641 (AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent) mixes AP with accruals -> combined. |
| current_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R4.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R4.htm | Liabilities, Total | 13148268000 | 13148268000 | 10386802000 | 10386802000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R4.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total stockholders’ equity | 5344485000 | 5344485000 | 2930602000 | 2930602000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash (used in) provided by operating activities | -411404000 | -411404000 | 277589000 | 277589000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -2386593000 | -2386593000 | -1592132000 | -1592132000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 3168685000 | 3168685000 | 1417432000 | 1417432000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -570376000 | 570376000 | -562531000 | 562531000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R8.htm | Depreciation and amortization | 630012000 |  | 443761000 |  |  | FILING-CHECKED | CF R8: Depreciation and amortization 393,434 + Amortization of other intangibles 236,578 (FY1 308,527 + 135,234); debt-cost amortization excluded / check: hand R8.htm corrected: CF prints 'Depreciation and amortization' 393,434 (tag Depreciation) and separately 'Amortization of other intangibles' 236,578 -> component sum 630,012K. |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 79362000 | 79362000 | 91761000 | 91761000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends on common stock | -94411000 | 94411000 | -89727000 | 89727000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010705 R8.htm period ..2025-12-31 / check: hand R8.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -100004000 | 100004000 | -170096000 | 170096000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 379919000 | 379919000 | 268351000 | 268351000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes paid | 328560000 | 328560000 | 320259000 | 320259000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010705 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebt | R4.htm | Corporate debt and other borrowings, net | 7258694000 | 7258694000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R4.htm agree |
| shares_outstanding | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1098 tags across all 129 R pages, face and notes) of 0001628280-26-010705; no face row matched / check: hand R5.htm agree |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001397911-16-000219 R2.htm prints 'Total net revenues' on us-gaap:Revenues = 4275054000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001397911-16-000219 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 3933363000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001397911-16-000219 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001397911-16-000219 R2.htm prints 'INCOME BEFORE PROVISION FOR INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 282555000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001397911-16-000219 R2.htm prints 'PROVISION FOR INCOME TAXES' on us-gaap:IncomeTaxExpenseBenefit = 113771000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001397911-16-000219 R2.htm prints 'NET INCOME' on us-gaap:NetIncomeLoss = 168784000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001397911-16-000219 R2.htm prints 'Earnings per share, basic' on us-gaap:EarningsPerShareBasic = 1.77 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001397911-16-000219 R2.htm prints 'Earnings per share, diluted' on us-gaap:EarningsPerShareDiluted = 1.74 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001397911-16-000219 R2.htm prints 'Weighted-average shares outstanding, basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 95273000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001397911-16-000219 R2.htm prints 'Weighted-average shares outstanding, diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 96786000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 724529000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 275419000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 1365838000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Total assets' on us-gaap:Assets = 4521061000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 332492000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 3805451000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001397911-16-000219 R5.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 715610000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 279451000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -74948000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 107694000 (FILING-CHECKED)
- capex: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -72565000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Depreciation and amortization' on us-gaap:Depreciation = 73383000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 29213000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Dividends on common stock' on us-gaap:PaymentsOfDividends = -95814000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -390835000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 51114000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001397911-16-000219 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 131833000 (FILING-CHECKED)
- operating_expenses: era 10-K 0001397911-21-000029 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 5139802000 (FILING-CHECKED)
- ppe_net: era 10-K 0001397911-21-000029 R3.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 582868000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001397911-19-000018 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 123623000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 16 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
