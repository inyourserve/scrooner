# Project Documentation

**A clean, fundamentals-first stock research site for the US**

---

## 1. What We're Building

**One line:** The calm, trustworthy, free place to *understand a company* — built for the millions of Americans who pick individual stocks but find today's tools cramped, overwhelming, or locked inside their broker.

### The opportunity

India has **Screener.in** — a beloved, bootstrapped, free stock-research site used by ~16 million people, profitable on a tiny team. The US has no equivalent loved product, not because Americans don't invest, but because:

- **Incumbents are polarized.** Finviz is dense and trader-focused; Stock Rover is powerful but overwhelming (users take weeks to learn it); brokers bundle "good enough" screeners that keep people locked in. Nobody owns the clean, fundamentals-first, calm lane.
- **The data is now free.** US company financials come from **SEC EDGAR** — 15+ years of structured data, public domain, royalty-free, fully redistributable. The data-cost moat that used to block a free product is gone.
- **The audience is large.** ~50M Americans own individual stocks; ~15M actively research them; two-thirds of new brokerage accounts are opened by under-45s who expect clean, modern UX.

### The product

A fast, beautiful, mobile-friendly research site with three surfaces on one owned data asset:

1. **Company pages** — 10-year financials, key ratios, and a plain-English read of any US stock, on one calm screen. The crown jewel.
2. **Screener** — filter stocks on fundamentals, with natural-language querying and shareable public screens.
3. **Data API** (later) — sell the clean, parsed data to other builders.

We parse EDGAR once into our own database, then serve it many ways. **The data asset is the moat; the pages are just views of it.**

### Why we win

- **No data-cost trap.** EDGAR is free and ours to keep — we can be free-forever and stay independent, like Screener.in.
- **UX is the wedge.** We beat incumbents on feel: clean, calm, readable, mobile-friendly — not on having 650 metrics.
- **SEO compounds.** Thousands of indexed company and screen pages become a self-reinforcing, near-free growth engine.
- **Trust is the durable moat.** Accurate data plus independence (research separate from monetization) is what earns loyalty money can't buy.

### How it makes money

Free core, monetized four ways: **premium subscriptions**, **broker affiliate** (paid per funded signup — no license needed), **ads** on high-traffic pages, and a **B2B data API**. Target milestone: **$10k/month (~1,000 subscribers)** — then compound from there.

### The bet

The idea is proven twice (Screener.in, Finviz). The tech is doable by a small team. The economics work at human scale. The two real risks are **data accuracy** (our moat and our trust) and **SEO/distribution** (slow, back-loaded, requires patience). Win those two and the rest is execution.

**North star:** be the site a US investor opens first to understand a company — and trusts enough to come back to every time.

---

## 2. Tech Stack

Chosen for three constraints the product implies: (a) thousands of pages must rank in Google, (b) a small team has to run this without a large ops burden, (c) the core hard problem is a data pipeline (parsing messy EDGAR filings into clean, comparable numbers), not app plumbing.

### Frontend — split by page type

Pages fall into two clearly different jobs, so the frontend is split accordingly instead of forcing one framework to do both:

| Surface | Pages | Framework | Why |
|---|---|---|---|
| **Static / SEO** | Company pages, saved/shared screens, marketing pages | **Next.js** | Zero JS by default, islands only where needed. These are the pages Google indexes and the pages the SEO growth engine depends on — Next.js gives them the lowest possible weight and the highest realistic Core Web Vitals ceiling. |
| **Dynamic / logged-in** | Screener tool, screen builder, account, billing | **Next.js (App Router)** | Genuinely stateful, interactive, behind auth. Next's app ecosystem (routing, server actions, mature Supabase/Stripe integrations) fits an application, not a content page. |

Split across **two subdomains**: `scrooner.com` (Next.js) and `scrooner.com/app` (Next.js) — see 3.1 for why this is safe for SEO here specifically, and how login carries across both.

| Layer | Choice | Why |
|---|---|---|
| Shared UI | **Tailwind CSS + a shared component package** | React components in `packages/ui` render as Next.js components directly and as Next.js islands (`client:load`/`client:visible`) where interactivity is needed — one design system, two runtimes. |
| Charts | **Recharts / visx** | Lightweight, good enough for 10-year financial charts without a heavy charting license; used as an island in Next.js, a normal component in Next. |
| Hosting | **Vercel** (both projects) | Native support for both frameworks; one platform, one team to learn, edge routing handles the domain split (3.1). |

### Backend / data layer

| Layer | Choice | Why |
|---|---|---|
| Primary database | **PostgreSQL on Supabase** | Relational fits financial statement data well (companies → filings → line items → ratios); strong indexing for screener filters. Committing to Supabase specifically (over Neon) so the database and auth sit on one platform instead of two. |
| Data pipeline | **Python** (pandas, `sec-edgar-downloader` / direct EDGAR XBRL API) | EDGAR filings are XBRL; Python has the mature tooling for parsing, normalizing, and validating financial statements. Runs as scheduled batch jobs, not request-time code. |
| App-facing API | **Next.js route handlers / tRPC**, consumed by both the Next.js site (build-time/ISR fetches) and the Next app (runtime) | One API surface, two consumers — avoids duplicating data-access logic. |
| Public Data API (Phase 3) | **FastAPI (Python)**, separate service | Split out once external developers consume it — needs its own auth, rate limiting, and versioning independent of the website. |
| Caching | **Redis** (Upstash) | Hot company pages and common screener queries; keeps Postgres load down as traffic grows. |
| Search (tickers/companies) | **Postgres full-text search** initially; **Meilisearch/Typesense** if it outgrows that | Avoid an early dependency on Elasticsearch-class infra. |

### Auth, billing, ops

| Layer | Choice | Why |
|---|---|---|
| Auth | **Supabase Auth**, session cookie set with `Domain=.scrooner.com` via `@supabase/ssr` | No third-party auth vendor — Supabase already owns the database, so auth rides on the same platform instead of adding a separate identity provider. Cross-subdomain sharing isn't automatic like Clerk's satellite-domain feature, but it's a standard, documented cookie-domain option in `@supabase/ssr`, not a hack. |
| Payments | **Stripe** | Standard for subscriptions; also used to gate premium features. |
| Ads | **Google Ad Manager / AdSense** | Standard programmatic path for high-traffic content pages. |
| Monitoring | **Sentry** (errors) + **Vercel Analytics / Plausible** (traffic) | Lightweight, low-maintenance observability for a small team. |
| CI/CD | **GitHub Actions** → Vercel (both frontends) / container registry (pipeline & data API) | Standard, free at this scale. |

### Trade-off, stated plainly

Splitting Next.js/Next buys the lowest realistic weight on the pages Google ranks, at the cost of two frontend codebases, two build systems, and a shared-session/shared-design-system setup to maintain instead of one. That cost is worth paying here because the static pages *are* the growth engine — but it's a deliberate choice, not the default, and it puts more discipline on `packages/ui` (design system) and the shared cookie config (3.1) to keep the two feeling like one product.

**Why `scrooner.com/app` as a subdomain, not a subfolder:** the usual worry with subdomains is splitting SEO/domain authority across two properties. That worry applies when content you want ranked lives on the subdomain. Here it doesn't — every URL in 3.2 that's meant to rank (`/stock/`, `/screens/`, `/learn/`, `/sector/`, `/guides/`, `/blog/`, `/help/`) lives on the Next.js site at the root domain regardless. `scrooner.com/app` only ever serves pages that are either behind login (`/account`, `/watchlist`) or not realistic ranking targets on their own (`/screener` — 14k/mo search volume but dominated by Finviz/TradingView/brokers; it earns traffic from internal links off company pages and screens, not by ranking itself). So the subdomain split costs nothing on SEO in this specific case, while removing the edge-routing/rewrite layer entirely — two independent Vercel projects, two independent deploys, no shared-domain proxy config to maintain. That's a meaningful simplification for a small team, so it's the better call than the single-domain rewrite approach.

---

## 3. Structure

### 3.1 System architecture

```
                     ┌─────────────────────┐
                     │      SEC EDGAR       │
                     │  (XBRL filings, free) │
                     └──────────┬───────────┘
                                │  scheduled fetch
                                ▼
                     ┌─────────────────────┐
                     │   Ingest Pipeline    │
                     │  (Python, batch jobs)│
                     │  parse → normalize   │
                     │  → validate → ratios │
                     └──────────┬───────────┘
                                │  writes
                                ▼
                     ┌─────────────────────┐
                     │   PostgreSQL (core)  │
                     │  companies, filings, │
                     │  line items, ratios  │
                     └──────┬───────┬───────┘
                            │       │
              reads (build/ISR)     reads (runtime)
                            │       │
                            ▼       ▼
              ┌───────────────┐   ┌───────────────┐
              │  Next.js site    │   │  Next.js app   │
              │  (static/SEO)  │   │  (dynamic)     │
              │  scrooner.com  │   │  app.scrooner. │
              │  - company pgs │   │    com         │
              │  - saved screens│  │  - screener    │
              │  - marketing   │   │  - screen build│
              └───────┬────────┘   │  - account     │
                      │            │  - billing     │
                      │            └───────┬────────┘
                      │   separate Vercel  │
                      │   projects, shared │
                      │   cookie domain    │
                      └────────┬────────────┘
                               ▼
                   ┌─────────────────────┐
                   │  Auth session cookie   │
                   │  Domain=.scrooner.com  │
                   │  (Supabase Auth via    │
                   │  @supabase/ssr)        │
                   │  readable by both      │
                   │  scrooner.com and      │
                   │  scrooner.com/app      │
                   └─────────────────────┘
                               │
                      ┌────────┴────────┐
                      │  Redis cache      │
                      │  hot pages/queries│
                      └───────────────────┘
```

Single source of truth: EDGAR is parsed **once** into Postgres; every surface (Next.js pages, Next app, later the data API) reads from that same asset rather than re-deriving numbers.

**Two subdomains, not one domain with rewrites:** `scrooner.com` (Next.js) and `scrooner.com/app` (Next.js) deploy as two independent Vercel projects — no edge-routing/rewrite layer to maintain. This is safe for SEO here specifically because every page meant to rank lives on `scrooner.com` (see 3.2's "why subdomain" note); `scrooner.com/app` only ever serves logged-in or tool pages that were never realistic ranking targets anyway. Login carries across both because the auth cookie is explicitly set with `Domain=.scrooner.com` in the `@supabase/ssr` cookie config — Supabase doesn't hand you cross-subdomain sharing automatically the way Clerk's "satellite domain" feature does, so this one line of config is the thing to get right and test early, but it's a standard, documented option, not a workaround. The one cross-domain flow to wire up deliberately: saving a screen in the builder on `scrooner.com/app/screens/new` triggers a build hook / on-demand revalidation call that publishes the static page at `scrooner.com/screens/{slug}/` on the Next.js side.

### 3.2 URL structure

Finalized using two inputs: (1) reverse-engineering Screener.in's actual site structure via Ahrefs, since it's the proven model for this product category, and (2) US keyword research via Ahrefs to check which of those page types actually carry search demand in the US, and where the US market's demand differs from India's.

#### What Screener.in's structure actually is

Pulled their top pages by traffic and their full crawled URL list (Ahrefs Site Explorer). Grouping ~300+ URLs by pattern, their entire site reduces to eight page types:

| Pattern | Example | Purpose |
|---|---|---|
| `/` | `screener.in/` | Homepage |
| `/company/{TICKER}/` (+ optional `/consolidated/`) | `/company/TCS/consolidated/` | The company page — by far the highest-traffic page type; a single URL ranks for hundreds of keyword variants (`tcs share price`, `tcs pe ratio`, `tcs quarterly results`, etc.) |
| `/company/{INDEX_CODE}/` | `/company/CNX500/` | Reused for index/constituent-list pages (Nifty 500, BSE 500) — same template, different data shape |
| `/market/` → `/market/{sector}/` → `/…/{industry}/` → `/…/{sub-industry}/` | `/market/IN08/IN0801/IN080101/` | Hierarchical sector → industry → sub-industry drill-down, each listing constituent companies |
| `/screens/` | `/screens/` | Directory of public/popular screens |
| `/screens/{id}/{slug}/` | `/screens/3/highest-dividend-yield-shares/` | An individual saved, shareable screen — these rank well on their own (e.g. this one ranks for "best dividend stocks for beginners") |
| `/explore/`, `/ai/` | — | Discovery and AI-assistant entry points |
| `/guides/{slug}/`, `/docs/changelog/{slug}/` | `/guides/creating-screens/`, `/docs/changelog/Screener-AI/` | Static help/guide pages and a changelog-as-blog |

Auth (`/login/`, `/register/`) and account/premium pages sit on the same domain at the root level. Their help center is a **separate subdomain** (`support.screener.in`) — notably, this is the one place they split off a subdomain, and it's their lowest-value-add page type (a generic help-desk tool), not a pattern worth copying for pages that matter for SEO.

#### What US keyword research says about each pattern

| Page type | Signal | Verdict |
|---|---|---|
| Company pages (`AAPL stock`, `aapl stock price`, `aapl pe ratio`, `aapl stock dividend`, `aapl stock chart`, `aapl stock earnings date`…) | `aapl stock` alone: **694,000/mo**. Dozens of sub-intent variants (price, chart, dividend, split, earnings date, forecast) all cluster around one ticker. | Confirms Screener.in's model directly: **one comprehensive page per ticker** should capture price, financials, ratios, and dividend data together rather than splitting into sub-pages — matches how people actually search. |
| Saved/public screens (`dividend stocks`, `best dividend stocks`, `high dividend stocks`, `monthly dividend stocks`…) | This cluster alone is **~150,000+/mo combined** in the US — arguably bigger relative demand than what Screener.in's equivalent page captures in India. | High-value page type; publishing curated screens as static, shareable pages is one of the highest-leverage SEO plays available here. |
| Glossary / definitional (`pe ratio`, `what is pe ratio`, `what is a good pe ratio`, `pe ratio formula`…) | ~28,000/mo for `pe ratio` alone, ~9,600/mo combined for definitional variants of just that one term. Screener.in barely invests here. | **Gap Screener.in doesn't fill.** A `/learn/` glossary of financial terms is low-competition, high-volume, and compounds across dozens of terms (P/E, ROE, market cap, EPS, dividend yield, debt-to-equity…) — a real opportunity, not just a nice-to-have. |
| Sector/industry lists (`best tech stocks`, `best tech stocks to buy now`…) | Real but modest volume (~1,200–1,300/mo for top terms), with commercial/transactional intent. | Worth building (mirrors Screener.in's `/market/` hierarchy) but lower priority than companies/screens/glossary. |
| Ticker-vs-ticker comparisons (`aapl vs msft`, `msft vs aapl stock`…) | Under 20/mo for essentially every variant tested. | **Not worth a static SEO URL.** Build compare-two-stocks as an interactive feature inside the (dynamic) screener tool, not as indexed pages. |
| Stock screener tool itself (`stock screener`) | 14,000/mo but very high difficulty (77) — dominated by Finviz, TradingView, brokers. | The tool page is table-stakes, not a realistic ranking target on its own; it earns traffic by being linked from the company pages and screens, not by competing head-on for this term. |

#### Finalized URL structure

| URL | Surface | Notes |
|---|---|---|
| `/` | Next.js | Homepage |
| `/stock/{ticker}/` | Next.js | Company page — the crown jewel, one page per ticker (lowercase in the URL, e.g. `/stock/aapl/`; uppercase shown on-page). Uses `stock` rather than Screener.in's `company` because US search behavior centers on `AAPL stock`, not `AAPL company`. No `/consolidated/` split — not a US GAAP concept. |
| `/screens/` | Next.js | Directory of public screens |
| `/screens/{slug}/` | Next.js | An individual saved/shared screen (e.g. `/screens/highest-dividend-yield-stocks/`) — publishes automatically once built in the Next.js screen builder |
| `/sector/{sector}/`, `/sector/{sector}/{industry}/` | Next.js | Sector/industry drill-down, mirrors Screener.in's `/market/` hierarchy at lower priority |
| `/learn/{term}/` | Next.js | Financial glossary — the gap Screener.in leaves open; highest ROI new page type versus their model |
| `/guides/{slug}/`, `/about/`, `/privacy/`, `/terms/` | Next.js | Static marketing/legal pages |
| `/blog/{slug}/` | Next.js | Changelog-as-blog, same role as Screener.in's `/docs/changelog/` |
| `/help/{slug}/` | Next.js | Help/FAQ content, kept on the main domain (not a separate subdomain like Screener.in's `support.screener.in`) to keep all SEO equity on one root domain |
| `/screener` | Next.js | The interactive filter tool |
| `/screens/new`, `/screens/{id}/edit` | Next.js | Screen builder — publishes out to the static `/screens/{slug}/` Next.js page on save |
| `/compare` (tool, not indexed pages) | Next.js | Ticker-vs-ticker comparison as an interactive feature only — no static URLs, since search demand doesn't justify them |
| `/watchlist` | Next.js | Saved companies, behind login |
| `/account`, `/billing`, `/login`, `/register` | Next.js | Auth and subscription |

Everything in the Next.js column lives on `scrooner.com`; everything in the Next.js column lives on `scrooner.com/app` (3.1). This directly informs the `apps/app` vs `apps/app` route layout in 3.3.

#### Auth: logged-in vs logged-out pages

No third-party identity provider — auth runs on **Supabase Auth**, the same platform as the database, using `@supabase/ssr` on both the Next.js app and the Next.js site. `scrooner.com/app` does the actual sign-in/sign-up work and owns session refresh; `scrooner.com` only ever *reads* the session (server-side, from the shared cookie) to decide things like whether the nav shows "Sign in" or an account menu — it never handles credentials itself.

The piece that has to be built deliberately (Supabase doesn't give this for free the way Clerk's satellite-domain feature does): the session cookie must be set with `Domain=.scrooner.com` in the `@supabase/ssr` cookie options on the Next.js app, so it's readable on both subdomains. Get this one setting wrong and the two apps silently stop sharing a session — worth a dedicated integration test.

| Route (`scrooner.com/app`) | Purpose |
|---|---|
| `/login` | Sign in |
| `/register` | Sign up |
| `/forgot-password` | Password reset request (Supabase's built-in email flow) |
| `/logout` | Not a rendered page — calls `supabase.auth.signOut()`, clears the shared cookie, and redirects to `scrooner.com` (back to the public site, not a dead end) |

Redirect-back convention: every path into `/login` carries a `redirect_url` query param that the app reads after `signInWithPassword`/OAuth completes and manually redirects to. Example: clicking "Save to watchlist" on `scrooner.com/stock/aapl/` while logged out sends the user to `scrooner.com/app/login?redirect_url=https://scrooner.com/app/watchlist?add=AAPL`. Unlike Clerk, this redirect has to be handled explicitly in app code rather than configured declaratively — a small but real bit of extra plumbing that comes with dropping the third-party vendor.

**Deliberately not gating the whole app** — only the personalized actions require login, to keep the free-forever, low-friction positioning from the original pitch intact:

| Route | Auth required? | Why |
|---|---|---|
| `/screener` | No | Letting people use the filter tool before signing up *is* the conversion funnel — gate the "save this screen" action inside it, not the page itself |
| `/compare` | No | Same reasoning — a stateless tool, no reason to wall it off |
| `/screens/new`, `/screens/{id}/edit` | Yes | Writes to a user's saved screens |
| `/watchlist` | Yes | Personalized, per-user data |
| `/account`, `/account/billing` | Yes | Account and subscription state |

### 3.3 Repository layout

Monorepo, so the pipeline, both frontends, and shared data/design contracts evolve together without version drift.

```
scrooner/
├── apps/
│   ├── site/                  # Next.js — static/SEO surface
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   │   ├── stock/[ticker].tsx
│   │   │   │   ├── screens/index.tsx
│   │   │   │   ├── screens/[slug].tsx
│   │   │   │   ├── sector/[sector]/[[industry]].tsx
│   │   │   │   ├── learn/[term].tsx
│   │   │   │   ├── guides/[slug].tsx
│   │   │   │   ├── blog/[slug].tsx
│   │   │   │   ├── help/[slug].tsx
│   │   │   │   └── index.tsx
│   │   │   ├── components/     # Next.js components + React islands
│   │   │   └── layouts/
│   │   └── Next.js.config.mjs
│   │
│   ├── app/                    # Next.js — dynamic/logged-in surface
│   │   ├── app/                 # App Router routes
│   │   │   ├── screener/
│   │   │   ├── screens/new/
│   │   │   ├── screens/[id]/edit/
│   │   │   ├── compare/          # in-app tool, not statically indexed
│   │   │   ├── watchlist/
│   │   │   ├── account/
│   │   │   └── api/              # route handlers / tRPC
│   │   ├── components/
│   │   └── lib/
│   │
│   └── data-api/                # FastAPI service (Phase 3, B2B data API)
│       ├── routers/
│       ├── auth/                 # API keys, rate limiting
│       └── main.py
│
├── pipeline/                     # Python EDGAR ingest + normalization
│   ├── fetch/                    # download filings from EDGAR
│   ├── parse/                    # XBRL → structured line items
│   ├── normalize/                 # standardize across companies/periods
│   ├── ratios/                    # derived metrics (P/E, ROE, margins, etc.)
│   ├── validate/                   # data-quality checks before publish
│   └── jobs/                       # scheduled entrypoints (cron/Actions)
│
├── packages/
│   ├── db/                       # Postgres schema, migrations, shared queries
│   ├── types/                    # shared TypeScript/Python type contracts
│   └── ui/                        # shared design-system components
│                                    # (consumed as-is in Next, as islands in Next.js)
│
├── infra/
│   ├── ci/                       # GitHub Actions workflows
│   ├── auth/                      # shared @supabase/ssr cookie-domain config (Domain=.scrooner.com)
│   └── env/                       # environment configs per stage, incl. DNS for scrooner.com / scrooner.com/app
│
└── docs/
    ├── DOCUMENTATION.md           # this file
    └── architecture-decisions/    # ADRs as the system evolves
```

### 3.4 Data model (core entities)

- `companies` — ticker, name, sector, metadata
- `filings` — source EDGAR filing references per company/period
- `financial_line_items` — normalized statement data (income statement, balance sheet, cash flow)
- `ratios` — derived metrics computed from line items
- `screens` — saved/shareable user screener queries (rendered statically by Next.js once saved; built/edited in Next)
- `users` / `subscriptions` — auth and billing state (owned by Next, read by Next.js only via the shared session cookie for "is this user logged in / premium" checks)

### 3.5 Build phases

1. **Phase 1 — Core asset:** ingest pipeline + Next.js company pages (the crown jewel; proves data quality and SEO).
2. **Phase 2 — Screener:** Next.js screener + screen builder on top of the same data; saved screens publish back out as static Next.js pages.
3. **Phase 3 — Data API:** split out `apps/data-api` once external demand justifies it.
4. **Monetization layered in throughout:** ads on high-traffic Next.js pages early, subscriptions once the Next screener/saved-screens exist, affiliate links on company pages from day one.
