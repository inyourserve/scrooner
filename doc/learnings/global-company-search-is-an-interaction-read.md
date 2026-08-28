# Global company search is an interaction read

**Problem or clarification**

The homepage had a working company finder, but it server-rendered the complete
company directory into one page. Reusing that implementation in the shared
header would either add a second database query and a directory payload to
every public company page, or leave the header search-looking but nonfunctional.
Both outcomes conflict with the one-query company-page latency contract.

**How it was found**

The homepage, shared `PublicHeader`, consolidated `getCompanyPageData()` read,
and design framework section 6.2 were traced together. The page source showed
that all active listings were emitted as `<datalist>` options before a visitor
interacted. Supabase's current serverless connection guidance was also checked:
short-lived runtime traffic should use a transaction pooler with prepared
statements disabled, which the existing Astro database client already does.

**Fix / decision**

- Added `/api/company-search.json`, a parameterized prefix-search endpoint that
  returns at most eight active, current listings with ticker, company name,
  exchange, and Scrooner's SEC-derived sector bucket.
- The endpoint is called only after a visitor types, is debounced in the
  browser, deduplicated across multiple search instances, and carries CDN
  caching plus stale-while-revalidate headers. Empty requests never touch the
  database.
- Added one accessible `CompanySearch.astro` combobox to the shared public
  header and reused it for the homepage hero. It supports arrow keys, Enter,
  Escape, the global `/` shortcut, visible loading/empty/error states, and
  responsive layouts.
- Recent selections are capped at five and stored locally as public company
  identities. Storage failures are ignored safely, and recent entries can be
  cleared.
- Replaced the homepage's full-directory read with a small query for only its
  configured quick-pick tickers. The stock route still calls only
  `getCompanyPageData()` and keeps `X-Scrooner-DB-Queries: 1`.

Unit tests cover query normalization and untrusted local-storage data. Astro
tests, type checking, production build, the design-system contract, and live
browser/runtime checks are the verification gates for this work.

**Why it matters going forward**

Global UI does not mean global data belongs in every document. Put optional
discovery data behind the interaction that needs it, cap the response, expose
honest service states, and protect the primary page-read budget. If the covered
universe grows enough that prefix scans become measurable, add a reviewed
search index based on `EXPLAIN` evidence; do not pre-emptively put the full
universe back into page HTML.
