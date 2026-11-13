# KHC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001637459-26-000009 (CIK 0001637459, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001637459-16-000100 (CIK 0001637459, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001637459-18-000015 (CIK 0001637459, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001637459-20-000027 (CIK 0001637459, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0001637459.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Net sales | 24942000000 | 24942000000 | 25846000000 | 25846000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of products sold | 16633000000 | 16633000000 | 16878000000 | 16878000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 8309000000 | 8309000000 | 8968000000 | 8968000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses (incl. impairment losses) | 12978000000 |  | 7285000000 |  |  | FILING-CHECKED | sole face line between GP and OI; ties to GP - OI; includes goodwill and intangible impairments / check: hand R3.htm corrected: The only face line between Gross profit 8,309 and Operating income/(loss) (4,669) is 'Selling, general and administrative expenses' 12,978 (SG&A ex-impairment 3,672 + goodwill impairment 6,734 + intangible impairment 2,572) = GP - OI; FY1 7,285 = 8,968 - 1,683. |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 12978000000 | 12978000000 | 7285000000 | 7285000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R55.htm | Significant Accounting Policies - Additional Information (Details) | 167000000 | 167000000 | 150000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R55.htm 'Significant Accounting Policies - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R55.htm corrected: Not on R3; policies note R55 prints 'Research and development expense' 167 / 150; printed values were blank. |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income/(loss) | -4669000000 | -4669000000 | 1683000000 | 1683000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | 947000000 | 947000000 | 912000000 | 912000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income/(loss) before income taxes | -5445000000 | -5445000000 | 856000000 | 856000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for/(benefit from) income taxes | 403000000 | 403000000 | -1890000000 | -1890000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income/(loss) attributable to common shareholders | -5846000000 | -5846000000 | 2744000000 | 2744000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings/(loss) per share (in dollars per share) | -4.93 | -4.93 | 2.27 | 2.27 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings/(loss) per share (in dollars per share) | -4.93 | -4.93 | 2.26 | 2.26 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R3.htm period ..2025-12-27 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R133.htm | Earnings Per Share - Schedule of Earnings Per Common Share, Basic and Diluted (Details) | 1187000000 | 1187000000 | 1210000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R133.htm 'Earnings Per Share - Schedule of Earnings Per Common Share, Basic and Diluted (D' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R133.htm corrected: R3 has no share lines; EPS note R133 'Weighted average shares of common stock outstanding' 1,187 / 1,210 million. |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R133.htm | Earnings Per Share - Schedule of Earnings Per Common Share, Basic and Diluted (Details) | 1187000000 | 1187000000 | 1215000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R133.htm 'Earnings Per Share - Schedule of Earnings Per Common Share, Basic and Diluted (D' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R133.htm corrected: EPS note R133 '...including dilutive effect' 1,187 / 1,215 million. |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 2615000000 | 2615000000 | 1334000000 | 1334000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade receivables (net of allowances of $34 at December 27, 2025 and $26 at December 28, 2024) | 2254000000 | 2254000000 | 2147000000 | 2147000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 3167000000 | 3167000000 | 3376000000 | 3376000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 10127000000 | 10127000000 | 7655000000 | 7655000000 | Y | FILING-CHECKED | accn 0001637459-26-000009 R5.htm period ..2025-12-27 / check: hand R5.htm agree |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, plant and equipment, net | 7318000000 | 7318000000 | 7152000000 | 7152000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 22179000000 | 22179000000 | 28673000000 | 28673000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 81786000000 | 81786000000 | 88287000000 | 88287000000 | Y | FILING-CHECKED | accn 0001637459-26-000009 R5.htm period ..2025-12-27 / check: hand R5.htm agree |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R5.htm | Accounts payable | 4308000000 | 4308000000 | 4188000000 | 4188000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 8778000000 | 8778000000 | 7253000000 | 7253000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | TOTAL LIABILITIES | 39997000000 | 39997000000 | 38962000000 | 38962000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders' equity | 41664000000 | 41664000000 | 49185000000 | 49185000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R5.htm period ..2025-12-27 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by/(used for) operating activities | 4462000000 | 4462000000 | 4184000000 | 4184000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by/(used for) investing activities | -1833000000 | -1833000000 | -1023000000 | -1023000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by/(used for) financing activities | -1251000000 | -1251000000 | -3008000000 | -3008000000 | Y | FILING-CHECKED | accn 0001637459-26-000009 R9.htm period ..2025-12-27 / check: hand R9.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -801000000 | 801000000 | -1024000000 | 1024000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 968000000 | 968000000 | 948000000 | 948000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Equity award compensation expense | 95000000 | 95000000 | 109000000 | 109000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid | -1898000000 | 1898000000 | -1931000000 | 1931000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | 436000000 | 436000000 | 988000000 | 988000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 903000000 | 903000000 | 906000000 | 906000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637459-26-000009 R9.htm period ..2025-12-27 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R76.htm | Income Taxes - Additional Information (Details) | 721000000 | 721000000 | 967000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R76.htm 'Income Taxes - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R76.htm corrected: Tax note R76 'Income Taxes Paid, Net' 721,000,000 / 967,000,000; printed values were blank. |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt + Long-term debt | 21219000000 | 21219000000 | 19869000000 |  | Y | FILING-CHECKED | BS debt lines tagged LongTermDebtAndCapitalLeaseObligations(Current) already include finance leases (R127 30 + 130); not added again / check: hand R5.htm corrected: R5 'Current portion of long-term debt' 1,908 + 'Long-term debt' 19,311 = 21,219 (FY1 654 + 19,215 = 19,869); both tagged LongTermDebtAndCapitalLeaseObligations so finance leases (R127: 30 + 130) are inside by tag, not added. FY1 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (in shares) | 1184000000 | 1184000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-27; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 18338000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 12577000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 5761000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 3122000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001637459-16-000100 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Operating income/(loss)' on us-gaap:OperatingIncomeLoss = 2639000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 1321000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Income/(loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1013000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Provision for/(benefit from) income taxes' on us-gaap:IncomeTaxExpenseBenefit = 366000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Net income/(loss) attributable to Kraft Heinz' on us-gaap:NetIncomeLoss = 634000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Basic (loss)/income per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = -0.34 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001637459-16-000100 R2.htm prints 'Diluted (loss)/income per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = -0.34 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001637459-16-000100 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001637459-16-000100 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 4837000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Trade receivables (net of allowances of $32 at January 3, 2016 and $8 at Decembe' on us-gaap:AccountsReceivableNetCurrent = 871000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 2618000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 9780000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 6524000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 43051000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001637459-16-000100 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 122973000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Trade payables' on us-gaap:AccountsPayableTradeCurrent = 2844000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 6932000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001637459-16-000100 R4.htm prints 'TOTAL LIABILITIES' on us-gaap:Liabilities = 56737000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001637459-16-000100 R4.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 57685000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Net cash provided by/(used for) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2467000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -9704000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Net cash provided by/(used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 10183000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -648000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 740000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Equity award compensation expense' on us-gaap:ShareBasedCompensation = 133000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Dividends paid-common stock' on us-gaap:PaymentsOfDividendsCommonStock = -1302000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001637459-16-000100 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Interest Paid' on us-gaap:InterestPaid = 704000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001637459-16-000100 R7.htm prints 'Income Taxes Paid' on us-gaap:IncomeTaxesPaid = 577000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001637459-18-000015 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 16529000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001637459-18-000015 R7.htm prints 'Interest' on us-gaap:InterestPaid = 1269000000 (FILING-CHECKED)
- ppe_net: era 10-K 0001637459-20-000027 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 7055000000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001637459-20-000027 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -1953000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001637459-20-000027 R7.htm prints 'Income taxes paid during the period' on us-gaap:IncomeTaxesPaid = 974000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 9 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 6.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
