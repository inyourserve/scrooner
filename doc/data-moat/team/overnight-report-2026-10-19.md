# Overnight report, 2026-10-18 to 2026-10-19

Written for: the founder (plain language). Details and commands: `doc/planning/57_Overnight_Autonomous_Plan_2026-10-18.md`.

## Bottom line
The wrong values are out of the data and the fixed rule is in place. The metrics for the 1,741 repaired companies have **not** been recomputed yet, because the step before it ran out of time twice. Nothing is running now, and the database is healthy.

## What was done
1. **Rollout A, B, C finished** (derive Q4, resolve, metrics, screener snapshot) on 2026-10-18.
2. **Rule fixed** (`3defd93`): only annual-report-type forms can win an annual value, and sign-only conflicts are blanked instead of guessed.
3. **3,935 wrongly promoted facts demoted** at 21:22Z (945 sign-only, 3,077 from a proxy or quarterly report, 87 both), with their ids saved in `doc/data-moat/team/backups/`. None remain.
4. **Repair run 39167755310** (1,741 companies, 2 shards): Phase 1 (rule, derive, resolve) succeeded in 3 h 25 min. Phase 2 hit its 2-hour cap and was cancelled; metrics were skipped.
5. **Run D1 39195116060** (Phase 2 only): hit its 2-hour cap again at 05:32Z. Per the plan I stopped and did not redispatch. The scheduled check job was deleted.

## Why Phase 2 was slow (evidence, not proof)
The same fill stage took **29.5 minutes** in the earlier full run (39120726043) and **113.8 minutes** in D1. The first ten concepts ran at normal speed, then it slowed progressively; from 04:20Z single concepts took 12 to 27 minutes. A monitor tripped at 04:38Z on a single query of 777 seconds. Nothing else heavy was running. The database restarted at 16:22Z on 2026-10-18, and since then its table statistics counters are reset: `core.fact` shows about 1.3 million dead rows and no autovacuum or autoanalyze recorded. That is the best lead. I did not confirm it is the cause.

## What the yfinance check said (recent years only, 359 comparable facts)
54% agreed with both the demoted value and another filing's (harmless), 36% agreed only with another filing (demotion right), 6% agreed only with the demoted value (a right value blanked), 3% matched none. For sign-only conflicts the latest filing was right in 11 of 19, so blanking is safe but loses about half; the fix is the filing's own arithmetic (pre-tax minus tax equals net income), not built yet.

## Current state
- **Stored values** (`canonical_fact`) for the 1,741 companies are refreshed and correct under the new rule.
- **Metrics and the P/E, market cap and TTM figures** for those companies are still the older ones, so they may not match the stored values. Everyone else was rolled out already.
- **Not done:** the tag-preference merge, the last conflict-fill concepts, the metric recompute for the 1,741, the Verifier re-sample of repaired values, and the Q4-gap recount (the sanity run recounts it).

## What I recommend, in order
1. **Run `ANALYZE` (and a vacuum of `core.fact`) in a quiet window.** It is routine maintenance after a crash restart, and the first thing to try for the slowness. It needs a person to approve, since it is a production database operation.
2. **Then rerun D1 and D2** from the plan (Phase 2, then metrics plus snapshot). If it still hits the cap, raise the cap or split Phase 2.
3. **Consider a larger Supabase compute size.** The database runs with 256 MB of shared buffers on 46 GB of data, and every query waits on disk reads.
4. **Build the arithmetic tie-break for sign-only conflicts** so fewer right values are blanked.
5. **The scheduled refresh** is nominally due at 12:23Z and could start while a rerun is going. It cannot be paused from here (blocked), so avoid starting a rerun before it has finished.

## Open decisions for you or an accountant
Restatement basis (as filed or restated), the rounding tolerance for the Q4 vintage tool, non-USD retained earnings, finance-lease policy, switching on the Wave 1 concepts, and the compute upgrade.

## Log entry for doc 57 (to append when committed)
2026-10-19 09:25Z: D1 ended `cancelled` at 05:32Z, Phase 2 cap hit again; stopped per plan, no redispatch; cron check deleted; DB healthy (up 17 h, 12 connections, idle, read-only off). Resume only after a person approves `ANALYZE`/`VACUUM` of `core.fact` (or another fix), then D1 and D2.
