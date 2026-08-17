# 17 — Scrooner Company Page: Screener.in Reference and MVP Plan

Backend API is done. This doc does two things: (1) a structural analysis of Screener.in's actual company page (`doc/html/screener.html`, a real saved page for Reliance Industries — not a description from memory, the real markup), section by section, and (2) an honest mapping of each section against what Scrooner's pipeline already has, can build now, or genuinely can't (yet, or ever, for a US-listed company). This is the reference `/stock/{ticker}/` (doc DOCUMENTATION.md §3.2, "the crown jewel") gets built against.

> **Status:** Canonical (2026-08-17) — reference analysis complete; MVP built and verified against real AAPL/JPM/NKE/Block data, including two real edge cases (Block's ticker-change history, NKE's known missing operating income). Live at `/stock/{ticker}/` in `apps/site`. **Owner:** Founder / Product · **Review:** When Screener.in materially changes its own page, or when a mapped section's data readiness changes.

---

## 1. What Screener.in's company page actually contains

Extracted directly from the attached HTML (Reliance Industries' real page), not recalled from memory — every section below was found by searching the actual markup for its anchor id and reading the real table headers/row labels.

| # | Section (anchor) | What it shows |
|---|---|---|
| 1 | Top card | Company name, current price, day change %, price-as-of date, website + exchange links, Export/Follow (login-gated) |
| 2 | Top-ratios grid | 9 metrics: Market Cap, Current Price, High/Low, Stock P/E, Book Value, Dividend Yield, ROCE, ROE, Face Value — plus a user-customizable "add ratio" control (login-gated) |
| 3 | About + Key Points | A short business-description paragraph, plus auto-generated bullet insights ("Read More" modal) |
| 4 | Chart | Price chart with overlay toggles (not extracted in detail — needs real price data regardless) |
| 5 | Analysis (Pros/Cons) | Two bullet lists, explicitly labeled *"machine generated... based on a checklist"* — e.g. *"Company has a low return on equity of 8.77% over last 3 years"*, *"Dividend payout has been low at 10.2% of profits over last 3 years"* |
| 6 | Peer comparison | Sector→Industry→Sub-industry breadcrumb (4-level hierarchy) + index-membership tags (BSE Sensex, Nifty 50 — India-specific) + a comparison table |
| 7 | Quarterly Results | 13 quarters × 9 rows: `Sales+, Expenses+, Operating Profit, OPM%, Other Income+, Interest, Depreciation, Profit before tax, Tax%` (`+` = expandable sub-component drill-down) |
| 8 | Compounded growth cards | 4 small cards — Sales Growth, Profit Growth, Stock Price CAGR, Return on Equity — each showing 10Y / 5Y / 3Y / TTM-or-1Y figures |
| 9 | Profit & Loss (annual) | 11 years + TTM × 12 rows: the 9 quarterly rows plus `Net Profit+, EPS in Rs, Dividend Payout %` |
| 10 | Balance Sheet | 12 years × 10 rows: `Equity Capital, Reserves, Borrowings+, Other Liabilities+, Total Liabilities, Fixed Assets+, CWIP, Investments, Other Assets+, Total Assets` |
| 11 | Cash Flow | 12 years × 6 rows: `Cash from Operating/Investing/Financing Activity+, Net Cash Flow, Free Cash Flow, CFO/OP` |
| 12 | Ratios (additional) | 11 years × 6 rows for Reliance specifically: `Debtor Days, Inventory Days, Days Payable, Cash Conversion Cycle, Working Capital Days, ROCE%` (varies by company/industry) |
| 13 | Shareholding Pattern | Quarterly Promoters/FII/DII/Public % |
| 14 | Documents | Filing/announcement links with dates |

---

## 2. What actually generalizes vs. what's India-specific

Checked, not assumed — doc 10 already did this exercise once (§"What NOT to carry over directly"), this doc confirms it against the real page rather than restating it:

- **Genuinely portable**: top-ratios grid, Pros/Cons checklist mechanism (not the specific rules), Quarterly/Annual statement tables, compounded growth cards, documents/filings list, sector breadcrumb (flatter for US — SIC has no clean 4-level hierarchy the way NSE/BSE's classification does).
- **India-specific, don't port**: Shareholding Pattern's "Promoter Holding" (doc 10 already ruled this out — no such concept in US corporate structure; the honest US equivalent, Institutional Ownership via Form 13F + Insider activity via Form 4, needs data this project doesn't collect yet — P2 in doc 10, not MVP), index-membership tags (BSE Sensex/Nifty — no US equivalent worth building for MVP), "Face Value" (not a meaningful US equity concept the way it is for Indian par-value shares).

---

## 3. Section-by-section scope table — the actual MVP decision

| Section | Scope for MVP | Status | Why |
|---|---|---|---|
| Top-ratios grid | Build now, partial | ✅ Built | ROE, ROIC already real (Mapper). Market Cap, Current Price, Stock P/E, Dividend Yield shown honestly null, labeled as blocked on doc 02's still-open price vendor decision. Face Value dropped (not a US concept). |
| About text | Not built — no data source | ⬜ Out of scope | EDGAR has no clean business-description field the Collector fetches. Not fabricating one. |
| Pros/Cons checklist | Build now, in full | ✅ Built | 8-rule deterministic checklist (`apps/site/src/lib/prosCons.ts`) — real bullets rendered for AAPL ("high ROE 157.5% over 3Y", "positive FCF each of last 3 years"), zero bullets shown where no rule triggers, never a guessed one. |
| Quarterly Results + annual P&L, Balance Sheet, Cash Flow tables | Build now | ✅ Built, after 1 real bug | Statement classification (§4) built and verified; FY/quarterly period-ordering bug found and fixed (§4/learnings) — see `doc/learnings/company-page-mvp.md`. |
| Compounded growth cards | Build now, 3Y + YoY only | ⬜ Not built this pass | Deprioritized in favor of the statement tables within this session's scope; data (`revenue_growth_yoy`/`3y_cagr`) is ready, just not wired into the page yet. |
| Peer comparison | Deferred, not this doc | ⬜ Deferred | Needs real price data or a real US sector hierarchy — neither solved here. |
| Documents/filings | Build now, in full | ✅ Built | Real filing history rendered for every tested company, correct dates/accession numbers/form types. |
| Shareholding Pattern | Not built — genuinely out of scope | ⬜ Out of scope | Doc 10 already ruled the Promoter-holding concept out for US. |
| Chart | Not built this pass | ⬜ Deferred | Needs real, longer-history price data — blocked on doc 02's price vendor decision. |

---

## 4. The missing piece: statement classification (small, curated, same discipline as `concept_mapping`)

Checked live against the golden-8 before designing this (not assumed): the concrete tags below are the ones that actually appear across most/all fact-bearing golden companies, confirming they're a reasonable base set to curate first, not a guess:

`NetIncomeLoss`, `EarningsPerShareDiluted`, `Assets`, `CashAndCashEquivalentsAtCarryingValue`, `StockholdersEquity`, `NetCashProvidedByUsedInOperatingActivities`, `NetCashProvidedByUsedInFinancingActivities`, `PaymentsForRepurchaseOfCommonStock` — all present in **8/8** fact-bearing golden companies. `IncomeTaxExpenseBenefit`, `PropertyPlantAndEquipmentNet`, `NetCashProvidedByUsedInInvestingActivities` — **7/8**. Revenue itself is already known to be taxonomy-drift-prone (Mapper Day 1: 2 tags just within this narrower check, 3 within AAPL's own history) — the statement view reuses Mapper's *already-curated* `revenue` canonical concept rather than re-solving a problem Stage 3a already solved.

**Design**: a new, small, curated table — `analytics.statement_line` — mapping `(canonical_concept_id OR a new raw-tag reference, statement, display_order, display_label)`. Two source types, not one:
- Rows that are **already a Mapper canonical concept** (`revenue`, `net_income`, `stockholders_equity`, `cfo`, `capex`, etc.) — reuse `analytics.canonical_fact` directly, already resolved, already taxonomy-drift-safe.
- Rows that are **statement-only, not ratio-relevant** (e.g. `AssetsCurrent`, `InventoryNet`, `PropertyPlantAndEquipmentNet`, `LiabilitiesCurrent`) — map directly to a `core.concept` tag per statement line, curated the same deliberate way Mapper's Stage 3a was, not fuzzy-matched, starting from the 8/8-and-7/8 tags found above.

This is **new pipeline work, not new decisions** — no vendor, no external dependency, the same kind of task as Mapper's own Stage 3a, scoped smaller (a handful of statement lines, not a ratio-calculation engine).

---

## 5. Pros/Cons checklist — a concrete, deterministic ruleset (not AI-generated prose)

Directly mirroring Screener.in's own two real examples found in the HTML (`"low return on equity... over last 3 years"`, `"low dividend payout... over last 3 years"`), built from metrics already computed and verified (docs 11b/14b):

| Rule | Direction | Metric used |
|---|---|---|
| ROE > 20% (3Y avg) | Pro | `roe`, `period_label='FY'`, trailing 3 |
| ROE < 10% (3Y avg) | Con | same |
| ROIC > 15% (3Y avg) | Pro | `roic` |
| Revenue growth (3Y CAGR) > 15% | Pro | `revenue_growth_3y_cagr` |
| Revenue growth (3Y CAGR) < 0% | Con | same |
| FCF positive every year, last 3 | Pro | `fcf`, 3 consecutive FY rows |
| Debt/Equity > 2 | Con | `debt_to_equity` |
| Interest coverage < 2 | Con | `interest_coverage_ratio` |

Every rule reads only already-verified `metric_value` rows; a rule whose required metric is null for a company produces **no bullet**, never a guessed one — same discipline as everywhere else in this project. This ruleset is deliberately small and reviewed, not exhaustive — extend it the same deliberate way `concept_mapping`/`ai_query`'s alias tables get extended, one curated rule at a time.

---

## 6. Repository footprint

```text
pipeline/
├── src/scrooner_pipeline/
│   └── statements/              # NEW -- this doc's Sec 4
│       ├── classify.py             # statement_line seeding + resolution
│       └── prosense.py             # this doc's Sec 5 checklist engine
└── db/migrations/
    └── 0008_statement_schema.sql   # NEW -- analytics.statement_line

apps/
└── site/                        # NEW -- Astro, scrooner.com (doc 04/DOCUMENTATION.md §3)
    └── src/pages/stock/[ticker].astro   # the crown jewel page itself
```

`apps/site` reads `core`/`analytics` directly via a Postgres client (`postgres` npm package), not Supabase's JS SDK specifically — same architectural point doc 04 makes ("Astro... reads approved serving views" directly, no `apps/backend` dependency for a static read), a direct SQL connection satisfies it equally and needed no new infrastructure decision.

---

## Verification — real data, real edge cases, not asserted

Built and run against a live `astro dev` server, hit with real HTTP requests, same discipline as every other phase this session:

- **AAPL**: FY2025 revenue ($416.16B) and net income match `edgartools`-verified figures from earlier in this session exactly — three independent checks (pipeline, `edgartools`, this page) now agree. Balance sheet identity confirmed: Total Liabilities + Stockholders' Equity = Total Assets exactly (275,746 + 107,520 = 383,266) for the same real quarter. Pros/Cons checklist produced real, correct bullets from live `metric_value` data.
- **JPM, NKE**: both render correctly (200). NKE's known missing `OperatingIncomeLoss` (Mapper Day 3 finding) renders as an honest null on the page, not fabricated or hidden.
- **Block (ticker-change edge case)**: `/stock/xyz` resolves correctly; `/stock/sq` (the old, no-longer-current ticker) correctly 404s — directly exercising Company Master 4a's `effective_to` history, built weeks-equivalent earlier in this session, now serving a real page.
- **Unknown ticker**: correctly 404s.
- **One real bug found and fixed**: a merged quarterly+annual statement table interleaved "FY 2025" between "Q3 2025" and "Q4 2025" (same `end_date`, ambiguous sort order) — fixed by splitting into separate Quarterly Results and annual tables, matching the structure doc 17's own Screener.in analysis (§1) had already documented. See `doc/learnings/company-page-mvp.md`.
- **Statement classification regression check**: after extending `analytics.canonical_concept`/`concept_mapping` with 9 new statement-only concepts, the original 17 Mapper concepts' `canonical_fact` row count was confirmed unchanged (7,904 before and after) — the extension is purely additive, not a silent modification of Mapper's frozen, already-verified output.

---

## What this doc does *not* decide

- Business-description text sourcing (no data source identified).
- Peer comparison mechanics (needs price data or a real US sector taxonomy decision).
- Shareholding/ownership data (needs Form 13F/Form 4 collection — a new Collector scope, not decided here).
- The price chart (needs real, longer-history price data — blocked on doc 02's still-open vendor decision).
- Whether to add 5Y/10Y growth-CAGR metrics — flagged, not decided; would touch doc 02's locked metric-count guardrail.
