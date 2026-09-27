# 2026-09-27 — Metric plausibility gates: real percentile evidence

Direct request: "PE can't be higher and lower than this? dividend yield etc — do this for almost all the metrics, create a doc for this." Full doc: [`doc/reference/47_Scrooner_Metric_Plausibility_Gates.md`](../reference/47_Scrooner_Metric_Plausibility_Gates.md). This file preserves the raw evidence that doc's bounds were derived from, run live against `analytics.metric_value` on 2026-09-27 — not guessed numbers.

## Query

```sql
select md.metric_name,
  min(mv.value) as p_min,
  percentile_cont(0.01) within group (order by mv.value) as p01,
  percentile_cont(0.05) within group (order by mv.value) as p05,
  percentile_cont(0.50) within group (order by mv.value) as p50,
  percentile_cont(0.95) within group (order by mv.value) as p95,
  percentile_cont(0.99) within group (order by mv.value) as p99,
  max(mv.value) as p_max,
  count(*) as n
from analytics.metric_value mv
join analytics.metric_definition md on md.id = mv.metric_definition_id
where mv.value is not null and md.metric_name in (<~80 metric names>)
group by md.metric_name;
```

## Headline findings — real, currently-live degenerate values

These are rows sitting in `analytics.metric_value` today, not hypothetical worst cases:

| Metric | Real observed max/min | Why |
|---|---|---|
| `roe` | max **56,600,000%** | Near-zero-equity denominator |
| `price_to_book` | max **$1.29 billion** | Same shape — equity near zero |
| `current_ratio` | max **5,820,424** | Near-zero current-liabilities denominator |
| `dividend_yield` | max **837,700%** (8,377.8x) | Almost certainly a split-adjustment or per-share/aggregate scale mismatch — not yet root-caused |
| `goodwill_pct_assets` | max **51,099** (5.1M%) | Unit-scale mismatch between goodwill and total assets |
| `sga_pct_revenue` | max **1,400,587** (140M%) | Near-zero-revenue denominator |
| `interest_coverage_ratio` | max **30,774,371** | Near-zero interest-expense denominator |
| `debt_to_equity` | max **436,452** | Near-zero-equity denominator |
| `current_ratio` / `quick_ratio` | min **-1.27** / **-530.8** | Impossible by accounting definition (both inputs are non-negative) — a sign/tag bug, not a rare real case |

## Full raw percentile table

Preserved as originally returned (Decimal strings, not rounded) — see the doc's own §1-§8 for how each was turned into a CRITICAL/WATCH bound. Two queries were run (ratio-shaped metrics, then dollar/CAGR/streak-shaped metrics); results are combined here.

Ratio-shaped metrics (~50 rows: margins, returns, liquidity, leverage, valuation, yields, expense ratios, reconciliation gaps) — full table in the conversation this doc was built from; spot-checked values above are the ones that directly drove a bound decision. Re-run the query above against the live database to refresh, rather than trusting this snapshot indefinitely — per this project's own "a metric's real distribution shifts as coverage grows" precedent (`pipeline/CLAUDE.md`'s coverage-score entries).

Dollar/CAGR/streak metrics (~30 rows): confirmed `piotroski_f_score` already holds its `[0,9]` bound in real data (`min=0, max=9`); confirmed `market_cap`'s real max (**$5.47T**) is plausible, not a bug, while its real min (**exactly $0**) is suspicious; confirmed every growth-rate CAGR family has a hard real floor at **exactly -1** (-100%) with no violations, consistent with the mathematical floor this doc's §7 bound relies on.

## Not yet done

- The two live findings named at the bottom of the main doc (`dividend_yield`'s 837,700% max, `price_to_book`'s $1.29B max) were surfaced by this research but not root-caused or fixed in this pass — the doc's own job was the bounds, not the individual-company fix. Worth its own follow-up, same shape as every other `sanity/tag_investigator.py`-mediated fix in this project's history.
- No code reads these bounds yet — see the main doc's "Status and next step" section.
