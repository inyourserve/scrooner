# CHD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-048139 (CIK 0000313927, filed 2026-02-12): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001564590-16-012917 (CIK 0000313927, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001564590-18-002984 (CIK 0000313927, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000950170-23-003066 (CIK 0000313927, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000313927.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net Sales | 6203200000 | 6203200000 | 6107100000 | 6107100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R2.htm | Cost of sales | 3428400000 | 3428400000 | 3317000000 | 3317000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross Profit | 2774800000 | 2774800000 | 2790100000 | 2790100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:MarketingAndAdvertisingExpense+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:OtherAssetImpairmentCharges | R2.htm | Marketing expenses + Selling, general and administrative expenses + VMS Trade name and other asset impairments | 1697200000 |  | 1983000000 | 1983000000 | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001193125-26-048139 R2.htm period ..2025-12-31 / check: hand R2.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 988300000 | 988300000 | 927800000 | 927800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R46.htm | Significant Accounting Policies - Additional Information (Details) | 145600000 | 145600000 | 139700000 |  | Y | FILING-CHECKED | note R46 value; label reads 'Sec 174 R&D Capitalization' though tagged ResearchAndDevelopmentExpense / check: hand R46.htm corrected: Policies note R46 prints ResearchAndDevelopmentExpense 145.6M (FY1 139.7M), labelled 'Sec 174 R&D Capitalization'; only R&D amount in the filing shown. |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Income from Operations | 1077600000 | 1077600000 | 807100000 | 807100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R2.htm | Interest expense | -95200000 | 95200000 | -95000000 | 95000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before Income Taxes | 956900000 | 956900000 | 756300000 | 756300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income taxes | 220100000 | 220100000 | 171000000 | 171000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net Income | 736800000 | 736800000 | 585300000 | 585300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Net income per share - Basic | 3.04 | 3.04 | 2.39 | 2.39 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Net income per share - Diluted | 3.02 | 3.02 | 2.37 | 2.37 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Weighted average shares outstanding - Basic | 242700000 | 242700000 | 244400000 | 244400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Weighted average shares outstanding - Diluted | 244300000 | 244300000 | 246900000 | 246900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 409000000 | 409000000 |  | 964100000 | Y | FILING-CHECKED | accn 0001193125-26-048139 R4.htm period ..2025-12-31 / check: hand R4.htm agree |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable, less allowances of $3.7 and $5.1 | 593400000 | 593400000 |  | 600800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories | 534800000 | 534800000 |  | 613300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total Current Assets | 1597000000 | 1597000000 |  | 2240600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property, Plant and Equipment, Net | 822800000 | 822800000 |  | 931700000 | Y | FILING-CHECKED | accn 0001193125-26-048139 R4.htm period ..2025-12-31 / check: hand R4.htm agree |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 2627500000 | 2627500000 |  | 2433200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total Assets | 8912400000 | 8912400000 |  | 8883100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 732400000 | 732400000 |  | 705100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total Current Liabilities | 1497700000 | 1497700000 |  | 1315900000 | Y | FILING-CHECKED | accn 0001193125-26-048139 R4.htm period ..2025-12-31 / check: hand R4.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R4.htm | Total Liabilities | 4910200000 | 4910200000 |  | 4522300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total Stockholders' Equity | 4002200000 | 4002200000 |  | 4360800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net Cash Provided By Operating Activities | 1215400000 | 1215400000 | 1156200000 | 1156200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net Cash Used In Investing Activities | -616900000 | -616900000 | -183300000 | -183300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net Cash Used In Financing Activities | -1162400000 | -1162400000 | -343400000 | -343400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Additions to property, plant and equipment | -122400000 | 122400000 | -179800000 | 179800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AdjustmentForAmortization | R6.htm | Depreciation expense | 247400000 |  | 239100000 |  |  | FILING-CHECKED | Depreciation expense 89.7 + Amortization expense 157.7 (CF R6) / check: hand R6.htm corrected: CF prints Depreciation expense 89.7 and Amortization expense 157.7 as separate lines; component sum must include both = 247.4M (FY1 83.2 + 155.9 = 239.1). |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Non-cash compensation expense | 58000000 | 58000000 | 59200000 | 59200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R6.htm | Payment of cash dividends | -287200000 | 287200000 | -277000000 | 277000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Purchase of treasury stock | -900000000 | 900000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Interest (net of amounts capitalized) | 94600000 | 94600000 | 94400000 | 94400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R6.htm | Income taxes | 188100000 | 188100000 | 259600000 | 259600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-048139 R6.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R4.htm | Long-term Debt | 2205100000 | 2205100000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R4.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | CONSOLIDATED STATEMENTS OF STOCKHOLDERS' EQUITY |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R7.htm 'CONSOLIDATED STATEMENTS OF STOCKHOLDERS' EQUITY' (MetaLinks.json presentation); HAND REVIEW: no period-end value row found on the R page (only roll-forward or dimensioned rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueGoodsNet = 3394800000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 1883000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Gross Profit' on us-gaap:GrossProfit = 1511800000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Marketing expenses + Selling, general and administrative expenses' on us-gaap:MarketingAndAdvertisingExpense+us-gaap:SellingGeneralAndAdministrativeExpense = 837600000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 420100000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001564590-16-012917 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Income from Operations' on us-gaap:OperatingIncomeLoss = 674200000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -30500000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Income before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 635400000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 225000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Net Income' on us-gaap:ProfitLoss = 410400000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Net income per share - Basic' on us-gaap:EarningsPerShareBasic = 3.13 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Net income per share - Diluted' on us-gaap:EarningsPerShareDiluted = 3.07 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Weighted average shares outstanding - Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 131100000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-012917 R2.htm prints 'Weighted average shares outstanding - Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 133600000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 330000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Accounts receivable, less allowances of $1.0 and $1.9' on us-gaap:AccountsReceivableNetCurrent = 276200000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 274000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 906000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Property, Plant and Equipment, Net' on us-gaap:PropertyPlantAndEquipmentNet = 609600000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1354900000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Total Assets' on us-gaap:Assets = 4.257e+09 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 508300000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 872700000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Total Liabilities' on us-gaap:Liabilities = 2233700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-012917 R4.htm prints 'Total Stockholders' Equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 2023200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Net Cash Provided By Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 606100000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Net Cash Used In Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -141200000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Net Cash Used In Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -535000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Additions to property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -61800000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-012917 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Non-cash compensation expense' on us-gaap:ShareBasedCompensation = 1.61e+07 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Payment of cash dividends' on us-gaap:PaymentsOfDividends = -175300000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -363100000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Interest (net of amounts capitalized)' on us-gaap:InterestPaidNet = 29000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-012917 R6.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 174800000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001564590-18-002984 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 2046600000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-002984 R6.htm prints 'Net Cash Provided By Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 681500000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-002984 R6.htm prints 'Net Cash Used In Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1303400000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-002984 R6.htm prints 'Net Cash Provided By (Used In) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 698900000 (FILING-CHECKED)
- accounts_payable: era 10-K 0000950170-23-003066 R4.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 1102800000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:MarketingAndAdvertisingExpense+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:OtherAssetImpairmentCharges)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
