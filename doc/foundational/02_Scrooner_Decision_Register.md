# 02 — Scrooner Decision Register

A record of what is locked, what was rejected, and what remains open.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes

---

## How to use this document

This is the authoritative decision register. “Locked” means teams should
build against it. “Deferred” means intentionally postponed. “Open” means
a decision is still required. When a new decision changes an old one,
update this file and mark the replaced decision as superseded.

## Locked product decisions

| **Decision**                              | **Status**            | **Reason**                                              |
|-------------------------------------------|-----------------------|---------------------------------------------------------|
| US-listed equities only in V1             | Locked                | Depth and data quality before exchange breadth.         |
| Global audience; initial focus US + India | Locked                | US-stock interest extends beyond US residents.          |
| English and USD                           | Locked                | One consistent first-market experience.                 |
| Plain-English fundamental screening       | Locked                | This is the primary wedge.                              |
| Deterministic results; AI is assistive    | Locked                | Financial truth must come from data and formulas.       |
| ~15–20 metrics and ~10 operators          | MVP guardrail         | Enough for valuable screens without uncontrolled scope. |
| Approx. $100/year premium hypothesis     | Commercial hypothesis | Simple, globally legible pricing to validate.           |
| Free core + paid premium                  | Locked direction      | Supports SEO acquisition and product trial.             |
| Glossary, guides and public/indexed screen pages ship after MVP | Locked | Content/SEO layer, not core screening validation; ships as the SEO/Content Engine phase (doc 06, Part 12). Saved screens themselves (authenticated create/rerun/delete) remain in MVP — only their public, indexed publishing is deferred. Supersedes doc 03's original "guides and glossary foundation" MVP row. |
| V1 metric list and formula definitions — **Locked 2026-08-15**, resolves the Open-decisions row below | Locked | 18 metrics within the ~15–20 guardrail, selected from [doc 10](../requirements/10_scrooner_required_data_points.md)'s P0 inventory. Formulas given at the canonical-concept level (e.g. "Revenue," "Operating Income") — Mapper still resolves which XBRL tag(s) feed each concept per company/taxonomy-version, per doc 04's boundary table; this locks *what* to compute and *with what formula*, not *which tag* to source it from. See table below. |

### V1 metric list (18 metrics)

Pure-EDGAR metrics are computable as soon as Mapper/Metrics (Part 3) lands. Price-dependent metrics are formula-locked now but not computable until Company Master's market-data source is picked (separate open decision below) — they stay on this list, not deferred out of it.

| Metric | Formula (canonical-concept level) | Computable from |
|---|---|---|
| Gross Margin | Gross Profit ÷ Revenue | EDGAR only |
| Operating Margin | Operating Income ÷ Revenue | EDGAR only |
| Net Margin | Net Income ÷ Revenue | EDGAR only |
| Return on Equity (ROE) | Net Income ÷ Stockholders' Equity | EDGAR only |
| Return on Invested Capital (ROIC) | Net Operating Profit After Tax ÷ (Debt + Equity − Cash) | EDGAR only — v1 formula, tax-rate/invested-capital component detail is Mapper's to pin down with a version number |
| Revenue Growth | YoY: (Revenue₍t₎ − Revenue₍t-1₎) ÷ Revenue₍t-1₎; also 3Y CAGR | EDGAR only |
| EPS Growth | Same YoY/CAGR pattern, on diluted EPS | EDGAR only |
| Free Cash Flow (FCF) | Cash from Operations − CapEx | EDGAR only |
| FCF Margin | FCF ÷ Revenue | EDGAR only |
| Debt / Equity | Total Debt ÷ Stockholders' Equity | EDGAR only |
| Current Ratio | Current Assets ÷ Current Liabilities | EDGAR only |
| Interest Coverage Ratio | Operating Income ÷ Interest Expense | EDGAR only |
| Market Cap | Shares Outstanding × Price | **Needs market-price source** |
| Trailing P/E | Price ÷ Diluted EPS (TTM) | **Needs market-price source** |
| Price / Sales | Market Cap ÷ Revenue (TTM) | **Needs market-price source** |
| Price / Book | Market Cap ÷ Stockholders' Equity | **Needs market-price source** |
| Dividend Yield | Dividends per Share (TTM) ÷ Price | **Needs market-price source** |
| FCF Yield | FCF (TTM) ÷ Market Cap | **Needs market-price source** |

**Operators (9):** `>`, `<`, `>=`, `<=`, `=`, `≠`, `between` (range), `top N` / `bottom N` (ranked), categorical `=` (sector/industry).

---

## Locked architecture decisions

| **Decision**                            | **Status**            | **Notes**                                                                                   |
|-----------------------------------------|-----------------------|---------------------------------------------------------------------------------------------|
| scrooner.com                            | Locked                | Public marketing, guides, glossary, indexable company and saved/public screen pages.        |
| app.scrooner.com                        | Locked                | Interactive screener, prompt flow, authentication, saved screens and paid account features. |
| Astro for public web                    | Locked                | Static/SEO-first delivery with minimal client JavaScript.                                   |
| Next.js App Router for app              | Locked                | Dynamic and authenticated application experience.                                           |
| ~~Separate Scrooner Data project~~      | **Superseded 2026-08-14** | Was read as a separate git repo. Reversed to a monorepo — see next row.                     |
| Data pipeline lives in `pipeline/` (this repo, monorepo) | Locked           | Solo-founder manageability: one `.claude/` config, one `CLAUDE.md`, no cross-repo doc-pointer overhead — a bigger cost right now than the repo-separation benefit (deploy-target/blast-radius isolation) would buy. Pipeline stays architecturally independent (own `pyproject.toml`, own Python 3.12 env, writes only to `raw` schema) — folder-scoped, not repo-scoped. **Revisit trigger:** split back into a separate repo once hosting for the recurring Python jobs is actually decided and diverges from the web deploy, or once a team forms and the folder-wall stops being enough to hold the Collector boundary. |
| Collector → Normalizer → Mapper/Metrics | Locked                | Clear responsibilities and replaceable stages.                                              |
| Supabase Postgres + Auth + Storage      | Locked starting point | Database/auth and raw object storage with low operational overhead.                         |
| Django + Django Admin internally        | Selected direction    | Operational/admin interface; not part of ingestion logic.                                   |
| No FastAPI initially                    | Locked for MVP        | Add only when a stable external/internal API boundary is justified.                         |
| No Redis or Celery initially            | Locked for MVP        | Use simple scheduled/batch jobs first.                                                      |
| No Auth.js initially                    | Locked for MVP        | Use Supabase Auth to avoid duplicate auth complexity.                                       |
| Stripe for billing                      | Selected direction    | Implement when paid plan enters the build.                                                  |
| GitHub Actions + lightweight monitoring | Selected direction    | Automated checks/deployments; Sentry and simple analytics when needed.                      |

## Locked data decisions

- The Collector is dumb, lossless and immutable: it fetches and preserves raw SEC responses plus provenance, timestamps and checksums.

- The Collector does not calculate ROIC/TTM, repair facts, map XBRL concepts or decide fiscal quarters.

- Bootstrap with SEC bulk archives; run incremental updates through SEC APIs and daily indexes.

- Use a declared SEC User-Agent and keep the aggregate internal request rate at or below 8 requests per second.

- Jobs must be idempotent, resumable, deduplicated and reconciled; failures go to an inspectable dead-letter/error path.

- Raw objects live in Supabase Storage; ingest metadata and downstream structured facts live in Postgres.

- Initial logical schemas: raw, core, analytics and app.

- **Market-price vendor: Alpaca Markets (resolved 2026-08-17).** Closes the "Market price source and delay" open decision below — real API credentials provided directly by the founder, stored in `pipeline/.env` (gitignored, never committed) with placeholders in `.env.example`. Unblocks the 6 price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield), Tier A's price-dependent candidates (doc 18), and the company page's currently-null top-ratios fields. **Not yet integrated** — `core.market_price` still holds only the 300 mock rows from Company Master 4b (`is_mock=true`); wiring Alpaca in, clearing the mock rows, and computing the price-dependent metrics is a real, separate build task (Company Master 4b's real-data follow-on), not done by this decision alone. See doc 13's own note: mock rows must be cleared, never left coexisting with real rows for the same company/date.

## Rejected or deferred directions

| **Item**                           | **Disposition**   | **Revisit trigger**                                        |
|------------------------------------|-------------------|------------------------------------------------------------|
| Single Next.js site for everything | Superseded        | None; split-domain decision is newer.                      |
| No app subdomain                   | Superseded        | None; final domains are scrooner.com and app.scrooner.com. |
| Broad AI research assistant        | Rejected          | Only after screening trust and retention are proven.       |
| Real-time trading data             | Deferred          | Clear user demand and sustainable data economics.          |
| Technical indicators               | Excluded from MVP | Expansion beyond fundamental screening.                    |
| News and earnings-call AI          | Excluded from MVP | After core screening product-market fit.                   |
| Portfolio tracking                 | Excluded from MVP | After repeat screening usage is established.               |
| Analyst estimates                  | Excluded from MVP | Reliable licensed source and demonstrated demand.          |
| Non-US exchanges                   | Excluded from MVP | US dataset and operations are dependable.                  |
| Generic stock Q&A/recommendations  | Rejected for MVP  | Would weaken focus and raise trust/compliance risk.        |
| Public/B2B FastAPI layer           | Deferred          | Multiple consumers or external API demand.                 |
| Complex dashboards                 | Rejected for MVP  | Conflicts with KISS BORING.                                |

## Open decisions requiring explicit closure

| **Question**                                 | **Default until decided**                                                                          | **Decision deadline**                   |
|----------------------------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------|
| ~~Market price source and delay~~ **RESOLVED 2026-08-17 — Alpaca Markets, see "Locked data decisions" above.** | Vendor picked; end-of-day/delayed data, no real-time promise, still the working assumption pending Alpaca's own plan-tier confirmation. Integration (replacing 4b's mock `core.market_price` rows, computing the 6 price-dependent metrics) is a separate, not-yet-done build task. | Closed |
| Free vs paid usage limits                    | Apply rate limits; keep core trial meaningful.                                                     | Before private beta                     |
| Final pricing tiers and regional taxes       | $100/year remains the working hypothesis.                                                         | Before billing implementation           |
| Hosting provider for recurring Python jobs   | Choose the lowest-ops reliable option.                                                             | Before incremental collector scheduling |
| Public saved-screen indexing rules           | Index only curated, useful, stable pages.                                                          | Before SEO templates ship               |
| Legal disclaimers and data licensing review  | No investment advice; confirm all provider terms.                                                  | Before public launch                    |
| Are 20-F/40-F filers (US-*listed* foreign private issuers/Canadian MJDS filers) in scope? "US-listed equities only" doesn't by itself resolve this — they're listed on US exchanges but aren't domestically incorporated. (Surfaced in doc 07.) | Collector records them as a known form type (doc 07 §8) but Normalizer/Mapper treat them as out of scope until decided. | Before Company Universe/Normalizer treats 20-F/40-F companies as first-class |
| Which investing decision should the first user-facing screen/company-page UX optimize for — long-term compounders, undervalued cash-generative companies, or fast-growing pre-acceleration companies? (Surfaced in [doc 27](../scoping/27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md).) Affects the "Decision Cards" grouping and which metrics get UI prominence in doc 24 Phase 3 (Screener UI) — not decidable from data, founder's call. | No emphasis yet — all locked metrics stay equally weighted, no card grouping or curated-screen bias applied. | Before doc 24 Phase 3 (Screener UI) UX design starts |
| How wide should the Normalizer's company-universe coverage go, given the Supabase **free tier**'s 500 MB database cap? Measured live 2026-08-15: real XBRL fact counts run ~20-25K/company for long-history filers; even a curated few-hundred-company priority list exceeds 500 MB, let alone the full 10,396-company collected universe. (Surfaced in doc 09.) **Readiness gate added 2026-08-16** (doc 11): before any backfill wider than the golden-10, `analytics.concept_mapping`'s coverage-gap report should show the 12 EDGAR-only V1 metrics' required concepts resolving cleanly for ≥95% of a representative larger sample, checked cheaply via SEC's Frames API (no ingestion required) — otherwise a wider backfill produces avoidable unmapped-tag nulls that mapping coverage, done first, would have prevented. | Build and verify all Normalizer/Mapper stages against the golden-10 set only, on the current free-tier project, at zero added cost. Wider coverage (curated list vs. full universe) stays undecided. Upgrading to Supabase Pro (~$25/mo) is confirmed not a cost blocker whenever it's needed, but per doc 05 ("evidence before expansion") shouldn't happen until both the golden-10 Definition of Done and the ≥95% mapping-coverage gate above actually pass. | Before backfilling any company set wider than the golden-10 |

## Decision rule

When choosing between two valid approaches, select the one that improves
data correctness, auditability or user simplicity with the least
operational burden. A new dependency must solve a demonstrated problem,
not a hypothetical future problem.
