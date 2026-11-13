# FLEX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000866374-26-000012 (CIK 0000866374, filed 2026-05-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001047469-15-004931 (CIK 0000866374, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000866374-18-000007 (CIK 0000866374, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000866374-21-000030 (CIK 0000866374, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000866374.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 27914000000 | 27914000000 | 25813000000 | 25813000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 25288000000 | 25288000000 | 23584000000 | 23584000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2567000000 | 2567000000 | 2159000000 | 2159000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions+us-gaap:AmortizationOfIntangibleAssets | R5.htm | Selling, general and administrative expenses + Restructuring and impairment charges + Intangible amortization | 1199000000 | 1199000000 | 990000000 | 990000000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000866374-26-000012 R5.htm period ..2026-03-31 / check: hand R5.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 1052000000 | 1052000000 | 904000000 | 904000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1027 tags across all 119 R pages, face and notes) of 0000866374-26-000012; no face row matched / check: hand R5.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1368000000 | 1368000000 | 1169000000 | 1169000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | 215000000 | 215000000 | 218000000 | 218000000 | Y | FILING-CHECKED | accn 0000866374-26-000012 R5.htm period ..2026-03-31 / check: hand R5.htm agree |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income from continuing operations before income taxes | 1143000000 | 1143000000 | 1023000000 | 1023000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | 263000000 | 263000000 | 185000000 | 185000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Flex Ltd. | 880000000 | 880000000 | 838000000 | 838000000 | Y | FILING-CHECKED | accn 0000866374-26-000012 R5.htm period ..2026-03-31 / check: hand R5.htm agree |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share attributable to the shareholders of Flex Ltd (in dollars per share) | 2.37 | 2.37 | 2.14 | 2.14 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share attributable to the shareholders of Flex Ltd (in dollars per share) | 2.33 | 2.33 | 2.11 | 2.11 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 371000000 | 371000000 | 391000000 | 391000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 378000000 | 378000000 | 398000000 | 398000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R5.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2389000000 | 2389000000 | 2289000000 | 2289000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for doubtful accounts | 4679000000 | 4679000000 | 3671000000 | 3671000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 5845000000 | 5845000000 | 5071000000 | 5071000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 16332000000 | 16332000000 | 12841000000 | 12841000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 2505000000 | 2505000000 | 2330000000 | 2330000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1369000000 | 1369000000 | 1341000000 | 1341000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 22060000000 | 22060000000 | 18381000000 | 18381000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 8055000000 | 8055000000 | 5147000000 | 5147000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 12016000000 | 12016000000 | 9850000000 | 9850000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 16916000000 | 16916000000 | 13379000000 | 13379000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R3.htm period ..2026-03-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders' equity | 5144000000 | 5144000000 | 5002000000 | 5002000000 | Y | FILING-CHECKED | accn 0000866374-26-000012 R3.htm period ..2026-03-31 / check: hand R3.htm agree |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1685000000 | 1685000000 | 1505000000 | 1505000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R8.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -672000000 | -672000000 | -838000000 | -838000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R8.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) provided by financing activities | -924000000 | -924000000 | -821000000 | -821000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R8.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -633000000 | 633000000 | -438000000 | 438000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R8.htm period ..2026-03-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R8.htm | Depreciation (CF) + Intangible amortization (IS) | 525000000 |  | 509000000 |  |  | FILING-CHECKED | component sum: Depreciation 457 / 439 (R8) + Intangible amortization 68 / 70 (R5); CF 'Amortization and other impairment charges' 106 not used because it includes impairments / check: hand R8.htm corrected: Machine kept only CF 'Depreciation' 457; the CF amortization line 'Amortization and other impairment charges' 106 includes impairments, but the IS prints pure 'Intangible amortization' 68 / 70, so D&A = 457 + 68 = 525 (FY25 439 + 70 = 509). |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 142000000 | 142000000 | 125000000 | 125000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R8.htm period ..2026-03-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1027 tags across all 119 R pages, face and notes) of 0000866374-26-000012; no face row matched / check: hand R8.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Payments for repurchases of ordinary shares | -944000000 | 944000000 | -1257000000 | 1257000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000866374-26-000012 R8.htm period ..2026-03-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R83.htm | SUPPLEMENTAL CASH FLOW DISCLOSURES (Details) | 212000000 | 212000000 | 214000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R83.htm 'SUPPLEMENTAL CASH FLOW DISCLOSURES (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R83.htm corrected: R83 'Interest' paid 212 / 214; values were blank. |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R83.htm | SUPPLEMENTAL CASH FLOW DISCLOSURES (Details) | 323000000 | 323000000 | 184000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R83.htm 'SUPPLEMENTAL CASH FLOW DISCLOSURES (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R83.htm corrected: R83 'Income taxes' paid 323 / 184; values were blank. |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Bank borrowings and current portion of long-term debt + Long-term debt, net of current portion | 3751000000 | 3751000000 | 3692000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm corrected: R3 'Bank borrowings and current portion of LTD' 0 + 'Long-term debt, net of current portion' 3,751 = 3,751; no finance-lease tags; FY25 1,209 + 2,483 = 3,692 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Ordinary shares, outstanding (in shares) | 365690291 | 365690291 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-03-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 26147916 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 24602576 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 1545340 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001047469-15-004931 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 844473 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047469-15-004931 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001047469-15-004931 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Income (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 670655 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 69854 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Net income' on us-gaap:ProfitLoss = 600801 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.04 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.02 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 579981 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-15-004931 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 591556 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1628408 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts' on us-gaap:AccountsReceivableNetCurrent = 2337515 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 3488752 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 8740900 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2092167 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Goodwill and other intangible assets, net' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 415175 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Total assets' on us-gaap:Assets = 11665624 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 4561194 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 6756223 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047469-15-004931 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001047469-15-004931 R2.htm prints 'Total Flextronics International Ltd. shareholders' equity' on us-gaap:StockholdersEquity = 2360814 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 794034 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -242216 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -516017 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -347413 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Depreciation, amortization and other impairment charges' on us-gaap:DepreciationDepletionAndAmortization = 540490 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 50270 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-15-004931 R8.htm prints 'Payments for repurchases of ordinary shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -415945 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-15-004931 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-15-004931 R8.htm read; no row matched (auto)
- revenue: era 10-K 0000866374-18-000007 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 25441131000 (FILING-CHECKED)
- interest_expense: era 10-K 0000866374-18-000007 R4.htm read; no row matched (auto)
- cash_paid_for_interest: era 10-K 0000866374-18-000007 R8.htm read; no row matched (auto)
- interest_expense: era 10-K 0000866374-21-000030 R4.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 10 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 4.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
