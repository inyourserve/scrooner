# Three real bugs behind "the GitHub worker failed" (2026-09-10)

Prompted by a short user report ("meanwhile github worker failed"). Traced to
three separate, real issues, not one — each verified against live logs/data
before being called a bug, then fixed and re-verified.

## 1. Two new workflows missing 3 of 4 required secrets

`pipeline-sanity.yml` and `pipeline-frames-check.yml` (both added 2026-09-08)
only set `env: DATABASE_URL` (and `SEC_USER_AGENT` for the Frames one) —
`Settings()` (`common/config.py`) requires `supabase_url`/
`supabase_service_role_key`/`sec_user_agent` too, all three missing from the
sanity workflow. Every step crashed immediately on `pydantic_core.ValidationError`.
Fixed by copying the exact working `env:`/"Require production configuration"
pattern already proven in `pipeline-refresh.yml`.

## 2. The main daily cron alert-failed for 8+ consecutive days on pure noise

`pipeline-refresh.yml`'s "Enforce freshness and dead-letter health" step
(`scrooner-operations --fail-on-alert`) failed every single day from
2026-09-02 through 2026-09-09 — but the actual pipeline work underneath
(`if: always()` steps) mostly kept succeeding regardless. Root cause:
`evaluate_alerts()` treated **any** unresolved `raw.collector_errors` row as
fatal, with no distinction by `error_type`. Checked the table's entire
history before assuming this was a real gap: `NotInBulkArchive` is the
**only** error_type it has ever recorded (97/97 rows) — a CIK genuinely
absent from that day's `companyfacts.zip` snapshot, an expected condition
(new registrants, edge-of-index-rebuild timing), not a pipeline bug. Someone
had already been periodically resolving these by hand (82/97 resolved before
this fix) but gaps in that manual triage kept re-triggering the alert.

Fixed: `DEAD_LETTER_QUERIES["collector"]` now excludes `NotInBulkArchive`
(still zero-tolerance for any *other* collector error type — a genuinely new
error type would still alert immediately). A new, parallel
`EXPECTED_MISS_QUERIES`/`OperationalSnapshot.expected_misses` field tracks
the excluded category for visibility only — it's in the JSON output but
never reaches `evaluate_alerts()`. 8 new/updated tests in
`test_operations.py`, full suite 505 → 511 passing.

**This fix immediately un-masked two real, previously-invisible problems** —
exactly the risk alert fatigue creates: a persistently-red gate trains
everyone to stop reading it, so a second real signal arriving under the same
red status goes unnoticed.

## 3. `core.filing` was 11 days stale — 2,176 active companies' recent filings never normalized

`normalizer_backlog` freshness (`max(filing_date)` in `core.filing`) showed
306.76 hours stale (last touched 2026-08-28) once the noise above stopped
hiding it — while `raw.sec_filing_documents` (the Collector's own output)
was current through 2026-09-08. A fix for this exact gap
(`scripts/reprocess_recent_filers.sh`, wired into the cron as "Reprocess
Normalizer + Mapper for recently-filed companies") had *already been added*
to the workflow file on 2026-09-09 — but the most recent actual cron
execution (16:45 UTC 09-09) ran *before* that commit landed on `main`, so it
had never actually executed once. Confirmed live: 2,176 active companies had
a raw filing in the last 10 days with zero `core.filing` awareness of it.

Fixed by running the script manually rather than waiting for tomorrow's
schedule (`bash scripts/reprocess_recent_filers.sh 10`, backgrounded --
2,176 companies × 19 normalize/map stages, several hours). Verified
mid-run: `normalizer_backlog` freshness already dropped to 42.97 hours
(well under the 96-hour target) after only the `identity` stage had
processed a fraction of the list, confirming the fix is real and working,
not just theoretically correct.

## 4. A genuine race condition, found investigating dead-letter noise from #2

6 new `analytics.mapper_error` rows, all the same shape: a `UniqueViolation`
on `metric_value_company_id_metric_definition_id_period_start_p_key`,
`metric_definition_id=44` (`ebitda`), all within a ~16-minute window on
2026-09-09. Traced to `mapper/expanded_metrics.py`: its output rows are all
anchored on `period_start = period_end = date.today()` (an "as of now"
composite metric convention this project uses in several places), so two
*concurrent* invocations of `calculate_expanded_metrics_for_company()` for
the *same company* on the *same calendar day* target the identical primary
key. The existing delete-then-insert write pattern has a real window: one
process's `INSERT` can land between another process's `DELETE` and its own
`INSERT`, raising a hard constraint violation instead of converging safely
— a genuine, live-confirmed instance of the multi-session-on-shared-DB race
this project has already documented once for calculate.py's own resolution
logic (2026-08-31), now confirmed in a second module.

Fixed by switching to an atomic upsert (`INSERT ... ON CONFLICT (company_id,
metric_definition_id, period_start, period_end, period_label) DO UPDATE`),
verified against the real constraint definition (`pg_constraint`) before
writing it, not assumed from the error message alone. Safe specifically
because `rows` always contains a full entry for every `OUTPUT_METRIC_NAMES`
metric on every call (checked directly — no early-return short-circuits
before the write), so there's no "stale row a delete would have cleaned up"
case an upsert-without-delete could leave behind. 2 tests
rewritten/added in `test_expanded_metrics.py` (the old delete-scope test
became an upsert-scope test; a new test asserts the SQL itself uses
`ON CONFLICT ... DO UPDATE`, not delete-then-insert). The 6 stale
`mapper_error` rows marked `resolved=true` with a note pointing at this fix,
since the underlying bug — not just the symptom — is now closed.

## Verification

- Full pipeline suite: 505 → 511 passing across all fixes.
- `scrooner-operations` run live against the real database after all fixes:
  `status: "ok"`, zero alerts, `dead_letters` all zero, `expected_misses`
  correctly shows the 15 benign collector misses without alerting on them.
- `normalizer_backlog` freshness confirmed dropping in real time mid-reprocess
  run, not just asserted from the code change.

## Generalizable lessons

- **A persistently-failing status check trains people to stop reading it —
  which is exactly when a second, real signal under the same red status
  goes unnoticed.** Clearing known-benign noise from an alert isn't just
  cosmetic; it's what makes the alert useful again. Found here: fixing the
  8-day noise issue immediately surfaced two real problems that had been
  invisible underneath it the whole time.
- **A workflow-file fix landing on `main` doesn't mean it ran** — GitHub
  Actions schedules use whatever's on the default branch *at trigger time*;
  a fix committed between two scheduled runs has a real gap where it exists
  in the repo but has never once executed. Check the actual run history
  (`gh run list`/`gh run view`), not just the file on disk, before assuming
  a recently-added cron step already closed a gap.
- **Any write anchored on `date.today()` (not a real filing period) is a
  same-day collision risk the moment more than one process can touch it** —
  this project already has several such "as-of-now" metrics
  (`price_metrics.py`, other `expanded_metrics.py` rows); this specific
  race was found for `ebitda`'s newly-added TTM row, but the same shape of
  bug is latent anywhere else a delete-then-insert (not an upsert) writes to
  a `date.today()`-keyed row on a shared, multi-session dev database.
