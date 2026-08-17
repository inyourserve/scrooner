# 04 — Scrooner System Design and Technology Stack

The target architecture, service boundaries, data flow and operational
constraints.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes

---

## Architecture summary

Scrooner is divided into three concerns: a separate data pipeline that
creates trusted financial data; a public SEO website; and an
authenticated interactive application. They share governed data, but
each has a narrow responsibility.

## System topology

| **Layer**         | **Primary technology**                       | **Responsibility**                                                                        |
|-------------------|----------------------------------------------|-------------------------------------------------------------------------------------------|
| Public web        | Astro + Tailwind                             | Marketing, guides, glossary, indexable company and curated screen pages on scrooner.com.  |
| Application       | Next.js App Router + Tailwind/shared UI      | Prompt/screener interaction, auth, saved screens, limits and billing on app.scrooner.com. |
| Data platform     | Python 3.12 + Polars + Postgres              | Collect, normalize, map, validate and calculate financial data.                           |
| Operational admin | Django + Django Admin                        | Inspect jobs, mappings, companies, freshness, exceptions and controlled corrections.      |
| Shared platform   | Supabase Postgres, Auth and Storage          | Structured data, authentication and immutable raw objects.                                |
| Billing           | Stripe                                       | Annual subscription and entitlement events.                                               |
| Automation        | GitHub Actions plus scheduled worker runtime | Tests, deployment and batch schedules.                                                    |
| Observability     | structlog, Sentry, lightweight analytics     | Pipeline diagnostics, app errors, freshness and product usage.                            |

## Domains and routing

| **Domain**       | **Owns**                                                                                        | **Must not own**                                            |
|------------------|-------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| scrooner.com     | SEO pages, education, public company data, curated/public screens, product and pricing content. | Authenticated app workflows or heavy client-side screening. |
| app.scrooner.com | Interactive screener, prompt parsing UI, accounts, saved screens, entitlements and billing.     | Large programmatic SEO surface.                             |
| Internal admin   | Restricted operational interface.                                                               | Public product experience.                                  |

## Data flow

1.  SEC EDGAR exposes bulk archives, submissions, company facts, filing
    metadata/documents and daily indexes.

2.  Collector downloads exact source payloads, attaches
    provenance/checksums and writes immutable raw objects plus run
    metadata.

3.  Normalizer parses raw objects into consistent entities, periods,
    units and fact records without applying product metric meaning.

4.  Mapper resolves issuer-specific XBRL concepts into canonical
    Scrooner concepts and records mapping confidence/version.

5.  Metrics engine calculates versioned historical and derived measures
    such as growth, FCF, ROIC and dilution.

6.  Company Master connects CIK, ticker, exchange, identity changes and
    market-price inputs.

7.  Screener evaluates structured, deterministic predicates against
    analytics data.

8.  AI query layer translates user language into the supported query
    schema; validation rejects unknown metrics or ambiguous clauses.

9.  Astro and Next.js read approved serving views; user state and
    entitlements remain in the app schema.

## Data boundaries

| **Component**  | **Can do**                                                                   | **Cannot do**                                                                       |
|----------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Collector      | Fetch, retry, checkpoint, hash, store, dedupe and record provenance.         | Normalize, repair, infer periods, map concepts or calculate metrics.                |
| Normalizer     | Parse formats, standardize units/period structures and preserve lineage.     | Apply investment meaning or user-facing formulas.                                   |
| Mapper/Metrics | Map to canonical concepts, calculate versioned metrics and validate outputs. | Modify immutable raw evidence.                                                      |
| AI query layer | Interpret language into a supported schema and explain interpretation.       | Generate financial facts or bypass deterministic filters.                           |
| Web/app        | Present approved data and user workflows.                                    | Perform hidden one-off financial calculations inconsistent with metric definitions. |
| Admin          | Inspect, approve controlled mappings and rerun work.                         | Become a parallel source of untracked truth.                                        |

## Collector V1 technical design

| **Concern**       | **Choice**                                                                             |
|-------------------|----------------------------------------------------------------------------------------|
| Runtime           | Standalone Python 3.12 package/worker; no web framework.                               |
| HTTP              | httpx with explicit timeouts and connection management.                                |
| Validation/config | Pydantic.                                                                              |
| Retries           | Tenacity with bounded exponential backoff and jitter.                                  |
| Database access   | psycopg.                                                                               |
| CLI               | Typer.                                                                                 |
| Logging           | structlog with run/source/company identifiers.                                         |
| Raw storage       | Supabase Storage; exact source payload, append-only/immutable policy.                  |
| Metadata          | Postgres run, object, checksum, source, status and error records.                      |
| Bootstrap         | SEC bulk ZIP files including submissions.zip and companyfacts.zip.                     |
| Incremental       | SEC endpoints and daily indexes.                                                       |
| Fair access       | Declared User-Agent; aggregate internal limit ≤8 requests/second.                      |
| Reliability       | Idempotency keys, SHA-256, checkpoints, resume, dead-letter errors and reconciliation. |

## Logical database organization

| **Schema** | **Purpose**                                            | **Examples**                                                    |
|------------|--------------------------------------------------------|-----------------------------------------------------------------|
| raw        | Ingest metadata and references to immutable objects.   | source_object, ingest_run, fetch_attempt, checksum, dead_letter |
| core       | Normalized identities and facts.                       | company, listing, filing, fact, period, unit                    |
| analytics  | Canonical mappings, derived metrics and serving views. | concept_mapping, metric_definition, metric_value, screen_fact   |
| app        | Users and product state.                               | profile, saved_screen, query_run, entitlement, usage_event      |

## API strategy

Do not introduce FastAPI merely because the system has multiple parts.
Astro/Next.js may use direct server-side access to restricted database
functions/views and internal Next.js routes for app workflows. Introduce
a dedicated API only when consumers, security boundaries, scaling or a
B2B product make the contract valuable.

## Security and correctness controls

- Row-level security and least-privilege service roles for app/user data.

- Raw, core and analytics writes restricted to pipeline/admin identities.

- Secrets stored outside source control; separate local, staging and production environments.

- Version metric definitions and mapping changes so historical outputs are reproducible.

- Track data_as_of, source filing, calculation version and freshness on served metrics.

- Test ticker changes, amendments, duplicate facts, restatements, currency/unit differences and corporate actions.

- Do not promise real-time prices unless the source, licenses and refresh SLO support it.

- Money never touches `float`, end to end — parse with `Decimal` at the earliest ingestion point (not just at the database column), carry `Decimal` through every calculation, and serialize it as a string, not a JS number, at any API/frontend boundary. Found live (Normalizer Day 4): Python's default JSON float parsing already loses precision on monetary values before a `numeric` column type gets a chance to matter.

- A duplicate/conflict flag doesn't need a new table if it can be expressed as a queryable state on existing columns — e.g. `core.fact.is_authoritative`: a real conflict is just a duplicate group where no row is authoritative, no separate conflict table required. Prefer this over scaffolding new schema for every kind of ambiguity a phase discovers.

- Any per-company/per-concept batch job (Normalizer, Mapper, Company Master) loads its lookups into memory up front and batches its writes (`executemany`, not a query per item) — never one-or-more round trips per candidate row inside a loop. Found live (Normalizer Day 7): a stage that deviated from this shape hit real `SSL SYSCALL... Operation timed out` errors processing a large company (JPM, 3,704 groups) that the other five stages, all following this shape from the start, never hit.

- A formula that sums multiple inputs under one role (e.g. Mapper's `invested_capital_add`, fed by both `total_debt` and `stockholders_equity`) must verify **every** concept mapped to that role actually resolved, not just that the role has at least one value. Found live (Mapper Day 4): checking only "is the accumulated list non-empty" let a missing `total_debt` silently drop out of an AAPL ROIC calculation, computing 346% (a wrong number that looked valid) instead of correctly nulling the metric. This is a materially worse failure mode than a missing input producing `null` — a wrong-but-plausible number carries no signal anything is off. Any future formula engine (Mapper's Stage 3e TTM windows, Company Master's price-dependent metrics) needs an explicit per-role completeness check, not a truthiness check on the accumulated values.

- Idempotency checks must cover dead-tuple/bloat, not just row counts. Found live (Normalizer Days 4-5): a no-op rerun of an `ON CONFLICT DO UPDATE` or bulk `UPDATE` leaves the row count unchanged but still bloats the table via Postgres MVCC (58MB→77MB on one no-op rerun) until vacuumed — relevant to any repeated-upsert job on the 500MB Supabase free tier, not just the Normalizer.

## Deployment principle

Optimize for a solo bootstrapper: managed database/auth/storage,
static-first public delivery, a separate scheduled Python worker and
minimal always-on infrastructure. Scale components only after
measurements show a real constraint.
