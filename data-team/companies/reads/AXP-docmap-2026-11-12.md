# AXP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). DATA-INFERRED rows say so.

## Filings opened
- Latest 10-K 0000004962-26-000080 (CIK 0000004962, filed 2026-02-06, FY ended 2025-12-31, comparative 2024-12-31). R3 income statement, R4 IS parenthetical, R5 comprehensive income, R6 balance sheet, R7 BS parenthetical (shares outstanding), R8 cash flows, R10/R11 equity (R11 parenthetical: dividends per share); notes R85 goodwill, R93 debt (interest paid), R122/R125 income taxes paid.
- companyfacts CIK0000004962.json (one call). Sector template: lender (bank-like income statement) per SECTOR-TEMPLATES-2026-11-01.

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenuesNetOfInterestExpense | IS R3.htm | Total revenues net of interest expense | 72229000000 | 72229000000 | 65949000000 | 65949000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cost_of_revenue | OUT |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | lender/bank-like IS: no cost of revenue line (R3) |
| gross_profit | OUT |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | no gross profit line |
| operating_expenses | mapped | NoninterestExpense | IS R3.htm | Total expenses | 53178000000 | 53178000000 | 47869000000 | 47869000000 | Y | FILING-CHECKED | bank-like: 'Total expenses' (excludes provisions for credit losses, which sit above) = noninterest expense; sector template replaces opex with noninterest expense | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| sga_expense | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | no SG&A line; 'Marketing' 6,252 (MarketingExpense), 'Salaries and employee benefits' 9,016 are separate components, never SG&A |
| research_and_development | OUT |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | no R&D line |
| operating_income | OUT |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | no operating income line; 'Pretax income' follows 'Total expenses' |
| interest_expense | mapped | InterestExpenseOperating | IS R3.htm | Total interest expense | 8234000000 | 8234000000 | 8252000000 | 8252000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| interest_income | mapped | InterestAndDividendIncomeOperating | IS R3.htm | Total interest income | 25598000000 | 25598000000 | 23795000000 | 23795000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| other_income_expense_net | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED | no non-operating other income/expense section on R3 (bank-like statement) |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R3.htm | Pretax income | 13795000000 | 13795000000 | 12895000000 | 12895000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income tax provision | 2962000000 | 2962000000 | 2766000000 | 2766000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net income | 10833000000 | 10833000000 | 10129000000 | 10129000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic (in dollars per share) | 15.41 | 15.41 | 14.04 | 14.04 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted (in dollars per share) | 15.38 | 15.38 | 14.01 | 14.01 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic (in shares) | 695000000 | 695000000 | 712000000 | 712000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted (in shares) | 696000000 | 696000000 | 713000000 | 713000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R11.htm | Common stock, dividend per share (in dollars per share) | 3.28 | 3.28 | 2.8 | 2.8 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R5.htm | Comprehensive income | 10951000000 | 10951000000 | 9806000000 | 9806000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | CF R8.htm | Cash and cash equivalents at end of year | 47792000000 | 47792000000 | 40640000000 | 40640000000 | Y | FILING-CHECKED | bank rule: CF printed ending cash (R8) = BS 'Total cash and cash equivalents' 47,792 (R6); includes restricted cash (labelled); BS 'Cash and due from banks' 3,559 is a component | accn 0000004962-26-000080 period ..2025-12-31 |
| accounts_receivable | OUT |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED | bank/lender template: no trade accounts receivable; 'Card Member receivables' are financing receivables |
| inventory | OUT |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED | no inventory line |
| current_assets | OUT |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED | unclassified balance sheet: no total current assets |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R6.htm | Premises and equipment, less accumulated depreciation and am | 6118000000 | 6118000000 | 5371000000 | 5371000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| goodwill | mapped | Goodwill | NOTE R85.htm | Goodwill, ending balance | 4872000000 | 4872000000 | 4187000000 | 4187000000 | Y | FILING-CHECKED | not on the BS face (inside 'Other assets' 24,263); consolidated goodwill ending balance from note R85 (note-sourced) | accn 0000004962-26-000080 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R6.htm | Total assets | 300052000000 | 300052000000 | 271461000000 | 271461000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| accounts_payable | mapped | AccountsPayableCurrentAndNoncurrent | BS R6.htm | Accounts payable | 14700000000 | 14700000000 | 13884000000 | 13884000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| current_liabilities | OUT |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED | unclassified balance sheet: no total current liabilities |
| total_liabilities | mapped | Liabilities | BS R6.htm | Total liabilities | 266578000000 | 266578000000 | 241197000000 | 241197000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| total_debt | component sum | ShortTermBorrowings+LongTermDebt | BS R6.htm+R6.htm | Short-term borrowings + Long-term debt (includes debt issued | 57758000000 | 57758000000 | 51089000000 | 51089000000 | Y | FILING-CHECKED | BS 'Short-term borrowings' + 'Long-term debt (includes VIE debt)'; customer deposits are not debt; operating leases excluded; finance leases: none found in fetched pages (R105 shows operating lease only) | accn 0000004962-26-000080 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R6.htm | Total shareholders’ equity | 33474000000 | 33474000000 | 30264000000 | 30264000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | PAR R7.htm | Common shares, outstanding (in shares) | 686000000 | 686000000 | 702000000 | 702000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R8.htm | Net cash provided by operating activities | 18428000000 | 18428000000 | 14050000000 | 14050000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R8.htm | Net cash used in investing activities | -22891000000 | -22891000000 | -24402000000 | -24402000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R8.htm | Net cash provided by financing activities | 11210000000 | 11210000000 | 4436000000 | 4436000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R8.htm | Purchase of premises and equipment, net of sales: 2025, $1;  | -2425000000 | 2425000000 | -1911000000 | 1911000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | bank template OUT-by-definition but AXP prints the line (company override) | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | mapped | DepreciationAmortizationAndAccretionNet | CF R8.htm | Depreciation and amortization | 1777000000 | 1777000000 | 1676000000 | 1676000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | not_presented |  | NOTE  |  |  |  |  |  |  | FILING-CHECKED | no such line on the face statements (R pages read) and no consolidated fact in the fetched detail pages; no amortization-of-intangibles line on R8 or in the fetched detail pages (searched tags AmortizationOfIntangibleAssets / FiniteLivedIntangibleAssetsAmortizationExpense) |
| sbc | mapped | ShareBasedCompensation | CF R8.htm | Stock-based compensation | 551000000 | 551000000 | 504000000 | 504000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| dividends_paid | mapped | PaymentsOfDividends | CF R8.htm | Dividends paid | -2271000000 | 2271000000 | -1999000000 | 1999000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R8.htm | Repurchase of American Express common shares and other | -5814000000 | 5814000000 | -6020000000 | 6020000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | R8 'Repurchase of American Express common shares' (pure common repurchase line) | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cf_ar_change | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED | no receivables change in operating section; 'Net increase in loans and Card Member receivables' is investing and is a lending flow |
| cf_inventory_change | OUT |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED | no inventory line |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities | CF R8.htm | Accounts payable & other liabilities | 3645000000 | 3645000000 | -2897000000 | -2897000000 | Y | FILING-CHECKED | 'Accounts payable & other liabilities' = combined line | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | NOTE R93.htm | Interest paid | 8000000000 | 8000000000 | 8200000000 | 8200000000 | Y | FILING-CHECKED | not on the CF face; note R93 'Interest paid' printed rounded (8,000.0 / 8,200.0 million): rounded note figure, flag | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | NOTE R125.htm | Total | 3195000000 | 3195000000 | 3600000000 | 3600000000 | Y | FILING-CHECKED | ASU 2023-09 era: in the tax note (R125 Total 3,195 / 3,600), not on the CF face | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| net_interest_income | mapped | InterestIncomeExpenseNet | IS R3.htm | Net interest income | 17364000000 | 17364000000 | 15543000000 | 15543000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| total_interest_income | mapped | InterestAndDividendIncomeOperating | IS R3.htm | Total interest income | 25598000000 | 25598000000 | 23795000000 | 23795000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| noninterest_income | mapped | NoninterestIncome | IS R3.htm | Total non-interest revenues | 54865000000 | 54865000000 | 50406000000 | 50406000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| noninterest_expense | mapped | NoninterestExpense | IS R3.htm | Total expenses | 53178000000 | 53178000000 | 47869000000 | 47869000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period 2025-01-01..2025-12-31 |
| provision_for_credit_losses | mapped | ProvisionForLoanLossesExpensed |   |  | 5256000000 | 5256000000 | 5185000000 | 5185000000 | Y (hand) | FILING-CHECKED | check: hand R3 (IS) 'Provisions for credit losses' 5,256 / 5,185 on ProvisionForLoanLossesExpensed = companyfacts (same accession); also R8 CF; the AUTO not_presented was wrong | 2026-11-12 |
| deposits | mapped | Deposits | BS R6.htm | Customer deposits | 152488000000 | 152488000000 | 139413000000 | 139413000000 | Y | FILING-CHECKED |  | accn 0000004962-26-000080 period ..2025-12-31 |
| loans_net | not_presented |  | BS R6.htm |  |  |  |  |  |  | FILING-CHECKED | AXP BS prints Card Member receivables and Card Member loans as separate lines; no loans-net total; instants are never summed |

## Era checks (tag changes in the last ~5 years)
Auto scan: interest_expense tag InterestExpenseOperating covers FY2022-FY2025; older FY2021-2023 also carry InterestExpense (see ERA-CHECK row). EPS tags: the latest filing prints EarningsPerShareBasic/Diluted on R3 ('Basic'/'Diluted'); cloud's IncomeLossFromContinuingOperationsPerBasicShare rule (7 filings) is an older era, no longer on the latest line. Revenue tag RevenuesNetOfInterestExpense covers 5 FY (the custom twin ax:TotalRevenuesNetOfInterestExpense is older).

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1. AXP IS RevenuesNetOfInterestExpense map revenue (35) / custom twin (17): AGREE (R3 'Total revenues net of interest expense' 72,229).
2. AXP IS TotalRevenuesNetOfInterestExpenseAfterProvisionsForLosses exclude revenue (27): AGREE (ax: custom subtotal 66,973 sits below revenue).
3. AXP IS NoninterestIncome exclude revenue (31): AGREE (component 54,865).
4. AXP IS IncomeLossFromContinuingOperationsPerBasicShare map basic_eps (7) / Diluted: NOT APPLICABLE to the latest filing (R3 EPS is EarningsPerShareBasic 15.41 / Diluted 15.38); no discontinued operations, so either reading gives the same number in the old era.
5. AXP BS CashAndDueFromBanks map cash (52): DISAGREE. R6 prints 'Cash and due from banks (includes restricted cash...)' 3,559 AND 'Total cash and cash equivalents (includes restricted cash...)' 47,792 (CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents). Card rule (bank cash = the CF printed ending cash; Dhairya 2026-11-12) -> 47,792 (R8 'Cash and cash equivalents at end of year', same value) with the restricted-cash flag; the 3,559 line is only one component of cash and equivalents. The cloud mapping serves 3,559 (a partial cash). Filing supports: CF ending cash 47,792.
6. AXP BS template_out_pending_read current_assets/current_liabilities: CONFIRMED OUT (R6 unclassified, no total current assets / liabilities).
7. AXP IS template_out_pending_read gross_profit / cost_of_revenue / operating_income: CONFIRMED OUT (R3 has no such lines; 'Pretax income' follows 'Total expenses').
8. AXP CF c:PaymentsForRepurchasesOfCommonSharesAndOther combined share_buybacks (13): NOT APPLICABLE to the latest filing: R8 financing prints 'Repurchase of American Express common shares' (PaymentsForRepurchaseOfCommonStock) 5,814 / 6,020, a pure common repurchase line (era change); mapped.

## Mismatches (printed vs API)
none beyond sign differences (printed parentheses / negated labels). Interest paid R93 is a rounded note figure (8,000.0 / 8,200.0 millions): flagged.

## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)
- provision_for_credit_losses: check: hand -> mapped | check: hand R3 (IS) 'Provisions for credit losses' 5,256 / 5,185 on ProvisionForLoanLossesExpensed = companyfacts (same accession); also R8 
- 0 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
