# PLD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-051453 (CIK 0001045609, filed 2026-02-13): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-16-012933 (CIK 0001045609, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000950170-24-014539 (CIK 0001045609, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-18-002228 (CIK 0001045609, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001045609.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total revenues | 8790127000 | 8790127000 | 8201610000 | 8201610000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| operating_expenses | mapped | pld:OperatingExpensesBeforeGainsOnRealEstateTransactionsNet | R4.htm | Total expenses | 5375825000 |  | 5103569000 |  | API missing | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it; company extension tag, matched by printed label / accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 469114000 | 469114000 | 418765000 | 418765000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 4357864000 | 4357864000 | 4415920000 | 4415920000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R4.htm | Interest expense | -1002344000 | 1002344000 | -863932000 | 863932000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Earnings before income taxes | 3769316000 | 3769316000 | 4114878000 | 4114878000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | -204017000 | 204017000 | -166943000 | 166943000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net earnings attributable to controlling interests | 3328231000 | 3328231000 | 3731635000 | 3731635000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net earnings per share/unit attributable to common stockholders/unitholders - Basic | 3.58 | 3.58 | 4.02 | 4.02 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net earnings per share/unit attributable to common stockholders/unitholders - Diluted | 3.56 | 3.56 | 4.01 | 4.01 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average common shares/units outstanding - Basic | 928473000 | 928473000 | 926172000 | 926172000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average common shares/units outstanding - Diluted | 956832000 | 956832000 | 953590000 | 953590000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 1145647000 | 1145647000 | 1318591000 | 1318591000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R66.htm | Other Assets and Other Liabilities - Schedule of Other Assets and Liabilities (Detail) |  | 221704000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R66.htm 'Other Assets and Other Liabilities - Schedule of Other Assets and Liabilities (D' (MetaLinks.json presentation); value from companyfacts same accession |
| goodwill | mapped | us-gaap:Goodwill | R109.htm | Reportable Segments - Reportable Segment Net Operating Income and Assets (Parenthetical) (Detail) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R109.htm 'Reportable Segments - Reportable Segment Net Operating Income and Assets (Parent' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 98724256000 | 98724256000 | 95328909000 | 95328909000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R2.htm | Accounts payable and accrued expenses | 1963645000 | 1963645000 | 1769327000 | 1769327000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-051453 R2.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 40970248000 | 40970248000 | 36712139000 | 36712139000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total Prologis, Inc. stockholders’ equity | 53193178000 | 53193178000 | 53951138000 | 53951138000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by (used in) operating activities | 5008434000 | 5008434000 | 4912209000 | 4912209000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | -3630447000 | -3630447000 | -3099057000 | -3099057000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | -1563619000 | -1563619000 | -999957000 | -999957000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1203 tags across all 113 R pages, face and notes) of 0001193125-26-051453; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 2626028000 | 2626028000 | 2580519000 | 2580519000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Equity-based compensation awards | 185466000 | 185466000 | 231747000 | 231747000 | Y | FILING-CHECKED | accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends/distributions paid on common and preferred stock/units | -3764745000 | 3764745000 | -3570480000 | 3570480000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | pld:RepurchaseOfAndRepaymentsOnDebtExcludingLineOfCredit | R8.htm | Repurchase of and payments on debt | -701861000 |  | -919481000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-051453 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R77.htm | Debt - Interest Expense (Detail) |  | 842257000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R77.htm 'Debt - Interest Expense (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R91.htm | Income Taxes - Additional Information (Detail) |  | 142700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'Income Taxes - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebt+us-gaap:LongTermDebt | R2.htm | Debt + Debt | 70074146000 | 70074146000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 929153000 | 929153000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Total revenues' on us-gaap:RealEstateRevenueNet = 2197074000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 1816902000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-012933 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 238199000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 380172000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -301363000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 948605000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Total income tax expense (benefit)' on us-gaap:IncomeTaxExpenseBenefit = 23090000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Net earnings attributable to controlling interests' on us-gaap:NetIncomeLoss = 869439000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Net earnings per share attributable to common stockholders/unitholders – Basic' on us-gaap:EarningsPerShareBasic = 1.66 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Net earnings per share attributable to common stockholders/unitholders – Diluted' on us-gaap:EarningsPerShareDiluted = 1.64 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Weighted average common shares/units outstanding – Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 521241000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-012933 R4.htm prints 'Weighted average common shares/units outstanding – Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 533944000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-012933 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 264080000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-012933 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001564590-16-012933 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001564590-16-012933 R2.htm prints 'Total assets' on us-gaap:Assets = 31394767000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-012933 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 712725000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-012933 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 12973931000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-012933 R2.htm prints 'Total Prologis, Inc. stockholders’ equity' on us-gaap:StockholdersEquity = 14667935000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 963410000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -4648613000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 3608214000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 880373000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Equity-based compensation awards' on us-gaap:ShareBasedCompensation = 53665000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Distributions paid on common and preferred stock' on us-gaap:PaymentsOfDividends = -804697000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-012933 R7.htm prints 'Repurchase and redemption of preferred stock' on us-gaap:PaymentsForRepurchaseOfPreferredStockAndPreferenceStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-012933 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-012933 R7.htm read; no row matched (auto)
- interest_expense: era 10-K 0000950170-24-014539 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -641332000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-002228 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1687246000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-002228 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 543278000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-002228 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -2606584000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (pld:OperatingExpensesBeforeGainsOnRealEstateTransactionsNet)
- share_buybacks: API missing (pld:RepurchaseOfAndRepaymentsOnDebtExcludingLineOfCredit)

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R4.htm): 2026-11-12 R4.htm: REIT IS (R4) prints rental and development expenses by nature, no cost-of-revenue line; MetaLinks: tags absent
- gross_profit: not_presented  (R4.htm): 2026-11-12 R4.htm: no gross profit line on R4; MetaLinks: GrossProfit absent
- research_and_development: not_presented  (R4.htm): 2026-11-12 R4.htm: no R&D line; MetaLinks: tags absent
- accounts_receivable: not_presented  (R2.htm): 2026-11-12 R2.htm: PLD's BS (R2) prints no receivables line (in other assets); MetaLinks: AR tags absent
- inventory: not_presented  (R2.htm): 2026-11-12 R2.htm: no inventory line on R2; MetaLinks: InventoryNet absent
- current_assets: not_presented  (R2.htm): 2026-11-12 R2.htm: unclassified REIT balance sheet (R2); MetaLinks: AssetsCurrent absent
- ppe_net: component_in_note us-gaap:PropertyPlantAndEquipmentNet (R66.htm): 2026-11-12 R66.htm: R66 'Other assets' schedule prints corporate property and equipment 221.7 million: only a component of PLD's operating property (the real estate is reported as investments in real estate properties), 
- goodwill: review us-gaap:Goodwill (R109.htm): 2026-11-12 R109.htm: R109 segment asset table carries Goodwill only by segment (no undimensioned fact for this accession): the consolidated amount is not printed on the face; needs the other-assets note page read before 
- current_liabilities: not_presented  (R2.htm): 2026-11-12 R2.htm: unclassified REIT balance sheet (R2); MetaLinks: LiabilitiesCurrent absent
- capex: component sum pld:PaymentForPropertyImprovements+us-gaap:PaymentsForLeasingCostsCommissionsAndTenantImprovements+us-gaap:PaymentsToDevelopRealEstateAssets (R8.htm): 2026-11-12 R8.htm: R8 prints property improvements 327,355 + tenant improvements and lease commissions 562,197 + real estate development 2,781,260 = 3,670,812 (REIT capex rule 24, doc 02 line 114; acquisitions excluded);
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R77.htm): 2026-11-12 R77.htm: R77 debt note prints interest paid (net of capitalized) 842.3 million = XBRL: mapped, stmt NOTE (InterestPaidNet, DQC_0065)
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R91.htm): 2026-11-12 R91.htm: R91 income-tax note prints income taxes paid 142.7 million = XBRL: mapped, stmt NOTE
- total_debt: mapped us-gaap:LongTermDebt (R2.htm): 2026-11-12 R2.htm: R2 prints 'Debt' 35,037,073 twice: Prologis, Inc. and the co-registrant Prologis, L.P.; the machine sum 70,074 double counts. Parent column only: 35,037,073
- sbc: mapped us-gaap:ShareBasedCompensation (R8.htm): 2026-11-12 R8.htm: 10% mapped sample: CF R8.htm 'Equity-based compensation awards' is the sbc line, printed 185466000 = filing XBRL 185466000; agrees
- dividends_paid: combined us-gaap:PaymentsOfDividends (R8.htm): 2026-11-12 R8.htm: R8 'Dividends/distributions paid on common and preferred stock/units' mixes common with preferred and OP units: combined (never keyed as common dividends). SAMPLE DISAGREEMENT

## Loader-reject fixes 2026-11-13 (docmap-load dry run on 669f8477)
- cost_of_revenue: unverified -> re-checked on the R page
- gross_profit: unverified -> re-checked on the R page
- research_and_development: unverified -> re-checked on the R page
- accounts_receivable: unverified -> re-checked on the R page
- inventory: unverified -> re-checked on the R page
- current_assets: unverified -> re-checked on the R page
- ppe_net: period/accession added
- current_liabilities: unverified -> re-checked on the R page
- capex: unverified -> re-checked on the R page
- cash_paid_for_interest: period/accession added
- cash_paid_for_income_taxes: period/accession added
- total_debt: unverified -> re-checked on the R page
- shares_outstanding: period/accession added
- goodwill: review -> member row (0125 dims loader)
