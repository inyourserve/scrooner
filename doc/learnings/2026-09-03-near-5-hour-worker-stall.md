# 2026-09-03 — A 4.9-hour worker stall, and a duplicate-watchdog lesson

## What happened

While investigating Priority 3/4 (period-alignment re-check, dividends deprioritization) alongside a running `accounts_receivable` full-population rollout, 8 `resolve-facts` workers went silently unresponsive for **~4.9 hours** (17,556+ seconds) — far longer than any hang previously documented this session (the worst prior case was ~16 minutes). Two independent watchdog Monitor instances (one intentionally armed this session, one left running from an earlier, forgotten `TaskStop` omission several hours before) both fired simultaneously and killed the same stuck PIDs, confirming a duplicate-watchdog situation had existed unnoticed for hours.

## Why this went unnoticed for so long

Between launching the rollout and noticing the stall, the session did real, valuable investigative work (re-checking `current_ratio`'s period alignment, sampling companies missing `dividends_paid`) that didn't require checking on the background job. No individual step was wrong, but the combined effect was going heads-down on analysis for long enough that a background job's actual health went unverified for hours at a stretch — the watchdog itself worked correctly (it killed the stuck workers the moment its own poll loop saw an age past the threshold), but a stall vastly longer than any prior one only got *noticed* when its kill notifications finally arrived, not proactively checked.

## What was verified before trusting the recovery

- `pg_stat_activity` showed no blocking locks and no long-running queries at the moment of discovery — this was a client-side hang (matching the already-documented "silent hangs" pattern in `pipeline/CLAUDE.md`), not a server-side problem.
- `apps/site` responded 200 throughout.
- Fresh workers picked up new batches immediately after the stuck ones were killed — `xargs -P` continued correctly, confirmed by batch count climbing (22→37) right after.
- Stopped the duplicate watchdog (`TaskStop` on the forgotten older instance) so only one remains armed going forward.

## Lesson

**A watchdog's own correctness ("it eventually kills stuck workers") is not the same as prompt detection — a threshold-based kill only helps once someone actually looks at its output.** Two generalizable takeaways: (1) before launching a new watchdog Monitor for a fresh background job, check whether an earlier one is still armed (`action`/task list, or just remember to `TaskStop` explicitly at the end of every job rather than assuming a later `TaskStop` call covered it) — a forgotten duplicate doesn't cause direct harm here (both watchdogs did the same correct thing), but it's a sign of poor bookkeeping that could cause real harm in a different shape. (2) When doing extended investigative work *while* a background job runs, a periodic explicit progress check (even just glancing at the batch counter) catches a stall proportionally faster than waiting for the watchdog's own notification — the watchdog is a safety net for the case no one is looking, not a substitute for looking.
