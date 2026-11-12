# QXO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-012601 (CIK 0001236275, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001185185-16-004077 (CIK 0001236275, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001185185-18-000498 (CIK 0001236275, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001185185-24-000237 (CIK 0001236275, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001236275.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 6842200000 | 6842200000 | 56900000 | 56900000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of products sold | 5269500000 | 5269500000 | 33800000 | 33800000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1572700000 | 1572700000 | 23100000 | 23100000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expense | 1817900000 | 1817900000 | 94100000 | 94100000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1394800000 | 1394800000 | 93000000 | 93000000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (846 tags across all 77 R pages, face and notes) of 0001628280-26-012601; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -245200000 | -245200000 | -71000000 | -71000000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest (expense) income, net | -47700000 | -47700000 | 121800000 | 121800000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | (Loss) income before (benefit from) provision for income taxes | -337100000 | -337100000 | 50800000 | 50800000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | (Benefit from) provision for income taxes | -57700000 | -57700000 | 22800000 | 22800000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net (loss) income | -279400000 | -279400000 | 28000000 | 28000000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Loss per common share - basic (in usd per share) | -0.63 | -0.63 | -0.11 | -0.11 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Loss per common share - diluted (in usd per share) | -0.63 | -0.63 | -0.11 | -0.11 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 613000000 | 613000000 | 204000000 | 204000000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 613000000 | 613000000 | 204000000 | 204000000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2361600000 | 2361600000 |  | 5068500000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 1145100000 | 1145100000 |  | 2700000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, net | 1497300000 | 1497300000 |  | 0 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 5546300000 | 5546300000 |  | 5089600000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 688600000 | 688600000 |  | 400000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5111300000 | 5111300000 |  | 1200000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 15887300000 | 15887300000 |  | 5098300000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 819000000 | 819000000 |  | 6200000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1550000000 | 1550000000 |  | 45100000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 6180500000 | 6180500000 |  | 45400000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 9706800000 | 9706800000 |  | 5052900000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 2.614e+08 | 261400000 |  | 84800000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -10630300000 | -10630300000 |  | -100000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 7662800000 | 7662800000 |  | 4981100000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Capital expenditures | -78200000 | 78200000 |  | 100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R8.htm | Depreciation + Amortization | 423100000 | 423100000 |  | 1100000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 144500000 | 144500000 |  | 34400000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Payment of common-stock dividend | 0 | 0 |  | 17400000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (846 tags across all 77 R pages, face and notes) of 0001628280-26-012601; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 138000000 | 138000000 |  | 100000 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes, net of refunds | 38200000 | 38200000 |  | 0 | Y | FILING-CHECKED | accn 0001628280-26-012601 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Long-term debt, net | 3057300000 | 3057300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 674500000 | 674500000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Total revenues, net' on us-gaap:SalesRevenueNet = 27641982 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Total cost of revenues' on us-gaap:CostOfRevenue = 16798448 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 10843534 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 10485746 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001185185-16-004077 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 5635571 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 357788 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNet = -57483 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 434305 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 60000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Net income' on us-gaap:ProfitLoss = 374305 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Basic (in Dollars per share)' on us-gaap:EarningsPerShareBasic = 0.09 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Diluted (in Dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.09 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Basic (in Shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 4301782 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001185185-16-004077 R4.htm prints 'Diluted (in Shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 4318449 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1193313 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Accounts receivable, net of allowance of $375,000 and $125,000' on us-gaap:AccountsReceivableNetCurrent = 2477301 (FILING-CHECKED)
- inventory: FY2015 10-K 0001185185-16-004077 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4893776 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 425347 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 401000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Total assets' on us-gaap:Assets = 8483549 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1594100 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 5569420 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 6927228 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001185185-16-004077 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1556321 (FILING-CHECKED)
- cfo: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 126659 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -643376 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Net cash provided by (used by) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 401693 (FILING-CHECKED)
- capex: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -67483 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 165597 (FILING-CHECKED)
- sbc: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Share-based compensation' on us-gaap:AllocatedShareBasedCompensationExpense = 40860 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001185185-16-004077 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Interest' on us-gaap:InterestPaid = 60579 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001185185-16-004077 R6.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 87732 (FILING-CHECKED)
- revenue: era 10-K 0001185185-18-000498 R4.htm prints 'Total revenues, net' on us-gaap:SalesRevenueNet = 34852028 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001185185-18-000498 R4.htm prints 'Total cost of revenues' on us-gaap:CostOfRevenue = 20986588 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001185185-18-000498 R6.htm prints 'Interest' on us-gaap:InterestPaid = 30946 (FILING-CHECKED)
- revenue: era 10-K 0001185185-24-000237 R4.htm prints 'Revenues' on us-gaap:Revenues = 54516941 (FILING-CHECKED)
- sga_expense: era 10-K 0001185185-24-000237 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 10217157 (FILING-CHECKED)
- interest_expense: era 10-K 0001185185-24-000237 R4.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -55666 (FILING-CHECKED)
- ppe_net: era 10-K 0001185185-24-000237 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 503347 (FILING-CHECKED)
- dividends_paid: era 10-K 0001185185-24-000237 R6.htm prints 'Payment of cash dividend' on us-gaap:PaymentsOfDividends = -1051256 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001185185-24-000237 R6.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 300732 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | mapped-sample | agree | page value 1817900000 vs printed 1817900000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | combined | agree | page value -47700000 vs printed -47700000 |
| goodwill | mapped-sample | agree | page value 5111300000 vs printed 5111300000 |
| current_liabilities | mapped-sample | agree | page value 1550000000 vs printed 1550000000 |
| cfo | mapped-sample | agree | page value 261400000 = printed 2.614e+08 at 4 significant digits; fy0_printed restored to the page value |
| depreciation_and_amortization | component sum | agree | page value 423100000 vs printed 423100000 |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 3245200000 vs printed 3245200000 |
