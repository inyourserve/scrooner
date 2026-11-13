# Rules: bank (GENERATED from rules/bank.csv and exam/results/ledger.csv — do not edit by hand)

17 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## (structural)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| bank.detect | sector_detect | bank | `{"all_of":["Deposits"],"any_of":["InterestAndDividendIncomeOperating","InterestExpenseDeposits","NoninterestIncome","LoansAndLeasesReceivabl` | `{"group":"bank"}` | sector-faces.md (Deposits + NII is not a bank test alone) | 0 | 0 |  |
| template.out.bank_insurer | sector_out | bank;insurer | `{"groups":["bank","insurer_unclassified"]}` | `{"status":"OUT","data_points":["current_assets","current_liabilities","cost_of_revenue","gross_profi` | sector templates (docmap OUT rows) | 95 | 48 | 49.5% |

## deposits

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| template.deposits | data_point | all | `{"order":18}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.deposits.tags | bank_tag | bank | `{"tags":["Deposits"]}` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 0 | 100.0% |

## loans_net

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| template.loans_net | data_point | all | `{"order":30}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.loans_net.tags | bank_tag | bank | `{"tags":["LoansAndLeasesReceivableNetReportedAmount","LoansAndLeasesReceivableNetOfDeferredIncome","FinancingReceivableExcludingAccruedInter` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 0 | 100.0% |

## net_interest_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.is.InterestIncomeExpenseNet | tag | all | `{"stmt":"IS","tag":"InterestIncomeExpenseNet","order":167}` | `{"decision":"map","concept":"net_interest_income","parent_concept":"","reason_class":""}` | interest.md §6 | 2 | 0 | 100.0% |
| template.net_interest_income | data_point | all | `{"order":32}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.net_interest_income.tags | bank_tag | bank | `{"tags":["InterestIncomeExpenseNet"]}` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 0 | 100.0% |

## noninterest_expense

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| template.noninterest_expense | data_point | all | `{"order":33}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.noninterest_expense.tags | bank_tag | bank | `{"tags":["NoninterestExpense"]}` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 0 | 100.0% |

## noninterest_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| template.noninterest_income | data_point | all | `{"order":34}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.noninterest_income.tags | bank_tag | bank | `{"tags":["NoninterestIncome"]}` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 0 | 100.0% |

## provision_for_credit_losses

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| template.provision_for_credit_losses | data_point | all | `{"order":39}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.provision_for_credit_losses.tags | bank_tag | bank | `{"tags":["ProvisionForLoanLeaseAndOtherLosses","ProvisionForLoanAndLeaseLosses","ProvisionForCreditLossesNet","ProvisionForLoanLossesExpense` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 2 | 0.0% |

## total_interest_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| template.total_interest_income | data_point | all | `{"order":49}` | `{"home_stmt":"IS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bank.total_interest_income.tags | bank_tag | bank | `{"tags":["InterestAndDividendIncomeOperating"]}` | `{"status":"mapped"}` | sector-faces.md; bank template | 2 | 0 | 100.0% |

