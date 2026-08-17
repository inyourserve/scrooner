# Day 4 — Retry, Checkpoint/Resume

## Problem 1: a remote agent's incomplete work looked complete twice more

A remote/cloud agent was launched for Day 4 (same pattern as Day 3). It built real, substantial code (`collector/retry.py`, migration `0002_checkpoint_and_run_tracking.sql`, wiring into `companyfacts.py`/`submissions.py`/`jobs/bootstrap.py`) and made genuine progress — it even fixed the historical Day 3 stuck-run row. But it hit an API session limit mid-"final verification pass" and never invoked `verify-collector-day` or wrote this file. Its last message ("run succeeded... let's do the final verification pass") looked like a natural stopping point, not a failure.

### How it was found

Checking `doc/learnings/day-04-retry-and-resume.md` for existence (it didn't exist) and the live `raw.collector_runs` table directly, rather than trusting that a plausible-sounding final message meant the work was done. Exactly the `run-collector-day` skill's own rule, applied to itself.

### Fix / decision

Took over verification directly instead of resuming the (session-limited) agent further. All of Problems 2-5 below were found during that direct verification, not by the agent.

### Why it matters going forward

A cut-off agent's last message can sound like a natural conclusion even when the actual required steps (verify, document) never happened. "Sounds finished" is not evidence, same as "status: completed" wasn't on Day 3 — just a different disguise for the same problem.

## Problem 2: silent data loss when a requested CIK isn't in the bulk archive

`companyfacts.py`/`submissions.py` only counted/logged a CIK if it was both requested (`only_ciks`) and physically present in the bulk zip. A requested CIK genuinely absent from the archive was invisible — not counted, not logged, no error row — while the run still reported `errors: 0` and closed out `succeeded`.

### How it was found

Testing the fix with `--ciks 0000018748,0000023426,0000320193`: `considered` came back as 147 in an earlier full-batch run against a 149-CIK params_key, with the 2 missing CIKs (`0000018748`, `0000023426`) having zero trace anywhere in `sec_companyfacts`, including no error row. Found by directly diffing the params_key's CIK list against what was actually stored — not by reading the run's own reported stats, which looked clean.

### Fix

Both `bootstrap_companyfacts` and `bootstrap_submissions` now track `seen_ciks` during the archive scan, then explicitly compute `only_ciks - seen_ciks` afterward and record each as a `not_in_archive` stat plus a `raw.collector_errors` row (`error_type='NotInBulkArchive'`). Confirmed the 2 CIKs are genuinely absent from SEC's real archive (not a parsing bug) via an HTTP Range request against the zip's central directory — no need to download the whole 1.4GB to check membership.

### Why it matters going forward

"Zero errors reported" is not the same as "nothing went wrong" — it can mean "nothing that was checked for went wrong." Any filter based on a caller-supplied allowlist (`only_ciks` here) needs an explicit accounting of what *didn't* match, not just silence about it.

## Problem 3: full 1.4GB re-download on every invocation, including resume

Every call to `companyfacts`/`submissions` re-downloaded the entire bulk zip from scratch, even a *resumed* run continuing an interrupted invocation, and even a test run scoped to 2 CIKs. This defeats the point of Day 4: a killed run should resume cheaply, not re-pay the full download cost.

### How it was found

Pointed out directly — re-downloading a 1.4GB file just to re-test a 2-CIK fix was visibly wasteful in real time, not found through instrumentation.

### Fix

`SECClient.get_cached_bulk_zip()` — caches the downloaded zip locally, keyed by date (`companyfacts-YYYY-MM-DD.zip`), since SEC recompiles these nightly (doc 07 §5) so a same-day cache hit is exactly as fresh as a new download. Correctness never depends on the cache — it's purely a bandwidth optimization underneath the existing `(job, params_key)` checkpoint logic, which still governs what actually gets skipped.

### Why it matters going forward

An inefficiency that's merely annoying during a full bootstrap becomes actively wrong-shaped once "kill and resume cheaply" is a stated requirement (Day 4's whole point). Check whether a design choice that was fine for one day's scope still fits the next day's actual bar.

## Problem 4: the failure-handling path used a connection that had already gone stale

A real (not staged) failure: SEC's server dropped the `companyfacts.zip` transfer 3 times in a row (`RemoteProtocolError: peer closed connection without sending complete message`) over a 32-minute span. When `download_to_file` finally exhausted its retries and raised, `bootstrap.py`'s `except Exception: finish_run(conn, ctx.run_id, "failed", {})` tried to record the failure — using the *same* psycopg connection that had sat idle for the whole 32 minutes. That connection had gone stale (`OperationalError: consuming input failed: server closed the connection unexpectedly`), so the failure was never recorded and `raw.collector_runs` was left stuck at `status='running'` — the exact bug Day 4 exists to fix, produced by a different mechanism (dead connection) than a process kill.

### How it was found

Watching the actual background run to its real conclusion rather than assuming a long-running command was healthy. The final traceback showed the *second* exception (the DB error) masking the *first, real* one (SEC dropping the connection) — had to read the full log, not just the tail, to find the true root cause.

### Fix

Added `_finish_run_safely()` in `jobs/bootstrap.py`: opens a **fresh** connection specifically to record a failure, never reuses whatever connection the caller had been holding. If even that fails, it logs and swallows the secondary error rather than letting it replace the original exception in what gets raised.

### Why it matters going forward

Error-handling code must not assume the resources it inherited from the "happy path" are still valid — a connection, file handle, or lock held across a long operation can die specifically *because* it sat idle waiting for that operation, which is exactly when you most need it to still work.

## Problem 5: the DB hostname stopped resolving mid-session

Separately, `db.yaqvssrpkieutdklmdjr.supabase.co` stopped resolving in DNS entirely (confirmed against two independent public resolvers, not a local caching issue) while the Supabase management API still reported the project `ACTIVE_HEALTHY`.

### Fix

Switched `DATABASE_URL` to Supabase's connection pooler (`aws-0-us-east-1.pooler.supabase.com`, username `postgres.<project-ref>`) instead of the direct `db.<project-ref>.supabase.co` host. Verified working. Also more robust generally for a connection held across long operations (Problem 4), independent of why the direct host stopped resolving.

### Why it matters going forward

Don't assume a fixed-forever hostname for a managed database is infrastructure that can't fail — have a fallback (the pooler) in mind and documented (`.env.example`) rather than discovering it mid-incident.

## Verified (doc 08's Day 4 "Done when," each condition independently)

Killed the actual worker process (not just the CLI wrapper — verified separately, they're different PIDs) mid-run at 13/20 companies stored; reran the identical command; it resumed the same `run_id` (not a fresh one); final state: 18 rows for that run, 18 distinct CIKs, zero duplicate `storage_path` anywhere in the table; all 20 originally-requested CIKs accounted for (18 stored + 2 explicitly `not_in_archive`). See `verify-collector-day`'s Day 4 report in the session transcript for the full per-condition breakdown.
