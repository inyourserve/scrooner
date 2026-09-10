# Company display name cleanup — EDGAR's raw `/XX/` suffix, fixed 2026-09-07

## The report

Direct user report, two examples: "COSTCO WHOLESALE CORP /NEW" and "TUCOWS
INC /PA/" rendering on the company page — EDGAR's own disambiguation
convention (a state-of-incorporation or "/NEW" re-registration marker
appended to a company name) leaking straight into the UI.

## Scope, checked live before building

`company_name ~ '/[A-Za-z]{2,4}/?\s*$'` against `core.company` found **181**
active companies, not the 140 an initial narrower regex (requiring a
trailing slash) found — 41 more genuine cases use the same convention
without the closing slash (`CORNING INC /NY`, `WELLS FARGO & COMPANY/MN`,
`QUALCOMM INC/DE`). All manually spot-checked: zero false positives, every
suffix is a real 2-letter US state code (or `/CN` for a Canadian filer).

## The fix

New `core.company.display_name`/`display_name_source` columns (migration
`0046`), kept strictly separate from `company_name` (the SEC source of
truth, never overwritten) — same pattern as `y_sector`/`y_industry` and
`y_about_text`/`y_website`. `company_master/display_name.py` resolves it in
priority order: **yfinance** `longName`/`shortName` (real, human-cased legal
name) → **OpenFIGI** `name` (ALL-CAPS but suffix-free) → a deterministic
regex strip of the EDGAR suffix off `company_name` itself (always succeeds,
so this is the one place in the whole yfinance-integration effort where the
output is never an honest null — the input always has *some* real name to
clean up).

Run unpaced first, by explicit user direction ("first use yfinance without
rate limit") — at this population size (181), a single unpaced pass
comfortably stayed under Yahoo's real throttle threshold (~1,800-2,000
requests, found empirically 2026-09-06): **180/181 resolved via yfinance,
1 via OpenFIGI, 0 needed the fallback strip.** No cleanup pass was needed.

## Wired into the frontend

`apps/app/lib/company/db.ts`: every query that selects `company_name` for
direct display (`getCompanyPageData`, its peer-comparison CTE,
`searchCompanyDirectory`, `getCompaniesByTickers`, `getCompaniesBySectorSlug`,
`getCompaniesByIndustrySlug`) now selects `coalesce(c.display_name,
c.company_name) as company_name` instead. Safe because none of these
interfaces are used as a join/lookup key elsewhere — checked directly
(`CompanyIdentity`/`getCompanyPageData` has exactly one consumer, the stock
page itself) before coalescing under the same field name rather than adding
a parallel one. Search matching (`WHERE ... starts_with(...)`) still checks
the raw `company_name` too (so a query using the literal EDGAR suffix text
would still match, extremely unlikely but harmless), plus now also checks
`display_name` directly.

Verified live via the running `next dev` server (not just SQL): `/stocks/cost`
renders `<title>Costco Wholesale Corporation (COST) — Scrooner`, `<h1
id="company-name">` shows `Costco Wholesale Corporation`, `/stocks/tcx` shows
`Tucows Inc.` — no raw SEC suffix visible anywhere on either page. Full
pipeline suite: 427/427. App suite: 69/69. `npx tsc --noEmit`: clean.
