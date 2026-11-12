# WMB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000107263-26-000006 (CIK 0000107263, filed 2026-02-24): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000107263-16-000021 (CIK 0000107263, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000107263-25-000031 (CIK 0000107263, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000107263-24-000019 (CIK 0000107263, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- companyfacts CIK0000107263.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenues | 11950000000 | 11950000000 | 10503000000 | 10503000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R3.htm | Cost of Goods and Service, Excluding Depreciation, Depletion, and Amortization | 2133000000 |  | 2075000000 |  | API missing | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1305 tags across all 110 R pages, face and notes) of 0000107263-26-000006; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total costs and expenses | 7754000000 | 7754000000 | 7164000000 | 7164000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative expenses | 721000000 | 721000000 | 708000000 | 708000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1305 tags across all 110 R pages, face and notes) of 0000107263-26-000006; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | 4196000000 | 4196000000 | 3339000000 | 3339000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -1442000000 | 1442000000 | -1364000000 | 1364000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (loss) before income taxes | 3625000000 | 3625000000 | 2986000000 | 2986000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Less: Provision (benefit) for income taxes | 857000000 | 857000000 | 640000000 | 640000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 2618000000 | 2618000000 | 2225000000 | 2225000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income (loss) available to common stockholders - Basic | 2.14 | 2.14 | 1.82 | 1.82 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income (loss) available to common stockholders - Diluted | 2.14 | 2.14 | 1.82 | 1.82 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted Average Number of Shares Outstanding, Basic | 1221000000 | 1221000000 | 1219000000 | 1219000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted Average Number of Shares Outstanding, Diluted | 1225000000 | 1225000000 | 1223000000 | 1223000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R6.htm | Cash and cash equivalents | 63000000 | 63000000 | 60000000 | 60000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R6.htm | Receivables, Net, Current | 2084000000 | 2084000000 | 1863000000 | 1863000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 314000000 | 314000000 | 279000000 | 279000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 3244000000 | 3244000000 | 2661000000 | 2661000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, Plant and Equipment, Net | 41996000000 | 41996000000 | 38692000000 | 38692000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R64.htm | Acquisitions (Details) |  | 466000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'Acquisitions (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 58573000000 | 58573000000 | 54532000000 | 54532000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 2224000000 | 2224000000 | 1613000000 | 1613000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 6106000000 | 6106000000 | 5312000000 | 5312000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1305 tags across all 110 R pages, face and notes) of 0000107263-26-000006; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders’ equity | 12807000000 | 12807000000 | 12436000000 | 12436000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided (used) by operating activities | 5898000000 | 5898000000 | 4974000000 | 4974000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash provided (used) by investing activities | -5489000000 | -5489000000 | -4863000000 | -4863000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash provided (used) by financing activities | -406000000 | -406000000 | -2201000000 | -2201000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Capital expenditures (1) | -4893000000 | 4893000000 | -2573000000 | 2573000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation, depletion, and amortization | 2347000000 | 2347000000 | 2219000000 | 2219000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Amortization of stock-based awards | 93000000 | 93000000 | 99000000 | 99000000 | Y | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Common dividends paid | -2442000000 | 2442000000 | -2316000000 | 2316000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Purchases of treasury stock | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0000107263-26-000006 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R95.htm | Cash Payments For Interest (Net of Amounts Capitalized) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R95.htm 'Cash Payments For Interest (Net of Amounts Capitalized) (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R76.htm | Provision (Benefit) for Income Taxes Cash Payments and Textuals (Details) |  | 162000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R76.htm 'Provision (Benefit) for Income Taxes Cash Payments and Textuals (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:CommercialPaper+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Commercial paper + Long-term debt due within one year + Long-term debt | 29361000000 | 29361000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1305 tags across all 110 R pages, face and notes) of 0000107263-26-000006; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Total revenues' on us-gaap:Revenues = 7360000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000107263-16-000021 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 7134000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Selling, general, and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 741000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Operating income (loss)' on us-gaap:OperatingIncomeLoss = 226000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000107263-16-000021 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Income (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -1713000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Provision (benefit) for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -399000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Net income (loss) attributable to The Williams Companies, Inc.' on us-gaap:NetIncomeLoss = -571000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Net income (loss)' on us-gaap:EarningsPerShareBasic = -0.76 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Net income (loss)' on us-gaap:EarningsPerShareDiluted = -0.76 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Weighted-average shares (thousands)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 749271000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000107263-16-000021 R2.htm prints 'Weighted-average shares (thousands)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 749271000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 100000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Income tax receivable' on us-gaap:IncomeTaxesReceivable = 7000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 127000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1527000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Property, plant, and equipment – net' on us-gaap:PropertyPlantAndEquipmentNet = 29579000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 47000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Total assets' on us-gaap:Assets = 49020000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 744000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2497000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000107263-16-000021 R5.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 6148000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Net cash provided (used) by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2678000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Net cash provided (used) by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -3299000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 481000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Capital expenditures (1)' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -3167000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 1738000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Amortization of stock-based awards' on us-gaap:ShareBasedCompensation = 82000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000107263-16-000021 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -1836000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000107263-16-000021 R8.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000107263-16-000021 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000107263-16-000021 R8.htm read; no row matched (auto)
- sga_expense: era 10-K 0000107263-25-000031 R3.htm prints 'Selling, general, and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 708000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000107263-24-000019 R3.htm prints 'Interest expense' on us-gaap:InterestCostsIncurred = -1236000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:OperatingCostsAndExpenses+us-gaap:DepreciationDepletionAndAmortization+us-gaap:GeneralAndAdministrativeExpense+us-gaap:OtherAssetImpairmentCharges+us-gaap:GainLossOnSaleOfBusiness+us-gaap:OtherOperatingIncomeExpenseNet (R3.htm): 2026-11-12 R3.htm: corrected: opex = 2,282 + 2,347 + 721 + 212 + 0 - 7 = 5,555 = 11,950 - 2,199 - 4,196
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- goodwill: combined us-gaap:Goodwill (R64.htm): 2026-11-12 R64.htm: R64 466 is goodwill recognized in an acquisition (not the BS balance); the BS bundles goodwill inside 'Intangible assets - net' (IntangibleAssetsNetIncludingGoodwill 6,763): combined
- total_liabilities: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R95.htm): 2026-11-12 R95.htm: R95 consolidated 'Cash payments for interest (net of amounts capitalized)' 1,404 (the 336 and 24 rows are subsidiaries); InterestPaidNet per DQC_0065
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaid (R76.htm): 2026-11-12 R76.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:CommercialPaper+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R6.htm): 2026-11-12 R6.htm: agree: R6 lines on LongTermDebtAndCapitalLeaseObligations; no finance-lease facts in the filing
- shares_outstanding: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- sga_expense: mapped us-gaap:GeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'General and administrative expenses' is the sga_expense line, printed 721000000 = filing XBRL 721000000; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net income' is the net_income line, printed 2618000000 = filing XBRL 2618000000; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Weighted Average Number of Shares Outstanding, Bas' is the weighted_basic_shares line, printed 1221000000 = filing XBRL 1221000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Property, Plant and Equipment, Net' is the ppe_net line, printed 41996000000 = filing XBRL 41996000000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R10.htm): 2026-11-12 R10.htm: 20% mapped sample: CF R10.htm 'Net cash provided (used) by financing activities' is the cash_flow_financing line, printed -406000000 = filing XBRL -406000000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R10.htm): 2026-11-12 R10.htm: 20% mapped sample: CF R10.htm 'Common dividends paid' is the dividends_paid line, printed -2442000000 = filing XBRL 2442000000; agrees
- cost_of_revenue: component sum check: hand 2026-11-12 R3.htm: corrected: R3 prints two cost rows on the same tag (members oil and gas purchased 2,133 and natural gas purchased for shrink 66); the tool took the first: 2,199
