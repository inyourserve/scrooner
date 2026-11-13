# ITW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000049826-26-000008 (CIK 0000049826, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000049826-16-000151 (CIK 0000049826, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, CF R7.htm
- 10-K 0000049826-18-000017 (CIK 0000049826, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000049826-24-000008 (CIK 0000049826, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0000049826.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Operating Revenue | 16044000000 | 16044000000 | 15898000000 | 15898000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of revenue | 8969000000 | 8969000000 | 8858000000 | 8858000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (950 tags across all 96 R pages, face and notes) of 0000049826-26-000008; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (950 tags across all 96 R pages, face and notes) of 0000049826-26-000008; no face row matched |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (950 tags across all 96 R pages, face and notes) of 0000049826-26-000008; no face row matched |
| research_and_development | mapped | itw:SellingAdministrativeAndResearchAndDevelopmentExpenses | R3.htm | Selling, administrative, and research and development expenses | 2779000000 |  | 2675000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 4216000000 | 4216000000 | 4264000000 | 4264000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -292000000 | 292000000 | -283000000 | 283000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Income Before Taxes | 3966000000 | 3966000000 | 4422000000 | 4422000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 900000000 | 900000000 | 934000000 | 934000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:ProfitLoss | R3.htm | Net Income | 3066000000 | 3066000000 | 3488000000 | 3488000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 10.52 | 10.52 | 11.75 | 11.75 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 10.49 | 10.49 | 11.71 | 11.71 | Y | FILING-CHECKED | accn 0000049826-26-000008 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R65.htm | Net Income Per Share (Details) |  | 291500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Net Income Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R65.htm | Net Income Per Share (Details) |  | 292300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Net Income Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and equivalents | 851000000 | 851000000 | 948000000 | 948000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Trade receivables | 3227000000 | 3227000000 | 2991000000 | 2991000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1659000000 | 1659000000 | 1605000000 | 1605000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 6200000000 | 6200000000 | 5856000000 | 5856000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Net plant and equipment | 2230000000 | 2230000000 | 2036000000 | 2036000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 5098000000 | 5098000000 | 4839000000 | 4839000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 16148000000 | 16148000000 | 15067000000 | 15067000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 522000000 | 522000000 | 519000000 | 519000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 5126000000 | 5126000000 | 4308000000 | 4308000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (950 tags across all 96 R pages, face and notes) of 0000049826-26-000008; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R5.htm | Total stockholders' equity | 3226000000 | 3226000000 | 3317000000 | 3317000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000049826-26-000008 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 3126000000 | 3126000000 | 3281000000 | 3281000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used for) investing activities | -521000000 | -521000000 | -144000000 | -144000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used for) financing activities | -2744000000 | -2744000000 | -3189000000 | -3189000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Additions to plant and equipment | -419000000 | 419000000 | -437000000 | 437000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 317000000 | 317000000 | 301000000 | 301000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 69000000 | 69000000 | 61000000 | 61000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends paid | -1785000000 | 1785000000 | -1695000000 | 1695000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -1500000000 | 1500000000 | -1500000000 | 1500000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash Paid During the Year for Interest | 279000000 | 279000000 | 248000000 | 248000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash Paid During the Year for Income Taxes, Net of Refunds | 1052000000 | 1052000000 | 1180000000 | 1180000000 | Y | FILING-CHECKED | accn 0000049826-26-000008 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt + Long-term debt | 8969000000 | 8969000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 288600000 | 288600000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Operating Revenue' on us-gaap:SalesRevenueNet = 13405000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Cost of revenue' on us-gaap:CostOfGoodsAndServicesSold = 7888000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Selling, administrative, and research and development expenses' on itw:SellingAdministrativeAndResearchAndDevelopmentExpenses = 2417000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 2867000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -226000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Income from Continuing Operations Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 2719000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 820000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Net Income' on us-gaap:ProfitLoss = 1899000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 5.16 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000049826-16-000151 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 5.13 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000049826-16-000151 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000049826-16-000151 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Cash and equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3090000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Trade receivables' on us-gaap:ReceivablesNetCurrent = 2203000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 1086000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 6720000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Net plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 1577000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 4439000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Total Assets' on us-gaap:Assets = 15729000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 449000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2368000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000049826-16-000151 R5.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 5228000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2299000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Net cash provided by (used for) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -210000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Net cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2526000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000049826-16-000151 R7.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0000049826-16-000151 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 41000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -742000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2002000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Cash Paid During the Year for Interest' on us-gaap:InterestPaidNet = 200000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000049826-16-000151 R7.htm prints 'Cash Paid During the Year for Income Taxes, Net of Refunds' on us-gaap:IncomeTaxesPaidNet = 775000000 (FILING-CHECKED)
- revenue: era 10-K 0000049826-18-000017 R2.htm prints 'Operating Revenue' on us-gaap:SalesRevenueNet = 14314000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000049826-24-000008 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -266000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- research_and_development: API missing (itw:SellingAdministrativeAndResearchAndDevelopmentExpenses)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum itw:SellingAdministrativeAndResearchAndDevelopmentExpenses+itw:AmortizationandImpairmentofIntangibleAssets (R3.htm): 2026-11-12 R3.htm: corrected: 2,779 + 80 = 2,859 = 16,044 - 8,969 - 4,216
- sga_expense: combined itw:SellingAdministrativeAndResearchAndDevelopmentExpenses (R3.htm): 2026-11-12 R3.htm: corrected: ITW prints SG&A only bundled with R&D (custom tag): combined, not not_presented
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R65.htm): 2026-11-12 R65.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R65.htm): 2026-11-12 R65.htm: agree: carrying sentence read: the note value is the full data point
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- depreciation_and_amortization: combined us-gaap:Depreciation (R9.htm): 2026-11-12 R9.htm: CF R9 prints depreciation 317 and 'Amortization and impairment of intangible assets' 80; the second line includes impairment: combined
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating Revenue' is the revenue line, printed 16044000000 = filing XBRL 16044000000; agrees
- income_before_tax: mapped us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income Before Taxes' is the income_before_tax line, printed 3966000000 = filing XBRL 3966000000; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Cash and equivalents' is the cash_and_equivalents line, printed 851000000 = filing XBRL 851000000; agrees
- stockholders_equity: combined us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest (R5.htm): 2026-11-12 R5.htm: sample DISAGREES: 'Total stockholders' equity' 3,226 is on StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest and includes NCI (1); no parent-only line: combined
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Repurchases of common stock' is the share_buybacks line, printed -1500000000 = filing XBRL 1500000000; agrees
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BSP R6.htm 'Common stock, outstanding (in shares)' is the shares_outstanding line, printed 288600000 = filing XBRL 288600000; agrees
