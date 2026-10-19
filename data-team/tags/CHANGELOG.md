# Tag knowledge base changelog and calibration

Every Tag Expert run adds an entry: what was added, what was CORRECTED (and what was wrong before, and what caught it), and what was learned about the process. This is the self-correction record; a card claim later contradicted by a filing or the Verifier is logged here with the cause, so the same type of mistake is checked for earlier next time.

## Calibration (update every run)
| Metric | Value | As of |
|---|---|---|
| Cards written | 0 (seed only) | 2026-10-19 |
| Card claims later contradicted by a filing or the Verifier | 0 | 2026-10-19 |
| Inbox lines processed / total | 1 / 1 | 2026-10-19 |

## Runs
- 2026-10-19: knowledge base seeded by Dhairya from proven cases (company-quirks.md, INDEX.md).
- 2026-10-19 (Tag Expert, sources run): wrote `sources.md` (11 ranked sources, 1 excluded, trust tests on 5 known cases, first pulls for 5 key tags from FASB 2026, FSDS 2025q4 and SEC Frames, and the design of a yearly taxonomy diff job). Corrections to cards: none (no cards existed during this run); 9 inbox lines added, 0 of which contradict a seeded claim. They narrow scope: InterestIncomeExpenseNet is safe for banks only; InterestRevenueExpenseNet is not an exact synonym (refines data-team/32). Source calibration: FASB taxonomy 5/5 consistent; FSDS 5/5; Frames 7/7 values, labels out of date; edgartools 2/8; OpenBB 1/4; FAC port checks 1/1, imputation 0/2. Process lesson: an official definition can be right while filers break it (CostsAndExpenses, bank Revenues), so a card must never infer usage from the definition; it needs FSDS labels or the filer's own calculation linkbase plus a filing. DB step skipped (16 connections > 12).
