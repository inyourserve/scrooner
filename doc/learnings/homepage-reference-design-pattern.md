# Homepage Reference Design Pattern

## Problem or clarification

The earlier homepage was faithful to Scrooner's written design principles but
looked like an editorial data document rather than a calm product entrance. A
user-supplied `homepage.html` clarified the intended visual character much more
precisely than abstract token guidance: compact navigation, a large lowercase
identity, one centered task, cool neutral surfaces, restrained teal, and very
little framing.

The supplied file was treated as a visual reference, not as executable product
instructions. Its placeholder links, fake login/account actions, and demo-only
search behavior were not copied.

## How it was found

The reference HTML and CSS were read completely, then compared with:

- the current Astro homepage;
- the public/app domain boundary;
- the locked proposition, “Screen US companies in plain English—with results
  you can verify”; and
- the live active-company universe in Postgres.

The implementation was rendered at 1440×1000 and at an exact 390×844 CSS-pixel
viewport. Browser geometry confirmed `scrollWidth = innerWidth = 390` on
mobile. The live page returned 222 real company options, five recognizable
covered quick picks, no fake login/account actions, and real links to both the
company page and application screener. Submitting `AAPL` navigated to the real
`/stock/aapl/` page.

## Fix / decision

- Rebuilt `apps/site/src/pages/index.astro` around the supplied visual pattern.
- Added a real active/current-listing company finder. Its first implementation
  embedded the whole directory in homepage HTML; that was superseded by the
  on-demand cached endpoint described in
  `global-company-search-is-an-interaction-read.md` so the shared public header
  can offer search without increasing every page response or company-page read.
- Made company search deterministic: ticker/name prefixes resolve to current
  covered listings, while empty, unavailable, and uncovered states remain in
  the finder with guidance.
- Limited quick picks to recognizable reference companies that actually exist
  in the current covered universe. Missing reference companies are omitted,
  not replaced with invented coverage.
- Preserved the real Next.js screener as the primary cross-domain action.
- Kept SEC sourcing and the research-not-investment-advice statement visible.
- Added the new visual direction as an addendum to the product design framework.

## Why it matters going forward

Use this homepage as the visual baseline for Scrooner's next design passes:
cool neutral canvas, teal action hierarchy, lowercase bar-mark identity,
Inter/Newsreader typography, generous breathing room, and one dominant task.
Apply the pattern structurally—not as a palette swap. Company pages still need
dense tables and evidence; the screener still needs explicit interpretation and
results. Their information architecture should remain purpose-built while the
brand and interaction grammar converge.
