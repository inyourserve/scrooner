# ADP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000008670-26-000030 (CIK 0000008670, filed 2026-08-05): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000008670-15-000021 (CIK 0000008670, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000008670-18-000011 (CIK 0000008670, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000008670-21-000027 (CIK 0000008670, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0000008670.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 21947400000 | 21947400000 | 20560900000 | 20560900000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | TOTAL COSTS OF REVENUES | 11760200000 | 11760200000 | 11097300000 | 11097300000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (923 tags across all 107 R pages, face and notes) of 0000008670-26-000030; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | TOTAL EXPENSES | 16627700000 | 16627700000 | 15604900000 | 15604900000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general, and administrative expenses | 4408200000 | 4408200000 | 4051700000 | 4051700000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 1028800000 | 1028800000 | 988600000 | 988600000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (923 tags across all 107 R pages, face and notes) of 0000008670-26-000030; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | 459300000 | 459300000 | 455900000 | 455900000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | EARNINGS BEFORE INCOME TAXES | 5730300000 | 5730300000 | 5310100000 | 5310100000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 1316800000 | 1316800000 | 1230400000 | 1230400000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | NET EARNINGS | 4413500000 | 4413500000 | 4079700000 | 4079700000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | BASIC EARNINGS PER SHARE (in dollars per share) | 10.97 | 10.97 | 10.02 | 10.02 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | DILUTED EARNINGS PER SHARE (in dollars per share) | 10.94 | 10.94 | 9.98 | 9.98 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic weighted average shares outstanding (in shares) | 402300000 | 402300000 | 407100000 | 407100000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted weighted average shares outstanding (in shares) | 403300000 | 403300000 | 408700000 | 408700000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R3.htm period ..2026-06-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 4230100000 | 4230100000 | 3347800000 | 3347800000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net of allowance for doubtful accounts of $44.5 and $47.1, respectively | 3521100000 | 3521100000 | 3579100000 | 3579100000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (923 tags across all 107 R pages, face and notes) of 0000008670-26-000030; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 52561100000 | 52561100000 | 43252200000 | 43252200000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 641300000 | 641300000 | 655400000 | 655400000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 3284400000 | 3284400000 | 3273500000 | 3273500000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 63193300000 | 63193300000 | 53369300000 | 53369300000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 162500000 | 162500000 | 169100000 | 169100000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 50024900000 | 50024900000 | 41278300000 | 41278300000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 57162100000 | 57162100000 | 47181300000 | 47181300000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders’ equity | 6031200000 | 6031200000 | 6188000000 | 6188000000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R6.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash flows provided by operating activities | 5441200000 | 5441200000 | 4939700000 | 4939700000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash flows used in investing activities | -4713800000 | -4713800000 | -3035000000 | -3035000000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash flows provided by/(used in) financing activities | 4881000000 | 4881000000 | -6973400000 | -6973400000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment | R10.htm | Capital expenditures | -196600000 | 196600000 | -168700000 | 168700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation and amortization | 585900000 | 585900000 | 582400000 | 582400000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation expense | 242600000 | 242600000 | 266100000 | 266100000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R10.htm | Dividends paid | -2626300000 | 2626300000 | -2398900000 | 2398900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Repurchases of common stock | -2083300000 | 2083300000 | -1280500000 | 1280500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Cash paid for interest | 439600000 | 439600000 | 426800000 | 426800000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R10.htm | Cash paid for income taxes, net of income tax refunds | 1006700000 | 1006700000 | 1198000000 | 1198000000 | Y | FILING-CHECKED | accn 0000008670-26-000030 R10.htm period ..2026-06-30 |
| total_debt | component sum | us-gaap:CommercialPaper+us-gaap:LongTermDebtNoncurrent | R6.htm | Obligations under commercial paper borrowings + Long-term debt | 4964100000 | 4964100000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding | 397800000 | 397800000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-06-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000008670-15-000021 R2.htm prints 'TOTAL REVENUES' on us-gaap:Revenues = 10938500000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000008670-15-000021 R2.htm prints 'TOTAL COSTS OF REVENUES' on us-gaap:CostOfServices = 6427600000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000008670-15-000021 R2.htm prints 'TOTAL EXPENSES' on us-gaap:CostsAndExpenses = 8931000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000008670-15-000021 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 2496900000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000008670-15-000021 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000008670-15-000021 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 6500000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000008670-15-000021 R2.htm prints 'EARNINGS FROM CONTINUING OPERATIONS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 2.071e+09 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000008670-15-000021 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 694200000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000008670-15-000021 R2.htm prints 'NET EARNINGS' on us-gaap:NetIncomeLoss = 1452500000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000008670-15-000021 R2.htm prints 'BASIC EARNINGS PER SHARE' on us-gaap:EarningsPerShareBasic = 3.07 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000008670-15-000021 R2.htm prints 'DILUTED EARNINGS PER SHARE' on us-gaap:EarningsPerShareDiluted = 3.05 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000008670-15-000021 R2.htm prints 'Basic weighted average shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 472600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000008670-15-000021 R2.htm prints 'Diluted weighted average shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 475800000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1639300000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 1546900000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 28809200000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Property, Plant and Equipment, Net' on us-gaap:PropertyPlantAndEquipmentNet = 672700000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 1793500000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Total assets' on us-gaap:Assets = 33110500000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 194500000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 27113700000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 28302000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000008670-15-000021 R5.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 4808500000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Net cash flows provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1905600000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Net cash flows (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -3760300000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Net cash flows provided by / (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1616700000 (FILING-CHECKED)
- capex: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment = -158800000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 277900000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 143200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -927600000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000008670-15-000021 R9.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1557200000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000008670-15-000021 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000008670-15-000021 R9.htm read; no row matched (auto)
- revenue: era 10-K 0000008670-18-000011 R2.htm prints 'TOTAL REVENUES' on us-gaap:Revenues = 13325800000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000008670-18-000011 R2.htm prints 'TOTAL COSTS OF REVENUES' on us-gaap:CostOfServices = 7842600000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000008670-21-000027 R2.htm prints 'EARNINGS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 3361200000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: R3 prints no gross profit line; MetaLinks: GrossProfit absent
- operating_expenses: combined us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: R3 'TOTAL EXPENSES' 16,627.7 includes costs of revenues: combined
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: R3 prints no operating income line (earnings before income taxes only); MetaLinks: OperatingIncomeLoss absent
- inventory: not_presented  (R6.htm): 2026-11-12 R6.htm: no inventory line on R6; MetaLinks: InventoryNet absent
- total_debt: component sum us-gaap:CommercialPaper+us-gaap:LongTermDebtNoncurrent (R6.htm): 2026-11-12 R6.htm: R6 prints commercial paper 0.0 + long-term debt 4,964.1 = 4,964.1 = XBRL; no other borrowing line
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'NET EARNINGS' is the net_income line, printed 4413500000 = filing XBRL 4413500000; agrees
- diluted_eps: mapped us-gaap:EarningsPerShareDiluted (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'DILUTED EARNINGS PER SHARE (in dollars per share)' is the diluted_eps line, printed 10.94 = filing XBRL 10.94; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R10.htm): 2026-11-12 R10.htm: 10% mapped sample: CF R10.htm 'Repurchases of common stock' is the share_buybacks line, printed -2083300000 = filing XBRL 2083300000; agrees
