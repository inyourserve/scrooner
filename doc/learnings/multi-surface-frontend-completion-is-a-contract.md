# Multi-surface frontend completion is a contract

## Problem or clarification

“Finish the frontend” is not a useful completion condition when one product
spans a public Astro site, a dynamic Next.js application, a shared design
system, and live financial data. Counting completed pages can still leave
duplicated shells, inconsistent states, inaccessible tables, broken mobile
geometry, or documentation describing an interface that no longer exists.

## How it was found

The homepage, design-system catalog, AAPL research page, and screener were
traced from shared tokens through rendered DOM at desktop and exact mobile
viewports. That cross-surface check found issues page-by-page review missed:
undefined tokens, catalog fallbacks, a browser-cleanup race, a route-cleanup
rejection, the false review-before-run click, and stale framework claims about
the Astro starter and uncurated metrics.

## Fix / decision

Frontend completion is now assessed as a layered contract:

1. shared semantic tokens and primitives are consumed by both runtimes;
2. each framework keeps native shells and components;
3. product journeys enforce click count, ambiguity, null, and error behavior;
4. landmarks, focus, labels, tables, tabs, live states, and responsive overflow
   are verified structurally;
5. production builds, tests, design-system checks, docs checks, and real browser
   rendering all pass; and
6. open product boundaries remain explicit rather than being hidden inside a
   broad “frontend complete” label.

The current boundary deliberately leaves auth/account UI, saved screens,
global autocomplete/recent search, complete parser aliases, API-exposed metric
lineage, formal usability/screen-reader audits, and pixel baselines open.

## Why it matters going forward

A new page is not complete merely because it looks finished in one browser.
It is complete when it composes the shared system, preserves the product's data
and accessibility contracts, passes the same render geometry, and updates the
canonical status documentation. Conversely, an unbuilt feature must stay named
as open even when adjacent surfaces are polished. This keeps “complete” useful
for planning instead of turning it into a visual impression.
