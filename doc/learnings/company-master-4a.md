# Company Master 4a — Identity Completion

## A proxy signal that worked for the case it was designed around, and failed everywhere else

The plan (doc 13) proposed proxying a ticker's `effective_from` from the nearest name-change date whenever no forward-observed change exists — reasoning from one real, verified case: Block/Square's ticker change (SQ→XYZ) and name change (Square, Inc. → Block, Inc.) both landed in the same corporate action in December 2021, confirmed against EDGAR's own `formerNames` dates. Built and run against the full golden-10 before trusting it, and the result was decisive: **27 of 38 listing rows came back with a wrong or misleading date.** AAPL and NKE — neither of which has ever changed its ticker — both got a plausible-looking `effective_from` from unrelated real renames (AAPL dropped "Computer" from its name in 2007, then normalized capitalization in 2019; neither corresponded to a ticker change). RDDT and JPM got proxied to the exact date of an EDGAR data artifact (see below), not any real event at all.

The lesson isn't "the proxy is wrong" — it's real evidence for Block. The lesson is that **a signal verified correct for one case is not evidence it generalizes**, and the only way to find out is to run it against every case available and check, not to reason from the one case it was designed to explain. Fixed by keeping the detection (compute and log the candidate date for every company) but requiring explicit, reviewed confirmation before applying it — a small, hardcoded `CONFIRMED_TICKER_PROXY_CIKS` allowlist, currently just Block. This is the same shape as Mapper's `approved`/`provisional`/`rejected` `concept_mapping` states (doc 11): automate ranking/detection, keep acceptance human and explicit, especially anywhere a wrong answer would look plausible rather than obviously broken.

## A second, independent EDGAR data-quality finding, needed for the same fix

While building the proxy, found that RDDT's and JPM's `formerNames` arrays each end with an entry whose name is byte-for-byte identical to the company's current name, dated up to what looks like the data's own fetch/generation timestamp — not a real rename, an artifact of how EDGAR (or this environment's data) represents the boundary of the "current" name interval. Caught by comparing the parsed history against the real company facts directly (I know RDDT hasn't renamed since its 2024 IPO) rather than trusting the payload's shape at face value. Fixed with an exact-string-equality filter against the current name before any row reaches `core.company_name_history` — a small, targeted fix, but one that would have silently corrupted both the name-history table and (before the proxy fix above) the ticker-dating logic for two golden companies if left unchecked.

## A second idempotency bug, same root cause as ones this project has hit before

`ON CONFLICT (company_id, company_name, effective_from)` looked like a reasonable dedup key. It silently doesn't work when `effective_from` is `NULL` — SQL's `NULL ≠ NULL` means the constraint never matches, so `ON CONFLICT` never fires, and a rerun just inserts a second copy. Every company with no former-names history at all (MSFT, TSM, ARCC, GOOGL, RDDT) has exactly this shape: one row, current name, `effective_from=NULL`. Found by doing what this project now does by default — rerun the stage and diff the row counts, don't assume idempotency from reading the upsert clause. 19 rows became 24 on the first rerun. Fixed by switching to delete-then-reinsert per company, the exact pattern Mapper's `resolve.py` and (after its own Day 6 fix) `calculate.py` already use for this same class of problem: a composite `ON CONFLICT` key with any nullable column is a standing risk, not a one-off mistake, and delete-then-reinsert sidesteps it entirely rather than requiring a `COALESCE`-a-sentinel workaround.

## Why it matters going forward

Two lessons worth carrying into 4b and beyond, not just this stage: (1) a plan-stage design idea grounded in one real, verified case still needs to be checked against the *whole* target set before being trusted as a default — one confirming example is not the same evidence as a clean sweep across ten. (2) any `ON CONFLICT` clause built on a composite key needs an explicit check for whether any key column can be `NULL` — if so, either delete-then-reinsert (this project's now-established default for exactly this reason) or an explicit `COALESCE` sentinel, never an unexamined assumption that the constraint will fire.

## Verification summary

- 10/10 golden companies got SIC/entity-metadata fields, sourced entirely from already-stored data, zero new SEC fetches.
- 19 `core.company_name_history` rows, confirmed exact against EDGAR's own `formerNames` for Block and AAPL; 2 real EDGAR-artifact rows correctly filtered out (RDDT, JPM).
- 38 `core.listing` rows dated: 2 correctly proxied (Block, independently verified), 36 honestly `unknown` — down from an incorrect 27 `former_names_backfill` on first attempt.
- All 10 companies correctly `active`, each `status_reason` traceable to a real `core.filing.filing_date`.
- Reran all three stages twice; confirmed byte-for-byte identical row counts on the second attempt, after fixing the `NULL`-conflict-target bug found on the first.
