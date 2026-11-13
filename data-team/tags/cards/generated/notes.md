# Rules: notes (GENERATED from rules/notes.csv and exam/results/ledger.csv — do not edit by hand)

44 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## amortization_of_intangibles

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.AmortizationOfIntangibleAssets | tag | all | `{"stmt":"IS","tag":"AmortizationOfIntangibleAssets","order":205}` | `{"decision":"map","concept":"amortization_of_intangibles","parent_concept":"","reason_class":""}` | capex-and-da.md; Dhairya full 10-K reads (12 cos) 2026-11-12, FILING-CHECKED; Data Verifier docmaps ranks 51-67, 2026-11 | 8 | 0 | 100.0% |
| template.amortization_of_intangibles | data_point | all | `{"order":2}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.amortization_of_intangibles.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"AmortizationOfIntangibleAssets","status":"mapped","disabled_when_no_face":false}` | dev-set majority (exam README v2/v3) | 0 | 0 |  |
| notes.amortization_of_intangibles.fact.AmortizationOfIntangibleAssets | note_fact | all | `{"tag":"AmortizationOfIntangibleAssets","rank":0}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 43 | 25 | 41.9% |
| notes.amortization_of_intangibles.fact.AdjustmentForAmortization | note_fact | all | `{"tag":"AdjustmentForAmortization","rank":1}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 2 | 2 | 0.0% |

## cash_paid_for_income_taxes

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.cf.IncomeTaxesPaidNet | tag | all | `{"stmt":"CF","tag":"IncomeTaxesPaidNet","order":101}` | `{"decision":"map","concept":"cash_paid_for_income_taxes","parent_concept":"","reason_class":""}` | interest.md §6; Dhairya full 10-K reads (12 cos) 2026-11-12, FILING-CHECKED | 38 | 1 | 97.4% |
| lib.cf.IncomeTaxesPaid | tag | all | `{"stmt":"CF","tag":"IncomeTaxesPaid","order":189}` | `{"decision":"map","concept":"cash_paid_for_income_taxes","parent_concept":"","reason_class":""}` | interest.md §6 | 8 | 1 | 87.5% |
| template.cash_paid_for_income_taxes | data_point | all | `{"order":8}` | `{"home_stmt":"CF"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.cash_paid_for_income_taxes.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"IncomeTaxesPaidNet","status":"mapped","disabled_when_no_face":false}` | dev-set majority (exam README v2/v3) | 0 | 0 |  |
| notes.cash_paid_for_income_taxes.fact.IncomeTaxesPaidNet | note_fact | all | `{"tag":"IncomeTaxesPaidNet","rank":0}` | `{"status":"mapped"}` | FASB Income Taxes TIG v1.0 2025-02; Dhairya note convention 2026-11-12 | 56 | 20 | 64.3% |
| notes.cash_paid_for_income_taxes.fact.IncomeTaxesPaid | note_fact | all | `{"tag":"IncomeTaxesPaid","rank":1}` | `{"status":"mapped"}` | FASB Income Taxes TIG v1.0 2025-02; Dhairya note convention 2026-11-12 | 6 | 1 | 83.3% |
| notes.cash_paid_for_income_taxes.prefer.IncomeTaxesPaidNet | prefer_tag | all | `{"among":"mapped candidates"}` | `{"tag":"IncomeTaxesPaidNet"}` | DQC_0065 | 38 | 1 | 97.4% |

## cash_paid_for_interest

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.cf.InterestPaidNet | tag | all | `{"stmt":"CF","tag":"InterestPaidNet","order":99}` | `{"decision":"map","concept":"cash_paid_for_interest","parent_concept":"","reason_class":""}` | XBRL US DQC_0065 "Interest Paid Net (Operating) Not on Cash Flow" (final, released 2017-10-04, rule v5; github.com/DataQ | 57 | 0 | 100.0% |
| lib.cf.InterestPaid | tag | all | `{"stmt":"CF","tag":"InterestPaid","order":226}` | `{"decision":"map","concept":"cash_paid_for_interest","parent_concept":"","reason_class":""}` | XBRL US DQC_0065 "Interest Paid Net (Operating) Not on Cash Flow" (final, released 2017-10-04, rule v5; github.com/DataQ | 0 | 0 |  |
| template.cash_paid_for_interest | data_point | all | `{"order":9}` | `{"home_stmt":"CF"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.cash_paid_for_interest.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"InterestPaidNet","status":"mapped","disabled_when_no_face":false}` | dev-set majority (exam README v2/v3) | 0 | 0 |  |
| notes.cash_paid_for_interest.fact.InterestPaidNet | note_fact | all | `{"tag":"InterestPaidNet","rank":0}` | `{"status":"mapped"}` | DQC_0065; Dhairya note convention 2026-11-12 | 34 | 11 | 67.6% |
| notes.cash_paid_for_interest.fact.InterestPaid | note_fact | all | `{"tag":"InterestPaid","rank":1}` | `{"status":"mapped"}` | DQC_0065; Dhairya note convention 2026-11-12 | 9 | 6 | 33.3% |
| notes.cash_paid_for_interest.prefer.InterestPaidNet | prefer_tag | all | `{"among":"mapped candidates"}` | `{"tag":"InterestPaidNet"}` | DQC_0065 | 57 | 0 | 100.0% |

## dividends_per_share

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| notes.dividends_per_share.fact.CommonStockDividendsPerShareDeclared | note_fact | all | `{"tag":"CommonStockDividendsPerShareDeclared","rank":0}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 7 | 2 | 71.4% |
| notes.dividends_per_share.fact.CommonStockDividendsPerShareCashPaid | note_fact | all | `{"tag":"CommonStockDividendsPerShareCashPaid","rank":1}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 1 | 0 | 100.0% |

## interest_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.InvestmentIncomeInterest | tag | all | `{"stmt":"IS","tag":"InvestmentIncomeInterest","order":160}` | `{"decision":"map","concept":"interest_income","parent_concept":"","reason_class":""}` | interest.md §6 | 15 | 0 | 100.0% |
| lib.is.InterestAndDividendIncomeOperating | tag | all | `{"stmt":"IS","tag":"InterestAndDividendIncomeOperating","order":240}` | `{"decision":"map","concept":"interest_income","parent_concept":"","reason_class":""}` | interest.md §6 | 4 | 1 | 75.0% |
| lib.is.InterestAndDividendIncomeSecurities | tag | all | `{"stmt":"IS","tag":"InterestAndDividendIncomeSecurities","order":398}` | `{"decision":"component","concept":"","parent_concept":"interest_income","reason_class":"component_no` | bank-loans-and-allowance.md | 0 | 0 |  |
| lib.is.InterestAndFeeIncomeLoansAndLeases | tag | all | `{"stmt":"IS","tag":"InterestAndFeeIncomeLoansAndLeases","order":401}` | `{"decision":"component","concept":"","parent_concept":"interest_income","reason_class":"component_no` | bank-loans-and-allowance.md | 0 | 0 |  |
| lib.is.InterestIncomeOperating | tag | all | `{"stmt":"IS","tag":"InterestIncomeOperating","order":402}` | `{"decision":"map","concept":"interest_income","parent_concept":"","reason_class":""}` | interest.md §6 | 1 | 0 | 100.0% |
| lib.is.OtherInterestAndDividendIncome | tag | all | `{"stmt":"IS","tag":"OtherInterestAndDividendIncome","order":421}` | `{"decision":"component","concept":"","parent_concept":"interest_income","reason_class":"component_no` | bank-loans-and-allowance.md | 0 | 0 |  |
| nd.InvestmentIncomeNet | combined_concept | all | `{"tag":"InvestmentIncomeNet","order":4}` | `{"data_point":"interest_income","members":"interest_income:+1 (an interest child) ; dividends, gains` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.InterestAndOtherIncome | combined_concept | all | `{"tag":"InterestAndOtherIncome","order":9}` | `{"data_point":"interest_income","members":"interest_income:+1 (an interest child) ; dividends, gains` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.InterestIncomeOther | combined_concept | all | `{"tag":"InterestIncomeOther","order":17}` | `{"data_point":"interest_income","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.OtherInterestAndDividendIncome | combined_concept | all | `{"tag":"OtherInterestAndDividendIncome","order":43}` | `{"data_point":"interest_income","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.InterestIncomeSecuritiesTaxable | combined_concept | all | `{"tag":"InterestIncomeSecuritiesTaxable","order":48}` | `{"data_point":"interest_income","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| template.interest_income | data_point | all | `{"order":28}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| notes.interest_income.default_tag | note_default | all | `{"no_face_line":true,"no_note_facts_input":true}` | `{"tag":"InvestmentIncomeInterest","status":"mapped","disabled_when_no_face":true}` | dev-set majority (exam README v2/v3) | 0 | 0 |  |
| notes.interest_income.fact.InvestmentIncomeInterest | note_fact | all | `{"tag":"InvestmentIncomeInterest","rank":0}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 12 | 5 | 58.3% |
| notes.interest_income.fact.InterestIncomeOther | note_fact | all | `{"tag":"InterestIncomeOther","rank":1}` | `{"status":"component_in_note"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 6 | 4 | 33.3% |
| notes.interest_income.fact.InvestmentIncomeInterestAndDividend | note_fact | all | `{"tag":"InvestmentIncomeInterestAndDividend","rank":2}` | `{"status":"combined"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 7 | 4 | 42.9% |
| notes.interest_income.inside_net_line | procedure | all | `{"pretax_prefix":"IncomeLossFromContinuingOperationsBeforeIncomeTaxes","oi_tag":"OperatingIncomeLoss","label_any":"(?i)interest","label_net"` | `{"procedure":"notes.interest_income.inside_net_line"}` | interest card; dev keys | 10 | 5 | 50.0% |

## sbc

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| notes.sbc.fact.ShareBasedCompensation | note_fact | all | `{"tag":"ShareBasedCompensation","rank":0}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 3 | 1 | 66.7% |
| notes.sbc.fact.AllocatedShareBasedCompensationExpense | note_fact | all | `{"tag":"AllocatedShareBasedCompensationExpense","rank":1}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 13 | 8 | 38.5% |

## weighted_basic_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| notes.weighted_basic_shares.fact.WeightedAverageNumberOfSharesOutstandingBasic | note_fact | all | `{"tag":"WeightedAverageNumberOfSharesOutstandingBasic","rank":0}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 27 | 9 | 66.7% |
| notes.weighted_basic_shares.fact.WeightedAverageNumberOfShareOutstandingBasicAndDiluted | note_fact | all | `{"tag":"WeightedAverageNumberOfShareOutstandingBasicAndDiluted","rank":1}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 0 | 0 |  |

## weighted_diluted_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| notes.weighted_diluted_shares.fact.WeightedAverageNumberOfDilutedSharesOutstanding | note_fact | all | `{"tag":"WeightedAverageNumberOfDilutedSharesOutstanding","rank":0}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 27 | 9 | 66.7% |
| notes.weighted_diluted_shares.fact.WeightedAverageNumberOfShareOutstandingBasicAndDiluted | note_fact | all | `{"tag":"WeightedAverageNumberOfShareOutstandingBasicAndDiluted","rank":1}` | `{"status":"mapped"}` | Dhairya note convention 2026-11-12 (fsn-line-to-concept.md §AB) | 0 | 0 |  |

