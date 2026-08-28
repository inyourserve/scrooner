# Rendered Design Review — 2026-08-21

## Problem or clarification

The current public site, company page, and application shell follow the approved
palette and editorial-ledger vocabulary, but document compliance did not produce
a top-class product experience. The rendered product is credible and readable;
it is also visually flat, excessively framed, and too close to an internal data
sheet.

The main company-page journey is also out of order. Users encounter the complete
metric catalogue before the financial statements, so the most important research
workflow is buried beneath a long wall of similarly weighted cards.

## How it was found

The real Astro homepage and Apple company page were rendered from the local
database at desktop and exact 390 CSS-pixel mobile viewports. The Next.js
screener was rendered at the same sizes. Browser geometry was measured in
addition to inspecting screenshots so a browser-window capture artifact was not
mistaken for a responsive defect.

The review found:

- the public homepage header has a 672-pixel minimum content width at a
  390-pixel viewport because all desktop navigation and actions remain in one
  unwrapped row;
- the homepage results figure retains the browser's default 40-pixel side
  margins, leaving only 274 pixels for the table, whose content is then clipped
  by `overflow: hidden`;
- the company hero uses a large vertical and horizontal gap between identity
  and price without turning that space into useful context or action;
- Key Metrics places a bordered metric ledger inside another bordered card;
- All Metrics appears before Financials and repeats the same card-and-grid
  treatment across a very long page, including visibly incomplete rows;
- small uppercase mono labels are used so frequently that supporting metadata
  competes with the research story;
- desktop homepage composition concentrates the value proposition in the left
  half while leaving the right half largely unused; and
- the Next.js screener is genuinely responsive at 390 pixels, but its large
  bordered empty/error states share the same visually flat, document-like
  treatment.

## Fix / decision

No product source was changed during this review. The next design pass should be
a structural correction, not a series of cosmetic color changes:

1. Fix the public mobile header and the homepage figure before adding features.
2. Reorder the company journey to Overview → Financials → Strengths & Risks →
   Ownership → Filings → All Metrics / Definitions.
3. Compress the company identity, price, freshness, and primary research actions
   into one deliberate hero composition.
4. Remove outer cards where an inner table or ledger already defines the
   boundary; reserve cards for objects that need containment.
5. Make All Metrics progressive disclosure with a category index, compact rows,
   and an explicit expanded state instead of displaying every category at once.
6. Reduce mono/uppercase metadata, strengthen section-level editorial hierarchy,
   and use the green accent for decisions and evidence actions rather than
   decoration.
7. Give the homepage a balanced proof composition: product promise and live
   screener evidence should read as one scene, not two vertically separated
   documents.

This direction preserves the product's research-not-recommendation position and
the locked Astro/public versus Next.js/application boundary documented in
[`public-app-domain-boundary.md`](public-app-domain-boundary.md).

## Why it matters going forward

A token-compliant interface can still have weak hierarchy and poor composition.
Future design reviews must include real desktop and exact-width mobile renders,
content-order evaluation, and browser geometry checks. The product should be
judged by how quickly a user can form and verify a research view—not by how many
approved components appear on the page.

