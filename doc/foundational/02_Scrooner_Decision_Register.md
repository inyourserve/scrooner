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
| scrooner.com as the single product origin | **Locked 2026-09-05; supersedes split domains** | Public research and authenticated product share one origin. Authenticated workflows live under `/app`; there is no separate product subdomain. |
| Next.js App Router for all frontend routes | **Locked 2026-09-05; supersedes Astro** | Public Server Components/static routes and authenticated `/app` routes share one runtime. See [doc 43](../planning/43_Single_Nextjs_Shared_Domain_and_Shadcn_Migration_Plan.md). |
| Public/private URL boundary | **Locked 2026-09-06; supersedes the earlier `/screener` split** | Every `/app/*` page requires authentication. Everything outside `/app` is public and indexable unless explicitly excluded for a non-auth reason. `/` owns company search, the public screener, and broad “US stock screener” SEO intent. |
| Canonical public routes | **Locked 2026-09-06** | `/stocks`, `/stocks/{company_slug}`, `/screens/{slug}`, `/pricing`, `/learn`, `/glossary`, and `/blog`. Public slugs are stable SEO identifiers; private saved-screen IDs and user data never appear in public URLs. |
| Canonical private routes | **Locked 2026-09-06** | `/app`, `/app/watchlists`, `/app/saved-screens`, `/app/alerts`, and `/app/account`. Use plural `/watchlists` because a user may create more than one. |
| Stock pages use request-time SSR           | **Locked 2026-09-05** | Canonical `/stocks/[company_slug]` pages use request-time SSR, remain indexable, and are not static/ISR routes. The legacy `/stock/[ticker]` route must redirect only after the slug read model exists. |
| shadcn New York as base UI language     | **Locked 2026-09-05** | Owned source components, Tailwind v4 CSS variables, and Scrooner theme tokens. |
| ~~Separate Scrooner Data project~~      | **Superseded 2026-08-14** | Was read as a separate git repo. Reversed to a monorepo — see next row.                     |
| Data pipeline lives in `pipeline/` (this repo, monorepo) | Locked           | Solo-founder manageability: one `.claude/` config, one `CLAUDE.md`, no cross-repo doc-pointer overhead — a bigger cost right now than the repo-separation benefit (deploy-target/blast-radius isolation) would buy. Pipeline stays architecturally independent (own `pyproject.toml`, own Python 3.12 env, writes only to `raw` schema) — folder-scoped, not repo-scoped. **Revisit trigger:** split back into a separate repo once hosting for the recurring Python jobs is actually decided and diverges from the web deploy, or once a team forms and the folder-wall stops being enough to hold the Collector boundary. |
| Collector → Normalizer → Mapper/Metrics | Locked                | Clear responsibilities and replaceable stages.                                              |
| Supabase Postgres + Auth + Storage      | Locked starting point | Database/auth and raw object storage with low operational overhead.                         |
| Django + Django Admin internally        | Selected direction    | Operational/admin interface; not part of ingestion logic.                                   |
| No FastAPI initially                    | Locked for MVP        | Add only when a stable external/internal API boundary is justified.                         |
| ~~No Redis or Celery initially~~ — **Superseded 2026-09-10 for Redis/caching only** | Partially superseded | Celery/background-job-queue stays locked out — no evidence of need. Redis is now a real `apps/backend` production dependency, scoped exclusively to a dataset-versioned cache for `/v1/screen`/`/v1/ask` (measured live: a real ROE screen took 13.9s; caching + connection pooling brought a cache-hit request to ~4-8ms). Explicit founder direction, overriding the original lock after the tradeoff was surfaced. See [ADR 0001](../adr/0001-screener-redis-cache-and-boolean-logic.md). |
| No Auth.js initially                    | Locked for MVP        | Use Supabase Auth to avoid duplicate auth complexity.                                       |
| Stripe for billing                      | Selected direction    | Implement when paid plan enters the build.                                                  |
| GitHub Actions + lightweight monitoring | Selected direction    | Automated checks/deployments; Sentry and simple analytics when needed.                      |

- **Founder decision of 2026-11-13: connection budget raised** (typed by the founder in Dhairya's session: "use more connection i think we can use 90 connections").
  1. Data loads may use up to **70 connections** in company-disjoint shards; the preflight and in-run pause threshold moves from 60 to **80** backends. This supersedes item 2 of 2026-11-12.
  2. Measured 2026-11-13: `max_connections` = 90, `superuser_reserved_connections` = 3, 19 in use. The remaining headroom (about 10) stays free for the app, backend, Supabase services and other sessions; a job never targets all 90.

- **Founder decision of 2026-11-12: connection rules replaced** (typed by the founder in Dhairya's session: "We have 60+ connections please note that. So change all old rules please").
  1. The root `CLAUDE.md` line "at most 4 shards, never beside the nightly refresh" is retired. This is the founder's OK that item 7 of the 2026-11-01 entry asked for.
  2. Data loads use up to 40 connections in company-disjoint shards, with no fixed shard count. The 60-backend preflight and in-run pause (items 4 and 5 of 2026-11-01) stay.
  3. The 18:00–21:30 UTC nightly window is no longer a fixed no-go. A job checks before each step whether `pipeline-refresh` is running. A full-population job pauses while it runs. A job scoped to a set of companies may run alongside it.
  4. The `pipeline/CLAUDE.md` "~15 connections" line was stale. `max_connections` is 90 (measured 2026-11-12, 14 in use).
- **Founder decision of 2026-11-01: database connection budget for data loads** (typed by the founder in Dhairya's session, scrooner-df, and relayed to the release approver; the approver did not hear it directly). In the founder's words: "Great we have 90 connections limits. Use maximum connections" and "Faster the process. Use shard."
  1. Measured: `max_connections` = 90 on the dev Supabase (checked by the approver 2026-11-03, 16 in use).
  2. Budget within that (Dhairya's, under delegation): data loads use at most **40 connections**. The rest stays free for the app, backend, nightly refresh and superuser slots.
  3. Heavy jobs connect directly or through the transaction pooler, run outside the 18:00–21:30 UTC nightly window and set their own `statement_timeout`.
  4. Shards are company-disjoint: two writers never touch one company's rows.
  5. A 60-backend preflight runs at the start of a job, and every shard re-checks it during the run, pausing while `pg_stat_activity` exceeds 60.
  6. Example: the FSN cohort write runs 16 shards × at most 2 connections.
  7. The root `CLAUDE.md` line "at most 4 shards" is not changed by this entry; changing it needs the founder's OK. Until then, this entry governs data loads that stay within the 40-connection budget.

## Locked data decisions

- The Collector is dumb, lossless and immutable: it fetches and preserves raw SEC responses plus provenance, timestamps and checksums.

- The Collector does not calculate ROIC/TTM, repair facts, map XBRL concepts or decide fiscal quarters.

- Bootstrap with SEC bulk archives; run incremental updates through SEC APIs and daily indexes.

- Use a declared SEC User-Agent and keep the aggregate internal request rate at or below 8 requests per second.

- Jobs must be idempotent, resumable, deduplicated and reconciled; failures go to an inspectable dead-letter/error path.

- Raw objects live in Supabase Storage; ingest metadata and downstream structured facts live in Postgres.

- Initial logical schemas: raw, core, analytics and app.

- **Market-price vendor: Alpaca Markets (resolved 2026-08-17, re-evaluated and reconfirmed 2026-08-24).** Closes the "Market price source and delay" open decision below — real API credentials provided directly by the founder, stored in `pipeline/.env` (gitignored, never committed) with placeholders in `.env.example`. Unblocks the 6 price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield), Tier A's price-dependent candidates (doc 18), and the company page's currently-null top-ratios fields. **2026-08-24 re-evaluation**: a real EODHD Commercial Display quote (€300/month, required specifically because Scrooner displays actual price values to end users, not just internal use) was obtained and compared against the already-built, free Alpaca `delayed_sip` feed. Since the actual requirement (15-minute-delayed pricing) is exactly what Alpaca's `delayed_sip` already provides, Alpaca was reconfirmed rather than switched — no functional gap Alpaca has that EODHD would close for this use case. Integration into the full 5,258-company population is tracked in `doc/execution-plans/30_Data_Moat_Full_Population_Strengthening_Plan.md` (Track 1), not yet complete as of this addendum.

- **yfinance sector/industry: promoted from dev-tool-only to a stored, production-facing reference field (decided 2026-09-06, explicit founder direction, supersedes `doc/planning/y-finance.md`'s original recommendation).** The original doc recommended yfinance for dev-time prototyping and offline cross-checks only, never stored or shown to a user, citing Yahoo's own personal-use-only terms with no commercial tier to license around (unlike FMP). That recommendation is superseded for this one use: `core.company.y_sector`/`y_industry` (migration `0044`, `company_master/yfinance_industry.py`) are now real, persisted columns, backfilled for the full active population and usable in production features (starting with peer comparison) — kept strictly separate from `core.company.sector`/`sector_reason` (the SIC-derived taxonomy), never merged. The founder made this call knowingly, after the tradeoff was surfaced directly (Yahoo ToS risk vs. peer-comparison quality) — this is a deliberate risk acceptance, not an oversight. Revisit if Yahoo's terms enforcement changes, or before any B2B/API redistribution of this field.

- **Founder data decisions of 2026-11-04** (relayed to the release manager by scrooner-0f, the chief of staff, as the founder's decisions; the release manager did not hear them directly). They bind the top-1000 data programme:
  1. **SEC request budget:** no cap. The 4 requests per second limit and the sec.gov-only rule stay.
  2. **Q4 dividends per share** may be derived as the filed full-year value minus the filed nine-month value on the same share basis. Never-derive still applies to EPS.
  3. **Capex** includes leased fleets, capitalized software, the discontinued-operations block, turnarounds, REIT tenant improvements and construction in progress. It excludes oil and gas property and acreage acquisitions.
  4. **Buybacks** are cash repurchases of the company's own common stock. They exclude tax-withholding shares, excise tax, employee-plan purchases, option-exercise items, subsidiary buybacks and share swaps.
  5. **Total debt** includes finance leases disclosed in the notes.

- **Founder decision of 2026-11-12: value source for custom-tag lines** (the founder chose the option in Dhairya's session, the chief of staff; recorded by Dhairya). Under the hybrid build (FSN to learn which tag is what, the SEC company API for values), a line the company prints only under its own extension tag takes its value from the filing's own XBRL through SEC's FSN data (`fsn.value`, undimensioned, same accession and period), checked against the printed R page. Standard us-gaap tags keep the SEC company API (`core.fact`) as the value source. Each cell records which source it used. Reason: the companyfacts API carries only the us-gaap, dei, ecd and ffd namespaces; FSN was shown equal to the filing XBRL (20 of 20 filings, 22,774 of 22,774 numbers).

- **Founder decision of 2026-11-12: full filing read before certification** (typed by the founder in Dhairya's session: "read as much as possible, test as much as possible, then we can have correct data"). A company is certified only after its latest 10-K is read in full (face statements, the notes behind template data points, the segment note) plus one filing at each tag-change era, with every template data point tested against the printed value. Reads are kept in `data-team/companies/reads/`.

- **Founder decision of 2026-11-04: development phase, rebuild instead of patch (corrected the same day)** (relayed to the release manager by scrooner-0f, the chief of staff, as the founder's decision and correction; the release manager did not hear them directly). The hybrid build replaces the old mapping and its values in `canonical_fact` for the 1,000 companies. Values are rebuilt from the FSN filing structure and each cell is proven on its own. **There is no old-table fallback and no switch view.** An earlier version of this entry described a new `canonical_fact_v2` table, the old table kept as a fallback and a view that switches between them; the founder corrected that. The per-family patch release packages are superseded, and no new patch packages are landed. Packages already on main stay as records and the ones already applied stay applied.


- **Founder decision of 2026-11-01: company-wise FSN statement store** (approved by the founder to scrooner-ca, the chief of staff, and relayed to the release approver; the approver did not hear it directly). Design: `data-team/strategy/FSN-STORE-DESIGN-2026-11-01.md`. It is how the rebuild-instead-of-patch decision above is carried out:
  1. Every 10-K/10-Q since 2014 in the FSN set is loaded into a new `fsn` schema (migration 0118). The load is per company and runs in one transaction per company. Each print is a separate vintage row, and nothing is overwritten or marked current.
  2. Lines map to canonical concepts by standard tag, then by calculation position for custom tags. A label may demote a line but never promote it. A combined line is never mapped as a single concept.
  3. The winner for a cell is the latest accepted print whose column passes every filing check. If the latest print fails a check, the cell is blank with a reason. It never falls back to an older vintage.
  4. A quarter with no printed 3-month column is derived only when its inputs share an accounting basis (no restatement break between them plus a re-print witness). Otherwise it is a reasoned blank. EPS and instants are never derived.
  5. `analytics.canonical_fact` stays the serving table, with no view and no fallback. A company is written only when all seven completion conditions in design §5 hold. Migration 0119 then makes `fsn_cells` that company's only writer, so the nightly job can no longer overwrite it.
  6. This retires each lane's own whole-cohort FSN pass and quarter derivation, `materialize_fsn_fact`, `unrestated_single_value` and migration 0101 (left unapplied).
  7. Production steps need three separate founder authorizations, typed in the release approver's session: (1) migrations 0117/0118/0119; (2) the MSFT and HD pilot; (3) the 1,000-company cohort.


- **Founder ruling of 2026-11-01: sector templates and 100% coverage** (typed by the founder in scrooner-ca, the chief of staff's session, and relayed to the release approver; the approver did not hear it directly). In the founder's words: "I don't want blank cells. If a sector's companies don't report a field, set different templates sector-wise, but keep 100% coverage." It amends the company-wise FSN statement store entry above:
  1. A field is shown for a company only if its sector template includes that field, and every displayed cell has a value.
  2. Coverage is valued cells ÷ template cells, with a target of 100%. This replaces the 95% bar in gates G2 (MSFT and HD at 100% of their template) and G3 (the top 100 at 100%).
  3. A line the company prints combined with others (for example D&A inside another line) is shown as the company's own combined line in its template, never as a blank, and never mapped as a single concept.
  4. Periods before a company's first filing or IPO are outside its window and are not cells.
  5. Any other blank is a defect to fix: derive it under SAME_BASIS, release it after the Verifier, or capture it from the filing. A blank is never a resting state.
  6. The target does not loosen any correctness rule: never fabricate a value, never fall back to an older vintage, never derive EPS or instants, and pass every filing check. Until a defect is fixed, the cell stays blank with its reason and the company does not pass the gate.
- **Founder ruling of 2026-11-01: BDC revenue and earnings** (the founder typed "yes" in scrooner-df, Dhairya's session, and Dhairya relayed it to the release approver; the approver did not hear it directly). For business development companies (ARCC, BXSL; the `bdc` template, `data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md` §8):
  1. Revenue = total investment income as printed (interest, dividend and fee income).
  2. The earnings line = net investment income (NII) as printed.
  3. Both are face lines taken as printed, never derived.
- **Founder metric decisions of 2026-11-13** (founder: "yes go ahead for everything", relayed by the chief of staff in the task brief). Metric registry, `pipeline/src/scrooner_pipeline/metrics/`:
  1. A ratio whose denominator can go negative (equity, earnings, EBITDA, FCF, invested capital) is null when the denominator is below zero, reason `negative_ratio_undefined` ("not meaningful"); zero keeps `zero_denominator` (ROIC: `zero_invested_capital`). Applies to ROE, ROIC, P/E, price/book, debt/equity, OCF/net income, EPS dilution spread, payout ratio, EV/EBITDA, net debt/EBITDA, debt/EBITDA, buybacks and dividends as % of FCF. Margins (revenue denominator) keep current behaviour. Formula versions bumped; old proofs are stale by design.
  2. ROIC invested capital = total debt (including finance leases) + equity - cash; operating leases are out of invested capital.
  3. Insurers are treated like banks for corporate-only metrics (`not_applicable_insurer`).
  4. Strict inputs: a metric is blocked when any input is UNCHECKED.
  5. Deferred: shareholder yield and the quality-flag formulas.
  6. Deferred until after certification: the TTM-margin and net debt/EBITDA alignment.

## Rejected or deferred directions

| **Item**                           | **Disposition**   | **Revisit trigger**                                        |
|------------------------------------|-------------------|------------------------------------------------------------|
| Split Astro/Next.js frontend       | **Superseded 2026-09-05** | Replaced by one Next.js App Router application; see doc 43. |
| Separate application product subdomain | **Superseded 2026-09-05** | Retired. All product routes live on the apex origin. |
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
