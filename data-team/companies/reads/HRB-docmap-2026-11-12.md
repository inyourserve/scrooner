# HRB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000012659-26-000026 (CIK 0000012659, filed 2026-08-14): COVER R1.htm, IS R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000012659.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 3945392000 | 3945392000 | 3760995000 | 3760995000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Costs of revenues | 2196407000 | 2196407000 | 2086111000 | 2086111000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 3037706000 | 3037706000 | 2933025000 | 2933025000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 841299000 | 841299000 | 846914000 | 846914000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the operating_income tag/label rules; not hand-verified |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R3.htm | Interest expense on borrowings | -80611000 | 80611000 | -78113000 | 78113000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 853888000 | 853888000 | 781403000 | 781403000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 117570000 | 117570000 | 171953000 | 171953000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET INCOME | 733596000 | 733596000 | 605773000 | 605773000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Consolidated (in usd per share) | 5.72 | 5.72 | 4.45 | 4.45 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Consolidated (in usd per share) | 5.66 | 5.66 | 4.39 | 4.39 | Y | FILING-CHECKED | accn 0000012659-26-000026 R3.htm period ..2026-06-30 |
| weighted_basic_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_basic_shares tag/label rules; not hand-verified |
| weighted_diluted_shares | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the weighted_diluted_shares tag/label rules; not hand-verified |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 958706000 | 958706000 | 983277000 | 983277000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables, less allowance for credit losses of $57,504 and $55,775 | 58248000 | 58248000 | 63621000 | 63621000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1125557000 | 1125557000 | 1162548000 | 1162548000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, at cost, less accumulated depreciation and amortization of $863,795 and $828,744 | 141456000 | 141456000 | 135068000 | 135068000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 812543000 | 812543000 | 802053000 | 802053000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 3256351000 | 3256351000 | 3263898000 | 3263898000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued expenses | 156330000 | 156330000 | 144046000 | 144046000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 993425000 | 993425000 | 1298610000 | 1298610000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3138863000 | 3138863000 | 3175002000 | 3175002000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity | 117488000 | 117488000 | 88896000 | 88896000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R5.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 838695000 | 838695000 | 680883000 | 680883000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -124809000 | -124809000 | -105373000 | -105373000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -734220000 | -734220000 | -647443000 | -647443000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -82614000 | 82614000 | -82034000 | 82034000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 122440000 | 122440000 | 116827000 | 116827000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 30478000 | 30478000 | 32503000 | 32503000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid | -211005000 | 211005000 | -197330000 | 197330000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| share_buybacks | mapped | hrb:PaymentsForRepurchaseOfCommonStockIncludingSharesSurrendered | R7.htm | Repurchase of common stock, including shares surrendered | -512905000 |  | -437133000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid on borrowings | 76728000 | 76728000 | 74639000 | 74639000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid (received), net (includes payments for purchased investment tax credits) | 202134000 | 202134000 | 226820000 | 226820000 | Y | FILING-CHECKED | accn 0000012659-26-000026 R7.htm period ..2026-06-30 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Long-term debt | 1491493000 | 1491493000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
none found in companyfacts

## Mismatches (printed vs API)
- share_buybacks: API missing (hrb:PaymentsForRepurchaseOfCommonStockIncludingSharesSurrendered)
