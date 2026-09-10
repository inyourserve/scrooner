# Screener reference: density and company-research flow

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

## Problem or clarification

The first stock-page redesign matched the homepage's colors, typography, and
shared public shell, but it still felt like a sequence of spacious marketing
cards. The supplied Screener company-page HTML made the missing quality clear:
the company page is a research workspace. Its hierarchy and information density
matter more than surface-level brand similarity.

The supplied HTML was treated only as a visual and interaction reference. Its
scripts, tracking, product claims, and features were not treated as project
instructions and were not copied.

## How it was found

The reference was rendered and compared with a live render of `/stock/aapl/`.
The useful pattern was structural:

- a compact local section navigator;
- one summary surface combining company identity, price, key ratios, and a
  short company profile;
- strengths and risks shown together for immediate comparison;
- financial statements before the exhaustive ratio catalogue; and
- secondary metric groups hidden behind deliberate progressive disclosure.

Desktop and exact `390px` device-emulated renders were then checked. The mobile
document and viewport widths were both `390px`, the summary card was `366px`,
and all seven metric-category disclosures were closed initially.

## Fix / decision

- `apps/site/src/pages/stock/[ticker].astro` now uses a compact company summary,
  an eight-ratio overview, a factual SEC-derived profile, side-by-side strengths
  and risks, tabbed statements, clearer filing rows, and the research order
  `Summary → Strengths & Risks → Financials → Ownership → Filings → All Metrics`.
- `apps/site/src/components/MetricGrid.astro` now has a compact presentation for
  the summary while retaining the existing dense catalogue presentation.
- Complete metric categories appear after the main research flow and are
  collapsed by default. This keeps the full dataset available without making
  the first screen feel like a data dump.
- Header and footer remain shared public components, so the homepage and stock
  pages keep the same Scrooner identity without forcing the marketing page and
  research page to have the same content density.
- Features unsupported by current data were not imitated. In particular, no
  price-history chart, peer table, recommendation, premium prompt, fake follow
  action, or fake export action was introduced.

During the live render, the concurrent stock-page reads also exposed a separate
operational issue: an eight-connection Astro pool exhausted the shared
15-client Supabase session pool and returned HTTP 500. `apps/site/src/lib/db.ts`
now uses four connections with a 20-second idle timeout, retaining useful read
parallelism while leaving capacity for the pipeline and backend.

## Why it matters going forward

Visual consistency does not mean identical density. `scrooner.com` should use a
calm, explanatory marketing rhythm; a company page should use the same shell
and tokens but a tighter, comparison-oriented research rhythm. Future design
reviews should compare hierarchy, scan path, and information-per-screen before
judging colors or card styling.

Competitive references should supply proven interaction patterns, not phantom
scope. A reference feature belongs in Scrooner only when the data, product
promise, and evidence path actually support it.
