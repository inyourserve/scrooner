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

- **Market-price vendor: Alpaca Markets (resolved 2026-08-17, re-evaluated and reconfirmed 2026-08-24).** Closes the "Market price source and delay" open decision below — real API credentials provided directly by the founder, stored in `pipeline/.env` (gitignored, never committed) with placeholders in `.env.example`. Unblocks the 6 price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield), Tier A's price-dependent candidates (doc 18), and the company page's currently-null top-ratios fields. **2026-08-24 re-evaluation**: a real EODHD Commercial Display quote (€300/month, required specifically because Scrooner displays actual price values to end users, not just internal use) was obtained and compared against the already-built, free Alpaca `delayed_sip` feed. Since the actual requirement (15-minute-delayed pricing) is exactly what Alpaca's `delayed_sip` already provides, Alpaca was reconfirmed rather than switched — no functional gap Alpaca has that EODHD would close for this use case. Integration into the full 5,258-company population is tracked in `doc/execution-plans/30_Data_Moat_Full_Population_Strengthening_Plan.md` (Track 1), not yet complete as of this addendum.

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
| ~~Are 20-F/40-F filers (US-*listed* foreign private issuers/Canadian MJDS filers) in scope?~~ **RESOLVED 2026-08-27 — excluded from V1 scope.** Surfaced concretely during the full-population run (2026-08-26): of the SEC universe's 7,995 unique companies, 2,520 are foreign private issuers (`entityType != "operating"`, e.g. Alibaba/BABA, Novartis/NVS, Shell/SHEL, ARM Holdings/ARM, Royal Bank of Canada/RY) — real, well-known, US-exchange-listed names, but excluded by the eligibility filter. Kept excluded rather than added, because: (1) Mapper's 32 concept mappings were built and verified only against US-GAAP filings — most FPIs report under IFRS, where the same XBRL tag can mean something different or not exist, an untested risk to the "trust moat" if included silently; (2) no demonstrated user demand, only surfaced via internal audit — "evidence before expansion" applies directly; (3) the product's own framing ("US-listed equities") matches a user's actual mental model of "US companies," which wouldn't include Shell or Alibaba even though both trade on NYSE. | Collector still records them as a known form type (doc 07 §8); Normalizer/Mapper continue to treat them as out of scope. Revisit only as a deliberate, separately-scoped project (IFRS concept-mapping verified first, not assumed to reuse the US-GAAP mapping table), not as a default inclusion. | Closed |
| Which investing decision should the first user-facing screen/company-page UX optimize for — long-term compounders, undervalued cash-generative companies, or fast-growing pre-acceleration companies? (Surfaced in [doc 27](../scoping/27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md).) Affects the "Decision Cards" grouping and which metrics get UI prominence in doc 24 Phase 3 (Screener UI) — not decidable from data, founder's call. | No emphasis yet — all locked metrics stay equally weighted, no card grouping or curated-screen bias applied. | Before doc 24 Phase 3 (Screener UI) UX design starts |
| ~~How wide should the Normalizer's company-universe coverage go~~ **RESOLVED 2026-08-26 — full eligible population, 5,258 companies.** Supabase upgraded to Pro (2026-08-21, ~$25/mo + overage) specifically to clear this blocker; the full-population run (all 7 Normalizer stages + all 11 Mapper stages) completed for all 5,257 currently-eligible US-listed operating companies (of 7,995 total unique CIKs in the SEC seed list — the rest excluded for real reasons: 2,520 foreign private issuers per the resolved decision above, 218 stale/no-exchange/no-filing shells). `analytics.canonical_fact` grew from 268K rows (golden-10/174-pilot) to **8.3M**; `analytics.metric_value` to **6.66M**. Real cost: database now **30 GB**, ~22 GB over the Pro plan's included 8 GB — a genuine, currently-unactioned billing overage, not yet decided whether to address (archive/trim `core.fact`, or accept the cost). | Full 5,258-company population is live in `core`/`analytics`. The ≥95% mapping-coverage gate (doc 11) was implicitly cleared — no wide-scale unmapped-concept failures surfaced during the run. Open follow-up, not blocking: whether to trim `core.fact`'s ~26 GB footprint (e.g. archiving non-authoritative superseded rows) to reduce the storage overage. | Closed |

## Decision rule

When choosing between two valid approaches, select the one that improves
data correctness, auditability or user simplicity with the least
operational burden. A new dependency must solve a demonstrated problem,
not a hypothetical future problem.
