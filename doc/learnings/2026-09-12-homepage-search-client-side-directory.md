# 2026-09-12 — Homepage global search made real-time and client-side

Prompted directly: make the homepage company/ticker search box "one of the fastest," real-time, and consider storing the searchable names close to local or an industry-standard solution.

## What was there already

`components/public/CompanySearch.tsx` already did debounced (180ms) as-you-type search, calling `/api/company-search?q=` → `searchCompanyDirectory()` (`lib/company/db.ts`) — a Postgres query joining `core.company`/`core.listing`, ranked via `starts_with()` prefix matching, no `ILIKE`/full-text search. Checked before assuming it needed a new mechanism: `EXPLAIN (ANALYZE, BUFFERS)` on the worst case (single-letter query) showed **33.5ms server-side**, a full sequential scan of both tables (5,216 companies, ~6,145 listings) — no index on `ticker`/`company_name`/`display_name` exists, but the table is small enough that a seq scan is still fast in absolute terms. The real, dominant cost per keystroke was never the query — it was the same network round trip this whole session has already documented repeatedly (this dev machine to Supabase's `us-east-1`, ~250-270ms), paid **once per keystroke** even with the 180ms debounce.

## What "one of the fastest" actually means for a universe this size

6,041 rows qualify for search (one row per ticker, same filters as before) — ~250KB of raw text, ~334KB as JSON, **~75KB gzipped**. That comfortably fits in memory and in a single one-time page-load fetch. The fastest possible per-keystroke latency for a dataset this size isn't a faster query — it's **zero queries**: ship the whole directory to the browser once and match client-side, the same pattern command palettes (VS Code) and small-catalog doc-search widgets use industry-wide.

## What was built

- `lib/company/db.ts`: new `loadFullCompanyDirectory()` — the same query as `searchCompanyDirectory()` minus the prefix predicate, returns every qualifying `(ticker, company_name, exchange, sector)` row.
- `app/api/company-search/directory/route.ts`: new route, `dynamic = "force-static"` + `revalidate = 3600` — Next.js statically generates it and revalidates hourly (confirmed via `next build`: renders as `○` static with `1h` revalidate, `1y` expire), matching the real data-freshness need (the pipeline's own daily cron is the only thing that changes this data). Payload is an array of `[ticker, company_name, exchange, sector]` tuples, not objects — with ~6k rows, repeated JSON key names cost real bytes even after gzip.
- `lib/company/search.ts`: `loadCompanyDirectory()` (a module-level singleton promise, so mounting `CompanySearch` twice on one page — header + hero — never double-fetches; caches the payload in `localStorage` keyed by the response's own `generatedAt` date, so a same-day page reload never refetches) and `rankCompanyMatches()` — a pure function reproducing `searchCompanyDirectory`'s exact SQL ranking (exact ticker → exact name → ticker-prefix → name-prefix, tie-broken by ticker length then alphabetically) entirely in the browser.
- `components/public/CompanySearch.tsx`: loads the directory once on mount; once loaded, every keystroke calls `rankCompanyMatches()` synchronously — no debounce, no network call, no `AbortController`. Falls back to the original debounced server endpoint only while the directory hasn't loaded yet (first paint) or if the fetch fails, so the box never breaks, it just briefly behaves as it did before this change.

## Verified live, not assumed

- `next build --webpack`: `/api/company-search/directory` renders `○` (static) with `1h` revalidate — confirmed the ISR caching is real, not just configured.
- Real headless-Chrome test (CDP, typed into the actual rendered input, read back the actual rendered result list): `"V"` → Visa ranked first (exact ticker match), `"appl"` → AppLovin/Apple/Applied-* correctly ranked by the same prefix rules as the SQL version, `"micron"` → Micron Technology matched by company-name prefix. Not a unit test of the ranking function in isolation — the real component, real DOM, real browser.
- 4 new unit tests for `rankCompanyMatches` (`lib/company/search.test.ts`) covering exact-ticker-first ranking, ticker-prefix-over-name-prefix with the SQL's own alphabetical tie-break, name-prefix matching, and blank-query/limit behavior. Full frontend suite 82→86 passing.

## A real CSS stacking-context bug this surfaced, not caused

Making the search box actually return results reliably immediately surfaced a pre-existing visual bug: the results dropdown's first two rows rendered visibly interleaved with the "Or analyse" quick-pick chips below it, rather than cleanly overlaying them.

Root cause, confirmed via a real headless-Chrome screenshot (not source/CSS inspection, per this project's own established discipline): `#company-search` and `.quick-picks` (`app/home.css`) each carry a `home-rise` entrance animation targeting `opacity`/`transform`. Per the CSS spec, **any element with a CSS animation targeting opacity/transform/filter establishes its own stacking context for the life of that rule, independent of its current computed values** — so both elements are separate stacking contexts even after the animation finishes at `opacity: 1; transform: none`. `.company-search-results`' `z-index: 70` only has authority inside `#company-search`'s own local stacking context; it has no way to out-rank a sibling stacking context (`.quick-picks`), which paints on top purely because it comes later in the DOM.

Fixed with `position: relative; z-index: 1;` on `.home-main #company-search`, giving it explicit priority over `.quick-picks`' implicit `z-index: auto`. Verified live: the dropdown now cleanly overlays the chips instead of interleaving with them; the no-interaction baseline render is pixel-identical to before.

**Generalizable lesson**: two sibling elements that both use a CSS `animation`/`transition` on opacity or transform are *each* an independent stacking context regardless of whether the animation is currently running — a `z-index` set deep inside one of them can never win against the other sibling if that sibling is later in the DOM, no matter how high the z-index number is. Any future absolutely-positioned overlay (dropdown, popover, tooltip) nested inside an animated container needs an explicit `z-index` on that *container* itself, not just on the overlay.

## The bigger gap: the sitewide ⌘K search never got this fix (found 2026-09-13)

A direct "what's missing" review the next day found the real higher-impact gap: `components/scrooner/SearchCommand.tsx` — the `⌘K` command palette in the site header, present on **every page**, not just the homepage — is a completely separate component from `CompanySearch` and still ran the original debounced `fetch('/api/company-search?q=...')` per keystroke. Since this is the search surface actually used site-wide, it was paying the same per-keystroke network cost this whole effort was meant to remove, on every page except the homepage.

Fixed by wiring it onto the same `loadCompanyDirectory()`/`rankCompanyMatches()` used by `CompanySearch`, falling back to the server endpoint only while the directory hasn't loaded yet or failed — identical pattern, verified live via headless Chrome on a non-homepage page (`/about`, opened cold with no prior homepage visit): typing "v" returns Visa ranked first in well under the debounce window, and the existing arrow-key navigation (Up/Down + active-index highlight, a feature `SearchCommand` already had that `CompanySearch` doesn't) continued to work unchanged.

Also found and removed in the same pass: `CompanySearch`'s `variant?: "header" | "hero"` prop was dead code — grepped the whole app and found `variant="header"` was never actually rendered anywhere (the real header search is `SearchCommand`, an unrelated component). Removed the prop, hardcoded the `hero` class, updated the one real call site (`app/page.tsx`).

**Generalizable lesson**: when a fix targets "the search box," check whether the app has more than one — a homepage-only fix left the more heavily-trafficked entry point (present on every page) untouched, and it would have been easy to report the work as complete without checking.

## What this doesn't change

The old `/api/company-search` route and `searchCompanyDirectory()` query are kept exactly as they were — they're now the fallback path, not deleted. No index was added to `core.listing`/`core.company` for this — the seq scan was never the bottleneck, and removing the per-keystroke query removes the reason to add one.
