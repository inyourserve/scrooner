# HSY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008586 (CIK 0000047111, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000047111-16-000095 (CIK 0000047111, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000047111-18-000011 (CIK 0000047111, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000047111-19-000010 (CIK 0000047111, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000047111.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 11692576000 | 11692576000 | 11202263000 | 11202263000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 7769885000 | 7769885000 | 5901375000 | 5901375000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 3922691000 | 3922691000 | 5300888000 | 5300888000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+hsy:RestructuringChargesBusinessRealignment | R3.htm | Selling, marketing and administrative expense + Business realignment costs | 2481163000 |  | 2402656000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001628280-26-008586 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, marketing and administrative expense | 2460569000 | 2460569000 | 2373621000 | 2373621000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R53.htm | SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES - SELLING, MARKETING AND ADMINISTRATIVE EXPENSE (Details) | 61655000 | 61655000 | 55798000 |  | Y | FILING-CHECKED | not on the face statement; shown in R53.htm 'SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES - SELLING, MARKETING AND ADMINISTRATI' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R53.htm corrected: R53 'Research and development costs' 61,655 / 55,798 (note only, inside SM&A); printed values were blank. |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating profit | 1441528000 | 1441528000 | 2898232000 | 2898232000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest expense, net | 190206000 | -190206000 | 165655000 | -165655000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 1214208000 | 1214208000 | 2473936000 | 2473936000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 330949000 | 330949000 | 252697000 | 252697000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 883259000 | 883259000 | 2221239000 | 2221239000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income per share - basic (USD per share) | 4.46 |  | 11.22 |  | API missing | FILING-CHECKED | accn 0001628280-26-008586 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income per share - diluted (USD per share) | 4.34 |  | 10.92 |  | API missing | FILING-CHECKED | accn 0001628280-26-008586 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R122.htm | EARNINGS PER SHARE - SCHEDULE OF BASIC AND DILUTED EARNINGS PER SHARE (Details) | 148281000 |  | 148349000 |  |  | FILING-CHECKED | R122 two-class EPS note: Common Stock basic weighted shares 148,281 / 148,349 (thousands); Class B 54,614 / 54,614 reported separately / check: hand R122.htm corrected: R122 'Total weighted-average shares-basic' Common Stock 148,281 / 148,349 thousand (Class B 54,614 separate), the denominator of the $4.46 basic EPS; values were blank. |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R122.htm | EARNINGS PER SHARE - SCHEDULE OF BASIC AND DILUTED EARNINGS PER SHARE (Details) | 203379000 |  | 203487000 |  |  | FILING-CHECKED | R122 Common Stock diluted weighted shares 203,379 / 203,487 (thousands), includes assumed conversion of Class B / check: hand R122.htm corrected: R122 'Total weighted-average shares-diluted' Common Stock 203,379 / 203,487 thousand (includes conversion of Class B 54,614); values were blank. |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash and cash equivalents | 925859000 | 925859000 | 730746000 | 730746000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable—trade, net | 729547000 | 729547000 | 800402000 | 800402000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1429254000 | 1429254000 | 1254094000 | 1254094000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 3588899000 | 3588899000 | 3759457000 | 3759457000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, plant and equipment, net | 3529608000 | 3529608000 | 3458853000 | 3458853000 | Y | FILING-CHECKED | accn 0001628280-26-008586 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2996005000 | 2996005000 | 2705753000 | 2705753000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 13741297000 | 13741297000 | 12946861000 | 12946861000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 1255701000 | 1255701000 | 1159177000 | 1159177000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 3011896000 | 3011896000 | 3929495000 | 3929495000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 9104547000 | 9104547000 | 8232207000 | 8232207000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 4636750000 | 4636750000 | 4714654000 | 4714654000 | Y | FILING-CHECKED | accn 0001628280-26-008586 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 2277367000 | 2277367000 | 2531596000 | 2531596000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1278717000 | -1278717000 | -960314000 | -960314000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -803357000 | -803357000 | -1296501000 | -1296501000 | Y | FILING-CHECKED | accn 0001628280-26-008586 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital additions (including software) | -454622000 | 454622000 | -605942000 | 605942000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 503701000 | 503701000 | 455255000 | 455255000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 65460000 | 65460000 | 44414000 | 44414000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Cash dividends paid | -1085296000 | 1085296000 | -1084802000 | 1084802000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | 0 | 0 | -494191000 | 494191000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | 195927000 | 195927000 | 179777000 | 179777000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid | 140616000 | 140616000 | 201799000 | 201799000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008586 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Short-term debt + Current portion of long-term debt + Long-term debt | 5403067000 | 5403067000 | 5102151000 |  | Y | FILING-CHECKED | sum of printed BS debt lines; finance lease liabilities already inside current portion of LTD and LTD (R82 extensible enumeration) / check: hand R5.htm corrected: R5 Short-term debt 218,546 + Current portion of LTD 503,327 + LTD 4,681,194 = 5,403,067; R82 shows finance leases (4,499 / 69,011) sit inside current portion and long-term debt, so not added; FY24 1,306,976 + 604,965 + 3,190,210 = 5,102,151 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R118.htm | EQUITY AND NONCONTROLLING INTEREST - EQUITY AND NONCONTROLLING INTEREST NARRATIVE (Details) | 202839656 | 202839656 | 202383069 |  | Y | FILING-CHECKED | not on face/BS parenthetical (R6 gives issued and treasury only); R118 equity note prints total outstanding 202,839,656 / 202,383,069 = issued - treasury / check: hand R118.htm corrected: R118 CommonStockSharesOutstanding (all classes) 202,839,656 at Dec 31 2025 and 202,383,069 at Dec 31 2024, equal to R6 issued 221,553,025 less treasury 18,713,369 / 19,169,956; values were blank. |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 7386626000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 4003951000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000047111-16-000095 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 6348867000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Selling, marketing and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 1969308000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000047111-16-000095 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Operating profit' on us-gaap:OperatingIncomeLoss = 1037759000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = 105773000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 901847000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 388896000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 512951000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Net income per share - basic (USD per share)' on us-gaap:EarningsPerShareBasic = 2.4 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000047111-16-000095 R2.htm prints 'Net income per share - diluted (USD per share)' on us-gaap:EarningsPerShareDiluted = 2.32 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000047111-16-000095 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000047111-16-000095 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 346529000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Accounts receivable—trade, net' on us-gaap:AccountsReceivableNetCurrent = 599073000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 750970000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1848598000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2240460000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 684252000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Total assets' on us-gaap:Assets = 5344371000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 474266000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2217912000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000047111-16-000095 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 4296909000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000047111-16-000095 R4.htm prints 'The Hershey Company stockholders’ equity' on us-gaap:StockholdersEquity = 997997000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1214456000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -477255000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -755162000 (FILING-CHECKED)
- capex: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Capital additions' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -329707000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 244928000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 51533000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -476132000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -582623000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Interest paid (excluding loss on early extinguishment of debt in 2015)' on us-gaap:InterestPaidNet = 88448000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000047111-16-000095 R6.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 368926000 (FILING-CHECKED)
- revenue: era 10-K 0000047111-18-000011 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 7515426000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000047111-18-000011 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 4070907000 (FILING-CHECKED)
- revenue: era 10-K 0000047111-19-000010 R2.htm prints 'Net sales' on us-gaap:Revenues = 7791069000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000047111-19-000010 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 587998000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000047111-19-000010 R6.htm prints 'Interest paid' on us-gaap:InterestPaidNet =  (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+hsy:RestructuringChargesBusinessRealignment)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: API missing (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 11 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 5.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
