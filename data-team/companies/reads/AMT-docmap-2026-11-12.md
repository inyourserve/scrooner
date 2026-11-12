# AMT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001053507-26-000035 (CIK 0001053507, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R10.htm
- 10-K 0001053507-16-000018 (CIK 0001053507, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001053507-17-000009 (CIK 0001053507, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001053507-24-000011 (CIK 0001053507, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R11.htm
- companyfacts CIK0001053507.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total operating revenues | 10644600000 | 10644600000 | 10127200000 | 10127200000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Services | 174000000 |  | 92600000 |  | API missing | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R140.htm | BUSINESS SEGMENTS - Summarized Segment Financial Information (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R140.htm 'BUSINESS SEGMENTS - Summarized Segment Financial Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 5798800000 | 5798800000 | 5610700000 | 5610700000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general, administrative and development expense | 940700000 | 940700000 | 933400000 | 933400000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1293 tags across all 150 R pages, face and notes) of 0001053507-26-000035; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | OPERATING INCOME | 4845800000 | 4845800000 | 4516500000 | 4516500000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -1359400000 | 1359400000 | -1404500000 | 1404500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | INCOME FROM CONTINUING OPERATIONS BEFORE INCOME TAXES | 3044200000 | 3044200000 | 3624800000 | 3624800000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | -415700000 | 415700000 | -366300000 | 366300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R5.htm | NET INCOME ATTRIBUTABLE TO AMERICAN TOWER CORPORATION COMMON STOCKHOLDERS, BASIC | 2529500000 | 2529500000 | 2255000000 | 2255000000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income attributable to American Tower Corporation common stockholders (in dollars per share) | 5.41 | 5.41 | 4.83 | 4.83 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income attributable to American Tower Corporation common stockholders (in dollars per share) | 5.4 | 5.4 | 4.82 | 4.82 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | BASIC (in shares) | 467922000 | 467922000 | 467011000 | 467011000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | DILUTED (in shares) | 468757000 | 468757000 | 468120000 | 468120000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1474800000 | 1474800000 | 1999600000 | 1999600000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 650300000 | 650300000 | 540000000 | 540000000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1293 tags across all 150 R pages, face and notes) of 0001053507-26-000035; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2741800000 | 2741800000 | 3178800000 | 3178800000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | PROPERTY AND EQUIPMENT, net | 20356300000 | 20356300000 | 19056800000 | 19056800000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | GOODWILL | 12255500000 | 12255500000 | 11768100000 | 11768100000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL | 63190400000 | 63190400000 | 61077400000 | 61077400000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 259800000 | 259800000 | 240800000 | 240800000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 6913800000 | 6913800000 | 7075600000 | 7075600000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 52835100000 | 52835100000 | 51428700000 | 51428700000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total American Tower Corporation equity | 3652500000 | 3652500000 | 3382200000 | 3382200000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Cash provided by operating activities | 5464000000 | 5464000000 | 5290500000 | 5290500000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Cash (used for) provided by investing activities | -1859800000 | -1859800000 | 410600000 | 410600000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Cash used for financing activities | -4208500000 | -4208500000 | -5452400000 | -5452400000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Payments for purchase of property and equipment and construction activities | -1680400000 | 1680400000 | -1590000000 | 1590000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | amt:DepreciationAmortizationAndAccretionIncludingDiscontinuedOperations | R10.htm | Depreciation, amortization and accretion | 2041600000 |  | 2.125e+09 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation expense | 174200000 | 174200000 | 203600000 | 203600000 | Y | FILING-CHECKED | accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R128.htm | EQUITY - Distributions Declared (Details) |  | 3180800000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R128.htm 'EQUITY - Distributions Declared (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Purchases of common stock | -364600000 | 364600000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001053507-26-000035 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R138.htm | SUPPLEMENTAL CASH FLOW INFORMATION (Details) |  | 1287400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R138.htm 'SUPPLEMENTAL CASH FLOW INFORMATION (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R115.htm | INCOME TAXES - Cash Paid for Income Taxes, Net of Refunds (Details) |  | 328700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R115.htm 'INCOME TAXES - Cash Paid for Income Taxes, Net of Refunds (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current portion of long-term obligations + LONG-TERM OBLIGATIONS | 37220300000 | 37220300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 466318000 | 466318000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Total operating revenues' on us-gaap:SalesRevenueNet = 4771516000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Services (including stock-based compensation expense of $439, $440 and $567, res' on us-gaap:CostOfServices = 33432000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001053507-16-000018 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 3158727000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Selling, general, administrative and development expense (including stock-based ' on us-gaap:SellingGeneralAndAdministrativeExpense = 497835000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001053507-16-000018 R4.htm prints 'OPERATING INCOME' on us-gaap:OperatingIncomeLoss = 1612789000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -820000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001053507-16-000018 R4.htm prints 'INCOME FROM CONTINUING OPERATIONS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 829962000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = -157955000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001053507-16-000018 R4.htm prints 'NET INCOME ATTRIBUTABLE TO AMERICAN TOWER CORPORATION STOCKHOLDERS' on us-gaap:NetIncomeLoss = 685074000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Basic net income attributable to American Tower Corporation common stockholders ' on us-gaap:EarningsPerShareBasic = 1.42 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001053507-16-000018 R4.htm prints 'Diluted net income attributable to American Tower Corporation common stockholder' on us-gaap:EarningsPerShareDiluted = 1.41 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001053507-16-000018 R4.htm prints 'BASIC (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 418907000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001053507-16-000018 R4.htm prints 'DILUTED (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 423015000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 320686000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 227354000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 996468000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001053507-16-000018 R2.htm prints 'PROPERTY AND EQUIPMENT, net' on us-gaap:PropertyPlantAndEquipmentNet = 9866424000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001053507-16-000018 R2.htm prints 'GOODWILL' on us-gaap:Goodwill = 4091805000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001053507-16-000018 R2.htm prints 'TOTAL' on us-gaap:Assets = 26904272000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 96714000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1200029000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 20191454000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001053507-16-000018 R2.htm prints 'Total American Tower Corporation equity' on us-gaap:StockholdersEquity = 6651679000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 2183052000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -7741735000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 5589101000 (FILING-CHECKED)
- capex: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Payments for purchase of property and equipment and construction activities' on us-gaap:PaymentsToAcquireProductiveAssets = -728753000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Depreciation, amortization and accretion' on us-gaap:DepreciationAmortizationAndAccretionNet = 1285328000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 90537000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Distributions paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -710852000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001053507-16-000018 R9.htm prints 'Purchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001053507-16-000018 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001053507-16-000018 R9.htm read; no row matched (auto)
- revenue: era 10-K 0001053507-17-000009 R4.htm prints 'Total operating revenues' on us-gaap:SalesRevenueNet = 5785668000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001053507-17-000009 R4.htm prints 'Services (including stock-based compensation expense of $688, $439 and $440, res' on us-gaap:CostOfServices = 27695000 (FILING-CHECKED)
- cfo: era 10-K 0001053507-17-000009 R9.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 2703604000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001053507-17-000009 R9.htm prints 'Cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -2107446000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001053507-17-000009 R9.htm prints 'Cash (used for) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -99294000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001053507-17-000009 R9.htm read; no row matched (auto)
- interest_expense: era 10-K 0001053507-24-000011 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -1398200000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- depreciation_and_amortization: API missing (amt:DepreciationAmortizationAndAccretionIncludingDiscontinuedOperations)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: component_in_note us-gaap:GrossProfit (R140.htm): 2026-11-12 R140.htm: R140 carries gross margin by segment only (no consolidated value); AMT prints no gross profit line
- operating_expenses: component sum us-gaap:DepreciationAmortizationAndAccretionNet+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:OtherOperatingIncomeExpenseNet+us-gaap:GoodwillImpairmentLoss (R5.htm): 2026-11-12 R5.htm: corrected: opex = 2,041.6 + 940.7 + 68.4 = 3,050.7 = 10,644.6 - (2,574.1 + 174.0) - 4,845.8
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: mapped amt:PaymentsOfOrdinaryDividendsCommonStockAndShareBasedPaymentArrangement (R10.htm): 2026-11-12 R10.htm: corrected: the CF face prints 'Distributions paid on common stock' 3,157.2; the tool took distributions DECLARED (3,180.8, R128), which is not cash paid
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R138.htm): 2026-11-12 R138.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R115.htm): 2026-11-12 R115.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R3.htm): 2026-11-12 R3.htm: agree: R3 lines on LongTermDebtAndCapitalLeaseObligations; R94 places finance leases inside long-term obligations (finance-lease ruling (founder 2026-11-04 item 5))
- operating_income: mapped us-gaap:OperatingIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'OPERATING INCOME' is the operating_income line, printed 4845800000 = filing XBRL 4845800000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic net income attributable to American Tower Co' is the basic_eps line, printed 5.41 = filing XBRL 5.41; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'PROPERTY AND EQUIPMENT, net' is the ppe_net line, printed 20356300000 = filing XBRL 20356300000; agrees
- total_assets: mapped us-gaap:Assets (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'TOTAL' is the total_assets line, printed 63190400000 = filing XBRL 63190400000; agrees
- accounts_payable: mapped us-gaap:AccountsPayableCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts payable' is the accounts_payable line, printed 259800000 = filing XBRL 259800000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R10.htm): 2026-11-12 R10.htm: 20% mapped sample: CF R10.htm 'Purchases of common stock' is the share_buybacks line, printed -364600000 = filing XBRL 364600000; agrees
- cost_of_revenue: component sum check: hand 2026-11-12 R5.htm: corrected: 'Costs of operations' prints Property 2,574.1 and Services 174.0; the tool took only Services: 2,748.1
