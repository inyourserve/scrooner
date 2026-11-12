# BRO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-046984 (CIK 0000079282, filed 2026-02-12): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000079282-16-000034 (CIK 0000079282, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- 10-K 0000950170-24-018890 (CIK 0000079282, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000079282-19-000006 (CIK 0000079282, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- companyfacts CIK0000079282.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R2.htm | Total revenues | 5902000000 | 5902000000 | 4805000000 | 4805000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| operating_expenses | mapped | bro:OperatingExpensesAndNonoperatingExpenses | R2.htm | Total expenses | 4531000000 |  | 3502000000 |  | API missing | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it; company extension tag, matched by printed label / accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| operating_income | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R2.htm | Interest | 297000000 | 297000000 | 193000000 | 193000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income taxes | 1371000000 | 1371000000 | 1303000000 | 1303000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income taxes | 304000000 | 304000000 | 301000000 | 301000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income attributable to the Company | 1054000000 | 1054000000 | 993000000 | 993000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic | 3.37 | 3.37 | 3.48 | 3.48 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted | 3.16 | 3.16 | 3.46 | 3.46 | Y | FILING-CHECKED | accn 0001193125-26-046984 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R46.htm | Summary of Significant Accounting Policies - Reconciliation between Basic and Diluted Weighted Average Shares Outstandin |  | 310000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R46.htm 'Summary of Significant Accounting Policies - Reconciliation between Basic and Di' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R46.htm | Summary of Significant Accounting Policies - Reconciliation between Basic and Diluted Weighted Average Shares Outstandin |  | 313000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R46.htm 'Summary of Significant Accounting Policies - Reconciliation between Basic and Di' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 1079000000 | 1079000000 | 675000000 | 675000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| inventory | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 8614000000 | 8614000000 | 6924000000 | 6924000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Fixed assets, net | 367000000 | 367000000 | 319000000 | 319000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 15087000000 | 15087000000 | 7970000000 | 7970000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 29991000000 | 29991000000 | 17612000000 | 17612000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 990000000 | 990000000 | 373000000 | 373000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 8294000000 | 8294000000 | 6314000000 | 6314000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R4.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R90.htm | Insurance Company Subsidiary Operations - Additional Information (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Insurance Company Subsidiary Operations - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| stockholders_equity | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of StockholdersEquity in MetaLinks.json (1045 tags across all 91 R pages, face and notes) of 0001193125-26-046984; no face row matched |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1450000000 | 1450000000 | 1174000000 | 1174000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -7914000000 | -7914000000 | -898000000 | -898000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 7713000000 | 7713000000 | -64000000 | -64000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Additions to fixed assets | -68000000 | 68000000 | -82000000 | 82000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R8.htm | Depreciation | 55000000 | 55000000 | 44000000 | 44000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Non-cash stock-based compensation | 93000000 | 93000000 | 101000000 | 101000000 | Y | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Cash dividends paid | -193000000 | 193000000 | -154000000 | 154000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchase of treasury stock | -100000000 | 100000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-046984 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R78.htm | Supplemental Disclosures of Cash Flow Information and Non-Cash Financing and Investing Activities - Summary of Cash Paid |  | 284000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R78.htm 'Supplemental Disclosures of Cash Flow Information and Non-Cash Financing and Inv' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R78.htm | Supplemental Disclosures of Cash Flow Information and Non-Cash Financing and Investing Activities - Summary of Cash Paid |  | 371000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R78.htm 'Supplemental Disclosures of Cash Flow Information and Non-Cash Financing and Inv' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R4.htm | Current portion of long-term debt + Long-term debt less unamortized discount and debt issuance costs | 7613000000 | 7613000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Common stock, shares outstanding (in shares) | 336000000 | 336000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Total revenues' on us-gaap:Revenues = 1660509000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 1257950000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Interest' on us-gaap:InterestExpense = 39248000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 402559000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 159241000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 243318000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.72 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000079282-16-000034 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.7 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000079282-16-000034 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000079282-16-000034 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 443420000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1537389000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 81753000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Goodwill' on us-gaap:Goodwill = 2586683000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Total assets' on us-gaap:Assets = 5012739000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 63910000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000079282-16-000034 R3.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1328547000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000079282-16-000034 R3.htm read; no row matched (auto)
- cfo: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 411848000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -144637000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -293839000 (FILING-CHECKED)
- capex: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Additions to fixed assets' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -18375000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000079282-16-000034 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Share-based Compensation' on us-gaap:ShareBasedCompensation = 15513000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividends = -64108000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000079282-16-000034 R5.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -163750000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000079282-16-000034 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000079282-16-000034 R5.htm read; no row matched (auto)
- interest_expense: era 10-K 0000950170-24-018890 R2.htm prints 'Interest' on us-gaap:InterestExpense = 190000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000079282-19-000006 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 462462000 (FILING-CHECKED)
- cfo: era 10-K 0000079282-19-000006 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 567529000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000079282-19-000006 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -951771000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000079282-19-000006 R5.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 337750000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000079282-19-000006 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
- operating_expenses: API missing (bro:OperatingExpensesAndNonoperatingExpenses)
