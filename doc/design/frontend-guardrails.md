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

## 1a. Theming — one light theme today, and exactly where a second one would plug in

**Current state: Scrooner ships a single, light theme. There is no dark
mode, no theme toggle, and no per-user theme preference anywhere in
`apps/app` today.** This is a fact to verify against the code before
assuming otherwise, not a permanent constraint — but as of 2026-09-20
nothing in this repo reads `prefers-color-scheme` or a `data-theme`
attribute for `apps/app`'s own pages.

The plumbing that *would* carry a second theme already exists in two
layers, and understanding both is what "theming" means in this codebase:

1. **`packages/design-system/src/tokens.css`** — every real value (color,
   spacing, radius, shadow, type) is a `--ds-*` custom property on `:root`.
   This is the ONLY place a color/size value is allowed to be defined. A
   theme, if one is ever added, is a second block of `--ds-*`
   redefinitions scoped to a selector (`[data-theme="dark"]` or a
   `prefers-color-scheme: dark` media query) — never a second copy of
   component CSS. Every component (`.ds-button`, `.stock-hero`, etc.)
   already reads tokens, never a hardcoded value (rule 1), so a theme
   switch only has to touch this one file to reach the whole app.
2. **`apps/app/app/globals.css`'s `@theme inline` block + `:root`
   "compatibility alias" block** — bridges Tailwind's utility classes
   (`bg-muted`, `text-primary`, the shadcn-generated primitives) to the
   real `--ds-*` tokens, and gives a handful of legacy short names
   (`--surface-canvas`, `--text-primary`, `--brand-700`, etc.) still used
   by some older app-level CSS. These are aliases, never a second source
   of truth — a color's real value is set exactly once, in `tokens.css`;
   this block only renames it for Tailwind/legacy call sites. See rule 1's
   note on the two dead alias values that once diverged from the real
   token (`--muted`/`--accent`) — that bug is exactly what happens when an
   alias block is treated as a place to *set* a value instead of just
   forward one.

If dark mode (or any second theme) is ever built: add the redefinition
block to `tokens.css` under the appropriate selector, leave every
component and every app-level CSS file untouched, and toggle the
selector/attribute from wherever the app reads the user's preference.
Nothing in `apps/app`'s component or page CSS should need to change for
that to work — if a component *does* need a change to support a new
theme, that component was hardcoding a raw value somewhere and rule 1 was
violated; fix the component to read a token instead of special-casing the
new theme.

## 1b. Scaffolding — where a new file goes

`components/` is organized by **who else can use it**, not by page or
feature name alone. Check this table before creating a new component file
— putting a component in the wrong folder is how the duplicate-empty-state
and duplicate-`BrandMark` bugs in rule 3 happened:

| Folder | What belongs here | Example |
|---|---|---|
| `components/ui/` | Generic shadcn-derived primitives — no Scrooner-specific business logic, would make sense in any product | `Button`, `Badge`, `Card`, `Dialog`, `Popover`, `Field`, `IconButton`, `StatusPanel`, `Tooltip`, `Surface`, `BrandMark` |
| `components/scrooner/` | Cross-page business/domain components — Scrooner-specific meaning, but reusable across more than one feature area | `Delta` (price/metric change), `TickerBadge`, `EmptyState`, `TableSkeleton`, `SearchCommand`, `StockHeader` |
| `components/layout/` | Page shells and chrome — arrange other components, own no business data themselves | `AppShell`, `AppPageLayout`, `AppSidebar`, `PageHeader` |
| `components/public/` | Public-site-specific components not used inside `/app` | `PublicHeader`, `PublicFooter`, `PublicPage`, `AccountMenu`, `CompanySearch`, `HeaderAuthAction`, `DashboardNavLink` |
| `components/auth/` | Login/signup/OAuth screens | `AuthForm`, `AuthShell`, `OAuthButtons` |
| `components/company/` | Stock/company-page-only components, not reused elsewhere | `FinancialTable`, `MetricGrid`, `PriceChart`, `ResearchSection`, `StockSectionNav` |
| `components/screener/` | Screener/create-screen-only components | `NaturalQueryPanel`, `ScreenerClient`, `InterpretationTable` |
| `components/saved-screens/` | Saved-screens feature only | `SaveScreenButton`, `SavedScreensClient`, `SavedScreenDetailClient` |

The test for which folder a new component belongs in: **would a second,
unrelated feature area plausibly import this?** If yes and it's a raw
primitive with no Scrooner meaning → `ui/`. If yes and it carries Scrooner
domain meaning (a price, a ticker, a research concept) → `scrooner/`. If
no, it's specific to one page/feature → that feature's own folder, named
after the feature, not the page route. Don't create a new top-level
folder for a single component — every feature folder above started with
one file and grew; a one-off component that doesn't fit an existing
feature folder is a signal to check rule 3's table first (it may already
exist), not to invent a new folder.

CSS follows the same page-vs-shared split as components: shared visual
rules live in `packages/design-system` (rule 1); page-specific layout
rules live in a CSS file next to the page or route segment it styles
(`app/company-research.css`, `app/app/workspace.css`, `app/pricing.css`,
`app/home.css`) and are never imported by more than the pages that need
them — a page-scoped stylesheet reaching into another page's classes
(rather than a shared component) is exactly the class-name-collision shape
rule 8's postmortems already document.

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

## 13. `.main-content` + `AppPageLayout` is the one shell for every non-table `/app` page

Every `/app` page that isn't a wide data table shares exactly one outer
container (`.main-content`, 1040px) and, inside it, the exact same
content+sidebar frame (`<AppPageLayout>`, `components/layout/AppPageLayout.tsx`)
wrapping a shared `<AppSidebar>` (`components/layout/AppSidebar.tsx`).
That's it — a page's actual content (a list, a single form, a card) sizes
itself *within* that shared main column; it never resizes the page's own
outer container to fit itself. Concretely:

| Page | Uses `AppPageLayout`? |
|---|---|
| `/app` Dashboard | Yes |
| `/app/account` | Yes |
| `/app/account/update-password` | Yes — the form itself stays a narrow 460px card centered in the main column, the *page* is still 1040 |
| `/app/screens/new/save` (save-screen confirmation) | Yes — same pattern, card capped at 620px |
| `/app/screens` (Saved Screens) | Yes |
| `/app/alerts`, `/app/watchlists` | Yes |
| `/app/screens/new` (Create screen) | **No** — already has its own two-column composer+examples layout; adding a second, different sidebar would be a third competing layout, not a fix |
| `/app/screens/new/raw` (results), `/app/screens/[slug]` (saved-screen detail) | **No** — wide data tables, plus a Premium/popular-screens promo next to the exact results a user is trying to read is the wrong moment for it |
| Public pages (`/stocks/{ticker}`, `/explore`, etc.) | **No** — different nav/ownership entirely |

This replaced an earlier, worse answer to the same problem (2026-09-20,
same day): first the fix was "3 container-width tiers, no others" — better
than 5 arbitrary widths, but still meant the single-form pages (password
update, save-confirmation) rendered as an isolated narrow column with
nothing else on the page. Correctly called out live: a real product doesn't
strand a settings page by itself when it could be promoting Premium or a
popular screen right next to it, the same way Dashboard already did. Fixed
by extracting Dashboard's sidebar into `AppSidebar` (adds a Premium→
`/pricing` promo card and 2-3 short example-screen links, on top of the nav
links already there) and a thin `AppPageLayout` wrapper, then adopting both
on every page in the "Yes" rows above — collapsing "3 width tiers" down to
one shared shell, since the form-width cases turn out to just be a
`max-width` on the *card*, not a different page container at all.

Before giving a new `/app` page its own layout: if it's not a wide table
and not Create Screen's own composer, it almost certainly wants
`<AppPageLayout>`, not a bespoke width.

## 13a. A "wide table" exemption from the layout rules is not an exemption from every other rule

Found live 2026-09-20, on the results page specifically (excluded from
`AppPageLayout` per §13, correctly): three controls that should have used
shared components didn't, just because the page as a whole was treated as
"the exception" and never got the same scrutiny as everything else:

- The "Industry" toggle and "Export CSV" toolbar buttons were bare
  `<button>` elements styled only via a page-scoped `.results-toolbar >
  button` selector — not `<Button variant="ghost"/"secondary">`. They
  happened to *look* like buttons because the CSS re-implemented padding/
  border/hover from scratch, but they weren't the shared component, so a
  future global button change (spacing, focus ring, disabled state) would
  silently skip them.
- "Edit columns" was a native `<details>/<summary>` dropdown, a different
  interaction mechanism from every other floating menu in the app (Account
  menu uses the controlled `Popover` component). Converted to
  `Popover` + a `Button` trigger — now it gets the same Escape-to-close,
  click-outside, and focus-restore behavior as the Account menu for free,
  instead of whatever `<details>` happens to do.
- `SaveScreenButton` passed `variant="secondary"` in its own source, then a
  page-scoped CSS rule (`.save-screen-control .ds-button`) forced it to
  render as if it were `variant="primary"` (navy fill) anyway. Fixed by
  just passing `variant="primary"` and deleting the override — the same
  visual result, but now truthful: reading the JSX tells you what the
  button actually looks like.

Generalizable check: a page being the documented exception to a *layout*
rule (no sidebar, wider width) doesn't make it exempt from *component*
rules. Grep for `<button ` and `<details` with no `Button`/`Popover`
import nearby on any page that's been carved out as a special case —
that's exactly where this kind of drift hides, because it stops getting
compared against the pages that share a common wrapper.

## 14. Reuse `PageHeader` and `EmptyState` — don't hand-roll either

Every standard-width `/app` page's title block uses the shared `PageHeader`
component (`components/layout/PageHeader.tsx`); every "nothing here yet"
state uses the shared `EmptyState` component
(`components/scrooner/EmptyState.tsx`, already documented in table form in
§3 above). Found live 2026-09-20: Dashboard, Alerts, and Watchlists had each
hand-rolled their own header markup and/or empty-state `<div>`/`<p>` instead
of reusing either component — not because the components didn't exist, but
because each page was built independently without checking first. Create
Screen and Saved-screen-detail are legitimate exceptions for the header
(a composer card title and a back-link+action-buttons bar are genuinely
different shapes PageHeader doesn't support) — but a page hand-rolling its
*empty* state has no equivalent excuse; `EmptyState`'s `bordered`/`icon`/
`action` props already cover every case seen so far.

## 15. Type scale is discrete — snap to it, `clamp()` fluid ranges excepted

`--ds-font-size-*` defines exactly these steps: 11, 12, 13, 14, 15, 16, 18,
20, 24, 30, 36, 48, 64, 88 (px-equivalent). A literal `font-size` value
outside this list (`13.5px`, `10.5px`, `12.5px`, a bare `10px`/`9px` used as
if it were a deliberate step) is drift, not a real design decision — nobody
sits down and picks 13.5px on purpose. Found and fixed six instances live
2026-09-20 (three introduced earlier the same day building the dashboard
sidebar and `/explore`, three pre-existing on the homepage and the stock
page's key-metrics grid) by snapping each to its nearest real step. The one
legitimate exception: a `clamp(26px, 3.4vw, 34px)`-style fluid range for
responsive headline sizing has continuous, computed endpoints by design —
those aren't required to land on scale steps. A handful of pre-existing
sub-11px sizes in the stock page's dense financial tables (9-10px table
headers, chart axis labels) were checked and deliberately left alone — real
data-density tables trading off legibility for column count is a considered
exception this project has tuned carefully over many sessions, not
accidental drift, and forcing them to 11px would visibly worsen those
tables for no real consistency gain. Grep for the pattern before trusting a
page looks consistent: `grep -rhoE "font-size:\s*[0-9]+(\.[0-9]+)?px" | sort
-u` against the full token list surfaces every literal outside it in one
pass.

## 16. A descendant CSS selector meant for one child can silently size an unrelated nested component

Found live 2026-09-20, on the stock page's price chart: `.price-chart svg
{ width: 100%; height: 280px; }` was written to size the chart's own line
graph, but `.price-chart svg` matches *any* `<svg>` anywhere inside
`.price-chart` — including the tiny 11×11 `Delta` arrow icon rendered a few
DOM levels up in the same card's toolbar (`$334.88 ↑ +10.17%`). That icon's
own `width="11" height="11"` HTML attributes lost to the CSS rule, stretching
a small Lucide arrow-up glyph to fill the entire chart area — a huge, bold,
unmistakably-arrow-shaped icon sitting where a price line should be. Looked
exactly like "a big arrow" because that's literally what it was: the real
line-chart `<polyline>` was rendering correctly the whole time, just
underneath/beside this oversized, mis-scoped icon.

Root cause was purely a selector-scope mistake, not a rendering engine
quirk — `document.querySelector('.price-chart svg')` in isolation looks
fine (it exists, has the right viewBox), so the compiled-CSS-grep habit
from rule #8 wasn't enough here; the bug only shows up once you check
*which* elements a broad descendant selector actually matches, not just
whether the rule you wrote exists. Fixed by scoping to `.price-chart__plot
svg` (the wrapper that only ever contains the actual chart canvas) instead
of `.price-chart svg` (the whole card, which also contains the toolbar's
icon). General check: before writing `.card-class svg` or `.card-class
button` to size/style "the one thing inside," ask whether any shared
component (an icon, a `Delta`, a `Badge`) could also render inside that
same card elsewhere — if yes, scope to the specific wrapper, not the whole
card.

## 17. Two independent number formatters for the same page will disagree on precision

`lib/company/format.ts`'s `fmtNum()` is documented as *the* shared
formatter so "the metric grid, statement tables, and any future page share
one formatting contract" — but `FinancialTable.tsx` had its own separate
`amount()` function instead, and the two disagreed: `fmtNum` used 2 decimal
places for thousand/million/billion/trillion scaling uniformly, while
`amount()` used 2 for trillion but only 1 for billion/million (inconsistent
even with *itself*), and used `toLocaleString(..., { maximumFractionDigits:
2 })` with no minimum for small values (per-share numbers like EPS) — which
silently drops trailing zeros, so a real value of exactly 2.40 rendered as
"2.4" while every other row in the same column showed 2 decimals. Both
bugs were only visible by reading an actual rendered table row next to
its neighbors ("2.4" among "0.97 / 1.65 / 1.57 / 1.84"), not from the code
in isolation. Fixed by aligning `amount()`'s precision to match `fmtNum()`
exactly (2 decimals throughout, `minimumFractionDigits` set) — kept as a
separate function rather than switching call sites to `fmtNum()` directly,
since financial statements need the parens-for-negative convention
(`(29.6B)`) that `fmtNum()` doesn't have. When a page has more than one
number formatter, their precision needs to match even if their other
behavior legitimately differs — check by reading real adjacent output, not
by comparing function signatures.

## 18. Public pages inherit a global serif `h1`/`h2` default that `/app` explicitly opts out of — new public pages don't get that opt-out for free

`globals.css` has a bare, unscoped `h1, h2 { font-family: var(--font-serif)
}` — every heading site-wide is serif by default. `/app` pages look sans
only because `.app-shell .page-intro h1, .app-shell .page-intro h2 { ... }`
explicitly overrides it back to sans, scoped to `.app-shell`. The stock
page (`.stock-hero h1`, `.research-section__header h2`) is a *public* page
(outside `.app-shell`), so it never got an equivalent override and rendered
large serif headings by the same default About/Methodology/Home use on
purpose. Reported live 2026-09-20 as "why is the h1 so big, why isn't it
standard" — correct call: the stock page is a data tool, not editorial
content, and reads better matching `/app`'s own type voice. Fixed by giving
`.stock-hero h1` and `.research-section__header h2` explicit sans overrides
(matching Dashboard's own h1 size/weight, not just "smaller") rather than
leaving the page half-migrated with a sans h1 sitting above serif h2
section headers, which would have been a new, self-inflicted
inconsistency. Home/About/Methodology/Pricing keep the serif default
untouched — that split (editorial content vs. tool pages) is the
correct, intentional half of this default, not the half that was wrong.

## 19. "Snap to the scale" and "use the token, not the matching number" are two different fixes — both are needed

Rule 15's original sweep (2026-09-20) fixed every literal `font-size` whose
*value* didn't match a token step. That sweep's own grep pattern
(`font-size:\s*[0-9]+(\.[0-9]+)?px`) missed some real drift because it was
run before a few off-scale values existed yet in files touched later the
same session, and a second, independent pass (also 2026-09-20, prompted
directly by "core typography... use these only, no hardcoding") found six
more: `.price-chart__toolbar strong` (19px), `.natural-query-heading h1`
(22px — a genuine duplicate page-title style that should have matched
`.page-intro h1`'s `clamp(28px, 4vw, 36px)` all along, not just landed on
the nearest flat number), the global `h2`/`h3` element defaults (23px/18px
in `globals.css`), `.stock-hero__price strong`'s mobile override (34px),
`.pricing-plan__price strong` (40px), and `.hero-wordmark .name`'s
narrowest mobile override (44px). Each was snapped to its nearest real step
(preferring "one step down from the desktop/clamp value" over pure numeric
distance when the literal was clearly a freehand mobile shrink, e.g.
44px→36px and 40px→36px rather than a nearer-by-distance value that isn't
actually one scale step away).

Separately, and just as real a form of "hardcoding": dozens of *already
on-scale* literals (`font-size: 13px`, `font-weight: 600`, etc.) were still
spelled as bare numbers rather than `var(--ds-font-size-13)` /
`var(--ds-font-weight-semibold)` — visually correct, but not actually
wired to the token source, so a future token-scale change wouldn't reach
them and a linter can't tell them apart from real drift. Converted every
remaining bare literal that exactly matches a token value to its `var()`
form, project-wide, via a value-preserving sed pass (`font-size: 600` and
`font-weight: 600` are bijective with their token names, so this is a
zero-visual-risk mechanical substitution, not a design decision — verified
with a full rebuild + screenshot pass after, not assumed safe from the
diff alone). After both passes: **zero** raw `font-weight` literals remain
anywhere in `app`/`components`, and the only remaining raw `font-size`
literals are the six pre-existing sub-11px dense-table values rule 15
already named and deliberately excepted (9px/10px, no token exists that
low). Re-run both greps after any future typography change:
`grep -rhoE "font-(size|weight):\s*[0-9]" app components --include="*.css"
| sort | uniq -c` — any row naming a value other than 9/10 (font-size) is
new drift to fix, not a false positive to explain away.

## 20. A row-level highlight class loses to a column-level sticky rule at higher specificity — scope the highlight to match

Found live 2026-09-20 adding a highlighted "this is the current company" row
to the stock page's peer-comparison table (`.research-table__self`,
prompted by a Screener.in comparison — see
`doc/learnings/2026-09-20-screener-in-stock-page-comparison.md`). The rule
`.research-table th:first-child { position: sticky; left: 0; background:
var(--ds-color-bg-surface); }` (needed so the company-name column stays
visible while a wide table scrolls horizontally) has specificity `(0,2,1)`.
A naive `.research-table__self th { background: ... }` is only `(0,1,1)` —
lower, so it silently lost on exactly the one cell (the sticky name column)
where the highlight mattered most, even though every other cell in the same
row highlighted correctly. Caught by an actual rendered screenshot, not by
reading the CSS (the two rules don't look like they conflict without knowing
Chrome's specificity math) — same discipline as rule 8. Fixed with an
explicit `.research-table__self th:first-child` rule at matching
specificity `(0,2,1)`, so source order (mine comes later) decides the tie.
**Generalizable check: before adding a row-level (or any partial-row)
highlight class to a table that also has a sticky/pinned column, grep for
that column's own rule's selector shape — if it's `.table th:first-child`
or similar, the new class needs an explicit `:first-child` (or matching)
companion rule, not just a bare `.new-class th`.** `FinancialTable`'s own
`.hl` class was already safe here because it's applied per-`<td>`, not
per-`<tr>`, so it never had to fight the sticky-column rule in the first
place — the peer table's row-level approach is what exposed this.

## 21. A `position: fixed; inset: 0` overlay rendered inside a sticky ancestor can silently lay out at the ancestor's own height, not the viewport's

Found live 2026-09-21 auditing the shared `Dialog` component (used by the
⌘K search command and by `SavedScreensClient`'s confirm dialogs) for a
"make these shadcn components premium" pass. Reading `.ds-dialog-backdrop`'s
CSS looked entirely correct (`position: fixed; inset: 0; display: grid;
place-items: center`), and it would have been easy to conclude the component
was fine from source alone. Only a direct `getBoundingClientRect()` check
(via a real headless-Chrome CDP session — see the standing rule on verifying
visual changes with a screenshot, extended here to "or a live DOM
measurement when a screenshot alone doesn't explain what's wrong") showed
the backdrop's actual rendered box was `1440×64` — exactly the sticky
header's own height — instead of the full viewport. The dialog rendered
pinned to the top-right corner with no visible dimming below the header,
because `Dialog` renders in place inside the page's React tree, nested
inside the sticky `<header>`, rather than escaping it.

Root cause was not fully isolated (no ancestor had `transform`/`filter`/
`will-change` — the usual textbook cause of a fixed-position element's
containing block changing — and the only `overflow: hidden` in the chain
was `<body>`, which `Dialog` itself deliberately sets while open to lock
background scroll, a correct and unrelated pattern). Rather than chase the
exact browser-engine interaction further, fixed it the way any full-viewport
modal should be built regardless of cause: **`createPortal` it to
`document.body`**, so it can never inherit a layout quirk from wherever it
happens to be mounted in the component tree. This is the standard, textbook
answer for "a fixed-position full-screen overlay behaves wrong depending on
where it's rendered" — reach for it directly next time this class of bug
shows up, rather than re-deriving the root cause from scratch. `Popover`
does not have this problem and needs no portal: it's `position: absolute`,
anchored to its own trigger's positioning context by design, never meant to
fill the viewport.

**Generalizable check: any component using `position: fixed; inset: 0` (a
full-viewport overlay — dialogs, drawers, full-screen loading states) should
be portaled to `document.body`, not rendered in place** — especially in this
app, where every page has a `position: sticky` header. A `position: absolute`
component anchored to its trigger (popovers, dropdowns, tooltips) does not
need this and should stay in place, since portaling would break its
anchor-relative math for no benefit.

## 22. Never name a custom CSS class after a Tailwind utility

Found live 2026-09-26: `.overline` (the small mono "INVESTOR SNAPSHOT" label on the stock page) rendered with a line drawn above the text, because Tailwind v4 is imported globally and ships a utility literally called `.overline` (`text-decoration: overline`). Our own rule never set `text-decoration`, so the utility silently applied — invisible in source review, obvious only in a rendered screenshot, then confirmed via `getComputedStyle().textDecoration`. Renamed to `.section-label`. **Before adding a bare class name, check it isn't a Tailwind utility** (`underline`, `overline`, `truncate`, `container`, `hidden`, `block`, `flex`, `grid`, `static`, `fixed`, `sticky`, `italic`, `border`, `shadow`, `ring`, `blur`, `visible`, `invisible`, `sr-only`...) — prefer BEM-style prefixed names (`.stock-hero__ticker`).

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
