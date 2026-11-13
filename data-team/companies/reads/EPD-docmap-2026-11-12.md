# EPD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001061219-26-000006 (CIK 0001061219, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001061219-16-000058 (CIK 0001061219, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001061219-18-000008 (CIK 0001061219, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001061219-24-000006 (CIK 0001061219, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- companyfacts CIK0001061219.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenues | 52596000000 | 52596000000 | 56219000000 | 56219000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R55.htm | Inventories - Summary of Cost of Sales and Lower of Cost/Net Realizable Value Adjustments (Details) |  | 38566000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R55.htm 'Inventories - Summary of Cost of Sales and Lower of Cost/Net Realizable Value Ad' (MetaLinks.json presentation); value from companyfacts same accession |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingCostsAndExpenses | R5.htm | Total operating costs and expenses | 45440000000 | 45440000000 | 49045000000 | 49045000000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | Total general and administrative costs | 251000000 | 251000000 | 244000000 | 244000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 7266000000 | 7266000000 | 7338000000 | 7338000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -1401000000 | 1401000000 | -1352000000 | 1352000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 5899000000 | 5899000000 | 6035000000 | 6035000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes (see Note 16) | -23000000 | 23000000 | -65000000 | 65000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to common unitholders | 5810000000 | 5810000000 | 5897000000 | 5897000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:NetIncomeLossPerOutstandingLimitedPartnershipUnitBasicNetOfTax | R5.htm | Basic earnings per common unit (in dollars per unit) | 2.66 | 2.66 | 2.69 | 2.69 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:NetIncomeLossNetOfTaxPerOutstandingLimitedPartnershipUnitDiluted | R5.htm | Diluted earnings per common unit (in dollars per unit) | 2.66 | 2.66 | 2.69 | 2.69 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001061219-26-000006 R5.htm period ..2025-12-31 |
| weighted_basic_shares | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of WeightedAverageNumberOfSharesOutstandingBasic in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R92.htm | Earnings Per Unit (Details) |  | 2188000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Earnings Per Unit (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 969000000 | 969000000 | 583000000 | 583000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 6494000000 |  | 9236000000 |  | API missing | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories (see Note 3) | 3884000000 | 3884000000 | 3955000000 | 3955000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 13360000000 | 13360000000 | 15133000000 | 15133000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net (see Note 4) | 51359000000 | 51359000000 | 49062000000 | 49062000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill (see Note 6) | 5712000000 | 5712000000 | 5712000000 | 5712000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 77902000000 | 77902000000 | 77168000000 | 77168000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 1021000000 |  | 1227000000 |  | API missing | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 12832000000 | 12832000000 | 15177000000 | 15177000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |
| stockholders_equity | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of StockholdersEquity in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash flow provided by operating activities | 8585000000 | 8585000000 | 8115000000 | 8115000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash flow used in investing activities | -5491000000 | -5491000000 | -5433000000 | -5433000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash flow used in financing activities | -2687000000 | -2687000000 | -2164000000 | -2164000000 | Y | FILING-CHECKED | accn 0001061219-26-000006 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -5620000000 | 5620000000 | -4544000000 | 4544000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001061219-26-000006 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | epd:DepreciationAndAccretion | R7.htm | Depreciation and accretion | 2107000000 |  | 1987000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001061219-26-000006 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R96.htm | Equity-Based Awards - Schedule of Equity-Based Award Compensation Expense (Details) |  | 197000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R96.htm 'Equity-Based Awards - Schedule of Equity-Based Award Compensation Expense (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common units under 2019 Buyback Program (see Note 8) | -300000000 | 300000000 | -219000000 | 219000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001061219-26-000006 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R123.htm | Supplemental Cash Flow Information - Schedule of Net Effect of Changes in Operating Assets and Liabilities (Details) |  | 1352000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R123.htm 'Supplemental Cash Flow Information - Schedule of Net Effect of Changes in Operat' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R116.htm | Income Taxes - Schedule of Income Taxes Paid, Net (Details) |  | 12000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R116.htm 'Income Taxes - Schedule of Income Taxes Paid, Net (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current maturities of debt (see Note 7) + Long-term debt (see Note 7) | 34395000000 | 34395000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1150 tags across all 125 R pages, face and notes) of 0001061219-26-000006; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 27027900000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001061219-16-000058 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Total operating costs and expenses' on us-gaap:OperatingExpenses = 23668700000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Total general and administrative costs' on us-gaap:GeneralAndAdministrativeExpense = 192600000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 3540200000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -961800000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 2555900000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Benefit from (provision for) income taxes' on us-gaap:IncomeTaxExpenseBenefit = 2500000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Net income attributable to limited partners' on us-gaap:NetIncomeLoss = 2521200000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Basic earnings per unit (in dollars per unit)' on us-gaap:NetIncomeLossPerOutstandingLimitedPartnershipUnitBasicNetOfTax = 1.28 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001061219-16-000058 R4.htm prints 'Diluted earnings per unit (in dollars per unit)' on us-gaap:NetIncomeLossNetOfTaxPerOutstandingLimitedPartnershipUnitDiluted = 1.26 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001061219-16-000058 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 19000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Accounts receivable - trade, net of allowance for doubtful accounts of $12.1 at ' on us-gaap:AccountsReceivableNetCurrent = 2569900000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 1.038e+09 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4313000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 32034700000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 5745200000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Total assets' on us-gaap:Assets = 48952000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Accounts payable - trade' on us-gaap:AccountsPayableCurrent = 860100000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001061219-16-000058 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 7166600000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001061219-16-000058 R6.htm prints 'Net cash flows provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 4002400000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001061219-16-000058 R6.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -3441800000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001061219-16-000058 R6.htm prints 'Cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -616000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001061219-16-000058 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -3830700000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001061219-16-000058 R6.htm prints 'Depreciation, amortization and accretion' on us-gaap:DepreciationAmortizationAndAccretionNet = 1516000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001061219-16-000058 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001061219-16-000058 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001061219-16-000058 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001061219-16-000058 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001061219-18-000008 R4.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 29241500000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001061219-18-000008 R4.htm read; no row matched (auto)
- interest_expense: era 10-K 0001061219-24-000006 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -1269000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_receivable: API missing (us-gaap:AccountsReceivableNetCurrent)
- accounts_payable: API missing (us-gaap:AccountsPayableCurrent)
- depreciation_and_amortization: API missing (epd:DepreciationAndAccretion)

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServicesSold (R55.htm): 2026-11-12 R55.htm: agree: R55 'Cost of sales' 38,566: the face prints only 'Total operating costs and expenses'; the note gives the full cost of sales
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- weighted_basic_shares: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R92.htm): 2026-11-12 R92.htm: agree: carrying sentence read: the note value is the full data point
- total_liabilities: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- stockholders_equity: definition_call  (R3.htm): 2026-11-12 R3.htm: MLP: the BS prints partners' equity, not stockholders' equity; whether partners' equity maps to stockholders_equity is a template call for Dhairya
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R96.htm): 2026-11-12 R96.htm: agree: carrying sentence read: the note value is the full data point
- dividends_paid: definition_call  (R7.htm): 2026-11-12 R7.htm: MLP: the CF prints distributions to common unitholders, not dividends; template call for Dhairya
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R123.htm): 2026-11-12 R123.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R116.htm): 2026-11-12 R116.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: agree: R3 debt lines; no finance-lease facts in the filing
- shares_outstanding: definition_call  (R3.htm): 2026-11-12 R3.htm: MLP: common units outstanding, not shares; template call for Dhairya
- operating_income: mapped us-gaap:OperatingIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Operating income' is the operating_income line, printed 7266000000 = filing XBRL 7266000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current assets' is the current_assets line, printed 13360000000 = filing XBRL 13360000000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current liabilities' is the current_liabilities line, printed 12832000000 = filing XBRL 12832000000; agrees
- capex: mapped us-gaap:PaymentsToAcquireProductiveAssets (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Capital expenditures' is the capex line, printed -5620000000 = filing XBRL 5620000000; agrees
- depreciation_and_amortization: combined epd:DepreciationAndAccretion (R7.htm): 2026-11-12 R7.htm: sample DISAGREES: 'Depreciation and accretion' includes accretion: combined (Dhairya ruling)
- operating_expenses: combined: 'Total operating costs and expenses' 45,440 includes cost of sales (38,566, R55) and no line-by-line face breakdown ties to GP - OI: combined, never opex
- total_debt: corrected per finance-lease ruling (founder 2026-11-04 item 5): R119.htm: finance leases sit in other current (3) and other non-current liabilities (13), outside the debt lines: 34395000000 + 16000000 = 34411000000

## MLP rulings applied 2026-11-13
- stockholders_equity: mapped us-gaap:PartnersCapital (R3.htm): MLP ruling (Dhairya 2026-11-13, binds every MLP) 1: total partners' equity attributable to the partnership 29,739, excluding noncontrolling interests (831)
- dividends_paid: mapped us-gaap:DistributionMadeToLimitedPartnerCashDistributionsPaid (R7.htm): MLP ruling (Dhairya 2026-11-13, binds every MLP) 2: cash distributions paid to common unitholders 4,678; distributions to NCI (93), distribution equivalent rights and preferred units are excluded
- shares_outstanding: mapped us-gaap:LimitedPartnersCapitalAccountUnitsOutstanding (R4.htm): MLP ruling (Dhairya 2026-11-13, binds every MLP) 3: common units outstanding at 2025-12-31 (BS parenthetical R4); never the cover count
- weighted_basic_shares: mapped us-gaap:WeightedAverageLimitedPartnershipUnitsOutstanding (R92.htm): by analogy to MLP ruling (Dhairya 2026-11-13, binds every MLP) 3: weighted-average common units outstanding (basic) 2,166 million in the EPU note R92; flagged to Dhairya as an analogy
