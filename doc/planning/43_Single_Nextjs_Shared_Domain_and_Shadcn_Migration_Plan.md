# 43 — Single Next.js, shared-domain, and shadcn migration plan

> **Status:** Executed. Next.js is the only frontend framework. **Owner:** Founder / Product ·
> **Date:** 2026-09-05

## Outcome

Scrooner is one Next.js App Router application on `scrooner.com`. The former
frontend and subdomain split are retired. Legacy URLs permanently redirect to
their shared-origin destinations. Shadcn New York is the owned component foundation, themed with
Scrooner's semantic tokens.

Use one shared-origin route system. Every `/app/*` route requires
authentication. Everything else is public and indexable unless explicitly
excluded for a non-auth reason.

```text
/                         public company search and stock screener; primary SEO landing page
/stocks                   public company directory
/stocks/{company_slug}    public company research
/screens/{slug}           public predefined screen
/pricing                  public information
/learn                    public learning hub
/glossary                 public investing glossary
/blog                     public editorial content
/login                    authentication entry
/signup                   authentication entry
/forgot-password          authentication recovery
/auth/callback            PKCE callback
/app                      logged-in dashboard
/app/watchlists           private watchlists
/app/saved-screens        private saved screens
/app/alerts               private alerts
/app/account              private account and security
```

## Why consolidate

- One runtime, component registry, navigation system, and responsive contract.
- Same-origin cookies, authentication callbacks, and internal navigation.
- No `PUBLIC_APP_URL`/`NEXT_PUBLIC_SITE_URL` cross-domain choreography.
- Public pages retain Server Components, static generation, metadata, caching,
  and minimal client JavaScript.
- Preview deployments and end-to-end tests cover the whole product.

Framework consolidation must not turn public pages into client-rendered app
screens. Use Server Components by default and `use client` only on interactive
leaves.

## Target structure

```text
apps/app/app/
├── layout.tsx
├── (public)/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── stocks/page.tsx
│   ├── stocks/[company_slug]/page.tsx
│   ├── screens/[slug]/page.tsx
│   ├── about/page.tsx
│   ├── methodology/page.tsx
│   ├── data-sources/page.tsx
│   ├── pricing/page.tsx
│   ├── privacy/page.tsx
│   └── terms/page.tsx
├── (auth)/
│   ├── layout.tsx
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   ├── forgot-password/page.tsx
│   └── auth/callback/route.ts
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── watchlists/page.tsx
│   ├── saved-screens/page.tsx
│   ├── alerts/page.tsx
│   └── account/
└── api/
```

Keep one root `html`/`body`. Route groups provide public and auth layouts
without adding URL segments; `/app` provides the authenticated shell.

## Shadcn contract

- `components.json`: New York, Tailwind v4, CSS variables, Lucide.
- `lib/utils.ts`: canonical `cn()`.
- Scrooner teal maps to `primary`; shadcn does not replace the brand.
- Components are owned source, not an opaque package.
- Initial set: Button, Input, Textarea, Label/Field, Card, Badge, Alert,
  Dialog/Alert Dialog, Popover, Tooltip, Tabs, Table, Select, Checkbox,
  Skeleton, Separator.
- New files use lowercase shadcn names. Temporary re-exports preserve current
  capitalized imports until all consumers migrate.
- Do not turn every research section into a Card. Financial tables remain
  dense semantic tables; badges remain exceptional.

## Completed route mapping

| Former route | Next.js destination | Rendering |
|---|---|---|
| `/` | `(public)/page.tsx` | Static Server Component |
| `/stock/[ticker]` | `/stocks/[company_slug]/page.tsx` after slug support lands | Permanent redirect to request-time SSR canonical page |
| `/api/company-search.json` | `/api/company-search/route.ts` | Cached Route Handler |
| information pages | matching `(public)` pages | Static |
| `/404` | `not-found.tsx` | Static |

Port data access before markup. Extract the company read model from the large
Astro page into typed server modules, then compose React sections from it.

## SEO and cache contract

- Canonicalize company research at `/stocks/{company_slug}`. Keep stable slugs
  separate from display names and tickers; redirect legacy ticker URLs only
  after the slug lookup contract is available.
- Preserve canonical metadata, Open Graph, robots, sitemap, structured data,
  real 404s, and server-readable HTML.
- Redirect ticker casing to lowercase canonical paths.
- Cache the complete company read with bounded revalidation and ticker-specific
  tags; invalidate after successful pipeline refresh.
- Static information pages remain prerendered.
- Record response size, server time, cache status, and client JavaScript before
  and after. Next.js must not regress the Astro baseline.

## Authentication and authorization

- Supabase Site URL: `https://scrooner.com`.
- Allow `https://scrooner.com/auth/callback` plus controlled preview/local URLs.
- Successful login defaults to `/app`; preserve only validated relative `next`
  paths for deep links.
- Proxy performs optimistic cookie refresh/routing only.
- Authorization remains in the data-access layer and every private Route
  Handler/Server Action.
- Protect `/app/:path*` as one route group. Private APIs retain server-side
  authorization. Public screen reads use a publication-safe contract and never
  reuse the caller-scoped private saved-screen endpoint.
- Avoid session work on public pages unless the rendered header needs it.

## Legacy redirects

| Old app-subdomain path | New apex path |
|---|---|
| `/` | `/app` |
| `/screener` | `/` |
| `/saved-screens` | `/app/saved-screens` |
| `/account` | `/app/account` |
| `/account/update-password` | `/app/account/update-password` |
| `/login` | `/login` |
| `/signup` | `/signup` |
| `/forgot-password` | `/forgot-password` |

Avoid forwarding auth codes through redirect chains. Update the Supabase
allowlist before switching email/OAuth destinations. Keep the old subdomain as
a redirect for bookmarks and existing links.

## Migration phases

### 0. Freeze and baseline

- Commit current shadcn/copy changes.
- Record routes, screenshots, HTML, accessibility results, response headers,
  cache behavior, and bundles.
- Add route-contract tests.

**Gate:** clean working tree and reproducible production baseline.

### 1. Shells and primitives

- Add `(public)`, `(auth)`, and `/app` layouts.
- Port public header/footer and authenticated navigation.
- Complete the initial shadcn primitive set.
- Migrate consumers incrementally; no big-bang CSS rewrite.

**Gate:** component, keyboard, state, and responsive shell tests pass.

### 2. Static public pages

Port About, Methodology, Data Sources, Pricing, Privacy, Terms, and 404 with
metadata tests. Keep Astro live until parity is proven.

### 3. Homepage and company search

Port homepage and search; move the JSON endpoint to a cached Route Handler.
Preserve autocomplete, recent searches, keyboard behavior, and honest states.

### 4. Stock research

- Extract and type the company data layer.
- Port sections one at a time as Server Components.
- Client components are limited to chart controls, financial view/history,
  tabs, tooltips, and enhanced disclosures.
- Preserve `previous → latest`, table semantics, null reasons, ownership
  limitations, and direct SEC evidence.

**Gate:** fixtures cover normal issuers, financials, BDCs, missing prices,
sparse ownership, and 404s; desktop/mobile visual and no-JS reviews pass.

### 5. Authenticated route move

Expose company search and screening on `/`. Keep dashboard, watchlists,
saved-screen management, alerts, and account settings under `/app`. Public
predefined screens use `/screens/{slug}` only after a publication-safe backend
read model exists.

**Gate:** unauthenticated deep links return to the requested route after login;
RLS and user-isolation tests pass.

### 6. Production cutover

- Point `scrooner.com` to Next.js.
- Configure app-subdomain redirects.
- Update Supabase URLs and production environment.
- Remove cross-origin URL construction.
- Monitor callback failures, 404s, latency, caches, and search indexing.

**Gate:** production smoke test passes before Astro removal.

### 7. Astro retirement

After the rollback window, delete `apps/site`, Astro dependencies/config, its
Vercel project, duplicated adapters, and compatibility aliases. Update CI,
documentation, diagrams, and runbooks.

## Required validation

- Unit and component tests.
- Public/auth/app/API/redirect/404 route tests.
- PKCE login, confirmation, recovery, logout, and expired-link tests.
- Server-side authorization and RLS isolation tests.
- Company read-model contract tests.
- Desktop/mobile visual regression.
- Keyboard, screen-reader, axe, reduced-motion, and forced-colors checks.
- Cache/revalidation and pipeline invalidation tests.
- Preview and production smoke tests.

## Rollback

Use the previous Vercel production deployment for application rollback. No
second frontend runtime remains in the repository. Use additive database
changes only.

## Definition of done

- `apps/app` is the only production frontend.
- `scrooner.com` is the only product origin.
- The homepage owns public company search and screening; every personalized
  workflow lives under `/app`; published screens live under `/screens/{slug}`.
- `app.scrooner.com` only redirects.
- No Astro runtime, active route, dependency, or deployment remains.
- UI primitives follow the shadcn registry and Scrooner theme.
- Public pages remain server-rendered, indexable, canonical, and cached.
- All functional, accessibility, visual, SEO, redirect, and smoke gates pass.

## Out of scope

Database/formula changes, billing, admin, new investor features, a stock-page
information-architecture redesign during the port, a generic dashboard, and
dark mode.
