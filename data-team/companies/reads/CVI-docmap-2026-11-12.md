# CVI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001376139-26-000014 (CIK 0001376139, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- companyfacts CIK0001376139.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Net sales | 7162000000 | 7162000000 | 7610000000 | 7610000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of sales | 6816000000 | 6816000000 | 7405000000 | 7405000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses (exclusive of depreciation and amortization) | 148000000 | 148000000 | 139000000 | 139000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 182000000 | 182000000 | 58000000 | 58000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense, net | -108000000 | -108000000 | -77000000 | -77000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 80000000 | 80000000 | 19000000 | 19000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax (benefit) expense | -10000000 | -10000000 | -26000000 | -26000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to CVR Energy stockholders | 27000000 | 27000000 | 7000000 | 7000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share (in dollars per share) | 0.27 | 0.27 | 0.06 | 0.06 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share (in dollars per share) | 0.27 | 0.27 | 0.06 | 0.06 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 100500000 | 100500000 | 100500000 | 100500000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 100500000 | 100500000 | 100500000 | 100500000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents (including $69 and $91, respectively, of consolidated variable interest entity (“VIE”)) | 511000000 | 511000000 | 987000000 | 987000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net (including $59 and $65, respectively, of VIE) | 235000000 | 235000000 | 295000000 | 295000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories (including $83 and $76, respectively, of VIE) | 472000000 | 472000000 | 502000000 | 502000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1267000000 | 1267000000 | 1824000000 | 1824000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant, and equipment, net (including $712 and $736, respectively, of VIE) | 2050000000 | 2050000000 | 2176000000 | 2176000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3706000000 | 3706000000 | 4263000000 | 4263000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable (including $48 and $37, respectively, of VIE) | 415000000 | 415000000 | 538000000 | 538000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 706000000 | 706000000 | 1098000000 | 1098000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total CVR stockholders’ equity | 730000000 | 730000000 | 703000000 | 703000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 144000000 | 144000000 | 404000000 | 404000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -362000000 | -362000000 | -121000000 | -121000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -258000000 | -258000000 | -482000000 | -482000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Capital expenditures | -185000000 | 185000000 | -179000000 | 179000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 403000000 | 403000000 | 298000000 | 298000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 42000000 | 42000000 | 15000000 | 15000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends to CVR Energy’s stockholders | 0 | 0 | -151000000 | 151000000 | Y | FILING-CHECKED | accn 0001376139-26-000014 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Long-term debt and finance lease obligations, net of current portion (including $569 and $568, respectively, of VIE) | 1751000000 | 1751000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era checks (tag changes in the last ~5 years)
none found in companyfacts

## Mismatches (printed vs API)
none beyond sign differences
