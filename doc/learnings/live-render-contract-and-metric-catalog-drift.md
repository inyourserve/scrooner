# Live render contract and metric-catalog drift

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

## Problem or clarification

Builds and component tests could prove compilation and state behavior, but not
that the real Astro and Next.js surfaces composed correctly with seeded data.
The live metric catalog had also grown faster than its human-facing metadata,
and CSS could reference a misspelled design token without any build failure.

## How it was found

The backend was run against its configured database, a real ROE screen was
executed, and four user surfaces were rendered at desktop and exact emulated
390px widths. Repository searches then compared every bare `--ds-*` reference
with available custom-property definitions. Finally, the live `/api/metrics`
response was inspected for its fallback category and definition.

This found three distinct failures:

- three undefined footer token references silently discarded by the browser;
- 26 of 47 active metrics using generic presentation fallbacks; and
- a successful browser run exiting non-zero because Chrome profile cleanup
  raced a still-running process; and
- an unhandled `AbortError` when repeated route navigation aborted the
  screener's in-flight metric-catalog request.

## Fix / decision

- Corrected the footer to defined semantic tokens and added undefined-token
  detection to `scripts/check_design_system.py`.
- Curated all 47 current screenable metrics in
  `apps/backend/metric_catalog.py` and added a completeness regression test.
- Added `scripts/check_frontend_render.mjs`, a dependency-free local Chrome
  contract covering homepage, catalog, AAPL research, and screener at 1440px
  and exact 390px widths.
- Made that command reject generic catalog fallbacks, forbidden happy-path
  errors, missing stable content, and horizontal document overflow.
- Scoped browser termination and temporary-profile deletion to the exact
  process and directory created by the command.
- Replaced route-cleanup request abortion with an active-instance guard and
  added a regression test, preventing stale state updates without generating a
  browser rejection during navigation.

## Why it matters going forward

Compilation is not rendered evidence, and a screenshot is not trustworthy
unless the CSS viewport is measured rather than inferred from its pixel size.
Likewise, a database metric becoming technically screenable does not make its
machine name product-ready. Scrooner's release discipline now checks the whole
local chain—data, API metadata, both frontend runtimes, exact viewport, and
cleanup—without introducing a second frontend testing framework.
