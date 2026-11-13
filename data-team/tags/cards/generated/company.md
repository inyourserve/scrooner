# Rules: company (GENERATED from rules/company.csv and exam/results/ledger.csv — do not edit by hand)

21 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## (structural)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.MCD.PaymentsToAcquireOtherProductiveAssets | override | MCD | `{"cik":"0000063908","tag":"PaymentsToAcquireOtherProductiveAssets","stmt":"CF","order":8}` | `{"concept":"(excluded)","status":"FILING-CHECKED","value_source":"sec_api"}` | Dhairya document-first reads ranks 68-84, 2026-11-12, FILING-CHECKED | 0 | 0 |  |
| company.BA.PaymentsOfDividends | override | BA | `{"cik":"0000012927","tag":"PaymentsOfDividends","stmt":"CF","order":9}` | `{"concept":"(excluded)","status":"FILING-CHECKED","value_source":"sec_api"}` | Dhairya document-first reads ranks 68-84, 2026-11-12, FILING-CHECKED | 0 | 0 |  |
| company.CB.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | override | CB | `{"cik":"0000896159","tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents","stmt":"BS","order":15}` | `{"concept":"(served as printed, \"includes restricted cash\")","status":"FILING-CHECKED","value_sour` | Dhairya document-first reads ranks 85-100, 2026-11-12, FILING-CHECKED | 0 | 0 |  |
| company.CRM.AmortizationOfAboveAndBelowMarketLeases | override | CRM | `{"cik":"0001108524","tag":"AmortizationOfAboveAndBelowMarketLeases","stmt":"IS","order":18}` | `{"concept":"(excluded)","status":"FILING-CHECKED","value_source":"sec_api"}` | 0001108524-26-000060 R63 (intangibles note, 1,700M); Data Verifier docmaps ranks 51-67, 2026-11-12, FILING-CHECKED | 0 | 0 |  |
| company.SNDK.AccountsPayableCurrent | override | SNDK | `{"cik":"0002023554","tag":"AccountsPayableCurrent","stmt":"BS","order":19}` | `{"concept":"(not_presented)","status":"FILING-CHECKED","value_source":"sec_api"}` | 0001628280-26-057406 R3 (related 460 / non-related 516, no total); Data Verifier docmaps ranks 51-67, 2026-11-12, FILING | 0 | 0 |  |

## accounts_receivable

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.RTX.ReceivablesNetCurrent | override | RTX | `{"cik":"0000101829","tag":"ReceivablesNetCurrent","stmt":"BS","order":0}` | `{"concept":"accounts_receivable","status":"FILING-CHECKED","value_source":"sec_api"}` | Dhairya full 10-K read 2026-11-12 (data-team/companies/reads/) | 0 | 0 |  |
| company.MO.OtherReceivablesNetCurrent | override | MO | `{"cik":"0000764180","tag":"OtherReceivablesNetCurrent","stmt":"BS","order":10}` | `{"concept":"accounts_receivable","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000764180-26-000017 BS R3 "Receivables" 263M / 177M (tag changed from ReceivablesNetCurrent vs 0000764180-21-000037); d | 1 | 0 | 100.0% |
| company.BKNG.AccountsAndOtherReceivablesNetCurrent | override | BKNG | `{"cik":"0001075531","tag":"AccountsAndOtherReceivablesNetCurrent","stmt":"BS","order":11}` | `{"concept":"accounts_receivable","status":"FILING-CHECKED","value_source":"sec_api"}` | 0001075531-26-000009 BS R3 "Accounts receivable, net (Allowance … $137 and $146)" 3,820M / 3,199M; docmap data-team/comp | 1 | 0 | 100.0% |

## capex

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.MS.PaymentsForProceedsFromProductiveAssets | override | MS | `{"cik":"0000895421","tag":"PaymentsForProceedsFromProductiveAssets","stmt":"CF","order":5}` | `{"concept":"capex_resolved","status":"FILING-CHECKED","value_source":"sec_api"}` | Dhairya full 10-K read 2026-11-11 ("premises, equipment and software") | 0 | 0 |  |

## capex_resolved component

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.IBM.custominvestmentinsoftware | override | IBM | `{"cik":"0000051143","tag":"(custom) investment in software","stmt":"CF","order":20}` | `{"concept":"capex_resolved component","status":"FILING-CHECKED","value_source":"fsn_xbrl"}` | 0000051143-26-000010 R7 "Investment in software" 647 + "Payments for property, plant and equipment" 1,091; Data Verifier | 0 | 0 |  |

## cash_and_equivalents

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.FITB.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | override | FITB | `{"cik":"0000035527","tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents","stmt":"BS","order":1}` | `{"concept":"cash_and_equivalents_resolved","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000035527-26-000202 R2 4,374M (fsn-balance-sheet-assets.md) | 0 | 0 |  |
| company.GILD.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | override | GILD | `{"cik":"0000882095","tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents","stmt":"BS","order":2}` | `{"concept":"cash_and_equivalents_resolved","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000882095-26-000006 BS R3 "Cash and cash equivalents" 7,564 / 9,991M = CF R9 ending 7,564 / 9,991M; no restricted cash  | 1 | 0 | 100.0% |
| company.DHR.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | override | DHR | `{"cik":"0000313616","tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents","stmt":"BS","order":3}` | `{"concept":"cash_and_equivalents_resolved","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000313616-26-000062 BS R3 "Cash and equivalents" 4,615 / 2,078M = CF R8 ending; no restricted cash anywhere (Dhairya R- | 1 | 0 | 100.0% |

## cf_ar_change

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.LLY.IncreaseDecreaseInAccountsAndOtherReceivables | override | LLY | `{"cik":"0000059478","tag":"IncreaseDecreaseInAccountsAndOtherReceivables","stmt":"CF","order":4}` | `{"concept":"cf_ar_change","status":"FILING-CHECKED","value_source":"sec_api"}` | Dhairya full 10-K read 2026-11-11 (24 top-50 cos) | 0 | 0 |  |

## interest_expense

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.NEM.InterestIncomeExpenseNonoperatingNet | override | NEM | `{"cik":"0001164727","tag":"InterestIncomeExpenseNonoperatingNet","stmt":"IS","order":17}` | `{"concept":"interest_expense_resolved","status":"FILING-CHECKED","value_source":"sec_api"}` | 0001164727-26-000010 IS R3 "Interest expense, net of capitalized interest of $144, $114 and $89" stored −229M / −375M; d | 1 | 0 | 100.0% |

## interest_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.FTNT.InvestmentIncomeNet | override | FTNT | `{"cik":"0001262039","tag":"InvestmentIncomeNet","stmt":"IS","order":12}` | `{"concept":"interest_income","status":"FILING-CHECKED","value_source":"sec_api"}` | 0001262039-26-000007 IS R5 "INTEREST INCOME" 162.3M / 155.2M; docmap data-team/companies/reads/FTNT-docmap-2026-11-12 (m | 1 | 0 | 100.0% |
| company.PH.InterestIncomeExpenseNonoperatingNet | override | PH | `{"cik":"0000076334","tag":"InterestIncomeExpenseNonoperatingNet","stmt":"IS","order":13}` | `{"concept":"interest_income","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000076334-26-000105 note R120 "Interest income" stored −14M / −11M (abs 14 / 11): sign −1; docmap data-team/companies/r | 0 | 0 |  |

## inventory

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.T.PrepaidExpenseCurrent | override | T | `{"cik":"0000732717","tag":"PrepaidExpenseCurrent","stmt":"BS","order":6}` | `{"concept":"inventory","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000732717-26-000120 BS R6 "Inventories" 2,420M / 2,270M (PrepaidExpenseCurrent; same tag in the FY-4 10-K 0000732717-23 | 1 | 0 | 100.0% |

## sbc

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.NEM.EmployeeBenefitsAndShareBasedCompensation | override | NEM | `{"cik":"0001164727","tag":"EmployeeBenefitsAndShareBasedCompensation","stmt":"CF","order":14}` | `{"concept":"sbc","status":"FILING-CHECKED","value_source":"sec_api"}` | 0001164727-26-000010 CF R8 "Stock-based compensation" 99M / 89M (ShareBasedCompensation not used); docmap data-team/comp | 1 | 0 | 100.0% |

## weighted_basic_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.MCD.WeightedAverageNumberOfSharesOutstandingBasic | override | MCD | `{"cik":"0000063908","tag":"WeightedAverageNumberOfSharesOutstandingBasic","stmt":"IS","order":7}` | `{"concept":"weighted_basic_shares","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000063908-26-000035 IS R3 "Weighted-average shares outstanding–basic" printed 713.4 / 718.3 (millions) and stored 713.4 | 1 | 0 | 100.0% |

## weighted_diluted_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| company.MCD.WeightedAverageNumberOfDilutedSharesOutstanding | override | MCD | `{"cik":"0000063908","tag":"WeightedAverageNumberOfDilutedSharesOutstanding","stmt":"IS","order":16}` | `{"concept":"weighted_diluted_shares","status":"FILING-CHECKED","value_source":"sec_api"}` | 0000063908-26-000035 IS R3 "Weighted-average shares outstanding–diluted" 716.4 / 721.9 stored unscaled; docmap data-team | 1 | 0 | 100.0% |

