# Rules: per_share (GENERATED from rules/per_share.csv and exam/results/ledger.csv — do not edit by hand)

23 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## (structural)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| per_share.parenthetical_allowed | parenthetical_allowed | all | `{}` | `{"data_points":["shares_outstanding","dividends_per_share"]}` | net-income-and-shares card | 0 | 0 |  |

## basic_eps

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.EarningsPerShareBasic | tag | all | `{"stmt":"IS","tag":"EarningsPerShareBasic","order":6}` | `{"decision":"map","concept":"basic_eps_resolved","parent_concept":"","reason_class":""}` | net-income-and-shares.md §7 | 98 | 0 | 100.0% |
| template.basic_eps | data_point | all | `{"order":3}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## diluted_eps

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.EarningsPerShareDiluted | tag | all | `{"stmt":"IS","tag":"EarningsPerShareDiluted","order":7}` | `{"decision":"map","concept":"diluted_eps_resolved","parent_concept":"","reason_class":""}` | net-income-and-shares.md §7 | 100 | 0 | 100.0% |
| lib.is.EarningsPerShareBasicAndDiluted | tag | all | `{"stmt":"IS","tag":"EarningsPerShareBasicAndDiluted","order":399}` | `{"decision":"map","concept":"diluted_eps_resolved","parent_concept":"","reason_class":""}` | explicit | 0 | 0 |  |
| template.diluted_eps | data_point | all | `{"order":20}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## dividends_per_share

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.CommonStockDividendsPerShareDeclared | tag | all | `{"stmt":"IS","tag":"CommonStockDividendsPerShareDeclared","order":133}` | `{"decision":"map","concept":"dividends_per_share_resolved","parent_concept":"","reason_class":""}` | shareholder-returns.md §3; Data Verifier docmaps ranks 51-67, 2026-11-12, FILING-CHECKED | 6 | 0 | 100.0% |
| lib.is.CommonStockDividendsPerShareCashPaid | tag | all | `{"stmt":"IS","tag":"CommonStockDividendsPerShareCashPaid","order":201}` | `{"decision":"map","concept":"dividends_per_share_resolved","parent_concept":"","reason_class":""}` | shareholder-returns.md §3 | 8 | 0 | 100.0% |
| lib.eq.CommonStockDividendsPerShareDeclared | tag | all | `{"stmt":"EQ","tag":"CommonStockDividendsPerShareDeclared","order":337}` | `{"decision":"map","concept":"dividends_per_share_resolved","parent_concept":"","reason_class":""}` | shareholder-returns.md §3; MDT 0001613103-18-000024 | 32 | 3 | 90.6% |
| template.dividends_per_share | data_point | all | `{"order":22}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.dividends_per_share.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"CommonStockDividendsPerShareDeclared","status":"mapped","disabled_when_no_face":true}` | dev-set majority (exam README v2/v3) | 0 | 0 |  |

## shares_outstanding

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.eq.CommonStockSharesOutstanding | tag | all | `{"stmt":"EQ","tag":"CommonStockSharesOutstanding","order":66}` | `{"decision":"map","concept":"shares_outstanding_resolved","parent_concept":"","reason_class":""}` | net-income-and-shares.md §7; Dhairya / Engineering expander request 2026-11-12 | 0 | 0 |  |
| lib.eq.SharesOutstanding | tag | all | `{"stmt":"EQ","tag":"SharesOutstanding","order":108}` | `{"decision":"component","concept":"","parent_concept":"shares_outstanding_resolved","reason_class":"` | net-income-and-shares.md §7 | 0 | 0 |  |
| lib.bs.CommonStockSharesOutstanding | tag | all | `{"stmt":"BS","tag":"CommonStockSharesOutstanding","order":445}` | `{"decision":"map","concept":"shares_outstanding_resolved","parent_concept":"","reason_class":""}` | fsn-balance-sheet-liabilities-equity.md; net-income-and-shares.md §7 | 36 | 3 | 91.7% |
| template.shares_outstanding | data_point | all | `{"order":45}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| per_share.shares_outstanding.stmt | stmt_restrict | all | `{"stmts":["BS","EQ"]}` | `{}` | Dhairya shares ruling 2026-11-12 | 0 | 0 |  |

## weighted_basic_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.WeightedAverageNumberOfSharesOutstandingBasic | tag | all | `{"stmt":"IS","tag":"WeightedAverageNumberOfSharesOutstandingBasic","order":21}` | `{"decision":"map","concept":"weighted_basic_shares","parent_concept":"","reason_class":""}` | net-income-and-shares.md §7 | 77 | 0 | 100.0% |
| lib.is.WeightedAverageNumberOfShareOutstandingBasicAndDiluted | tag | all | `{"stmt":"IS","tag":"WeightedAverageNumberOfShareOutstandingBasicAndDiluted","order":425}` | `{"decision":"map","concept":"weighted_basic_shares","parent_concept":"","reason_class":""}` | net-income-and-shares.md §7 | 0 | 0 |  |
| template.weighted_basic_shares | data_point | all | `{"order":51}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.weighted_basic_shares.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"WeightedAverageNumberOfSharesOutstandingBasic","status":"mapped","disabled_when_no_face":fal` | dev-set majority (exam README v2/v3) | 0 | 0 |  |

## weighted_diluted_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.WeightedAverageNumberOfDilutedSharesOutstanding | tag | all | `{"stmt":"IS","tag":"WeightedAverageNumberOfDilutedSharesOutstanding","order":20}` | `{"decision":"map","concept":"weighted_diluted_shares","parent_concept":"","reason_class":""}` | net-income-and-shares.md §7 | 78 | 0 | 100.0% |
| template.weighted_diluted_shares | data_point | all | `{"order":52}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.weighted_diluted_shares.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"WeightedAverageNumberOfDilutedSharesOutstanding","status":"mapped","disabled_when_no_face":f` | dev-set majority (exam README v2/v3) | 0 | 0 |  |

