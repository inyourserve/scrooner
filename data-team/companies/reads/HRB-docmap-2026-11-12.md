# HRB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000012659-26-000026 (CIK 0000012659, filed 2026-08-14): COVER R1.htm, IS R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001574842-15-000011 (CIK 0000012659, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001574842-18-000019 (CIK 0000012659, era filing): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001838862-21-000028 (CIK 0000012659, era filing): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000012659.json (one call); submissions CIK0000012659.json (SIC 7200).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 3945392000 | 3945392000 | 3760995000 | 3760995000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Costs of revenues | 2196407000 | 2196407000 | 2086111000 | 2086111000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (708 tags across all 71 R pages, face and notes) of 0000012659-26-000026; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 3037706000 | 3037706000 | 2933025000 | 2933025000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 841299000 | 841299000 | 846914000 | 846914000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (708 tags across all 71 R pages, face and notes) of 0000012659-26-000026; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits 'Effective Income Tax Rate Reconciliation, Tax Credit, Percen' R60; us-gaap:IncomeTaxReconciliationTaxCredits 'Effective Income Tax Rate Reconciliation, Tax Credit, Amount' R60 |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (708 tags across all 71 R pages, face and notes) of 0000012659-26-000026; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:OtherNonoperatingIncomeExpense 'Other income (expense), net / Other Nonoperating Income (Exp' R4,R3 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R3.htm | Interest expense on borrowings | -80611000 | 80611000 | -78113000 | 78113000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 853888000 | 853888000 | 781403000 | 781403000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 117570000 | 117570000 | 171953000 | 171953000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME | 733596000 | 733596000 | 605773000 | 605773000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Consolidated (in usd per share) | 5.72 | 5.72 | 4.45 | 4.45 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Consolidated (in usd per share) | 5.66 | 5.66 | 4.39 | 4.39 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R42.htm | Basic weighted average common shares (in shares) | 127644000 | 127644000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R42.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R42.htm | Dilutive weighted average common shares (in shares) | 128866000 | 128866000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R42.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 958706000 | 958706000 | 983277000 | 983277000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables, less allowance for credit losses of $57,504 and $55,775 | 58248000 | 58248000 | 63621000 | 63621000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Tax-services company; balance sheet R5 has no inventory line and no inventory tag or label exists in the filing. / pages opened: R5 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1125557000 | 1125557000 | 1162548000 | 1162548000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, at cost, less accumulated depreciation and amortization of $863,795 and $828,744 | 141456000 | 141456000 | 135068000 | 135068000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 812543000 | 812543000 | 802053000 | 802053000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 3256351000 | 3256351000 | 3263898000 | 3263898000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued expenses | 156330000 | 156330000 | 144046000 | 144046000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 993425000 | 993425000 | 1298610000 | 1298610000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3138863000 | 3138863000 | 3175002000 | 3175002000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity | 117488000 | 117488000 | 88896000 | 88896000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 838695000 | 838695000 | 680883000 | 680883000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -124809000 | -124809000 | -105373000 | -105373000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -734220000 | -734220000 | -647443000 | -647443000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -82614000 | 82614000 | -82034000 | 82034000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 122440000 | 122440000 | 116827000 | 116827000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 30478000 | 30478000 | 32503000 | 32503000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid | -211005000 | 211005000 | -197330000 | 197330000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| share_buybacks | mapped | hrb:PaymentsForRepurchaseOfCommonStockIncludingSharesSurrendered | R7.htm | Repurchase of common stock, including shares surrendered | -512905000 |  | -437133000 |  | API missing | FILING-CHECKED | check: machine-full-filing / company extension tag, matched by printed label / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid on borrowings | 76728000 | 76728000 | 74639000 | 74639000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid (received), net (includes payments for purchased investment tax credits) | 202134000 | 202134000 | 226820000 | 226820000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Long-term debt | 1491493000 | 1491493000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (708 tags across all 71 R pages, face and notes) of 0000012659-26-000026; HAND REVIEW: 5 label candidate(s) incl. custom tags: us-gaap:CommonStockSharesIssued 'Common stock, shares issued (in shares) / Common Stock, Shar' R6; dei:EntityCommonStockSharesOutstanding 'Entity Common Stock, Shares Outstanding / Entity Common Stoc' R1; us-gaap:WeightedAverageNumberDilutedSharesOutstandingAdjustment 'Potential dilutive shares (in shares) / Weighted Average Num' R42; us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding 'Dilutive weighted average common shares (in shares) / Weight' R42; us-gaap:WeightedAverageNumberOfSharesOutstandingBasic 'Basic weighted average common shares (in shares) / Weighted ' R42 |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- income_tax_expense: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- net_income: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- basic_eps: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- diluted_eps: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- weighted_basic_shares: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001574842-15-000011 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- accounts_receivable: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- accounts_payable: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- current_liabilities: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- total_liabilities: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001574842-15-000011 R4.htm read; no row matched (auto)
- cfo: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- cash_flow_investing: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- cash_flow_financing: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- capex: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001574842-15-000011 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001574842-18-000019 R2.htm prints 'Total revenues' on us-gaap:Revenues = 3159931000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001574842-18-000019 R2.htm prints 'Cost of revenues' on us-gaap:CostOfRevenue = 1739729000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001838862-21-000028 R2.htm prints 'Income (loss) from continuing operations before income taxes (benefit)' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 668736000 (FILING-CHECKED)

## Mismatches (printed vs API)
- share_buybacks: API missing (hrb:PaymentsForRepurchaseOfCommonStockIncludingSharesSurrendered)
