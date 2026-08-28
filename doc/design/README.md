# Scrooner Design

Product-design, UX, interface-system, and implementation-handoff documents
live in this folder.

- [`10_Scrooner_Product_Design_Framework.md`](10_Scrooner_Product_Design_Framework.md) — Scrooner's core proposition, experience principles, information architecture, page and journey frameworks, visual system, components, states, accessibility requirements, data/UI contracts, validation plan, and execution sequence. **Reconciled 2026-08-22** against the implemented Astro homepage/company research, Next.js results-first screener, shared design system, responsive render contract, and structural accessibility pass. Remaining auth/saved-screen, global-autocomplete, parser-coverage, lineage, and formal-validation boundaries are marked rather than implied complete.
- [`13_Scrooner_Scalable_Design_System.md`](13_Scrooner_Scalable_Design_System.md) — implemented cross-application system: package boundaries, token model, primitives, framework adapters, component layering, accessibility/responsive/state contracts, governance, versioning, migration status, and quality gates.
- [`14_Top_10_Design_Execution_Evidence.md`](14_Top_10_Design_Execution_Evidence.md) — the ranked ten-task hardening pass: executable catalog, expanded primitives and adapters, reusable page/state patterns, extracted public-page styles, accessibility modes, and automated anti-drift gates.
- [`15_Rendered_Frontend_Contract_and_Catalog_Curation.md`](15_Rendered_Frontend_Contract_and_Catalog_Curation.md) — repeatable live render contract for four real surfaces at desktop/exact mobile widths, full 47-metric presentation curation, and evidence for the token/catalog/browser-lifecycle defects it caught.
- [`16_Simple_Language_Screener_Redesign.md`](16_Simple_Language_Screener_Redesign.md) — implemented one-action, results-first plain-language screener; progressive disclosure of exact filters; reference analysis; responsive rules; trust contract; and test/render evidence.

## Related

- [`../consultant/02_Ten_Day_Product_Readiness_Plan.md`](../consultant/02_Ten_Day_Product_Readiness_Plan.md) and its Day 8/9 evidence docs — the plan that has already built and verified a real Next.js screener UI against this framework. Read together; the framework without the evidence docs looks unimplemented, and the evidence docs without the framework lack the design rationale.

## Source material

- `805328183-The-UI-UX-Playbook-Tips-Tricks-for-Exceptional-Design.pdf` (local-only, intentionally not tracked in Git) — supplied reference for hierarchy, clarity, layout, typography, interaction cost, and interface states.
- `How+to+design+better+UI+Components+3.0+-+full+ebook.pdf` (local-only, intentionally not tracked in Git) — supplied reference for responsive foundations, components, accessibility, and design-system practices.

These documents guide UI execution. Canonical product scope and locked
decisions remain in [`../foundational/`](../foundational/).
