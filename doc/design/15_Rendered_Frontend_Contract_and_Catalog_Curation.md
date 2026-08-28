# 15 — Rendered frontend contract and metric-catalog curation

> **Status:** Complete · **Date:** 2026-08-22  
> **Applies to:** Astro public surfaces, Next.js screener, and the local product API  
> **Executable contract:** `scripts/check_frontend_render.mjs`

## Outcome

Scrooner now has a repeatable rendered contract over four real surfaces:

1. public homepage;
2. no-index design-system catalog;
3. seeded AAPL company-research page; and
4. Next.js screener connected to the real local backend and database.

Each surface is loaded at 1440×1100 and an exact emulated 390×844 viewport.
The check waits for surface-specific content, rejects document-level horizontal
overflow, captures a diagnostic screenshot, and verifies that the live metric
catalog contains no generic presentation fallbacks.

This is a structural render contract, not pixel-baseline visual regression.
That distinction keeps changing filing dates, prices, and company values from
creating meaningless image diffs while still catching broken composition.

## Prerequisites and command

Run the configured local services first:

```bash
cd apps/backend && ./.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --env-file .env
cd apps/site && npm run build && node dist/server/entry.mjs
cd apps/app && npm run dev -- --hostname 127.0.0.1
```

Then, from the repository root:

```bash
node scripts/check_frontend_render.mjs
```

Optional inputs are `--site-url`, `--app-url`, `--output`, and
`--chrome-path`; `CHROME_PATH` is also supported. The implementation uses only
Node.js built-ins and the Chrome DevTools protocol, so it adds no browser-test
package to either application.

## Contract assertions

| Surface | Stable content assertion | Live dependency |
|---|---|---|
| Homepage | Proposition and SEC-derived research copy | Seeded quick picks; company results load only after search interaction |
| Catalog | System proposition and brand section | Shared CSS package |
| AAPL page | Company identity, Financials, Recent Filings | Seeded PostgreSQL serving data |
| Screener | Plain-language creator and advanced-filter gateway | FastAPI `/v1/metrics` |

For every viewport the command requires:

- the requested CSS viewport width is exact;
- `documentElement.scrollWidth` does not exceed it;
- `body.scrollWidth` does not exceed it;
- required content appears before timeout;
- forbidden service-error content does not appear on the happy path; and
- every active metric has a curated category and definition.

Screenshots go to the operating system's temporary directory by default and
are diagnostic artifacts, not committed baselines.

## Live evidence

The completed run reported:

- 47 curated live metrics;
- 8/8 rendered surface/viewport combinations passing;
- 1440px document width at every desktop case;
- 390px document width at every mobile case;
- real AAPL page title and populated financial research content; and
- the live plain-language screener without its unavailable-catalog state.

Before the render run, the backend was independently checked: `/health`
returned OK and a real screen for ROE above 30% returned four matches (AAPL,
MSFT, GOOGL, and ALX), 142 explicit missing-data exclusions, and 17 inactive
exclusions.

## Defects found and fixed

### Undefined footer tokens

Three footer references used non-existent names (`font-size-sm`,
`font-size-xs`, and `text-tertiary`). Browsers silently dropped those
declarations. They now use defined semantic tokens, and
`scripts/check_design_system.py` rejects any future bare `--ds-*` reference
without a definition. Component extension points remain legal when they carry
an explicit CSS fallback.

### Metric-catalog drift

Only 21 of 47 screenable metrics had curated presentation metadata. The other
26 appeared under “Other” with machine-generated title casing and the generic
definition “Defined Scrooner metric.” Every current metric now has an
investor-facing name, short definition, category, and correct available value
type. Accounting-quality, operating-efficiency, growth, profitability,
financial-strength, capital-allocation, and ownership groupings replace the
generic bucket.

The live render command rejects either the `Other` category or generic
definition, making pipeline-to-product catalog drift visible immediately.

### Browser cleanup race

The first successful eight-surface run still exited non-zero because Chrome
was writing its temporary profile while cleanup ran. The checker now waits for
the exact spawned process, escalates from `SIGTERM` to `SIGKILL` only for that
process when needed, retries the narrowly scoped temporary-profile removal,
and exits cleanly.

### Route-cleanup abort rejection

Repeated navigation during the render pass exposed an unhandled browser
`AbortError` from the screener metric-catalog effect. The data request was
already followed by a catch handler, but aborting it during route cleanup still
surfaced as an unhandled development-runtime rejection. The effect now uses an
active-instance guard: the small catalog request may finish, but it cannot
update an unmounted route and no rejection is manufactured during navigation.
A regression test verifies route cleanup does not attach or abort a request
signal.

## Remaining boundary

Pixel-level baselines remain deferred until a deliberately frozen fixture data
set exists. The next trust-UI work should expose already-stored lineage,
`data_as_of`, and friendly null-reason metadata through the screener result
contract. Plain-English aliases also remain behind the growing structured
metric catalog; catalog curation does not imply parser coverage.
