# Day 8 — Structured Screener UI Evidence

> **Status:** COMPLETE  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 8

## Executive outcome

Scrooner now has a usable structured-screening vertical slice at `/screener`. A non-developer can select validated financial metrics and operators, add or remove conditions, constrain by SIC classification, choose sorting and a result limit, run the existing Screener API, and inspect exact matched values and their financial periods.

This is a real product boundary, not a static mock-up. The browser constructs the backend's typed query contract, the Next.js server proxies it to the existing FastAPI service, and the service delegates screening to the already-tested pipeline engine. The interface does not recalculate financial metrics or silently reinterpret missing values.

Day 8 is complete. This does not override Day 7's no-go decision: the UI can proceed against the verified golden-company system while the wider-universe deployment, mapping, and capacity blockers are resolved separately.

## What was built

### Interactive application

- A Next.js App Router application in `apps/app`, with `/` redirecting to `/screener`.
- Server-side same-origin proxy routes for `GET /v1/metrics` and `POST /v1/screen`; the backend origin remains server configuration rather than browser state.
- A structured filter builder with add/remove controls and all nine supported operators.
- Percentage-aware inputs that convert display percentages to API ratios without binary floating-point conversion.
- Exact string-based range comparison so high-precision endpoints are not collapsed through JavaScript `Number`.
- SIC classification, sort metric, sort direction, result limit, and inactive-company controls.
- Four one-click reference screens matching the previously verified Screener examples.

### Honest result and failure states

- Distinct idle, loading, successful-zero-result, API-error, and metric-catalog-error states.
- Client-side validation that prevents empty, malformed, unsupported, or contradictory screens from executing.
- Result rows showing ticker, company, SIC classification, selected/sorted metric values, period label/date, and formula version.
- Backend result ordering preserved without client-side re-sorting.
- Exact Decimal strings retained in the response model and exposed on formatted values; display rounding is presentation only.
- Missing-data exclusions presented separately from companies that failed a financial condition.
- Direct links to the canonical Astro company page at `/stock/{ticker}/`.
- An expandable exact-query disclosure for auditability and support.

### Metric contract

The backend now exposes `GET /v1/metrics`. Database rows remain authoritative for metric name, formula, version, active status, and current screenability. A small presentation catalog supplies human-readable labels, definitions, categories, and value types. The endpoint deliberately uses the same current `requires_price = false` boundary as the Screener resolver, so the UI cannot advertise a metric that the engine will reject.

### Design-system implementation

The UI implements the framework in `doc/design/10_Scrooner_Product_Design_Framework.md`:

- approximately 60% neutral canvas and breathing space;
- approximately 30% white/subtle surfaces, borders, tables, and structural controls;
- approximately 10% green brand emphasis for primary actions and key orientation cues;
- red, amber, and blue reserved for semantic error, warning, link, and focus roles rather than decoration;
- restrained density, visible periods, plain-language definitions, one dominant action, and progressive disclosure;
- responsive layouts, semantic fieldsets/tables, programmatic labels, keyboard-visible focus, non-color status cues, and horizontal-table focus access.

## Four reproducible reference contracts

The UI's reference buttons generate these exact logical requests:

| Reference screen | Predicate | Sort | Limit |
|---|---|---|---:|
| ROE above 30% | `roe > 0.3` | ROE, descending | 50 |
| Software companies | `sic_code = 7372` | deterministic default | 50 |
| Debt/equity 0–1x | `debt_to_equity between [0, 1]` | debt/equity, ascending | 50 |
| Top 3 by ROIC | `roic top_n 3` | ranking operator | 3 |

Automated tests assert the complete payload for every reference, including `include_inactive`, `sort_desc`, categorical predicates, and null sorting.

## Verification evidence

### Frontend

Run from `apps/app`:

```bash
npm test
npm run lint
npm run build
```

Results on 2026-08-18:

- Vitest: **2 files, 9 tests passed**.
- ESLint: **passed with zero findings**.
- Next.js production build: **passed**, including TypeScript and static generation.
- Built routes: `/`, `/screener`, `/api/metrics`, and `/api/screen`.

The tests cover all four reference payloads, arbitrary-precision percentage conversion, arbitrary-precision range comparison, empty-screen blocking, loading, successful zero results, API failure, result period/value rendering, company links, and partial coverage.

### Backend

Run from `apps/backend`:

```bash
.venv/bin/pytest tests -q
```

Result on 2026-08-18: **14 tests passed** in 0.83 seconds. The focused API coverage verifies full Decimal serialization, invalid-request rejection before execution, the metric-catalog contract, and the existing safe interpretation boundary for `/v1/ask`.

One non-blocking `StarletteDeprecationWarning` is emitted by FastAPI's installed test-client compatibility layer. It does not change the result, but dependency migration should be handled in routine maintenance rather than ignored indefinitely.

### Continuous integration

The required GitHub Actions workflow now has a dedicated Screener-app job that runs locked installation, lint, tests, and production build. The local `scripts/quality.sh` equivalent includes the same three app gates. Node production dependencies are also included in the advisory audit job.

## Definition of Done

| Gate | Result |
|---|---|
| Four verified screens reproducible without an API client | PASS — buttons and exact-payload test |
| UI matches backend schema | PASS — typed builder and route proxy |
| Deterministic order and Decimal precision preserved | PASS — no client sort; string conversion/display evidence |
| Invalid queries blocked and explained | PASS — validation and UI test |
| Empty, failed, and incomplete results distinguished | PASS — separate state components and UI tests |
| Metric definitions and type-specific formatting available | PASS — live catalog endpoint and formatter |
| Company-page navigation present | PASS — canonical ticker links |
| Keyboard, labels, focus, and contrast addressed | PASS — semantic controls and design tokens |
| Production build passes | PASS |

## Consultant assessment

The vertical slice is appropriately narrow and high quality for Day 8. Its strongest feature is not visual polish; it is the faithful preservation of Scrooner's core proposition: simple discovery with inspectable financial truth. The UI exposes periods, versions, exact requests, and missing coverage while keeping the primary workflow compact.

Three limitations remain deliberate:

1. The current Screener engine still excludes price-dependent metrics, so the UI catalog does too.
2. The interface has not yet been validated through external usability sessions; that belongs in the Day 10 readiness review.
3. The plain-English interpretation workflow is not mixed into this screen prematurely; it is the separate Day 9 outcome.

The recommended next action is Day 9: add the explainable plain-English Query interface on top of the same structured contract, with interpretation shown and explicit user confirmation before execution.
