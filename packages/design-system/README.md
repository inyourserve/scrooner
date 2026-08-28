# Scrooner design system package

Framework-neutral visual foundations shared by the Astro public site and the
Next.js application.

- `src/tokens.css` is the only shared visual-value source of truth.
- `src/foundation.css` owns reset, focus, selection, and reduced-motion rules.
- `src/primitives.css` exposes stable `ds-*` layout and UI primitives.
- `src/index.css` is the normal application entry point.
- `package.json` exposes that entry through both the standard `style` field and
  the `style` export condition so PostCSS/Tailwind and JavaScript-aware bundlers
  resolve the same package import.

The live implementation catalog is the Astro route `/design-system/`. Run
`python3 scripts/check_design_system.py` from the repository root to reject raw
application colors, page-level style blocks, missing implementation contracts,
duplicate required tokens, inaccessible muted-text contrast, undersized default
buttons, or disconnected application entry points.
With the local Astro, Next.js, and FastAPI services running, execute
`node scripts/check_frontend_render.mjs` for the real desktop/exact-mobile
render contract and live metric-catalog curation gate.

Astro and React components remain inside their applications. They are adapters
over this package, not a reason to force both frameworks through one component
runtime. Product-specific composition stays with the product feature.

See `doc/design/13_Scrooner_Scalable_Design_System.md` for the architecture,
component contracts, accessibility rules, contribution process, and migration
policy.
