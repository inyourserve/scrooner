# Tag Mapper coexistence results (2026-10-19) - PARTIAL, BLOCKED ON DB LOAD

Role: Tag Mapper (13). Scope: checks designed in file 27 (I-1/I-2, D-1/D-2/D-6, Q-D3b, Q-D2). Read-only. No DB writes, no code edits, no mappings applied.

## Verdicts so far
No check has completed. There is NO eligibility evidence yet for any tag. Every tag keeps the status file 27 gave it, and "ELIGIBLE" in file 27 means only "may go to checks". Do not apply any mapping on the strength of this file.

| Tag | Verdict from my runs | Cells it would fill |
|---|---|---|
| InterestExpenseNonoperating | NOT_RUN | unknown |
| NotesPayable / SeniorNotes / SubordinatedDebt (F1) | NOT_RUN | unknown |
| Q-D3b zero-debt audit | NOT_RUN | wrong zeros found: unknown (0 examined) |
| Q-D2 SG&A | NOT_RUN | unknown |

## What was done
- Read data-team 20, 21, 22, 13, 27 and parts of `mapper/concept_fallback.py` (`compute_total_debt`, lines 50-103, 300-470).
- Confirmed all candidate tags exist in `analytics.sec_tag_library` (us-gaap): NotesPayable 996 companies (unmapped), NotesPayableCurrent 1202, LongTermNotesPayable 756, LongTermLineOfCredit 421, SeniorNotes 328, SubordinatedDebt 254, AdvancesFromFederalHomeLoanBanks 240, InterestExpenseNonoperating 2017 (candidate), InterestExpenseOperating 538, InterestExpense 3627 (approved), InterestExpenseDebt 1416, InterestIncomeExpenseNonoperatingNet 1048 (approved), InterestCostsIncurred 211, DebtInstrumentCarryingAmount 2021, UnamortizedDebtIssuanceExpense 714, SellingGeneralAndAdministrativeExpense 2057 (approved). Library snapshot as read 2026-10-19.
- Pre-check at start: 9-10 connections, no active query older than 10 min, `default_transaction_read_only` = off. Proceeded.
- First debt scan (Q-BASE-style, chunk 1 = companies 1..~250, `begin read only`, `set local statement_timeout='5min'`) hit the 5-minute timeout. Cause: the query filters by tag text through a join to `core.concept` for about 110 tags and joins `core.filing`. Fix for the rerun, not yet tested: resolve concept ids first and filter `f.concept_id = any(ids)`, and use chunks of about 100 companies. This is a query-design finding, not a data finding.
- After that, the guard stopped every further run: connections stayed at 11-14 (limit 10) and active queries from other sessions reached 278 s while I polled for about 15 minutes (30 polls, 30 s apart). A different session was running something heavy throughout. I did not override the stop rule.

## Scripts (scratchpad, ready to rerun)
`/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/tm/lib.py` (guard, chunking, read-only helper), `debt.py` (D-1..D-6 and Q-D3b in one pass; imports the real `compute_total_debt` to test "existing path returns None"), `ex.py` (index/plan probe, never ran past the guard). Interest (Q-I) and Q-D2 scripts are not written yet.

## Untested scope
Everything: I-1..I-5, D-1..D-6, Q-D3b, Q-D2, Q-C. Wrong zeros: none examined.

## Next action / unblock
Run when `select count(*) from pg_stat_activity` is at most 10 and no peer query is older than 10 minutes (ask the peer running the heavy job, now unidentified because I cannot call ListAgents, to finish). Then: patch `debt.py` to prefilter by concept id and use 100-company chunks, run it, then write and run the interest script, then Q-D2. Estimated runtime once load is low: 20-40 minutes for debt.
