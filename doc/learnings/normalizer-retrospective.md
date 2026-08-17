# Normalizer Retrospective — Gaps Found on Re-Read

Not a day entry (there is no Day 8 — the Normalizer finished at Day 7, see `doc/09b_Normalizer_Definition_of_Done_Evidence.md`). This is a look back across all 7 day files for patterns that were real, validated, and worth keeping — but that only ever got written into one day's narrative instead of being promoted to a project-level rule the way Days 1–6's findings were (doc 05's build method, doc 04's correctness controls, CLAUDE.md's Mapper notes). Two gaps found; both fixed as part of this entry.

## Gap 1: "load everything, batch the writes" was never promoted, despite causing a real production-relevant bug

Day 7's own entry documents the incident: `derive_q4_for_company`'s first version made several individual round-trip queries per candidate group, and JPM alone has 3,704 groups — real `SSL SYSCALL... Operation timed out` errors resulted, twice, before the fix (load all lookups into memory up front, two batched `executemany` writes) brought a full golden-8 run from repeatedly timing out to under a minute.

The pattern itself — `identity.py`, `periods.py`, `units.py`, and `facts.py` all *already* did this correctly from Day 1 onward — was proven right five times before `derived.py` deviated from it and paid for that deviation directly. But the "why" only ever got written into Day 7's own file ("worth checking new Normalizer/Mapper code against the established shape"). Nothing forced a future session — building Mapper, which will do similar per-company/per-concept aggregation at potentially larger scale — to see that rule before making the same mistake a second time.

**Fixed:** promoted to doc 04's correctness controls (see below) and CLAUDE.md's Mapper notes, next to the existing `is_authoritative`/Decimal rules from the same review pass.

## Gap 2: "a clean or zero-looking result needs the same scrutiny as a surprising one" was stated once, never generalized

Day 6's "why it matters" section says it directly: three different companies (MSFT, NKE, GOOGL) produced `superseded_pairs=0`, for three completely different legitimate reasons, and none of them would have been distinguishable from an actual bug without checking the underlying accession-level data. Day 4 did the same thing in miniature (verifying the 8,986-skip count matched a pre-computed expectation exactly, rather than trusting a plausible-looking number).

This is a distinct lesson from "inspect real payloads before finalizing schema" (which doc 05's build method now covers) — it's about **trusting your own pipeline's output**, not the source data's shape. A confident, clean-looking zero is exactly as capable of hiding a broken join as a messy nonzero number is of hiding real data — and is actually *more* dangerous, because "it ran and produced 0 conflicts / 0 superseded pairs / 0 skips" reads as good news, which lowers the instinct to double-check it. This never got written into doc 05 or CLAUDE.md alongside the payload-verification rule it directly complements — it only lived in one day's own retrospective paragraph.

**Fixed:** added to doc 05's data-quality methodology and CLAUDE.md.

## Also worth naming, lower priority: Supabase connection flakiness became a recurring theme, never turned into a runbook

Day 7 alone hit three distinct connection incidents: two SSL timeouts (root-caused and fixed, see Gap 1), then a multi-minute silent hang on an idempotency-check rerun with no error at all (resolved by stopping the task, checking `pg_stat_activity` for blocking locks — found none — and retrying cleanly). Doc 05's documentation methodology table has a "Runbooks" row for exactly this kind of repeatable operational response, but no runbook doc exists yet, and three incidents in one day is close to but not quite the "2-3 real repeats" bar this project uses before scaffolding new infrastructure (per doc 05's own "evidence before expansion" and the precedent set by `verify-collector-day`/`run-collector-day` only getting built after repeated real need).

**Not building a runbook doc yet** — that would be scaffolding ahead of proven need, the exact thing this project's methodology warns against. Instead, added a short operational note to `pipeline/CLAUDE.md` (the natural home, since it's Postgres/Supabase-specific) capturing the concrete diagnostic step that actually worked: when a DB-heavy job hangs with no error, check `pg_stat_activity` for blocking locks before assuming it's a repeat of a previously-fixed root cause, and don't hesitate to stop and retry once — this session's hang and the earlier SSL timeouts turned out to be unrelated causes that looked identical from the outside. If this recurs 1-2 more times during Mapper work, that's the trigger to promote it into an actual runbook.

## Why this retrospective itself matters

Every prior day's "why it matters" section was written looking forward from that day alone, not against the accumulated set of prior days — so a lesson stated once in Day 6's file had no mechanism forcing it to be cross-checked against what Day 1-5 already established, or promoted if it turned out to generalize. A single retrospective pass after a phase completes (not after every day — that would be premature, the pattern needs to have actually shown up before promoting it) is a cheap, one-time check for exactly this kind of gap. Worth repeating after Mapper finishes, not after every one of its own days.
