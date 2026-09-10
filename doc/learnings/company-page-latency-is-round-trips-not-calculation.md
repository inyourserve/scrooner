# Company-page latency is round trips, not metric calculation

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

**Problem or clarification**

The company page felt slow enough to suggest that every metric might be
recalculated on each visit.

**How it was found**

The Astro route and database module were traced end to end, then the real page
was timed and its SQL inspected with `EXPLAIN (ANALYZE, BUFFERS)`. The route
reads precomputed `analytics.metric_value` rows. It sends 16 SQL requests per
uncached page, while the client permits four simultaneous connections. Local
TTFB was 1.9–6.7 seconds. The first remote pooled connection took about 2.2
seconds, but the main metric query executed inside Postgres in about 6ms and
the slowest inspected query in about 24ms. The response had no cache header.

A broader localhost pass on 2026-08-28 showed the same pattern outside Astro.
The company page was 4.53s cold and 0.67–0.94s warm, while `/api/metrics`
remained 2.56–2.69s warm even though FastAPI `/health` was about 2ms. A fresh
Postgres connection took 1.70–1.85s and a subsequent `select 1` another
0.53–0.58s. `pg_stat_statements`, by contrast, put the consolidated company
query at about 138ms mean across 47 calls. FastAPI was found to use a fresh
`psycopg.connect()` per operation, and some requests opened another connection
for usage logging.

**Fix / decision**

The Astro page now makes one parameterized `getCompanyPageData()` request for
every section, and the deterministic checklist consumes history included in
that response rather than opening three more connections. The site now builds
with Astro's official Vercel adapter and CDN cache provider: company pages are
fresh for 15 minutes, stale-while-revalidate for 24 hours, and tagged per
ticker. Vercel compute is pinned to `iad1`; the Postgres pool is two clients
with prepared statements disabled for transaction-pooler compatibility.
Origin responses expose database duration and the one-query count.

The next serving-path decision is to put the consolidated company read behind
one versioned backend endpoint and give FastAPI a bounded, lifecycle-managed
connection pool. This API remains one complete read model; splitting the page
into section endpoints would recreate the round-trip problem. Stable metadata
such as the metric catalog should be cached in process. Public Astro HTML
remains CDN-cached ahead of the API.

The complete page was verified against live Supabase data. AAPL improved from
6.65s cold / 2.32s warm to 3.03s cold / 0.58s with a reused connection. The
production build emits the Vercel cache provider and route directives, but CDN
hit latency still requires verification after deployment. A persisted serving
snapshot is deliberately conditional on that deployed miss evidence.

Redis remains conditional, not prohibited. Add a region-local shared
cache-aside layer when measurements show repeated company, catalog, search, or
identical short-lived screener reads across multiple API instances after
connection pooling. Do not add it merely to hide unpooled connections, and do
not cache auth decisions. Use TTL plus versioned keys and targeted pipeline
invalidation so cached data cannot become a second source of truth.

**Why it matters going forward**

Parallel queries are not equivalent to one query when the database is remote
and the client pool is smaller than the fan-out. Full-response CDN caching is
the first cache for identical public HTML; consolidating the origin read is the
second protection for misses. Measure database execution, connection
acquisition, rendering, and cache behavior separately. Do not add Redis,
database compute, or speculative indexes as the first response to latency
outside Postgres. Pool connections first, cache the largest public artifact at
the CDN, preserve one coarse-grained company read, and introduce shared caching
only when cross-instance reuse is measured.
