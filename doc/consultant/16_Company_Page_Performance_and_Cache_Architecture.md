# 16 — Company-page performance and cache architecture

> **Status:** P0 implemented and locally verified; production deployment/cache-hit verification pending  
> **Date:** 2026-08-22  
> **Scope:** Public Astro `/stock/{ticker}/` pages, Supabase Postgres, and the
> future production CDN/runtime boundary

## Executive answer

Opening a company page does **not** calculate every metric again. Mapper jobs
calculate metrics before the request and persist them in
`analytics.metric_value`. The page reads those stored values and performs only
small presentation work, including three 3-year averages for the deterministic
Pros/Cons checklist.

Before remediation, every uncached request server-rendered the full page and
performed **16 remote SQL round trips**:

1. one ticker-to-company lookup;
2. twelve independent company-data reads scheduled together; and
3. three metric-history reads for the checklist.

The Astro Postgres client allows four connections, so the twelve parallel reads
execute in roughly three network waves, followed by another checklist wave.
There was no page, route, or HTTP cache configured.

## Implementation update — 2026-08-22

The immediate serving-path remediation is now implemented:

- `getCompanyPageData()` returns identity, metrics, the four rendered statement
  views, filings, ownership, price, public float, book value, and checklist
  history in **one parameterized SQL request**;
- the checklist now consumes history from that response and performs no
  follow-up reads;
- the connection pool is reduced from four sessions to two and prepared
  statements are disabled so the same client is compatible with Supabase's
  transaction pooler for Vercel;
- Astro now uses its official Vercel adapter and Vercel CDN cache provider;
- successful company pages are fresh for 15 minutes and stale-while-revalidate
  for 24 hours, with a ticker-specific cache tag;
- Vercel compute is pinned to `iad1`, colocated with the `us-east-1` Supabase
  project; and
- origin renders expose `Server-Timing` plus `X-Scrooner-DB-Queries: 1`.

The production build contains the `Vercel-CDN-Cache-Control` provider and the
900/86,400-second route directives. Cache hits cannot be measured until this
change is deployed to the Vercel project.

## Measured evidence before remediation

Local requests to the real Supabase-backed development page:

| Request | TTFB | Total |
|---|---:|---:|
| AAPL, cold | 6.649s | 6.658s |
| AAPL, warm | 2.318s | 2.320s |
| MSFT, warm | 1.933s | 1.934s |

The response had no `Cache-Control`, CDN cache, or Astro cache headers.

The configured database endpoint is Supabase's shared **session pooler** on
port 5432 in `us-east-1`. Establishing the first measured connection from the
local environment took about **2.2 seconds**.

By contrast, `EXPLAIN (ANALYZE, BUFFERS)` showed fast database execution:

| Read | Postgres execution time |
|---|---:|
| Company identity | 0.306ms |
| Latest 50 metrics | 6.256ms |
| Annual income statement | 2.897ms |
| Recent filings | 0.866ms |
| One 3-year metric history | 0.168ms |
| Institutional-holder deduplication | 23.740ms |

The tables are modest: about 23k metric values, 31k canonical facts, 80k
filings, 55k insider transactions, and 58k institutional holdings. Expected
company-filter indexes are deployed, including migration 0020's filing and
metric-definition indexes.

**Conclusion:** Postgres computation is not the dominant latency. Remote
connection setup, repeated network waves, uncached SSR, and region placement
are the dominant constraints. Adding compute capacity or recalculating fewer
metrics will not solve the observed page speed.

## Measured evidence after remediation

The consolidated page returned complete AAPL and MSFT HTML with HTTP 200 and
the one-query diagnostic header. From the local India development environment
to Supabase `us-east-1`:

| Request | TTFB | Database/connection timing |
|---|---:|---:|
| AAPL, cold connection | 3.03s | 2.73s |
| AAPL, reused connection | 0.58s | 0.57s |
| MSFT, reused connection | 0.64s | 0.62s |

The AAPL cold result improved from 6.65s to 3.03s, and its reused-connection
result improved from 2.32s to 0.58s. These are origin-development results, not
CDN-hit results. Production repeat requests should not invoke Astro or
Postgres; that claim remains a deployment acceptance check rather than a
locally asserted result.

## Target architecture

```text
Pipeline success
    │
    ├─ computes canonical metrics once
    ├─ writes core/analytics truth tables
    ├─ rebuilds one company-page serving snapshot
    └─ invalidates stock:{ticker} cache tag/path
                    │
Visitor → CDN/ISR cache ── HIT → HTML near user
                    │ MISS/STALE refresh
                    ▼
          Astro origin near Supabase
                    │ one pooled query
                    ▼
       serving.company_page_snapshot
```

The canonical normalized facts and metric values remain the source of truth.
The snapshot is a disposable read model, not another calculation authority.

## Recommended sequence

### P0 — Cache the public HTML

Company pages are public and identical for every visitor. Configure Astro route
caching or the production CDN/ISR adapter for `/stock/*`.

Recommended starting policy:

- fresh at the CDN for 5–15 minutes;
- stale-while-revalidate for up to 24 hours;
- no browser-private or user-specific data in the cached response;
- show `data_as_of`/price timestamp so freshness is explicit; and
- invalidate the exact company path/tag after a successful pipeline update.

The full-page TTL should initially respect the delayed price feed. If price is
later isolated into a small independently refreshed component, fundamentals can
be cached for hours while price refreshes every few minutes.

Astro 7 supports route caching with `maxAge`, `swr`, tags, and path
invalidation. Its cache is intentionally disabled during development, so local
development timing must not be mistaken for production cache-hit timing. If
Vercel remains the frontend host, its Astro adapter can map cache directives to
the Vercel CDN and support tag/path revalidation.

### P0 — Reduce 16 SQL calls to one serving read — implemented

Create an internal serving model such as:

```text
serving.company_page_snapshot
  company_id       primary key
  ticker           lookup identity
  payload          versioned JSON document
  data_as_of       newest included source timestamp
  snapshot_version schema/contract version
  generated_at     snapshot build timestamp
```

Build or replace the row only after a company's pipeline transaction succeeds.
The page then performs one indexed lookup and renders the returned payload.
Canonical values, Decimal strings, null reasons, periods, formula versions, and
source identifiers remain in the payload; no number is recomputed in Astro.

The implemented first step is one parameterized query that returns all page
sections as nested JSON. It removes network round trips without persisting a
snapshot, but it still executes the joins on every cache miss. Add the
persisted snapshot only if deployed cache-miss p95 remains above the target;
the CDN must be measured first so a new write model is justified by evidence.

Do not use a whole-universe materialized-view refresh on every filing. A
per-company snapshot table allows atomic, incremental rebuilds and targeted
cache invalidation.

### P0 — Align region and connection mode

- Place the Astro production function in the same geographic region as the
  `us-east-1` Supabase project.
- For a long-lived Node container, a direct or session-pooled connection with a
  small application pool is suitable.
- For Vercel/serverless instances, use a transaction pooler. Supabase Pro also
  offers a co-located dedicated pooler with lower latency. Transaction mode
  requires prepared statements to be disabled in the Postgres client.
- After the page becomes one query, use one or two application connections per
  serverless instance rather than four. Four multiplied by many instances can
  exhaust database capacity even when each instance looks conservative.

Do not switch connection strings blindly: choose the mode together with the
final hosting runtime and verify it under concurrent load.

### P1 — Add only evidence-supported indexes

Indexes are secondary here because the measured SQL is already fast. After the
read path is consolidated, test these candidates with real `EXPLAIN` plans:

- current ticker lookup: partial expression index on `lower(ticker)` for active
  listings;
- latest metrics: company + metric definition + TTM preference + period end,
  with selected values included;
- recent filings: partial composite index on
  `(company_id, filing_date desc)` where the date is not null; and
- institutional deduplication: company + filer + amendment/date ordering, or
  preferably persist the latest deduplicated holder set in the snapshot.

Remove any candidate whose measured plan does not improve. Current server-side
execution is tens of milliseconds, so indexes alone cannot recover the two to
six seconds lost outside Postgres.

### P1 — Instrument every layer

Add `Server-Timing` or structured timings for:

- cache status (`HIT`, `MISS`, `STALE`);
- connection acquisition;
- snapshot query;
- Astro rendering; and
- total origin response.

Use Supabase Observability/`pg_stat_statements` for mean time and call count,
and Vercel/Astro cache headers for cache-hit evidence. Performance work should
be judged on p50/p95, not one local request.

## Redis decision

Do **not** add Redis yet.

CDN/ISR caches the most valuable artifact—the complete public HTML—near the
visitor and prevents the origin and database from running at all. A serving
snapshot makes cache misses cheap. Redis would introduce another bill, network
hop, serialization format, invalidation mechanism, and failure mode before a
remaining problem has been measured.

Add Redis only if production evidence later shows one of these:

- low CDN hit rate because many responses are personalized;
- expensive shared data needed across several dynamic endpoints;
- repeated origin reads that cannot be cached as full responses; or
- a required cross-instance runtime cache not supplied by the host.

## Acceptance targets

| Measure | Target |
|---|---:|
| Public company-page CDN hit ratio | ≥95% after warm-up |
| Cache-hit TTFB | <200ms p95 in primary audience regions |
| Cache-miss SQL calls | 1, maximum 2 |
| Cache-miss database execution | <50ms p95 |
| Cache-miss origin TTFB | <500ms p95 when region-co-located |
| User-visible stale data | bounded and labeled by `data_as_of` |
| Cache invalidation | exact company path/tag after successful update |

## What not to do

- Do not calculate metrics during a page request.
- Do not refresh a materialized view from a visitor request.
- Do not increase the Postgres connection limit to hide round-trip latency.
- Do not cache personalized/authenticated HTML under a public key.
- Do not use Redis as the first cache layer for public SEO pages.
- Do not invalidate the whole company universe when only one company changes.

## Implementation decision needed

Before implementation, lock the Astro production runtime/adapter and region.
The architecture is stable across hosts, but the exact cache provider,
invalidation API, and pooler mode depend on whether Astro runs as Vercel
serverless, a long-lived Node container, or another CDN-backed runtime.
