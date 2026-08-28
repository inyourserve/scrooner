# 13 — Scrooner scalable design system

> **Status:** Implemented foundation · **Date:** 2026-08-21  
> **Applies to:** `scrooner.com` (Astro) and `app.scrooner.com` (Next.js)  
> **Source of truth:** `packages/design-system/src/`  
> **Product guidance:** `10_Scrooner_Product_Design_Framework.md`

## 1. Outcome

Scrooner now has one visual system with two framework adapters:

```text
packages/design-system (framework-neutral CSS)
              │
        ┌─────┴─────┐
        │           │
 Astro adapters   React adapters
 scrooner.com     app.scrooner.com
        │           │
 public pages     authenticated workflows
```

The shared layer owns visual decisions and is consumed through the local
`@scrooner/design-system` package export. Each application owns rendering,
routing, data access, and product composition. We share stable design contracts
without coupling Astro to React or adding a component-platform toolchain.

## 2. Principles

1. **Research clarity before decoration.** Density is deliberate on research
   surfaces; breathing room is deliberate on marketing surfaces.
2. **One semantic token contract.** Components consume meaning such as
   `--ds-color-text-secondary`, never a raw shade.
3. **Framework-neutral foundations, native components.** CSS is shared; Astro
   and React components remain idiomatic.
4. **Composition over variants.** Add a variant only for a repeated product
   need, not for every one-off layout.
5. **Accessible by construction.** Focus, target size, contrast, motion, field
   errors, and table overflow are system concerns.
6. **Financial truth remains visible.** Period, freshness, source, formula
   version, null state, and audit context survive visual simplification.
7. **No speculative platform work.** The system grows from demonstrated use.

## 3. Repository architecture

```text
packages/design-system/
├── package.json                 identity and CSS exports
├── README.md                    contributor orientation
└── src/
    ├── index.css                stable consumer entry point
    ├── tokens.css               values and semantic contracts
    ├── foundation.css           reset, focus, selection, motion
    └── primitives.css           framework-neutral ds-* primitives

apps/site/src/
├── styles/public-theme.css      Astro theme/compatibility adapter
└── components/
    ├── BrandMark.astro
    ├── PublicHeader.astro
    └── PublicFooter.astro

apps/app/
├── app/globals.css              Next.js feature styles + aliases
└── components/
    ├── layout/AppShell.tsx
    ├── layout/app-shell.css
    └── ui/BrandMark.tsx, Button.tsx, Badge.tsx,
           Surface.tsx, StatusPanel.tsx
```

### Ownership

| Concern | Owner |
|---|---|
| Color, type, spacing, radius, shadow, motion values | `tokens.css` |
| Reset, focus, selection, reduced motion | `foundation.css` |
| Generic button/surface/badge/chip/control/layout behavior | `primitives.css` |
| Public navigation and footer | Astro components |
| Logged-in navigation and application chrome | React app shell |
| Screener and company research compositions | Feature code |
| Product hierarchy and UX direction | Design framework |

## 4. Token model

Tokens have two levels. Palette primitives such as `--ds-color-slate-200`
construct themes. Product components consume semantic tokens such as
`--ds-color-border-default`.

| Purpose | Semantic contracts |
|---|---|
| Canvas/surfaces | `bg-canvas`, `bg-surface`, `bg-subtle`, `bg-raised` |
| Text | `text-primary`, `text-secondary`, `text-muted`, `text-inverse` |
| Structure | `border-subtle`, `border-default`, `border-strong` |
| Action | `action`, `action-hover`, `action-active`, `action-subtle` |
| Meaning | `positive`, `negative`, `warning`, `info` and subtle pairs |
| Interaction | `focus`, `overlay` |

This indirection makes a future theme or brand refinement a token change rather
than a component rewrite. It does not promise dark mode for MVP.

Token categories are color, typography, spacing, shape, elevation, layout, and
interaction. The spacing system uses a 4px base; controls use 36/42/48px
heights; the normal minimum pointer target is 44px.

### 60–30–10 application

- Approximately 60% canvas and quiet neutral background.
- Approximately 30% white surfaces, typography, borders, and table structure.
- At most 10% teal action/meaning accent.

Red, amber, and blue are semantic status colors, not decoration. Positive data
must not become green merely because its number is high; color follows meaning.

## 5. Typography

| Role | Family | Use |
|---|---|---|
| Interface | Inter | navigation, controls, labels, body copy |
| Editorial | Newsreader | marketing proposition and section hierarchy |
| Data | IBM Plex Mono | values, periods, formulas, audit metadata |

- Use only 400, 500, and 600 weights.
- Use tabular numerals for comparable financial values.
- Do not use mono for long prose.
- Company identity may use Inter for compact research density.
- Small uppercase labels require letter spacing and compliant contrast.

## 6. Layout and density

| Container | Maximum | Typical use |
|---|---:|---|
| Reading | 720px | methodology and long-form content |
| Content | 960px | focused workflows and forms |
| Application | 1220px | screener and authenticated workspaces |
| Research | 1296px | financial statements and company data |

Generic flow uses `ds-stack`, `ds-cluster`, and `ds-grid`. A product-specific
grid stays local when it encodes information hierarchy rather than spacing.

Density is contextual:

- **Marketing:** generous rhythm and one dominant task.
- **Application:** moderate density with explicit workflow grouping.
- **Research:** compact ratios/tables with progressive disclosure.

## 7. Primitive contracts

### Button

`ds-button` supports primary, secondary, ghost, size, and full-width modifiers.
React uses the typed `Button` adapter. Links may use the CSS contract when they
navigate and visually need button treatment.

- Primary: one per current decision state.
- Secondary: safe alternative or review action.
- Ghost: reset, dismiss, or low-emphasis utility.
- Destructive behavior requires explicit negative language and styling.

### Surface

`ds-surface` owns border, background, and radius. Raised and padded modifiers
are independent so one Card component does not accumulate unrelated props.

### Badge and chip

`ds-badge` carries a short neutral/positive/warning/negative state. Meaning
remains available in text. `ds-chip` is lightweight selection or navigation,
not a primary-action substitute.

### Forms

`ds-label`, `ds-control`, `ds-help`, and `ds-error` define the base contract. A
field adapter connects label, description, and error through `for`,
`aria-describedby`, and `aria-invalid`.

### Alerts, data, and feedback

- `ds-alert`: neutral, positive, warning, and negative state communication.
- `ds-table-scroll`: labelled horizontal containment for wide tables.
- `ds-tabular`: mono/tabular financial values.
- `ds-spinner`: indeterminate work with adjacent accessible status.
- `ds-skeleton`: layout-preserving loading, never error concealment.
- `ds-sr-only`: visually hidden accessible content.

### Brand

The three-bar mark is defined once in shared CSS. Astro and React render only
the minimal three-span structure. Navigation spells the wordmark `scrooner`.

## 8. Component layers

1. **Foundations** — tokens, reset, motion, focus.
2. **Primitives** — button, surface, badge, chip, field, alert, layout.
3. **Patterns** — shells, section navigation, statement tabs, metric grid,
   state panel, data table.
4. **Features** — screener builder, interpretation, results, company summary,
   ownership, filings.

A feature may depend downward. A primitive must never import feature logic.
Astro and React adapters share class contracts, not runtime dependencies.

## 9. State contract

Every data-dependent component considers:

- idle and loading;
- success with data and success with zero results;
- partial or missing coverage;
- validation blocked and service error;
- stale, delayed, unavailable, and not-applicable data; and
- entitlement blocked when authentication arrives.

Zero, null, stale, delayed, and failed are distinct. Financial components
preserve the value's period and provenance when available.

## 10. Accessibility

- WCAG 2.2 AA is the baseline.
- Every control is keyboard reachable with visible focus.
- Normal pointer targets are at least 44px.
- Errors are announced and programmatically associated.
- Tabs use tablist/tab/tabpanel semantics and arrow-key movement.
- Tables use headings, captions, and scroll instructions.
- Color is never the only state signal.
- Motion respects `prefers-reduced-motion`.
- Pages work at 320px and 200% zoom without document-level overflow. Wide data
  tables may scroll only inside a labelled container.

## 11. Responsive behavior

- 320–640px: one-column composition, contained section navigation, stacked
  actions, and two-column compact metrics only while legible.
- 641–1024px: two-column supporting grids and simplified settings.
- 1025px+: full research/application density.

Do not hide financial context to fit mobile. Reflow controls, preserve headers,
and contain wide comparisons.

## 12. Content and financial formatting

- Buttons begin with verbs: “Run screen,” “View company,” “Interpret query.”
- Values never show unsupported precision.
- Percent, multiple, currency, shares, and period formats use central helpers.
- “Current” is not a freshness claim; use a date or delayed state.
- Generated checklists are fixed rules, not AI opinions.
- No component implies recommendation or investment advice.

## 13. Framework adapters

### Astro

- Import `@scrooner/design-system` once through `public-theme.css`.
- Use `.astro` components for the public shell and public patterns.
- Keep client JavaScript limited to interactions requiring it.
- Marketing and research pages may differ in density while sharing tokens.

### Next.js

- Import `@scrooner/design-system` once through `app/globals.css`. Turbopack's
  root is the repository root so local workspace packages resolve in dev and
  webpack production builds.
- Put route chrome in `app/layout.tsx` through `AppShell`.
- Generic typed adapters live in `components/ui/`.
- Cross-route composition lives in `components/layout/`.
- Feature composition stays under its domain.
- Use co-located, strictly prefixed pattern styles and shared `ds-*` primitives
  for common contracts. The app shell uses `app-shell__*`; this avoids a real
  Next.js Turbopack CSS Module/global-import incompatibility found in dev mode.

## 14. Adding or changing a component

1. Confirm repetition in two real contexts or an accessibility-critical need.
2. Classify it as primitive, pattern, or feature.
3. Reuse semantic tokens; add tokens only for cross-component roles.
4. Specify hover, focus, active, disabled, loading, error, and mobile states.
5. Implement native semantic HTML first.
6. Add a framework adapter only when type safety or behavior justifies it.
7. Test keyboard use, long text, null data, and narrow width.
8. Update this contract when the public API changes.

Do not add a dependency for a component that CSS and native HTML express well.

## 15. Versioning and migration

The package remains private and `0.x` while migration is active.

- Additive contract: minor version.
- Visual correction without contract change: patch.
- Rename/removal or semantic change: major plus migration note.
- Compatibility aliases in `public-theme.css` and `globals.css` are temporary.
- New code uses `--ds-*` directly.
- Remove an alias only after repository search shows zero consumers.

## 16. Quality gates

```bash
python3 scripts/check_design_system.py
cd apps/site && npm run build
cd apps/app && npm run lint && npm test && npm run build
node scripts/check_frontend_render.mjs  # with local site, app, API running
python3 scripts/check_docs.py
git diff --check
```

Material UI changes also require desktop and exact-device mobile renders when a
stable seeded preview is available. `scripts/check_frontend_render.mjs` now
enforces the local happy-path contract at 1440px and exact 390px across the
homepage, catalog, AAPL research page, and screener. The integrity script verifies unique
required tokens, required implementation contracts, both application entry
points, raw application-color leakage, and page-level style-block leakage.

## 17. Migration status

Implemented:

- shared tokens, foundation, and primitives;
- Astro and Next.js entry points connected;
- shared brand contract with native adapters;
- public header/footer and homepage actions using primitives;
- route-level Next.js shell with a co-located prefixed stylesheet;
- typed React Button, Badge, Surface, and StatusPanel adapters;
- reusable application PageHeader and accessible asynchronous feedback states;
- an executable, no-index component catalog at `/design-system/`;
- extracted homepage and company-research page-pattern stylesheets;
- stock-page visual values resolving through the shared package; and
- automated design-system integrity validation with raw-color and page-style
  anti-drift checks.

Incremental follow-up, not a release blocker:

- migrate remaining feature compatibility aliases to direct `--ds-*`;
- split the large screener stylesheet by feature as those features change;
- add visual-regression snapshots after a stable deployment test environment;
- add primitives only when repeated product use earns them.

## 18. Definition of done

A frontend change is system-compliant when it uses semantic tokens, lives at
the correct component layer, covers product and financial-data states, works
with keyboard/focus/reduced motion/narrow widths/long content, preserves the
Astro/Next boundary, implies no unsupported capability, and passes all quality
gates.
