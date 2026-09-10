# 14 — Scrooner Screener Engine: Execution Plan

Company Master 4a is done and 4b's ingestion shape is built (on mock data). This is the concrete build plan for Part 5 (Screener Engine) — the deterministic query engine that evaluates structured filter predicates against `analytics.metric_value` and returns matching companies. It does not relitigate anything already locked in doc 02/03/04/06 — it operationalizes them into something buildable, the same way docs 08/09/11/13 did for the Collector, Normalizer, Mapper, and Company Master. If anything here conflicts with those, they win; fix this doc, not your assumptions.

> **Status:** Canonical (2026-08-17) — all 5 stages built and verified against the golden-company set with real, hand-checked expected results. Evidence: [doc 14b](14b_Screener_Engine_Definition_of_Done_Evidence.md). **Owner:** Founder / Product · **Review:** When a core decision changes, or when the AI Query Engine (Part 6) needs something this doc didn't anticipate.
>
> **Addendum, 2026-09-10 — performance rewrite + OR/NOT support, see [ADR 0001](../adr/0001-screener-redis-cache-and-boolean-logic.md).** Two things below are now superseded: (1) the Screener reads a new precomputed table, `analytics.company_screening_snapshot` (`screener/snapshot.py`, migration 0061), not `analytics.metric_value` directly — a live-measured 13.9s ROE screen was traced to a Bitmap Heap Scan against `metric_value`'s 11M scattered rows, not an unindexed query; the snapshot precomputes the same "most recent value" resolution once, offline. (2) `ScreenQuery` gained an optional `where: PredicateGroup` field supporting arbitrary AND/OR/NOT trees, compiled to parameterized SQL (`EXISTS` subqueries per leaf) — the "AND-of-predicates only" restriction stated in this doc's boundary table and §"Explicitly out of scope" below is no longer accurate; the flat `metric_predicates`/`categorical_predicates` lists still work unchanged (implicit AND) for backward compatibility. `apps/backend` also gained a Redis cache (dataset-versioned, keyed by `scrooner_pipeline.screener.cache_key.compute_query_hash`) and a process-wide connection pool — a cache-hit `/v1/screen` request now completes in ~4-8ms, down from 13.9s. Everything else in this doc (the 9 comparison/ranked operators, null-never-matches semantics, `excluded_missing_data`/`excluded_inactive` tracing for flat AND queries) is unchanged. See `doc/learnings/2026-09-10-screener-performance.md` for the full investigation.

---

## Where this sits

```
PHASE 1   Collector                    ✅ done
              ↓
PHASE 2   Normalizer                   ✅ done
              ↓
PHASE 3   Mapper / Metrics             ✅ done
              ↓
PHASE 4   Company Master (4a + 4b-mock) ✅ done (4b real vendor still open)
              ↓
PHASE 5   Screener Engine              ← this doc
              ↓
PHASE 6   AI Query Engine
```

**One-line job description**, from doc 04's data-flow step 7: *"Screener evaluates structured, deterministic predicates against analytics data."* It takes an already-validated, already-structured query — never natural language, never a free-text filter — and returns a deterministic, traceable result set.

**Not in scope here:** natural-language parsing (AI Query Engine, Part 6 — this doc's own query schema is exactly what that phase will need to validate its NL→structured translation against, per doc 04: *"validation rejects unknown metrics or ambiguous clauses"*), any HTTP/API exposure (Backend API, Part 7 — doc 02's "no FastAPI initially" gate isn't cleared yet), saved/named screens or auth (User System, Part 9), and computing the 6 price-dependent metrics (still a separate, not-yet-built Mapper follow-on per doc 13).

---

## What the Screener is allowed to do — and not

Doc 04's boundary table has no Screener row, the same gap Company Master's doc 13 had to resolve for itself. This resolves it:

| Can do | Cannot do |
|---|---|
| Evaluate the 9 locked operators (doc 02) against `analytics.company_screening_snapshot` (see 2026-09-10 addendum above), combined with AND, or with OR/NOT via an explicit `where` tree | Parse natural language, or accept an unstructured/free-text query — that's the AI Query Engine's job (Part 6), strictly downstream of this one |
| Resolve "the current value" for a company/metric using an explicit, documented selection rule (see below) | Guess, backfill, or fall back to a lower-confidence value when the current value is null — exclude the company instead, and say why |
| Filter on company identity/sector/status (`core.company`, built by Company Master 4a) | Write to `core` or `analytics` — the Screener is read-only, the same discipline as every phase before it: Collector→`raw`, Normalizer→`core`, Mapper→`analytics`, Screener→nothing |
| Return a fully traceable result: which metric, which period, which formula version, which companies were excluded and why (for a `where`-tree query, per-predicate exclusion attribution is intentionally not attempted — see 2026-09-10 addendum) | Invent a metric or operator not in doc 02's locked lists — the "~10 operators" MVP guardrail is about the operator vocabulary (>, <, between, top_n, ...), not how predicates combine; AND/OR/NOT combination is now supported, see addendum above |

---

## Where this code lives, and why

Doc 04's architecture diagram lists Screener as its own box, downstream of Company Master and upstream of the AI Query Engine — not explicitly inside "the data pipeline (`pipeline/`... Collector → Normalizer → Mapper/Metrics)." But it reads the exact same `analytics`/`core` schema `pipeline/`'s Python environment already knows how to connect to, and doc 02's "no FastAPI initially" gate means there's no Backend API service to host it in yet either. Building it as a new top-level module inside `pipeline/` (`screener/`, with a Typer CLI for direct manual testing, same pattern as every phase so far) avoids standing up a new service ahead of actual need — matching doc 05's "evidence before expansion," the same reasoning that's kept Polars unused and FastAPI unbuilt so far. **Revisit trigger**: once Backend API (Part 7) actually starts and doc 02's FastAPI gate clears, this module gets wrapped by an API layer, not rewritten — the engine/HTTP-exposure boundary is deliberate.

---

## The real problems this phase has to solve — checked live, not assumed

Same discipline as docs 08/09/11/13: checked `analytics.metric_value`'s actual shape before writing this plan.

### 1. "The current value" is not well-defined without a rule — checked live, not assumed

`analytics.metric_value` has **multiple rows per company per metric** — one per reported period, not just the latest. Checked directly: `roe`/`roic` have both `FY` (annual) and `TTM` (rolling, updates every quarter) rows; the other 12 metrics (margins, growth, `fcf`, `fcf_margin`, `current_ratio`, `debt_to_equity`, `interest_coverage_ratio`) have `FY` **and** `Q1`-`Q4` rows, no `TTM` at all (TTM was only built for `roic`/`roe` — doc 11's Stage 3e). A screen has to pick one value per company, not average or list all of them. **Rule, evidenced against real data**: prefer the most recent `TTM` row if one exists for that metric/company (more current — updates quarterly, never more than ~3 months stale); otherwise take the row with the latest `period_end` regardless of label (naturally picks up a fresher quarter over a stale prior-year FY). Verified against real output: querying "most recent ROE" this way ranks AAPL (119.9% TTM, 2026-06-27) highest and correctly returns nothing at all for TSM/ENB (20-F/40-F, out of Mapper's fact-extraction scope) — no fabricated row, no silent default.

### 2. Null handling — resolved the same way `is_authoritative` and `is_null_reason` already resolve it everywhere else

A company's most-recent value for a filtered metric can be null (a genuine Stage 2e conflict, an industry-structural gap like a bank lacking `current_assets`, or simply no data yet). **Resolved**: a null value never matches any comparison operator — the company is excluded from the result, not shown with a guessed pass/fail. This isn't new logic to build; it's exactly how SQL/Python's own null semantics already behave (`None > 5` is never true), so implementing predicate evaluation directly against resolved values gets this for free rather than needing a special case. What *is* new: the excluded-for-missing-data set must be returned as its own explicit, visible list — never silently dropped — matching doc 03's explainability gate ("interpreted criteria and metric definitions are visible") and closing the "decide the UX for 'no confident data'" item flagged as open in the last scorecard update.

### 3. Sector filtering is SIC-only, and SIC is coarser than "sector" — already decided, restated so it isn't silently forgotten

Doc 10 already resolved this: SIC code (from Company Master 4a's `core.company.sic_code`/`sic_description`) is the fallback; GICS (the more standard sector taxonomy) is a licensed feed, out of scope. Categorical `=` in doc 02's operator list filters on SIC. Worth restating plainly here because SIC is really an *industry* classification (JPM: `6021` "National Commercial Banks"), not a broad *sector* the way "Financials" is — a real V1 limitation, not a bug, and not something to quietly paper over with a fake sector-mapping table.

### 4. Company status default — a real, undocumented-until-now decision

Company Master 4a built `core.company.status` (`active`/`stale`/`unknown`). A screen for "good stocks to buy" showing a company with no recent filing would be a real, visible quality problem. **Decision**: screens default to `status='active'` companies only, with an explicit `include_inactive` override for anyone who wants the full universe (e.g., internal QA). All 10 golden companies are currently `active`, so this default is untested against a real `stale`/`unknown` case — worth revisiting the moment a wider company set surfaces one.

### 5. Only 12 of 18 locked metrics have any real data to screen on right now

The 6 price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield) have **zero** `analytics.metric_value` rows — Company Master 4b built the price *input* (on mock data), but the Mapper follow-on that actually computes these metrics from it hasn't been built (a deliberate sequencing choice, not an oversight). **Decision**: the Screener's metric catalog (the list of screenable field names it validates predicates against) includes only the 12 EDGAR-only, non-price metrics for now. Adding the other 6 back is a one-line catalog change once that Mapper follow-on exists — not a Screener redesign.

---

## Query schema — the concrete input/output shape

This is also, deliberately, the schema the AI Query Engine (Part 6) will need to produce and validate against later — building it carefully now pays twice.

```python
MetricPredicate:
    metric_name: str            # must be in the screenable-metric catalog (12 EDGAR-only metrics)
    operator: Literal[">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"]
    value: Decimal | None             # for >,<,>=,<=,=,!=
    value_range: tuple[Decimal, Decimal] | None   # for between
    n: int | None                     # for top_n/bottom_n

CategoricalPredicate:
    field: Literal["sic_code", "sic_description"]
    operator: Literal["="]
    value: str

ScreenQuery:
    metric_predicates: list[MetricPredicate]   # combined with AND
    categorical_predicates: list[CategoricalPredicate]   # combined with AND
    include_inactive: bool = False
    sort_by: str | None          # metric_name to sort results by
    sort_desc: bool = True
    limit: int | None

ScreenResult:
    matched: list[CompanyResult]     # cik, ticker, company_name, {metric_name: (value, period_label, period_end, formula_version)}
    excluded_missing_data: list[CompanyExclusion]   # cik, company_name, which metric(s) were null
    excluded_inactive: list[str]     # ciks excluded by the status default, if include_inactive=False
```

Rejecting an unknown `metric_name`/`field`, or a malformed predicate (e.g. `between` without a `value_range`), is **validation, not a query result** — the same "never invent a field" discipline doc 04 requires of the AI Query layer applies here first, since the Screener is this project's actual gate against a bad structured query reaching real data, AI-generated or not.

---

## Build sequence

Vertical slices, per doc 05's build method — each stage runnable and gate-checked before the next starts, same discipline as docs 09/11/13.

| Stage | Deliverable | Gate before moving on |
|---|---|---|
| 5a. Query schema | ✅ **Done and verified 2026-08-17.** `screener/schema.py` — `MetricPredicate`/`CategoricalPredicate`/`ScreenQuery`, Pydantic-validated. Malformed predicates (missing `value`, missing `value_range` for `between`, missing/invalid `n` for ranked ops, more than one ranked predicate per query) all confirmed rejected with a clear error. |
| 5b. Value resolution | ✅ **Done and verified 2026-08-17.** `screener/resolve.py`. ROE's TTM-preferred ranking reproduced exactly against an independently hand-computed query; `debt_to_equity` (no TTM variant) confirmed picking ARCC's genuinely freshest quarter (2026-03-31) over its older FY row — direct proof of the latest-period_end half of the rule, not just the TTM half. |
| 5c. Predicate evaluation | ✅ **Done and verified 2026-08-17.** `screener/evaluate.py`. All 9 operators exercised against real data (see doc 14b); a null value confirmed to never pass a comparison and never rank in `top_n`/`bottom_n`. |
| 5d. Query execution | ✅ **Done and verified 2026-08-17, after one real bug.** `screener/query.py`. All 4 test screens below matched hand-computed expected results exactly. Found and fixed live: `sort_by` on a metric that wasn't also a filter predicate produced a correctly-ordered result with no visible value explaining the order — an incomplete-lineage gap, fixed by including `sort_by`'s metric in every match's output regardless of whether it's also a predicate. See `doc/learnings/screener-5a-5e.md`. |
| 5e. End-to-end verification | ✅ **Done and verified 2026-08-17.** `doc/14b` DoD evidence. Determinism confirmed via byte-identical reruns; unknown-metric rejection confirmed before any per-company query runs. |

---

## Test screens — golden-set, concrete, hand-checkable now

Grounded in real `metric_value` data already checked while writing this plan, not hypothetical. **All 4 confirmed exactly against the running implementation, 2026-08-17** — see doc 14b.

| Screen | Expected result (checked live 2026-08-17) |
|---|---|
| `roe > 0.30` (most recent, TTM-preferred) | AAPL (119.9%), GOOGL (38.1%), MSFT (30.2%) match; NKE, JPM, ARCC, Block below threshold; TSM/ENB correctly excluded entirely (no data, 20-F/40-F scope) |
| `sic_code = '7372'` (categorical) | MSFT and Block both match (both genuinely SIC `7372`, "Services-Prepackaged Software") — a real two-company categorical case, not a single-row trivial one |
| `debt_to_equity between (0, 1)` | Exercises `between` against real leverage-ratio data across the set |
| `roic top_n(3)` | Exercises ranked selection; must return exactly 3 companies, ordered, excluding any with null ROIC (AAPL's own FY2024 ROIC is a known real null — Mapper Day 4 — good test that a null doesn't quietly rank as zero) |

---

## Definition of Done

Mirroring docs 08/09/11/13's bar — not "the schema exists," a behavioral one.

**Output:** for every golden-set company —
```text
Every one of the 9 locked operators evaluates correctly against real metric_value data
"Most recent value" resolves via the documented TTM-preferred/latest-period_end rule,
    hand-verified against at least 3 metrics across multiple companies
A null value at a company's most-recent period excludes it from a match -- never guessed,
    never silently dropped from the exclusion list
Sector/status filtering works against real core.company data (SIC codes, active/stale/unknown)
Every matched company's result cites the exact metric_value row (period, formula_version)
    that produced it
```

**Operationally, it can:**

- run the same query twice against unchanged data and get an identical result (determinism)
- reject a query naming an unknown metric or malformed predicate before touching the database
- run a `top_n`/`bottom_n` ranked query that correctly skips null values rather than ranking them as zero
- report exactly which companies were excluded and why (missing data vs. inactive status), not just the matches
- be extended with the 6 price-dependent metrics later by a catalog change alone, once Mapper computes them

Then — and only then — the AI Query Engine (Part 6) can start, since it depends on this doc's query schema already existing and being trustworthy.

---

## What this phase does *not* decide

- **Natural-language query parsing** — AI Query Engine's job (Part 6), strictly downstream.
- ~~OR logic / nested boolean predicate groups — out of the "~10 operators" MVP guardrail; AND-of-predicates only for V1.~~ **Built 2026-09-10** — see the addendum above and [ADR 0001](../adr/0001-screener-redis-cache-and-boolean-logic.md).
- ~~A persisted `analytics.screen_fact` serving view... at golden-10 scale, querying `metric_value` directly with joins is fast enough that building a materialized view now would be scaffolding ahead of a real latency problem.~~ **Wrong at full-population scale, built 2026-09-10.** This assumption held at golden-10 (10 companies); at the real full population (5,216 companies × 82 metrics, 11M `metric_value` rows) a live-measured ROE screen took 13.9s — the precomputed table this line said not to build yet (`analytics.company_screening_snapshot`) is exactly what closed it. Left here, not deleted, as the specific "evidence before expansion" call this doc made and the specific scale at which it stopped being true — the general principle wasn't wrong, this one application of it needed revisiting once real population size arrived, not golden-10.
- **Computing the 6 price-dependent metrics** — still Mapper's unfinished follow-on (doc 13), not this phase's to build or wait for.
- **Saved/named screens, auth, or any user-facing surface** — User System (Part 9) and Frontend (Part 8), later.
- **HTTP/API exposure** — Backend API (Part 7), blocked on doc 02's still-uncleared "no FastAPI initially" gate.

---

## Repository footprint

```text
pipeline/
├── src/
│   └── scrooner_pipeline/
│       ├── collector/         # done (Phase 1)
│       ├── normalizer/        # done (Phase 2)
│       ├── mapper/            # done (Phase 3)
│       ├── company_master/    # done (Phase 4a; 4b mock-only)
│       ├── screener/          # this phase
│       │   ├── schema.py         # 5a -- ScreenQuery/ScreenResult/predicates
│       │   ├── resolve.py        # 5b -- most-recent-value resolution rule
│       │   ├── evaluate.py       # 5c -- the 9 operators, null handling
│       │   └── query.py          # 5d -- full query execution
│       ├── common/             # existing, unchanged
│       ├── db/                  # existing, unchanged
│       └── jobs/
│           └── screen.py           # NEW -- Typer CLI, mirrors jobs/map.py's pattern (accepts a query as JSON for manual testing)
└── tests/
    └── golden_companies/       # reused unchanged
```

No new migration — the Screener is read-only against tables Mapper/Company Master already built.

---

## Gotchas to watch for, specifically

- Don't let a null value rank as zero in `top_n`/`bottom_n` — a company with no confident ROIC is not "the worst ROIC," it's unranked. Exclude it from the ranking entirely, same as any other comparison.
- Don't quietly expand the operator or metric list past doc 02's locked sets "since it'd be easy" — that guardrail exists on purpose (doc 02: "not permission to expand ad hoc").
- Don't let the "most recent value" rule silently pick a stale FY over a fresher, already-null-checked TTM row for roic/roe, or vice versa for metrics that never have TTM — the rule is metric-shape-aware on purpose, not a single blind "latest row" query.
- Don't write to `core`/`analytics` from `screener/` for any reason, including "just to cache a computed screen result" — that's exactly the kind of boundary-blur this project has held four times already.
- Don't wrap this in a FastAPI endpoint "since it's basically ready" — doc 02's gate on that is still closed until Backend API (Part 7) actually starts.
