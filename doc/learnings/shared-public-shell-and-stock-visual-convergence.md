# Shared Public Shell and Stock-Page Visual Convergence

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

## Problem or clarification

After the new homepage shipped, public stock pages still looked like another
product. They retained the earlier warm-paper palette, bracket wordmark,
Fraunces headings, heavier ledger borders, separate header markup, and a
different footer. Matching values manually would not prevent the two surfaces
from drifting again.

“Keep the header and footer the same everywhere” therefore required shared
rendering components, not a visual imitation in two files.

## How it was found

The real homepage and `/stock/aapl/` were rendered side by side at 1440×1100
and at an exact 390×844 CSS-pixel viewport. The comparison exposed the identity,
palette, typography, border, radius, shadow, spacing, and shell differences.

After implementation, browser geometry and DOM text were checked on both mobile
pages. Each reported `innerWidth = 390`, `scrollWidth = 390`, and identical
header/footer content. The stock page retained its horizontally scrollable local
section navigation and financial tables without creating document-level
overflow.

## Fix / decision

- Added `PublicHeader.astro` and `PublicFooter.astro` as the only public-site
  header and footer implementations.
- Added `public-theme.css` for shared cool-gray, teal, Inter, and Newsreader
  primitives.
- Refactored both the Astro homepage and stock page to render those components.
- Migrated the stock page from the old warm/bracket/Fraunces treatment to the
  homepage identity and visual tokens.
- Reworked the company identity into a calm white hero surface with the same
  radius and shadow language as homepage search.
- Softened cards, metric cells, statement tabs, tables, filing rows, and
  category surfaces while retaining dense, inspectable financial data.
- Removed the obsolete stock-page header/footer CSS after the shared shell was
  active.

The Next.js application remains a separate domain and workflow shell. It should
share brand primitives, but a persistent public footer should not be forced into
an authenticated research workspace without a product reason.

## Why it matters going forward

Every new public Astro page must use `PublicHeader`, `PublicFooter`, and
`public-theme.css`; it must not reproduce their markup or tokens locally.
Context may change the active navigation state and company link target, but the
shell structure, spacing, identity, and responsive behavior stay shared.

Shared components prevent brand drift. Shared screenshots and exact viewport
measurements prove that reuse still works in the rendered product.
