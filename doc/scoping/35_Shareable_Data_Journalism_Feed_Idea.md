# Doc 35 — Idea: A Shareable "Data Journalism" Feed for Reporters/Analysts

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

**Status:** Idea capture (2026-08-28), not scoped or built. Owner: Founder/Product.

---

## The idea (as raised)

A public-facing feed of auto-generated, shareable content — infographics, comparison charts, trend visuals — built from Scrooner's own already-computed data, designed specifically to be **embedded or shared by financial journalists, analysts, and bloggers**, not primarily for Scrooner's own screener users. Each piece carries a Scrooner watermark/attribution, functioning as a distribution/backlink channel rather than a monetized product surface.

**Example content types named:**
- Peer/industry comparisons: "How does Apple's P/E compare to similar stocks?" — a chart, not a table
- Corporate-action trend visuals: dividend history, buyback trends, insider-activity spikes over time
- General "data point of the day"-style shareable graphics

**Stated motive:** help a reporter who needs a quick, credible, embeddable chart — the same logic as any data-provider's "chart of the day" press kit, but generated automatically from data Scrooner already has, at zero marginal content-creation cost per company.

## Why this fits the existing product thesis

This isn't a new idea in isolation — it's a concrete instance of something already named but not built:

- **Doc 01's "Distribution moat"** explicitly names "thousands of indexable company/screen/glossary pages compound via SEO" as moat #3. A shareable infographic feed is the same mechanism aimed outward (earned backlinks/embeds from journalists) rather than only inward (search-indexed pages).
- **Doc 06 Part 12 (SEO/Content Engine)** is already deferred-to-post-MVP scope for glossary/guides/curated-screen pages. This idea is a sibling of that Part, not a replacement — worth scoping alongside it when Part 12 actually gets picked up, not as a separate, competing initiative.
- **Doc 17 explicitly lists peer comparison as NOT built** ("About/business-description text, peer comparison, price chart, shareholding pattern... explicitly out of scope per doc 17 §3"). So the single most-named example content type here (P/E-vs-peers) requires new work regardless of the "shareable feed" framing — it isn't sitting half-built already.
- **Architecture fit is clean**: this is exactly "static/public" content (doc 04/05's "Static/public; dynamic/private" principle) — belongs in `apps/site` (Astro), not `apps/app`, same as everything else aimed at search/external distribution rather than logged-in users.

## What already exists to build on

- All 18 locked V1 metrics + expanded metrics (P/E already computed once price integration is live — see doc 02's resolved Alpaca decision)
- Corporate-action-adjacent data already real: dividends paid, share buybacks (doc 17), insider transactions (doc 19, currently mid-expansion via Track 2), now mutual fund ownership (doc 21, just built)
- SIC code per company (Company Master 4a) — a *candidate* basis for "similar stocks," see open question below

## Real, unresolved design questions — not decidable from data alone

1. **What defines "peer"/"similar stock"?** No peer-grouping concept exists in the schema today. SIC code is the obvious free, already-collected starting point, but SIC codes are notoriously coarse/stale (e.g., a modern software company can carry a decades-old generic code) — this needs a real design decision, likely "SIC code, with manual override for known-bad groupings" rather than assumed-correct automatic grouping. Same "automate detection, keep acceptance human" discipline this project already uses for other ambiguous-classification problems (ticker-change proxies, concept-mapping confidence states).
2. **Generation mechanism**: static pre-rendered images (via a charting library at build/cron time) vs. server-rendered SVG on request vs. a client-side interactive embed (iframe). Each has very different engineering cost and "how embeddable is this really" tradeoffs — worth a real feasibility pass before committing to one.
3. **Watermarking**: a visible brand mark is trivial; preventing easy removal/relabeling is not solvable in image form (any watermark on a raster image can be cropped) — decide whether the goal is "attribution as the polite norm" (like most financial-data chart kits) or something stronger, since stronger implementations (SVG with embedded non-removable text, or an iframe embed that always live-loads from Scrooner) cost more to build.
4. **Update cadence**: does a shared chart need to update live (embed always shows current data) or is a point-in-time snapshot acceptable (simpler, cacheable, but can go stale in a reporter's old article)? This materially changes the engineering approach (iframe/live embed vs. static image).
5. **Legal/licensing**: doc 02 has an open item ("legal disclaimers and data licensing review... before public launch") that already covers the core product — a feed specifically meant for third-party redistribution likely needs its own explicit review pass, not an assumed extension of the core site's terms.

## Suggested next step (not started)

Don't scope this in isolation — when Part 12 (SEO/Content Engine) is picked up per its own doc 06 timing, evaluate this alongside it as a related-but-separate initiative, starting with the "peer" data-model question above, since every content type named depends on it existing first.

Nothing in this document is built or scheduled.
