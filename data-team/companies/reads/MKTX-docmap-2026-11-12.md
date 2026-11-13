# MKTX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-067009 (CIK 0001278021, filed 2026-02-24): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001564590-16-013407 (CIK 0001278021, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-18-002713 (CIK 0001278021, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000950170-24-018935 (CIK 0001278021, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0001278021.json (one call); submissions CIK0001278021.json (SIC 6211).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Revenues | 846268000 | 846268000 | 817097000 | 817097000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| cost_of_revenue | component_in_note | mktx:TransactionCosts | R4.htm | Clearing costs | 16583000 |  |  |  |  | FILING-CHECKED | check: hand / Expenses are presented by nature with no cost-of-revenue total; only clearing costs (16,583k) are a direct transaction cost; R103 is parent-only. / pages opened: R4, R103, R28, R45, R74, R98 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Income statement goes from revenues to expenses by nature to operating income; no gross profit in face or segment notes. / pages opened: R4, R28, R45, R98, R99 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Total expenses | 504430000 | 504430000 | 476227000 | 476227000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line; no cost-of-revenue line above it / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:MarketingAndAdvertisingExpense | R4.htm | General and administrative + Marketing and advertising | 37792000 | 37792000 | 34422000 | 34422000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No R&D expense line; R74 shows capitalized software as an asset only. / pages opened: R4, R78, R74, R85, R94 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 341838000 | 341838000 | 340870000 | 340870000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R4.htm | Interest expense | -1487000 | 1487000 | -1601000 | 1601000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes and equity in undistributed earnings of subsidiaries | 366995000 | 366995000 | 360546000 | 360546000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Provision for income taxes | 120083000 | 120083000 | 86365000 | 86365000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 246627000 | 246627000 | 274181000 | 274181000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 6.66 | 6.66 | 7.29 | 7.29 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 6.64 | 6.64 | 7.28 | 7.28 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 37056000 | 37056000 | 37600000 | 37600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 37137000 | 37137000 | 37672000 | 37672000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 519734000 | 519734000 | 544478000 | 544478000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R2.htm | Accounts receivable, net of allowance | 100989000 |  |  |  |  | FILING-CHECKED | check: hand / Unclassified balance sheet reports trade accounts receivable net 100,989k (tagged without the Current suffix); broker-dealer receivables 489,211k are a separate line. / pages opened: R2, R3, R9, R17, R49, R54 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Electronic trading platform; no inventory on the balance sheet or in the cash flow. / pages opened: R2, R4, R9 |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet (statement of financial condition) is unclassified with no current-assets subtotal; listed pages show only credit-facility capacity. / pages opened: R2, R92, R105 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Furniture, equipment, leasehold improvements and capitalized software, net of accumulated depreciation and amortization | 112431000 | 112431000 | 107298000 | 107298000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 283667000 | 283667000 | 236706000 | 236706000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 1934886000 | 1934886000 | 1789216000 | 1789216000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R2.htm | Accounts payable, accrued expenses and other liabilities | 42584000 | 42584000 | 37320000 | 37320000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet is unclassified with no current-liabilities subtotal; R68 is an acquisition allocation (excluded) and R92 credit-facility terms. / pages opened: R2, R68, R92 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 776627000 | 776627000 | 400556000 | 400556000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 1145667000 | 1145667000 | 1388660000 | 1388660000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 382139000 | 382139000 | 385237000 | 385237000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) investing activities | -96927000 | -96927000 | -86935000 | -86935000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash (used in) financing activities | -332369000 | -332369000 | -201377000 | -201377000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of furniture, equipment and leasehold improvements | -8204000 | 8204000 | -9942000 | 9942000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R9.htm | Depreciation and amortization | 76699000 | 76699000 | 73824000 | 73824000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 30918000 | 30918000 | 29684000 | 29684000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfOrdinaryDividends | R9.htm | Cash dividends on common stock | -115199000 | 115199000 | -112697000 | 112697000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -420015000 | 420015000 | -75474000 | 75474000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 721000 | 721000 | 1717000 | 1717000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash paid for income taxes | 62834000 | 62834000 | 96932000 | 96932000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-067009 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings | R2.htm | Borrowings | 220000000 | 220000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 35776886 |  |  |  |  | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Total revenues' on us-gaap:Revenues = 303098000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 155198000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013407 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 13008000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013407 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001564590-16-013407 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Income before income taxes from continuing operations' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 147900000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 51863000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 96037000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Net income per common share' on us-gaap:EarningsPerShareBasic = 2.62 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Net income per common share' on us-gaap:EarningsPerShareDiluted = 2.55 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 36690000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013407 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 37637000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 199728000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Furniture, equipment, leasehold improvements and capitalized software, net of ac' on us-gaap:PropertyPlantAndEquipmentNet = 30897000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Goodwill and intangible assets, net of accumulated amortization' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 64142000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Total assets' on us-gaap:Assets = 439041000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Accounts payable, accrued expenses and other liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 12257000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 48328000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013407 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 390713000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 120196000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Net cash (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -37953000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Net cash (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -51054000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Purchases of furniture, equipment and leasehold improvements' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -4795000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 18542000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 12519000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Cash dividend on common stock' on us-gaap:PaymentsOfOrdinaryDividends = -29534000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -23158000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013407 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013407 R8.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 50875000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-002713 R4.htm prints 'Total revenues' on us-gaap:Revenues = 397471000 (FILING-CHECKED)
- interest_expense: era 10-K 0000950170-24-018935 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -1983000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
