# 09 — Scrooner Normalizer: Execution Plan

The Collector is done. This is the concrete build plan for Part 2 (Normalizer) from doc 06 — architecture, database schema, folder structure, a day-by-day target, tests, and (new, 2026-08-15) a Supabase free-tier capacity check that shapes how wide this phase can run before Mapper work starts. It does not relitigate anything already locked in doc 02/04/06 — it operationalizes them into something buildable this week, the same way doc 08 did for the Collector. If anything here conflicts with those, they win; fix this doc, not your assumptions.

> **Status:** Canonical (promoted from Draft 2026-08-15 — all 7 stages built and independently verified against live data; see [doc 09b](09b_Normalizer_Definition_of_Done_Evidence.md) for the Definition-of-Done evidence) · **Owner:** Founder / Product · **Review:** When the Normalizer's implementation changes in a way that would invalidate this plan.

---

## Where this sits

Per doc 06's execution order, the Normalizer is **Phase 2** — it starts now that the Collector (Phase 1) is done, and it has to finish before the Mapper & Metrics Engine (Phase 3) can start.

```
PHASE 1   Collector          ✅ done
              ↓
PHASE 2   Normalizer         ← this doc
              ↓
PHASE 3   Mapper / Metrics
              ↓
PHASE 4   Screener Engine
```

**One-line job description**, straight from doc 04: parse raw objects into consistent entities, periods, units, and fact records — **without applying product metric meaning**. Structure, not interpretation.

**Not in scope here:** Mapper, Metrics, anything that decides what a fact *means*. If you find yourself calculating a ratio or deciding what a fact represents financially, stop — that's the next doc, not this one.

---

## What the Normalizer is allowed to do — and not

Restating doc 04's boundary table exactly, because this is the boundary most likely to get blurred under time pressure:

| Can do | Cannot do |
|---|---|
| Parse SEC/XBRL formats into consistent structures | Decide which XBRL tag "means" revenue, ROIC, etc. — that's the Mapper |
| Standardize units (USD, shares, per-share, pure ratios) | Apply investor-facing formulas or calculations |
| Standardize period structures (fiscal → canonical calendar periods) | Repair, guess, or infer facts the filing didn't actually report |
| Preserve full lineage back to the raw object | Modify or reinterpret the immutable raw evidence itself |

If a task on this list starts to feel like "well, obviously `Revenues` means revenue" — that's the Mapper's decision to make, deliberately, with a version number attached, not the Normalizer's to assume.

---

## Repository

`pipeline/` inside this repo (`scrooner`) — same folder as the Collector, per doc 02's monorepo decision. `src/` layout, extending the existing Collector package rather than starting a new one:

```text
pipeline/
├── src/
│   └── scrooner_pipeline/
│       ├── collector/            # done (Phase 1)
│       ├── normalizer/           # this phase
│       │   ├── identity.py       # 2a — company / listing / filing
│       │   ├── periods.py        # 2b — canonical period resolution
│       │   ├── units.py          # 2c — canonical unit resolution
│       │   ├── facts.py          # 2d — fact extraction from companyfacts JSON
│       │   ├── dedupe.py         # 2e — duplicate/overlap resolution
│       │   ├── restatements.py   # 2f — amendment supersession
│       │   └── derived.py        # 2g — Q4 derivation
│       ├── common/               # existing — config, sec_client (unchanged)
│       ├── db/                   # existing — psycopg connection handling
│       └── jobs/
│           ├── bootstrap.py           # existing (Collector)
│           ├── incremental.py         # existing (Collector)
│           ├── normalize.py           # NEW — Typer command: run normalizer over a company set
│           └── report.py              # existing
├── db/
│   └── migrations/
│       ├── 0001_raw_schema.sql            # done
│       ├── 0002_checkpoint_and_run_tracking.sql  # done
│       └── 0003_core_schema.sql           # NEW — this phase, written at Stage 2a, not before
├── tests/
│   └── golden_companies/          # existing — reused as-is, see Tests below
└── scripts/
```

Same rule as the Collector's `CLAUDE.md`: this is a folder wall, not a repo wall — don't let a Normalizer function reach back and mutate anything in `collector/`, and don't let it write to `raw` (read-only from here on).

Runtime: adds **Polars** to `pipeline/pyproject.toml` (doc 04 locks it for this phase; the Collector deliberately shipped without it). Everything else — httpx, Pydantic, psycopg, Typer, structlog — stays as-is; no new HTTP calls happen in this phase, so Tenacity's retry policies aren't exercised here the way they were in the Collector.

---

## Inputs and outputs

**Input:** raw payloads sitting in the `raw` schema / Supabase Storage, exactly as the Collector left them — `companyfacts` JSON per CIK, `submissions` JSON per CIK, both traceable to a specific collection run via `raw.sec_companyfacts` / `raw.sec_submissions`.

**Output:** populated `core` schema tables (per doc 04's logical database organization).

## Database schema — `core.*`, resolves table-level detail doc 04 left open

Doc 04 locked the schema name (`core`) and the concept list (`company`, `listing`, `filing`, `period`, `unit`, `fact`) but not column-level detail. This resolves it, with one deliberate addition (`concept`) driven by the storage math below — normalizing tag names out of `fact` into their own small lookup table is a real, load-bearing decision on a 500 MB budget, not a nice-to-have.

| Table | Purpose | Key fields |
|---|---|---|
| `core.company` | One row per CIK. Anchors identity — never touched by ticker changes. | `id` (surrogate), `cik` (unique), `company_name`, `created_at` |
| `core.listing` | Ticker/exchange associations — a company can have several simultaneously (GOOGL's 4 tickers; ENB's 16, mostly preferred-share series). Sourced from `raw.sec_submissions`' own `tickers`/`exchanges` arrays, not `raw.company_universe` — verified live 2026-08-15 that submissions is richer (e.g. Block/XYZ's OTC symbol `BSQKZ`, absent from `company_tickers.json`). `effective_from`/`effective_to` exist as columns but are **always null as of Stage 2a** — neither source exposes historical ticker intervals (Block/XYZ's submissions payload lists only its two *current* tickers, not the former `SQ`); populating real intervals is Company Master's job (doc 06 Part 4), not fabricated here. | `id`, `company_id`, `ticker`, `exchange`, `effective_from`, `effective_to` |
| `core.filing` | One row per filing, restricted to `FORM_ALLOWLIST` (10-K/10-Q + `/A` variants, plus 20-F/40-F for the two foreign-filer golden companies — everything else stays in `raw.sec_submissions`, unparsed but inspectable). Links to the raw submission it came from. **No `fiscal_year`/`fiscal_period` columns** — an earlier draft of this table had them; verified live 2026-08-15 that SEC's submissions API carries no such field per filing (only `accessionNumber`/`form`/`filingDate`/`reportDate`), and a single 10-K reports several fiscal years' facts at once anyway, so fiscal year/period is correctly a per-*fact* attribute (`core.period`, Stage 2b), not per-filing. Fixed before any row shipped. | `id`, `company_id`, `accession_number` (unique), `form`, `filing_date`, `period_of_report`, `is_amendment`, `amends_filing_id` (nullable, self-FK for 10-K/A → original, populated Stage 2f), `raw_submission_id` (lineage to `raw.sec_submissions`) |
| `core.period` | Canonical periods. **Identity is the objective calendar span** `(company_id, start_date, end_date, period_type)` — **not** `(fiscal_year, fiscal_period)` as an earlier draft had it. Verified live 2026-08-15: a fact's own `fy`/`fp` describes which *filing* reported it, not the period itself — the same real quarter shows up under different `fy`/`fp` depending on whether it's an original disclosure or a later comparative. `fiscal_year`/`fiscal_period` are instead derived, nullable, best-effort labels (from each company's own observed full-year-end dates + calendar-distance math), excluded from the table's identity — every downstream stage keys off `start_date`/`end_date`/`period_type`, never these two. See `doc/learnings/normalizer-day-02-periods.md`. | `id`, `company_id`, `start_date` (not null — equals `end_date` for instants, so the unique constraint stays NULL-safe), `end_date`, `period_type` (`instant`\|`duration`), `fiscal_year` (nullable), `fiscal_period` (nullable, `FY`\|`Q1`\|`Q2`\|`Q3`\|`Q4`, null for non-standard-length durations like YTD half-year/three-quarter spans) |
| `core.unit` | Small, mostly-static lookup — not repeated as text on every fact row. | `id`, `unit_name` (`USD`, `USD/shares`, `shares`, `pure`, ...) |
| `core.concept` | **New, not in doc 04's example list but implied by "preserve the original tag."** Lookup of `(taxonomy, tag)` pairs — cardinality is a few thousand across all filers, versus tens of millions of fact rows referencing them. | `id`, `taxonomy` (`us-gaap`, `ifrs-full`, `dei`, ...), `tag` (`Revenues`, `Assets`, ...) |
| `core.fact` | Every individual reported value. Still uses the issuer's original tag via `concept_id` — never renamed to a canonical concept here. | `id`, `company_id`, `concept_id`, `unit_id`, `period_id`, `filing_id` (the filing this value is authoritative from), `value` (`numeric`, never `float`), `is_derived` (Q4 flag), `is_authoritative` (2e), `supersedes_fact_id` (nullable, self-FK for 2f), `raw_object_id` (FK to `raw.sec_companyfacts.id` — final lineage hop back to the exact blob), `created_at` |

The key discipline carried over unchanged: a `fact` row after normalization still resolves (via `concept_id`) to `us-gaap:Revenues` or `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`, not "Revenue." Renaming issuer tags into canonical concepts is Mapper work (Phase 3), not this phase.

`value` is `numeric`, not `double precision` — XBRL reports financial figures, and doc 05's correctness-before-breadth principle rules out float rounding error on money, full stop.

---

## Supabase free-tier capacity — measured, not assumed

You're on the Supabase **free plan**: 500 MB database, 1 GB file storage, 5 GB egress/month, auto-suspend after 1 week idle, 2 active projects (confirmed live against the current pricing page, 2026-08-15 — worth re-checking on their dashboard if this doc is read much later, since these numbers move). This caps `core.*`, not `raw.*` — raw payloads already live in Storage (1 GB budget, separate from the 500 MB DB budget), and `raw`'s Postgres footprint is metadata-only (currently 14 MB total DB size for everything).

**Measured directly against your live data, not estimated:** downloaded two real `companyfacts` blobs from your Storage bucket (AAPL and Enbridge, both golden-set companies with long filing histories) and counted actual XBRL datapoints — **~21,000–25,000 facts each**. That's the ceiling case (decade-plus filers using hundreds of distinct tags). A recent-IPO or thinly-tagged small-cap will land far lower, plausibly in the low thousands.

Rough sizing, with the `concept`/`unit` lookup-table design above (so `fact` rows carry small integer FKs, not repeated tag text) and 1–2 supporting indexes:

| Scope | Facts (est.) | Rows | Approx. DB size |
|---|---|---|---|
| Golden-10 set (current test companies, long-history filers) | ~20K/company | ~200K | **~50–80 MB** — comfortably inside 500 MB |
| A curated ~500-company priority set (e.g. large/mid-cap) | 3K–20K/company | ~2.5M–10M | **~0.7–3 GB** — already over the free-tier cap |
| Full collected universe (10,396 companies in `raw.company_universe` today) | 500–25K/company | ~20M–100M+ | **several GB to tens of GB** — nowhere close to fitting |

Conclusion: **the free tier can hold Normalizer output for the golden set comfortably, and essentially nothing wider than that.** This isn't a schema-efficiency problem to engineer away — even the low end of a real priority list blows the 500 MB ceiling.

**Decision (recorded here and added to doc 02's open-decisions table):** build and verify all of Stage 2a–2g against the **golden-10 set only**, on the current free-tier project — zero additional cost, and it's the actual reconciliation set this phase is graded against anyway (see Tests, below). Do **not** upgrade Supabase or attempt a wider backfill until the Normalizer's Definition of Done actually passes against that set. Upgrading before then would be spending against an unproven pipeline — the opposite of doc 05's "evidence before expansion." Once the golden-10 DoD passes, upgrading to Supabase Pro (~$25/mo, 8 GB+ DB, no auto-suspend) is a non-blocking, low-stakes next step — the user has confirmed cost isn't the constraint — but the **exact next company set** (curated few-hundred priority list vs. full universe vs. something between) is a separate, still-open product decision, not something to default into just because Pro removes the size ceiling. Revisit it then, with real per-company averages from the golden-10 run instead of the two-sample estimate above.

**Practical dev-loop note:** re-running Normalizer stages repeatedly during development against a non-idempotent design could quietly accumulate duplicate rows and eat the 500 MB budget faster than the table above suggests. Each stage's writes should be idempotent (upsert or truncate-and-reload for the golden set, same discipline the Collector already applies to `raw.company_universe`) — check `pg_database_size(current_database())` after each stage lands, the same way this planning pass did, rather than assuming. **Confirmed on Stage 2d (2026-08-15):** row-count idempotency isn't the whole story — rerunning the same `ON CONFLICT DO UPDATE` upsert with unchanged values still left 3,315 dead tuples (58MB→77MB) until `VACUUM FULL` reclaimed it (52MB after). Check dead-tuple counts (`pg_stat_user_tables`), not just row counts, during active dev-loop iteration on any stage past 2c.

**Real measurement, not estimate (2026-08-15):** Stage 2d's actual output for the golden-8 (TSM/ENB excluded) — 169,825 fact rows, 52 MB for `core.fact` alone after vacuum, averaging ~21K facts/company. This lands almost exactly at the "golden-10 set" row in the estimate table above (~20K facts/company assumed) — the estimate held up against real data, not just golden-set scale generally but this specific number.

---

## The real problems this phase has to solve

EDGAR's raw XBRL data is internally consistent per filing, but not consistent *across* filings, companies, or years, without deliberate work. These are the specific problems the Normalizer exists to solve — not edge cases to handle "later," but the actual job:

### 1. Fiscal year misalignment

Not every company's fiscal year is the calendar year. A fact tagged for "FY2024" from a company with a June fiscal year-end covers a completely different twelve months than a December-fiscal-year-end company's FY2024. The Normalizer has to resolve every period to actual start/end dates (which XBRL does report per-fact) and make those comparable — not just trust the label.

### 2. Missing Q4 — the classic EDGAR quirk

Companies file 10-Qs for Q1–Q3 and a 10-K for the full year — there is usually no standalone "Q4" filing. A Q4 value has to be **derived** (`Full Year − Q1 − Q2 − Q3`) rather than read directly. This derived value must be clearly flagged as *derived*, not *reported*, in the `fact` table (`is_derived`) — the distinction matters for trust and lineage (doc 05's traceability principle).

### 3. Duplicate and overlapping facts

The same concept, same period, is often reported in more than one filing (e.g. a value shown in a 10-Q and then again as a prior-year comparative in the next 10-K). The Normalizer needs a deterministic rule for which instance is authoritative when they agree (`is_authoritative`), and how to flag it when they don't.

### 4. Restatements and amendments

A 10-K/A or 10-Q/A restates figures from the original filing. The Normalizer must supersede, not duplicate — the corrected value becomes the current fact (`supersedes_fact_id` points back), but the original must remain inspectable (never silently overwritten) so lineage and historical reproducibility (doc 04's "version metric definitions... so historical outputs are reproducible") survive intact.

### 5. Units and sign conventions

XBRL facts carry an explicit unit (`USD`, `USD/shares`, `shares`, `pure`), but sign conventions for things like contra-revenue accounts or accumulated deficits aren't always intuitive. The Normalizer standardizes units; it does not decide whether a negative number "should" be read as a loss for product purposes — that judgment belongs to the Mapper's formula definitions.

### 6. Instantaneous vs. duration facts

Balance-sheet facts are point-in-time ("as of" a date); income-statement and cash-flow facts cover a duration (a quarter or year). Mixing these up is a common source of bad screens later. `core.period.period_type` carries this distinction from day one.

### 7. Taxonomy drift is explicitly out of scope here

The `us-gaap` taxonomy itself changes over time — concept tags get renamed, deprecated, or split (the `Revenues` → `RevenueFromContractWithCustomerExcludingAssessedTax` migration is the canonical example). Resolving *that* — knowing two differently-named tags mean the same canonical thing across years — is the Mapper's job, explicitly, per doc 04's boundary table. The Normalizer's job is only to preserve the tag exactly as reported (via `core.concept`), with its correct period and unit, so the Mapper has clean, comparable raw material to map from.

---

## Tasks, priorities and a 7-day target

Mirrors the Collector's doc 08 cadence. Identity before periods, periods before facts (you can't attach a fact to a period that doesn't exist yet), dedupe/restatement/derivation last since they all operate on facts that must already exist.

| Day | Deliverable | Done when |
|---|---|---|
| **1** ✅ | `db/migrations/0003_core_schema.sql` applied; Polars added to `pyproject.toml`; `normalizer/identity.py` (Stage 2a); `jobs/normalize.py` (`identity`/`golden` commands) | **Done and verified 2026-08-15.** All 10 golden companies → exactly one `core.company` row each (10 total, zero dupes); GOOGL → 4 listings (GOOG/GOOGL/GOOGM/GOOGN); 814 `core.filing` rows across the set (ARCC correctly shows 5 `10-K/A` rows); zero orphaned filings (FK-enforced); rerunning the job produced identical row counts (idempotent/deterministic). DB size after: 14 MB, unchanged — nowhere near the free-tier ceiling. |
| **2** ✅ | `normalizer/periods.py` (Stage 2b) | **Done and verified 2026-08-15.** `period_type` structurally correct for all 1,832 golden-set periods (0 bad instants/durations). AAPL's 19 derived `FY` end dates match the public record exactly (2007-09-29 → 2025-09-27); AAPL/MSFT/NKE FY2024 quarter-end dates spot-checked against each company's actual reported fiscal calendar and matched exactly; JPM (calendar FYE) correctly degenerates to plain Jan–Dec quarters. "Unclassified" (non-quarter, non-FY) durations cluster cleanly at ~180d/~272d (YTD spans) with no stray ~90-day values missed. Idempotent rerun confirmed (identical row count). See `doc/learnings/normalizer-day-02-periods.md` for the `fy`/`fp` design correction found along the way. |
| **3** ✅ | `normalizer/units.py` (Stage 2c) | **Done and verified 2026-08-15.** 29 raw unit strings across the golden-10 → 28 canonical `core.unit` rows (case-fold only, e.g. `Segment`/`segment` → one row for the same real unit; deliberately did NOT merge textually-different-but-structurally-similar custom units like `Store` vs `Job` counts, since that would be a Mapper-level meaning judgment, not string standardization). Zero case-duplicate rows confirmed directly. Idempotent rerun confirmed (identical row count). See `doc/learnings/normalizer-day-03-units.md`. |
| **4** ✅ | `normalizer/facts.py` (Stage 2d) | **Done and verified 2026-08-15.** 178,811 raw datapoints across the golden-8 (TSM/ENB excluded per the Day-7 scope note below) → 169,825 written, 8,986 skipped (facts tied to non-MVP-scope filings: 8-K/424B/DEF14A/S-8/S-3 — checked which concepts these carry and confirmed none are financial-statement line items doc 03 needs). AAPL Q1 FY2024 revenue, MSFT Q3 FY2024 net income, and JPM FY2023 net income all reconciled exactly against public record, stored as exact `Decimal` (not float). Zero unit/period lookup misses — cross-confirms Stages 2b/2c were exhaustive. Idempotent rerun confirmed by row count, but surfaced real `ON CONFLICT DO UPDATE` tuple bloat (58MB→77MB despite unchanged row count) — fixed with `VACUUM FULL` (52MB after). See `doc/learnings/normalizer-day-04-facts.md`. |
| **5** ✅ | `normalizer/dedupe.py` (Stage 2e) | **Done and verified 2026-08-15.** 48,360 duplicate `(company, concept, unit, period)` groups across the golden-8; 45,182 agreed (earliest-filed marked authoritative, deterministic) and 3,178 (~6.6%) genuinely conflicted (all rows marked non-authoritative — flagged, not silently resolved). Verified on both a known agreed case (AAPL Q1 FY2024 revenue) and a known conflict (JPM `DerivativeNotionalAmount`, a real silent revision with no `10-K/A` on file). Global consistency check across all 48,360 groups: zero with a wrong authoritative-row count. Idempotent rerun confirmed. See `doc/learnings/normalizer-day-05-dedupe.md`. |
| **6** ✅ | `normalizer/restatements.py` (Stage 2f) | **Done and verified 2026-08-15.** 43 amendments across the golden-10; 36 linked to their original filing (rule verified against all of them, not assumed), 7 correctly left unmatched (all pre-2002, original not in captured history). 681 fact pairs superseded. ARCC's 5 real `10-K/A`s verified end-to-end: original rows remain queryable (`is_authoritative=false`), amendments authoritative with `supersedes_fact_id` populated — turned out to be routine cover-page updates, not P&L restatements, so also verified the mechanism against genuine material restatements found elsewhere in the golden set (JPM's EPS restated $1.31→$1.19/$1.20; AAPL's FY2008 assets restated $39.572B→$36.171B, likely tied to its real historical options-backdating restatement). Idempotent rerun confirmed. See `doc/learnings/normalizer-day-06-restatements.md`. |
| **7** ✅ | `normalizer/derived.py` (Stage 2g) + end-to-end DoD proof | **Done and verified 2026-08-15.** 4,397 Q4 values derived across the golden-8 (14,907 candidate groups; 10,336 incomplete — missing one of FY/Q1/Q2/Q3, correctly skipped; 174 already directly reported, correctly left alone). AAPL FY2024 Q4 revenue verified by hand: $391,035,000,000 − $119,575,000,000 − $90,753,000,000 − $85,777,000,000 = **$94,930,000,000**, matching Apple's real reported figure. Full Definition of Done proven item-by-item with live evidence, not asserted — see [doc 09b](09b_Normalizer_Definition_of_Done_Evidence.md). Fixed a real per-group round-trip design bug along the way (SSL timeouts on large companies) by matching the batched load-then-write shape every other stage already used. See `doc/learnings/normalizer-day-07-derived-q4.md`. |

TSM (20-F, `ifrs-full`) and ENB (40-F) run through Stages 2a/2b for identity/period structure (they're real filings, no reason to skip that), but are **excluded from Stage 2d fact-reconciliation acceptance** — doc 02's 20-F/40-F scope question is still open, and normalizing their facts in earnest would be treating them as first-class ahead of that decision. Keep them in the fixture set as identity/period edge cases only, same restraint doc 02 already applies to the Collector.

---

## Tests — golden-company set

Reused as-is from the Collector (`pipeline/tests/golden_companies/companies.json`) — it's the same set, doing new work. Per doc 05's data-quality methodology, here's what each company now stresses on the *Normalizer* side specifically:

| Ticker | Normalizer edge case exercised |
|---|---|
| AAPL | Non-calendar FYE (Sep) period resolution |
| MSFT | Non-calendar FYE (Jun) period resolution, second independent case |
| JPM | High filing volume — dedupe/overlap resolution at scale |
| GOOGL | One `core.company`, four `core.listing` rows — identity normalization's core case |
| XYZ | Ticker change (SQ → XYZ) — `listing.effective_from/to`, not a new `company` row |
| RDDT | Recent IPO — short history, tests the low end of fact volume |
| TSM | `ifrs-full` taxonomy — identity/period only, per the Day-7 scope note above |
| ENB | 40-F — identity/period only, per the Day-7 scope note above |
| ARCC | Real 10-K/A — restatement supersession (Stage 2f)'s primary case |
| NKE | Non-calendar FYE (May), third independent case, no shared code path with AAPL/MSFT |

Same discipline as the Collector: every edge case found later gets added to this fixture set, never fixed silently.

---

## Definition of Done

Mirroring the Collector's Definition of Done in doc 06 — this is not "the schema exists," it's a behavioral bar, graded against the golden-10 set per the Supabase capacity decision above (not "the full collected universe," which doc 08's original draft of this line assumed before the capacity check happened).

**Input:** raw `companyfacts` and `submissions` payloads for the golden-company set.

**Output:** for every golden-set company —
```text
Canonical period records (with correct start/end dates and duration/instantaneous type)
Canonical unit records
Fact records under original issuer tag names (via core.concept), linked to period + unit + filing
Restatement history preserved, not overwritten
Derived Q4 values, explicitly flagged as derived
Full lineage: every fact traceable back to its raw object and filing
```

**Operationally, it can:**

- reprocess a company from raw data and get the same normalized output (determinism)
- handle a non-calendar fiscal year correctly
- handle a restated company without losing the original figures
- flag, not silently resolve, any conflicting duplicate fact it can't confidently reconcile
- be re-run incrementally as new raw data arrives, without reprocessing the entire golden set every time

Then — and only then — does the team make the wider-coverage decision flagged above, and eventually move to the Mapper & Metrics Engine.

---

## What this phase does *not* decide

Two things are explicitly deferred past the Normalizer, both flagged as open decisions in doc 02:

- **The V1 metric list and formula definitions** — **resolved 2026-08-15**, locked in doc 02 (18 metrics, ~9 operators, sourced from [doc 10](../requirements/10_scrooner_required_data_points.md)'s P0 inventory). This plan still doesn't *use* that list — it just needs to make sure the underlying facts those formulas will need (revenue, margins, cash flow lines, share counts, debt, etc.) come out of this phase clean and comparable. Formulas are locked at the canonical-concept level only; which XBRL tag(s) feed each concept is still Mapper's decision, per doc 04's boundary table.
- **Concept-to-canonical-metric mapping** (which issuer tags across which taxonomy versions equal "revenue," "ROIC inputs," etc.) — Mapper's job, Phase 3, not this one.
- **Company-universe breadth beyond the golden-10** (this doc, new) — default is golden-10 on the free tier now; wider coverage (curated list vs. full universe) is deliberately left open until the golden-10 DoD passes, per the capacity section above.

---

## Gotchas to watch for, specifically

- Don't let "normalize" quietly become "interpret." If a normalizer function needs to know that a number represents *profitability*, it's drifted into Mapper territory.
- Don't overwrite raw facts in place when a restatement lands — always add, never destructively edit, so lineage survives (doc 04's security/correctness controls).
- The golden-company set already includes a non-calendar fiscal year (three, independently), a restated company, and two genuinely messy foreign-filer histories — doc 05's data-quality methodology exists precisely so the messy cases get caught here, not in production. Don't swap it for something easier.
- Keep this phase's scope to what doc 03's MVP actually needs (10-K/10-Q for US domestic filers) — resist normalizing 20-F/40-F foreign-issuer quirks past identity/period, or segment-level XBRL data, until there's an explicit product decision to support them.
- Don't upgrade Supabase or start a wider backfill "just to be safe" before the golden-10 DoD passes — see the capacity section. The upgrade itself is cheap and not the constraint; building against an unproven pipeline is.
- Re-check current Supabase free-tier numbers on their dashboard/pricing page if this doc is read much later — the 500 MB/1 GB/5 GB figures above were confirmed live on 2026-08-15 but plans change.
