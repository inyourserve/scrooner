# Design-system hardening and enforcement

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

## Problem or clarification

A shared token file and a few components did not yet make the interface safely
scalable. The two largest Astro routes still embedded hundreds of lines of page
CSS, loading and failure messages were repeated in feature code, and raw colors
could quietly re-enter application styles after the initial migration.

## How it was found

The audit counted page-level style blocks, searched application sources for
hex/RGB values, compared repeated state-panel markup, and followed common page
hierarchy through both Astro and React. The important gap was enforcement: the
written rule said to use semantic tokens, but no gate could reject a violation.

## Fix / decision

- Extracted homepage and company-research styles into explicit page-pattern
  stylesheets and removed inline presentation from those page templates.
- Added an executable no-index catalog that exercises the shipped primitives.
- Added typed React adapters and a common accessible `StatusPanel`, then used it
  in real loading and error flows.
- Added contrast and forced-colors support to the shared foundation.
- Expanded `scripts/check_design_system.py` so raw application colors,
  page-level style blocks, missing implementation contracts, duplicate tokens,
  and disconnected app entry points fail validation.
- Added adapter tests for semantic variants, native disabled behavior, alert
  announcement, and busy state.
- Rendered the built public surfaces and Next.js screener at desktop and exact
  390px mobile sizes. The screener was also checked with its backend absent,
  exercising the accessible service-error composition rather than only a happy
  static state.
  Chrome's `--window-size=390` still used a wider minimum layout viewport and
  merely cropped the screenshot; DevTools device-metric emulation exposed the
  real viewport and confirmed `innerWidth`, document width, and body width all
  equal 390px. The shorter mobile-safe search placeholder came from that check.

## Why it matters going forward

Documentation explains intent; executable examples and gates preserve it.
Scrooner should keep three layers distinct: semantic visual decisions in the
shared package, framework-native adapters in each application, and product
composition inside features. A new route should mostly compose established
patterns. If it needs a new raw shade or page-level style block, that is now an
explicit system decision rather than invisible drift.
