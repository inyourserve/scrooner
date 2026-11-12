# ENS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001628280-26-036900 (CIK 0001289308, filed 2026-05-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001289308-24-000018 (CIK 0001289308, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001289308.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R5.htm | Net sales | 3751376000 | 3751376000 | 3617579000 | 3617579000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 2345865000 |  | 2223939000 |  | API missing | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1097562000 | 1097562000 | 1092404000 | 1092404000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the sga_expense tag/label rules; not hand-verified |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating earnings | 426460000 | 426460000 | 464686000 | 464686000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | 50501000 | 50501000 | 51116000 | 51116000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Earnings before income taxes | 347406000 | 347406000 | 406577000 | 406577000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 53849000 | 53849000 | 42842000 | 42842000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net earnings attributable to EnerSys stockholders | 293557000 | 293557000 | 363735000 | 363735000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (usd per share) | 7.84 | 7.84 | 9.15 | 9.15 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (usd per share) | 7.7 | 7.7 | 8.99 | 8.99 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 37439727 | 37439727 | 39760829 | 39760829 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 38144210 | 38144210 | 40438579 | 40438579 | Y | FILING-CHECKED | accn 0001628280-26-036900 R5.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 438675000 | 438675000 | 343131000 | 343131000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for doubtful accounts (2026–$8,583; 2025–$8,675) | 506072000 | 506072000 | 597942000 | 597942000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, net | 724690000 | 724690000 | 739994000 | 739994000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2141810000 | 2141810000 | 2089814000 | 2089814000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant, and equipment, net | 593002000 | 593002000 | 592433000 | 592433000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 752424000 | 752424000 | 721073000 | 721073000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4003324000 | 4003324000 | 3971248000 | 3971248000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 354190000 | 354190000 | 405694000 | 405694000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 804038000 | 804038000 | 775068000 | 775068000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2094452000 | 2094452000 | 2051760000 | 2051760000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total EnerSys stockholders’ equity | 1905284000 | 1905284000 | 1916078000 | 1916078000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R3.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 547596000 | 547596000 | 260298000 | 260298000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -87882000 | -87882000 | -336394000 | -336394000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash (used in) provided by financing activities | -380703000 | -380703000 | 90270000 | 90270000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -80074000 | 80074000 | -121038000 | 121038000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 113558000 | 113558000 | 100876000 | 100876000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 37594000 | 37594000 | 27825000 | 27825000 | Y | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid to stockholders | -38142000 | 38142000 | -37466000 | 37466000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchase of treasury stock | -370685000 | 370685000 | -153961000 | 153961000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-036900 R9.htm period ..2026-03-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent | R3.htm | Short-term debt + Long-term debt, net of unamortized debt issuance costs | 1108983000 | 1108983000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 36462211 | 36462211 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-03-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001289308-24-000018 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = 49954000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
