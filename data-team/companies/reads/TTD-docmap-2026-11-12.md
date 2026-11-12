# TTD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001671933-26-000014 (CIK 0001671933, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001564590-18-003611 (CIK 0001671933, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0001671933.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 2896284000 | 2896284000 | 2444831000 | 2444831000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Platform operations | 619067000 | 619067000 | 472012000 | 472012000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 2306963000 | 2306963000 | 2017664000 | 2017664000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 518455000 | 518455000 | 535816000 | 535816000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Technology and development | 525141000 | 525141000 | 463319000 | 463319000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 589321000 | 589321000 | 427167000 | 427167000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 658755000 | 658755000 | 507302000 | 507302000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 215451000 | 215451000 | 114226000 | 114226000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 443304000 | 443304000 | 393076000 | 393076000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 0.91 | 0.91 | 0.8 | 0.8 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 0.9 | 0.9 | 0.78 | 0.78 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 488278000 | 488278000 | 490879000 | 490879000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 493551000 | 493551000 | 501924000 | 501924000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 658175000 | 658175000 | 1369463000 | 1369463000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for credit losses of $12,199 and $11,244 as of December 31, 2025 and 2024, respect | 3770194000 | 3770194000 | 3330343000 | 3330343000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | TOTAL CURRENT ASSETS | 5261004000 | 5261004000 | 5336458000 | 5336458000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 396819000 | 396819000 | 209332000 | 209332000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 6153220000 | 6153220000 | 6111951000 | 6111951000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 3007651000 | 3007651000 | 2631213000 | 2631213000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | TOTAL CURRENT LIABILITIES | 3265997000 | 3265997000 | 2873465000 | 2873465000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | TOTAL LIABILITIES | 3668829000 | 3668829000 | 3162806000 | 3162806000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | TOTAL STOCKHOLDERS’ EQUITY | 2484391000 | 2484391000 | 2949145000 | 2949145000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 992721000 | 992721000 | 739456000 | 739456000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -292632000 | -292632000 | -157513000 | -157513000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -1411377000 | -1411377000 | -107609000 | -107609000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -197011000 | 197011000 | -98238000 | 98238000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization expense | 115784000 | 115784000 | 87490000 | 87490000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 490627000 | 490627000 | 494699000 | 494699000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of Class A common stock | -1380422000 | 1380422000 | -234784000 | 234784000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 993000 | 993000 | 986000 | 986000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes, net of refunds | 150114000 | 150114000 | 158579000 | 158579000 | Y | FILING-CHECKED | accn 0001671933-26-000014 R7.htm period ..2025-12-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: no standard debt line on the BS face; not hand-verified |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 475923000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cost_of_revenue: era 10-K 0001564590-18-003611 R4.htm prints 'Platform operations' on us-gaap:CostOfServices = 66230000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-003611 R7.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 31224000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-003611 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -16064000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-003611 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 7390000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
