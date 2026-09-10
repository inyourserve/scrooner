# Public Site and Application Domain Boundary

> **Superseded 2026-09-05:** The founder explicitly replaced this two-domain,
> Astro/Next.js boundary with one Next.js application on `scrooner.com` and
> authenticated routes under `/app`. This document remains historical context.
> The active decision is in the Decision Register and the migration contract is
> [doc 43](../planning/43_Single_Nextjs_Shared_Domain_and_Shadcn_Migration_Plan.md).

## What needed clarification

Scrooner has two product surfaces that must share one brand while retaining
different responsibilities:

- `scrooner.com`, implemented in `apps/site` with Astro; and
- `app.scrooner.com`, implemented in `apps/app` with Next.js App Router.

The tempting shorthand is “logged-out pages use Astro; logged-in pages use
Next.js.” That is directionally useful but incomplete. Authentication state is
not the canonical routing test.

## How it was resolved

The boundary is already explicit and **locked** in the canonical documentation:

- [Decision Register](../foundational/02_Scrooner_Decision_Register.md):
  `scrooner.com` owns public marketing, guides, glossary, indexable company
  pages, and public screens; `app.scrooner.com` owns the interactive screener,
  prompt flow, authentication, saved screens, and paid-account features.
- [System Design](../foundational/04_Scrooner_System_Design_and_Tech_Stack.md):
  the public domain must not own authenticated workflows or heavy client-side
  screening, while the app domain must not become the programmatic SEO surface.
- [Methodology](../foundational/05_Scrooner_Product_and_Engineering_Methodology.md):
  “Static/public; dynamic/private” is an operating rule, with Astro for
  crawlable content and Next.js for authenticated interaction.
- [Design Framework](../design/10_Scrooner_Product_Design_Framework.md): the
  domain split should be visible in the information architecture without making
  the product feel like two unrelated brands.

The decision register wins if a planning, design, or implementation document
ever contradicts these boundaries.

## The working routing test

Ask these questions in order:

1. Should the page be discoverable, indexable, shareable, and useful without an
   account? It belongs on `scrooner.com` in Astro.
2. Does the page manipulate user state, run a rich application workflow, enforce
   an entitlement, or require a session? It belongs on `app.scrooner.com` in
   Next.js.
3. Is it a transition between the two? Keep the destination on the domain that
   owns the destination job, and use an explicit cross-domain URL.

This produces the following ownership matrix:

| Experience | Domain and framework | Reason |
|---|---|---|
| Homepage, product explanation, methodology, guides, glossary | `scrooner.com` / Astro | Public and indexable |
| Pricing explanation | `scrooner.com` / Astro | Public product content |
| Public company search and `/stock/{ticker}` | `scrooner.com` / Astro | Public company research and SEO |
| Curated or public screen landing pages | `scrooner.com` / Astro | Shareable/indexable content |
| Plain-English screener and structured builder | `app.scrooner.com` / Next.js | Interactive product workflow |
| Screen results and “why matched” interaction | `app.scrooner.com` / Next.js | Dynamic workflow state |
| Sign in, sign up, session recovery | `app.scrooner.com` / Next.js | Authentication is app-owned even before a session exists |
| Saved screens, account, usage, plan, checkout | `app.scrooner.com` / Next.js | Private user and entitlement state |
| Sign-out action | `app.scrooner.com` / Next.js | Mutates the application session |
| Post-sign-out public landing page | `scrooner.com` / Astro | Public destination after the app clears the session |

## Important nuances

- **Astro does not mean every page must be pre-rendered.** The current company
  page uses Astro server output and reads governed Postgres views. It remains a
  public-site concern because its product role is public/indexable company
  research.
- **Unauthenticated does not always mean Astro.** Sign-in, sign-up, password
  recovery, and auth callbacks are part of the app workflow and therefore belong
  to Next.js.
- **Pricing content and billing are different concerns.** The public explanation
  belongs on Astro; checkout, subscription management, and entitlements belong
  on Next.js.
- **Company research and screening are different jobs.** Public company lookup
  belongs on Astro. Multi-condition screening and query interpretation belong on
  Next.js.
- **The design system is shared; the runtime is not.** Typography, colors,
  spacing, navigation language, accessibility, and trust patterns should match
  across both apps. Components do not need to be forced into one frontend
  runtime to achieve that consistency.

## Current implementation audit — 2026-08-21

The repository currently follows the boundary in its main routes:

- `apps/site/src/pages/index.astro` is the public homepage.
- `apps/site/src/pages/stock/[ticker].astro` is public company research.
- `apps/app/app/screener/page.tsx` is the interactive screener.
- `apps/app/.env.example` uses `NEXT_PUBLIC_SITE_URL` for links from the app to
  public company research.
- `apps/site/.env.example` uses `PUBLIC_APP_URL` for links from the public site
  into the screener.

The recent visual-system work in `apps/app` stayed inside the correct boundary.
The Astro homepage and company page were audited for visual consistency but were
not moved into Next.js.

There is one material implementation gap: the Next.js screener does not yet have
an authentication guard. The route is owned by the correct application, but it
is currently reachable before sign-in because the planned Supabase Auth UI and
session layer have not been built. The intended production state, clarified by
the founder on 2026-08-21, is that the dynamic application experience is the
logged-in surface. Authentication entry and recovery routes are the unavoidable
pre-session exception on `app.scrooner.com`; after authentication, protected app
routes must enforce the session server-side. Saved-screen pages remain future
app work as well.

## Working rule for future tasks

Before making product, design, or implementation changes:

1. Read `doc/README.md`, the Decision Register, the relevant foundational or
   execution document, current status, and related learnings.
2. State which domain owns the user job before choosing a file or framework.
3. Preserve explicit cross-domain navigation and environment-configured origins;
   do not rely on same-origin relative links across the boundary.
4. After material work, write what was learned, how it was verified, what changed,
   and what future work must remember in `doc/learnings/`.
5. Update canonical decisions only when the founder explicitly changes them;
   learning notes explain application of a decision and do not supersede it.

## Why this matters going forward

Without this test, the project could drift toward the explicitly superseded
“single Next.js site for everything” architecture, duplicate public pages across
two domains, weaken SEO, or put session-sensitive behavior on the public site.
The correct goal is one coherent Scrooner experience with two deliberately narrow
delivery systems.
