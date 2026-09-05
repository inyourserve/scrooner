# 2026-08-31 — `analytics.metric_value` duplicate-row cleanup

Found during an autonomous data-sanity pass (user direction: "plan data sanity etc," don't wait for instructions).

## What was found

`analytics.metric_value` had 29,764 groups of `(company_id, metric_definition_id, period_label, period_end)` with more than one row — there's no unique constraint on that tuple at the DB level, so nothing prevents it. Breaking the 29,764 groups down:

- **11,745 groups**: all rows in the group are `value IS NULL` — harmless duplication (a "most recent value" query returns null either way), just wasted rows.
- **~16,360 groups**: duplicate rows carry the *same* non-null value — also harmless in effect, still wasted rows.
- **1,659 groups**: duplicate rows carry *genuinely different* non-null values — a real correctness risk. Whichever row a query's `ORDER BY ... LIMIT 1` happens to return first is undefined without an explicit tie-break, so two different renders of the same page could show two different numbers for the same metric/period.

## Root cause, checked on a real example, not assumed

Company 161, `roa`, period `Q2 2012-07-28`:

| id | value | data_as_of | source_fact_ids |
|---|---|---|---|
| 7865094 | 0.01499911555... | 2026-08-29 11:24:34.595657+00 | {1495266, 1484996} |
| 7865051 | 0.01499566590... | 2026-08-29 11:24:34.595657+00 | {1495267, 1484996} |

Identical timestamp (same `calculate` run, not a stale-vs-fresh rerun issue) and `source_fact_ids` overlap on one fact (1484996) but differ on the other (1495266 vs 1495267). This points to the Mapper's `calculate.py` fanning out into a separate `metric_value` row for *each* candidate `core.fact` row when Normalizer's Stage 2e correctly leaves two `is_authoritative=true` facts unresolved for the same concept/period (documented, deliberate — Normalizer Day 5's "picking any single value would be a guess the Mapper shouldn't inherit as settled fact"). The values above differ by ~0.03%, immaterial to a human reader, but the *pattern* — two competing rows for one (company, metric, period) — is a real, general risk that would matter more for a less-forgiving metric or a genuine restatement conflict.

**Not fixed at the root** (`calculate.py`'s fan-out behavior) in this pass — that's a real Mapper-layer design question (how should the formula engine resolve an unresolved multi-fact conflict? Pick one deterministically? Skip and leave null? Both are defensible, neither was decided here) worth its own scoping pass, not something to decide unilaterally mid-sanity-check. Flagged here, not resolved, matching this project's own "flagged, not fixed" precedent (`insider_summary.py`'s N+1 pattern).

## What was fixed

The duplicate *rows* themselves — deleted all but the lowest-`id` row per group (30,183 rows removed, 8,070,108 → 8,039,925, exact match to the predicted count). A simple, deterministic, low-risk cleanup: it doesn't decide which of two conflicting values is "more correct" (that's the unresolved question above), it just guarantees the table has exactly one row per (company, metric, period) going forward, so "most recent value" resolution is at least deterministic rather than silently depending on query-plan order.

## Also checked, confirmed harmless

- **Mock price / real price overlap**: `core.market_price` (the 300-row mock dataset from Company Master 4b, all `is_mock=true`) and `core.market_price_alpaca` (3,350 real rows) share 10 `(company_id, price_date)` pairs. Checked live whether anything reads `core.market_price` at all (`apps/site`, `apps/backend`, `screener/`, `mapper/`) — nothing does. The overlap is dead data, not a live bug; not worth further cleanup effort right now.

## Lesson for future writers to `analytics.metric_value`

Any calculate/growth/expanded-metrics job that resolves a metric from `core.fact`/`analytics.canonical_fact` needs to guarantee it writes at most one row per `(company_id, metric_definition_id, period_label, period_end)` — either by explicitly picking one candidate fact when more than one `is_authoritative=true` row exists for the same concept/period, or by adding a real unique constraint (and an `ON CONFLICT` resolution rule) so a future ambiguous case fails loudly instead of silently fanning out. Neither exists today.
