# 14 — Top 10 design execution evidence

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

> **Status:** Complete · **Date:** 2026-08-22  
> **Scope:** `scrooner.com` Astro surfaces and `app.scrooner.com` Next.js product surfaces  
> **System contract:** [`13_Scrooner_Scalable_Design_System.md`](13_Scrooner_Scalable_Design_System.md)

## Outcome

This pass selected the ten tasks with the highest compound return: changes that
improve the current interface while reducing the cost and inconsistency of
every page added next. The result is an executable system, not only a written
style guide.

The selection order followed four tests: visible user impact, repeated use,
accessibility or financial-trust risk, and future maintenance leverage.

## Completed tasks

| # | Priority task | What is now true | Primary evidence |
|---:|---|---|---|
| 1 | Audit and rank design debt | Both frontends were traced from tokens through shared chrome, page styles, states, and repeated markup. The ten tasks below came from observed duplication and drift rather than a speculative component inventory. | This report; repository diff; design doc 13 |
| 2 | Ship an executable component catalog | `/design-system/` renders the actual brand, palette roles, typography, buttons, badges, alerts, form states, and financial table primitives. It is `noindex,nofollow` and uses the same public shell as the site. | `apps/site/src/pages/design-system.astro`; `apps/site/src/styles/design-system-catalog.css` |
| 3 | Complete shared semantic primitives | Added destructive actions, icon actions, tabs, empty states, disclosure, status marks, table containment, and semantic border/code/header roles. Raw shades remain owned by `tokens.css`. | `packages/design-system/src/tokens.css`; `packages/design-system/src/primitives.css` |
| 4 | Add typed React adapters | Repeated primitives now have native typed `Button`, `Badge`, `Surface`, and `StatusPanel` adapters. They preserve normal HTML props and use the framework-neutral CSS contract. | `apps/app/components/ui/`; `ui.test.tsx` |
| 5 | Standardize application page hierarchy | The screener intro is now a reusable `PageHeader` with eyebrow, title, description, and optional actions. New authenticated routes no longer need to invent first-screen hierarchy. | `apps/app/components/layout/PageHeader.tsx`; `ScreenerClient.tsx` |
| 6 | Standardize feedback and asynchronous states | Metric-catalog and screen loading/error states plus natural-language interpretation states now use one accessible status pattern. Error, busy, live-region, title, body, and retry semantics stay consistent. | `StatusPanel.tsx`; `ScreenerClient.tsx`; `NaturalQueryPanel.tsx` |
| 7 | Extract the homepage presentation layer | The Astro homepage contains structure and content; its page pattern lives in a dedicated stylesheet. This removes a large page-level style block and makes the visual architecture inspectable. | `apps/site/src/styles/home.css`; `apps/site/src/pages/index.astro` |
| 8 | Extract the company-research presentation layer | The stock route's dense research CSS is now a named page pattern. Table alignment, note spacing, statements, ownership, filings, metrics, and responsive behavior are maintained outside the data-rendering template. | `apps/site/src/styles/company-research.css`; `apps/site/src/pages/stock/[ticker].astro` |
| 9 | Enforce semantic visuals and accessibility modes | Application code no longer carries raw hex/RGB colors. Shared foundations now cover reduced motion, increased contrast, forced-colors focus, 320px minimum layout, and contained wide financial tables. Inline page presentation was removed. | `foundation.css`; semantic token consumers; design-system validator |
| 10 | Add governance and regression checks | A validator now checks required implementation files, unique required tokens, both app entry points, raw color leakage, and page-level style blocks. React adapter tests verify variants, native attributes, alert roles, and busy state. | `scripts/check_design_system.py`; `apps/app/components/ui/ui.test.tsx` |

## Architecture after this pass

```text
packages/design-system       semantic tokens + accessible CSS primitives
          │
     ┌────┴────┐
     │         │
Astro adapters React adapters
     │         │
public patterns app patterns
     │         │
homepage / company    authenticated features
```

The domain boundary remains unchanged: public/static and logged-out content is
Astro on `scrooner.com`; authenticated and dynamic workflows are Next.js on
`app.scrooner.com`. Sharing happens through semantic CSS contracts, not by
coupling the two runtimes.

## Quality gates

The completion gate for this pass is:

```bash
python3 scripts/check_design_system.py
cd apps/site && npm run build
cd apps/app && npm run lint && npm test && npm run build
python3 scripts/check_docs.py
git diff --check
```

Record the final command results in the handoff rather than treating the
existence of this document as proof that they passed.

Rendered QA also exercises the built homepage, component catalog, and Next.js
screener at 1440px and an exact emulated 390px viewport. All three mobile
surfaces reported `innerWidth`, document scroll width, and body scroll width as
390px. The screener's live service-unavailable path also verified the new error
state with the backend intentionally absent. A cropped browser window is not
valid responsive evidence.

## Deliberate next boundary

A dependency-free structural render contract is now implemented in
`scripts/check_frontend_render.mjs`; see design doc 15. Pixel-baseline visual
regression remains deferred until a frozen fixture data set exists, because
live filing dates, prices, and values are intentionally non-deterministic. New
components should still be earned by repeated product use. Compatibility
aliases should migrate feature by feature rather than through a second visual
abstraction layer.
