# MUR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001628280-26-011709 (CIK 0000717423, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000717423-24-000008 (CIK 0000717423, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000717423-23-000015 (CIK 0000717423, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0000717423.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues and other income | 2718823000 | 2718823000 | 3028474000 | 3028474000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Costs of purchased natural gas | 0 | 0 | 3147000 | 3147000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 2417586000 | 2417586000 | 2425881000 | 2425881000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling and general expenses | 137332000 | 137332000 | 110085000 | 110085000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income from continuing operations | 301237000 | 301237000 | 602593000 | 602593000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense, net | -96072000 | 96072000 | -105926000 | 105926000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income from continuing operations before income taxes | 182866000 | 182866000 | 567569000 | 567569000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 44552000 | 44552000 | 78272000 | 78272000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME ATTRIBUTABLE TO MURPHY | 104234000 | 104234000 | 407171000 | 407171000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income (in USD per share) | 0.73 | 0.73 | 2.71 | 2.71 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income (in USD per share) | 0.72 | 0.72 | 2.7 | 2.7 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 143124118 | 143124118 | 150011458 | 150011458 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 144025322 | 144025322 | 151027352 | 151027352 | Y | FILING-CHECKED | accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 377196000 | 377196000 | 423569000 | 423569000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 346759000 | 346759000 | 272530000 | 272530000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 57284000 | 57284000 | 54858000 | 54858000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 816712000 | 816712000 | 785279000 | 785279000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, at cost less accumulated depreciation, depletion and amortization of $15,068,149 in 2025  | 8136346000 | 8136346000 | 8054653000 | 8054653000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9832626000 | 9832626000 | 9667479000 | 9667479000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 572183000 | 572183000 | 472165000 | 472165000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1062749000 | 1062749000 | 942814000 | 942814000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4595929000 | 4595929000 | 4325636000 | 4325636000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Murphy Shareholders' Equity | 5118380000 | 5118380000 | 5194250000 | 5194250000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R7.htm | Net cash provided by continuing operations activities | 1247808000 | 1247808000 | 1728990000 | 1728990000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash required by investing activities | -1028926000 | -1028926000 | -908164000 | -908164000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash required by financing activities | -264065000 | -264065000 | -716541000 | -716541000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| capex | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the capex tag/label rules; not hand-verified |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation, depletion and amortization | 977753000 | 977753000 | 865753000 | 865753000 | Y | FILING-CHECKED | accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| sbc | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the sbc tag/label rules; not hand-verified |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Cash dividends paid | -186205000 | 186205000 | -179961000 | 179961000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -102620000 | 102620000 | -301350000 | 301350000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt, finance lease + Long-term debt, including finance lease obligation | 1385080000 | 1385080000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0000717423-24-000008 R5.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -112373000 (FILING-CHECKED)
- ppe_net: era 10-K 0000717423-23-000015 R3.htm prints 'Property, plant and equipment, at cost less accumulated depreciation, depletion ' on us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization = 8228016000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
