# Screener.in stock-page comparison — 2026-09-20

Prompted by a direct request to study Screener.in's real production page (a
saved HTML export of `screener.in/company/COASTCORP/consolidated/`, its
`custom.186527c1d677.css`, and 8 real screenshots covering every section) and
use it to find concrete gaps in Scrooner's own `/stocks/[ticker]` page —
**not** to visually clone it. Screener.in is India-market-specific (BSE/NSE,
promoter holdings, concalls, credit ratings) and several of its sections have
no honest Scrooner equivalent given what SEC EDGAR actually discloses. The
useful work here is separating **real, fixable gaps** from **legitimate,
data-scoped divergence** — copying a pattern Scrooner has no real data to back
would violate this project's own "never fabricate a value" rule (CLAUDE.md,
company-page section).

## Method

Read the saved HTML verbatim (not summarized), its actual CSS file, and 8
screenshots (top-ratios, documents/credit-ratings/concalls, shareholding +
insights-lock teaser, cash-flow/ratios tables, balance sheet, P&L, quarterly
results, pros/cons + peer table, price chart). Then read Scrooner's real
current stock page (`apps/app/app/stocks/[ticker]/page.tsx`) and its
components (`StockHeader`, `MetricGrid`, `StockSectionNav`, `FinancialTable`,
`ResearchSection`, `PriceChart`) directly — not from memory of earlier
sessions — before concluding anything was missing.

## Already matched or exceeded — verified by reading the actual code, not assumed

- **Sticky sub-nav with scroll-spy.** Screener's `scroll-aid.js` uses an
  `IntersectionObserver` to highlight the active tab and scroll it into view.
  Scrooner's `StockSectionNav.tsx` already does the same (`IntersectionObserver`
  + `scrollIntoView`) — built independently, same real pattern, nothing to
  change.
- **Statement tables** (Quarterly Results / P&L / Balance Sheet / Cash Flow):
  Scrooner's `FinancialTable` already has sticky first column, sticky header,
  a highlighted "most recent" column, and a period-count toggle — functionally
  ahead of Screener's static periods-only table (Screener has no period-count
  control at all, just whatever the schedule shows).
- **Pros/Cons.** Screener's version is machine-generated from a fixed
  checklist with an explicit "please exercise caution" disclaimer. Scrooner's
  `buildChecklist()` is the same idea — deterministic, rule-based, not
  AI-generated prose — just styled with a colored dot instead of a colored
  border box. Cosmetic difference only; not a gap.
- **Ownership section.** Screener's shareholding pattern (Promoters/FIIs/DIIs/
  Public %) is an India-specific disclosure concept with no US equivalent.
  Scrooner's institutional/insider/mutual-fund breakdown (with the explicit
  "never sum these" rule already documented in `insider_info.md`) is the
  correct SEC-native adaptation, not a lesser version of Screener's.

## Real gaps found and fixed this pass

**1. Peer comparison table had no way to see where the company itself sits
relative to its peers, and no summary statistic — Screener's table includes
the subject company as its own bolded row and a bottom "Median" row computed
over the peer set.** Scrooner's table only ever listed peers, with the
current company's own ROIC/growth/margin/ROE visible only in a totally
separate part of the page (Investor Snapshot). Fixed: `page.tsx`'s peers
section now renders the current company as a highlighted first row (reusing
metrics already fetched for the snapshot panel, no new query) and a `<tfoot>`
median row computed client-side over the peer array only (`medianOf()`,
matching Screener's own convention of never including the subject company in
its own median). Also surfaced `company.y_industry` (already joined on by the
peer query but never returned to the frontend) as the section's description
— "Companies sharing the '{y_industry}' industry classification" — so the
match criterion is visible, not implicit.

**2. Real cascade bug caught building the fix, same class already documented
in this file for other tables: a highlighted-row class fought the table's own
sticky-first-column rule and lost.** `.research-table th:first-child` (rule
1, "sticky first column") has higher specificity (0,2,1) than
`.research-table__self th` (0,1,1), so the self-row's highlight color applied
to every cell except the sticky name column — verified by an actual
screenshot, not caught from source alone (see the standing rule: "any
visual/CSS change must be confirmed with a rendered screenshot"). Fixed with
an explicit `.research-table__self th:first-child` rule at matching
specificity. **Generalizable, worth re-checking anywhere else a row-level
highlight class is added to a table that also has a sticky first column**
(`FinancialTable`'s own `.hl` class already handles this correctly by scoping
per-cell rather than per-row — the peer table's row-level approach was the
one exposed to this bug).

## Real gaps identified, deliberately NOT built this pass — data- or scope-blocked, not a frontend oversight

- **Company logo square next to the name.** Screener fetches a real per-company
  logo image. Scrooner has no logo data source at all — adding a placeholder
  or generic icon would be decorative filler, not a real gap closed.
- **Multi-metric price chart (PE Ratio / EV-EBITDA / Price-to-Book / Market
  Cap-to-Sales toggle, moving averages, volume bars, legend checkboxes).**
  Screener plots several precomputed historical ratio *time series*. Scrooner
  only has a daily price series (Alpaca, doc 25) — no historical PE/EV/PB
  series exist yet. This is a real, valuable, but large pipeline feature
  (computing and storing historical ratio time series), not a chart-component
  gap. Flagged for a future scoping pass, not attempted here.
- **Multi-period shareholding trend** (Screener shows 10+ quarters of
  Promoter/FII/DII/Public % history). Scrooner's institutional/mutual-fund
  ownership is *by design* scoped to 2 consecutive periods (`insider_info.md`,
  locked 2026-08-25) — extending this is a backend scope change with its own
  SEC bulk-fetch cost, not a frontend rendering gap.
- **"Add ratio to table" personalized ratio picker.** Already scoped as
  future work in `doc/scoping/29_Scrooner_Personalized_Key_Metrics_Plan.md`,
  explicitly gated on Part 9 (User System) existing first. Not re-scoped here.
- **About-text source citations** (Screener's `[1]`/`[2]` footnote links to
  the exact PDF page a claim came from). Real, valuable, matches this
  project's own trust-moat principle — but `core.company.about_text`'s
  extraction pipeline (`company_master/business_text.py`) does not currently
  persist a per-claim source URL/page alongside the extracted text, only the
  text itself. Needs a pipeline change before the frontend can show it
  honestly; noted for whoever scopes that.

## Deliberately not adopted — would require fabricating data Scrooner doesn't have

Screener's Documents section additionally shows **Credit ratings** and
**Concalls** (transcript/PPT/AI-summary links) — Scrooner has no credit-rating
data source and no earnings-call transcripts for any US-listed company in its
pipeline. Its own "Insights" section is a **paywalled/blurred-table teaser**
pattern (`Log in to view insights`) over data that, per its own footer, is
"Extracted by Screener AI" — a real product choice for Screener, but adopting
the *visual pattern* (a blurred table + login CTA) without the underlying
premium data behind it would be a UI lie, not a design improvement. Both are
correctly absent from Scrooner's Documents section, which only ever links to
real, verifiable SEC filings — left as-is.

## Components audited for dead/duplicate code (per the "delete what's not needed" part of the request)

Checked `StockHeader`, `MetricGrid`, `ResearchSection`, `PriceChart`,
`StockSectionNav`, `FinancialTable` against every Screener section they'd
need to cover — each maps to exactly one real section with no overlap. No
dead or duplicate component was found in this pass; nothing was deleted
because nothing was found unused. (Contrast with the earlier, real
`BrandMark` fork and three-independent-empty-state duplication documented
elsewhere in `frontend-guardrails.md` §3 — this comparison specifically did
not surface a new instance of that pattern.)
