# Predictor backtest (2026-11-12T19:14:44Z)

Baseline `/tmp/claude-0/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/scratchpad/wt/data-team/tags/exam/tools/predict.py` (sha-07ae6421) vs candidate `/tmp/claude-0/-home-user-scrooner/e0c2c2bc-3f21-517b-a31a-2cd36f9600b5/scratchpad/cand/predict.py` (sha-7c0f604d). Verdict: **PASS**.

Tickers with keys 320; hand-verified key rows 6480 (excluded as not hand-verified 6658); compared 6346; set aside (key_error / key_unverified in either) 134.

Overall: baseline 88.2%, candidate 88.2%, right->wrong 0, wrong->right 0, net delta +0.

Key sources: origin/main b20da4d2; origin/work/reads/201-300 5d60d3fb; origin/work/reads/301-400 15210537; origin/work/reads/401-500 cea08276; origin/work/reads/501-600 e87d7686; origin/work/reads/601-700 24507f64; origin/work/reads/701-800 b9d77b9b; origin/work/reads/701-800-fsn-expert-handcheck c6664bd7; origin/work/reads/801-900 ec0885bc; origin/work/reads/901-1000 3b995909

Predictor runs without output: {'baseline': 2, 'candidate': 2}

## By statement

| Statement | n | Baseline | Candidate |
|---|---|---|---|
| BS | 1880 | 87.6% | 87.6% |
| CF | 1434 | 89.2% | 89.2% |
| IS | 2104 | 90.3% | 90.3% |
| NOTE-type | 928 | 83.1% | 83.1% |

## Data point x template group

| Stmt | Data point | Group | n | Baseline % | Candidate % | Delta pp | R->W | W->R | Graduated |
|---|---|---|---|---|---|---|---|---|---|
| BS | accounts_payable | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | Real Estate:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | bank | 13 | 84.6 | 84.6 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | bdc_fund_or_unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | corporate | 94 | 97.9 | 97.9 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | other_financial | 9 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | reit | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| BS | accounts_payable | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Energy:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Other:unclassified | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | Real Estate:unclassified | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | bank | 13 | 69.2 | 69.2 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | corporate | 99 | 85.9 | 85.9 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | energy | 4 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | other_financial | 10 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | accounts_receivable | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | Financials:unclassified | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | bank | 7 | 14.3 | 14.3 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | bdc_fund_or_unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | corporate | 88 | 95.5 | 95.5 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | other_financial | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | cash_and_equivalents | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | corporate | 87 | 98.9 | 98.9 | +0.0 | 0 | 0 |  |
| BS | current_assets | energy | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | insurer | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | other_financial | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | current_assets | reit | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_assets | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | corporate | 84 | 98.8 | 98.8 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | insurer | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | other_financial | 10 | 90.0 | 90.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | reit | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | current_liabilities | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | deposits | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | deposits | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Energy:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | Utilities:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | bank | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | bdc_fund_or_unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | corporate | 99 | 94.9 | 94.9 | +0.0 | 0 | 0 |  |
| BS | goodwill | energy | 11 | 81.8 | 81.8 | +0.0 | 0 | 0 |  |
| BS | goodwill | insurer | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | goodwill | other_financial | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | goodwill | reit | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | goodwill | utility | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Other:unclassified | 8 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | corporate | 115 | 94.8 | 94.8 | +0.0 | 0 | 0 |  |
| BS | inventory | energy | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | inventory | insurer | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| BS | inventory | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | other_financial | 12 | 91.7 | 91.7 | +0.0 | 0 | 0 |  |
| BS | inventory | reit | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | inventory | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | loans_net | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | loans_net | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | Other:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | bank | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | corporate | 94 | 85.1 | 85.1 | +0.0 | 0 | 0 |  |
| BS | ppe_net | energy | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| BS | ppe_net | insurer | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | other_financial | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| BS | ppe_net | reit | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | ppe_net | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Energy:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | bank | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | corporate | 84 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | energy | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | insurer | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | other_financial | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| BS | shares_outstanding | reit | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | corporate | 92 | 92.4 | 92.4 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | insurer | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | other_financial | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | stockholders_equity | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | bank | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | corporate | 86 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| BS | total_assets | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_assets | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | Energy:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | Other:unclassified | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | Real Estate:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | bank | 10 | 10.0 | 10.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | bdc_fund_or_unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| BS | total_debt | corporate | 146 | 69.2 | 69.2 | +0.0 | 0 | 0 |  |
| BS | total_debt | energy | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| BS | total_debt | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | other_financial | 10 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | reit | 4 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| BS | total_debt | utility | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | Utilities:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | corporate | 112 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| BS | total_liabilities | energy | 9 | 88.9 | 88.9 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | reit | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| BS | total_liabilities | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | Energy:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | capex | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | Real Estate:unclassified | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | capex | bank | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | capex | bdc_fund_or_unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | capex | corporate | 92 | 88.0 | 88.0 | +0.0 | 0 | 0 |  |
| CF | capex | energy | 7 | 57.1 | 57.1 | +0.0 | 0 | 0 |  |
| CF | capex | insurer | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | capex | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | capex | other_financial | 9 | 77.8 | 77.8 | +0.0 | 0 | 0 |  |
| CF | capex | reit | 4 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | capex | utility | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | corporate | 86 | 97.7 | 97.7 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_financing | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | corporate | 93 | 97.8 | 97.8 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cash_flow_investing | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | bank | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | corporate | 85 | 94.1 | 94.1 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | energy | 6 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | other_financial | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ap_change | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | bank | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | corporate | 84 | 82.1 | 82.1 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | energy | 5 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | other_financial | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_ar_change | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | corporate | 84 | 95.2 | 95.2 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | energy | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | other_financial | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cf_inventory_change | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | corporate | 85 | 96.5 | 96.5 | +0.0 | 0 | 0 |  |
| CF | cfo | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | cfo | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | cfo | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Energy:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Real Estate:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | Utilities:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | bank | 8 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | bdc_fund_or_unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | corporate | 104 | 80.8 | 80.8 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | energy | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | insurer | 5 | 20.0 | 20.0 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | other_financial | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | reit | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| CF | depreciation_and_amortization | utility | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Energy:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Other:unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | bank | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | corporate | 138 | 92.0 | 92.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | energy | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | other_financial | 11 | 81.8 | 81.8 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | dividends_paid | utility | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | bdc_fund_or_unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| CF | sbc | corporate | 90 | 90.0 | 90.0 | +0.0 | 0 | 0 |  |
| CF | sbc | energy | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | sbc | insurer | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | sbc | reit | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | sbc | utility | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Energy:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Real Estate:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | Utilities:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | bank | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | bdc_fund_or_unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | corporate | 112 | 99.1 | 99.1 | +0.0 | 0 | 0 | Y |
| CF | share_buybacks | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | insurer | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | other_financial | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | reit | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| CF | share_buybacks | utility | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | basic_eps | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | Real Estate:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | corporate | 88 | 96.6 | 96.6 | +0.0 | 0 | 0 |  |
| IS | basic_eps | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | basic_eps | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | Financials:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | corporate | 81 | 95.1 | 95.1 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | comprehensive_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Real Estate:unclassified | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | Utilities:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | bdc_fund_or_unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | corporate | 97 | 93.8 | 93.8 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | other_financial | 10 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | cost_of_revenue | utility | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | corporate | 88 | 97.7 | 97.7 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | diluted_eps | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Energy:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Other:unclassified | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Real Estate:unclassified | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | Utilities:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | corporate | 129 | 96.1 | 96.1 | +0.0 | 0 | 0 |  |
| IS | gross_profit | energy | 12 | 91.7 | 91.7 | +0.0 | 0 | 0 |  |
| IS | gross_profit | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | other_financial | 11 | 81.8 | 81.8 | +0.0 | 0 | 0 |  |
| IS | gross_profit | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | gross_profit | utility | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | Real Estate:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | corporate | 87 | 93.1 | 93.1 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | insurer | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_before_tax | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | Real Estate:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | corporate | 84 | 98.8 | 98.8 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | no_revenue_line | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | income_tax_expense | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Other:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | Real Estate:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | corporate | 104 | 78.8 | 78.8 | +0.0 | 0 | 0 |  |
| IS | interest_expense | energy | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | interest_expense | insurer | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | interest_expense | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | other_financial | 7 | 85.7 | 85.7 | +0.0 | 0 | 0 |  |
| IS | interest_expense | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | interest_expense | utility | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | net_income | Financials:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | net_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | bdc_fund_or_unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | corporate | 85 | 97.6 | 97.6 | +0.0 | 0 | 0 |  |
| IS | net_income | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | net_income | insurer | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_interest_income | Financials:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_interest_income | bank | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | net_interest_income | other_financial | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_expense | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_expense | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_income | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | noninterest_income | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Energy:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Financials:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Other:unclassified | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Real Estate:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | Utilities:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | bank | 13 | 61.5 | 61.5 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | bdc_fund_or_unclassified | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | corporate | 117 | 71.8 | 71.8 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | energy | 5 | 40.0 | 40.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | insurer | 4 | 25.0 | 25.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | other_financial | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | reit | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | operating_expenses | utility | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | Financials:unclassified | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | bank | 12 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | operating_income | bdc_fund_or_unclassified | 6 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | operating_income | corporate | 97 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| IS | operating_income | energy | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | other_financial | 8 | 62.5 | 62.5 | +0.0 | 0 | 0 |  |
| IS | operating_income | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | operating_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | bank | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | corporate | 84 | 85.7 | 85.7 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | other_income_expense_net | utility | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | provision_for_credit_losses | bank | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Energy:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Other:unclassified | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Real Estate:unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | Utilities:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | bank | 10 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | corporate | 132 | 94.7 | 94.7 | +0.0 | 0 | 0 |  |
| IS | research_and_development | energy | 11 | 81.8 | 81.8 | +0.0 | 0 | 0 |  |
| IS | research_and_development | insurer | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | other_financial | 12 | 91.7 | 91.7 | +0.0 | 0 | 0 |  |
| IS | research_and_development | reit | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | research_and_development | utility | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | Real Estate:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | revenue | bank | 10 | 70.0 | 70.0 | +0.0 | 0 | 0 |  |
| IS | revenue | bdc_fund_or_unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| IS | revenue | corporate | 87 | 100.0 | 100.0 | +0.0 | 0 | 0 | Y |
| IS | revenue | energy | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | revenue | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | reit | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | revenue | utility | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Other:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Real Estate:unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | Utilities:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | bank | 13 | 84.6 | 84.6 | +0.0 | 0 | 0 |  |
| IS | sga_expense | bdc_fund_or_unclassified | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | corporate | 98 | 94.9 | 94.9 | +0.0 | 0 | 0 |  |
| IS | sga_expense | energy | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | insurer | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | sga_expense | other_financial | 7 | 85.7 | 85.7 | +0.0 | 0 | 0 |  |
| IS | sga_expense | reit | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| IS | sga_expense | utility | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | total_interest_income | bank | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| IS | total_interest_income | other_financial | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | Other:unclassified | 2 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | bank | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | corporate | 87 | 69.0 | 69.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | energy | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | other_financial | 5 | 60.0 | 60.0 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | reit | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| NOTE-type | amortization_of_intangibles | utility | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Other:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Real Estate:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | Utilities:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | bank | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | bdc_fund_or_unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | corporate | 109 | 83.5 | 83.5 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | insurer | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | other_financial | 8 | 87.5 | 87.5 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | reit | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_income_taxes | utility | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Financials:unclassified | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | Real Estate:unclassified | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | bank | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | bdc_fund_or_unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | corporate | 116 | 83.6 | 83.6 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | energy | 7 | 71.4 | 71.4 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | insurer | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | no_revenue_line | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | other_financial | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | reit | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| NOTE-type | cash_paid_for_interest | utility | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | Financials:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | Other:unclassified | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | bank | 4 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | bdc_fund_or_unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | corporate | 88 | 97.7 | 97.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | energy | 6 | 83.3 | 83.3 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | reit | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | dividends_per_share | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | Financials:unclassified | 3 | 33.3 | 33.3 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | Other:unclassified | 2 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | bdc_fund_or_unclassified | 2 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | corporate | 90 | 68.9 | 68.9 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | energy | 6 | 50.0 | 50.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | insurer | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | other_financial | 5 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | reit | 3 | 66.7 | 66.7 | +0.0 | 0 | 0 |  |
| NOTE-type | interest_income | utility | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | bank | 6 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | corporate | 98 | 89.8 | 89.8 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | energy | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | insurer | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_basic_shares | utility | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Energy:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Financials:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Other:unclassified | 3 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | Real Estate:unclassified | 1 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | bank | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | corporate | 97 | 89.7 | 89.7 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | energy | 5 | 80.0 | 80.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | insurer | 4 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | other_financial | 7 | 100.0 | 100.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | reit | 4 | 75.0 | 75.0 | +0.0 | 0 | 0 |  |
| NOTE-type | weighted_diluted_shares | utility | 1 | 0.0 | 0.0 | +0.0 | 0 | 0 |  |
