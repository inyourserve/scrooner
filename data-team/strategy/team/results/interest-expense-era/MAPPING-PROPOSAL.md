# Mapping proposal: interest_expense from the 2024+ taxonomy tags (rule interest_expense.era_tag_fill@1)

Preparer: scrooner-26 (per-share lane). Approver requested: Ritwik (scrooner-31), named by Dhairya 2026-11-02. Not a new definition: the same concept (gross interest expense) under tags that only exist from the us-gaap 2024 taxonomy.

## What is asked
Approve, for the canonical concept `interest_expense` (and its `interest_expense_resolved` twin):
- `us-gaap:InterestExpenseNonoperating` for non-banks, and `us-gaap:InterestExpenseOperating` for banks (SIC 6021/6022/6029/6035/6036),
- used ONLY for a period with no `InterestExpense` fact (the existing approved mapping, `InterestExpense` p1 / `InterestExpenseDebt` p2, is untouched and still wins),
- and only for a cell that passes every guard below. Every other cell stays blank with its hold reason.

Not asked: `InterestExpenseOperating` for non-banks (operating component; held), any net-perimeter line, `InterestAndDebtExpense`.

## Why (tag card `data-team/tags/cards/interest.md`, FILING-CHECKED there)
Both tags first appear in the us-gaap 2024 schema (absent in 2015/2019/2022/2023). Filers on the 2024+ taxonomy (Colgate, Avery Dennison, EFSC, ...) moved their gross interest line to them, so `interest_expense` goes blank from about FY2024.

## Guards (per cell)
1. Same company, same tag: the new tag equals `InterestExpense` within rounding (0.5% or one printed unit) in every period where both are filed, OR the cell's own income statement presents the fact on a plain "(Total) interest expense" line.
2. Label on the filer's own income statement (FSN pre) is gross: not "net", not "interest income/expense" (282 + 9 held), "net of capitalized interest" counts as gross.
3. Value > 0 (sign trap ANDE/BBW in the card).
4. Copies of the fact agree; source is an authoritative, non-derived 10-K/10-Q fact; cells are 3- or 12-month periods ending 2015-01-01 or later.

## Evidence (cohort v1.1, read-only, 2026-10-31/11-02)
- Coexistence in shared periods: IEN = IE 2,499 of 2,715; bank IEO = IE 254 of 260; non-bank IEO = IE 268 of 290. Differences: rounding vintage, sign, component perimeter (company 646 IEO is about 60% of IE). File: `coexistence_cohort.json`.
- Plan: 3,968 blank cells at 494 companies -> fill 2,606 (347 companies) / hold 1,362 (net label 291, no overlap 305, non-bank IEO 268, not on face 173, label unread 130, perimeter 119, sign 76). Every count has a cell list: `SUMMARY_COUNTS_TO_CELL_LISTS.json`.
- Verifier: verify/interest-expense-era-2026-11-02, 12 of 12 fills right. The 328 cells released by guard 1's face clause after that draw use a face-equality rule the Verifier already verified (Dhairya 2026-11-02: no new draw); 9 earlier fills were moved to hold by the tightened net-label check ("INTEREST EXPENSENET"). Diff: `changed_fills_vs_release1_425842.csv`.

## After approval
Write package `release-1/` (digest af73066ec27c5733fe99d000f40c04a391f868207e356fc26f6c2f7bf7e67479; module `mapper/interest_expense_era_release.py`; flag default OFF; stale cells refuse the run; restore by run id). The production write needs the founder's typed words. Durable form: the nightly rebuild must honour the rule (concept_mapping alone would map the held cells too); until then a nightly can remove the written rows.
