# Company page moved to an API call, not direct DB access (2026-10-03)

By explicit founder direction: `apps/app` must never hold a direct Postgres connection for the company page — it must call `apps/backend`, matching the Screener's architecture, for consistency. This **supersedes** doc 04/17's original "Next.js reads approved serving views directly" design for this one page; recorded here, not silently assumed.

## What moved

- `apps/app/lib/company/db.ts::getCompanyPageData()` (one ~570-line SQL query assembling the whole company page as nested JSONB) → `apps/backend/company_page.py::get_company_page_data()`. The SQL is copied **verbatim**, with exactly three mechanical substitutions (`${ticker}` → `%(ticker)s`, `${EQUITY_ONLY_SQL}`/`${HISTORY_FLOOR}` → their own literal text, both fixed constants in the original, never user input). `assembleStatement()` is ported 1:1 to `_assemble_statement()`.
- `apps/app/lib/company/cache.ts` (Redis cache, 15-min TTL) → new functions in `apps/backend/cache.py` (`get_cached_company_page`/`set_cached_company_page`), same key naming (`company-page:<ticker>`), same TTL, same fail-open contract. A `CACHE_MISS` sentinel distinguishes "nothing cached" from "cached as not-found" (a persistently invalid ticker's 404 is itself cached, same as the original).
- New `GET /v1/company/{ticker}` (`apps/backend/routers/company.py`), no auth (public SEO page, matches `/v1/metrics`'s own posture).
- `apps/app/app/stocks/[ticker]/page.tsx` now calls that endpoint via `fetch()`; the old direct-query/cache functions and their now-dead private types (`RawStatementRow`, `CompanyPageQueryRow`, `MetricHistoryRow`) were deleted from `db.ts`, and `lib/company/cache.ts` was deleted outright — both confirmed unused anywhere else first.

## Verification

Faithful-port discipline, not "rewrite and hope": ran the OLD TypeScript function and the NEW Python port side by side against the real live database for two very differently-shaped companies (AAPL — full peer/price/segment data; JPM — a bank, different metric coverage) and deep-diffed the JSON output key-by-key. **Zero differences** both times (the raw byte-size gap was only JSON unicode-escaping style, not a real discrepancy). Then verified the real HTTP endpoint: cache miss 1.6s → cache hit 4ms, a genuinely nonexistent ticker correctly 404s, and the live Next.js page (`next dev`, real browser path) still renders correctly for both a real ticker and an unknown one. 4 new backend tests (`_assemble_statement`'s dedup/sort logic, the router's cache-hit/cache-miss/404 branches); full backend suite 59 → 64 passing; frontend `tsc`/`eslint`/`vitest` (112 tests) and the repo's design-token checker all clean after deleting the dead code.

## Known tradeoff, stated not hidden

This adds a network hop (Next.js → FastAPI → Postgres) where there was none before. On this dev machine that cost is masked by Redis caching (cache-hit path is still ~ms), but a **cache-miss** now pays the backend's own connection/query cost *plus* the Next→backend hop, rather than Next.js reaching Postgres directly. The founder's own stated reason for this change is architectural consistency (one service owns all DB access, matching the Screener), not raw speed — worth remembering if a future session is confused why this page has an extra hop other `apps/app` pages (sector, industry, search) don't yet have. Those other pages still read Postgres directly and were **not** touched — this change was scoped to the company page only, per the original ask.
