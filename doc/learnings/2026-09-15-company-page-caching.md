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

## Third addendum, same day: "match the speed with screener speed" — applied to `apps/backend`'s saved-screens endpoints

Directly asked to apply the same treatment to the screens/screener surface. Audited it the same way: checked `app.saved_screen`/`app.user_screen_run`/`app.screen_result`/`app.screen_result_item` for missing indexes (all already correctly indexed — this schema got the same audit during the 2026-09-10/12 screener performance work, `EXPLAIN ANALYZE` on the real queries confirmed sub-millisecond execution, `user_id`/`slug`/`(company_id, position)` all covered) and checked `apps/backend/db_pool.py`'s connection pool (already `min_size=1`/`autocommit=True`, opened once at FastAPI startup — no cold-connect penalty, unlike `apps/app`'s own pool before this session's `idle_timeout` fix).

The real gap: `POST /v1/screen` and `/v1/screen-runs` already have thorough Redis caching (query results, run pointers, paginated pages, auth verification — all from the 2026-09-10/12 work), but `routers/saved_screens.py`'s `list_screens` (`GET /v1/screens`) and `get_screen` (`GET /v1/screens/{slug}`) had **none** — every call paid a real Postgres round trip even though the query itself is sub-millisecond, because the round trip (not execution) is the actual cost (same ~270ms/hop finding as the rest of this project's performance work).

Added to `apps/backend/cache.py`: a 30s-TTL cache for the saved_screen row itself (`company-page`-style key, `screens-list:{user_id}` / `screen-detail:{user_id}:{slug}`), same fail-open contract as every other cache in that file. Deliberately does **not** cache the run's own paginated result data — that already has its own separate, correctness-sensitive caching (`get_cached_run_page`, keyed by run_id) and mixing the two would risk serving a stale run pointer past its own TTL. Every write in the router (`create_screen`, `rename_screen`, `delete_screen`, `refresh_screen`) now explicitly invalidates the relevant cache entries — TTL alone is a memory-hygiene backstop here, not the correctness mechanism, matching this file's own stated philosophy for the `/v1/screen` cache.

One real wrinkle: `rename_screen`/`delete_screen` only ever took a numeric `screen_id`, not the row's `slug` — needed to invalidate the slug-keyed detail cache. Changed both `UPDATE`/`DELETE` statements' `RETURNING id` to `RETURNING slug` rather than adding a second lookup query.

7 new unit tests (`tests/test_saved_screens_cache.py`, monkeypatching the cache functions directly — this project's REDIS_URL is deliberately unreachable in tests, so a real Redis is never required to exercise this logic), full backend suite 41→48 passing. Verified live against the real database and a real local Redis (not mocked), using real saved-screen data:

| Endpoint | Cold (Redis miss) | Warm (Redis hit) |
|---|---|---|
| `GET /v1/screens` (list) | 297.7ms | **0.29ms** (1,027x) |
| `GET /v1/screens/{slug}` (detail + run page) | 1,760.6ms | **2.14ms** (823x) |

The `apps/app` frontend pages (`/app/screens`, `/app/screens/[slug]`) were deliberately left as `force-dynamic` with `cache: "no-store"` fetches — correct and unchanged, since this is per-user authenticated data that can never be shared across users the way the public company page can. The Redis cache added here lives entirely on the `apps/backend` side, the same place `/v1/screen`'s own cache already lives.

## Fourth addendum, same day: `loading.tsx` for the three coldest routes — perceived speed, not measured speed

Direct follow-up: "evaluate our pages... how can we make [them] so faster, that user start loving our product." All the fixes above reduce real latency on a cache MISS, but even the best remaining cache-miss number (a few hundred ms to a few seconds for a large company) rendered as **nothing on screen** before this — Next.js shows a blank tab until an async Server Component with no `loading.tsx` finishes. Checked directly: `app/stocks/[ticker]/` had no `loading.tsx` at all; `app/app/screens/` and `app/app/screens/[slug]/` only inherited the generic, page-shape-agnostic spinner at `app/app/loading.tsx` (four pulsing dots, shared by every `/app/*` route).

Added three route-level `loading.tsx` files, each shaped like the real page they precede (same principle `TableSkeleton` already established, doc/design/shadcn-system.md section 12: "don't show 'Loading...' — show a skeleton matching the exact layout"), reusing real, already-instant components (`PublicHeader`/`StockSectionNav`/`PageHeader` need no fetched data, so they render for real even in the loading state) and the existing `.ds-skeleton` shimmer utility:

- `app/stocks/[ticker]/loading.tsx` — hero + snapshot metrics grid + chart/quarterly-results placeholders. Needed a new small shared module, `components/company/stockPageSections.ts`, because Next's typed-routes checker rejects a `page.tsx` exporting anything beyond its own known special names (a real `tsc` error found live: "Property 'sections' is incompatible with index signature") — the nav section list moved there so both files import the same static list instead of duplicating it.
- `app/app/screens/loading.tsx` — reuses `SavedScreensClient`'s own CSS module classes for a 3-card skeleton list.
- `app/app/screens/[slug]/loading.tsx` — reuses `TableSkeleton` directly (its `.results-table` classes are the exact ones `SavedScreenDetailClient` already renders into).

Verified live via two methods (real HTTP screenshots need an actual multi-second wait to land on the loading frame, so a throwaway `await new Promise(r => setTimeout(r, 4000))` was added to `getCompanyPageDataCached` only for this test, reverted immediately after; the two authenticated `/app/screens*` skeletons were verified by rendering the loading components directly through a temporary unauthenticated preview route, since a real login couldn't be scripted in this environment — see below): all three render correctly, shaped closely enough to the real content that the swap causes no visible layout jump. One real tooling gotcha hit along the way: a first attempt at a preview route under `app/_preview/` 404'd, because Next.js's App Router treats any `_`-prefixed folder as private and excludes it from routing entirely — moved to `app/preview-check/` (no underscore) to actually resolve, then deleted once screenshots were captured.

This is a genuinely different lever from everything else in this file: it doesn't reduce a single millisecond of backend/database time, it changes what the user sees *during* the wait that's still there — from a blank tab to an instantly-rendered, content-shaped page. Framed against Screener.in as this project's own stated feel benchmark (doc 05), this is exactly the category of thing that benchmark is about.

## Secondary fix: pool idle_timeout

`lib/company/db.ts`'s `postgres()` pool had `idle_timeout: 20` — meaning a connection closes after 20s of no queries, so a cache-miss regeneration (now much rarer, but still real) could pay the full reconnect cost even between two regenerations minutes apart during low traffic. Raised to `90`. Still one connection well within Supabase's shared ~15-connection pooler ceiling (root `CLAUDE.md`); `max: 2` left unchanged.

## Verification

- Production build clean (`next build --webpack`), 87/87 frontend tests passing, `tsc --noEmit` clean, `eslint` clean on both changed files.
- Live timing table above, captured against the real Supabase project, not a local/mocked database.

## Generalizable lesson

**A `revalidate` route-segment export is a no-op for any data source that isn't `fetch()`-based.** Any other Next.js page in this repo that reads Postgres directly (the `apps/app/lib/*/db.ts` pattern) and wants caching needs `unstable_cache` (or, longer-term, Cache Components' `"use cache"` directive, which Next 16's own docs say supersedes `unstable_cache` — not adopted here since it's a bigger, repo-wide model switch, out of scope for a single-page fix) — setting `revalidate` alone will silently do nothing and is easy to mistake for "already handled."
