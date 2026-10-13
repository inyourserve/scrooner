# 54. Site-Wide Caching Scope

**Status:** Built (2026-10-13) — Option A (centralize in `apps/backend`) implemented, by explicit founder direction ("decide everything by[your]self") after this doc's own recommendation. See `doc/learnings/2026-10-13-sitewide-caching-built.md` for what shipped and how it was verified. Originally drafted 2026-10-09 as scoping only; renumbered from 52 to 54 on 2026-10-13 to resolve a real doc-number collision with `doc/planning/52_Scrooner_Coverage_and_Ticket_Backlog_Replan_2026-10-11.md`, written by a concurrent session in the same shared tree. Prompted directly by the founder: "note down a learning and scoping document, we will create caching system for the entire site," following the same day's broader "my real goal is make the query super faster" direction (see `doc/learnings/2026-10-09-supabase-usage-audit.md` for the infra audit that preceded this).

**Owner:** Founder/Product. **Review:** when the next force-dynamic/zero-cache page is found, same discipline as this doc's own build method.

## Why this doc exists

Caching on this site grew the same way most of this project's features have — one page at a time, verified live, shipped. That discipline (`doc/learnings/2026-09-15-company-page-caching.md`, `2026-09-10-screener-performance.md`, `2026-09-12-screens-infra-world-class-sanity-check.md`) produced three genuinely different caching mechanisms, each correct in isolation, with no single page telling you which one a *new* page should use. Before building a unified system, this doc inventories exactly what exists today, against real code, and names the gaps precisely rather than from memory.

Every claim below is a file:line reference checked in this session on 2026-10-09, not recalled from an earlier summary.

## Current state: what IS cached

### `apps/backend/cache.py` — Redis, fail-open, the project's primary cache

| Key prefix | TTL | What | Invalidation |
|---|---|---|---|
| `screen:*` | 7 days | `/v1/screen` results, keyed by query hash + dataset_version | Never explicitly invalidated — keyed by `dataset_version`, so a snapshot rebuild naturally produces new keys ([`analytics.company_screening_snapshot`](../../pipeline/CLAUDE.md), migration 0074) |
| `screen-run:*` / `screen-run-page:*` | 7 days | Saved/shared screen-run pointers and paginated result pages | Same dataset_version keying |
| `auth-user:*` | 30s | Supabase `GET /auth/v1/user` result, keyed by token hash | TTL only (deliberate: short enough that a revoked token's exposure window is bounded, per `doc/learnings/2026-09-12-screens-infra-world-class-sanity-check.md`) |
| `screens-list:{user_id}` / `screen-detail:{user_id}:{slug}` | 30s | Saved-screen metadata (not run results) | Explicit invalidation on every write (`create_screen`/`rename_screen`/`delete_screen`/`refresh_screen`) + TTL backstop |
| `company-page:{ticker}` | 15 min | The whole company page JSON (`apps/backend/company_page.py`) | TTL only; `CACHE_MISS` sentinel also caches a confirmed-404 ticker |

All five are read through the exact same fail-open contract: every Redis call wrapped in try/except `RedisError`, returning `None`/no-op on failure. A Redis outage degrades every one of these paths to "slower," never "broken." This convention is the right foundation to keep, not replace.

### `apps/app` — three *different*, inconsistent mechanisms, none of them this Redis contract

1. **`app/api/company-search/route.ts`** — `searchCompanyDirectory(query, 8)` ([`lib/company/db.ts:638`](../../apps/app/lib/company/db.ts)), returned with an HTTP `Cache-Control: public, max-age=60, stale-while-revalidate=300` header. This is CDN/browser-level caching, not server-side — correct for a per-keystroke autocomplete endpoint (cheap to recompute, fine to let a CDN edge cache it), but it means every cache miss still pays a cold Postgres round trip, and nothing shares that result across edge nodes on a given deploy.
2. **`app/api/company-search/directory/route.ts`** — `loadFullCompanyDirectory()` ([`lib/company/db.ts:684`](../../apps/app/lib/company/db.ts)) wrapped in `unstable_cache(..., { revalidate: ... })`. **This is the same per-process-only mechanism already proven insufficient and replaced once** — the company page used `unstable_cache` for exactly one day (2026-09-15) before being swapped for Redis, because `unstable_cache`'s default handler doesn't share across server instances: a horizontally-scaled deployment would have every instance independently pay the full directory-load cost on its own first hit. That lesson was never applied back to this endpoint. It still works correctly on a single dev server, which is why it hasn't surfaced as a live bug — but it has the identical latent gap the company page already had, documented, and fixed elsewhere.
3. **Nothing** — the homepage and every browse/category page (next section).

There is no `apps/app`-side Redis client at all right now — `lib/company/cache.ts` was deleted on 2026-10-03 when the company page moved to calling `apps/backend` instead of Postgres directly (`doc/learnings/2026-10-03-company-page-api-port.md`). Any future `apps/app`-side Redis caching needs that module rebuilt from scratch, or (see Decision point below) the work should go through `apps/backend` instead so a second Redis client never needs to exist.

## Current state: what is NOT cached at all

Confirmed live via `export const dynamic`/`export const revalidate` in each file — `force-dynamic` disables all of Next.js's own caching, full stop:

| Page | `db.ts` function(s) called | Dynamic export |
|---|---|---|
| `app/page.tsx` (homepage) | `getCompaniesByTickers` (11 hardcoded tickers) | `force-dynamic` |
| `app/stocks/page.tsx` | `loadFullCompanyDirectory` | `force-dynamic` |
| `app/stocks/sector/page.tsx` | `getSectorList` | `force-dynamic` |
| `app/stocks/industry/page.tsx` | `getIndustryList` | `force-dynamic` |
| `app/explore/page.tsx` | `getSectorList`, `getIndustryList` | `force-dynamic` |
| `app/sitemap.ts` | (directory/sector/industry lists) | `force-dynamic` **and** a `{ revalidate: 3600 }` object present in the same file — the two are contradictory; `force-dynamic` wins, so the `revalidate` value is currently dead config, not a working 1-hour cache |

Not yet confirmed (lower priority — these are per-slug company listing pages, same shape as the two above but parameterized): `app/stocks/sector/[slug]/page.tsx` (`getCompaniesBySectorSlug`, `lib/company/db.ts:802`) and `app/stocks/industry/[slug]/page.tsx` (`getCompaniesByIndustrySlug`, `lib/company/db.ts:819`) had no `dynamic`/`revalidate` export found by direct grep — in Next.js App Router that means the *default* (static/cached-at-build, revalidated only by an explicit mechanism) rather than `force-dynamic`. Worth a direct confirmation before implementation, since "no export found" can also mean the check missed a differently-named config; not loosely assumed here.

**Every one of these pages pays a full, uncached Postgres round trip on every single visit, for every visitor, forever.** This is the exact pattern already measured and fixed once for the company page: cache-miss cost there was 1.3–9.7s (cold connection + query), cache-hit was 0.02–0.05s (`doc/learnings/2026-09-15-company-page-caching.md`). The homepage and the four browse pages above are the same shape of problem, unfixed, on pages that — unlike the company page — have *no per-entity variation to justify freshness*: the sector list, the industry list, and the full company directory change only when the data pipeline reclassifies something, not per request.

One more finding, minor: `getExampleScreenResults` (`lib/company/db.ts:843`) has no caller anywhere in `app/` or `lib/` — it appears to be dead code from an earlier design. Not a caching gap; flagged for cleanup, not addressed here.

## Why this matters for "make the query super faster"

The founder's stated goal this session was raw speed, and the dominant unresolved lever remains same-region hosting for `apps/backend` (no deploy manifest exists yet — a real, separate, not-yet-made decision, not revisited in this doc). But of the levers that don't require a hosting decision, the force-dynamic pages above are the single most concrete, already-proven-effective fix available: they are the *least* personalized, *most* repeat-traffic pages on the whole site (homepage, sector list, industry list, full directory) and currently get zero benefit from any caching layer that exists. Fixing these requires no architecture change — just applying the pattern already proven on the company page.

## The real problem: three mechanisms, no rule for which to use

This is the actual thing worth fixing before writing more caching code, not just the five uncached pages:

- **Redis via `apps/backend`** — shared across instances, fail-open, used for company page + screener + saved screens.
- **`unstable_cache`** — per-process only, used for the directory endpoint, known-insufficient (already proven and fixed once elsewhere), left in place anyway.
- **HTTP `Cache-Control` header** — CDN/browser-level, used for search-as-you-type, correct for its one use case but structurally unlike the other two (it caches the *response*, not server-side work, so it doesn't reduce Postgres load the way the other two do — a slow origin still gets hit on every edge-cache miss).
- **Nothing** — the five pages above.

A new page added to this site today has no documented rule for which of these four states it should land in. That's the gap this doc is meant to close before any more caching code gets written.

## Decision point — needs a founder call before implementation

Two genuinely different architectures could serve as "the" unified system, and this project has already made one consequential, explicit choice in this direction (2026-10-03: company page moved from direct-Postgres to backend-API, for architectural consistency with the Screener, at the cost of one extra network hop per cache miss). The same fork applies here:

**Option A — centralize in `apps/backend`.** Every public page's data (directory, sector list, industry list, homepage quick-picks) gets its own small `GET /v1/...` endpoint in `apps/backend`, cached with the exact same Redis contract `cache.py` already uses. `apps/app` becomes a pure API consumer for all DB-backed content, with zero direct Postgres access anywhere in the frontend — the natural conclusion of the 2026-10-03 decision, extended consistently. Cost: each of these ~5 pages needs its own backend port (small; these are far simpler queries than the company page), and every one gains a network hop that direct Postgres access doesn't have.

**Option B — cache directly in `apps/app`.** Rebuild a thin Redis client module in `apps/app` (the one deleted 2026-10-03) and cache these five pages' queries in place, no new backend endpoints. Cost: `apps/app` keeps (regains) a direct Postgres dependency and its own Redis client, which is the exact pattern the founder moved *away* from for the company page three days ago — reintroducing it elsewhere would mean the site has both patterns live simultaneously, unless this doc's recommendation is to also revisit that earlier call.

Recommendation, stated plainly rather than left implicit: **Option A**, for one reason that outweighs the extra hop — these five pages are the *cheapest possible candidate* to prove out "the whole site goes through `apps/backend`" as a durable rule, since their queries are simple (sector/industry lists, a directory, 11 hardcoded tickers) and their cache TTLs can be long (hours, not minutes — this data only changes when the pipeline reclassifies a company, see below). A long TTL mostly erases the hop's cost in practice: the number of requests that actually pay the extra network round trip approaches zero once the cache is warm for hours at a time. This also avoids re-litigating the 2026-10-03 consistency decision and avoids `apps/app` regaining a Postgres dependency it just shed. If the founder instead wants Option B (faster to ship, no backend changes), that's a reasonable call too — naming it here so it's a decision, not a default.

**Resolved 2026-10-13: Option A, built.** By explicit founder direction ("decide everything by[your]self") rather than a further back-and-forth — this doc's own recommendation stood on its reasoning (consistency with the 2026-10-03 move, cheapest-candidate argument, long TTLs erasing the hop cost) and nothing in the intervening 4 days changed any of it. See `doc/learnings/2026-10-13-sitewide-caching-built.md` for what was actually shipped, how it was verified live, and the one pre-existing ticker-format gap (confirmed not a regression) found along the way.

## Proposed TTL policy by data-volatility class

Not yet a final design — proposed as the starting shape for whichever option is chosen:

| Class | Examples | Proposed TTL | Why |
|---|---|---|---|
| Static reference data | sector list, industry list, full company directory | 1–6 hours | Changes only on a pipeline reclassification run, not per request — see `doc/reference/40_Scrooner_XBRL_Tag_Coverage_Library.md`-era cadence; nothing on this site reclassifies sectors more than daily |
| Per-company detail | company page (existing) | 15 min (existing, keep as-is) | Already tuned and verified; a company's own numbers change at most daily via the cron |
| Per-user data | saved-screen metadata (existing) | 30s (existing, keep as-is) | Already tuned; short because it's a user's own in-flight edits |
| Exact-repeat computation | screen results (existing) | 7 days, versioned (existing, keep as-is) | Already tuned; invalidated structurally via `dataset_version`, not TTL |
| Search-as-you-type | company search (existing) | 60s CDN (existing, keep as-is) | Already tuned; different mechanism by design, not a gap |

The only new category this doc proposes is the first row — everything else already has a tuned, working TTL; the gap was never "wrong TTLs," it was "five pages with no TTL at all."

## What this doc does NOT cover

- Pre-warming/scheduled refresh for popular tickers or screens (raised earlier in this session, still open, genuinely separate from "does a cache exist at all").
- The `apps/backend` same-region hosting decision (the dominant remaining lever, unrelated to caching).
- Moving the 69.3 GB `raw` Storage bucket to cold storage (unrelated, from the same day's Supabase audit).
- Observability/hit-rate metrics for the cache layer itself — `apps/backend/observability.py` already has a request-metrics pattern (`api_request_metrics`) that a future cache-hit-rate counter could extend, but that's an implementation detail for whichever option is chosen, not scoped here.

## Next step

Built — see `doc/learnings/2026-10-13-sitewide-caching-built.md`. Remaining, explicitly out of scope for this pass (same list as "What this doc does NOT cover" above): pre-warming, same-region hosting, Storage tiering, cache-hit-rate observability.
