# Predictor backtest (2026-11-13T05:08:07Z)

Baseline `/tmp/claude-0/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/scratchpad/wt/data-team/tags/exam/tools/predict.py` (sha-c7333fee) vs candidate `/tmp/claude-0/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/scratchpad/cand/predict.py` (sha-1646029b). Verdict: **FAIL**.

Tickers with keys 519; hand-verified key rows 8063 (excluded as not hand-verified 12557); compared 7971; set aside (key_error / key_unverified in either) 92.

Overall: baseline 89.0%, candidate 88.7%, right->wrong 23, wrong->right 3, net delta -20.

Key sources: origin/main 16be8a4c; origin/work/reads/201-300 88b71db8; origin/work/reads/301-400 08e7a4bd; origin/work/reads/401-500 8f481368; origin/work/reads/501-600 d372e3a4; origin/work/reads/601-700 ef86fd7e; origin/work/reads/701-800 e1b45bb2; origin/work/reads/701-800-fsn-expert-handcheck c6664bd7; origin/work/reads/801-900 ebf25aa5; origin/work/reads/901-1000 c7e0ee17

Predictor runs without output: {'baseline': 2, 'candidate': 2}

## Gate failures

- overall net delta -20 <= 0 (right->wrong 23, wrong->right 3)

## By statement

| Statement | n | Baseline | Candidate |
|---|---|---|---|
| BS | 2496 | 87.3% | 87.3% |
| CF | 1680 | 89.3% | 89.3% |
| IS | 2702 | 90.5% | 89.7% |
| NOTE-type | 1093 | 88.6% | 88.6% |

## Data point x template group

| Stmt | Data point | Group | n | Baseline % | Candidate % | Delta pp | R->W | W->R | Graduated |
|---|---|---|---|---|---|---|---|---|---|
| BS | accounts_payable | Energy:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Financials:unclassified | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Other:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Real Estate:unclassified | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | bank | 15 | 86.7 | 86.7 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | bdc_fund_or_unclassified | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | corporate | 111 | 95.5 | 95.5 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | other_financial | 12 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | reit | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | utility | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Energy:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Financials:unclassified | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Other:unclassified | 6 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Real Estate:unclassified | 7 | 42.9 | 42.9 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Utilities:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | bank | 15 | 73.3 | 73.3 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | bdc_fund_or_unclassified | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | corporate | 130 | 82.3 | 82.3 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | energy | 7 | 14.3 | 14.3 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | other_financial | 12 | 58.3 | 58.3 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | reit | 6 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | utility | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | Financials:unclassified | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | bank | 9 | 11.1 | 11.1 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | bdc_fund_or_unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | corporate | 97 | 92.8 | 92.8 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | other_financial | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | reit | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | Real Estate:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | bank | 11 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | bdc_fund_or_unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | corporate | 95 | 98.9 | 98.9 | +0.0 | 0 | 0 |  |
| BS | current_assets | energy | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| BS | current_assets | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | other_financial | 11 | 81.8 | 81.8 | +0.0 | 0 | 0 |  |
| BS | current_assets | reit | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | Real Estate:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | bank | 11 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | bdc_fund_or_unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | corporate | 100 | 99.0 | 99.0 | +0.0 | 0 | 0 | Y |
| BS | current_liabilities | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | other_financial | 12 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | reit | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | deposits | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | deposits | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Energy:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Real Estate:unclassified | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | goodwill | Utilities:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | bank | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | bdc_fund_or_unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | corporate | 122 | 94.3 | 94.3 | +0.0 | 0 | 0 |  |
| BS | goodwill | energy | 14 | 85.7 | 85.7 | +0.0 | 0 | 0 |  |
| BS | goodwill | insurer | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | goodwill | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | other_financial | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | goodwill | reit | 10 | 90.0 | 90.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | utility | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Other:unclassified | 10 | 90.0 | 90.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Real Estate:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Utilities:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | inventory | bank | 11 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | bdc_fund_or_unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | corporate | 148 | 93.2 | 93.2 | +0.0 | 0 | 0 |  |
| BS | inventory | energy | 12 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | inventory | insurer | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | inventory | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | other_financial | 15 | 86.7 | 86.7 | +0.0 | 0 | 0 |  |
| BS | inventory | reit | 9 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | utility | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | loans_net | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | loans_net | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | Other:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | Real Estate:unclassified | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | ppe_net | bank | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | bdc_fund_or_unclassified | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | ppe_net | corporate | 112 | 81.2 | 81.2 | +0.0 | 0 | 0 |  |
| BS | ppe_net | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| BS | ppe_net | insurer | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | other_financial | 9 | 55.6 | 55.6 | +0.0 | 0 | 0 |  |
| BS | ppe_net | reit | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| BS | ppe_net | utility | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Energy:unclassified | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Other:unclassified | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Utilities:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | bank | 9 | 77.8 | 77.8 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | corporate | 158 | 87.3 | 87.3 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | energy | 9 | 77.8 | 77.8 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | insurer | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | other_financial | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | reit | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | utility | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Energy:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | corporate | 97 | 92.8 | 92.8 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | energy | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | insurer | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | other_financial | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | bank | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | corporate | 95 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| BS | total_assets | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | Energy:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | Financials:unclassified | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | Other:unclassified | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | Real Estate:unclassified | 7 | 42.9 | 42.9 | +0.0 | 0 | 0 |  |
| BS | total_debt | Utilities:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | bank | 13 | 23.1 | 23.1 | +0.0 | 0 | 0 |  |
| BS | total_debt | bdc_fund_or_unclassified | 6 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | corporate | 234 | 76.9 | 76.9 | +0.0 | 0 | 0 |  |
| BS | total_debt | energy | 12 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | total_debt | insurer | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | other_financial | 13 | 69.2 | 69.2 | +0.0 | 0 | 0 |  |
| BS | total_debt | reit | 8 | 12.5 | 12.5 | +0.0 | 0 | 0 |  |
| BS | total_debt | utility | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Utilities:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | corporate | 139 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| BS | total_liabilities | energy | 11 | 90.9 | 90.9 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | utility | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | Energy:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | capex | Financials:unclassified | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| CF | capex | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | Real Estate:unclassified | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | capex | bank | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | capex | bdc_fund_or_unclassified | 6 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | capex | corporate | 108 | 85.2 | 85.2 | +0.0 | 0 | 0 |  |
| CF | capex | energy | 12 | 41.7 | 41.7 | +0.0 | 0 | 0 |  |
| CF | capex | insurer | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | capex | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | other_financial | 11 | 72.7 | 72.7 | +0.0 | 0 | 0 |  |
| CF | capex | reit | 7 | 14.3 | 14.3 | +0.0 | 0 | 0 |  |
| CF | capex | utility | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | Financials:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | corporate | 101 | 98.0 | 98.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | reit | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | corporate | 100 | 97.0 | 97.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | reit | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | bank | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | corporate | 77 | 96.1 | 96.1 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | energy | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | other_financial | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | bank | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | corporate | 76 | 81.6 | 81.6 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | energy | 4 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | other_financial | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | corporate | 77 | 94.8 | 94.8 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | energy | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | other_financial | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | corporate | 99 | 97.0 | 97.0 | +0.0 | 0 | 0 |  |
| CF | cfo | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | cfo | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Energy:unclassified | 2 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Financials:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Real Estate:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Utilities:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | bank | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | bdc_fund_or_unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | corporate | 134 | 84.3 | 84.3 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | insurer | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | other_financial | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | reit | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | utility | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Energy:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Financials:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Other:unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Real Estate:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Utilities:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | bank | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | corporate | 187 | 94.1 | 94.1 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | energy | 8 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | other_financial | 13 | 84.6 | 84.6 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | utility | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Financials:unclassified | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Utilities:unclassified | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| CF | sbc | bank | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | bdc_fund_or_unclassified | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | sbc | corporate | 106 | 90.6 | 90.6 | +0.0 | 0 | 0 |  |
| CF | sbc | energy | 10 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | sbc | insurer | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | reit | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | sbc | utility | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Energy:unclassified | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Real Estate:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Utilities:unclassified | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | bank | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | bdc_fund_or_unclassified | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | corporate | 145 | 99.3 | 99.3 | +0.0 | 0 | 0 | Y |
| CF | share_buybacks | energy | 9 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | insurer | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | other_financial | 10 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | utility | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | Real Estate:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | basic_eps | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | corporate | 99 | 96.0 | 96.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | Financials:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | corporate | 74 | 94.6 | 94.6 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Real Estate:unclassified | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Utilities:unclassified | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | bank | 11 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | bdc_fund_or_unclassified | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | corporate | 131 | 87.8 | 87.8 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | energy | 10 | 70.0 | 70.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | other_financial | 11 | 72.7 | 72.7 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | reit | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | utility | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | corporate | 97 | 96.9 | 96.9 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | reit | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Energy:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Other:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Real Estate:unclassified | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Utilities:unclassified | 13 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | bank | 11 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | bdc_fund_or_unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | corporate | 176 | 95.5 | 95.5 | +0.0 | 0 | 0 |  |
| IS | gross_profit | energy | 16 | 93.8 | 93.8 | +0.0 | 0 | 0 |  |
| IS | gross_profit | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | other_financial | 15 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | reit | 10 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | utility | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Real Estate:unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | corporate | 97 | 90.7 | 90.7 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | energy | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | insurer | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | corporate | 97 | 96.9 | 96.9 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | no_revenue_line | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Other:unclassified | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Real Estate:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | bdc_fund_or_unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | corporate | 156 | 82.1 | 71.2 | -10.9 | 20 | 3 |  |
| IS | interest_expense | energy | 9 | 77.8 | 66.7 | -11.1 | 1 | 0 |  |
| IS | interest_expense | insurer | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | other_financial | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | utility | 5 | 60.0 | 20.0 | -40.0 | 2 | 0 |  |
| IS | net_income | Financials:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | net_income | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | corporate | 99 | 98.0 | 98.0 | +0.0 | 0 | 0 |  |
| IS | net_income | energy | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | net_income | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_interest_income | Financials:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_interest_income | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_interest_income | other_financial | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_expense | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_expense | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_income | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_income | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Energy:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Other:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Real Estate:unclassified | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Utilities:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | bdc_fund_or_unclassified | 8 | 37.5 | 37.5 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | corporate | 166 | 82.5 | 82.5 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | energy | 11 | 36.4 | 36.4 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | insurer | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | other_financial | 7 | 85.7 | 85.7 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | reit | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | utility | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| IS | operating_income | Financials:unclassified | 10 | 90.0 | 90.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | Real Estate:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | bank | 15 | 73.3 | 73.3 | +0.0 | 0 | 0 |  |
| IS | operating_income | bdc_fund_or_unclassified | 10 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | corporate | 119 | 99.2 | 99.2 | +0.0 | 0 | 0 | Y |
| IS | operating_income | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| IS | operating_income | insurer | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | other_financial | 9 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | operating_income | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | bank | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | corporate | 77 | 84.4 | 84.4 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | energy | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | utility | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | provision_for_credit_losses | bank | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Energy:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Other:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Real Estate:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Utilities:unclassified | 13 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | bank | 11 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | bdc_fund_or_unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | corporate | 182 | 88.5 | 88.5 | +0.0 | 0 | 0 |  |
| IS | research_and_development | energy | 16 | 81.2 | 81.2 | +0.0 | 0 | 0 |  |
| IS | research_and_development | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | other_financial | 14 | 85.7 | 85.7 | +0.0 | 0 | 0 |  |
| IS | research_and_development | reit | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | utility | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | Financials:unclassified | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | revenue | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | Real Estate:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | revenue | bank | 13 | 69.2 | 69.2 | +0.0 | 0 | 0 |  |
| IS | revenue | bdc_fund_or_unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | revenue | corporate | 101 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| IS | revenue | energy | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| IS | revenue | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | reit | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | utility | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Financials:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Real Estate:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Utilities:unclassified | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | bank | 15 | 86.7 | 86.7 | +0.0 | 0 | 0 |  |
| IS | sga_expense | bdc_fund_or_unclassified | 9 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | corporate | 140 | 98.6 | 98.6 | +0.0 | 0 | 0 |  |
| IS | sga_expense | energy | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| IS | sga_expense | insurer | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | other_financial | 10 | 90.0 | 90.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | reit | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | utility | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | total_interest_income | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | total_interest_income | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | bank | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | corporate | 71 | 81.7 | 81.7 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | other_financial | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | reit | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Energy:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Other:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Real Estate:unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Utilities:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | bank | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | bdc_fund_or_unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | corporate | 161 | 89.4 | 89.4 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | energy | 11 | 90.9 | 90.9 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | insurer | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | other_financial | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | reit | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | utility | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Financials:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | bank | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | corporate | 159 | 87.4 | 87.4 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | energy | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | insurer | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | reit | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | utility | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | Financials:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | Other:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | bank | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | corporate | 81 | 98.8 | 98.8 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | energy | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | reit | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | Financials:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | bdc_fund_or_unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | corporate | 82 | 72.0 | 72.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | reit | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Energy:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | bank | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | bdc_fund_or_unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | corporate | 128 | 93.8 | 93.8 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | other_financial | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | utility | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Energy:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Real Estate:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | bank | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | corporate | 125 | 93.6 | 93.6 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | energy | 8 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | other_financial | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | reit | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | utility | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
