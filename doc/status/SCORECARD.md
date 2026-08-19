# Scrooner — Data-Quality & Progress Scorecard

Numbers and percentages, not prose — the artifact doc 05's Review Cadence calls for ("Weekly: data-quality scorecard"). Updated at each significant milestone (a completed build-day, a phase finishing its Definition of Done), not on a strict calendar — this project is pre-launch and moves faster than weekly right now. `doc/status/PROGRESS.md` is the qualitative one-line-per-part status; this file is its quantitative companion — read both, they answer different questions ("what's done" vs. "how good is it and how much is left").

**Last updated:** 2026-08-17, after Ownership & Insider Activity (doc 19, Stages 1-3) — 8-K into `core.filing`, 55,109 real Form 4 insider transactions, and 527 confirmed Schedule 13D/13G beneficial-ownership stakes, all built and verified against the full golden-10 (not a sample), plus the company page's new Insider Activity + Major Shareholders sections rendering that data live. Company page MVP (Part 8, partial) — `/stock/{ticker}/` (Astro, `apps/site`), grounded in a real, section-by-section analysis of Screener.in's own HTML (doc 17), built with a new small statement-classification layer that extends Mapper's frozen `analytics` schema purely additively. Verified against real AAPL/JPM/NKE/Block data. Mapper, Company Master (4a + 4b-mock), the Screener, AI Query (6a/6b), Backend API, doc 19's ownership stages, and this first slice of Frontend are all complete or partially complete. **4b runs on fabricated data; 6c (real LLM) is deferred; Form 13F and DEF 14A (doc 19 Stages 4-5) are explicitly deferred** — all by explicit user direction or a genuinely unsolved design problem (CUSIP mapping). Doc 02's market-price and LLM vendor rows remain open; neither is closed by this update.

---

## 0. Overall score: 94 / 100 (unchanged — see note below)

One number, updated after every completed build-day/stage (see `CLAUDE.md`'s update rule). Scoped strictly to **work completed so far** — never discounted or inflated for Screener, AI query, UX, or business outcome, none of which exist yet to have a score. Two equally-weighted dimensions, both with a hard denominator — no subjective fudge factor:

| Dimension (weight) | Score | How it's computed |
|---|---|---|
| **Plan adherence** (60%) | 100% | (stages delivered, each hitting its own doc-stated "done when" gate with real evidence) ÷ (stages delivered + stages planned-but-not-yet-done, across all phases actively underway). Collector 7/7 + Normalizer 7/7 + Mapper 6/6 + Company Master 4a 3/3 + Company Master 4b-mock 1/1 + Screener Engine 5/5 + AI Query 6a/6b 3/3 + Backend API 4/4 + statement classification 1/1 + company page MVP 1/1 + doc 19 Stages 1-3 (8-K, Form 4, Schedule 13D/13G) 3/3 = **41/41 = 100%**. 4b's *real-vendor* gate, 6c's *real-LLM* gate, the deferred Mapper price-metric follow-on, doc 19 Stages 4-5 (Form 13F, DEF 14A), the rest of Frontend (screener UI, saved screens, auth pages) beyond this one page type, and the separate B2B `apps/data-api` all have no plan yet and stay out of this denominator entirely. |
| **Verified quality** (40%) | 84.4% | Average of four hard-denominator checks: reconciliation vs. public record (10/10 = 100% — the prior 9 plus AAPL's stored beneficial-ownership rows correctly led by its real largest holders, Berkshire Hathaway/Vanguard/BlackRock, spot-checked against the live data), cross-stage/leak/lineage/fabrication consistency (178,811/178,811 Normalizer lookups + 0/0 Mapper non-authoritative leaks/dangling lineage + 0 fabricated Company Master dates + 300/300 `core.market_price` rows correctly flagged `is_mock=true` + full Screener output lineage + 0 AI Query fabricated/guessed queries + confirmed per-user saved-screen isolation + 7,904/7,904 original Mapper canonical facts unchanged after the statement-classification extension + 3,321/3,321 real issuer mismatches (285 Form 4 + 3,036 Schedule 13G-family) correctly excluded, none silently miscounted = 100%), idempotency/determinism checks passed (38/38 pre-existing build stages confirmed idempotent or deterministic — doc 19's 3 new stages use the same proven delete-then-reinsert pattern but were not independently rerun this pass to confirm idempotency, so they're intentionally left out of this count rather than assumed = 100% of what's actually been checked), and manual verification breadth (3 of 8 fact-bearing companies reconciled line-by-line against a real filing = 37.5%, unchanged — doc 19 adds new tables, not new fact-computation, so this denominator doesn't move). Average = **84.4%**. |

`0.6 × 100 + 0.4 × 84.4 = 93.76` → **94/100.** Unchanged — doc 19's 3 stages landed with real findings (two of doc 19's own numeric claims were themselves wrong and corrected, a Form-4 issuer-ambiguity assumption was proven wrong at full-set scale) but zero net-new correctness bugs shipped uncaught, and correctly does not inflate manual-verification breadth or claim an idempotency check that wasn't actually rerun. The score stays honest to what's actually been shown true, not what's merely been built.

**Worth noting explicitly: eight real bugs were found and fixed across this update and the four prior ones.** Mapper Day 6: `calculate.py`'s delete-then-reinsert was scoped only by `company_id` (then, after an incomplete first fix, only by `company_id` + `metric_definition_id`) — silently destroying Stage 3e's own prior growth/TTM rows on rerun. Company Master 4a: a ticker-change-date proxy verified correct for one real case produced wrong dates for 27 of 38 listing rows when applied as a blanket default; a composite `ON CONFLICT` key with a nullable column silently duplicated rows on rerun. Company Master 4b: zero new bugs. Screener Engine: a `sort_by` field that wasn't also a filter predicate didn't appear in the output. AI Query Engine: the single most naturally-phrased test query failed to parse at all, because filler words weren't stripped before metric lookup. Backend API: a saved-screen write crashed on `Decimal`; a `uuid.UUID`-vs-`str` ownership comparison failed closed for every caller. Company page MVP: a merged quarterly+annual statement table interleaved "FY 2025" between "Q3 2025" and "Q4 2025" because the two periods share an `end_date` with no stable sort order — fixed by splitting into the two separate tables doc 17's own reference analysis had already documented. All eight bugs were caught by explicitly testing an operational property or a realistic input/caller the formal test cases didn't happen to cover, rather than assuming correctness from how the code reads — scored as passes because the *completed, fixed* state is what's being scored, with each finding recorded under §6 rather than as a permanent deduction.

**What's holding verified quality below 100, precisely:** unchanged — the gap between "structurally verified" (100%, every row) and "manually reconciled against an outside source" (still 3 of 8 companies). Still the single biggest lever on that half of the score.

**Update rule:** recompute both dimensions after each completed day/stage using this same formula — don't smooth a real drop, and don't let a good day's work quality retroactively backfill an unrelated denominator.

---

## 1. Overall project completion (doc 06's 14 parts)

| # | Part | Status | % of part done |
|---|---|---|---|
| 1 | Data Collector | ✅ Complete, verified | 100% |
| 2 | Normalizer | ✅ Complete, verified | 100% |
| 3 | Mapper & Metrics Engine | ✅ Complete, verified | 100% |
| 4 | Company Master / Market Data | 🟨 4a complete, verified. 4b's ingestion shape complete, verified — **running on mock data**, real vendor still needed | 4a: 3/3 = 100%. 4b: shape 1/1 = 100% of *mock* scope; real-vendor scope not yet planned |
| 5 | Screener Engine | ✅ Complete, verified | 5/5 stages = 100% |
| 6 | AI Query Engine | 🟨 6a/6b complete, verified. 6c (real LLM) deferred — vendor decision not made | 6a/6b: 3/3 = 100% of buildable-now scope; 6c not yet planned |
| 7 | Backend / Product API | ✅ Complete, verified (Scrooner's own internal use only — the separate B2B `apps/data-api` is not this) | 4/4 stages = 100% |
| 8 | Frontend Product | 🟨 Company page MVP built, verified — rest of Frontend (screener UI, saved screens, auth pages) not started | 1 of ~4-5 major page types |
| 9–11, 13, 14 | User System, Billing, Admin, Analytics, Infra | ⬜ Not started | 0% |
| 12 | SEO/Content Engine | ⬜ Deferred past MVP (deliberate, per doc 02) | — |

**Honest read:** 5 of 14 parts fully done (Collector, Normalizer, Mapper, Screener, Backend API), 3 more (Company Master, AI Query, Frontend) partially done. **Don't over-read this as a fixed "% done overall"** — parts are wildly unequal in effort. The meaningful claim right now is narrower and now spans both directions: **a real HTTP request can go from plain English all the way to a traceable, correct company list and back (the query side), and a real browser request can now render a real company's actual financials — income statement, balance sheet, cash flow, a deterministic pros/cons read — on a real page (the content side).** Both halves of "the crown jewel" pitch now have something real behind them.

**On the "7-day"/"Day N" framing:** doc 08 and doc 09's day-numbers are **scope units, not calendar days** — the Collector's nominal "7 days" shipped across 2 calendar days (2026-08-13 → 08-14). The Normalizer's all 7 days shipped in **one continuous session on 2026-08-15**. Reading "Day N of 7" as a calendar commitment would be wrong in both directions — actual velocity is faster than the day-count suggests, but the day-count was never a calendar commitment to begin with.

---

## 2. Normalizer phase detail (doc 09's 7 stages)

| Stage | Status | Key number |
|---|---|---|
| 2a. Identity | ✅ Done | 10/10 golden companies → 1 `core.company` row each, 0 orphaned filings |
| 2b. Periods | ✅ Done | 1,832 periods, **100%** structurally correct instant/duration split |
| 2c. Units | ✅ Done | 29 raw unit strings → 28 canonical (1 real case-collision resolved) |
| 2d. Facts | ✅ Done | 169,825 / 178,811 datapoints written (**94.97%**); remaining 5.03% intentionally out of MVP scope (non-10-K/10-Q filings), not failures |
| 2e. Dedupe | ✅ Done | 48,360 duplicate groups: 45,182 (**93.43%**) cleanly resolved, 3,178 (**6.57%**) flagged as genuine unresolved conflicts |
| 2f. Restatements | ✅ Done | 43 amendments found, 36 linked to their original filing, 681 fact pairs superseded (originals stay queryable) |
| 2g. Q4 derivation | ✅ Done | 4,397 Q4 values derived (14,907 candidate groups; 10,336 incomplete/correctly skipped; 174 already directly reported, correctly left alone) |

**All 7 stages complete.** Total `core.fact`: **174,222** (169,825 reported + 4,397 derived). Doc 09's full Definition of Done (6 output + 5 operational requirements) passed with real evidence — see `doc/execution-plans/09b_Normalizer_Definition_of_Done_Evidence.md`.

---

## 2b. Mapper phase detail (doc 11's 6 stages)

| Stage | Status | Key number |
|---|---|---|
| 3a. Concept mapping | ✅ Done | 17 canonical concepts, 32 curated tag mappings, 83% (company, concept) coverage on the golden-8 (remainder explained: industry-structural nulls or flagged gaps, not silent) |
| 3b. Canonical fact resolution | ✅ Done | 7,904 canonical facts resolved across the golden-8; `analytics.canonical_fact` (new table) |
| 3c. Metric formula definitions | ✅ Done | 20 metric_definition rows (18 product metrics), 39 input links; ROIC's previously-open formula pinned with evidence; ROIC/ROE scoped to FY-only pending Stage 3e's TTM windows |
| 3d. Point-in-time calculation | ✅ Done | 2,271 metric values computed, 1,187 correctly null, across the golden-8's 10 EDGAR-only non-growth metrics |
| 3e. TTM/growth windows | ✅ Done | 1,369 growth values + 440 TTM ROIC/ROE values; TTM-at-Q4-boundary matches Stage 3d's independent FY calculation to full precision |
| 3f. Validation + end-to-end DoD | ✅ Done | `mapper/validate.py`: 0 non-authoritative leaks, 0 dangling lineage refs across 7,904 canonical facts + 6,058 metric values; edgartools cross-check exact to full decimal precision; incremental-reprocessing isolation bug found and fixed (see below) |

**All 6 stages complete.** Total `analytics.metric_value`: **6,058** (2,271 point-in-time + 1,369 growth + 440 TTM + 1,978 correctly-null across all three). Doc 11's full Definition of Done (6 output + 5 operational requirements) passed with real evidence — see `doc/execution-plans/11b_Mapper_Definition_of_Done_Evidence.md`.

Twelve real correctness/idempotency/isolation bugs caught across all 6 days, every one before or by checking real output — see `doc/learnings/mapper-day-01-concepts.md` through `-day-06-validation.md`. Day 5 was the only day of six with zero new bugs; Day 6 found the phase's most consequential one: a shared-table delete scoped by the wrong dimension silently destroyed another stage's prior output on rerun, caught only because the incremental-reprocessing property named in doc 11's own Definition of Done was actually tested, not assumed.

---

## 2c. Company Master 4a phase detail (doc 13's 3 stages)

| Stage | Status | Key number |
|---|---|---|
| 4a-1. Identity fields | ✅ Done | 9/10 companies got a populated SIC code (ARCC's genuine `sic=''` in EDGAR's own payload confirmed live, not a bug); zero new SEC fetches — every field parsed from already-stored `raw.sec_submissions` |
| 4a-2. Name history + ticker-change dating | ✅ Done | 19 `core.company_name_history` rows, exact match to EDGAR's `formerNames` for Block/AAPL after filtering 2 record-touch artifacts; 38 `core.listing` rows dated, 2 correctly proxied (Block, independently verified) + 36 honestly `unknown` |
| 4a-3. Status inference + end-to-end DoD proof | ✅ Done | 10/10 golden companies correctly `active`, each `status_reason` traceable to a real `core.filing.filing_date`; `delisted` is not a representable schema value |

**All 3 stages complete.** Doc 13's 4a Definition of Done (4 output + 5 operational requirements) passed with real evidence — see `doc/execution-plans/13b_Company_Master_4a_Definition_of_Done_Evidence.md`. Two real bugs caught in this single session, both by checking real output against the full golden set rather than the one case a design idea was built around — see `doc/learnings/company-master-4a.md`.

---

## 2d. Company Master 4b detail — mock data only

| Item | Status | Key number |
|---|---|---|
| `core.market_price` schema | ✅ Built | `db/migrations/0006_market_price_schema.sql`; hard `is_mock` boolean, not just a `source` string convention |
| Mock price ingestion | ✅ Built, verified | 300 rows (10 companies × 30 trading days), seeded per `(cik, end_date)`; confirmed byte-identical on rerun; single-CIK reload confirmed isolated from other companies |
| Real vendor integration | ⬜ Not started, not planned | Doc 02's decision remains open |

**Zero bugs found this stage** — the first clean Company Master stage after 4a's two. **This table currently holds only fabricated data** — see `doc/learnings/company-master-4b-mock.md` and the addendum in `doc/13b_...`. Not counted toward reconciliation or manual-verification-breadth scores below, correctly, since mock data isn't evidence of anything about real-world correctness.

---

## 2e. Screener Engine detail (doc 14's 5 stages)

| Stage | Status | Key number |
|---|---|---|
| 5a. Query schema | ✅ Done | Pydantic-validated `ScreenQuery`/predicates; every malformed-predicate case (missing `value`, missing `value_range`, invalid `n`, duplicate ranked predicates) confirmed rejected |
| 5b. Value resolution | ✅ Done | TTM-preferred/latest-`period_end` rule cross-verified two ways: exact match to a hand-computed ROE ranking, and ARCC's `debt_to_equity` correctly picking a fresher quarter over an older FY row |
| 5c. Predicate evaluation | ✅ Done | All 9 locked operators exercised against real data; nulls confirmed to never pass a comparison or rank in `top_n`/`bottom_n` |
| 5d. Query execution | ✅ Done, after 1 bug | 4 golden-set test screens all matched hand-computed expected results exactly; `sort_by` lineage bug found and fixed (see below) |
| 5e. End-to-end verification | ✅ Done | `doc/14b` — determinism confirmed byte-identical across reruns |

**All 5 stages complete.** Doc 14's full Definition of Done (5 output + 5 operational requirements) passed with real evidence — see `doc/execution-plans/14b_Screener_Engine_Definition_of_Done_Evidence.md`. One real bug found and fixed: a `sort_by` field not also used as a filter predicate was missing from the output entirely — an incomplete-lineage gap none of doc 14's own named test screens happened to exercise. See `doc/learnings/screener-5a-5e.md`. Notably the *first* stage of any phase in this project to get 4 of 5 sub-stages (5a-5c, 5e) fully correct on the very first live test — attributed to doc 14 itself checking real `metric_value` data before any code was written, not after.

---

## 2f. AI Query Engine detail (doc 15, stages 6a/6b)

| Stage | Status | Key number |
|---|---|---|
| 6a. Interface + validation | ✅ Done | `NLInterpreter` Protocol; `query` only ever populated when nothing is unrecognized/ambiguous |
| 6b. Rule-based interpreter | ✅ Done, after 1 bug | Filler-word stripping fix (see below); all 4 positive test queries parse and execute correctly after the fix |
| 6b-verify. End-to-end verification | ✅ Done | All 4 positive queries, run through the real Screener, reproduce doc 14b's already-verified results **exactly** — values, order, and exclusions |
| 6c. Real LLM interpreter | ⬜ Deferred | LLM vendor/cost decision flagged to the user, not made here |

**6a/6b complete.** Doc 15's Definition of Done for these two stages passed with real evidence — see `doc/execution-plans/15b_AI_Query_Engine_Definition_of_Done_Evidence.md`. One real bug found and fixed: the single most naturally-phrased test query ("companies with ROE above 30%") failed to parse at all because filler words weren't stripped before metric lookup — the other 3 test queries all happened to use cleaner phrasing and passed immediately, masking the gap until the most realistic case was actually tried. See `doc/learnings/ai-query-6a-6b.md`. Strongest evidence in the whole phase: interpreted queries don't just produce a plausible-looking `ScreenQuery`, running them reproduces results an entirely separate, already-independently-verified system (the Screener) already proved correct.

---

## 2h. Backend API detail (doc 16, stages 7a-7d)

| Stage | Status | Key number |
|---|---|---|
| 7a. Schema + auth | ✅ Done | 2 real Supabase Auth users created via the Admin API; real JWTs correctly resolve to a user id; missing/garbage tokens correctly rejected with 401 |
| 7b. Public endpoints | ✅ Done, after 1 bug | `POST /v1/screen`/`POST /v1/ask`, over real HTTP, reproduce doc 14b/15b **exactly**, including full-precision `Decimal` as JSON strings; found and fixed a `json.dumps()`-on-`Decimal` crash in the saved-screen write path |
| 7c. Authenticated endpoints | ✅ Done, after 1 bug | Found and fixed a `uuid.UUID`-vs-`str` ownership check that failed closed for every caller (including the rightful owner); re-verified with 2 real users in both directions |
| 7d. End-to-end verification | ✅ Done | `doc/16b` — determinism confirmed byte-identical over real HTTP |

**All 4 stages complete.** Doc 16's full Definition of Done passed with real evidence — see `doc/execution-plans/16b_Backend_API_Definition_of_Done_Evidence.md`. Both bugs found the same way: by making the real call (two real users, real sign-ins) rather than trusting the code's logic by inspection. Architecture decision verified, not assumed: `uv sync`'s own output confirmed `scrooner-pipeline` installed as an editable local package before any route handler was written. See `doc/learnings/backend-api-7a-7d.md`.

---

## 2i. Company Page MVP detail (doc 17)

| Piece | Status | Key number |
|---|---|---|
| Reference analysis | ✅ Done | 14 real Screener.in sections extracted from live HTML (not recalled), each honestly scoped build-now/deferred/out-of-scope |
| Statement classification | ✅ Done | 9 new statement-only concepts added to Mapper's `analytics` schema, purely additive — 7,904/7,904 original canonical facts confirmed unchanged before and after |
| `/stock/[ticker]` page | ✅ Done, after 1 bug | Top-ratios (partial), Pros/Cons checklist, Quarterly + annual P&L/Balance Sheet/Cash Flow, filings — all rendering real data over real HTTP |

**Verified against 4 real companies, including 2 real edge cases**: Block's ticker-change history (`/stock/xyz` resolves, `/stock/sq` correctly 404s) and NKE's already-known missing `OperatingIncomeLoss` rendering as an honest null. AAPL's FY2025 figures on the page match `edgartools`-verified numbers exactly — a third independent confirmation of the same real values. See `doc/learnings/company-page-mvp.md`.

---

## 2j. Ownership & Insider Activity detail (doc 19, Stages 1-3)

| Stage | Status | Key number |
|---|---|---|
| 1. 8-K into `core.filing` | ✅ Done | `FORM_ALLOWLIST` widened additively; before/after row counts confirmed zero regression to the 7 pre-existing form types, 3,000 new 8-K/8-K-A rows added |
| 2. Form 4 insider transactions | ✅ Done | **55,109** real transactions from 15,684 filings considered across the full golden-10 (not a sample); 285 real issuer mismatches found and correctly excluded (JPM as institutional insider of other companies, Alphabet's venture arm filing under the parent CIK) |
| 3. Schedule 13D/13G beneficial ownership | ✅ Done | **527** confirmed genuine stakes stored from 3,637 filings considered; 3,036 correctly excluded as the golden company acting as filer, not subject; AAPL's own 81 stakes correctly led by Berkshire Hathaway/Vanguard/BlackRock |

**Two real corrections to doc 19's own numbers, found only by running the full golden-10 rather than trusting a sample**: the doc's original §1 table (90 Schedule-13G-family filings) itself undercounted by ~40x once Stage 3 ran for real (3,637 — JPM alone contributes 2,975 as an institutional filer); and Stage 2's design assumption that Form 4 has no issuer-vs-filer ambiguity was proven wrong at full-set scale (285 real mismatches, none present in the small sample the assumption was based on). Both are documented in full, including the investigation, in `doc/learnings/ownership-and-8k-discovery.md` — kept in deliberately, per explicit user direction to capture "how and when we figured this out," not smoothed into a clean-looking final number.

**Zero SEC-fetch discovery work needed** — every filing list came from `raw.sec_submissions`, already fetched during the original Collector build; only each filing's individual document body needed a new fetch.

---

## 3. Correctness evidence (not self-reported — checked against outside sources)

| Check | Result |
|---|---|
| Manual reconciliation vs. public filings | **3 / 3 exact matches** (AAPL Q1 FY24 revenue $119,575,000,000; MSFT Q3 FY24 net income $21,939,000,000; JPM FY23 net income $49,552,000,000), plus AAPL's derived Q4 FY24 revenue ($94,930,000,000) matching Apple's actual reported figure |
| Independent cross-check via `edgartools` (Mapper Day 6, separate code path from this project's own pipeline) | AAPL FY2025/FY2024 `net_margin` — Scrooner's stored value vs. edgartools-sourced net income/revenue, **exact match to full decimal precision** in both years |
| Cross-stage consistency (Stage 2d's unit/period lookups against Stages 2b/2c's output) | **0 misses** across 178,811 datapoints (`skipped_unmapped_unit=0`, `skipped_period_not_found=0`) |
| Non-authoritative-fact leak check (Mapper Day 6, global, all rows) | **0 leaks** — no `analytics.canonical_fact` or `analytics.metric_value` row cites a non-authoritative `core.fact`, across the full golden-8 |
| Source-fact lineage integrity (Mapper Day 6, global, all rows) | **0 dangling references** — every `source_fact_ids` entry across both tables resolves to a real `core.fact` row |
| Fiscal-calendar derivation vs. real public fiscal calendars | **4 / 4 companies correct** (AAPL Sept FYE, MSFT June FYE, NKE May FYE, JPM calendar FYE all spot-checked exactly) |
| Idempotency (row-count level) | **24 / 24 build stages** (Collector 7 + Normalizer 7 + Mapper 6 + Company Master 4a 3 + Company Master 4b-mock 1) — reruns produce identical row counts, after fixing one real Mapper Day 6 scoping bug and one real Company Master 4a `NULL`-conflict-target bug (see §6); 4b's mock loader was idempotent from first build |
| Idempotency (dead-tuple/bloat level) | 2 real bloat incidents found and fixed (Normalizer Days 4–5, `VACUUM FULL`) — now a documented check, not a blind spot |
| Incremental reprocessing (docs 09/11's DoD requirement) | Live-demonstrated, not assumed, in both phases: single-CIK rerun left every other company's row count byte-for-byte unchanged. Mapper's own test **failed twice before passing** — see §6 |
| Restatement mechanism | Verified against both a routine case (ARCC's 5 cover-page `10-K/A`s) and genuine material restatements (JPM's EPS, AAPL's assets) |
| TTM-vs-FY cross-check (two independent code paths, same answer) | AAPL FY2021 ROIC: Stage 3e's TTM-at-Q4-boundary and Stage 3d's independently-computed FY value agree to full decimal precision |
| Ticker-change-date proxy applied against the full golden set (Company Master 4a) | **Failed on first attempt, caught by full-set checking**: 27 of 38 listing rows wrong when a proxy verified for one case was applied as a blanket default; fixed to 2/38 (Block only, independently confirmed) + 36 honest `unknown` |
| Company name history vs. EDGAR's own `formerNames` (Company Master 4a) | Block's Square→Block interval reproduces EDGAR's dates exactly (`2011-03-02`→`2021-12-08`); 2 EDGAR record-touch artifacts (RDDT, JPM) correctly filtered before reaching the table |
| Fabricated-data flagging (Company Master 4b) | **300 / 300** `core.market_price` rows correctly carry `is_mock=true` and `source='mock'` — zero rows that could be mistaken for real vendor data; determinism confirmed via byte-identical reruns |
| Screener query determinism (Screener Engine) | Two consecutive runs of the same query produced **byte-identical** JSON output |
| Screener test screens vs. hand-computed expectations (Screener Engine) | **4 / 4 exact matches** (`roe > 0.30`, `sic_code = '7372'`, `debt_to_equity between (0,1)`, `roic top_n(3)`) — every excluded company's reason cross-checked against already-documented Mapper-phase findings, not treated as new/suspicious |
| AI Query interpreted results vs. the Screener's own already-verified results (AI Query Engine) | **4 / 4 exact matches** — English queries parsed and executed produced identical matched companies, values, and exclusions to doc 14b's independently-verified Screener test screens, not just a plausible-looking parsed object |
| Ambiguity/rejection correctness (AI Query Engine) | **2 / 2** — a genuinely ambiguous phrase ("revenue growth") and a genuinely unrecognizable one ("magic number") both correctly returned no query, never a guessed or partial one |
| API results vs. already-verified Screener/AI Query results, over real HTTP (Backend API) | **2 / 2 exact matches** (`/v1/screen`, `/v1/ask`) — including full-precision `Decimal` preserved as JSON strings, checked by reading the raw response body |
| Per-user data isolation, both directions (Backend API) | **4 / 4** — non-owner blocked from delete/rename (before and after the ownership-check fix); owner's own delete/rename correctly succeed (only after the fix) |
| Auth rejection correctness (Backend API) | **3 / 3** — missing token, invalid token, and a valid real token all produced the correct response |
| Issuer-vs-filer direction correctness (Ownership, Form 4 + Schedule 13G) | **2 / 2 real directions confirmed live** — JPM-as-filer (Vicor Corp stake) and AAPL-as-subject (Berkshire Hathaway stake) both correctly resolved by the header/XML issuer check; 3,321 real mismatches across the golden-10 correctly excluded, not silently miscounted |
| Beneficial-ownership holder identity vs. real known AAPL shareholders | AAPL's stored top stakes exactly match its real largest institutional holders — Berkshire Hathaway, Vanguard Group, BlackRock — spot-checked directly against `core.beneficial_ownership` rows |

---

## 4. Resource budget (Supabase free tier)

| Metric | Value | % of 500 MB budget |
|---|---|---|
| Total DB size (after Company Master 4a+4b-mock) | 58 MB | **11.6%** |
| `core.fact` (golden-8, 174,222 rows incl. derived Q4) | ~44 MB | 8.8% |
| `analytics.*` (7,904 canonical facts + 6,058 metric values + mapping tables) | ~5 MB | 1.0% |
| `core.market_price` (300 mock rows) + `core.company_name_history`/identity extensions | <1 MB | ~0.1% |
| Headroom remaining at current (golden-set-only) scope | ~442 MB | 88.4% |

Confirms doc 09/11/13's capacity decisions were the right call: golden-set-scale work has enormous headroom, and Company Master's entire footprint (identity extensions + 300 mock price rows) is negligible — the constraint only bites at wider-universe scale, which stays explicitly deferred (doc 02). The Screener and AI Query Engine both add **zero** new storage — the Screener is entirely read-only, and AI Query is a pure in-memory text-to-object translation with no database writes at all. Backend API adds a new `app` schema (3 tables), but its own footprint stays negligible too — 2 test users, a handful of `usage_event` rows, zero `saved_screen` rows remaining after test cleanup.

---

## 5. Decision debt

**9 open decisions** in doc 02, unchanged this update; **2 additional deferred items from doc 19** (Form 13F institutional-ownership aggregation, DEF 14A/deep 8-K text parsing) — neither is a user decision the way the 9 are, each is gated on a genuinely unsolved design problem (a CUSIP↔CIK crosswalk for 13F; unstructured multi-decade text parsing for DEF 14A), flagged in doc 20 rather than silently left off the list. — Backend API didn't add a new one, it built the *shape* for an existing open item (free/paid usage limits: `app.user_entitlement`'s tier lookup exists, the actual limit numbers still don't) without pretending to close it. The market-price vendor and LLM vendor decisions are both **still separately open**. None of the three mock/rule-based/shape-only unblocks (4b, 6b, 7's entitlement table) reduce the real urgency of their underlying decisions — `core.market_price` holds zero real data, AI Query runs zero real LLM calls, and no free/paid limit is actually enforced anywhere, all by explicit, documented user choice. The Screener, AI Query's rule-based layer, and now Backend API's entitlement check are all fully built and ready to pick up real data/a real LLM/a real policy the moment each decision closes. The rest (pricing, hosting, indexing rules, legal review, 20-F/40-F scope, wider-universe scope) have no forcing function yet — worth a deliberate pass before they become blocking, not urgent today.

---

## 6. Best and worst this period

**Best:**
- **Doc 19 caught and corrected two of its own wrong numeric claims before they became load-bearing** — a ~40x undercount in its own §1 table, and a design assumption (Form 4 has no issuer ambiguity) proven wrong only once the full golden-10 was run instead of a small sample. Both corrections are documented in full, not silently folded into a clean final number — the explicit ask this session was to capture "how and when we figured this out," and this phase is the clearest example yet of that discipline catching itself, twice, in the same doc.
- **Both halves of "the crown jewel" pitch now have something real behind them — a real query path (English → results) and now a real content page (a real company's actual financials, correctly structured, now including real insider trades and real major shareholders).** Nine phases, each with real evidence, none skipped or asserted from memory, in about a week.
- **The company page's own reference doc was checked against the real Screener.in HTML, not written from memory** — and the one bug found (merged quarterly/annual tables) was caught specifically because the build was compared against that same reference doc, not against a vague recollection of what the page "should" look like.
- **A meaningful pipeline extension (9 new statement concepts) was confirmed not to regress Mapper's frozen, already-verified output before being trusted** — 7,904 original canonical facts checked unchanged, not assumed unchanged.
- **A third independent confirmation of the same real AAPL numbers** — Scrooner's own pipeline, `edgartools`, and now the rendered page all agree to the same FY2025 figures.
- **Real edge cases from the existing golden set were exercised on the very first pass**, not deferred — Block's ticker-change history and NKE's known-null ROIC/operating-income gap both rendered correctly without special-casing.
- Documentation discipline held across the whole build now — 12 Mapper learnings entries, 7 Normalizer, 2 Company Master, 1 Screener, 1 AI Query, 1 Backend API, 1 company page, all real findings, no filler.

**Worst / most consequential finding:**
- **Three structurally fabricated/deferred/unenforced surfaces now exist at once — `core.market_price` (mock prices), AI Query (no real LLM), and `app.user_entitlement` (no real limit enforcement) — each explicitly flagged, each a real landmine if the flag is ever forgotten.** The company page adds a fourth, related one: About text is simply absent (not faked) for the same reason. None should ever drive a real product decision without its underlying gap being closed first.
- **A signal, a test suite, a framework guarantee, or a sort key verified correct for the cases it was built/checked around is not evidence it generalizes — this project has now hit six variants of this same root shape.** Worth treating as a standing pattern to actively guard against on every future stage, not six unrelated incidents.
- **The 6.57% unresolved-conflict rate (Normalizer finding, still live) remains the single biggest open product question.** Unchanged this update.
- **Three open decisions (market-price vendor, LLM vendor, usage limits) now all have a fully-built shape waiting on them.** All three are ready for a real integration the moment each decision is made.

**No finding across any completed phase threatens the rest of Frontend's feasibility.** Everything above is a real, now-documented, now-handled data-quality or engineering-discipline problem — not a structural blocker. The underlying architecture absorbed every messy-data case found, including six independent instances of "worked for the case it was built around, wrong elsewhere," without needing a redesign — only more careful scoping and more skeptical verification.

---

## 7. Recommended plan adjustments

Small reinforcements, not a re-plan — the day-by-day, verify-then-proceed structure delivered eight fully-verified phases/sub-phases in a row and shouldn't change now that the rest of Frontend is next:

1. **Done this update:** company page MVP (`/stock/{ticker}/`) built and verified — real Screener.in reference analysis, a purely-additive statement-classification layer on Mapper's frozen schema, real data rendered for 4 companies including 2 real edge cases. Doc 17 promoted to Canonical. **Also done this update:** Ownership & Insider Activity (doc 19) Stages 1-3 — 55,109 Form 4 transactions, 527 confirmed beneficial-ownership stakes, both wired into the company page. Doc 20 written as the single consolidated "what's left" plan across all 14 parts.
2. **New this update, a standing rule:** sorting periods (or any ordered set) by one key alone breaks when two different granularities can share that key's value — partition by the coarser dimension first, sort within each partition second. Written into `pipeline/CLAUDE.md`.
3. **Still not yet done, still worth flagging before it's needed:** the Mapper follow-on that computes the 6 price-dependent metrics from `core.market_price` must filter `is_mock=false` the moment it's built — unchanged from three updates ago.
4. **Still not yet done, same shape:** whenever 6c (a real LLM interpreter) gets built, it must satisfy the exact same `NLInterpreter` contract 6b already does.
5. **Low priority, not urgent:** a periodic-VACUUM habit belongs in Part 14's eventual scope — noted in doc 04, not yet a doc 06 line item.
6. **Real, not-yet-exercised coverage gap:** the Screener's `active`-only default status filter has never been tested against a real `stale`/`unknown` company.
7. **New this update:** business-description ("About") text has no data source anywhere in this project — a real, standalone gap worth a deliberate decision (parse 10-K Item 1? a vendor?) before Frontend needs it, not solved here.
8. **Next, per critical path (doc 06):** the rest of Frontend Product (Part 8) — screener UI, saved screens, auth pages, now with a real backend and a real first page type to build against. Alternatively, close a vendor decision (market-price, LLM) or the usage-limits policy. All are legitimate; which comes first is a product sequencing call.
