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

## Why 900s, why not Redis

`revalidate: 900` (15 min) was chosen, not the 3600s other `apps/app` API routes use, to keep worst-case staleness in the same order of magnitude as Alpaca's own ~15-minute delayed price feed (doc 25) — the page was never going to be fresher than that anyway.

Did **not** reach for Redis here the way `apps/backend`/ADR 0001 did. `unstable_cache` is Next's own built-in mechanism, requires zero new infrastructure, and is the documented tool for exactly this shape of problem (cache a non-fetch async function, keyed on its arguments). Redis was justified for the Screener because the input space (arbitrary query strings/trees) isn't enumerable ahead of time and the backend already needed Redis for other reasons (auth-verification cache, dataset-versioned invalidation). The company page's key space is a bounded set of ticker routes — `unstable_cache` fits without reopening doc 02's Redis question a second time for a case that doesn't need it.

## Secondary fix: pool idle_timeout

`lib/company/db.ts`'s `postgres()` pool had `idle_timeout: 20` — meaning a connection closes after 20s of no queries, so a cache-miss regeneration (now much rarer, but still real) could pay the full reconnect cost even between two regenerations minutes apart during low traffic. Raised to `90`. Still one connection well within Supabase's shared ~15-connection pooler ceiling (root `CLAUDE.md`); `max: 2` left unchanged.

## Verification

- Production build clean (`next build --webpack`), 87/87 frontend tests passing, `tsc --noEmit` clean, `eslint` clean on both changed files.
- Live timing table above, captured against the real Supabase project, not a local/mocked database.

## Generalizable lesson

**A `revalidate` route-segment export is a no-op for any data source that isn't `fetch()`-based.** Any other Next.js page in this repo that reads Postgres directly (the `apps/app/lib/*/db.ts` pattern) and wants caching needs `unstable_cache` (or, longer-term, Cache Components' `"use cache"` directive, which Next 16's own docs say supersedes `unstable_cache` — not adopted here since it's a bigger, repo-wide model switch, out of scope for a single-page fix) — setting `revalidate` alone will silently do nothing and is easy to mistake for "already handled."
