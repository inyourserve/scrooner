# DXCM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001093557-26-000027 (CIK 0001093557, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001093557-16-000432 (CIK 0001093557, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001093557-18-000018 (CIK 0001093557, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001093557-24-000021 (CIK 0001093557, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001093557.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 4662000000 | 4662000000 | 4033000000 | 4033000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 1860100000 | 1860100000 | 1594800000 | 1594800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2801900000 | 2801900000 | 2438200000 | 2438200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1890100000 | 1890100000 | 1838200000 | 1838200000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1291000000 | 1291000000 | 1285800000 | 1285800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 599100000 | 599100000 | 552400000 | 552400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 911800000 | 911800000 | 600000000 | 600000000 | Y | FILING-CHECKED | accn 0001093557-26-000027 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R51.htm | Balance Sheet Details and Other Financial Information - Other Income (Expense), Net (Details) | -18300000 | 18300000 | -19000000 |  | Y (sign differs: printed in parentheses) | FILING-CHECKED | not on the face statement; shown in R51.htm 'Balance Sheet Details and Other Financial Information - Other Income (Expense), ' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R51.htm corrected: Face shows only Other income, net; note R51 prints gross Interest expense (18.3) / (19.0) on InterestExpenseNonoperating; filled printed values. |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1088400000 | 1088400000 | 709000000 | 709000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 252100000 | 252100000 | 132800000 | 132800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 836300000 | 836300000 | 576200000 | 576200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in usd per share) | 2.14 | 2.14 | 1.46 | 1.46 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in usd per share) | 2.09 | 2.09 | 1.42 | 1.42 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Shares used to compute basic net income per share (in shares) | 390200000 | 390200000 | 393600000 | 393600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Shares used to compute diluted net income per share (in shares) | 405500000 | 405500000 | 412700000 | 412700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 917700000 | 917700000 | 606100000 | 606100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 1216100000 | 1216100000 | 1005700000 | 1005700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 629100000 | 629100000 | 542600000 | 542600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4033300000 | 4033300000 | 4301400000 | 4301400000 | Y | FILING-CHECKED | accn 0001093557-26-000027 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 1559900000 | 1559900000 | 1339900000 | 1339900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 24200000 | 24200000 | 22800000 | 22800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 6339900000 | 6339900000 | 6484500000 | 6484500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndOtherAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued liabilities | 1944000000 | 1944000000 | 1585100000 | 1585100000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001093557-26-000027 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 2142500000 | 2142500000 | 2932000000 | 2932000000 | Y | FILING-CHECKED | accn 0001093557-26-000027 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3593900000 | 3593900000 | 4381900000 | 4381900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 2746000000 | 2746000000 | 2102600000 | 2102600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1440700000 | 1440700000 | 989500000 | 989500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | 536000000 | 536000000 | -207500000 | -207500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -1686400000 | -1686400000 | -734800000 | -734800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -363500000 | 363500000 | -358800000 | 358800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 251800000 | 251800000 | 217700000 | 217700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 159600000 | 159600000 | 170400000 | 170400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (862 tags across all 82 R pages, face and notes) of 0001093557-26-000027; no face row matched / check: hand R8.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchases of treasury stock | -500000000 | 500000000 | -750000000 | 750000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid during the year for interest | 11400000 | 11400000 | 11400000 | 11400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid during the year for income taxes | 94400000 | 94400000 | 198000000 | 198000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001093557-26-000027 R8.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:ConvertibleNotesPayableCurrent+us-gaap:ConvertibleLongTermNotesPayable+us-gaap:FinanceLeaseLiability | R3.htm | Current portion of long-term senior convertible notes + Long-term senior convertible notes + finance lease liability (R61) | 1301400000 |  |  |  |  | FILING-CHECKED | convertible notes from BS R3 (0.0 + 1,240.9) plus finance lease liability 60.5 from note R61; FY1 finance lease total not printed (noncurrent 58.5 only); FY1 notes alone = 2,441.4 / check: hand R3.htm corrected: Face prints Current portion of senior convertible notes 0.0 / 1,204.4 and Long-term senior convertible notes 1,240.9 / 1,237.0; R61 note adds finance lease liability 60.5 (current 6.7 + noncurrent 53.8). FY0 = 0 + 1,240.9 + 60.5 = 1,301.4; FY1 lease total not printed (only noncurrent 58.5), so FY1 left blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock outstanding (in shares) | 384800000 | 384800000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Total Revenue' on us-gaap:SalesRevenueNet = 402000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Total cost of sales' on us-gaap:CostOfRevenue = 123600000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 278400000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 335500000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 198000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 137500000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Operating loss' on us-gaap:OperatingIncomeLoss = -57100000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -400000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Loss before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -57500000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -100000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Net loss' on us-gaap:NetIncomeLoss = -57600000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Basic and diluted net loss per share' on us-gaap:EarningsPerShareBasicAndDiluted = -0.72 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001093557-16-000432 R4.htm prints 'Basic and diluted net loss per share' on us-gaap:EarningsPerShareBasicAndDiluted = -0.72 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001093557-16-000432 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001093557-16-000432 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 86100000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 74100000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 35200000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 231300000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 54700000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 3700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Total assets' on us-gaap:Assets = 292000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndOtherAccruedLiabilitiesCurrent = 38900000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 6.69e+07 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 70800000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001093557-16-000432 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 221200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Net Cash Provided by (Used in) Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 49000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -51500000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 16800000 (FILING-CHECKED)
- capex: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Purchase of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -3.33e+07 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 10800000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 82700000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001093557-16-000432 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001093557-16-000432 R7.htm prints 'Interest Paid' on us-gaap:InterestPaid = 300000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001093557-16-000432 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001093557-18-000018 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 718500000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001093557-18-000018 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 226400000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001093557-18-000018 R7.htm prints 'Cash paid during the year for interest' on us-gaap:InterestPaid = 2400000 (FILING-CHECKED)
- interest_expense: era 10-K 0001093557-24-000021 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
