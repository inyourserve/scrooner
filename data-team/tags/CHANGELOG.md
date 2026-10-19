# Tag knowledge base changelog and calibration

Every Tag Expert run adds an entry: what was added, what was CORRECTED (and what was wrong before, and what caught it), and what was learned about the process. This is the self-correction record; a card claim later contradicted by a filing or the Verifier is logged here with the cause, so the same type of mistake is checked for earlier next time.

## Calibration (update every run)
| Metric | Value | As of |
|---|---|---|
| Cards written | 6 families (revenue, operating-income, interest, debt, cash, net-income-and-shares) | 2026-10-19 |
| Card claims later contradicted by a filing or the Verifier | 0 | 2026-10-19 |
| Inbox lines processed / total | 14 / 15 (1 left `new`: PaymentsForRepurchaseOfEquity, outside the six families); 5 Data Chief lines folded as relayed evidence, not re-opened | 2026-10-19 |

## Runs
- 2026-10-19: knowledge base seeded by Dhairya from proven cases (company-quirks.md, INDEX.md).
- 2026-10-19 (Tag Expert, sources run): wrote `sources.md` (11 ranked sources, 1 excluded, trust tests on 5 known cases, first pulls for 5 key tags from FASB 2026, FSDS 2025q4 and SEC Frames, and the design of a yearly taxonomy diff job). Corrections to cards: none (no cards existed during this run); 9 inbox lines added, 0 of which contradict a seeded claim. They narrow scope: InterestIncomeExpenseNet is safe for banks only; InterestRevenueExpenseNet is not an exact synonym (refines data-team/32). Source calibration: FASB taxonomy 5/5 consistent; FSDS 5/5; Frames 7/7 values, labels out of date; edgartools 2/8; OpenBB 1/4; FAC port checks 1/1, imputation 0/2. Process lesson: an official definition can be right while filers break it (CostsAndExpenses, bank Revenues), so a card must never infer usage from the definition; it needs FSDS labels or the filer's own calculation linkbase plus a filing. DB step skipped (16 connections > 12).
- 2026-10-19 (Tag Expert, first card run): ADDED cards/revenue.md, operating-income.md, interest.md, debt.md, cash.md, net-income-and-shares.md; INDEX.md and company-quirks.md extended; 7 ledger rows appended to 22. Evidence: taxonomy 2025 text and period/balance for ~110 tags; 132 SEC Frames pulls (CY2013 and CY2023); about 20 filing R-files opened by me. DB reads skipped every time (pg_stat_activity 14-18, limit 12), so SIC-family splits and `analytics.sec_tag_library` counts are missing; "bank-like = also files NoninterestExpense" is a Frames proxy, not an SIC split.
  - Leads closed: Citigroup `Revenues` = net revenue (CONFIRMED, R2); Flushing `InvestmentIncomeInterest` = securities interest line only, NOT total interest income (CONFIRMED as a securities line; the "possible total" reading is rejected).
  - CORRECTED (my own, before publishing): (1) first draft of interest.md said "five meanings across seven banks"; the real count is three (securities line, total interest income, NII itself). Cause: counted banks, not meanings. (2) debt.md first said 85+57 SubordinatedDebt/FHLB filers overlap LongTermDebt; actual overlaps are 46 and 57 (85 belongs to LongTermLineOfCredit). Cause: read the wrong row of the overlap table. (3) I first guessed a tag name `WeightedAverageNumberOfSharesOutstandingBasicAndDiluted` that does not exist; the real one is `...NumberOfShareOutstanding...` (singular). (4) I first marked all 15 inbox lines processed with a blanket replace, including 5 Data Chief lines I had not read; reverted and processed them properly.
  - Calibration: 0 earlier card claims contradicted; 4 self-corrections caught before publish, all by re-reading the source table.
  - Routine change: never bulk-edit inbox status; compute every cross-tab count from a script and paste the output rather than re-typing it; check tag names against the taxonomy file before using them in a Frames pull.

