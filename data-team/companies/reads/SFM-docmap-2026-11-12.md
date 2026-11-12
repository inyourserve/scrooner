# SFM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001575515-26-000008 (CIK 0001575515, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001564590-19-003562 (CIK 0001575515, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000950170-24-018768 (CIK 0001575515, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001575515.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 8806159000 | 8806159000 | 7719290000 | 7719290000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 5389770000 | 5389770000 | 4777799000 | 4777799000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 3416389000 | 3416389000 | 2941491000 | 2941491000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 2574687000 | 2574687000 | 2291350000 | 2291350000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 686158000 | 686158000 | 504497000 | 504497000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest (income) expense, net | -2626000 | 2626000 | -2201000 | 2201000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 688784000 | 688784000 | 506698000 | 506698000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | 165114000 | 165114000 | 126097000 | 126097000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 523670000 | 523670000 | 380601000 | 380601000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 5.36 | 5.36 | 3.79 | 3.79 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 5.31 | 5.31 | 3.75 | 3.75 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 97687000 | 97687000 | 100363000 | 100363000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 98704000 | 98704000 | 101379000 | 101379000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 257282000 | 257282000 | 265159000 | 265159000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Accounts receivable, net | 65221000 | 65221000 | 30901000 | 30901000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 427095000 | 427095000 | 343329000 | 343329000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 809904000 | 809904000 | 675520000 | 675520000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net of accumulated depreciation | 1085356000 | 1085356000 | 895189000 | 895189000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 381750000 | 381750000 | 381750000 | 381750000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4158649000 | 4158649000 | 3640699000 | 3640699000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 291033000 | 291033000 | 213414000 | 213414000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 870803000 | 870803000 | 679968000 | 679968000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2755575000 | 2755575000 | 2318806000 | 2318806000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 1403074000 | 1403074000 | 1321893000 | 1321893000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash flows from operating activities | 715998000 | 715998000 | 645214000 | 645214000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Cash flows used in investing activities | -248267000 | -248267000 | -230375000 | -230375000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Cash flows used in financing activities | -474050000 | -474050000 | -351496000 | -351496000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -248267000 | 248267000 | -230375000 | 230375000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization expense | 157722000 | 157722000 | 140164000 | 140164000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 31103000 | 31103000 | 28417000 | 28417000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -471926000 | 471926000 | -228472000 | 228472000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 1809000 | 1809000 | 5008000 | 5008000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes | 120076000 | 120076000 | 102226000 | 102226000 | Y | FILING-CHECKED | accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: no standard debt line on the BS face; not hand-verified |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 95926024 | 95926024 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-28; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001564590-19-003562 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -27435000 (FILING-CHECKED)
- ppe_net: era 10-K 0000950170-24-018768 R2.htm prints 'Property and equipment, net of accumulated depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 798707000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
