# CASY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000726958-26-000046 (CIK 0000726958, filed 2026-06-22): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0000726958-15-000075 (CIK 0000726958, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000726958-17-000055 (CIK 0000726958, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000726958-19-000078 (CIK 0000726958, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0000726958.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenue | 17561101000 | 17561101000 | 15940899000 | 15940899000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R5.htm period ..2026-04-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R5.htm | Cost of goods sold (excluding depreciation and amortization, shown separately below) | 13240060000 | 13240060000 | 12188496000 | 12188496000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000726958-26-000046 R5.htm period ..2026-04-30 / check: hand R5.htm agree |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (668 tags across all 61 R pages, face and notes) of 0000726958-26-000046; no face row matched / check: hand R5.htm agree |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Operating expenses | 2837426000 | 2837426000 | 2552356000 | 2552356000 | Y | FILING-CHECKED | face line 'Operating expenses' excludes COGS (printed separately) and excludes D&A (separate line 449,958K); no operating income subtotal printed / check: hand R5.htm corrected: The face line 'Operating expenses' 2,837,426 / 2,552,356 (us-gaap:OperatingExpenses) is printed separately from Cost of goods sold 13,240,060, so it excludes cost of revenue; the machine's 'includes cost of revenue' is wrong. Rule 5: a printed opex line excluding COGS -> mapped. D&A 449,958 is a separate line, not included. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (668 tags across all 61 R pages, face and notes) of 0000726958-26-000046; no face row matched / check: hand R5.htm agree |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (668 tags across all 61 R pages, face and notes) of 0000726958-26-000046; no face row matched / check: hand R5.htm agree |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (668 tags across all 61 R pages, face and notes) of 0000726958-26-000046; no face row matched / check: hand R5.htm agree |
| interest_expense | combined | us-gaap:InterestExpense | R5.htm | Interest, net | 96634000 | 96634000 | 83951000 | 83951000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000726958-26-000046 R5.htm period ..2026-04-30 |
| income_before_tax | mapped | us-gaap:IncomeLossAttributableToParent | R5.htm | Income before income taxes | 937023000 | 937023000 | 712449000 | 712449000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000726958-26-000046 R5.htm period ..2026-04-30 / check: hand R5.htm agree |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Federal and state income taxes | 222575000 | 222575000 | 165929000 | 165929000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R5.htm period ..2026-04-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 714448000 | 714448000 | 546520000 | 546520000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R5.htm period ..2026-04-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in Dollars per share) | 19.28 | 19.28 | 14.72 | 14.72 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R5.htm period ..2026-04-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in Dollars per share) | 19.16 | 19.16 | 14.64 | 14.64 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R5.htm period ..2026-04-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R45.htm | Net Income Per Common Share - Schedule of Basic and Diluted Earnings Per Share (Details) | 37065319 | 37065319 | 37116152 |  | Y | FILING-CHECKED | not on face IS; R45 EPS schedule 37,065,319 / 37,116,152 / check: hand R45.htm corrected: Not on face IS; R45 Weighted average shares outstanding-basic 37,065,319 / 37,116,152. |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R45.htm | Net Income Per Common Share - Schedule of Basic and Diluted Earnings Per Share (Details) | 37281653 | 37281653 | 37343012 |  | Y | FILING-CHECKED | not on face IS; R45 EPS schedule 37,281,653 / 37,343,012 / check: hand R45.htm corrected: Not on face IS; R45 Weighted-average shares outstanding-diluted 37,281,653 / 37,343,012. |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 522991000 | 522991000 | 326662000 | 326662000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| accounts_receivable | mapped | us-gaap:AccountsAndOtherReceivablesNetCurrent | R3.htm | Receivables | 243502000 |  | 180746000 |  |  | FILING-CHECKED | single receivables line on BS face (AccountsAndOtherReceivablesNetCurrent), rule 9 / check: hand R3.htm corrected: BS prints a single receivables line 'Receivables' 243,502 / 180,746 $K under us-gaap:AccountsAndOtherReceivablesNetCurrent; rule 9 allows the wider tag as the single receivables line. |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 557151000 | 557151000 | 480034000 | 480034000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1364012000 | 1364012000 | 1012853000 | 1012853000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Net property and equipment | 5749468000 | 5749468000 | 5413244000 | 5413244000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1268686000 | 1268686000 | 1244893000 | 1244893000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 8936055000 | 8936055000 | 8208118000 | 8208118000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 823804000 | 823804000 | 620447000 | 620447000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1350606000 | 1350606000 | 1101693000 | 1101693000 | Y | FILING-CHECKED | accn 0000726958-26-000046 R3.htm period ..2026-04-30 / check: hand R3.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4984336000 | 4984336000 | 4699448000 | 4699448000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders’ equity | 3951719000 | 3951719000 | 3508670000 | 3508670000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R3.htm period ..2026-04-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1377540000 | 1377540000 | 1090854000 | 1090854000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -755431000 | -755431000 | -1726668000 | -1726668000 | Y | FILING-CHECKED | accn 0000726958-26-000046 R8.htm period ..2026-04-30 / check: hand R8.htm agree |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) provided by financing activities | -425780000 | -425780000 | 755994000 | 755994000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property and equipment | -655920000 | 655920000 | -506224000 | 506224000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 449958000 | 449958000 | 403647000 | 403647000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 63407000 | 63407000 | 47732000 | 47732000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Payments of cash dividends | -83136000 | 83136000 | -72309000 | 72309000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock and payment of related excise taxes | -200505000 | 200505000 | -734000 | 734000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest, net of amount capitalized | 110546000 | 110546000 | 86598000 | 86598000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000726958-26-000046 R8.htm period ..2026-04-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes, net | 138018000 | 138018000 | 89771000 | 89771000 | Y | FILING-CHECKED | accn 0000726958-26-000046 R8.htm period ..2026-04-30 / check: hand R8.htm agree |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current maturities of long-term debt and finance lease obligations + Long-term debt and finance lease obligations, net o | 2431594000 | 2431594000 | 2508545000 |  | Y | FILING-CHECKED | both BS debt lines include finance lease obligations by label (R40), not added again / check: hand R3.htm corrected: Current maturities of LTD and finance lease obligations 101,357 + LTD and finance lease obligations net 2,330,237 = 2,431,594 (agrees; finance leases 115,197 inside per R40 label/extensible list, not added again); FY1 blank: 94,925 + 2,413,620 = 2,508,545. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 36904285 | 36904285 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-04-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 7767216000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Cost of goods sold (exclusive of depreciation and amortization, shown separately' on us-gaap:CostOfGoodsSold = 6327431000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000726958-15-000075 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Interest, net' on us-gaap:InterestExpense = 41225000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 282025000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Federal and state income taxes' on us-gaap:IncomeTaxExpenseBenefit = 101397000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 180628000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Basic (in Dollars per share)' on us-gaap:EarningsPerShareBasic = 4.66 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000726958-15-000075 R4.htm prints 'Diluted (in Dollars per share)' on us-gaap:EarningsPerShareDiluted = 4.62 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000726958-15-000075 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000726958-15-000075 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 48541000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 197331000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 305260000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Net property and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 2019364000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 127046000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Total assets' on us-gaap:Assets = 2469965000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 226577000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 364889000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1594736000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000726958-15-000075 R2.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 875229000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 341682000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -399143000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -15639000 (FILING-CHECKED)
- capex: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Purchase of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -360734000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 156111000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 7307000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Payments of cash dividends' on us-gaap:PaymentsOfDividends = -30175000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000726958-15-000075 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Cash paid during the year for interest, net of amount capitalized' on us-gaap:InterestPaidNet = 41382000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000726958-15-000075 R7.htm prints 'Cash paid for income taxes, net' on us-gaap:IncomeTaxesPaidNet = 64367000 (FILING-CHECKED)
- revenue: era 10-K 0000726958-17-000055 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 7506587000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000726958-17-000055 R4.htm prints 'Cost of goods sold (exclusive of depreciation and amortization, shown separately' on us-gaap:CostOfGoodsSold = 5825426000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000726958-19-000078 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 263402000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 14 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 5.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
