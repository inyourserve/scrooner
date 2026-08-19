# 06 — Scrooner Project Breakdown and Execution Plan

How the whole of Scrooner splits into independent, sequenced parts — and why the Data Engine (Collector → Normalizer → Mapper) is only the foundation, not the whole project.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes

---

## Why break it up

Before timelines, Scrooner splits into **independent project parts** so the team executes one system at a time.

The important distinction: **Collector, Normalizer and Mapper are only the Data Engine.** They are not the whole Scrooner project — they're the plumbing everything else stands on.

## The 14 parts

| # | Project Part | Purpose | Start |
|---|---|---|---|
| **1** | **Data Collector** | Fetch source data and preserve raw data | **NOW** |
| **2** | **Normalizer** | Convert SEC/XBRL data into consistent financial facts | After Collector |
| **3** | **Mapper & Metrics Engine** | Calculate Scrooner metrics such as FCF, ROIC, CAGR, dilution | After Normalizer |
| **4** | **Company Master / Market Data** | Ticker, CIK, exchange, sector, price, market cap | Parallel later |
| **5** | **Screener Engine** | Filter companies using structured conditions | After metrics |
| **6** | **AI Query Engine** | Natural language → structured screener filters | After screener |
| **7** | **Backend / Product API** | Expose company, screener, user and screen data | Later |
| **8** | **Frontend Product** | Homepage, search results, company pages, screens | Later |
| **9** | **User System** | Auth, saved screens, preferences, rate limits | Later |
| **10** | **Billing** | Free/Pro access and $100/year subscription | Pre-launch |
| **11** | **Internal Admin** | Data QA, mapping overrides, failed jobs, company management | Alongside data |
| **12** | **SEO / Content Engine** | Guides, glossary, public screens, landing pages | After MVP |
| **13** | **Analytics & Monitoring** | Product analytics, errors, pipeline health | Before beta |
| **14** | **Infrastructure / DevOps** | Deployments, cron/jobs, DB backups, observability | Throughout |

## The dependency chain

```text
                    SCROONER
                       │
                DATA FOUNDATION
                       │
              ┌────────┴────────┐
              │                 │
          Collector       Company Master
              │
          Normalizer
              │
       Mapper / Metrics
              │
         Screener Engine
              │
        AI Query Engine
              │
        Product Backend
              │
            Frontend
              │
      User/Auth/Saved Screens
              │
            Billing
              │
             LAUNCH
```

The critical path is **Data → Screener → Product**. Everything else (Internal Admin, SEO/Content, Analytics & Monitoring, Infrastructure/DevOps) runs alongside or after, not instead of, this spine.

---

## Part 1 — Data Collector

This is what ships **first**.

Its responsibility should be extremely narrow:

> **Collect source data reliably, save it in raw form, track what was collected, and make it reproducible.**

### The Collector should NOT

- calculate ROIC
- calculate FCF
- decide which XBRL concept means revenue
- clean financial statements
- calculate CAGR
- generate screens
- contain AI
- expose frontend APIs

That belongs later, to the Normalizer, the Mapper & Metrics Engine, the Screener Engine, and the AI Query Engine respectively. A Collector that starts transforming data instead of just recording it exactly as received has stopped doing its job — and broken the one thing the whole system is trusted for.

### Collector modules

| Module | Job |
|---|---|
| 1. Company Universe | Determines which companies Scrooner knows about |
| 2. SEC Identity / CIK Mapping | Maintains reliable ticker ↔ CIK ↔ name mappings |
| 3. SEC Company Facts Collector | Fetches SEC XBRL/company facts, saved exactly as received |
| 4. SEC Submissions Collector | Collects filing history — 10-K, 10-Q, 8-K, 20-F, 40-F, amendments |
| 5. Filing Metadata Collector | Maintains a structured index of what's been collected |
| 6. Filing Document Collector | Downloads actual filing artifacts (HTML, XBRL instance) when needed |
| 7. Raw Storage | Holds the raw payloads, untouched |
| 8. Scheduler | Decides when the next collection run happens |
| 9. Retry / Failure Handling | Retries transient failures without giving up or duplicating work |
| 10. Collection Logs | Records what happened, when, and to what |
| 11. Data Integrity Checks | Confirms nothing was lost or silently corrupted |

### 1. Company Universe

Determines which companies Scrooner knows about. This becomes the foundation for everything else.

```text
company_id
cik
ticker
company_name
exchange
status
```

### 2. SEC Identity Layer

Maintains reliable mappings — because a ticker isn't a permanent SEC identity, but a CIK is.

```text
AAPL
  ↓
0000320193
  ↓
Apple Inc.
```

**CIK is the SEC-side primary identity.** Treat it as such everywhere downstream.

### 3. Company Facts Collector

Fetches SEC XBRL/company facts. Saves the response **exactly as received**. No normalization — that's the Normalizer's job, not the Collector's.

```text
raw/sec/companyfacts/0000320193.json
```

### 4. Submissions Collector

Collects filing history: `10-K`, `10-Q`, `8-K`, `20-F`, `40-F`, amendments, accession numbers, filing dates, report dates. Raw first, always.

### 5. Filing Metadata

Maintains a structured collection index, so the team always knows exactly what's on hand.

```text
cik
accession_number
form
filing_date
report_date
source_url
download_status
collected_at
```

### 6. Filing Documents

Later, downloads required filing artifacts: primary filing HTML, XBRL instance, XBRL facts, metadata. **Do not** necessarily download every possible SEC attachment on Day 1. KISS BORING.

---

## Raw Storage Architecture

Raw storage is conceptually separate from application tables:

```text
raw_sources
raw_sec_companyfacts
raw_sec_submissions
raw_sec_filings
collector_runs
collector_errors
```

Or object storage for large raw JSON/files plus PostgreSQL metadata:

```text
Postgres
    ↓
What exists?
Storage
    ↓
Actual raw payload
```

This beats stuffing huge documents unnecessarily into relational tables — object storage holds the payloads, Postgres holds the metadata.

---

## Collector's Definition of Done

This is important. We should **not** say:

> "The Collector is finished because it downloads Apple."

**Collector V1 is done when:**

**Input:**
```text
CIK / company universe
```

**Output** — for every supported company:
```text
Company Facts raw payload
Submissions raw payload
Collection metadata
Timestamp
Source identifier
Status
```

**Operationally, it can:**

- resume after failure
- retry transient failures
- avoid unnecessary re-downloads
- respect SEC fair-access requirements
- log failures
- run repeatedly
- identify new filings
- preserve historical raw data

Then — and only then — the team moves to the Normalizer.

---

## Recommended repository structure

**Superseded 2026-08-14 — see doc 02.** Originally recommended as separate repos (`scrooner-data/`, `scrooner-web/`, potentially `scrooner-admin/`); reversed to a monorepo for solo-founder manageability. The Data Engine stays its own *subtree*, not its own repo:

```text
scrooner/                  # this repo — was "scrooner-web" in the original plan
├── pipeline/               # the Data Engine (was "scrooner-data")
│   ├── collector/
│   ├── normalizer/          # not yet scaffolded — added when that phase starts
│   ├── mapper/               # same
│   ├── common/
│   ├── db/
│   ├── jobs/
│   ├── tests/
│   └── scripts/
├── apps/site/                # Astro
├── apps/app/                  # Next.js
└── packages/                   # shared UI etc.
```

Admin (Django) can live in `pipeline/` alongside the data side if that stays operationally simpler, per the original note below — still true, just folder- rather than repo-scoped now.

Django Admin can live alongside the data/backend project if that stays simpler operationally.

---

## Execution order

Do **not** build all 14 parts simultaneously.

```text
PHASE 1   Collector
              ↓
PHASE 2   Normalizer
              ↓
PHASE 3   Mapper / Metrics
              ↓
PHASE 4   Screener Engine
              ↓
PHASE 5   AI Query
              ↓
PHASE 6   Frontend MVP
              ↓
PHASE 7   Auth + Saved Screens
              ↓
PHASE 8   Billing
              ↓
             LAUNCH
```

There will be some frontend/branding work in parallel later, but **the critical path is Data → Screener → Product.** For now, mentally ignore almost everything else and set the project board to:

> **SCROONER / DATA ENGINE / COLLECTOR**

## First milestone

Within the Collector's work, the first milestone is:

> **Given a US public company, Scrooner can reliably discover its SEC identity, collect its raw SEC datasets, preserve them unchanged, record exactly what was collected, and safely run again tomorrow without breaking or unnecessarily repeating work.**

That is the right first brick. After this, the team builds the **Collector-only execution plan** — architecture, database schema, folders, tasks, priorities, tests, and a 7-day target.
