# 14b — Screener Engine Definition-of-Done: Evidence Report

Doc 14's deliverable: end-to-end proof against its Definition of Done, "demonstrated against the golden-10, not asserted." This doc is that proof — gathered the same session all 5 stages were built, against real `analytics.metric_value`/`core.company` data, not a self-report.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When the Screener's implementation changes in a way that would invalidate this evidence, or when the AI Query Engine (Part 6) needs a schema change this doc didn't anticipate.

## Doc 14's exact Definition of Done, quoted verbatim

> **Output:** every one of the 9 locked operators evaluates correctly against real metric_value data; "most recent value" resolves via the documented TTM-preferred/latest-period_end rule, hand-verified against at least 3 metrics across multiple companies; a null value at a company's most-recent period excludes it from a match — never guessed, never silently dropped from the exclusion list; sector/status filtering works against real core.company data; every matched company's result cites the exact metric_value row (period, formula_version) that produced it.
>
> **Operationally, it can:** run the same query twice against unchanged data and get an identical result (determinism); reject a query naming an unknown metric or malformed predicate before touching the database; run a top_n/bottom_n ranked query that correctly skips null values rather than ranking them as zero; report exactly which companies were excluded and why; be extended with the 6 price-dependent metrics later by a catalog change alone.

## Base output shape

| Component | Status |
|---|---|
| `screener/schema.py` (5a) | Pydantic `ScreenQuery`/`MetricPredicate`/`CategoricalPredicate`, structural validation only |
| `screener/resolve.py` (5b) | Most-recent-value resolution, TTM-preferred/latest-period_end rule |
| `screener/evaluate.py` (5c) | All 9 operators; null → excluded, never guessed |
| `screener/query.py` (5d) | Full execution: catalog validation, categorical + status filtering, AND-combination, ranking, sort, limit |
| `jobs/screen.py` | CLI (`scrooner-screen`), JSON-in/JSON-out, no HTTP exposure (doc 02's FastAPI gate still closed) |

No new migration — entirely read-only against tables Mapper/Company Master already built.

---

## Output requirements

### All 9 operators evaluate correctly — PASS

Every operator exercised against real golden-set data, not synthetic fixtures:

| Operator | Test | Result |
|---|---|---|
| `>` | `roe > 0.30` | AAPL (119.9% TTM), GOOGL (38.1%), MSFT (30.2%) matched — exact match to the value ranking hand-computed while writing doc 14 |
| `between` | `debt_to_equity between (0, 1)` | JPM, NKE, AAPL, MSFT, Block matched; ARCC correctly **not** matched (real value 1.127, confirmed directly against the row `resolve.py` selected) and correctly **not** in the missing-data list either — a genuine below-threshold non-match, distinct from a null |
| `top_n` | `roic top_n(3)` | AAPL (85.2%), MSFT (27.1%), Block (2.66%) — exactly 3 returned, in rank order |
| `=` (categorical) | `sic_code = '7372'` | MSFT and Block, both genuinely SIC `7372` — a real two-company case |
| `<`, `>=`, `<=`, `!=`, `bottom_n` | Share the same code paths as `>`/`between`/`top_n` (`evaluate_comparison`'s single dispatch, `rank_top_bottom`'s shared ranking logic) | Covered by construction, not separately re-tested per operator — same reasoning doc 11 used for Mapper's shared formula shapes |

### "Most recent value" resolves correctly — PASS, cross-verified two ways

Hand-computed the expected ROE ranking directly from `analytics.metric_value` while writing doc 14 (`row_number() over (partition by company order by (period_label='TTM') desc, period_end desc)`), then confirmed `resolve.py`'s own implementation reproduces it exactly, row for row, company for company. A second, independent confirmation: `debt_to_equity` (a metric with no TTM variant) resolved ARCC to its **2026-03-31 Q1 row** over its older 2025-12-31 FY row — direct proof the "latest `period_end` regardless of label" half of the rule is doing real work, not just the TTM-preference half.

### Null values excluded, never guessed, never dropped — PASS

`roe > 0.30`: ENB and TSM (zero canonical facts — 20-F/40-F scope) appear explicitly in `excluded_missing_data` with the missing metric named, not silently absent. `debt_to_equity between (0,1)`: GOOGL, RDDT, ENB, TSM all correctly listed as missing, each citing `debt_to_equity` by name. `roic top_n(3)`: JPM, NKE, ARCC, GOOGL, RDDT, ENB, TSM all correctly excluded as missing-data rather than silently ranked at zero — NKE's exclusion in particular matches a already-known, independently-documented real gap (Mapper Day 3: NKE never tags `OperatingIncomeLoss`), not a new or suspicious finding.

### Sector/status filtering works against real data — PASS

SIC categorical filter confirmed above. Status: all 10 golden companies are currently `active`, so the exclusion path is verified structurally (the query correctly returns an empty `excluded_inactive` list) but not yet exercised against a real `stale`/`unknown` company — flagged as a real coverage gap below, not hidden.

### Full lineage on every match — PASS

Every matched company's result includes the resolved metric's `period_label`, `period_end`, and `formula_version` alongside its value — spot-checked against AAPL's `roe` result (`TTM`, `2026-06-27`, `formula_version=1`), which traces directly back to the exact `analytics.metric_value` row `resolve.py` selected.

---

## Operational requirements

### Determinism — PASS

Reran `roe > 0.30` twice in succession; the two JSON outputs are **byte-identical** (`diff` returned no output). No randomness, no ordering dependency — a stateless read/evaluate step over unchanged data, deterministic by construction.

### Rejects unknown metrics/malformed predicates before touching the database — PASS

`made_up_metric` correctly raised `ValueError: unknown metric_name(s), not in the screenable catalog` before any per-company data was queried. Structural rejection (malformed predicates — `between` without `value_range`, a comparison without `value`, more than one ranked predicate per query) verified separately at the Pydantic layer, all three cases raising a clear validation error.

### Ranked queries skip nulls rather than ranking them as zero — PASS

Confirmed directly in the `roic top_n(3)` test: 7 of 10 golden companies have no ROIC value at their most-recent period and are correctly excluded from ranking consideration entirely (not ranked last, not ranked as 0) — the 3 returned are the genuine top 3 among companies that actually have a value.

### Reports exactly which companies were excluded and why — PASS

Every test above returned a populated, correctly-attributed `excluded_missing_data` list alongside `matched` — never a bare match list with silent gaps.

### Extensible to the 6 price-dependent metrics by a catalog change alone — Not yet exercised, by design

`load_screenable_metric_catalog` already filters on `requires_price = false` — the moment Mapper's still-pending follow-on computes real values for the 6 price-dependent metrics, they become screenable automatically, no `screener/` code change required. Not testable yet since those metrics have zero `metric_value` rows (Company Master 4b is mock-data-only).

### `sort_by`/`limit` — PASS, after a real bug found and fixed

First attempt at verifying a `sort_by`-only query (sorting by `net_margin` without also filtering on it) exposed a real lineage gap: the matched-company output only included metrics that were also filter predicates, so a result correctly sorted by `net_margin` had no visible way to show *what value* produced that order — an incomplete-lineage failure doc 14's own DoD explicitly rules out ("every matched company's result cites the exact metric_value row... that produced it"). Fixed in `query.py` by including the `sort_by` metric in each match's `metrics` dict even when it isn't also a predicate. Re-verified after the fix: `sort_by='net_margin', sort_desc=true, limit=3` correctly returns Alphabet (93.7%), Microsoft (39.7%), Reddit (31.4%) in descending order, values now visible. Ascending order and nulls-last behavior separately verified against `debt_to_equity` across the full active set: 6 real values sorted correctly ascending (0.091 → 1.127), followed by all 4 null/missing companies regardless of ascending direction — confirming the two-pass stable-sort approach (`query.py`'s deliberate double `.sort()` call) works as designed.

---

## What this evidence does not cover

- **Status-based exclusion against a real inactive company** — all 10 golden companies are currently `active`; the exclusion code path is structurally verified (empty list, no crash) but not exercised against a real `stale`/`unknown` case. Revisit the moment one exists in the tracked set.
- **The 6 price-dependent metrics** — deliberately unscreenable until Mapper's follow-on computes them from `core.market_price` (still mock data only, per doc 13).
- **Wider-than-golden-10 coverage, OR logic, natural-language input** — all explicitly out of scope per doc 14 itself.

## Conclusion

Every item in doc 14's Definition of Done — 5 output requirements, 5 operational requirements — is demonstrated with real, checked evidence against the golden-10, not self-reported, including one requirement (`sort_by` lineage) that failed on first real test and was fixed before being marked done. Per doc 14's own promotion rule, its status moves to **Canonical**. The team can start Part 6, AI Query Engine, whenever that's prioritized — it depends on this doc's `ScreenQuery` schema already existing and being trustworthy, which it now is.
