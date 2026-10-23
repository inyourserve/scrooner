# RF-13 hidden-correct sample (2026-10-23): NOT RUN, stopped on the connection limit

Status: STOPPED before any frame or sample was drawn. No hidden-correct count exists yet.

## Why stopped
The data chief's added rule required `select count(*) from pg_stat_activity` to show 12 client backends or fewer in total (team limit 14) before each batch of queries. Measured 2026-10-23 (DATA-INFERRED): `count(*) filter (where backend_type='client backend')` = 18, total backends = 26. That is over the limit, so I ran no frame query and drew no sample.

## What was done
- Read the worker brief and the RF-13 description. RF-13 is in `data-team/strategy/FREEZE-REGISTER-2026-10-22.md` row RF-13 and in `data-team/strategy/team/RULE-REGISTRY-DRAFT-2026-10-22.md`. The draft registry and `NA-DEFINITIONS-AND-FOUNDER-SHEET-2026-10-22.md` name the guard `revenue.total_disagreement@1`; I did not read their definitions of the revenue-family tag list.
- Built the company frame from `doc/data-moat/team/top1000/shards.csv`: 1,014 rows, 986 not excluded, 842 after dropping SIC 6000-6411 (my bank/financial rule: banks and credit, brokers, insurers; REITs and real estate at 6500+ stay in). The id list is in `/private/tmp/claude-501/scratch-RF13/ids.txt`. FILING-CHECKED: none. DATA-INFERRED: the counts above.
- One exploratory read for AAPL (company_id 3) showed `core.fact` holds the 606 tag `RevenueFromContractWithCustomerExcludingAssessedTax` with `fiscal_period` FY/Q1-Q4, so a per-company-period frame is feasible in SQL.

## Planned method (not executed)
- Frame: for each of the 842 companies, in chunks of 10 company_ids, take the latest FY period and select the periods where two or more revenue-family tags are filed and no pair is within 1%. Tags: Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, RegulatedAndUnregulatedOperatingRevenue. Goods/Services component tags excluded because they would trigger falsely. This tag list is my assumption.
- Sample: Python `random.seed(20261023)`, 40 triggered periods.
- Verify: `headline.py` / `sec_rpages.py` on each sampled filing's income statement.
- Cost: about 85 frame queries, which is near the ~100 cap.

## Resume
Rerun once client backends are at or below 12. Record the exact frame query text here so the Verifier can reproduce it.
