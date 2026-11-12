# MKL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001096343-26-000020 (CIK 0001096343, filed 2026-02-26): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001096343-16-000185 (CIK 0001096343, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001096343.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total Operating Revenues | 15513233000 | 15513233000 |  | 14813544000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total Operating Expenses | 13394462000 | 13394462000 |  | 12908201000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating Income | 3194852000 | 3194852000 |  | 3712562000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | -205910000 | 205910000 |  | 204300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income Before Income Taxes | 2732708000 | 2732708000 |  | 3637700000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | -580303000 | 580303000 |  | 790294000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net Income to Shareholders | 2107010000 | 2107010000 |  | 2747022000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (dollars per share) | 169.7 | 169.7 |  | 199.7 | Y | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (dollars per share) | 169.2 | 169.2 |  | 199.3 | Y | FILING-CHECKED | accn 0001096343-26-000020 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R112.htm | Shareholders' Equity (Schedule Of Net Income Per Common Share) (Details) |  | 12609000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R112.htm 'Shareholders' Equity (Schedule Of Net Income Per Common Share) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R112.htm | Shareholders' Equity (Schedule Of Net Income Per Common Share) (Details) |  | 12648000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R112.htm 'Shareholders' Equity (Schedule Of Net Income Per Common Share) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 3964705000 | 3964705000 | 3692667000 | 3692667000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:PremiumsAndOtherReceivablesNet | R2.htm | Receivables | 3964598000 | 3964598000 | 3626799000 | 3626799000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001096343-26-000020 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R52.htm | Summary Of Significant Accounting Policies (Narrative) (Details) |  | 703400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R52.htm 'Summary Of Significant Accounting Policies (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R52.htm | Summary Of Significant Accounting Policies (Narrative) (Details) |  | 1500000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R52.htm 'Summary Of Significant Accounting Policies (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 2822091000 | 2822091000 | 2735867000 | 2735867000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total Assets | 68905050000 | 68905050000 | 61897982000 | 61897982000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total Liabilities | 49802861000 | 49802861000 | 44429009000 | 44429009000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total Shareholders' Equity | 18597756000 | 18597756000 | 16915898000 | 16915898000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net Cash Provided By Operating Activities | 2761256000 | 2761256000 | 2594006000 | 2594006000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net Cash Used By Investing Activities | -1189915000 | -1189915000 | -2398618000 | -2398618000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net Cash Used By Financing Activities | -1210056000 | -1210056000 | -297878000 | -297878000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Additions to property and equipment | -206894000 | 206894000 | -254991000 | 254991000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R6.htm | Depreciation and amortization expense | 347918000 | 347918000 | 342359000 | 342359000 | Y | FILING-CHECKED | accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| sbc | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ShareBasedCompensation, AllocatedShareBasedCompensationExpense in MetaLinks.json (1029 tags across all 123 R pages, face and notes) of 0001096343-26-000020; no face row matched |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsPreferredStockAndPreferenceStock | R6.htm | Dividends paid on preferred stock | -18000000 | 18000000 | -36000000 | 36000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchases of common stock | -429519000 | 429519000 | -572728000 | 572728000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001096343-26-000020 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R96.htm | Senior Long-Term Debt And Other Debt (Narrative) (Details) |  | 204000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R96.htm 'Senior Long-Term Debt And Other Debt (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R99.htm | Income Taxes (Narrative) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R99.htm 'Income Taxes (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| total_debt | component sum | us-gaap:LongTermDebt | R2.htm | Senior long-term debt and other debt (estimated fair value of $3,856,000 in 2025 and $3,791,000 in 2024) | 4303811000 | 4303811000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R111.htm | Shareholders' Equity (Schedule of Common Stock Outstanding Roll Forward) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Shareholders' Equity (Schedule of Common Stock Outstanding Roll Forward) (Detail' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Total Operating Revenues' on us-gaap:Revenues = 5369983000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Total Operating Expenses' on us-gaap:CostsAndExpenses = 4509577000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 860406000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 118301000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 742105000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 152963000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Net Income to Shareholders' on us-gaap:NetIncomeLoss = 582772000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Basic (dollars per share)' on us-gaap:EarningsPerShareBasic = 41.99 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001096343-16-000185 R4.htm prints 'Diluted (dollars per share)' on us-gaap:EarningsPerShareDiluted = 41.74 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001096343-16-000185 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001096343-16-000185 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001096343-16-000185 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2630009000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001096343-16-000185 R2.htm prints 'Receivables' on us-gaap:PremiumsAndOtherReceivablesNet = 1113703000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001096343-16-000185 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001096343-16-000185 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001096343-16-000185 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1167844000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001096343-16-000185 R2.htm prints 'Total Assets' on us-gaap:Assets = 24941271000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001096343-16-000185 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 17037704000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001096343-16-000185 R2.htm prints 'Total Shareholders' Equity' on us-gaap:StockholdersEquity = 7834150000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001096343-16-000185 R6.htm prints 'Net Cash Provided By Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 651151000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001096343-16-000185 R6.htm prints 'Net Cash Provided (Used) By Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 125773000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001096343-16-000185 R6.htm prints 'Net Cash Provided (Used) By Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -74211000 (FILING-CHECKED)
- capex: FY2015 10-K 0001096343-16-000185 R6.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -79755000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001096343-16-000185 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 200987000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001096343-16-000185 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001096343-16-000185 R6.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -31491000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001096343-16-000185 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001096343-16-000185 R6.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences
