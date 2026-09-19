# Scrooner Frontend Guardrails

**Status: Living document — update this in the same pass as any change that
establishes, breaks, or fixes a frontend convention.** This is the single
source of truth for "how we build the frontend," ahead of any other design
doc when they conflict — `shadcn-system.md` is the original design direction
this codebase is implementing against; `10_Scrooner_Product_Design_Framework.md`
and `13_Scrooner_Scalable_Design_System.md` are historical/evidence docs from
before the 2026-09-05 single-Next.js-app consolidation and may describe a
retired architecture. This doc describes what's actually true today.

Whoever (human or agent) touches `apps/app` or `packages/design-system`
should read this first, and add to it — a rule, a pitfall, a new shared
component — the same day it's discovered, not as a follow-up.

---

## 1. Token architecture — one file, no exceptions

- All visual values live in `packages/design-system/src/tokens.css`
  (palette + semantic contract) and `primitives.css` (component classes
  built from those tokens). Nothing in `apps/app` should hardcode a raw hex
  color, a raw pixel radius, or a one-off shadow — reference a `--ds-*`
  token, or add one to `tokens.css` if the concept doesn't exist yet.
- **`@import "@scrooner/design-system";` belongs in exactly ONE file:
  `apps/app/app/globals.css`, which loads first in `app/layout.tsx`.**
  Never add this import to any other CSS file. A second `@import` doesn't
  error — it silently duplicates every shared rule later in the merged
  stylesheet than the first copy. Any override written in `globals.css`
  that shares a base rule's specificity (e.g. a page-specific class next to
  a `.ds-*` class on the same element) will silently lose to that later,
  redundant copy — invisible until you go looking at the compiled CSS byte
  for byte. See Postmortem #1 below; this exact bug shipped a dark-logo-on-
  dark-background page before it was caught.
- When something in the app needs a new shared surface tone, spacing value,
  or type size, add the token to `tokens.css`/`primitives.css` — don't
  invent a local one-off in an app-level CSS file that happens to look
  right today.

## 2. Color semantics — brand and financial meaning are never the same hue

- `--ds-color-action` / `--ds-color-action-hover` / `--ds-color-link` /
  `--ds-color-focus` are **navy** — buttons, links, focus rings, selected
  states, the brand mark. Nothing about a number going up or down.
- `--ds-color-positive` / `--ds-color-positive-strong` are **teal**,
  `--ds-color-negative` is **red** — reserved for an actual financial
  gain/loss or a genuinely positive/negative status (e.g. "active"). Never
  reach for these to mean "this is the primary action" just because they
  render agreeably.
- These were the same hex value until 2026-09-06 (a primary "Run Screen"
  button and a stock gain were, by construction, indistinguishable) — see
  `doc/learnings/` from that date. Don't reunify them.
- A background/border pairing that assumes "brand tint" and "positive tint"
  are interchangeable (`--surface-brand-subtle` vs `--surface-positive-subtle`)
  is a real bug, not a style nit — check which one a given box actually
  means before reusing a snippet that pairs them.

## 3. One component per concept — check before you invent markup

Before writing a new empty state, loading skeleton, badge, or metric
display inline in a page, check whether one already exists:

| Need | Component | Lives in |
|---|---|---|
| Up/down indicator (price change, metric delta) | `<Delta />` | `components/scrooner/Delta.tsx` |
| Ticker chip | `<TickerBadge />` | `components/scrooner/TickerBadge.tsx` |
| "Nothing to show" placeholder | `<EmptyState />` | `components/scrooner/EmptyState.tsx` |
| Loading placeholder for a data table | `<TableSkeleton />` | `components/scrooner/TableSkeleton.tsx` |
| ⌘K company search | `<SearchCommand />` | `components/scrooner/SearchCommand.tsx` |
| Stock page identity/price/actions header | `<StockHeader />` | `components/scrooner/StockHeader.tsx` |
| Generic status/alert banner (loading, error, success) | `<StatusPanel />` | `components/ui/StatusPanel.tsx` |
| Page title + description + optional trust line | `<PageHeader />` | `components/layout/PageHeader.tsx` |
| Section title + description inside a research page | `<ResearchSection />` | `components/company/ResearchSection.tsx` |

If a page's "no results" state doesn't fit `EmptyState`'s two shapes
(`bordered` standalone vs. nested-in-a-bordered-container), that's a signal
to extend `EmptyState` with a new prop — not to write a fourth ad hoc empty
state div. Same logic for any other row in this table. Before 2026-09-06
this table had three independently-invented empty-state patterns doing the
same job, one of which (the actual shared primitive, `.ds-empty-state`) had
zero real usages.

There is exactly **one** `BrandMark` (`components/ui/BrandMark.tsx`) — the
upward-trend-line-and-arrow mark. It was accidentally forked once (a second
copy lived in `components/public/BrandMark.tsx` with a different shape) and
the two surfaces of the product showed different logos depending on whether
you were signed in. Never add a second brand mark component; if the mark
needs a different size, use the `size` prop or a CSS custom-property
override on `--ds-brand-mark-size` (see `.hero-research-mark` in
`app/home.css` for the pattern), not a new component.

## 4. Icon sizing — two values, no more

Lucide icons render at **16px** by default, **18px** only for a lead icon
in a deliberately larger list (see the pricing page's feature checklist vs.
its plan-card lists). That's it — don't introduce a third size because it
"looked a little big" in one spot. The one documented exception is
`Delta`'s arrow, which scales with its own `sm`/`md` text size (11/13px)
because it's a typographic mark glued to a number, not page-chrome — see
the comment in `Delta.tsx` before assuming that's an oversight.

## 5. Buttons stay boring

Real count as of 2026-09-06 (`Button` component, counted per-tag, not
per-line — dense JSX files put multiple buttons on one line and a naive
`grep -v` will miscount): 33 buttons app-wide, only 10 default/primary, 15
ghost, 7 secondary, 1 destructive. Keep that ratio. A page that reaches for
`variant="primary"` (the default) for more than its one genuinely primary
action is very likely wrong — reach for `ghost`/`secondary` first.

## 6. Testing — every `components/scrooner/*` file gets a test

This directory holds the app's own reusable, cross-page components (as
opposed to `components/ui/`, which holds primitive adapters). Every file in
it should have a corresponding case in `components/scrooner/scrooner.test.tsx`
covering its real behavioral contract (not just "it renders") — the same
discipline `components/ui/ui.test.tsx` already holds primitives to. A
component built and shipped without a test here is a gap to close in the
same pass, not a follow-up.

## 7. Never fabricate a number or state the data doesn't support

This one is inherited from the product's own decision register
(`CLAUDE.md`), restated here because it bites at the display layer
specifically: don't invent a plausible-looking value, don't scale a raw
number by an assumed unit you haven't confirmed, and don't offer a UI
control (a chart period toggle, a "show more" button) that implies more
data exists than actually does. See the price-chart period-selector fix
(2026-09-06) and the segment-revenue unit-scaling fix from the same day —
both were "premium feel" bugs that turned out to be "the UI claimed
something the data didn't back up," not cosmetic issues.

## 8. Before shipping a CSS change, check the compiled output once — then look at it

`grep` the actual served `/_next/static/css/*.css` for the rule you just
wrote, not just the source file — dev-server HMR and a duplicate `@import`
have both silently served stale or duplicated CSS in this project's own
history (see postmortems). But grepping the compiled rule in isolation is
still not enough on its own — it missed a real invisible-button-text bug
because the *rule itself* looked correct; the bug was a *different* rule
winning the cascade. **Capture an actual screenshot before reporting a
visual fix as done:**

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --screenshot=<path>.png \
  --window-size=<w>,<h> --hide-scrollbars <url>
```

No Playwright/Puppeteer install needed — Chrome is already a real macOS
app. Do a clean rebuild first (`rm -rf .next`, restart the dev server) so
you're not looking at stale HMR output. This is not optional polish; two
rounds of "fixed" that turned out not to be, in the same session, is what
made this rule exist.

## 9. A component's color/behavior must never depend on its container

Never write a rule shaped like `.some-container a { color: ... }` or
`.some-container button { ... }` without checking whether a real shared
component (`.ds-button`, `.ds-badge`, `.ds-control`, etc.) could ever be
rendered inside that container. If it could, exclude it explicitly
(`.some-container a:not(.ds-button)`) — a shared component owns its own
visual contract unconditionally, regardless of what page or section drops
it in. See Postmortem #2 (2026-09-06): six different containers had this
exact latent bug; only one had actually failed visibly so far.

---

## 10. Two valid authoring patterns, both token-driven — don't force a rewrite just to unify syntax

Most pages compose semantic, BEM-ish classes (`.workspace-page`, `.public-nav`,
`.saved-screen-detail__header`) that resolve entirely through `--ds-*`
tokens — this is the original, dominant pattern (`app/company-research.css`,
`app/public-theme.css`, every CSS module under `components/`). Tailwind
utility classes directly in JSX plus the `Card`/`Button`/`Badge` primitives
are the other valid option (used briefly by the dashboard on 2026-09-19,
before it moved back to the BEM pattern the next day as part of #12's IA
fix — not because Tailwind-in-JSX was wrong, the dashboard just needed
different *content*, and it happened to get rewritten in the dominant
pattern that pass) — both resolve through the exact same tokens via
`globals.css`'s `@theme inline` block, so neither is "more correct" or "raw/
un-tokenized." Don't treat a page's choice of BEM-class vs. Tailwind-utility
authoring as a consistency bug on its own — the actual bar (semantic-token
values, boring buttons, tabular numbers, border>shadow, restrained radius)
is what `doc/design/shadcn-system.md` prescribes. New pages are free to use
either pattern; match whichever the page they extend already uses rather
than converting for its own sake.

## 11. Verify mobile with real device-metrics emulation, not `--window-size` alone

Confirmed again 2026-09-19: a plain `--headless --window-size=390,900`
screenshot does NOT reflow the page at that width in this Chrome build — it
renders desktop layout and crops/scales it, producing a false-positive
"content is cut off past the right edge" bug that doesn't exist at a real
390px viewport. Use CDP device-metrics emulation instead (open a target via
`PUT /json/new?<url>` on a `--remote-debugging-port`, connect its
`webSocketDebuggerUrl`, call `Emulation.setDeviceMetricsOverride({width,
height, deviceScaleFactor: 2, mobile: true})` before `Page.captureScreenshot`)
— see rule 8 above for the desktop screenshot command this supplements, not
replaces.

## 12. Every `/app` page has one job — don't reuse another page's component to fake progress on it

Each authenticated page has a distinct, non-overlapping intent. Before adding
content to one, name which of these it is — content that belongs to a
different intent goes on that page, not copied onto this one:

| Page | Intent | Must never contain |
|---|---|---|
| `/app` (Dashboard) | The signed-in visitor's home base: a way back to research they already saved, plus two doors to the other two tools. | A query composer. It is not a smaller Create Screen page. |
| `/app/screens/new` (Create screen) | The one real interpret-and-run flow (`NaturalQueryPanel`). | A second, independent copy of this flow anywhere else — always prefill-and-redirect into this page (`?q=...&run=1`) instead of re-implementing the request. |
| `/app/screens` (Saved screens) | Manage (rename/delete/rerun) screens already saved. | A creation flow — it lists and acts on existing screens only. |
| `/explore` (public) | The entry point to *discovery*: popular screens, sectors, industries — "what could I look at" before you know what you want. | Personal/account data (saved screens, activity) — that's Dashboard's job, and this page is public/unauthenticated. |
| `/stocks` (public) | The full A-Z company directory — "I know roughly what I want to find, let me scan for it." Distinct from `/explore`: a flat list, not a curated browse surface. | Curated/grouped content (popular screens, sector cards) — that's `/explore`'s job. |

This table exists because the Dashboard was rebuilt 2026-09-20 to directly
embed a shrunk copy of the Create Screen page's own search card (serif
textarea, examples, the works) — it read as "the same feature wearing
different clothes" rather than two different tools, and using the exact
same visual language for two different intents will always read that way to
a user, regardless of how clean either page is in isolation. Fixed by
giving Dashboard its own distinct content (recent activity + two compact
links out), and by splitting what used to be one page into two real ones:
`/explore` (curated discovery — popular screens, sector/industry cards) and
`/stocks` (the plain full directory, upgraded from a bare unstyled `<ul>` to
a real A-Z-jump-nav'd list of all ~6,000 covered companies). Before adding a
new authenticated or discovery-adjacent page, add a row to this table first
— if its intent already matches an existing row, it probably shouldn't be a
new page.

## Postmortems (append here, most recent first)

### 2026-09-19 — Finished the app-shell top-nav migration, cleaned up the CSS it orphaned

A prior pass this session had already converted `AppShell`/`AppNavigation`
from a left-sidebar workspace layout to a horizontal top-nav (matching the
public site's own header shape), added a real `Card` primitive
(`components/ui/Card.tsx`), unified the public/app sign-in control into one
`HeaderAuthAction`, and rewritten the dashboard (`app/app/page.tsx`) on
Tailwind utilities + `Card`/`Button`/`Badge` — all uncommitted, mid-flight.
Verified it end-to-end (`tsc`, full Vitest suite, `next build --webpack`,
real screenshots at desktop and true mobile widths across home/pricing/
login/stock/methodology/about/design-system) rather than assuming it still
worked after a context reset. Found and removed the one real leftover: the
dashboard rewrite orphaned six CSS rules in `app/app/workspace.css`
(`.workspace-hero`, `.workspace-section`, `.workspace-section__heading`,
`.workspace-action-grid`, `.workspace-action*`, `.workspace-note`) that no
`.tsx` file referenced anymore — removed them and their mobile media-query
overrides, keeping `.workspace-page`/`.workspace-eyebrow`/`.workspace-content`/
`.workspace-empty`/`.workspace-loading`, which `app/app/error.tsx`,
`app/app/loading.tsx`, and the watchlists/alerts placeholder pages still use.
No visual regression found in the parts already migrated; see rule 10 above
for why the rest of the app's different (but equally token-driven) CSS
authoring style is not itself a bug to fix.



### 2026-09-06 — A generic `<a>` color rule silently hijacked `.ds-button`'s text color, making a primary button's text invisible

**Symptom:** the pricing page's "Create a free account" button rendered as
a solid navy rectangle with **no visible text at all**. Found by finally
capturing a real screenshot (see "verify with a screenshot" note below) —
grepping the compiled CSS for `.ds-button--primary` alone had shown the
correct, unremarkable rule and gave false confidence nothing was wrong.

**Root cause:** `.public-prose a { color: var(--ds-color-link); }` — a
rule meant for ordinary inline text links inside prose content — is a
*descendant* selector (specificity 0,1,1). `.ds-button--primary`'s own
`color` rule is a single class selector (0,1,0). Any `<Button asChild>`
rendered as a `<Link>` inside `.public-prose` (i.e. inside any page built
on `<PublicPage>`, which is most of the public site) had its text color
overridden to link-navy *regardless of source order*, because 0,1,1 always
beats 0,1,0. Link-navy text on the button's own navy background is exactly
invisible. Five more near-identical patterns existed elsewhere
(`.auth-card__links a`, `.research-table a`, `.public-links a`,
`.footer-links a`, `.screener-path a`) — none had visibly failed yet only
because their surrounding backgrounds happened not to match, not because
they were actually safe.

**Fix:** added `:not(.ds-button)` to every one of those six selectors. A
`.ds-button`-classed element must never have its color decided by whatever
container it happens to be dropped into — the component owns its own
color contract unconditionally.

**Generalizable lesson:** this is a *different* bug class from the
duplicate-`@import` one above — that was about cascade *order*, this is
about cascade *specificity* — but the same category of mistake: an ambient,
container-scoped style rule reaching into a self-contained component and
winning a fight it was never intended to be in. Any time you write a rule
shaped like `.container a { color: ... }` or `.container button { ... }`,
ask whether a real shared component (`.ds-button`, `.ds-badge`, etc.) could
ever land inside that container — if yes, exclude it explicitly.

### 2026-09-06 — Duplicate `@import "@scrooner/design-system"` silently overrode a same-specificity page override

**Symptom:** the auth pages' brand panel showed the brand mark in navy
against a navy background (functionally invisible) despite an explicit
`.auth-shell__mark { color: var(--ds-color-text-inverse); }` rule in
`globals.css` that should have won.

**Root cause:** `public-theme.css` *also* had `@import "@scrooner/design-system";`
at its top. `app/layout.tsx` loads `globals.css` first, then `public-theme.css`
— so the design system's rules (including `.ds-brand-mark`'s default navy
`color`) were physically duplicated later in the final merged stylesheet
than `globals.css`'s own `.auth-shell__mark` override. Same specificity (two
single-class selectors on the same element), tie broken by source order —
and the later, redundant copy won.

**Fix:** removed the second `@import` from `public-theme.css`; it's now
sourced exactly once, from `globals.css`. Confirmed via the compiled
`/_next/static/css/*.css` output that `.ds-brand-mark` and `.ds-button--primary`
each appear exactly once (down from two) outside the legitimate
`@media (forced-colors: active)` accessibility override, which is a real,
separate, intentional second definition and not part of this bug.

**Generalizable lesson:** a shared stylesheet must be imported from exactly
one place in the app's CSS entry chain. If you're adding a new top-level
CSS file to `app/layout.tsx`'s import list and it needs design-system
tokens, it already has them — tokens are `:root`-scoped custom properties,
visible everywhere once `globals.css` has loaded them once. It never needs
its own `@import`.
