# Frontend component-system audit — 2026-08-29

> **Scope:** every component under `apps/site/src/components`,
> `apps/app/components`, and every shared primitive under
> `packages/design-system/src`. This audit covers reuse boundaries, interaction
> states, accessibility, responsive behavior, visual consistency, and runtime
> cost. It does not treat a passing build as proof of good UX.

## Executive finding

Scrooner has a shared token layer, but it does **not yet have a consistently
high-quality component system**. The earlier audit over-weighted code reuse,
accessibility mechanics, and build correctness. Those are necessary gates, but
they do not prove that a control has the right hierarchy, density, shape,
label, or relationship to nearby content.

The clearest example was the homepage: company shortcuts used the generic
boxed chip treatment and read as a wall of oversized buttons. Their detached
“Or analyse” label, uneven wrap, ticker treatment, and proximity to an
oversized search control weakened the primary search task. That surface passed
the geometry checks but was still visually below the required bar.

That gap causes the visible defects:

- the homepage company search carried a redundant submit button and its hero
  results floated over the content below it;
- saved-screen dialogs have no shared Escape, focus-trap, focus-return, or
  backdrop behavior;
- the save-screen popover can escape a narrow viewport and has no dismiss
  contract;
- the app navigation always labels Screener as current, even on other routes;
- raw buttons and controls acquire different heights, focus treatments, and
  loading behavior depending on the feature stylesheet; and
- the two largest workflow components contain presentation, network state,
  validation, focus management, and multiple subviews in single files.

## Audit method

1. Enumerated all 20 production component files and the four shared CSS
   sources.
2. Traced every interactive element (`button`, `input`, `select`, `textarea`,
   dialog role, and disclosure) to its owning component.
3. Reviewed every component against six separate gates: purpose and hierarchy,
   visual composition, complete interaction states, accessibility, responsive
   behavior, and reuse/API quality.
4. Rendered the public homepage at 1440×1100 and 390×844. The desktop render
   confirmed the unnecessary View action; the narrow render exposed shared
   header, hero, quick-pick, and footer pressure that must be verified after
   shell changes.
5. Used existing unit tests, Astro diagnostics, and production builds only as
   regression gates, not as substitutes for the component review.

## Visual component scorecard

Each production component is graded separately. “Pass” means the rendered
component is ready to ship, not merely that its markup or tests are valid.

| Family | Visual finding | State finding | Verdict |
|---|---|---|---|
| Primary/secondary/destructive buttons | Shared height was sound, but the treatment was flat and generic; secondary hover had too little affordance. | Focus and disabled existed; active, busy, and consistent elevation feedback were incomplete. | **Reworked in this pass**: tighter radius/padding, distinct hover elevation/background, active press, busy cursor, and disabled normalization. |
| Ghost/text actions | Ghost buttons and feature-local `.text-button` controls compete. | Keyboard support exists, but hit area and state styling differ by feature. | **Needs migration**: one TextButton/ghost contract; remove feature-local copies. |
| Icon actions | Shared CSS exists, while Screener still uses a local `.icon-button`. | Labels exist in inspected consumers; destructive and pressed states are inconsistent. | **Needs migration** to one typed IconButton. |
| Homepage company shortcuts | Looked like large secondary buttons even though they are discovery links; wrap and label grouping were weak. | Link semantics were correct. | **Reworked in this pass** as compact text links with quiet tickers and underline affordance. |
| Hero company search | Search dominated the page and its 72px height made nearby links feel like a second control bar. | Combobox keyboard behavior is strong; loading and empty states exist. | **Reworked in this pass** to 60px with calmer radius/border and a 720px task width. |
| Header search | Appropriate compact density. | Needs visual review with populated, loading, empty, recent, and long-name results—not only closed state. | **Conditional pass**. |
| Fields/selects/textareas | Shared Field semantics now exist, but feature CSS still produces multiple shapes and label systems. | Error semantics improved; read-only, disabled, success, prefix/suffix, and long-help specimens are absent. | **Incomplete**. |
| Chips/badges | Badges are appropriately compact; `.ds-chip` is too generic to represent filters, links, and removable selections equally well. | No selected/removable contract. | **Split required**: LinkChip, FilterChip, removable Tag must not share one ambiguous API. |
| Navigation | Active route behavior is fixed; public and app navigation have different density logic. | Keyboard semantics are sound; overflow behavior is intentional. | **Conditional pass**, pending 320px and long-label visual review. |
| Cards/surfaces | Borders and elevation are consistent but too many feature panels use the same visual weight, weakening hierarchy. | Static states are fine. | **Needs hierarchy pass**: distinguish page section, interactive card, inset panel, and modal. |
| Dialog/popover | Shared behavior is now materially stronger. | Escape, focus lifecycle, outside/backdrop dismissal, and narrow viewport containment exist. | **Functional pass; visual review still required** for destructive, long-copy, validation, and mobile keyboard states. |
| Tables | Internal scrolling prevents page overflow. | Dense row actions and narrow-column prioritization remain feature-specific. | **Incomplete**: define desktop density and mobile priority per table. |
| Loading/empty/error states | StatusPanel provides a base, but icons, action buttons, and vertical rhythm vary. | Live-region behavior is present. | **Needs consolidation** and full catalog coverage. |

## Button inventory and decision rules

Buttons must represent actions. Navigation and company discovery remain links;
filter values use chips; status uses badges. Visual resemblance is not enough
reason to force them through one component.

| Current source | Intended role | Decision |
|---|---|---|
| `.ds-button` / React `Button` | Primary, secondary, ghost, destructive actions | Canonical action control. |
| Homepage `.company-chip` anchors | Company discovery navigation | Keep as links and style as compact discovery links, not buttons. |
| Natural-query example buttons | Run a prefilled query | Create an ExampleCard action; these need content hierarchy, not generic button chrome. |
| Candidate-choice buttons | Resolve one ambiguity | Create/select a choice-list control with selected and focus states. |
| `.text-button` retries | Inline recovery action | Migrate to small ghost Button or a dedicated TextButton with a 44px target. |
| Screener `.reference-button` | Apply a saved template | Treat as interactive cards with title, description, hover, focus, and pressed feedback. |
| Screener `.icon-button` | Remove a condition | Migrate to typed IconButton; destructive semantics and accessible name required. |
| `.add-condition` | Add a filter row | Migrate to secondary Button with a leading plus icon. |
| Navigation sign-out button | Navigation-level account action | Use a nav-action component; do not make it visually primary. |

## Shared design-system audit

| Primitive | Current quality | Finding | Required action |
|---|---|---|---|
| Tokens | Strong | One semantic source is used by both runtimes. Compatibility aliases remain extensive. | Keep canonical; retire aliases as components migrate. |
| Foundation | Strong | Global box sizing, focus, selection, reduced motion, contrast, and forced colors are present. | Add reusable scroll-lock behavior through Dialog, not global feature CSS. |
| Button | Good base | Typed variants exist, but no loading contract, icon-only contract, or link-button adapter. Feature code adds legacy classes back onto it. | Add busy/icon semantics; stop mixing `primary-button`/`secondary-button` with `Button`. |
| Badge | Good | Small, typed, semantic tones; no defect found. | Keep; add removable behavior only as a separate Chip component. |
| Surface | Too narrow | Hard-coded to a `div`; semantic cards/sections require wrappers or duplicate classes. | Make polymorphism explicit or provide Card/Section adapters. |
| StatusPanel | Good base | Live-region behavior is thoughtful, but glyph and action layout are fixed and raw actions vary. | Accept a standardized action component and improve neutral/positive icon contract. |
| BrandMark | Good | Shared appearance and forced-colors support; native adapters duplicate only framework markup. | Keep both thin adapters synchronized through a contract test. |
| Chip | CSS only | Used directly through class strings; no typed Astro/React adapter. | Add adapters before interactive/removable chips appear. |
| Form control | CSS only | `.ds-control`, label/help/error exist, but feature forms mostly bypass them. | Create reusable Field, Input, Select, Textarea, Checkbox components. |
| Icon button | CSS only | Screener uses a separate `icon-button` implementation. | Create an accessible IconButton requiring an `aria-label`. |
| Tabs | CSS only | Company financial tabs are page-local script/markup. | Extract only when a second tab consumer exists; preserve keyboard contract. |
| Dialog | Missing | Two saved-screen dialogs are handwritten with no shared focus lifecycle. | P0 reusable Dialog with Escape, focus trap, scroll lock, backdrop dismiss policy, and focus return. |
| Popover | Missing | Save-screen form and company search each own positioning/dismiss behavior. | Create Popover behavior after search-specific combobox remains separate. |
| Responsive table | Missing | Screener and saved screens independently own overflow/action layouts. | Create table shell/scroll primitive and mobile row-action policy. |

## Astro component audit

| Component | Reuse/status | UI/UX finding | Priority/action |
|---|---|---|---|
| `BrandMark.astro` | Thin reusable adapter | Decorative semantics and sizing are correct. | Keep; test parity with React adapter. |
| `CompanySearch.astro` | Reused in header and hero, but 400+ line monolith | Markup, storage, network cache, combobox state, navigation, DOM creation, and CSS are coupled. Request cache is unbounded; no abort controller; result rows are created imperatively. The submit button duplicated Enter/selection behavior. Hero results overlaid quick picks. | P0 remove redundant action and use in-flow hero results (done in current pass). P1 extract controller module, option renderer contract, bounded cache, and abort stale requests. Add real combobox interaction tests. |
| `MetricGrid.astro` | Useful domain component | Formatting and null semantics are centralized. Local CSS still relies on compatibility aliases and hover `title` for supplemental explanation; touch users get only the accessible label. | Keep domain-specific. Migrate tokens, add visible/detail disclosure for blocked values where explanation matters, and test 1–8 item responsive geometry. |
| `PublicHeader.astro` | Reused globally | Navigation/search/CTA are well grouped on desktop. Inline CSS and fixed item priorities create narrow-width pressure; there is no explicit compact navigation model. | P0 define mobile priority: brand + primary CTA first row, search second row, hide nonessential links. Add 320/390/768 geometry tests. |
| `PublicFooter.astro` | Reused globally | Correct semantic footer, but nine links compete at narrow widths and inline styles prevent reuse elsewhere. | Group links by product/company/legal, reduce mobile density, and move shell styles to shared public-shell CSS. |
| `PublicPageLayout.astro` | Strong reusable page shell | Metadata and public shell are centralized. `current` excludes design-system and company variants by design; no slot for page-specific head content. | Keep; add optional head slot only when a real consumer needs it. |

## Next component audit

| Component | Reuse/status | UI/UX finding | Priority/action |
|---|---|---|---|
| `BrandMark.tsx` | Thin reusable adapter | No defect found. | Keep parity-tested. |
| `Button.tsx` | Reusable base | Feature callers reapply legacy button classes, defeating the typed variants. No `aria-busy` loading API. | P0 migrate callers; add busy/leading/trailing icon slots without hiding button text. |
| `Badge.tsx` | Reusable | No material defect found. | Keep. |
| `Surface.tsx` | Partly reusable | `div` only; semantic use requires wrapper duplication. | P2 introduce Card/Section rather than an unsafe unrestricted `as` prop. |
| `StatusPanel.tsx` | Reusable | Strong live semantics. Raw action buttons and fixed glyphs weaken consistency. | P1 standardize action and tone icon. |
| `AuthForm.tsx` | Mode-driven reuse is good | Four modes share logic, but raw fields/buttons bypass design primitives. Password affordances, pending announcement, and consistent field error component are missing. | P0 migrate to Field/Input/Button; add show-password control and pending live text without moving layout. |
| `AppShell.tsx` | Global shell | Screener is always visually/semantically active. No compact/mobile navigation disclosure. Auth lookup is coupled to shell render. | P0 route-aware nav component; P1 responsive menu with keyboard/focus behavior; keep auth decision server-side. |
| `PageHeader.tsx` | Good reusable component | Clear hierarchy and trust-item support. Description is mandatory even when a page may not need one. | Keep; allow optional description only when a real page requires it. |
| `SaveScreenButton.tsx` | Feature component | Handwritten absolute popover lacks Escape, outside-click dismiss, focus return, and collision handling; can overflow narrow screens. | P0 migrate to reusable Popover/Field/Button. |
| `SavedScreensClient.tsx` | Feature monolith | Client-only loading waterfall; table, mutation state, dialogs, and navigation are coupled. Dialogs lack complete modal behavior; date formatting can hydrate differently by locale; row actions crowd mobile. | P0 shared Dialog and responsive table; P1 accept server-provided initial data; split row/dialog components. |
| `NaturalQueryPanel.tsx` | 300-line workflow component | `InterpretationTable` is reusable but hidden; raw example/candidate/retry buttons drift from primitives. Network, interpretation, examples, ambiguity resolution, and summary are coupled. | P1 extract QueryComposer, ExampleList, InterpretationTable, ClarificationPanel, and request hook. |
| `ScreenerClient.tsx` | 660-line page controller | Results, catalog loading, builder state, reference templates, filter rows, classifications, sorting, validation, saved-query restore, and focus management live together. It is the largest reuse/testability risk. | P0 extract ResultTable/ResultState and FilterRow; P1 extract StructuredBuilder and catalog hook; leave one controller for orchestration. |

## Cross-component implementation order

1. Fix CompanySearch action and layout behavior.
2. Add Field, TextAction/IconButton, Dialog, and responsive TableShell
   primitives with tests.
3. Migrate AuthForm and saved-screen components.
4. Make app navigation route-aware and harden both mobile shells.
5. Split ScreenerClient results and filter-row presentation.
6. Split NaturalQueryPanel presentation states.
7. Add component-state catalog examples for default, hover/focus, loading,
   empty, error, disabled, long-content, and mobile states.
8. Run 320, 390, 768, 1024, and 1440 rendered geometry checks plus keyboard
   and screen-reader smoke tests.

## Completion rule

This pass is not complete merely because components have been renamed or moved.
A component is reusable only when it has a narrow public API, owns its complete
interaction lifecycle, uses shared tokens/primitives, has representative state
tests, and is consumed by at least one real surface without feature-specific
class overrides recreating the same behavior.

## Implementation update — 2026-08-29

Completed in the first hardening pass:

- removed the redundant company-search submit action and made hero results
  participate in layout instead of covering quick picks;
- bounded the in-browser search request cache;
- added reusable `Dialog`, `Popover`, and `Field` components;
- migrated authentication and saved-screen interactions onto shared fields,
  buttons, popovers, and dialogs;
- added modal Escape, focus trap, initial focus, focus return, body scroll lock,
  and backdrop behavior;
- replaced the permanently-active Screener navigation state with a route-aware
  navigation component and a horizontally safe mobile navigation row;
- removed the duplicate Screener header destination, leaving one primary
  `Open screener` action;
- extracted `InterpretationTable` from the natural-query controller;
- removed legacy button-class overrides from the main screener workflows;
- corrected the stock document doctype and contained horizontal navigation,
  tabs, and financial tables as explicit internal scrollers; and
- corrected the rendered QA contract so intentional internal table scrolling
  is not misreported as root-page overflow under Chrome mobile emulation.

Completed in the visual-system implementation pass:

- replaced the homepage's boxed company shortcuts with a short, balanced
  discovery-link rail and reduced the hero search height and visual weight;
- refined the canonical button's hover, press, disabled, busy, size, radius,
  and elevation behavior, and added an owned loading-label/spinner contract;
- added a typed `IconButton` that requires its accessible name and migrated
  dialog close and remove-condition actions to it;
- migrated authentication, account, save, rename, retry, and add-condition
  actions away from the old feature-local button systems;
- removed the obsolete primary/secondary/tertiary/text/icon button CSS;
- applied shared controls to authentication, saved-screen, and exact-filter
  fields and applied the shared checkbox contract to screener switches;
- turned ambiguity candidates into clear choice controls and strengthened
  reference-card press feedback;
- expanded the component catalog with size, busy, and disabled action states;
  and
- added cached frontend presentation overrides for newly exposed dividend,
  net-cash, payout, and pretax-margin metrics so no generic metric copy reaches
  the UI while the backend catalog catches up.

Verified states include homepage, design-system catalog, company research,
screener initial state, and real screener results at desktop and mobile widths.
The mobile result review also found and fixed the result heading/save-action
collision by stacking those actions below 760px.

Still intentionally scheduled rather than disguised as complete: splitting
`ScreenerClient` into result/builder/filter-row modules, splitting the remaining
`NaturalQueryPanel` state views, server-first saved-screen data, self-hosted
fonts, and formal human screen-reader/usability sessions. These are structural
or production-environment tasks; the audit matrix above remains their source
of truth.
