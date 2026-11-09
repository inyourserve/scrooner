# Review: PR #5, heavy_job_guard.sh (Ritwik (cloud), release approver, 2026-11-09)

Reviewed at the head of pull/5 (fetched 2026-11-09). Read only. No DB queries and no SEC requests.

## Verdict: CHANGES (one blocking defect, then approve)
The design is right: the write refuses and never waits, and the nightly jobs wait for a write. The blocking defect is that the guard fails OPEN when the GitHub API call fails.

## Answers
1. **Can the write and the refresh still overlap?** Not on the normal path. Each side sees the other's run as in_progress, because the guard job itself makes the run in_progress:
   - the write checks first: the refresh waits;
   - the refresh checks first: the write refuses;
   - both check at once: the write refuses, and the refresh waits for the refused run to end.

   They CAN overlap in two cases:
   - (a) a `gh run list` call fails (see B1);
   - (b) a manual heavy workflow runs beside a write: recompute, certify, cells-load, cells-proof or cells-load-stage. These have no wait-for-write job, so they rely on the operator. The write refuses if one is already active, but not if one starts after the write.
2. **Can the guard deadlock?** No. Only the heavy jobs wait, and they wait only on fsn-write. fsn-write never waits; it refuses. fsn-write is in its own concurrency group (`fsn-write`), so a waiting refresh never blocks it in a queue.
3. **Can wait-for-write block the nightly forever?** No. It exits 1 after 330 minutes, inside the 340-minute job timeout, so that night's refresh fails closed and is skipped. It does not run beside the write.
   - A write can legitimately run longer than 330 minutes: its write job also has a 340-minute timeout, and its shards can queue for runners. That costs one missed nightly, which is the safe outcome.
   - Side effect: while the refresh waits, it holds the `heavy-db-jobs` slot for up to 5.5 h. GitHub keeps only one pending run per group, so a sanity or tag-library run queued during that time can be replaced and silently dropped. Add an alert to that job, so a failed wait is visible.
4. **Is the 17:00-02:00 backstop right?** It is acceptable, and the live guard does not need it for correctness: a refresh that starts during a write waits, whatever the clock says. The backstop only stops a write from starting just before a refresh GitHub has not yet queued, which would delay that night's refresh. Observed starts are 17:47-21:49 and ends are up to 01:34. The latest end leaves only 26 minutes before 02:00, and the reprocess has overrun its budget before (run 42507618224), but a write dispatched while a refresh is still running is refused by the live check anyway. Keep 02:00. If you want margin, 03:00 is also fine. Note that the backstop also blocks a `restore` for 9 hours a day; that is acceptable.

## Required before merge
- **B1. Fail closed on GitHub API errors.** In `active_runs`, only the last `gh` call's exit status counts. Command substitution does not inherit errexit, so a failed `gh` call for an earlier status is ignored. In `wait_for_write`, `| grep ... || true` turns every failure into "no write in progress".

  I reproduced this with a stub `gh` (local bash, `set -euo pipefail`):
  - first call fails: the refuse path passes with empty output;
  - every call fails: the wait path reports "no write".

  Fix:
  - `shopt -s inherit_errexit`, or check each `gh` call's status explicitly;
  - in refuse-if-heavy, any API error means refuse;
  - in wait-for-write, an API error means keep waiting (still bounded by `max_minutes`), never proceed.
- **B2. A test for the script, run in CI:** stub `gh` through PATH. Cover:
  - no runs;
  - a heavy run active;
  - a write in_progress;
  - a write queued only, so wait passes;
  - an API failure on the first status: refuse and keep waiting;
  - the max_minutes cap with `HEAVY_GUARD_POLL_SECONDS=0`.

  Mutation-check it: the test must fail on the current script, which fails open.

## Follow-ups (not blocking)
- F1. Add the same wait-for-write first job to `pipeline-recompute.yml` and `pipeline-certify.yml` (heavy-db-jobs group), and to the three cells workflows (manual-db-jobs group, plus `cells-load-stage.yml`). Without it, overlap answer 1(b) remains.
- F2. Alert on a failed wait-for-write, so a skipped nightly is noticed (answer 3).
