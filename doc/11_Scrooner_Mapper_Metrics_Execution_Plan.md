# 11 — Scrooner Mapper & Metrics Engine: Execution Plan

The Normalizer is done. This is the concrete build plan for Part 3 (Mapper & Metrics Engine) — mapping the Normalizer's issuer-original XBRL tags to canonical Scrooner concepts, then computing the 18 locked V1 metrics from them. It does not relitigate anything already locked in doc 02/04/06 — it operationalizes them into something buildable, the same way docs 08 and 09 did for the Collector and Normalizer. If anything here conflicts with those, they win; fix this doc, not your assumptions.

> **Status:** Canonical (2026-08-16) — all 6 stages built and verified against the golden-company set, same pattern as docs 08/09. Evidence: [doc 11b](11b_Mapper_Definition_of_Done_Evidence.md). **Owner:** Founder / Product · **Review:** When the Mapper's implementation changes in a way that would invalidate this plan.

---

## Where this sits

```
PHASE 1   Collector          ✅ done
              ↓
PHASE 2   Normalizer         ✅ done
              ↓
PHASE 3   Mapper / Metrics   ← this doc
              ↓
PHASE 4   Screener Engine
```

**One-line job description**, from doc 04's boundary table: *"Map to canonical concepts, calculate versioned metrics and validate outputs."* Two sub-jobs bundled into one phase name — the Mapper resolves issuer tags to canonical concepts; the Metrics Engine computes the locked formulas from them. Both stay strictly downstream of the Normalizer's `core` schema and strictly upstream of the Screener.

**Not in scope here:** Screener predicate evaluation, AI query parsing, market-price ingestion (Company Master, Part 4). If you find yourself writing a filter condition or fetching a stock price, stop — that's a later doc, not this one.

---

## What the Mapper/Metrics Engine is allowed to do — and not

Restating doc 04's boundary table exactly:

| Can do | Cannot do |
|---|---|
| Map issuer XBRL tags to canonical Scrooner concepts | Modify immutable raw evidence (`raw`) or reinterpret `core`'s normalized structure |
| Calculate versioned metrics from canonical concepts | Generate screens or evaluate user filter predicates (Screener's job) |
| Validate outputs against reconciliation checks | Bypass `core.fact.is_authoritative` — an unresolved conflict stays unresolved here too |

Writes are restricted to the `analytics` schema, mirroring the Collector→`raw`-only and Normalizer→`core`-only discipline exactly: **the Mapper never writes `core`.** If a task starts to feel like "let's just backfill a missing `core.period` row while we're in here," that's scope creep across a schema boundary this project has held strictly twice already — hold it a third time.

---

## Database schema — `analytics.*`

Doc 04 named the schema and gave example tables (`concept_mapping`, `metric_definition`, `metric_value`, `screen_fact`) but not column-level detail. This resolves it.

| Table | Purpose | Key fields |
|---|---|---|
| `analytics.canonical_concept` | Small lookup of Scrooner's own concept vocabulary (~15-20 entries, bounded by the same guardrail as the metric list itself) — `revenue`, `gross_profit`, `net_income`, etc. Never an issuer tag. `combination_mode` resolves an ambiguity §3 below found real evidence for: `revenue`'s mapped tags are *alternatives* (try priority order, first match with data wins — a company reports under exactly one); `total_debt`'s are *summands* (sum every mapped tag this company has data for — NKE reports three simultaneously). A single "priority-ordered list" description isn't enough on its own to tell a resolver which behavior applies. | `id`, `name` (unique), `statement` (`income_statement`\|`balance_sheet`\|`cash_flow`), `combination_mode` (`first_match`\|`sum`), `description` |
| `analytics.concept_mapping` | Ordered, human-curated list of which `core.concept` (issuer tag) rows count as a given canonical concept, for the Mapper to try in priority order. | `id`, `canonical_concept_id`, `concept_id` (FK `core.concept`), `priority` (int — try lowest first), `confidence` (`approved`\|`provisional`\|`rejected`, per doc 05's data-quality methodology), `notes`, `created_at` |
| `analytics.canonical_fact` | **Added Day 2 (Stage 3b)** — the resolver's actual persisted output: one resolved value per (company, canonical_concept, period), applying `concept_mapping`'s priority fallback or summation. Unlike `metric_value` below, this table legitimately FKs to `core.period` — it resolves values for periods the Normalizer already materialized, it doesn't invent new ones (TTM windows are Stage 3e's job, downstream of this). Written with delete-then-reinsert per company, not upsert-only — found live that upsert-only can leave stale rows behind when a mapping is rejected and the affected period has no other qualifying tag. | `id`, `company_id`, `canonical_concept_id`, `period_id` (FK `core.period`), `value` (`numeric`), `source_fact_ids` (`bigint[]`), `resolved_at` |
| `analytics.metric_definition` | One row per metric per formula version — never mutated once used, only superseded (doc 04: "version metric definitions... so historical outputs are reproducible"). | `id`, `metric_name` (matches doc 02's 18-metric list), `formula_version` (int), `formula_description` (text, canonical-concept-level, matches doc 02's table), `requires_price` (bool — flags the 6 metrics blocked on Company Master), `status` (`active`\|`deprecated`) |
| `analytics.metric_definition_input` | Structured formula inputs — not a jsonb blob, so "what does this metric actually depend on" is a real, queryable join, matching doc 05's "one definition, formula, inputs... per metric" rule. | `id`, `metric_definition_id`, `canonical_concept_id`, `role` (e.g. `numerator`\|`denominator`\|`subtrahend`) |
| `analytics.metric_value` | One computed value per company/period/metric/formula-version. **Not** a FK to `core.period` — a metric's period (a fiscal quarter, a TTM window) is an analytics-layer concept the Mapper computes, not something the Normalizer already materialized; self-contained so a TTM window never needs `core.period` relaxed or written to from here. | `id`, `company_id`, `metric_definition_id`, `period_start`, `period_end`, `period_label` (`FY`\|`Q1`-`Q4`\|`TTM`), `value` (`numeric`, never `float`), `data_as_of`, `is_null_reason` (nullable text, e.g. `missing_authoritative_fact:cost_of_revenue` — a null metric is a real, traceable outcome, not silence), `source_fact_ids` (`bigint[]`, every `core.fact.id` that fed this value — full lineage, doc 04's traceability principle) |

`analytics.screen_fact` (doc 04's fourth example table) is **not** built in this phase — it's the Screener's own serving view over `metric_value`, Part 4's job, not this one's.

### The concrete canonical-concept list — resolved, not left as "~15-20"

Derived directly from doc 02's 18-metric formula table, so Stage 3a starts with an unambiguous checklist rather than a round number. 17 canonical concepts cover every metric's inputs, including the 6 price-dependent metrics' EDGAR-derivable side (`shares_outstanding`, `dividends_per_share` — mapped now even though those metrics aren't computed until Company Master lands) and ROIC's tax-rate inputs (`income_tax_expense`, `income_before_tax` — Stage 3a maps the tags; Stage 3c still owns deciding the exact formula that uses them):

`revenue`, `gross_profit`, `operating_income`, `net_income`, `stockholders_equity`, `cash_and_equivalents`, `total_debt` (composite), `current_assets`, `current_liabilities`, `interest_expense`, `income_tax_expense`, `income_before_tax`, `cfo`, `capex`, `diluted_eps`, `shares_outstanding`, `dividends_per_share`.

This list is the actual Day 1 deliverable's scope — "every one of the ~15-20 canonical concepts" elsewhere in this doc means precisely these 17, not an approximation to be rediscovered during the build.

---

## The real problems this phase has to solve

Checked live against the golden set (already sitting in `core.fact` from the Normalizer, no new fetches needed) before writing this plan, same discipline as docs 08/09 — not asserted from the doc's own description.

### 1. Taxonomy drift is real, and worse than "one rename"

Doc 09 flagged this as explicitly out of Normalizer scope; it's squarely this phase's first job. Verified: **AAPL alone uses three different tags for "Revenue" across its own filing history** — `SalesRevenueNet` (11 authoritative FY facts, pre-2018), `Revenues` (3, transition years), `RevenueFromContractWithCustomerExcludingAssessedTax` (9, post-ASC-606). A concept mapping that only knows the current tag would silently lose a decade of AAPL's own history.

### 2. Industry-specific concept differences, not just renames

JPM (a bank) reports its primary top-line figure as `InterestAndDividendIncomeOperating` (5 authoritative FY facts) alongside `Revenues` (12) — an entirely different tag family from the product-company revenue tags above, because banks don't recognize revenue the way product companies do. **Solved by the same mechanism as taxonomy drift** (an ordered, per-canonical-concept list of acceptable tags, resolved per-company by "try each in priority order, use whichever this company actually has data under") — not a separate industry-classification system. A company that only ever reports under the bank-style tag simply falls through to it; no explicit SIC-code branching needed.

### 3. Composite concepts — one canonical concept, several summed tags, and it varies by company

"Total Debt" has no single XBRL tag. Verified live: NKE reports `LongTermDebtCurrent` + `LongTermDebtNoncurrent` + `ShortTermBorrowings` as three separate line items; ARCC reports just `LongTermDebt`; Block reports `LongTermDebtNoncurrent` + `OtherLongTermDebtNoncurrent` + `SecuredDebtCurrent`. The mapping for a composite canonical concept has to be "sum whichever of these component tags this company actually reports," not a single-tag lookup — genuinely different from taxonomy drift (those are alternatives; these are summands).

### 4. Formula versioning and reproducibility

Doc 04: *"Version metric definitions and mapping changes so historical outputs are reproducible."* A `metric_definition` row is never edited in place once it has `metric_value` rows depending on it — a formula change creates a new `formula_version`, and old values keep citing the version that produced them.

### 5. Null propagation from the Normalizer's own unresolved conflicts

Already flagged forward in `CLAUDE.md` before this doc existed: `core.fact.is_authoritative = false` is a hard filter, everywhere. ~6.6% of the golden-8's duplicate fact groups are genuine unresolved conflicts (Normalizer Day 5) — a metric whose required input falls into one of those must compute `null` with `is_null_reason` set, never fall back to a non-authoritative guess. This is common enough (thousands of groups) that it has to be a first-class, tested path, not an edge case handled once and forgotten.

### 6. Six of eighteen metrics are blocked on a decision this phase doesn't own

Doc 02's V1 metric list locks 18 metrics; 12 are pure-EDGAR and fully computable now. The other 6 (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield) need a market-price feed — Company Master's job (Part 4), still an open decision in doc 02. This phase still maps and defines all 18 (so nothing has to be redone when Company Master lands) but only *computes* the 12.

### 7. TTM and multi-year growth windows don't live in `core.period`

Revenue/EPS growth (YoY and 3Y CAGR) and any trailing-twelve-month figure need to assemble a window across multiple `core.period` rows. This is aggregation with financial meaning attached — Mapper-layer work by definition (doc 04), not something that should get written back into `core` as a new period type.

---

## Build sequence

Vertical slices, per doc 05's build method — each stage runnable and gate-checked before the next starts, same discipline as doc 09's 2a–2g.

| Stage | Deliverable | Gate before moving on |
|---|---|---|
| 3a. Concept mapping | `analytics.canonical_concept` + `analytics.concept_mapping` populated for all ~15-20 canonical concepts the 18 metrics need, priority-ordered, curated against real golden-set tag usage (not guessed) | Every golden company with any relevant data resolves each canonical concept it should have to the correct tag — including AAPL's 3-tag revenue history and JPM's bank-specific tag |
| 3b. Canonical fact resolution | A resolver that, given (company, canonical_concept, period), returns the right `core.fact` value(s) — single-tag lookup, priority fallback, or composite sum, `is_authoritative=true` only | No resolution ever returns a non-authoritative or wrong-priority value; composite concepts (Total Debt) sum correctly per company |
| 3c. Metric formula definitions | `analytics.metric_definition` + `metric_definition_input` for all 18 locked metrics, formula-versioned. ROIC's tax-rate/invested-capital detail (left open in doc 02) gets pinned down here, with evidence, not guessed | Every metric's formula is traceable to doc 02's locked table; ROIC's exact v1 formula is written down and justified |
| 3d. Point-in-time metric calculation | `analytics.metric_value` computed for the 12 EDGAR-only metrics, per company per reported period (FY/Q1-Q4) | Values reconcile by hand against golden companies' real reported margins/ratios; nulls appear exactly where an authoritative input is missing, never elsewhere |
| 3e. TTM and growth windows | Trailing-twelve-month and YoY/3Y-CAGR values for the metrics that need them | TTM figures match manual 4-quarter sums; growth figures match manual period-over-period math |
| 3f. Validation, confidence states, end-to-end DoD proof | `concept_mapping` confidence states (`approved`/`provisional`/`rejected`) actually used, not just schema; full Definition of Done proof, mirroring docs 08b/09b; cross-check a sample of `analytics.canonical_fact`/`metric_value` against `edgartools` (doc 12) as an independent second opinion, not just internal reconciliation | Full Definition of Done (below) demonstrated against the golden set, not asserted |

---

## Tasks, priorities and a 6-day target

Concept mapping before resolution, resolution before calculation, point-in-time before TTM — same "you can't build on what doesn't exist yet" ordering as doc 09.

| Day | Deliverable | Done when |
|---|---|---|
| **1** ✅ | `db/migrations/0004_analytics_schema.sql`; `mapper/concepts.py` (Stage 3a) | **Done and verified 2026-08-16.** 17 canonical concepts, 32 curated tag mappings, all resolving against real `core.concept` rows. Two real correctness bugs caught before any resolver code ran: `total_debt` would have double-counted long-term debt for 6/7 companies (`LongTermDebt` exactly equals its own current+noncurrent split whenever both are reported — fixed by mapping `LongTermDebt` alone); a candidate JPM revenue fallback tag turned out to be a subcomponent, not an alternative (`InterestAndFeeIncomeLoansAndLeases` = ~52% of `Revenues` in FY2024 — excluded). Coverage report: 113/136 (83%) of (company, concept) pairs resolve for the 8 fact-bearing companies; the rest are industry-structural nulls (ARCC/JPM have no `revenue`/`current_assets` concept the way product companies do) or genuine flagged gaps (Block/RDDT's share count uses a different, not-yet-mapped tag), not silent failures. Idempotent rerun confirmed. See `doc/learnings/mapper-day-01-concepts.md`. |
| **2** ✅ | `mapper/resolve.py` (Stage 3b); `analytics.canonical_fact` (new table, Stage 3b's persisted output) | **Done and verified 2026-08-16.** 7,904 canonical facts resolved across the golden-8. Two more real bugs caught: Block's `OtherLongTermDebtNoncurrent` (flagged provisional on Day 1) turned out to track 70-100% of `LongTermDebt`'s own value — rejected before it could inflate Total Debt; the resolver's upsert-only write left 3 stale Block rows citing a since-rejected tag after a rerun — fixed with delete-then-reinsert per company. ARCC's total debt resolves cleanly to `LongTermDebt` alone every period (the control case); AAPL's revenue resolution reproduces the real ASC 606 taxonomy transition exactly (`SalesRevenueNet` → `Revenues` → `RevenueFromContractWithCustomerExcludingAssessedTax`, smooth values, no discontinuity at the switchover). Zero non-authoritative facts leak through (checked directly). Idempotent rerun confirmed — row count now matches the resolver's own reported total exactly. See `doc/learnings/mapper-day-02-resolve.md`. |
| **3** ✅ | `mapper/definitions.py` (Stage 3c) | **Done and verified 2026-08-16.** 20 `metric_definition` rows (18 product-facing metrics; Revenue/EPS Growth each split into YoY + 3Y-CAGR variants), 39 input links, 14/6 split matching doc 02's EDGAR-only/price-dependent counts exactly. ROIC's formula pinned with real evidence (verified against AAPL: naive quarterly ×4 annualization gives an implausible 127.8% vs a sane 31.95% single-quarter figure — confirmed this is a structural flow-over-stock issue shared with ROE, not ROIC-specific; both deferred to FY-only computation until Stage 3e's TTM windows exist). Also surfaced: NKE never tags `OperatingIncomeLoss` at all (a real structural gap, not a resolver bug) and AAPL's own FY2024 `total_debt` is correctly null from a genuine Stage 2e conflict. Idempotent rerun confirmed. See `doc/learnings/mapper-day-03-definitions.md`. |
| **4** ✅ | `mapper/calculate.py` (Stage 3d) | **Done and verified 2026-08-16.** 2,271 metric values computed, 1,187 correctly null, across the golden-8's 10 EDGAR-only non-growth metrics. Three real bugs caught: a NOT NULL crash on Normalizer's deliberately-unclassified non-standard periods (skip them); duration/instant concepts for "the same period" are different `core.period` rows, so ROE/ROIC came back falsely null until matched by end-date instead of `period_id`; most seriously, a partial multi-concept role (ROIC's `invested_capital_add`) silently computed from whichever summand resolved instead of nulling when one was missing — AAPL showed 346% ROIC instead of correctly null. Fixed with an explicit per-role completeness check, promoted to doc 04's correctness controls. Hand-reconciled AAPL (margins, FCF exact matches; ROE 164.6% and ROIC 28-64% across periods with complete data, both sane) and MSFT (current ratio 1.2-1.4). Idempotent rerun confirmed. See `doc/learnings/mapper-day-04-calculate.md`. |
| **5** ✅ | `mapper/ttm.py` (Stage 3e) | **Done and verified 2026-08-16.** 1,369 growth values (revenue/EPS YoY + 3Y CAGR) and 440 TTM ROIC/ROE values computed across the golden-8. AAPL FY2024 revenue growth (2.02% YoY, 2.25% 3Y CAGR) matches manual math exactly. Strongest check of the whole Mapper phase: TTM ROIC at a Q4 boundary and Stage 3d's independently-computed FY ROIC agree to full decimal precision (`0.6432163420699880117275573775`, AAPL FY2021) — two separately-written code paths producing an identical answer. First day with no new bug found — direct payoff of Day 3/4's fixes already hardening the logic this stage builds on. Idempotent reruns confirmed on both jobs. See `doc/learnings/mapper-day-05-ttm.md`. |
| **6** ✅ | `mapper/validate.py` (Stage 3f); Stage 3f + end-to-end DoD proof (`doc/11b`, mirroring 08b/09b) | **Done and verified 2026-08-16.** Confidence-state distribution confirmed genuinely in use (28 approved/3 provisional/1 rejected, all traceable to real Day 1/2 findings). `validate` command confirms 0 non-authoritative leaks and 0 dangling lineage references across `analytics.canonical_fact`/`metric_value`, full golden-8. Cross-checked against `edgartools` (doc 12) as an independent second data path — AAPL FY2025/FY2024 `net_margin` match to full decimal precision. Most significant finding: the incremental-reprocessing isolation test (named in this doc's own DoD) **failed on first attempt** — `calculate.py`'s delete-then-reinsert was scoped only by `company_id`, silently destroying Stage 3e's growth/TTM rows for a company on every Stage 3d rerun (RDDT lost exactly 100 rows, its full Day 5 growth+TTM total). A first fix (scoping by `metric_definition_id`) was itself incomplete — `roic`/`roe` share a `metric_definition_id` between this stage's FY rows and Stage 3e's TTM rows, distinguished only by `period_label` — the real fix excludes `period_label='TTM'` too. Full golden-set re-verified idempotent after the fix (6,058 total `metric_value` rows, matching Day 5 exactly). See `doc/learnings/mapper-day-06-validation.md` and [doc 11b](11b_Mapper_Definition_of_Done_Evidence.md) for full evidence. |

---

## Tests — golden-company set (reused, no new companies needed)

The existing 10 already stress everything this phase needs — confirmed before assuming it, same as doc 09 did:

| Ticker | What it stresses for Mapper/Metrics |
|---|---|
| AAPL | Taxonomy drift within one company (3 revenue tags across its history) |
| JPM | Industry-specific concept mapping (bank revenue tag family); largest fact volume, stresses resolver performance |
| NKE | Composite Total Debt (3 separate debt-tag line items) |
| ARCC | Simplest Total Debt case (single tag) — the clean control case against NKE/Block's composite ones; BDC-style entity, worth checking ROIC's formula still makes sense here |
| XYZ (Block) | Different composite Total Debt combination again (`OtherLongTermDebtNoncurrent`, `SecuredDebtCurrent`) — a third real shape, not assumed to generalize from NKE's |
| MSFT | Second taxonomy-drift case, independent of AAPL |
| GOOGL | Multiple simultaneous tickers — confirms metric values attach to the company, not a ticker |
| RDDT | Short history — stresses growth/TTM calculations with limited prior periods (YoY may be null where 3Y CAGR can't exist yet; that's correct, not a bug) |
| TSM, ENB | **Excluded**, same as Normalizer's Stage 2d — no `core.fact` rows exist for them (20-F/40-F scope still open per doc 02), nothing to map or calculate |

---

## Definition of Done

Mirroring docs 08/09's bar — not "the schema exists," a behavioral one.

**Output:** for every golden-set company with fact data (the golden-8) —
```text
Every canonical concept the 12 EDGAR-only metrics need resolves to the correct tag(s), including
    taxonomy-drift and composite-concept cases
All 18 metrics formally defined and formula-versioned, including ROIC's previously-open detail
12 EDGAR-only metrics computed correctly for every reported period, hand-reconciled against
    real figures for at least 3 companies
TTM and growth-window values correct, hand-reconciled against manual math
Full lineage: every metric_value traceable back to the exact core.fact row(s) that produced it
Nulls appear exactly where an authoritative input is missing -- never a silent wrong guess
```

**Operationally, it can:**

- reprocess a company and get the same computed metrics (determinism)
- handle a company whose primary concept tag differs by industry (JPM) without special-casing it outside the mapping table
- handle a composite concept whose component tags vary by company (Total Debt)
- leave a metric null, with a reason, rather than guess when an input is unresolved or missing
- be re-run incrementally as the Normalizer produces new facts, without recomputing the entire golden set every time

Then — and only then — the team moves to Company Master (unblocking the 6 price-dependent metrics) and the Screener Engine.

---

## Scaling concept mapping beyond the golden set

This phase's design (Stage 3a) is built and verified against 8 fact-bearing companies. Before this doc could be called complete, it needed an actual answer to the obvious next question: what happens to `concept_mapping` when the universe is 10,396 companies, not 8 — does tag diversity keep growing, and does curation effort grow with it?

### Measured, not assumed: tag diversity is bounded by taxonomy × industry, not by company count

Checked live against SEC's own cross-company data (2026-08-16) before answering this theoretically. The `us-gaap` taxonomy is a fixed, finite vocabulary — companies pick from it (or, rarely, extend it for genuinely custom line items), they don't invent new standard tags per company. Queried the **Frames API** (doc 07 — "one fact, across all companies, for a given period," already documented, never yet used) for the exact 4 revenue-tag variants this phase's own 8 golden companies had already surfaced:

| Tag | Companies reporting under it, CY2023 |
|---|---|
| `RevenueFromContractWithCustomerExcludingAssessedTax` | 3,140 |
| `Revenues` | 2,674 |
| `SalesRevenueNet` | 404 |
| `InterestAndDividendIncomeOperating` (bank-specific) | 479 |

**The 4 tags this phase already mapped from an 8-company sample already cover several thousand real companies.** This confirms the shape of the problem: tag variety is a function of (taxonomy versions over time) × (industry-specific reporting conventions) — both **bounded, small numbers** — not a function of company count. Scaling from 8 companies to 10,396 does not mean discovering 10,396× more tags; it means finding the remaining handful of variants (REIT revenue tags, insurance premium tags, oil & gas revenue tags, and similar industry-specific cases not present in the current golden-10) that the golden set's own industry mix didn't happen to surface.

### The answer to "should we store it in a database, group it, manage a tag bank": we already do — no new schema needed

- **`core.concept`** (built Normalizer Day 3-4) already *is* the tag bank — one row per distinct `(taxonomy, tag)` ever observed, company-agnostic, referenced by a stable id. It already scales correctly: it doesn't duplicate per company, and it's already the thing every `concept_mapping` row points at.
- **`analytics.concept_mapping`'s existing `confidence` column** (`approved`/`provisional`/`rejected`) already *is* the triage mechanism doc 05's data-quality methodology calls for. A newly-discovered candidate tag isn't a new kind of object — it's just a `core.concept` row with no `concept_mapping` row yet. Triage is inserting one row with the right confidence state, not building new infrastructure.
- **Deliberately not building:** a separate "tag bank" or "candidate mapping" table. That would duplicate what `core.concept` + `concept_mapping` already do — scaffolding new schema before checking whether the existing design already handles it is exactly the mistake this project's own discipline (doc 05, "evidence before expansion") warns against, and checking it here is what avoided making that mistake.
- **Grouping:** the flat, priority-ordered list within `concept_mapping` (Stage 3a's existing design) already is the right grouping unit — one row per acceptable tag, ordered by preference, resolved per-company by "try each until one has data." No deeper hierarchy (a "tag families" table, industry-classification branching) is needed; the flat list already handles both drift (try the newest tag first) and industry variance (a bank falls through to its own tag) as shown above. It also has no database performance scaling concern — `concept_mapping` stays a small reference table (dozens to low hundreds of rows total, not one row per company), so resolution stays a cheap indexed join regardless of universe size.

### The curation workflow that actually scales: frequency-ranked discovery, not per-company review

Nobody should hand-review 10,396 companies' tags one at a time. The scalable version of Stage 3a's curation, for whenever wider-than-golden-10 coverage is decided:

1. **Discover candidates via the Frames API**, not via bulk ingestion. Querying "how many companies use tag X for period Y" costs one API call and needs zero local storage — meaning tag-coverage analysis can inform `concept_mapping` curation *before* any wider Collector backfill happens, not after. This directly supports (doesn't compete with) doc 02/09's existing decision to defer wider-universe collection: the mapping table can be well-populated ahead of time, cheaply, so a future backfill doesn't simultaneously blow the Supabase budget *and* flood the system with unmapped-tag nulls.
2. **Rank by impact, not alphabetically or exhaustively**: for each canonical concept, a coverage-gap report (a SQL query over `core.concept`/`core.fact`, no new table) surfaces tags with real company/datapoint volume that have no `concept_mapping` row yet — ordered by how many companies/how much value it would unlock, so curation effort goes where it matters.
3. **Approval stays human, deliberately not automated.** Ranking candidates is fine to automate; *accepting* one into `concept_mapping` is not — matches this project's stated bias toward "narrow, deterministic, auditable" behavior (`CLAUDE.md`), especially here, where a wrong auto-accepted mapping would silently corrupt a real financial metric. No fuzzy-matching, no LLM-guessed tag equivalence.
4. **Where this eventually lives operationally:** a CLI report is the right-sized tool for now (mirrors `normalizer/dedupe.py`'s `conflicts` command) — doc 06 already names the long-term home: Part 11, Internal Admin (Django), whose one-line job description is literally "Data QA, mapping overrides." Don't build that UI during Phase 3; that would be building ahead of proven need.

### New gate, tied to the existing open decision

This doesn't reopen doc 02's "how wide should company-universe coverage go" decision — it adds a concrete readiness gate to it, worth recording there when that decision actually gets made: **before any backfill wider than the golden-10, the coverage-gap report should show the 12 EDGAR-only metrics' required concepts resolving cleanly for ≥95% of a representative larger sample** (e.g., pulled cheaply via the Frames API, no ingestion required to check this), not just the golden-10. Below that threshold, a wider backfill would produce a wave of avoidable nulls that better mapping coverage, done first, would have prevented.

---

## What this phase does *not* decide

- **Market-price source/vendor** — Company Master's job (Part 4), still open in doc 02. This phase defines and formula-locks the 6 price-dependent metrics but does not compute them.
- **Screen predicate evaluation, ranking, or the ~10 operators' actual filter logic** — Screener Engine's job (Part 4/5), not this one's.
- **Which metrics surface in the UI, in what order, with what labels** — Frontend's job.
- **20-F/40-F (TSM/ENB) treatment** — stays out of scope here exactly as it did in the Normalizer, pending doc 02's still-open decision.

---

## Repository footprint

Within `pipeline/` (this repo), extending the existing `src/scrooner_pipeline/` package:

```text
pipeline/
├── src/
│   └── scrooner_pipeline/
│       ├── collector/        # done (Phase 1)
│       ├── normalizer/       # done (Phase 2)
│       ├── mapper/           # this phase
│       │   ├── concepts.py       # 3a -- canonical_concept + concept_mapping
│       │   ├── resolve.py        # 3b -- canonical fact resolution
│       │   ├── definitions.py    # 3c -- metric_definition + inputs
│       │   ├── calculate.py      # 3d -- point-in-time metric_value
│       │   ├── ttm.py            # 3e -- TTM / growth windows
│       │   └── validate.py       # 3f -- confidence states, reconciliation checks
│       ├── common/            # existing, unchanged
│       ├── db/                 # existing, unchanged
│       └── jobs/
│           └── map.py              # NEW -- Typer CLI, mirrors jobs/normalize.py's per-stage command pattern
├── db/
│   └── migrations/
│       └── 0004_analytics_schema.sql   # NEW -- this phase
└── tests/
    └── golden_companies/       # reused unchanged
```

---

## Gotchas to watch for, specifically

- Don't let "map" quietly become "invent." If a canonical concept has no tag any golden company actually reports under, leave it unmapped and flagged `provisional` — don't add a tag to the mapping table on the theory that it's "probably close enough."
- Don't write to `core` from `mapper/`, ever — not even to "fix" something the Normalizer got wrong. If the Normalizer is actually wrong, that's a Normalizer bug to fix in `normalizer/`, not a Mapper workaround.
- Composite concepts (Total Debt) need a documented, versioned summation rule per canonical concept — don't let the component-tag list drift silently as new companies reveal new combinations; add them to `concept_mapping` deliberately, same discipline as the golden-company regression-fixture rule from doc 05.
- Resist computing the 6 price-dependent metrics with a placeholder/estimated price "just to have a number" — a metric with `requires_price=true` and no price source is null, not approximately right.
- Keep ROIC's formula honest: doc 02 explicitly left the tax-rate/invested-capital detail open for this phase to pin down "with a version number." Do that pinning with real justification in Stage 3c, not by copying the first formula found online without checking it against what `core.fact` actually has available.
- `edgartools` (doc 12, adopted Day 2) is available for ad hoc cross-checks in **any** stage, not just 3f's formal validation pass — it already caught one real discrepancy on Day 2. Treat a mismatch as a signal to investigate (doc 12 §5), not automatically "our data is wrong" — it can also disagree because *it's* trusting an unreliable label ours already routes around (see the `fy`/`fp` finding). Never let it or its output touch a production write path.
