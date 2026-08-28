# Company Page Design Reference Audit

## Problem or clarification

The Astro company page already had Scrooner's approved colors, editorial
typography, metric ledger, deterministic checklist, financial statements,
ownership data, and filings. It was visually credible but still behaved like a
long implementation document:

- it did not have the public site's global Scrooner header;
- four financial statements appeared as four repeated cards instead of one
  statement workspace;
- horizontal financial review lost row/period context;
- filing accession numbers were visually louder than their meaning; and
- ownership and filing rows did not provide direct SEC evidence actions.

The supplied Trendlyne Apple HTML also needed interpretation. It contains useful
company-page hierarchy, but copying its scores, technical indicators, analyst
recommendations, promotional controls, and dense navigation would contradict
Scrooner's locked fundamental-research scope and KISS BORING methodology.

## How it was found

The current implementation was compared with:

- [Scrooner Product Design Framework](../design/10_Scrooner_Product_Design_Framework.md),
  especially the company-page, financial-statement, ownership, filing,
  accessibility, and responsive guidance;
- [Scrooner Design Guideline](../design/11_Scrooner_Design_Guideline.html);
- [Scrooner End-to-End Mockup](../design/12_Scrooner_End_to_End_Mockup.html);
- `doc/html/trendlyne-apple.html`, supplied as a real company-page reference;
- the locked [public/app domain boundary](public-app-domain-boundary.md); and
- the rendered `/stock/aapl/` response using real database data.

The most useful Trendlyne pattern was not its visual style. It was the stable
sequence of company identity → key metrics → financials → ownership → insider
activity, supported by persistent page navigation. Scrooner already had better
source transparency and less commercial noise, so the improvement was to make
that evidence easier to navigate rather than add more feature categories.

## What changed

### Public Astro company page

- Added the shared Scrooner public header, local public-home wordmark, and an
  explicit cross-domain “Open Screener” action.
- Kept the company-section navigation sticky beneath the global header.
- Added CIK as restrained audit metadata in the company identity block.
- Replaced four repeated financial cards with one progressively enhanced,
  keyboard-operable tab workspace.
- Preserved all four statement tables in the server-rendered HTML; JavaScript
  only changes their presentation, so content remains available without it.
- Made row labels and the latest period sticky during horizontal scrolling and
  added a visible scroll-direction cue.
- Added row-level SEC filing links to insider and beneficial-ownership tables.
- Reframed recent filings as a compact event list: event meaning first, form and
  accession as audit metadata, direct official SEC source action last.
- Added a consistent research disclaimer footer, skip link, mobile adaptations,
  and reduced-motion handling.

### Dynamic Next.js app

- Changed the app wordmark to return to the app's own `/screener` home.
- Added an explicit “Company research ↗” transition to the public Astro domain.

## What was deliberately not copied

- Composite ratings, buy/sell recommendations, analyst consensus, and forecast
  promises.
- Technical-analysis panels, price momentum signals, and trading controls.
- Large multi-level menus, promotional density, and premium upsell interruptions.
- A nonfunctional company search. The design framework recommends search, but an
  inert control would make an unsupported product promise; it should ship only
  with a real search contract and keyboard behavior.
- Charts without an accessible table/text equivalent.

## Verification

- Astro production server build: passed.
- Next.js tests: 13/13 passed.
- Next.js ESLint and production build: passed.
- Real runtime request: `/stock/aapl/` returned HTTP 200 and rendered the company
  title, CIK, all four statement tabs, and ten official SEC filing actions.
- Repository diff check: passed.

## Why it matters going forward

A reference product should be mined for information architecture and interaction
lessons, not copied wholesale. Each borrowed pattern must pass Scrooner's scope,
truthfulness, accessibility, and domain-ownership rules.

For future public company-page work:

1. Preserve server-readable public content even when adding interaction.
2. Make the latest period and evidence source easy to retain while scanning.
3. Lead with what a filing means; keep identifiers as audit metadata.
4. Add product controls only when their underlying workflow is real.
5. Keep public research in Astro and application work in Next.js while sharing
   one visual and content system.
