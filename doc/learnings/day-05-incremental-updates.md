# Day 5 — Incremental Updates

## Addendum (post-close-out): a near-miss false finding, and a real doc gap

Reviewing what actually landed in `raw.sec_filing_documents` (559 rows, 26 distinct form types, only 10 companies over 2 days) against doc 07 §8's form-type table turned up two things:

**Real gap, fixed**: more than half those 26 form types (424B2-5, 144, FWP, 425, NT 10-Q, DEFA14A, EFFECT, ARS, POS EX, and the 13F/N-PX pair below) weren't in doc 07's catalogue at all. Added them, sourced from what was actually observed, not guessed.

**Near-miss**: 13F-HR/13F-NT/N-PX (institutional-manager filings) showed up for CIKs in `raw.company_universe` — JPMorgan Chase, GSK, ING Groep, and others. First instinct: this looks like a scope-boundary bug, fund/manager entities leaking into what should be pure equity issuers. Checked *which* companies before writing that up, instead of asserting it — every one of them is a real, obviously-legitimate equity issuer (a bank, insurer, or diversified financial) that's *also* an institutional investment manager under a separate SEC obligation, so filing both 10-K/10-Q (as issuer) and 13F/N-PX (as manager) is normal, correct behavior — not a bug, and not evidence `filings.py`'s scope filtering is wrong. If this hadn't been checked, it would have become a false "finding" in this exact log, undermining the point of keeping one.

### Why it matters going forward

A pattern that *looks* like a bug from one angle deserves the same live-data check as anything else before it gets written down as a finding — a plausible-sounding false conclusion in `doc/learnings/` is worse than no entry at all, since a future session would trust it without re-checking. Same discipline as everything else here, just applied to my own hypothesis instead of someone else's claim.

## Decision: how to test "a day after bootstrap" without waiting a day

Doc 08's exact acceptance text is "running it a day after bootstrap finds only genuinely new filings" — this session cannot literally wait 24 hours.

### Reasoning (stated explicitly, not silently assumed)

SEC's daily index is organized by calendar date and is immutable once published — a past date's index doesn't change after the fact. So "a day after bootstrap" isn't really about elapsed wall-clock time; it's about the mechanism correctly distinguishing "already indexed" from "not yet indexed." That's testable right now: run the same date's index twice. First run finds whatever's genuinely there; second run (nothing about that date changed) must find zero new. That's a real, live proxy for the actual property doc 08 cares about, not a simulation.

### Proof

`run_id=7` (golden 10 companies, date 2026-08-13): `new=106`. `run_id=8`, identical scope and date, run immediately after: `new=0, already_known=106`. `run_id=9`, same companies, a different date (2026-08-12): `new=61, already_known=0` — confirms the idempotency is genuinely date-scoped, not a blanket "ran once" flag that would also suppress a legitimately different day.

### Why it matters going forward

When an acceptance test is phrased in terms of elapsed time that can't fit in a session, don't skip the test or fake the passage of time — find the actual invariant the time-based phrasing is a proxy for, and test that invariant directly. Write down the reasoning, not just the result, since the next reader needs to know *why* this counts as proof, not just that it does.

## Problem: a remote agent's environment died mid-run, taking a live background job with it

A full-universe-scope incremental run (`run_id=10`, `ciks=ALL`) was genuinely in progress — heartbeat 21 seconds old when checked — when the remote agent's own execution environment failed (`Connection refused`). The background job died with it silently; heartbeat simply stopped advancing.

### How it was found

Checked `heartbeat_at` against current wall-clock time directly rather than assuming a recent-looking heartbeat meant the job was still healthy — the environment failure notification arrived separately from (and after) the last real heartbeat, so heartbeat freshness alone would have been misleading for a few minutes.

### Fix

None needed in code — `reap_stale_runs` handled this exactly as designed: reaped, marked `failed` (not deleted, not guessed `succeeded`) once genuinely stale. This is the mechanism doing its job on a real failure it wasn't specifically built for (Day 4 targeted process kills and dead connections; this was a whole remote environment disappearing) — evidence the design generalizes rather than only covering the one scenario it was built against.

### Why it matters going forward

A "recent heartbeat" is only reassuring at the instant you check it — a remote agent's entire environment can disappear between one heartbeat and the next with no warning signal other than the heartbeat simply going quiet. Don't treat "last heartbeat was recent" as "still running" without also checking whether the *agent itself* is still alive.

## Minor: a live recheck hit a tool-level timeout, not a code issue

A follow-up manual rerun (`run_id=11`, same golden-set/date as runs 7-8, meant as a third confidence check) was killed by the Bash tool's own timeout before completing. `ps` confirmed no process was actually left running afterward — genuinely dead, not orphaned. Reaped cleanly.

### Why it matters going forward

Not every incomplete run is a bug to chase — runs 7 and 8 already constituted complete, valid proof of the acceptance criterion before this happened. Re-proving an already-proven fact isn't worth burning more attempts against a flaky network; recognize when existing evidence is already sufficient rather than compulsively re-verifying.
