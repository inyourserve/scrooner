# 2026-09-03 — `expanded_metrics.py` was silently wiping 7 metrics it doesn't own, every single run

## What was found

Re-checking the full metric coverage list (in response to "the score is low, plan how to increase it"), `market_cap`, `trailing_pe`, and `dividend_yield` showed **0% coverage** — despite having been verified at 60.0%/48.7%/16.1% earlier the same session. This was a genuine regression, confirmed live against `metric_value` directly, not a stale-read artifact.

## Root cause

`mapper/expanded_metrics.py`'s `calculate_expanded_metrics()` loads **17 metric IDs** into one `metric_ids` dict: its own 9 real outputs (`net_debt_ebitda`, `ev_ebitda`, `ev_sales`, `peg_ratio`, `buyback_yield`, `total_shareholder_yield`, `institutional_ownership_pct`, `share_dilution_trend`, `cash_conversion_cycle`) plus 8 metrics it only *reads* as dependencies (`ebitda`, `market_cap`, `trailing_pe`, `eps_growth_yoy`, `dividend_yield`, `debtor_days`, `inventory_days`, `payables_days`) — all in the same dict, passed to `calculate_expanded_metrics_for_company()` as a single `metric_ids` parameter. That function's per-company delete (`target_ids = list(metric_ids.values())`) used the **entire dict**, deleting all 17 metrics' TTM rows for that company — but only ever reinserting its own 9. The other 8 (owned by `calculate.py`'s generic engine and `price_metrics.py`) were deleted and never restored.

Every `calculate-expanded-metrics` run — and there were several today, since it's the last stage in every full-population rollout this session ran — silently erased `price_metrics.py`'s and `calculate.py`'s already-correct work. `calculate-price-metrics` was never rerun after the last `calculate-expanded-metrics` invocation, so the wipe was never noticed until a fresh, full-breadth coverage check surfaced the exact-zero.

## Fix

Added `OUTPUT_METRIC_NAMES` (the 9 real outputs, explicit and named) and scoped the delete to only those IDs (`[mid for name, mid in metric_ids.items() if name in OUTPUT_METRIC_NAMES]`), leaving `metric_ids` itself unchanged so the function can still *read* its 8 dependencies. One new regression test asserts the delete's parameter set is disjoint from the dependency names. 330/330 suite passing.

## Audited every other `calculate-family` module for the same shape — found nowhere else

Checked all 8 modules with a metric-scoped delete (`calculate.py`, `fcf_growth.py`, `reconciliation.py`, `ttm.py` ×2, `quality_flags.py`, `quality_score.py`, `dividend_streak.py`, `tax_reconciliation.py`, `price_metrics.py`). Every other module either uses a single (non-list) `metric_definition_id`, or builds its delete target list from an explicit, named subset (`ttm.py`'s `GROWTH_METRICS`, `fcf_growth.py`'s `LAG_YEARS`) rather than the full dict it was handed — or, like `reconciliation.py`, never mixes metric-level dependencies into `metric_ids` at all (its dependencies are concept-level, tracked in a completely separate dict). `expanded_metrics.py` was the only one that merged reads and writes into one dict and then deleted by the whole thing.

## Restoration

Launched a 3-stage full-population rerun in the correct dependency order — `calculate` (restores `ebitda`/`debtor_days`/`inventory_days`/`payables_days`) → `calculate-price-metrics` (restores `market_cap`/`trailing_pe`/`dividend_yield`, and the 3 metrics that were never touched by the bug: `price_to_sales`/`price_to_book`/`fcf_yield`) → `calculate-expanded-metrics` (now fixed, computed last so it reads the freshly-restored dependencies without being able to delete them again).

## Lesson

**A delete-then-reinsert pattern is only as safe as its delete scope — and "I pass this dict because I need to read from it" and "I pass this dict because I'm allowed to delete everything in it" are two different claims that must never be conflated into the same parameter.** This is the third distinct instance this week of a delete scoped too broadly relative to what a module actually owns (`resolve()`'s company-wide delete wiping a zero-mapping concept; this one). The generalizable check going forward: any function that both reads dependency values through a metric/concept-ID lookup dict *and* performs a delete-then-reinsert should build its delete target list from an explicit, named "this is what I write" set — never from `dict.values()` of whatever was loaded for convenience.
