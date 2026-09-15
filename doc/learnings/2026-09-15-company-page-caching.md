# Company page caching — 2026-09-15

Prompted directly: "like you had make create screen faster ... make company page load faster." The screener/backend work (2026-09-10 through 2026-09-12) had already established the pattern — measure live before guessing, then cache the expensive thing — for `apps/backend`. The company page (`apps/app/app/stocks/[ticker]/page.tsx`) had never gotten the same treatment.

## Measured, not assumed

`lib/company/db.ts`'s `getCompanyPageData` is already a single consolidated CTE query (doc 17's "one round trip" contract, `X-Scrooner-DB-Queries: 1` discipline) — so the obvious first guess, "it's issuing too many queries," was wrong before it was even written down. Extracted the real query (substituting a literal ticker for the JS template placeholders) and ran it directly against the live Supabase project via `psql`:

- `EXPLAIN (ANALYZE, BUFFERS)`: **207ms** server-side execution, 13ms planning, every buffer a `shared hit` (nothing read from disk) — the query itself is fine, well-indexed, nothing to optimize there.
- `\timing` on a warm connection: **1.3–1.6s** per request.
- `\timing` on a fresh connection (first `psql` invocation): **7.4–10.4s**.

The gap between 207ms of real work and 1.5–7s+ of wall time is almost entirely this dev machine's network round trip to Supabase (`us-east-1`) plus, on a cold connection, a full TCP+TLS+auth handshake — the exact class of latency [ADR 0001](../adr/0001-screener-redis-cache-and-boolean-logic.md) already measured and fixed for `/v1/screen` (`~270ms`/round-trip, `~1.7s` for a fresh `psycopg.connect()`). The page was paying that cost on **every single request, for every ticker**, because `export const dynamic = "force-dynamic"` disabled all caching outright.

## The fix, and a real dead end along the way

Removing `force-dynamic` and adding `export const revalidate = 900` (Next.js's standard route-segment ISR config) had **zero effect** — confirmed live via `next build && next start` plus repeated `curl` timings, every request still cost ~1.3–1.8s, no `x-nextjs-cache` header ever appeared. Root cause, found by reading `node_modules/next/dist/docs/` per this repo's own `apps/app/AGENTS.md` warning ("this is NOT the Next.js you know" — Next 16 shipped with this repo really did change caching semantics): the `revalidate` route config only governs `fetch()`-based caching signals. `lib/company/db.ts` uses the `postgres` npm package directly, never `fetch`, so Next has no caching signal to act on at all — the route falls back to dynamic rendering regardless of the `revalidate` export.

The documented fix for exactly this case (`unstable_cache` — "for non-fetch functions... database queries and other async functions that don't use fetch") is what actually works. Wrapped `getCompanyPageData` in `unstable_cache(getCompanyPageData, ["company-page-data"], { revalidate: 900, tags: ["company-page"] })`, still composed with the existing React `cache()` (which only dedupes the `generateMetadata` vs. page-render call *within* one request — a different, complementary mechanism, kept as-is).

Verified live, real production build (`next build --webpack && next start`):

| Request | Before (force-dynamic) | After (unstable_cache) |
|---|---|---|
| AAPL, 1st hit (cold) | ~1.3–1.8s every time | 4.9s (pays the real query once) |
| AAPL, 2nd+ hit | ~1.3–1.8s every time | **0.02–0.05s** |
| MSFT, 1st hit (different ticker, cold) | ~1.3–1.8s | 6.5s |
| MSFT, 2nd+ hit | ~1.3–1.8s | **0.03s** |

Confirmed the cache is genuinely per-ticker (not a single shared/incorrect entry) by diffing real rendered content — AAPL and MSFT pages differ, each served from its own cached entry.

## Why 900s

15 min was chosen, not the 3600s other `apps/app` API routes use, to keep worst-case staleness in the same order of magnitude as Alpaca's own ~15-minute delayed price feed (doc 25) — the page was never going to be fresher than that anyway.

## Addendum, same day: `unstable_cache` replaced with Redis

Initially deliberately avoided Redis here — `unstable_cache` needed zero new infrastructure and is Next's documented tool for exactly this shape of problem. Directly asked afterward ("why we need to run query everytime, when opening company?"), which prompted re-checking that reasoning: `unstable_cache`'s default cache handler (no `incrementalCacheHandlerPath`/`cacheHandlers` configured in `next.config.ts`) is **per server process, not shared**. That's invisible on a single dev server (which is all that had been tested) but means under any real horizontally-scaled deployment, every Next.js instance independently pays the full ~1.5-7s query cost on its own first hit for every ticker — the win only fully materializes with exactly one running instance.

Replaced with `lib/company/cache.ts`, a Redis-backed cache with the same fail-open contract as `apps/backend/cache.py` (get/set wrapped in try/catch, any Redis failure falls straight through to Postgres, never blocks the page). Justified reopening the Redis question a second time because Redis is already a real, accepted production dependency of this monorepo for exactly this problem (ADR 0001) — this isn't a new category of infrastructure, just a second, separately-keyed (`company-page:*` vs. the backend's `screen:*`/`auth-user:*`) use of the same instance.

Verified live, three scenarios via real `next build && next start`:

| Scenario | Result |
|---|---|
| Cold ticker, first hit | ~10s (unchanged — real query + Redis write) |
| Same process, repeat hit | ~0.04s |
| **Brand-new process** (killed and restarted on a different port), ticker another process already cached | **~0.27s** (Redis hit from a fresh process — proves cross-instance sharing) |
| Fresh process, steady state | ~0.04s |
| Fresh process, different (uncached) ticker | ~9.7s (correctly still a real miss — proves per-ticker correctness, not a blanket cache) |

The ~0.27s "fresh process, first request" number (vs. ~0.04s in steady state) is Node/Next cold-start overhead, not cache overhead — expected and irrelevant to the point being tested (cross-instance sharing).

## Second addendum, same day: real DB design flaws, found by asking "why is a cache MISS still slow"

Directly asked to check the DB design for flaws, since caching only masks a slow query — it doesn't explain why the underlying query was slow in the first place. All three CTE flaws below were found by `EXPLAIN (ANALYZE, BUFFERS)` on companies deliberately chosen to NOT be cache-warm (a random obscure ticker, then a large popular one after the shared-buffer cache had been evicted by other testing) — the earlier 207ms server-side number for AAPL turned out to be an artifact of the buffer cache staying warm across many repeated manual test runs, not representative of a real cold hit. Migration `pipeline/db/migrations/0066_company_page_hot_path_indexes.sql`.

1. **`core.listing` had no index usable for a ticker lookup.** Only `UNIQUE(company_id, ticker)` existed — useless when ticker is the known value. Every `lower(l.ticker) = lower($1)` query (the company page, plus ticker search/autocomplete) did a full `Seq Scan` of the whole table (confirmed: `Rows Removed by Filter: 6993`). Fixed with `idx_listing_lower_ticker on core.listing (lower(ticker))`.
2. **`core.company` had no index on `y_industry`**, the peer-comparison join key (doc 28's yfinance-industry peer matching). Every single stock page load did a full `Seq Scan` of the active company population just to find industry peers. Fixed with a partial index, `idx_company_y_industry_active on core.company (y_industry) where status = 'active'` (matches the query's own `status = 'active'` filter exactly).
3. **The real, serious one: `core.institutional_ownership`'s per-company "dedupe by filer, then top-15-by-shares" subquery had no covering index.** Confirmed on AAPL, not a small ticker: the existing `idx_institutional_ownership_company_source (company_id, source_zip)` index doesn't cover `filer_name`/`is_amendment`/`filing_date` (the dedup subquery's own `ORDER BY`), so Postgres had to heap-fetch all 18,962 of AAPL's institutional-ownership rows individually — measured at **8,205ms** for that one node alone (~0.43ms/row, consistent with random I/O against a 1.8GB table, not a planner mistake). A large, heavily-held company has orders of magnitude more rows here than a small one, so this was invisible in every earlier test that only used small tickers. Fixed with a covering index matching the subquery's exact sort order, `idx_institutional_ownership_dedup (company_id, filer_name, is_amendment desc, filing_date desc nulls last) include (shares, value_usd)` — turns the node into a single Index Only Scan, no heap access, no separate Sort.

Verified live, before/after, `EXPLAIN (ANALYZE, BUFFERS)`:

| Ticker | Before | After |
|---|---|---|
| VITL (small, cold) | 861ms execution, 114ms planning | 82ms execution, 20ms planning |
| AAPL (large, cold) | 8,767ms (the institutional_ownership node alone: 8,205ms) | 140-187ms |
| MSFT (large, cold) | not measured before the fix | 600ms warm / ~2.4s genuinely cold (a real, expected buffer-cache-cold cost, not a flaw — MSFT's own data volume) |

All three indexes are `create index if not exists` (idempotent) plus one `include`, applied directly against the live database and confirmed via a second run producing `NOTICE: ... already exists, skipping`. No application code changed — this was purely a schema-level fix, orthogonal to the Redis caching work above (a cache MISS is now itself fast, not just cache hits).

## Secondary fix: pool idle_timeout

`lib/company/db.ts`'s `postgres()` pool had `idle_timeout: 20` — meaning a connection closes after 20s of no queries, so a cache-miss regeneration (now much rarer, but still real) could pay the full reconnect cost even between two regenerations minutes apart during low traffic. Raised to `90`. Still one connection well within Supabase's shared ~15-connection pooler ceiling (root `CLAUDE.md`); `max: 2` left unchanged.

## Verification

- Production build clean (`next build --webpack`), 87/87 frontend tests passing, `tsc --noEmit` clean, `eslint` clean on both changed files.
- Live timing table above, captured against the real Supabase project, not a local/mocked database.

## Generalizable lesson

**A `revalidate` route-segment export is a no-op for any data source that isn't `fetch()`-based.** Any other Next.js page in this repo that reads Postgres directly (the `apps/app/lib/*/db.ts` pattern) and wants caching needs `unstable_cache` (or, longer-term, Cache Components' `"use cache"` directive, which Next 16's own docs say supersedes `unstable_cache` — not adopted here since it's a bigger, repo-wide model switch, out of scope for a single-page fix) — setting `revalidate` alone will silently do nothing and is easy to mistake for "already handled."
