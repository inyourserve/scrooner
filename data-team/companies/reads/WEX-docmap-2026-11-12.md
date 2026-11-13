# WEX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001309108-26-000010 (CIK 0001309108, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001309108-16-000146 (CIK 0001309108, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001309108-18-000013 (CIK 0001309108, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001309108-19-000020 (CIK 0001309108, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0001309108.json (one call); submissions CIK0001309108.json (SIC 7389).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenues | 2660800000 | 2660800000 | 2628100000 | 2628100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Total cost of services | 1100600000 | 1100600000 | 1037800000 | 1037800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Income statement shows total cost of services then G&A, S&M and D&A to operating income with no gross profit line; revenue and segment pages give none. / pages opened: R3, R12, R32, R42, R56, R69, R70, R130 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No total operating expenses subtotal; the face lists cost of services and G&A, S&M, D&A separately to operating income. / pages opened: R3, R32, R56, R87, R94, R112, R130 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R3.htm | General and administrative + Sales and marketing | 717200000 | 717200000 | 716800000 | 716800000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No R&D expense line or disclosure; label hits are tax-credit rate reconciliation items. / pages opened: R87, R94, R98, R99, R112, R130 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 663900000 | 663900000 | 686300000 | 686300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| interest_expense | combined | wex:FinancingInterestExpenseNetOfFinancialInstruments | R3.htm | Financing interest expense, net of financial instruments | 240600000 |  |  |  |  | FILING-CHECKED | check: hand / Financing interest is reported only net of interest-rate swap results ($240.6M for 2025); gross FinancingInterestExpense is given only for 2023 and operating interest ($109.0M) sits in cost of services. / pages opened: R3, R69, R91, R96, R112, R130 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 420200000 | 420200000 | 417800000 | 417800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax provision | 116100000 | 116100000 | 108200000 | 108200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to shareholders | 304100000 | 304100000 | 309600000 | 309600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 8.57 | 8.57 | 7.59 | 7.59 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 8.47 | 8.47 | 7.5 | 7.5 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 35500000 | 35500000 | 40800000 | 40800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 35900000 | 35900000 | 41300000 | 41300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 905800000 | 905800000 | 595800000 | 595800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndOtherReceivablesNetCurrent | R5.htm | Accounts receivable, net | 3362600000 |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet line 'Accounts receivable, net' is $3,362.6M at 2025-12-31 (customer payment-card receivables), separate from securitized receivables. / pages opened: R5, R8, R61, R62, R71, R73 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet has no inventory line and no listed pages. / pages opened: R5 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 9713000000 | 9713000000 | 8515500000 | 8515500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, equipment and capitalized software | 253700000 | 253700000 | 261200000 | 261200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 3015300000 | 3015300000 | 2983400000 | 2983400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 14399500000 | 14399500000 | 13321600000 | 13321600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrentAndNoncurrent | R5.htm | Accounts payable | 1.07e+09 | 1070400000 | 1090900000 | 1090900000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 9286600000 | 9286600000 | 8.327e+09 | 8327300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 13165000000 | 13165000000 | 11832800000 | 11832800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 1234500000 | 1234500000 | 1488800000 | 1488800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 454300000 | 454300000 | 481400000 | 481400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -696900000 | -696900000 | -960600000 | -960600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used for) financing activities | 418900000 | 418900000 | -260300000 | -260300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, equipment and capitalized software | -140600000 | 140600000 | -147300000 | 147300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 331100000 | 331100000 | 321300000 | 321300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 100300000 | 100300000 | 112200000 | 112200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No dividends in the equity statement or cash flow statement; R29/R120 only describe dividend restrictions. / pages opened: R7, R8, R29, R120 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -799800000 | 799800000 | -652000000 | 652000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 333600000 | 333600000 | 328500000 | 328500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001309108-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R95.htm | Income taxes paid (net of refunds) | 44500000 | 44500000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R95.htm 'Income Taxes - Schedule of Income Taxes Paid (Net of Refunds) (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt, net + Long-term debt, net | 4858400000 | 4858400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 34300000 | 34300000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 854637000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Service fees' on us-gaap:CostOfServices = 138844000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001309108-16-000146 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 228793000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 184908000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 75296000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Net earnings attributable to WEX Inc.' on us-gaap:NetIncomeLoss = 111317000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Basic (in usd per share)' on us-gaap:EarningsPerShareBasic = 2.63 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Diluted (in usd per share)' on us-gaap:EarningsPerShareDiluted = 2.62 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Basic (in usd per share)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 38771000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001309108-16-000146 R4.htm prints 'Diluted (in usd per share)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 38843000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 279989000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001309108-16-000146 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Property, equipment and capitalized software, net' on us-gaap:PropertyPlantAndEquipmentNet = 138585000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1112878000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Total assets' on us-gaap:Assets = 3857946000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrentAndNoncurrent = 378811000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001309108-16-000146 R2.htm read; no row matched (auto)
- total_liabilities: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2762265000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001309108-16-000146 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 1095681000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 445100000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -126658000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Net cash (used for) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -319538000 (FILING-CHECKED)
- capex: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Purchases of property, equipment and capitalized software' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -63491000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 86174000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 12420000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001309108-16-000146 R9.htm prints 'Purchase of shares of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -22011000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001309108-16-000146 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001309108-16-000146 R9.htm read; no row matched (auto)
- revenue: era 10-K 0001309108-18-000013 R4.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 1250548000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001309108-18-000013 R4.htm prints 'Cost of hardware and equipment' on us-gaap:CostOfGoodsSold = 4314000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001309108-18-000013 R9.htm prints 'Interest paid' on us-gaap:InterestPaid = 128888000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001309108-19-000020 R2.htm prints 'Processing costs' on us-gaap:CostOfGoodsAndServicesSold = 547929000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
