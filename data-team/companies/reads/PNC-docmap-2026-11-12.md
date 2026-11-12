# PNC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000713676-26-000020 (CIK 0000713676, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001193125-16-482577 (CIK 0000713676, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000713676-24-000028 (CIK 0000713676, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000713676-18-000032 (CIK 0000713676, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000713676.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenue | 23099000000 | 23099000000 | 21555000000 | 21555000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R152.htm | Segment Reporting - Schedule of Business Segment Results (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R152.htm 'Segment Reporting - Schedule of Business Segment Results (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R3.htm | Total interest expense | 10897000000 | 10897000000 | 12885000000 | 12885000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes and noncontrolling interests | 8486000000 | 8486000000 | 7242000000 | 7242000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 1489000000 | 1489000000 | 1289000000 | 1289000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:ProfitLoss | R3.htm | Net income | 6997000000 | 6997000000 | 5953000000 | 5953000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 16.6 | 16.6 | 13.76 | 13.76 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 16.59 | 16.59 | 13.74 | 13.74 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (shares) | 396000000 | 396000000 | 399000000 | 399000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (shares) | 396000000 | 396000000 | 400000000 | 400000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R5.htm | Cash and due from banks | 6777000000 | 6777000000 | 6904000000 | 6904000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R5.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| current_assets | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R95.htm | Premises, Equipment and Leasehold Improvements (Premises, Equipment and Leasehold Improvements) (Details) |  | 8935000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R95.htm 'Premises, Equipment and Leasehold Improvements (Premises, Equipment and Leasehol' (MetaLinks.json presentation); value from companyfacts same accession |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 10959000000 | 10959000000 | 10932000000 | 10932000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 573572000000 | 573572000000 | 560038000000 | 560038000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R5.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| current_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 512936000000 | 512936000000 | 505569000000 | 505569000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders’ equity | 60585000000 | 60585000000 | 54425000000 | 54425000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided (used) by operating activities | 4384000000 | 4384000000 |  | 7880000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided (used) by investing activities | -15617000000 | -15617000000 |  | -3232000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided (used) by financing activities | 4695000000 | 4695000000 |  | -9122000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| capex | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation, amortization and accretion | 381000000 | 381000000 |  | 259000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| sbc | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ShareBasedCompensation, AllocatedShareBasedCompensationExpense in MetaLinks.json (1521 tags across all 156 R pages, face and notes) of 0000713676-26-000020; no face row matched |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Common stock cash dividends paid | -2635000000 | 2635000000 |  | 2537000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Acquisition of treasury stock | -1338000000 | 1338000000 |  | 687000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 11154000000 | 11154000000 |  | 13052000000 | Y | FILING-CHECKED | accn 0000713676-26-000020 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R143.htm | Income Taxes (Income Tax Paid, Net of Refunds) (Details) |  | 704000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R143.htm 'Income Taxes (Income Tax Paid, Net of Refunds) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:SeniorNotes+us-gaap:LongTermDebt | R5.htm | Senior debt + Total borrowed funds | 95743000000 | 95743000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Consolidated Statement of Changes in Equity |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R7.htm 'Consolidated Statement of Changes in Equity' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Total revenue' on us-gaap:Revenues = 15225000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-482577 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Total interest expense' on us-gaap:InterestExpense = 1045000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Income (loss) before income taxes and noncontrolling interests' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 5507000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1364000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Net income' on us-gaap:ProfitLoss = 4143000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 7.52 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 7.39 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 514000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-482577 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 521000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-482577 R4.htm prints 'Cash and due from banks (a)' on us-gaap:CashAndDueFromBanks = 4065000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-482577 R4.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001193125-16-482577 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 9103000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-482577 R4.htm prints 'Total assets' on us-gaap:Assets = 358493000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-482577 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 312513000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-482577 R4.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 44710000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Net cash provided (used) by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 5496000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Net cash provided (used) by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -16260000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 10469000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 1088000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Common stock cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -1038000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Acquisition of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2152000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 1005000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-482577 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 919000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000713676-24-000028 R3.htm prints 'Total interest expense' on us-gaap:InterestExpense = 10392000000 (FILING-CHECKED)
- cfo: era 10-K 0000713676-18-000032 R7.htm prints 'Net cash provided (used) by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 5699000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000713676-18-000032 R7.htm prints 'Net cash provided (used) by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -15015000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- gross_profit: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:NoninterestExpense (R3.htm): 2026-11-12 R3.htm: corrected: bank opex = total noninterest expense (C, SCHW, BNY, USB precedent)
- sga_expense: component_in_note us-gaap:GeneralAndAdministrativeExpense (R152.htm): 2026-11-12 R152.htm: R152 segment table carries G&A by segment only (no consolidated value); PNC prints no SG&A line
- research_and_development: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- accounts_receivable: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- inventory: OUT  (R5.htm): 2026-11-12 R5.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- current_assets: OUT  (R5.htm): 2026-11-12 R5.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R95.htm): 2026-11-12 R95.htm: agree: R95 premises and equipment, net 8,935 (total)
- accounts_payable: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- current_liabilities: OUT  (R5.htm): 2026-11-12 R5.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- capex: not_presented  (R9.htm): 2026-11-12 R9.htm: agree: whole-filing check agrees; nothing printed
- sbc: not_presented  (R9.htm): 2026-11-12 R9.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R143.htm): 2026-11-12 R143.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: mapped us-gaap:LongTermDebt (R5.htm): 2026-11-12 R5.htm: corrected: 'Total borrowed funds' 57,101 already includes senior debt (38,642), subordinated debt, FHLB advances and other; the tool added senior debt twice (95,743); no finance-lease facts in the fili
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income taxes' is the income_tax_expense line, printed 1489000000 = filing XBRL 1489000000; agrees
- net_income: combined us-gaap:ProfitLoss (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: ProfitLoss 'Net income' 6,997 includes noncontrolling interests (61); no line for net income attributable to PNC is printed: combined
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic (shares)' is the weighted_basic_shares line, printed 396000000 = filing XBRL 396000000; agrees
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Interest paid' is the cash_paid_for_interest line, printed 11154000000 = filing XBRL 11154000000; agrees
