# 13 — Scrooner Company Master / Market Data: Execution Plan

Mapper & Metrics is done. This is the concrete build plan for Part 4 (Company Master / Market Data) — completing company identity (ticker changes, exchange, sector, active/stale status) and, once a market-price vendor is chosen, ingesting the price data the 6 remaining locked V1 metrics need. It does not relitigate anything already locked in doc 02/03/04/06 — it operationalizes them into something buildable, the same way docs 08/09/11 did for the Collector, Normalizer, and Mapper. If anything here conflicts with those, they win; fix this doc, not your assumptions.

> **Status:** 4a Canonical (2026-08-16). 4b Canonical **for its mock-data build** (2026-08-17) — `core.market_price` built and loaded with clearly-flagged MOCK prices (`is_mock=true`, `source='mock'`) to unblock the pipeline's shape ahead of a real vendor pick, per explicit user direction. **This does not close doc 02's market-price vendor decision** — that decision is still open, and this table must be cleared of mock rows (not appended to) before any real vendor data lands in it. Evidence: [doc 13b](13b_Company_Master_4a_Definition_of_Done_Evidence.md). **Owner:** Founder / Product · **Review:** When a real vendor is chosen, or when Company Master's implementation changes in a way that would invalidate this plan.

---

## Where this sits

```
PHASE 1   Collector          ✅ done
              ↓
PHASE 2   Normalizer         ✅ done
              ↓
PHASE 3   Mapper / Metrics   ✅ done
              ↓
PHASE 4   Company Master     ← this doc (4a buildable now, 4b blocked on vendor pick)
              ↓
PHASE 5   Screener Engine
```

**One-line job description**, from doc 04: *"Company Master connects CIK, ticker, exchange, identity changes and market-price inputs."* Doc 04's boundary table never gave Company Master its own row the way it did the Collector/Normalizer/Mapper/AI-query/Web-app — that gap is resolved below, the same way doc 11 had to resolve `analytics`'s under-specified column detail before Mapper could build.

**Not in scope here:** Screen predicate evaluation, AI query parsing, computing the 6 price-dependent metrics themselves. If you find yourself writing a filter condition or a `metric_value` insert, stop — that's the Screener's or Mapper's job, not this one's (see "What this phase does not decide" and the boundary table below).

---

## Split: 4a (buildable now) and 4b (blocked on a decision only the user can make)

Doc 02 gates the market-price vendor/delay decision as due "before Company Master/Market Data build" — a real recurring-cost, ToS-bound choice (which API, what budget, what delay tolerance), not something to assume the way a formula detail or a schema name can be resolved by checking live data. Rather than block this whole phase on that one decision, this plan follows the same pattern Mapper used for its own 6 price-dependent metrics: **define and scope everything, build the part that doesn't need the open decision, leave the rest formula-locked and ready.**

| Sub-phase | Scope | Blocked on |
|---|---|---|
| **4a. Identity completion** | Ticker-change history, exchange, SIC/sector classification, active/stale status — all sourced from data the Collector **already has stored**, zero new fetches | Nothing — buildable immediately |
| **4b. Market-price ingestion** | Daily EOD/delayed price per company, written to `core.market_price` | Doc 02's vendor decision **for real data**; unblocked for mock data by explicit user direction (2026-08-17) |

**4a is this doc's original build plan; 4b's real-vendor half is still blocked.** 4b's schema (below) has now actually been built and loaded — but with MOCK data (`is_mock=true`, `source='mock'`), not a real vendor, specifically so the rest of the pipeline has something to build and test against without waiting on doc 02's decision. **This is a development unblock, not a resolution of that decision** — swapping in real data is a contained follow-on (see `company_master/market_price.py`'s module docstring), not a rebuild, but it hasn't happened and shouldn't be assumed done. Still matches Mapper's own "formula-lock all 18, compute only the 12 that don't need Company Master" discipline in spirit: the shape is real, the data underneath one specific input isn't yet.

---

## What Company Master is allowed to do — and not

Doc 04's boundary table has no Company Master row; this resolves it, following the same shape as the other four components:

| Can do | Cannot do |
|---|---|
| Maintain company identity: ticker/exchange history, sector/SIC classification, active/stale status | Modify immutable raw evidence (`raw`) or reinterpret the Normalizer's `core.fact`/`core.period`/`core.unit` structures |
| Ingest and store market-price inputs (4b: daily EOD/delayed price) | **Calculate versioned metrics** — Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield stay Mapper's job (`analytics.metric_definition.requires_price=true`, already defined in Stage 3c) even after 4b supplies the missing price input. Company Master supplies the input; it does not compute the output. |
| Extend `core.company`/`core.listing` (it owns exactly the columns the Normalizer's own Day 2/Stage-2a comments flagged as "Company Master's job, not this phase's to fabricate") | Generate screens, evaluate filter predicates, contain AI, or expose frontend APIs |

Writes are restricted to `core` — same schema the Normalizer writes, because Company Master is completing identity work the Normalizer deliberately left half-built (see next section), not starting a new one. **Company Master never writes `analytics`.** If a task starts to feel like "let's just insert a `metric_value` row for Market Cap while we're in here," that's scope creep across a boundary this project has now held four times — hold it a fifth.

---

## The real problem this phase has to solve — checked live, not assumed

Same discipline as docs 08/09/11: checked the actual stored data before writing this plan.

### 1. Everything 4a needs is already sitting in `raw.sec_submissions`, unparsed

Fetched Block's (CIK `0001512673`) already-stored submissions payload directly from Supabase Storage — no new SEC request. It carries, and `core.company`/`core.listing` currently discard:

```text
tickers: ['XYZ', 'BSQKZ']
exchanges: ['NYSE', 'OTC']
formerNames: [{"name": "Square, Inc.", "from": "2011-03-02T05:00:00Z", "to": "2021-12-08T05:00:00Z"}]
sic: 7372 (Services-Prepackaged Software)
stateOfIncorporation: DE
entityType: operating
category: Large accelerated filer
```

GOOGL's (CIK `0001652044`) confirms `tickers`/`exchanges` are parallel, index-aligned arrays: `tickers: ['GOOGL','GOOG','GOOGM','GOOGN']`, `exchanges: ['Nasdaq','Nasdaq','Nasdaq','Nasdaq']` — exactly the shape `core.listing`'s existing `(company_id, ticker, exchange)` design already expects, confirming the Normalizer's Stage 2a schema choice was right; it just never got fed `sic`/`stateOfIncorporation`/`entityType`/`category`/`formerNames` at all. **4a's core.company/core.listing work is a parsing task over data already in Storage, not a new ingestion pipeline** — no new Collector work, no new SEC rate-limit exposure, no new golden-set fetch.

### 2. Ticker-change *dates* have no first-party EDGAR source — but two real signals cover it, imperfectly and honestly

Confirmed (again) what the Normalizer's Stage 2a comment already found: `tickers`/`exchanges` show only the **current** state, never historical intervals. There is no `tickerHistory` field. Two usable signals, neither perfect, both better than guessing:

- **`formerNames`, with real `from`/`to` dates.** Block/Square's case: the name changed from "Square, Inc." to "Block, Inc." exactly around the same window (Dec 2021) as its real, publicly known ticker change (SQ → XYZ). This is a genuine EDGAR-sourced date, but it is a **proxy** — a name-change date is not guaranteed to coincide with a ticker-change date (a company can rename without a new ticker, or vice versa). Any `effective_from` derived this way must be flagged as derived-from-name-change, not asserted as an exact ticker-change date — same "traceable, not silently guessed" discipline as `core.fact.is_authoritative` and Mapper's `is_null_reason`.
- **Forward detection via `raw.sec_submissions`'s own append-only history.** The Collector already re-fetches submissions on every incremental run and never overwrites a prior row (`raw.sec_submissions` has no unique constraint forcing an upsert — confirmed live: Block already has 2 stored snapshots from two runs minutes apart on 2026-08-13). Comparing the current run's `tickers` array against the immediately prior stored snapshot for the same CIK detects a real change **the moment it's observed**, with an exact, non-proxy date — the date of observation. This only dates changes going forward from whenever 4a starts running; it cannot retroactively date a change that happened before this project existed. **No new raw-layer table needed for this — `raw.sec_submissions`'s existing append-only design already is the change-history mechanism**, the same kind of "we already have the mechanism, just not the query" finding Mapper's own scaling section made about `core.concept`.

A ticker with no known start date (pre-existing at the time 4a starts watching, no former-name proxy available) gets `effective_from = null` with a recorded `source = 'unknown'` — an honest null, not a fabricated date. This mirrors exactly how the Normalizer left `core.listing.effective_from/effective_to` null rather than guess (Stage 2a's own comment), and how Mapper nulls a metric rather than falling back to a wrong-but-plausible number.

### 3. Sector classification: doc 10 already answered this — SIC is the fallback, GICS is out of scope

Doc 10 (§12): *"Sector/Industry classification — Use SIC code from EDGAR company record as a fallback; GICS is preferred but is a licensed taxonomy (not on EDGAR)."* Not a new decision — `sic`/`sicDescription` are sitting in every golden company's already-stored submissions payload (verified above for Block: `7372`, "Services-Prepackaged Software"; JPM/ARCC's very different SIC codes, given a bank and a BDC, would be a useful spot-check on Day 1). GICS stays explicitly out of scope, same as doc 10 already decided — don't relitigate it here.

### 4. Active/stale status has no explicit EDGAR flag — an honest heuristic, not a guess

No boolean "delisted" field exists anywhere in the submissions payload (checked directly: `category` is a filer-size classification — "Large accelerated filer" — not a listing-status flag). SEC doesn't republish delisting status on this endpoint. The only honest, checkable signal available without a new vendor: **how long since the company's most recent 10-K/10-Q** (`core.filing`, already populated by the Normalizer) — a company required to file quarterly that hasn't in ~18-24 months has very likely delisted, gone private, or merged, but this project has no way to confirm *which*. Status gets three states, not two: `active` (recent filing), `stale` (no recent filing, reason unconfirmed), `unknown` (insufficient filing history to judge, e.g. a very new company). **Never `delisted`** — that would claim certainty this signal doesn't have. Consistent with the same discipline used everywhere else in this project: a null/uncertain state is a real, traceable outcome, never a confident-looking guess.

### 5. The 6 price-dependent metrics reduce to exactly one missing number: price

Checked against doc 02's locked formula table: Market Cap = Shares Outstanding × Price; P/E = Price ÷ Diluted EPS; P/S = Market Cap ÷ Revenue; P/B = Market Cap ÷ Stockholders' Equity; Dividend Yield = Dividends/Share ÷ Price; FCF Yield = FCF ÷ Market Cap. **Every input except Price is already EDGAR-sourced and already flowing through Mapper's `analytics.canonical_fact`** (`shares_outstanding`, `diluted_eps` via existing concepts, `dividends_per_share`, `revenue`, `stockholders_equity`, `fcf`) — Stage 3a mapped `shares_outstanding`/`dividends_per_share` back on Mapper Day 1 specifically anticipating this. **4b's entire job, once a vendor is chosen, is "store one EOD price per company per trading day"** — not a broad market-data integration. Worth recording precisely because it bounds 4b's eventual scope tightly, the same way Mapper's Frames-API check bounded concept-mapping's scaling problem before assuming it was bigger than it is.

---

## Database schema — extending `core`, not a new schema

Company Master completes identity structures the Normalizer already created but deliberately left incomplete (see `core.listing`'s own Stage 2a comment: *"Populating real effective_from/effective_to needs a source the Collector doesn't fetch; that's Company Master's job... not this phase's to fabricate"*). No new schema — `core` already owns "normalized identities."

| Table | Change | New/changed columns |
|---|---|---|
| `core.company` | Extend | `sic_code` text, `sic_description` text, `state_of_incorporation` text, `entity_type` text, `filer_category` text, `status` text check (`active`\|`stale`\|`unknown`), `status_as_of` date, `status_reason` text (e.g. `no_filing_since:2023-11-15`) |
| `core.listing` | Extend | `source` text check (`submissions_snapshot`\|`former_names_backfill`\|`unknown`) — how `effective_from`/`effective_to` were derived, so a downstream consumer can tell an observed change from a proxied one |
| `core.company_name_history` | **New table** | `id`, `company_id` (FK), `company_name`, `effective_from`, `effective_to` — direct 1:1 capture of `formerNames` plus the current name as the still-open final interval. Both useful standalone (a company page's "formerly known as") and as 4a's own ticker-change-date proxy signal (§2 above) |
| `core.market_price` | **Built 2026-08-17** (`db/migrations/0006_market_price_schema.sql`), currently loaded with MOCK data only | `id`, `company_id` (FK), `price_date`, `close_price` (numeric, `Decimal`), `currency`, `source` (`'mock'` for every current row — never a real-sounding vendor name), `is_mock` (hard boolean, not just a string convention — a query can't accidentally treat mock rows as real by a spelling mistake), `fetched_at`. Deliberately minimal — EOD close only, matching doc 02's "no real-time promise" default; add fields only if a chosen real vendor's actual response shape demands it, not speculatively |

300 mock rows loaded across the golden-10 (30 trading days each, seeded per `(cik, end_date)` for reproducibility — confirmed byte-identical on rerun). **Every row must be cleared before any real vendor data lands in this table** — mock and real rows must never coexist for the same company/date.

---

## Build sequence (4a only)

Vertical slices, per doc 05's build method — each stage runnable and gate-checked before the next starts, same discipline as docs 09/11.

| Stage | Deliverable | Gate before moving on |
|---|---|---|
| 4a-1. Identity fields | ✅ **Done and verified 2026-08-16.** `db/migrations/0005_company_master_schema.sql`; `company_master/identity.py` parses `sic`/`sicDescription`/`stateOfIncorporation`/`entityType`/`category` out of each golden company's already-stored `raw.sec_submissions` payload into `core.company`. 9/10 companies got a populated SIC code (real, checked-live diversity: JPM `6021`, NKE `3021`, AAPL `3571`, ENB `4610`); ARCC's genuine `sic=''` in EDGAR's own payload confirmed directly, not a parsing bug. Zero new SEC fetches. |
| 4a-2. Name history + ticker-change dating | ✅ **Done and verified 2026-08-16.** `company_master/history.py`. Two real bugs caught: a blanket former-names-proxy default produced wrong dates for 27/38 listing rows (AAPL/NKE never changed ticker but got proxied anyway; RDDT/JPM proxied from an EDGAR record-touch artifact, not a real rename) — fixed by requiring explicit per-CIK confirmation, mirroring Mapper's approved/provisional/rejected discipline; a `NULL`-valued `ON CONFLICT` key silently duplicated rows on rerun for every company with no former-names history — fixed with delete-then-reinsert, the same pattern already proven in Mapper. Block's Square→Block interval reproduces EDGAR's dates exactly (`2011-03-02`→`2021-12-08`); GOOGL's 4 simultaneous tickers each got their own row. See `doc/learnings/company-master-4a.md`. |
| 4a-3. Status inference + end-to-end DoD proof | ✅ **Done and verified 2026-08-16.** `company_master/status.py`; `doc/13b` DoD evidence, mirroring 08b/09b/11b. All 10 golden companies correctly `active`, each `status_reason` traceable to a real `core.filing.filing_date`. `delisted` is not a representable schema value at all — `stale`/`unknown` is the honest ceiling. |

Three stages, not six-to-seven — 4a's real scope (parsing already-stored fields, dating a table the Normalizer already built) is genuinely smaller than a from-scratch phase, and padding it to look like Collector/Normalizer/Mapper's size would be inventing work doc 05's "kill scope aggressively" principle exists to prevent.

---

## Tests — golden-company set (reused, no new companies needed)

| Ticker | What it stresses for Company Master |
|---|---|
| XYZ (Block) | Ticker change (SQ → XYZ, Dec 2021) *and* a co-occurring name change (Square, Inc. → Block, Inc.) — the exact case §2's former-names proxy signal is built for |
| GOOGL | Multiple simultaneous tickers on one CIK, parallel `tickers`/`exchanges` arrays — confirms `core.listing`'s existing per-ticker row design (no schema change needed there, just dating) |
| JPM, ARCC | Genuinely different SIC codes from a product company (bank vs. BDC vs. AAPL/NKE/MSFT's various codes) — a real diversity check on sector classification, not just non-null |
| AAPL, MSFT, NKE | Baseline case: single stable ticker throughout the observed history, `core.listing` should show exactly one row each with `source='unknown'` (pre-existing, no observed or proxied change) |
| RDDT | Short public history (2024 IPO) — a genuine case where `status='active'` should be trivial to confirm (very recent filings) and there's no former-names history to test against, a useful "nothing to report, correctly nothing reported" control |
| TSM, ENB | Same scope-exclusion as every prior phase — 20-F/40-F, pending doc 02's still-open decision. Identity fields (SIC, tickers) still populate fine since `raw.sec_submissions` has them regardless of form-type scope; just don't let them become first-class in any way beyond that |

---

## Definition of Done (4a)

Mirroring docs 08/09/11's bar — not "the schema exists," a behavioral one.

**Output:** for every golden-set company —
```text
SIC code/description, state of incorporation, entity type, and filer category populated
    from data already in raw.sec_submissions -- no new SEC fetch
Full name-change history captured in core.company_name_history, matching formerNames exactly
core.listing has one correctly-dated row per (company, ticker) the company has ever
    reported under, with an honest source flag -- never a fabricated effective_from/to
core.company.status reflects real filing recency, with status_reason traceable to the
    actual core.filing row(s) it was derived from
```

**Operationally, it can:**

- reprocess a company and get the same identity fields (determinism)
- detect a ticker change the moment it's next observed in an incremental Collector run, without needing a new raw-layer table or a new fetch
- distinguish an observed ticker-change date from a former-names-proxied one from a genuinely unknown one — never presenting a proxy or a guess as if it were a directly observed fact
- leave `status` as `unknown`/`stale` rather than assert `delisted` without a confirming source
- be re-run incrementally as the Collector produces new submissions snapshots, without reprocessing the entire golden set every time

Then — and only then — 4b (market-price ingestion, once a vendor is picked) and, separately, the small follow-on task of re-opening `mapper/calculate.py` to actually compute the 6 price-dependent metrics once `core.market_price` exists.

---

## What this phase does *not* decide

- **Market-price vendor and delay** — still open in doc 02, deliberately not decided here (see the split rationale above). 4b's *schema and ingestion shape* are now built and exercised against mock data (2026-08-17), but the actual vendor pick is untouched by that — don't read the mock build as this decision having been made.
- **Computing Market Cap/P/E/P/S/P/B/Dividend Yield/FCF Yield** — Mapper's job per doc 04's boundary table, not Company Master's, even once 4b supplies the missing price input. Tracked as a short follow-on to the (frozen) Mapper codebase, not folded into this phase's own Definition of Done.
- **GICS sector taxonomy** — doc 10 already resolved this (SIC fallback only); not reopened here.
- **Confirmed delisting status** — genuinely undecidable from data this project has access to without a new vendor; `stale`/`unknown` is the honest ceiling for 4a, not a gap to fix later without a new data source.
- **20-F/40-F treatment** — stays out of scope here exactly as it did in the Normalizer and Mapper, pending doc 02's still-open decision.

---

## Repository footprint

Within `pipeline/` (this repo), extending the existing `src/scrooner_pipeline/` package:

```text
pipeline/
├── src/
│   └── scrooner_pipeline/
│       ├── collector/        # done (Phase 1)
│       ├── normalizer/       # done (Phase 2)
│       ├── mapper/           # done (Phase 3)
│       ├── company_master/   # this phase
│       │   ├── identity.py       # 4a-1 -- sic/state/entity/category from stored submissions
│       │   ├── history.py        # 4a-2 -- name history + ticker-change dating
│       │   ├── status.py         # 4a-3 -- active/stale/unknown inference
│       │   └── market_price.py   # 4b (mock) -- MOCK EOD prices only; see its module docstring before swapping in a real vendor
│       ├── common/            # existing, unchanged
│       ├── db/                 # existing, unchanged
│       └── jobs/
│           └── company_master.py   # NEW -- Typer CLI, mirrors jobs/map.py's per-stage command pattern
├── db/
│   └── migrations/
│       ├── 0005_company_master_schema.sql   # NEW -- 4a (core.company/core.listing extensions + core.company_name_history)
│       └── 0006_market_price_schema.sql     # NEW -- 4b (core.market_price; currently mock data only)
└── tests/
    └── golden_companies/       # reused unchanged
```

---

## Gotchas to watch for, specifically

- Don't let a former-names-derived ticker-change date get stored indistinguishably from an actually-observed one — the `source` column exists precisely so a downstream consumer (a company page showing "ticker changed on X") can decide whether to show that date with confidence or hedge it. Losing that distinction on write is a real, quiet correctness regression, not a cosmetic one.
- Don't infer `status='delisted'` from a filing gap, ever — this project has no data source that actually confirms delisting, and asserting it anyway would be exactly the "wrong-but-plausible" failure mode Mapper's Day 4 ROIC bug was fixed to prevent. `stale` is the correct, honest ceiling.
- **`core.market_price` currently holds only mock data (2026-08-17).** Every consumer of this table (including any future follow-on into Mapper's `calculate.py` to compute the 6 price-dependent metrics) must either filter `is_mock=false` before treating a value as real, or be explicitly, visibly operating in a development/demo context. Don't let a mock price reach anything presented to a real user as true — that's exactly the fabricated-data failure mode this project's whole trust model exists to prevent.
- Don't let "compute the 6 price-dependent metrics" creep into this phase — that's `analytics.metric_value`, Mapper's schema and Mapper's boundary (doc 04), even now that `core.market_price` has rows (mock ones) to compute from.
- Before swapping in a real vendor: clear `core.market_price` of mock rows (`delete where is_mock=true`) for whatever scope the real data covers — don't let mock and real rows coexist for the same company/date, and don't assume appending real rows on top of mock ones is safe.
- Re-parsing `raw.sec_submissions` for identity fields needs the same batch-load-then-write discipline as every other per-company job in this project (doc 04's correctness controls) — load each company's latest stored payload once, write once, never a query-per-field-per-company loop.
