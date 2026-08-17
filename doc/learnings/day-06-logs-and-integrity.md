# Day 6 — Logs and Integrity Reconciliation

## Decision: exhaustive hash re-verification, not sampled — for now

`scrooner-report reconcile` re-downloads and re-hashes every stored object by default (`--hash-sample-rate 1.0`), rather than sampling. Existence-checking is always exhaustive regardless (cheap — a metadata call per object, not a download).

### Reasoning

At current volume (364 objects, a few hundred MB total) exhaustive re-verification is simple, fast enough (~12 minutes end to end, including network round-trips to Storage), and gives an unambiguous answer — no sampling-confidence caveat to reason about. The tool already has a `--hash-sample-rate` knob for when that stops being true (a full 8,000-company universe will have vastly more objects), so the KISS choice now doesn't paint the tool into a corner later — it's a flag flip, not a rewrite, when volume actually demands it.

### Why it matters going forward

"Good enough for current scale, with an explicit escape hatch already built in" beats either premature sampling-complexity now or a hardcoded exhaustive-only design that becomes a problem later. The right time to switch the default is when reconcile's own runtime becomes a real operational cost, not before.

## Verified for real, not asserted

Ran `scrooner-report reconcile` against the actual accumulated data from Days 1-6 (not a synthetic fixture): 186 `sec_companyfacts` + 178 `sec_submissions` = 364 objects with a `storage_path`. Result: 364/364 exist in Storage, 364/364 re-hash to their recorded `sha256`, zero mismatches, zero check failures. Exit code 0 (the tool exits 1 on any real delta, so this is a genuine pass/fail signal, not just printed text). Per-run breakdown ties results back to specific `run_id`s, confirming the reconciliation is attributable, not just an aggregate count.

`collector/logs.py`'s `runs`/`run` commands independently verified against DB state already directly queried all session — matched exactly, including correctly surfacing the Day 4 `NotInBulkArchive` errors under the right run.

## Minor process note: an accidental duplicate process

Two `scrooner-report reconcile` invocations ended up running concurrently (7 minutes apart) during manual testing — not a code bug, just an artifact of re-running a foreground-then-backgrounded command without confirming the first had actually been cleared. Harmless here since `reconcile` is read-only, but killed the stray one before trusting the final result, to keep the evidence trail to a single unambiguous run.

### Why it matters going forward

Read-only tools tolerate accidental concurrent runs; anything that writes (bootstrap/incremental) would not — worth remembering before assuming "just run it again" is always free.

## Problem: a remote agent kept running for ~1 hour after its work was already done and independently verified

The Day 6 build agent's actual contribution (`logs.py`, `integrity.py`) was complete and verified early on. But the agent itself didn't stop — it kept generating "waiting for the next monitor notification" reports, one after another, for roughly an hour, apparently having launched extra `reconcile` runs of its own (a stray local `reconcile_run2.log` process was found and killed separately) and then just... continuing to wait on something that was never going to resolve.

### How it was found

Repeated identical-looking completion notifications from the same task-id were initially (correctly, for the first few) treated as harmless stale replay. What actually exposed it as a *live, still-running* problem rather than replay: `tool_uses` and `subagent_tokens` kept climbing across the repeats (104 → 108 → ... → 170 tool uses). A `TaskStop` call at one point reported "not running (status: completed)" — misleading — but `ListAgents` moments later showed it as genuinely `status: running`. Ground truth came from `ListAgents`, not from trusting either a single notification's `status` field or a single `TaskStop` response.

### Fix

`TaskStop` on the confirmed-running task-id actually ended it (notification came back `status: killed`). A prior `SendMessage` telling it to stop had already been sent and queued, but evidently didn't interrupt whatever loop the agent was stuck in — a polite stop message is not the same as confirmation of a stop.

### Why it matters going forward

Verifying a day is done is necessary but not sufficient for closing out a remote agent — the agent itself can keep running (and costing real money/tokens) well past the point its output stopped mattering. Don't assume "I told it to stop" means it stopped. The concrete signal to watch for: if the same task-id keeps notifying and the usage numbers keep climbing, it's alive; check `ListAgents` to confirm, then `TaskStop` it directly rather than waiting or re-messaging. Encoded into the `run-collector-day` skill's close-out step so this is standing procedure from Day 7 onward, not something to rediscover.
