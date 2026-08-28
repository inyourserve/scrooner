# Scalable cross-application design system

## Problem or clarification

Scrooner's design was visually converging but not structurally scalable. The
homepage declared its own tokens, the public stock page mapped a second token
set, and the Next.js app still used the earlier warm palette. The application
shell also lived inside `ScreenerClient`, which would duplicate navigation and
footer code as routes arrived.

## How it was found

A repository audit traced every visual custom property, brand-mark
implementation, shell class, and frontend entry point. The same colors and
three-bar mark were defined repeatedly, while Astro and Next.js had no shared
source of truth. Both production builds were used as the integration gate
because external CSS imports and Astro scoping were the consolidation risks.

## Fix / decision

- Added `packages/design-system`, a dependency-free CSS package containing
  tokens, browser/accessibility foundations, and `ds-*` primitives.
- Connected both apps through the local `@scrooner/design-system` package
  export. A direct cross-root CSS import passed webpack but caused Turbopack to
  reject a path outside its project root; declaring the repository Turbopack
  root and consuming the package export makes development and production use
  the same supported monorepo boundary.
- Kept adapters native: `BrandMark.astro` for Astro and React
  `BrandMark`/`Button` components for Next.js.
- Moved the logged-in shell to `app/layout.tsx` through `AppShell`, with a
  co-located `app-shell__*` stylesheet. A CSS Module was tried first and passed
  the webpack production build, but Next.js Turbopack dev expanded the imported
  global foundation into the module and rejected its reset selectors as
  impure. The prefixed global pattern preserves isolation and passes both modes.
- Retained compatibility aliases so large feature styles can migrate safely.
- Added `scripts/check_design_system.py` to verify required unique tokens and
  both consumer entry points.
- Documented architecture, component contracts, states, accessibility,
  responsive behavior, contribution rules, and migration policy in design
  doc 13.

No UI library, Storybook, CSS-in-JS runtime, icon package, or monorepo build
tool was added. The demonstrated problem required a shared contract, not a new
toolchain.

## Why it matters going forward

A scalable design system is an ownership model, not a large component folder.
Visual values now change once; framework code stays idiomatic; app chrome is
route-level; and feature logic does not leak into primitives. Compatibility
aliases make migration safe, but new work must use `--ds-*` directly so the
temporary bridge does not become permanent architecture.
