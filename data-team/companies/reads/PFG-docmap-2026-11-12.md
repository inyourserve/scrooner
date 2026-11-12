# PFG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-017031 (CIK 0001126328, filed 2026-02-18): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001047469-16-010094 (CIK 0001126328, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001104659-20-021174 (CIK 0001126328, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001126328.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total revenues | 15625500000 | 15625500000 | 16127700000 | 16127700000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| operating_expenses | mapped | us-gaap:BenefitsLossesAndExpenses | R4.htm | Total expenses | 14209500000 | 14209500000 | 14238100000 | 14238100000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R175.htm | Segment Information - Reconciliation of Segment Expenses (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R175.htm 'Segment Information - Reconciliation of Segment Expenses (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| income_before_tax | mapped | pfg:IncomeLossFromContinuingOperationsBeforeIncomeTaxes | R4.htm | Income (loss) before income taxes | 1416000000 |  | 1889600000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income taxes (benefits) | 160500000 | 160500000 | 291700000 | 291700000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income (loss) attributable to Principal Financial Group, Inc. | 1185100000 | 1185100000 | 1571000000 | 1571000000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic earnings per common share (in dollars per share) | 5.32 | 5.32 | 6.77 | 6.77 | Y | FILING-CHECKED | accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted earnings per common share (in dollars per share) | 5.25 | 5.25 | 6.68 | 6.68 | Y | FILING-CHECKED | accn 0001104659-26-017031 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R191.htm | Earnings Per Common Share (Details) |  | 222800000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R191.htm 'Earnings Per Common Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R191.htm | Earnings Per Common Share (Details) |  | 225700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R191.htm 'Earnings Per Common Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents (2025 and 2024 include $89.1 million and $86.1 million related to consolidated variable intere | 4431000000 | 4431000000 | 4.212e+09 | 4211900000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R2.htm | Property and equipment | 701400000 | 701400000 | 769400000 | 769400000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1600500000 | 1600500000 | 1549700000 | 1549700000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 341376500000 | 341376500000 | 313663600000 | 313663600000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (2132 tags across all 200 R pages, face and notes) of 0001104659-26-017031; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 328985200000 | 328985200000 | 302194600000 | 302194600000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity attributable to Principal Financial Group, Inc. | 11883900000 | 11883900000 | 11086400000 | 11086400000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used in) operating activities | 4536700000 | 4536700000 | 4602900000 | 4602900000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | -4135800000 | -4135800000 | -5399000000 | -5399000000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -181800000 | -181800000 | 300300000 | 300300000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| capex | mapped | pfg:PaymentsToAcquirePropertyPlantAndEquipmentNet | R7.htm | Net purchases of property and equipment | -98000000 |  | -68800000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation and amortization expense | 251400000 | 251400000 | 256200000 | 256200000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 109900000 | 109900000 | 108700000 | 108700000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends to common stockholders | -684000000 | 684000000 | -658400000 | 658400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Acquisition of treasury stock | -902700000 | 902700000 | -1.042e+09 | 1042400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 172600000 | 172600000 | 170300000 | 170300000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes | 220700000 | 220700000 | 117700000 | 117700000 | Y | FILING-CHECKED | accn 0001104659-26-017031 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R2.htm | Short-term debt (2025 and 2024 include $0.0 million and $119.0 million related to consolidated variable interest entitie | 3954000000 | 3954000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, outstanding (in shares) | 217380912 | 217380912 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Total revenues' on us-gaap:Revenues = 11964400000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Total expenses' on us-gaap:BenefitsLossesAndExpenses = 10533600000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-16-010094 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Income (loss) before income taxes' on pfg:IncomeLossFromContinuingOperationsBeforeIncomeTaxes = 1430800000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Income taxes (benefits)' on us-gaap:IncomeTaxExpenseBenefit = 177600000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Net income (loss) attributable to Principal Financial Group, Inc.' on us-gaap:NetIncomeLoss = 1234000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Basic earnings per common share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 4.11 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-010094 R4.htm prints 'Diluted earnings per common share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 4.06 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-010094 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-010094 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001047469-16-010094 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2564800000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-16-010094 R2.htm prints 'Property and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 633800000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-16-010094 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1009000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-010094 R2.htm prints 'Total assets' on us-gaap:Assets = 218685900000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047469-16-010094 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 209222800000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-010094 R2.htm prints 'Total stockholders' equity attributable to Principal Financial Group, Inc.' on us-gaap:StockholdersEquity = 9311600000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 4377100000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -3167600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -508600000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-16-010094 R8.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Depreciation and amortization expense' on us-gaap:DepreciationAmortizationAndAccretionNet = 193000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 84500000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Dividends to common stockholders' on us-gaap:PaymentsOfDividendsCommonStock = -441000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Acquisition of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -300600000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 149600000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-16-010094 R8.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 129600000 (FILING-CHECKED)
- ppe_net: era 10-K 0001104659-20-021174 R2.htm prints 'Property and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 967700000 (FILING-CHECKED)

## Mismatches (printed vs API)
- income_before_tax: API missing (pfg:IncomeLossFromContinuingOperationsBeforeIncomeTaxes)
- capex: API missing (pfg:PaymentsToAcquirePropertyPlantAndEquipmentNet)
