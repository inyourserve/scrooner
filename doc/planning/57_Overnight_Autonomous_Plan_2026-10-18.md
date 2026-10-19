# Overnight autonomous plan (2026-10-18/19) — resume here

Written for: any Claude session continuing the data-moat repair while the founder sleeps. Read this file first, then `doc/data-moat/learnings/2026-10-17-coverage-rebuild-atomicity-q4-conflicts-and-nonadditive-derivation.md` (sections 5 and 6) and `data-team/20-SCROONER-INFRA-MAP.md`.

## Authority and its limits
The founder said (2026-10-18): "whatever it takes", "you guys collab with each other", "there won't be any of my involvement now", and asked to resume after the usage limit resets. That authorizes completing the repair below with the guardrails below. It does **not** authorize: schedule or permission changes, cancelling runs, spending money, new accounting rules, seeding Wave 1 concepts, touching `apps/app`, or anything the permission classifier blocks. If an action is blocked, **stop that step, record it in the progress log, and do not work around it.**

## Why this plan exists
A Data Verifier check (47 promoted facts vs original filings) found the "latest filed wins" resolver published wrong values: sign-only conflicts (5 of 10 wrong) and annual values won by proxy statements or 10-Qs. The rule is fixed (`3defd93`) but already-promoted wrong facts remain. On 2026-10-18 a full-company repair (`dedupe` on 4 shards) failed and the database restarted at 16:22:53Z while three heavy jobs overlapped (scheduled refresh, recompute part C, repair). So this repair is **targeted and light**.

## State at hand-off (2026-10-18 ~19:40Z)
- Rollout parts A (`derive-q4`), B (resolve + population) and C (metrics + screener snapshot) all succeeded (runs 39095144507, 39120726043, 39129274636).
- Repair run 39130948676 (full `dedupe` chain, 1,232 companies) FAILED in Phase 1 when the database restarted. Nothing to resume from it.
- Still wrong in the database: **3,935 promoted facts** still `is_authoritative` that violate the new rules (945 sign-only, 3,077 wrong form, 87 both; rule annual 3,530, quarter 405; 1,196 companies). Backup of ids and values: `doc/data-moat/team/backups/violating_promotions_20261018.json`.
- Also stale: 2,203 negative derived weighted-share rows (824 companies); the deriver now retires them when it next runs for those companies (`6f3fcd5`), so the S2 run covers them only if those companies are included (see S2).
- Data Sanity run (started 18:10Z) was in progress.
- Postgres `max_connections` is 60; compute is small (shared_buffers 256 MB), so jobs are disk-bound.

## Steps (do in order; each has preconditions)

### S0. Preconditions for any heavy step (check immediately before)
All must hold, else wait (re-check later; do nothing heavy):
1. `gh run list --limit 40`: no run of "Pipeline freshness refresh", "Data sanity layer", "SEC Frames self-consistency", "Live SEC verification" or "Full-population recompute" is in_progress / queued / pending / waiting.
2. DB (Supabase MCP `execute_sql`, project `yaqvssrpkieutdklmdjr`): total connections ≤ 25; no client query older than 5 minutes (ignore `autovacuum:`); `default_transaction_read_only` = off; `now() - pg_postmaster_start_time()` > 30 minutes.
3. `ListAgents`: no peer session is `busy` on a heavy DB job.
4. Time rule: do not START S1/S2 if the next scheduled refresh could fire during the run. Nominal refresh is 12:23Z, in practice 13:00-17:00Z (jittered, sometimes ~16:00Z). Start only if now is before ~08:00Z, or accept waiting until after the day's refresh and sanity have both finished.

### S1. Demote the violating promoted facts (small production write, reversible)
Pipeline: `cd pipeline && set -a && source .env && set +a`, then a Python script using `scrooner_pipeline.db.connection.get_connection`:
1. Re-query the violating set live with the query used to build the backup (`core.fact_conflict_resolution` joined to `core.fact` / `core.filing`; sign-only = `value_min < 0 and value_max > 0 and abs(value_min) = abs(value_max)`; bad form = rule `latest_filed_fy_v1` and form not in `conflict_latest_filed.FY_ELIGIBLE_FORMS`, or rule `latest_filed_quarter_v1` and form not in `QUARTER_ELIGIBLE_FORMS`; only `is_authoritative` facts). Expect about 3,935 (±; abort and report if it is above 6,000 or below 2,000).
2. Save the live id list to `doc/data-moat/team/backups/` as well (reversal source).
3. In batches of 500 ids, in separate transactions with `set statement_timeout='120s'`: `update core.fact set is_authoritative = false where id = any(%s) and is_authoritative`, then `delete from core.fact_conflict_resolution where fact_id = any(%s)`. Re-check after: violating set size is 0.
4. Reversal (if needed): `update core.fact set is_authoritative = true where id = any(<ids from backup>)` and re-insert audit rows from the backup (rule, value_min/max are not in the backup; rerun `conflict-latest-filed` on the old code is not available, so reversal restores authority only).
Commit the new backup file and the script.

### S2. Targeted recompute for the affected companies (2 shards)
1. Build the CIK list live: ciks of the companies of the demoted facts, plus (optional, same run) companies that still have non-positive derived weighted-share rows (concept ids 935 and 936, `is_derived`, `value <= 0`). Input string must stay under ~60k characters (about 5,000 CIKs).
2. Re-check S0, then dispatch:
```
gh workflow run pipeline-recompute.yml \
  -f ciks="<comma list>" \
  -f normalize_stages="conflict-latest-filed derive-interim-quarters derive-q4" \
  -f resolve_stages="resolve-facts resolve-concept-fallbacks" \
  -f population_stages="resolve-statement-fallbacks resolve-conflict-fills" \
  -f metric_stages="calculate growth ttm-returns ttm-margins calculate-price-metrics calculate-expanded-metrics calculate-piotroski calculate-quality-flags calculate-reconciliation calculate-tax-reconciliation calculate-fcf-growth calculate-dividend-streak" \
  -f scope=active -f shards=0,1 -f snapshot=yes -f tag_library=no
```
Do not use more than 2 shards. Do not run `dedupe`. Estimated 3-5 hours (unmeasured for this size; the full runs measured: derive-interim 3.6 h, derive-q4 3.8 h, resolve ~1.1 h, phase 2 ~0.8 h, metrics ~3 h for ~1,300 companies per shard on 4 shards).

### S3. Monitor while it runs (every 5-10 minutes)
Stop condition (record and do not retry until healthy and S0 holds): connections ≥ 40, a client query > 10 minutes (ignore autovacuum), read-only turns on, postmaster restarted, or a second heavy workflow starts. You cannot cancel runs (blocked); record the situation in the progress log. The stages are idempotent, so a failed run can be re-dispatched after the database is healthy for 30 minutes.

### S4. Verify after success
1. Violating promoted facts remaining (the S1 query, re-run live) = 0 or explained.
2. Non-positive derived share rows (`concept_id in (935,936) and is_derived and value <= 0`) near 0 for the covered companies.
3. Spot-check the Verifier's rejected cases are now correct or blank: ADT 2017 tax (-764,313,000), AEHR FY2020 tax (+36,000), CAPS 2017 tax (-36,000), PCSV FY2023 tax (-1,011,466), SSM 2024 pre-tax, METC 2022 tax (30,153,000 from the 10-K), OPHC 2018 tax (blank).
4. Spawn the `scrooner-data-verifier` agent for about 25 re-sampled promotions (include sign-only and ineligible-form winners and a few clean ones) against the original filings. It is read-only.
5. Compare Market Cap coverage and Q4-gap counts to the 2026-10-17 baseline (Market Cap 4,377 companies / 91.04%; `q4_not_derived` 32,671; `period_gap` is rebuilt only by `period_completeness`, which runs in the sanity workflow, so a Q4-gap re-count may lag one day).

### S5. Write the report
Create `doc/data-moat/team/overnight-report-2026-10-19.md` (what ran, run ids, timings, counts before/after, anything blocked or odd). Commit named files only (`git commit -- <paths>`), push the same turn. Update the progress log below.

## Guardrails (always)
- Never `git add -A` / `git add .`; other sessions have uncommitted work. Commit with `git commit -- <paths>`; push in the same turn.
- One heavy job at a time. No local heavy jobs while a GitHub recompute runs.
- Do not change schedules, disable workflows, cancel runs, raise shards above 2, or retry a blocked command another way.
- No new accounting definitions. Quarantine (blank) is the safe default for sign-only conflicts.
- Keep summaries plain; the founder is not technical about this layer.

## Open decisions (do NOT take; leave for the founder or an accountant)
Restatement basis (as-filed or restated), rounding tolerance for the Q4 vintage tool, non-USD retained earnings, finance-lease policy, enabling Wave 1 seeding, a larger Supabase compute size, and wiring the Q4 vintage dry-run into writes.

## Progress log (append newest last)
- 2026-10-18 ~19:40Z: plan written; backup committed; waiting for the Data Sanity run (started 18:10Z) to finish before S0.
- 2026-10-18 21:22Z: S0 preconditions met (workflows idle, 11 connections, DB up 5 h, peers idle). S1 done: 3,935 violating promoted facts demoted in 8 batches, 3,935 audit rows removed, 0 violating remain; live id list saved in `doc/data-moat/team/backups/violating_promotions_live_20261018.json`. 1,741 companies for S2 (1,196 promotion-affected + 824 stale-share, overlapping).
- 2026-10-18 21:25Z: S2 dispatched: run 39167755310, 2 shards, commit 6646b13. Checked: the new `conflict_resolution.py` stale-fill code is not called by `resolve-conflict-fills` (comment at conflict_resolution.py:1345), so this run is unaffected by it. Monitor writes `recompute_monitor_S2.log` (scratchpad).
- 2026-10-18 21:46Z: yfinance cross-check of the demoted annual facts (359 comparable of 3,004 recent-year ones; older years have no yfinance data): yahoo agrees with both copies 54%, only with another copy (demotion right) 36%, only with the demoted value (a right value blanked) 6%, none 3%. Sign-only: latest filing right in 11 of 19. Conclusion: quarantine is safe but loses about half of the right sign-only values; next improvement is a tie-break from the filing's own arithmetic (pre-tax - tax = net income), not yfinance. Next: S3 monitoring, S4 verification.
- 2026-10-19 03:01Z: S2 run 39167755310 ended `cancelled`. Phase 1 (conflict-latest-filed, derive-interim, derive-q4, resolve-facts, resolve-concept-fallbacks) SUCCEEDED on both shards (21:25Z -> 00:50Z, 3 h 25 min). Phase 2 (population-wide stages) hit its 120-minute cap at 02:51Z: `resolve-statement-fallbacks` took ~70 min (00:50 -> 02:00Z), `resolve-conflict-fills` ran 02:00 -> 02:48Z and was in its last concepts (basic_eps) when cancelled; the tag-preference merge was skipped. Phase 3 (metrics) was skipped; Phase 4 snapshot ran anyway. No database restart (uptime 10 h 38 min, 12 connections, read-only off). Net state: canonical_fact for the 1,741 companies is refreshed, but their metrics are still the old ones from run C, the conflict-fills tail and the tag-preference merge are not done. Earlier full runs took 44-50 min for all of Phase 2, so this was ~2.5x slower (cause unknown; possibly cold caches after the 16:22Z restart).
- NEXT (do not start before 03:30Z and S0 holding 30 min): dispatch D1 = Phase 2 only: `-f ciks=<contents of doc/data-moat/team/backups/s2_ciks_20261018.txt> -f normalize_stages=none -f resolve_stages=none -f population_stages=resolve-conflict-fills -f metric_stages=none -f scope=active -f shards=0,1 -f snapshot=no -f tag_library=no` (conflict-fills ~50 min + tag-preference merge ~45 min, under the 120-min cap but tight). Then D2 = metrics only for the same CIKs with the 11-stage metric list, `population_stages=none`, `snapshot=yes` (est. ~2 h on 2 shards). If D1 hits its cap again, record it and stop; do not loop.
