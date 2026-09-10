# Scrooner Product Design Framework

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

The product, UX, interface, content, and implementation framework for a
simple, trustworthy US fundamental screener.

> **Status:** Implemented living framework; remaining gaps are marked inline
> **Prepared:** 2026-08-18  
> **Scope:** Product design direction plus implementation audit through 2026-08-22
> **Authority:** Advisory. Canonical product and architecture decisions remain in `doc/foundational/`.
>
> **Implementation reconciliation 2026-08-22 — this document is now substantially retrospective, not purely forward-looking.**
> Day 8 (structured screener) and Day 9 (plain-English query) of
> `doc/consultant/02_Ten_Day_Product_Readiness_Plan.md` have already been
> built against this framework, in a new `apps/app` Next.js application,
> with passing automated tests — see
> [`doc/consultant/10_Day_08_Screener_UI_Evidence.md`](../consultant/10_Day_08_Screener_UI_Evidence.md)
> and [`11_Day_09_Explainable_Query_UI_Evidence.md`](../consultant/11_Day_09_Explainable_Query_UI_Evidence.md).
> The application is tracked and its frontend foundation was consolidated
> into the cross-application design system on 2026-08-21. The public homepage,
> company-research workspace, results-first screener, responsive render
> contract, and structural accessibility pass are implemented. Sections 3,
> 7-9, 12, 17, 19, and 22 below have been
> corrected against the real, running implementation rather than left as
> untested assumptions; corrections are marked inline. Treat this document
> as a living spec to audit new work against, not a one-time brief.

> **Visual direction addendum — 2026-08-21:** the user-supplied
> `homepage.html` establishes the preferred product surface for new design
> work: a cool-gray canvas, white task surfaces, ink typography, restrained
> teal-green actions, Inter for interface copy, Newsreader for editorial copy,
> a lowercase Scrooner wordmark with a research-aperture mark, compact
> navigation, and one dominant task per page. This supersedes the earlier
> bracket wordmark and warm-paper/Fraunces treatment as a visual direction;
> the product, evidence, accessibility, and public/app boundary principles in
> this framework remain unchanged. The Astro homepage is the first implemented
> reference. Public company pages adopted the same shared header, footer,
> identity, tokens, typography, and surface grammar on 2026-08-21 while
> preserving their denser research workflow. The application surface now
> consumes the same semantic token and brand contract through the
> framework-neutral package documented in
> [`13_Scrooner_Scalable_Design_System.md`](13_Scrooner_Scalable_Design_System.md).

> **Brand-mark correction — 2026-08-28:** the three rising bars were removed
> because they read as a generic stock-screener/chart logo and made Scrooner
> less distinguishable from the category. The replacement uses two offset
> focus brackets, a scan line, and one evidence point. It represents scrutiny
> and verifiability rather than upward price movement; it must not be redrawn
> as bars, a candlestick chart, or a generic magnifying glass.

---

## 1. Executive design decision

Scrooner should feel simple in the same way Screener.in feels simple:
the user sees familiar financial information quickly, can scan dense
tables without ceremony, and is never forced through a decorative
dashboard.

Scrooner should not look like a copy of Screener.in. Its differentiator
is not a fresher coat of paint on a company-data site. It is the
combination of:

1. plain-English access to serious multi-condition screens;
2. deterministic calculations rather than generated financial opinions;
3. visible interpretation with every executed result;
4. metric-level periods, definitions, and source lineage; and
5. unusually useful SEC-native signals, including filings, insider
   activity, institutional ownership, and capital allocation.

The recommended design posture is:

> **Simple surface. Rigorous engine. Visible proof.**

Every major design choice should reinforce that posture.

---

## 2. What Scrooner is building

### 2.1 Product definition

Scrooner is a fundamental research and screening product for US-listed
companies. It lets a serious self-directed investor express an
investment idea in plain English, converts that request into an explicit
structured query, runs it deterministically against normalized data, and
lets the investor verify why each company matched.

### 2.2 Core proposition

The clearest customer-facing proposition is:

> **Screen US companies in plain English—with results you can verify.**

The fuller product promise is:

> Express a serious fundamental idea in plain English. Scrooner turns it
> into exact filters, finds matching US companies, and shows the periods,
> formulas, and SEC filings behind the answer.

This proposition has three proof pillars:

| Pillar | User meaning | Product proof |
|---|---|---|
| Simple to ask | “I do not need to learn a query language.” | Plain-English query with runnable examples today; broader metric aliases and global autocomplete remain open. |
| Exact to compute | “The answer is repeatable, not an AI opinion.” | Visible structured interpretation and deterministic execution. |
| Easy to verify | “I can inspect the evidence before trusting it.” | Values, periods, formula versions, null reasons, and filing links. |

### 2.3 Primary job to be done

> When I have a fundamental investment thesis, help me translate it into
> a precise screen, find the US companies that satisfy it, and verify the
> result without making me become an XBRL or screener-syntax expert.

Representative task:

> Find US companies below $20B market cap with revenue growing more than
> 15% for five years, average ROIC above 15%, positive free cash flow
> every year, and less than 5% share dilution.

### 2.4 Primary audience

- Serious self-directed fundamental investors.
- Initial focus in the United States and India, while remaining globally usable.
- Users who value company quality, financial consistency, cash generation,
  capital allocation, and ownership signals.
- Users comfortable with financial concepts but not necessarily with XBRL,
  SEC data mechanics, or a proprietary query language.

### 2.5 What the product is not

- Not a trading terminal.
- Not a stock-tip or buy/sell recommendation product.
- Not a general-purpose finance chatbot.
- Not a news feed, portfolio tracker, or technical-analysis platform.
- Not a decorative dashboard where charts exist without a decision purpose.
- Not an interface that hides missing data or makes weak evidence look certain.

---

## 3. Current product evaluation

### 3.1 What already creates real product value

Scrooner already has more than a UI concept behind it. The repository
contains working product primitives:

- a normalized SEC-derived data model with **45 company-page metrics** grouped
  into a curated key set and seven investor-language categories, plus a fully
  curated **47-metric structured-screen catalog** (see 12.2 and 19.1);
- versioned canonical concepts and calculated metrics;
- deterministic structured screening with validated operators;
- a bounded plain-English interpreter that rejects ambiguity rather than
  guessing — **but its metric vocabulary covers only 14 of the 47 active
  screenable metrics**
  (`pipeline/src/scrooner_pipeline/ai_query/aliases.py`'s `METRIC_ALIASES`
  is unchanged since 2026-08-17); every metric added after that date is
  screenable through the structured builder but not yet reachable in
  plain English (see 9.4);
- public screen and ask API endpoints, **and, as of Day 8/9 (2026-08-18/19),
  a real working `apps/app` Next.js frontend** exercising both — a
  structured filter builder and a plain-English interpretation panel with
  explicit one-request execution, ambiguity blocking, four verified reference screens, and
  passing Vitest/ESLint/production-build/pytest gates (see
  `doc/consultant/10_Day_08_Screener_UI_Evidence.md` and `11_...`). This
  is not a scaffold; it already implements a large share of this
  document's Section 9-11 recommendations. The latest workflow interprets and
  runs a valid query through one explicit **Show matches** action; ambiguity or
  unsupported language still blocks execution;
- authenticated saved-screen CRUD and an entitlement endpoint exist in the
  backend, but auth, saved-screen, and account frontend experiences are not
  accepted as complete by this framework yet;
- a functioning Astro company-research workspace with curated ratios,
  keyboard-operable statement tabs, checklist analysis, insider activity,
  institutional ownership, major holders, direct SEC filing actions, and the
  complete metric catalog intentionally placed after the primary research flow;
- real delayed market-price integration and price-dependent metrics; and
- explicit null reasons (`analytics.metric_value.is_null_reason`) and
  source lineage (`source_fact_ids`) *stored* in the underlying schema —
  **but dropped before they reach the API.** `screener/resolve.py` reads
  `is_null_reason`; `screener/query.py`'s response builder does not
  forward it, nor `data_as_of`, nor `source_fact_ids`. Section 19.1 was
  originally written as if these needed building; they need *exposing*.

That is the difficult product foundation. The UI should expose it, not
obscure it.

### 3.2 What the current interface communicates

The public homepage is now a real Astro product entrance with the shared public
shell, company/ticker search, covered-company shortcuts, and a direct path to
the Next.js screener. The company page uses the same identity and shell while
adopting a denser research hierarchy: company context and key metrics first,
then financials, strengths/risks, ownership, filings, and finally the exhaustive
metric catalog. It is no longer a starter page or an unstructured card stack.

The Next.js screener expresses the differentiating loop directly. A user can
run a typed request or an example in one explicit action, receive the answer and
readable criteria together, inspect why a company matched, and reopen wording
or exact filters without losing the result. The default semantic order is
creator → results → optional structured editor.

Both surfaces consume the same framework-neutral tokens and primitives. Shared
skip links, landmarks, labelled controls, live states, table captions/scopes,
keyboard statement tabs, visible focus, reduced-motion/high-contrast/
forced-colors foundations, and local horizontal table containment establish a
strong structural WCAG 2.2 AA baseline. This is implementation evidence, not a
claim that an independent accessibility audit or user study is complete.

### 3.3 Metric coverage still outruns plain-English coverage

Pipeline expansion no longer drops new metrics into a flat visual bucket. The
company page now curates all 45 displayed metrics and the API presentation
catalog explicitly defines all 47 active screenable metrics; the render gate
rejects generic category or definition fallbacks. The remaining downstream gap
is language reach: the deterministic parser still has only 14 metric aliases.

Every new metric therefore needs three explicit product decisions: whether it
enters the structured catalog, where it appears in company research, and
whether it earns a curated plain-English alias. Display/catalog coverage is now
enforced; alias coverage remains open and must not be implied by UI copy or a
generic autocomplete claim.

### 3.4 Strategic diagnosis

The product's strongest competitive advantage is currently beneath the
surface. A generic “financial dashboard” design would reduce Scrooner to
the same visible category as many free products.

The experience must instead make the following sequence obvious:

```text
Investment idea
    ↓
Explicit “Show matches” request
    ↓
Deterministic screen
    ↓
Visible interpretation + scannable matches
    ↓
Why it matched
    ↓
Metric and SEC source evidence
```

The natural-language interpretation and the evidence trail are not
supporting features. They are the product narrative.

---

## 4. Lessons applied from the two supplied design books

The two PDFs agree on the fundamentals and are directly applicable to
Scrooner.

### 4.1 Principles adopted

| Book principle | Scrooner application |
|---|---|
| Prioritize the information users seek | Financial values, result count, and matched criteria receive more emphasis than labels, cards, or decoration. |
| Use proximity to express relationships | Metric, value, period, source, and definition stay visually grouped. Separate unrelated statement or ownership sections with larger spacing. |
| Reduce cognitive and interaction cost | Show examples, autocomplete known metrics, preserve recent screens, keep related actions nearby, and do not hide common options behind nested menus. |
| Prefer recognition over recall | Use human-readable metric names, visible operators, examples, recent searches, presets, and consistent table patterns. |
| Simplicity is removal with purpose | Keep the primary workflow narrow; use progressive disclosure for formula and filing detail. Do not remove context required for trust. |
| Establish hierarchy with size, color, weight, and position | Query interpretation, match count, company identity, and key values lead; metadata recedes without becoming illegible. |
| Use a grid and spacing system | Adopt a 4px base with an 8px primary rhythm, fixed layout rules, and reusable components. |
| Design for accessibility | WCAG AA contrast, keyboard access, visible focus, non-color status cues, adequate targets, and semantic tables are release requirements. |
| Treat every component as a system | Buttons, fields, tabs, metric cells, tables, badges, drawers, errors, and empty states have explicit variants and states. |
| Design empty and error states as guidance | An unsupported query, missing metric, zero result, stale value, and API failure each receive a distinct explanation and next action. |
| Test real work, not visual taste | Validate the four reference screens and realistic investor tasks before aesthetic refinement. |

### 4.2 Principles deliberately rejected or constrained

- Gradients, glass effects, large shadows, overlapping imagery, and visual
  effects are not default patterns for Scrooner. They add little to a
  high-trust research workflow.
- Colored backgrounds should not compete with financial data.
- Cards should not wrap every piece of information. Tables and quiet
  sections are often the clearer pattern.
- Green and red must not be used as the only signal for good/bad,
  increase/decrease, buy/sell, or pass/fail.
- A large marketing hero must not push the usable product below the fold.

### 4.3 Source references

- `805328183-The-UI-UX-Playbook-Tips-Tricks-for-Exceptional-Design.pdf` (local-only source; uxpeak, 144 pages): visual hierarchy, proximity, clarity, alignment, contrast, simplicity, whitespace, layout, consistency, depth, color, typography, interaction cost, and state guidance. Confirmed by direct page sampling for this revision, not assumed from the filename.
- `How+to+design+better+UI+Components+3.0+-+full+ebook.pdf` (local-only source; Adrian Kuleszo/@uiadrian, 197 pages): Figma grid/spacing setup, colors, terminology, buttons, forms, pricing, dropdowns, navigation, search, modals, hero sections, cards, and style guides — confirmed against the book's actual table of contents.

**Neither book has a dedicated chapter on dense data or financial
tables** — the closest topic in either is "UI Cards." Scrooner's primary
UI surface (screener results, financial statements, ownership tables) is
exactly the pattern neither source covers. §14.4's table requirements are
this document's own synthesis, not a citation from the supplied material
— correct to rely on, but don't assume external validation exists for it
the way it does for buttons, forms, or color. If a third reference is
ever added specifically for data-grid/table patterns, this is the gap
it should close.

---

## 5. Experience principles

These are decision rules, not slogans.

### 5.1 Answer first

Put the useful answer at the top of the experience:

- Homepage: the query input and a crisp explanation of what it does.
- Screener: the interpreted filters and result count.
- Company page: identity, price/as-of state, and important ratios.
- Statements: latest periods first in the initial viewport.
- Filings: event/form, date, and why it matters before accession metadata.

### 5.2 Show the machine's interpretation

Plain English must never become an invisible black box. Show the structured
meaning as readable filter rows or chips with every executed result. A separate
pre-run review gate is required only when the wording is ambiguous, unsupported,
or otherwise needs a user decision:

```text
ROIC        greater than    15%       Latest / TTM
Revenue     3Y CAGR         above     12%
FCF         greater than    $0        Each of last 3 FY
```

The user should be able to correct a metric, operator, value, or period.

### 5.3 Progressive disclosure, not hidden truth

Use three levels:

1. **Scan:** human-readable value and status.
2. **Inspect:** period, definition, formula summary, freshness, and null reason.
3. **Audit:** formula version, exact source facts, accession number, filing link,
   and data caveats.

Do not place all audit metadata in the main table. Do not make audit
metadata impossible to reach.

### 5.4 Honest states over false completeness

`—` is acceptable only when it has an accessible explanation. Distinguish:

- not reported by the company;
- not mapped or not computable;
- insufficient history;
- unavailable for the selected period;
- stale or delayed;
- outside current universe coverage; and
- temporarily failed to load.

### 5.5 Familiar financial patterns

- Right-align numeric table cells.
- Use tabular numerals.
- Keep row labels left-aligned.
- Keep the company/ticker column sticky in wide result tables.
- Put years/periods in chronological order with a clear latest-period bias.
- Put units in headers or labels; do not repeat noisy units in every cell.
- Preserve full precision in data transport while formatting responsibly for display.

### 5.6 Speed is part of the design

- Server-render public pages.
- Avoid client JavaScript where it does not add interaction value.
- Provide immediate validation while editing filters.
- Use skeletons only when layout is known; otherwise use a concise progress state.
- Never show an empty table while a query is still running.

### 5.7 One primary action per state

Examples:

- Draft query: **Show matches**.
- Valid submitted query: show results and the interpreted criteria together.
- Results: **Save screen**.
- Ambiguity: **Choose meaning**.
- Empty results: **Edit filters**.
- Missing company data: **View source status**.

### 5.8 Research, not recommendation

Avoid labels such as “Best stock,” “Strong buy,” or “Winner.” Use
descriptive language:

- “Passed 4 of 4 selected criteria.”
- “ROIC exceeded 15% in the selected period.”
- “Checklist strength” rather than “Scrooner rating.”
- “Insider purchase reported” rather than “Bullish signal,” unless a
  rigorously defined signal is explicitly introduced later.

---

## 6. Information architecture

The canonical domain split should be visible in the experience but not
feel like two unrelated products.

```text
scrooner.com — public discovery and company research
├── Home
├── Company search
├── /stock/{ticker}
│   ├── Overview
│   ├── Financials
│   ├── Ownership
│   ├── Events & filings
│   └── Sources & methodology
├── Methodology / data coverage
├── Pricing
└── Later: curated screens, guides, glossary

app.scrooner.com — interactive and authenticated work
├── Find companies
│   ├── Plain English
│   └── Structured builder
├── Screen results
├── Saved screens
├── Account / plan
└── Help / metric definitions
```

### 6.1 Global navigation

Recommended desktop navigation:

| Position | Item | Behavior |
|---|---|---|
| Left | Scrooner wordmark | Returns to the relevant domain home. |
| Primary | Screener | Opens the main app workflow. |
| Primary | Companies | Focuses the global company search. |
| Secondary | Methodology | Explains data, formulas, and coverage. |
| Secondary | Pricing | Explains free/premium when policy is locked. |
| Right | Saved screens | Authenticated; otherwise prompts sign-in. |
| Right | Sign in / Account | Account state. |

Keep the header compact and sticky with a subtle bottom border. Do not
use a large mega-menu in the MVP.

### 6.2 Global company search

Company search is distinct from screening. Its placeholder should make
that distinction clear:

> Search company or ticker

Autocomplete rows show:

- ticker in a fixed-width visual slot;
- company name;
- exchange when available;
- SIC/industry description in secondary text; and
- active/inactive status where relevant.

Keyboard behavior: `/` focuses global search, arrows move through
results, Enter opens, Escape closes.

**Implementation boundary, 2026-08-22:** the Astro homepage currently ships a
labelled native company/ticker search backed by the covered-company directory,
clear validation, and deterministic navigation. The richer global autocomplete
contract above — including `/`, custom arrow-key selection, recent searches,
and an app-wide header instance — remains open. Do not describe the native
`datalist` implementation as completion of this full contract.

**Gap versus the cited source, worth closing:** `How to Design Better UI
Components 3.0`'s Search chapter specifically recommends surfacing recent
searches in the empty/focused state — "reduces cognitive load... users
don't have to expend mental effort recalling past searches." This
document cites that same chapter's guidance elsewhere (4.1's "preserve
recent screens") but never applied it to company search itself. Add a
recent-searches list (most-recent-first, capped, clearable) to the empty
state of this component — it's a small addition and the one concrete
pattern from that chapter this section currently omits.

**Implemented 2026-08-22:** the Astro public shell now uses one shared,
accessible company combobox on the homepage and company pages. Results come
from a debounced, capped, CDN-cacheable endpoint only after interaction; empty
focus shows up to five clearable local recents. This preserves the public
company page's single consolidated database read and avoids embedding the
covered universe in every HTML response.

---

## 7. Core user journeys

### 7.1 Journey A — plain-English screen

1. User sees a query field immediately.
2. User enters or selects an example query.
3. User explicitly chooses **Show matches**; Scrooner interprets and runs the
   valid query in one request.
4. Results and the readable interpreted criteria appear together.
5. Ambiguous and unsupported clauses appear separately and prevent execution.
6. User corrects the query or chooses an offered meaning; a meaning choice
   continues the explicitly requested run without a second run click.
7. Results show match count, coverage context, sort, selected values, and periods.
8. User edits the wording or opens exact filters on the same page when needed.
9. User opens “Why matched” or a company page.
10. Later, an authenticated user saves and names the screen; that frontend flow
    is not yet accepted as complete.

### 7.2 Journey B — structured screen

1. User opens the structured builder or switches from the English mode.
2. User selects a metric from the categorized metric control. Searchable
   metric autocomplete remains an enhancement, not a shipped claim.
3. Supported operators update based on the selected metric.
4. Value control and units adapt to percentage, currency, multiple, count,
   or categorical data.
5. User adds additional AND conditions.
6. User selects sort metric, direction, and limit.
7. Inline validation explains incomplete or impossible criteria.
8. User runs, reviews, and optionally saves.

### 7.3 Journey C — company verification

1. User opens a company from results, search, or an indexed page.
2. User confirms identity, current price/as-of status, and the matched metrics.
3. User reviews deterministic strengths/risks and multi-year financials.
4. User inspects ownership and filing events.
5. User opens metric detail for formula, period, null/freshness state, and source.
6. User follows the SEC filing when deeper audit is needed.

### 7.4 Journey D — return to saved work

1. User opens Saved screens.
2. Each screen shows name, criteria summary, last run, and data freshness.
3. User reruns against the current dataset.
4. The interface states that saved screens store criteria, not frozen results.
5. User can rename or delete; deletion requires a clear confirmation.

**Status:** Journey D is a target workflow. Backend saved-screen operations
exist, but the authenticated frontend experience is not complete.

---

## 8. Page framework

### 8.1 Public homepage

The homepage is a working product entrance, not a brochure.

#### Above the fold

1. Compact global header.
2. Left-aligned headline:

   > Screen US companies in plain English.

3. Supporting copy:

   > Build advanced fundamental screens without learning a query language.
   > Every result is deterministic and traceable to company filings.

4. Prominent query input with a concrete example.
5. Primary action: **Show matches**.
6. Secondary action: **Build with filters**.
7. Quiet proof line:

   > SEC filings · Defined formulas · Visible periods · No generated stock opinions

#### Directly below

- Three useful example screens, not abstract feature cards.
- A compact “How it works” sequence: Ask → Show matches → Verify filters and results.
- A real, small result-table preview.
- A methodology/data-coverage link.
- Pricing only after free/premium limits are explicitly locked.

Avoid fake logos, unverified customer counts, manufactured testimonials,
or unsupported claims of complete market coverage.

**Implemented boundary, 2026-08-22:** the shipped Astro homepage fulfills the
public entrance, shared shell, proposition, SEC-derived trust copy,
company/ticker discovery, and clear screener handoff. The plain-English query
itself stays on `app.scrooner.com/screener`; the homepage does not duplicate the
dynamic workflow. Methodology, pricing, and richer educational/preview sections
remain separate work.

### 8.2 Screener workspace

Recommended desktop layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ Header / company search / account                            │
├──────────────────────────────────────────────────────────────┤
│ Find companies                                  Save screen  │
│ Plain-language request                    [Show matches]     │
│ Current criteria · Edit wording · Edit filters               │
├──────────────────────────────────────────────────────────────┤
│ 27 matches · 92% criterion coverage     Columns · Export*    │
│ Results table                                                │
├──────────────────────────────────────────────────────────────┤
│ Build with filters ↓  (optional exact editor)                │
└──────────────────────────────────────────────────────────────┘
```

Before a run, plain language is the visually dominant builder and exact filters
are a compact optional disclosure. Once results exist, the creator collapses to
a one-line request and criteria summary, results move ahead of the exact editor,
and either editor can reopen without losing state.

### 8.3 Saved screens

Use a compact list/table instead of a card gallery.

Columns:

- screen name;
- concise criteria summary;
- last run;
- last match count, clearly marked as historical;
- owner-visible plan/limit state where relevant; and
- actions: Run, Rename, Delete.

The primary row action is Run. Destructive Delete belongs in an overflow
menu and uses a confirmation dialog with **Cancel** and **Delete screen**.

### 8.4 Company page

The company page is the trust destination and should have a compact
sticky section navigation.

Recommended order:

1. **Company header**
   - company name and ticker;
   - exchange, SIC/industry, and active status;
   - latest price, delayed/as-of label, and source;
   - official company and SEC links when available.

2. **Matched criteria context** when opened from results
   - “Passed 4 of 4 screen criteria”;
   - the exact values and periods that produced the match;
   - return-to-results link preserving query state.

3. **Key metrics**
   - one prioritized grid, not separate “top” and “additional” card blocks;
   - allow a compact “Show all metrics” expansion;
   - emphasize values over labels;
   - missing values expose a reason via click/focus, not hover only.

4. **Deterministic analysis**
   - strengths and risks generated by the fixed checklist;
   - label explicitly as rule-based;
   - each statement links to the metric history that triggered it.

5. **Financials**
   - tabs: Quarterly, Profit & Loss, Balance Sheet, Cash Flow;
   - single table surface with sticky first column;
   - Annual/Quarterly and units controls where relevant;
   - newest visible periods prioritized while preserving chronological clarity.

6. **Ownership and insider activity**
   - sub-tabs or sections for Insider activity, Institutions, and Major holders;
   - explain 10b5-1, Form 13F incompleteness, and Schedule 13D/13G scope in context;
   - label “Buy,” “Sell,” “Tax withholding,” or raw transaction type carefully.

7. **Events and filings**
   - most decision-relevant event label first;
   - form, filing date, and accession as metadata;
   - direct SEC source action;
   - filters for form/event later, when volume requires them.

8. **Methodology and data status**
   - coverage, freshness, known gaps, definitions, and legal disclaimer;
   - not a giant repeated note beneath every section.

### 8.5 Methodology and data coverage

Trust deserves a first-class public page. It should explain:

- official and vendor data sources;
- collection and update cadence;
- supported universe and exclusions;
- metric definitions and versions;
- treatment of restatements and periods;
- missing-data reasons;
- delayed price policy;
- Form 4/13F/13D/13G limitations; and
- “research tool, not investment advice.”

This page is both product support and a conversion asset for serious users.

---

## 9. Plain-English query design

### 9.1 Input behavior

- Use a multi-line input that grows to approximately four lines.
- Default example must be genuinely supported by the current parser.
- Show 3–5 selectable examples beneath the empty input.
- Preserve the user's original text after interpretation.
- `Cmd/Ctrl + Enter` submits the same explicit **Show matches** action; an
  unresolved ambiguity still prevents execution.
- Do not imitate a chat conversation. The product is a query workspace.

### 9.2 Interpretation states

| State | Presentation | Allowed action |
|---|---|---|
| Empty | Example queries and concise instructions. | Enter or select query. |
| Running | Small progress indicator with “Finding matching companies…” | Wait; cancel only if needed. |
| Complete | Compact request, readable criteria, and results. | Inspect, edit wording, edit filters, save later. |
| Ambiguous | Highlight phrase and offer explicit candidate meanings. | Choose meaning or edit. |
| Unsupported | Quote the unrecognized phrase and explain supported patterns. | Edit; do not run. |
| Partially recognized | Show recognized and unresolved clauses separately. | Resolve every clause; do not run. |
| API failure | Preserve text and explain retry path. | Retry or switch to structured mode. |

### 9.3 Interpretation presentation

Use editable rows rather than colored chips alone when criteria contain
multiple fields. Chips can provide the collapsed summary.

Example:

| Metric | Operator | Value | Period |
|---|---|---:|---|
| Return on equity | greater than | 30% | Latest available |
| Debt to equity | between | 0–1x | Latest available |

Include a “View exact query” disclosure for the validated JSON contract,
primarily for trust and debugging. It should not be the default user view.

### 9.4 Current parser truth

The existing rule-based parser is bounded. The UI must not imply broad
language understanding it does not have. Initial examples should use
currently supported forms such as:

- “companies with ROE above 30%”;
- “software companies”;
- “debt to equity between 0 and 1”;
- “top 3 by ROIC” (verified in the automated test suite; “top 10” is
  syntactically supported by the same generic `top_n` pattern but is not
  itself a tested example — prefer a verified count in shipped copy); and
- explicit growth horizons such as “revenue growth 3Y CAGR above 15%.”

For “revenue growth” or “EPS growth” without a horizon, the UI should ask
the user to choose YoY or 3-year CAGR.

**This list is not a stable subset — it is currently the *entire*
supported vocabulary.** `pipeline/src/scrooner_pipeline/ai_query/aliases.py`'s
`METRIC_ALIASES` contains exactly 14 metric names, unchanged since
2026-08-17 (its own docstring says so). Most metrics added
since then — Piotroski F-Score, EV/EBITDA, PEG, buyback yield, 5Y/10Y
CAGR, Debtor/Inventory/Payables Days, Cash Conversion Cycle, or any
quality flag — have no alias entry. A user who has just seen the expanded metric set on
a company page and reasonably tries “companies with a Piotroski score
above 7” will get an honest “unsupported phrase” state, which is
correct behavior, but the *product* gap (not a UI gap) is real: the
plain-English surface — the thing Section 1 calls the core
differentiator — currently covers only 14 of 47 active screenable metrics
(approximately 30%) and
that share is shrinking with every pipeline commit. This is a
prioritization decision for engineering (extend `aliases.py`, which is a
small, additive, already-proven pattern — see `pipeline/CLAUDE.md`'s own
notes on the alias tables' curated-not-fuzzy discipline), not something
the UI layer can paper over. Flag it in the same review that ships any
new key-metric curation (12.2) rather than treating parser vocabulary and
displayed-metric curation as two independent backlogs.

---

## 10. Structured filter builder

### 10.1 Filter row anatomy

Each row contains:

1. metric searchable select;
2. operator select;
3. value control;
4. unit suffix or prefix;
5. period/horizon when supported by the metric model;
6. accessible remove action; and
7. inline validation message.

On desktop, keep the row horizontal. On mobile, use a stacked group with
the remove action in the group header.

### 10.2 Metric picker

Group metrics using investor language:

- Valuation
- Growth
- Profitability
- Returns
- Cash flow
- Financial strength
- Capital allocation
- Ownership and insiders
- Company identity

Each option shows the display name and short definition. Search should
recognize common aliases such as ROE, return on equity, FCF, and free
cash flow, while selecting the exact canonical metric.

### 10.3 Operator controls

Use words in the main interface:

- greater than;
- at least;
- less than;
- at most;
- equal to;
- not equal to;
- between;
- top N; and
- bottom N.

The symbols may appear as secondary shorthand. Only show operators the
engine supports for the selected field.

### 10.4 Value controls

| Metric type | Control | Example display |
|---|---|---|
| Percentage | Numeric input with `%` suffix | 15% |
| Multiple/ratio | Numeric input with `x` suffix where meaningful | 2.5x |
| Currency | Numeric input with USD prefix and magnitude support | $20B |
| Count | Integer input | 10 |
| Category | Searchable single select | Software |
| Range | Two appropriately sized inputs | 0 to 1x |

Do not make users convert 15% to `0.15`. The UI converts display units to
the API's canonical decimal representation.

### 10.5 Logic and scope

The current engine combines predicates with AND. The UI must state this
clearly and must not display OR groups, nested conditions, or historical
consistency controls before the engine supports them.

---

## 11. Results framework

### 11.1 Results header

Show:

- exact match count;
- short criteria summary;
- universe/coverage context;
- active sort;
- rerun freshness or dataset version when available;
- Edit filters;
- Save screen; and
- column control only when the initial column set grows.

Avoid celebratory language. Zero and very high match counts are both
neutral research outcomes.

### 11.2 Default result columns

1. Company / ticker
2. Industry or SIC description
3. Every metric used in the criteria
4. Active sort metric if not already included
5. Period/as-of context
6. “Why matched” action

Do not add unrelated metrics merely to fill space.

### 11.3 Metric cell contract

Every displayed result metric must be able to expose:

| Field | Purpose |
|---|---|
| Display name | Human-readable metric identity. |
| Formatted value | Percentage, currency, multiple, or number. |
| Exact underlying value | Available in detail/audit view without float corruption. |
| Period label | FY, Q1–Q4, TTM, or point-in-time. |
| Period end | Exact date. |
| Formula version | Reproducibility. |
| Definition | Meaning and calculation. |
| Source state | SEC-derived, vendor-derived, or combined. |
| Null reason | Why no value exists. |
| Freshness | Filing/price/data timestamp as applicable. |

The current screen result API already exposes value, period label,
period end, and formula version for matched metrics. Definition, source,
freshness, and null-reason delivery should be treated as an API/UI
contract extension, not fabricated in the client.

### 11.4 Why matched

A row detail drawer should explain each condition:

```text
Passed  Return on equity > 30%
        34.2% · FY 2025 · formula v1

Passed  Debt to equity between 0x and 1x
        0.42x · Q2 FY 2026 · formula v1
```

From the drawer, the user can open the company page or metric source
details.

### 11.5 Coverage presentation

The API currently returns matched companies, companies excluded for
missing metrics, and inactive exclusions. Present this without making
the result table noisy:

> 27 companies matched. 6 otherwise eligible companies lacked at least
> one required metric. View coverage details.

Coverage detail groups missing companies by metric. It must not imply
that missing data failed the financial criterion; it was unranked or
excluded because the criterion could not be evaluated.

### 11.6 Sorting and formatting

- Preserve backend order; do not silently re-sort on first render.
- Column header sort calls the backend with explicit metric/direction.
- Indicate active direction visibly and in accessible text.
- Use locale separators and concise magnitudes for display.
- Provide exact values in accessible detail when concise formatting rounds.
- Negative values use a minus sign and text; color is secondary.

---

## 12. Company research framework

### 12.1 Company header component

The header needs a stable hierarchy:

```text
Apple Inc.                                      $231.42
AAPL · Nasdaq · Electronic Computers            Delayed · as of 15:45 ET
Active
```

Company identity leads on the left. Price and freshness form a single
group on the right. On mobile they stack, with price immediately beneath
identity.

### 12.2 Key-metric hierarchy

**Implemented state, verified 2026-08-22:**
`apps/site/src/pages/stock/[ticker].astro` renders all 45 company-page metrics
without reverting to build-order presentation. Eight decision-useful metrics
lead in the company summary; the remainder are grouped into seven named
investor-language categories behind a compact **All Metrics** disclosure area.
Current Price lives with company identity, and every missing metric has an
accessible explanation rather than a hover-only dash.

Default visible metrics should be curated by decision value, not simply
by build order. Recommended first set:

- Market cap
- P/E
- Revenue growth
- Operating margin
- ROIC
- Free cash flow yield
- Debt/equity
- Share-count dilution/buyback trend

Other ratios remain available under **All Metrics**. Industry-specific defaults
can be considered only after the base experience is validated.

The visual curation migration is complete; the actionable-language migration
is not. Several prominently displayed metrics still have no plain-English
alias. Any change to the primary set must therefore include an explicit parser
coverage decision rather than silently suggesting that every visible metric is
reachable in natural language.

### 12.3 Deterministic strengths and risks

Rename the generic section from “Analysis” to **Strengths and risks** or
**Checklist insights**. Include a compact explanation:

> Generated from fixed, published rules using Scrooner metrics—not an AI opinion.

Each item includes the triggering value/horizon. Empty states should say
“No current checklist rule was triggered,” not “No strengths” or “No risks.”

### 12.4 Financial statements

- Use one statement component with tabs rather than four repeated cards.
- Keep row labels and latest column sticky when feasible.
- Let users switch display units: actual, thousands, millions, billions.
- Use `—` for missing values and expose why if known.
- Allow horizontal scrolling with an explicit cue on mobile.
- Never convert a null to zero.
- Do not color entire profitable/unprofitable rows.

### 12.5 Insider activity

- Separate transaction type from interpretation.
- Display owner, role, transaction date, transaction type, shares, price,
  ownership after, and plan state.
- Use “Pre-arranged 10b5-1 plan,” “Discretionary,” or “Not disclosed for
  this filing period”; do not reduce unknown to discretionary.
- Add source filing access at row detail level.

### 12.6 Institutional and beneficial ownership

- State that Form 13F is reported by institutional managers and is not a
  complete real-time shareholder register.
- State whether displayed holdings represent one filing window or a trend.
- Distinguish Schedule 13D active intent from Schedule 13G passive status
  without turning either into an investment recommendation.
- Where percentage/share extraction is absent, do not imply it through
  visual proportions.

### 12.7 Filings and events

Use a compact timeline/list with:

- event label;
- form;
- filed date;
- concise metadata;
- source link; and
- “What this form means” help.

Do not make accession numbers the primary text. They are audit metadata.

---

## 13. Visual design system

### 13.1 Visual character

Scrooner should feel:

- calm;
- precise;
- credible;
- information-dense but not cramped;
- modern without trend effects; and
- serious without feeling institutional or hostile.

The visual metaphor is a well-edited research notebook, not a trading floor.

### 13.2 Layout grid

| Context | Rule |
|---|---|
| Wide desktop | Maximum content width 1240px; 12 columns; 24px gutters. |
| Desktop | 32px page margins, reducing as viewport narrows. |
| Tablet | 8 columns; 24px margins; 16px gutters. |
| Mobile | 4 columns; 16px margins; 8–12px gutters. |
| Reading copy | Maximum 68–75 characters per line. |
| Dense tables | May use the full content width with controlled horizontal overflow. |

Primary breakpoints for implementation:

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

Breakpoints are behavior thresholds, not device labels. Components should
respond when their content no longer fits, not merely when a named device
is assumed.

### 13.3 Spacing

Use a 4px base and 8px primary rhythm.

| Token | Value | Typical use |
|---|---:|---|
| `space-1` | 4px | Icon/text micro-gap. |
| `space-2` | 8px | Related inline elements. |
| `space-3` | 12px | Compact control gaps. |
| `space-4` | 16px | Card/table padding and mobile section gap. |
| `space-5` | 24px | Related groups and desktop card padding. |
| `space-6` | 32px | Section subgroups. |
| `space-8` | 48px | Major section separation. |
| `space-10` | 64px | Public-page section separation. |

Within a component, related elements use less space than the space
between components. Avoid one-off values unless optical alignment
requires a documented exception.

### 13.4 Color foundation

Recommended initial palette, subject to contrast testing in the actual UI:

| Role | Token | Value | Use |
|---|---|---|---|
| Canvas | `surface-canvas` | `#F6F8F6` | App background. |
| Surface | `surface-primary` | `#FFFFFF` | Tables, inputs, primary content. |
| Subtle surface | `surface-subtle` | `#EEF3EF` | Grouping and selected neutral states. |
| Primary text | `text-primary` | `#17211B` | Headings and main copy. |
| Secondary text | `text-secondary` | `#526158` | Metadata and descriptions. |
| Muted text | `text-muted` | `#68776E` | Nonessential metadata; verify size/contrast. |
| Border | `border-default` | `#D8E0DA` | Section, table, and input boundaries. |
| Strong border | `border-strong` | `#AAB8AE` | Active/focus-adjacent structure. |
| Brand | `brand-700` | `#176B4D` | Primary action and selected state. |
| Brand hover | `brand-800` | `#10533B` | Primary hover/pressed. |
| Link | `link-700` | `#175F9E` | Links and source actions. |
| Positive | `positive-700` | `#177245` | Positive status paired with label/icon. |
| Negative | `negative-700` | `#B42318` | Error/destructive/negative paired with label/icon. |
| Warning | `warning-700` | `#8A4B08` | Stale/partial/attention state. |
| Information | `info-700` | `#175CD3` | Neutral informational state. |

#### 60–30–10 color distribution

Scrooner formally uses an adapted **60–30–10 rule**. It is a visual
balance target across a page or major product surface, not a requirement
to calculate exact colored pixels. Data density, accessibility, and
semantic accuracy take precedence when the ratios conflict.

| Share | Layer | Tokens | Scrooner application |
|---:|---|---|---|
| **60%** | Neutral foundation | `surface-canvas`, `surface-primary` | Page canvas, tables, inputs, drawers, dialogs, and the main reading surface. This layer keeps financial information calm and legible. |
| **30%** | Structural support | `surface-subtle`, `border-default`, `border-strong`, `text-secondary`, `text-muted` | Navigation, table headers, grouped filters, selected neutral rows, dividers, secondary panels, and metadata. This layer creates hierarchy without competing with values. |
| **10% maximum** | Purposeful accent | `brand-*`, `link-*`, `positive-*`, `negative-*`, `warning-*`, `info-*` | Primary actions, focus and selected states, links, and genuine semantic messages. Accent color is never used merely to fill empty space. |

The 10% accent allowance is a ceiling rather than a quota. A financial
statement or results table may need only 3–5% accent color. Adding more
green, red, amber, or blue to reach a visual ratio would weaken their
meaning and make the interface resemble a trading terminal.

Application rules:

- Default to a neutral canvas with white primary surfaces; do not use the
  brand color as a full-page or large table background.
- Use structural neutrals to group content before introducing another
  accent color, border, or shadow.
- Use brand green for the primary action, active navigation, focus/selected
  treatment, and restrained brand moments—not for positive company performance.
- Keep status colors inside the accent allowance. Positive, negative,
  warning, and informational colors are semantic exceptions within the
  same 10%; they are not four additional 10% palettes.
- On a typical screen, one accent family should dominate. Other semantic
  colors appear only when the underlying data or system state requires them.
- Large tinted status regions use the lightest accessible semantic tint,
  with the strong color reserved for the icon, label, or border.
- Charts inherit the rule: begin with neutrals, highlight the selected or
  decision-relevant series with one accent, and introduce additional hues
  only when multiple series must be distinguished.
- Never use green/red area balance to make a company look broadly good or
  bad. The color belongs to the specific value or rule state being shown.

Reference distribution by surface:

| Surface | 60% foundation | 30% structure | ≤10% accent |
|---|---|---|---|
| Homepage | Canvas and query surface | explanatory copy, examples, preview structure | primary CTA, links, small trust cues |
| Screener | builder/results surfaces | filter groups, table headers, metadata, dividers | Run/Save, selected filters, validation states |
| Company page | financial tables and content surfaces | section navigation, labels, header rows, secondary panels | links, active tab, specific checklist/status signals |
| Saved screens | list/table surface | criteria summaries, timestamps, row structure | Run action, active state, destructive confirmation |

Rules:

- The brand green means action/selection, not “stock is good.”
- Positive and negative semantic color never appears without text, icon,
  sign, or shape.
- Use neutral backgrounds for most financial content.
- Reserve tinted backgrounds for compact state messages and selected rows.
- Dark mode is not an MVP requirement. Build semantic tokens so it can be
  added later without renaming every component property.

  This is a deliberate scope cut, not a default — worth stating plainly
  because the source material argues the other way for this exact
  domain. `The UI/UX Playbook`'s own Color chapter (p.68) shows a
  *portfolio-tracking* app (donut allocation chart, cash/bonds/equity
  breakdown — closer to Scrooner's own subject matter than any other
  example in either supplied book) and rates a dark theme "👍" on equal
  footing with the light theme, specifically citing reduced eye strain
  for financial-app users checking a screen repeatedly. Keeping dark mode
  out of MVP is still the right call under this project's "evidence
  before expansion" principle (`doc/foundational/05_...md`) — no beta
  user has asked for it yet — but it should be recorded as a considered
  tradeoff against the cited source, not treated as a settled non-issue.

### 13.5 Typography

Use one highly legible sans-serif family: Inter if self-hosted/licensed
appropriately, with `system-ui`, `-apple-system`, `Segoe UI`, and sans-serif
fallbacks.

| Style | Size / line height | Weight | Use |
|---|---|---:|---|
| Display | 40 / 48 | 650–700 | Homepage headline only. |
| H1 | 32 / 40 | 650–700 | Page title/company name. |
| H2 | 24 / 32 | 650 | Major section. |
| H3 | 18 / 26 | 600 | Subsection/card title. |
| Body | 16 / 25 | 400 | Main text and forms. |
| Body small | 14 / 21 | 400 | Table and supporting content. |
| Label | 13 / 18 | 550–600 | Control labels and metadata labels. |
| Caption | 12 / 17 | 400 | Timestamps and audit metadata; never core content. |
| Data large | 22 / 28 | 600 | Important metric values. |
| Data table | 13–14 / 20 | 450–500 | Dense financial tables. |

Use `font-variant-numeric: tabular-nums` for values and table columns.
Avoid body copy below 14px; reserve 12px for noncritical metadata that
still passes contrast requirements.

### 13.6 Shape, borders, and elevation

- Default radius: 6px.
- Larger containers/dialogs: 8px.
- Pills only for genuine tags, statuses, or compact criteria—not every button.
- Prefer light 1px borders and background separation over shadows.
- Use one subtle shadow for dropdowns/popovers and one stronger but soft
  shadow for dialogs. Normal content cards remain flat.
- Avoid full card nesting. A card inside a card is a warning that the
  information architecture should be reconsidered.

**Implementation update, 2026-08-21:** the earlier token drift audit is
superseded. `packages/design-system/src/tokens.css` now owns the shared cool-gray,
teal, semantic status, typography, spacing, radius, elevation, layout, and
interaction contracts. Astro and Next.js both import that package. Positive and
information roles exist; the undocumented application gradient is gone; radii
are explicit tokens rather than scattered implementation values. The complete
implemented contract and migration policy live in design doc 13.

### 13.7 Iconography

- Use one outlined icon family.
- Default icon size: 16px in dense controls, 20px in standard controls.
- Icons supplement labels; unfamiliar actions do not become icon-only.
- Filled variants may indicate selection if the meaning remains clear.

### 13.8 Motion

- Use 120–180ms transitions for hover, focus, dropdown, and disclosure.
- Respect `prefers-reduced-motion`.
- Avoid number-counting animations, chart spectacle, and motion that
  delays access to data.
- Loading indicators communicate actual waiting, not decorative activity.

---

## 14. Component system

Build primitives first, then product components.

### 14.1 Primitives

- Button: primary, secondary, tertiary, destructive; small/medium/large.
- Icon button with accessible name.
- Text input, number input, search input, textarea.
- Select, searchable combobox, multi-select only when truly supported.
- Checkbox, radio, switch only for appropriate input semantics.
- Tabs and segmented control.
- Badge/status label.
- Tooltip for supplementary help; never the only access to essential information.
- Popover, drawer, and dialog.
- Inline message and alert.
- Skeleton/progress indicator.
- Table primitives.

Every interactive primitive needs default, hover, focus-visible, active,
disabled, loading, error, and—where relevant—selected states.

### 14.2 Product components

- Global header and company search.
- Query composer.
- Interpretation panel.
- Filter row and filter-group summary.
- Metric picker.
- Unit-aware value input.
- Results toolbar.
- Company result row.
- Metric cell.
- Metric detail/source drawer.
- Coverage summary.
- Company identity header.
- Key-metric grid.
- Checklist insight.
- Financial statement table.
- Ownership table.
- Filing event row.
- Saved-screen row.
- Data freshness indicator.
- Empty, error, unsupported, and partial-data states.

### 14.3 Button hierarchy

- Primary: one main forward action in a region.
- Secondary: important alternative.
- Tertiary/link: low-emphasis navigation or disclosure.
- Destructive: reserved for irreversible or difficult-to-recover actions.
- Minimum target: 44×44px; dense desktop table controls may look smaller
  but retain an adequate clickable area.
- Labels are action verbs: “Run screen,” “Save screen,” “View source,”
  “Delete screen.” Avoid “Submit” and “Click here.”

### 14.4 Tables

Tables are a first-class design system, not leftover HTML.

Required features:

- semantic `<table>`, headers, scopes, and captions;
- sticky header for long vertical tables;
- sticky first column where horizontal comparison requires it;
- visible sortable state;
- keyboard-reachable row actions;
- row hover as a supplement, not the only action affordance;
- clear null, delayed, stale, and unavailable treatments;
- responsive horizontal overflow with a visible cue; and
- empty and loading rows that span the correct columns.

### 14.5 Dialogs and drawers

Use dialogs for:

- destructive confirmation;
- a short, focused save/rename task; or
- a blocking decision that must be resolved.

Use side drawers for:

- “Why matched”;
- metric details and source lineage; and
- coverage details.

Do not interrupt the natural flow with a modal when inline disclosure is sufficient.

---

## 15. State system

### 15.1 State taxonomy

| State | Meaning | Required presentation |
|---|---|---|
| Loading | The operation is in progress. | Name the operation and preserve layout where possible. |
| Empty | The operation succeeded but has no content. | Explain why and offer the best next action. |
| Zero matches | Valid screen, no companies matched. | Show criteria; suggest widening one filter without implying an error. |
| Missing coverage | A company could not be evaluated for a metric. | Identify missing metric and distinguish from criterion failure. |
| Validation error | User input is incomplete or invalid. | Inline, specific, and adjacent to the control. |
| Ambiguous | Input has multiple valid meanings. | Show choices; execution blocked. |
| Unsupported | Product cannot safely interpret the request. | Quote unsupported phrase and show supported alternatives. |
| Service error | Request failed technically. | Preserve user work, provide retry, include support reference if available. |
| Stale/delayed | Data is valid but not current. | Show timestamp/source and a warning label. |
| Permission/limit | User reached an entitlement boundary. | State current limit and exact upgrade/sign-in path. |
| Not found | Company/page does not exist or is outside coverage. | Search action and useful navigation. |

### 15.2 Empty-state examples

Saved screens:

> **No saved screens yet**  
> Save a screen to rerun the same criteria against updated company data.  
> **Create a screen**

Zero results:

> **No companies matched all 4 criteria**  
> The screen ran successfully. Try reducing the minimum ROIC or removing
> one condition.  
> **Edit criteria**

Unsupported query:

> **We could not interpret “management quality score.”**  
> Scrooner currently supports defined fundamental metrics and selected
> company categories.  
> **View supported metrics**

### 15.3 Error-copy standard

Every error should answer:

1. What happened?
2. What was preserved?
3. What can the user do next?
4. Is the problem input, data coverage, permission, or system availability?

Never expose raw stack traces or substitute “Something went wrong” when
the system knows a more precise category.

---

## 16. Responsive design

### 16.1 Mobile priorities

Mobile supports research and screen review; it does not need to imitate a
desktop terminal.

- Put company identity, query, match count, and key actions first.
- Stack filter controls with 44–48px targets.
- Keep the primary action reachable near the lower portion of the active task.
- Convert metric grids to two columns, then one where labels wrap poorly.
- Use horizontal scrolling for financial tables rather than destroying
  comparison through card conversion.
- Keep the first column sticky and show a small scroll cue.
- Allow the result table to become a compact company list only when each
  selected metric remains visible and comparable.

### 16.2 Desktop density

Desktop should use space efficiently:

- avoid oversized headings and cards;
- keep filters and results in the same work surface;
- allow 13–14px table text with adequate row height;
- use 40–44px standard control heights;
- reserve 48px controls for the primary query input or touch-heavy contexts.

### 16.3 Content transformation rules

| Component | Desktop | Mobile |
|---|---|---|
| Navigation | Inline primary links | Compact menu plus persistent search/screener access. |
| Filter row | Horizontal fields | Stacked labeled group. |
| Results | Comparison table | Horizontally scrollable table or metric-preserving list. |
| Metric detail | Right drawer | Full-height bottom sheet/page. |
| Company header | Two-sided identity/price | Stacked identity then price/as-of. |
| Statement tabs | Inline tabs | Horizontally scrollable tab list. |
| Ownership tables | Full columns | Essential columns plus row detail. |

---

## 17. Accessibility requirements

Target WCAG 2.2 AA for the MVP.

**Implemented structural baseline, 2026-08-22:** both application shells expose
skip links and `main` landmarks; public pages use labelled navigation and
search; financial/result tables provide captions, header scopes, and contained
keyboard-focusable overflow; statement tabs implement arrow/Home/End keyboard
behavior; form errors are associated with controls; async/error states use
appropriate live or alert semantics; successful screen runs move focus to the
result heading; external filing links announce new-tab behavior; and the shared
foundation covers visible focus, reduced motion, increased contrast, and forced
colors. Exact 390px rendered checks show no document-level overflow.

This does not close the whole section. A formal screen-reader audit, 200% zoom
task pass, automated accessibility scanner, and task-based usability sessions
remain release work. Auth, saved-screen, dialogs/drawers, sorting, and global
autocomplete must satisfy the requirements below when their frontends ship.

### 17.1 Required standards

- Text contrast at least 4.5:1 for normal text and 3:1 for large text.
- Non-text interactive/component contrast at least 3:1 where required.
- Visible focus on every interactive element.
- Full keyboard operation for query input, filter builder, autocomplete,
  results sorting, drawers, dialogs, tabs, and saved-screen actions.
- Proper labels and instructions that remain visible after data entry.
- Error messages programmatically associated with their fields.
- Dialog focus trap, initial focus, and focus return.
- Status updates announced with appropriate live regions without excessive chatter.
- Semantic headings and landmarks.
- Semantic tables with header associations.
- No information conveyed by color alone.
- Target size at least 44×44px where practicable.
- Zoom to 200% without loss of task completion.
- Reflow at 320 CSS pixels without two-dimensional scrolling except
  legitimate data tables.
- Reduced-motion support.

### 17.2 Financial-data accessibility

- Screen readers need meaningful values: “34.2 percent,” not an unlabeled “34.2.”
- Negative values should be announced as negative.
- Abbreviations such as TTM, ROIC, and FCF need accessible expansions or
  nearby definitions.
- Sort state must be exposed with `aria-sort`.
- A dash must not be the only accessible label for a missing value; announce
  the reason or “not available.”
- Charts, when added, require a table or textual equivalent.

---

## 18. Content design and terminology

### 18.1 Voice

Scrooner's voice is:

- direct;
- calm;
- specific;
- transparent about limits;
- financially literate without needless jargon; and
- never promotional at the expense of truth.

### 18.2 Naming rules

Use human names first and abbreviations second:

- Return on invested capital (ROIC)
- Free cash flow (FCF)
- Trailing price-to-earnings (P/E)
- Debt to equity

Use “screen” for a set of criteria and “results” for its current output.
Use “save screen,” not “save search,” if the object stored is the
structured ScreenQuery.

### 18.3 Trust copy

Good:

- “Calculated from company filings using formula version 1.”
- “Price delayed approximately 15 minutes.”
- “Excluded because ROIC was unavailable for the selected period.”
- “Rule-based checklist; not an investment recommendation.”

Avoid:

- “AI found the best stocks.”
- “Complete SEC coverage” before it is proven.
- “Real time” for delayed data.
- “No data” when the system knows a more precise reason.
- “Safe,” “guaranteed,” or “undervalued” without a defined, disclosed rule.

---

## 19. Data and design contract

The frontend should not invent financial semantics. Establish a shared
metric catalog contract containing:

- canonical metric name;
- display name;
- short and full definition;
- category;
- value type;
- unit and scaling;
- supported operators;
- allowed period/horizon modes;
- formatting precision;
- formula/version reference;
- screenable status;
- source class;
- known coverage caveat; and
- display priority.

This catalog should drive the filter picker, interpretation labels,
result formatting, metric detail, and glossary/methodology. Duplicating
these definitions independently in Python, the app, and the public site
will create trust-damaging drift.

### 19.1 Required additions before a complete trust UI

The existing result contract is already strong but the final experience
will need deliberate support for the items below. **Verified 2026-08-19:
most of these are not "build from scratch" — the data already exists in
`analytics.metric_value` and is populated by the Mapper; it stops one
layer short of the API.** Reframing each item by its real status:

| Item | Real status |
|---|---|
| Stable metric definitions endpoint | **Live and fully curated as of 2026-08-22.** `GET /v1/metrics` (`apps/backend/routers/screen.py`) joins `analytics.metric_definition` with `apps/backend/metric_catalog.py` for display name, definition, category, value type, formula version, and operators. All 47 currently screenable active metrics have explicit presentation metadata; the live render contract rejects future generic `Other`/placeholder fallbacks. |
| Source/lineage retrieval | **Column exists, populated, not selected.** `analytics.metric_value.source_fact_ids bigint[]` is written by every Mapper stage. `screener/resolve.py` doesn't select it and `screener/query.py`'s response builder doesn't forward it. This is a two-line pipeline fix, not new schema. |
| Explicit data freshness/dataset version | **Column exists, populated, not selected.** `analytics.metric_value.data_as_of timestamptz not null default now()` — same gap as above. |
| Structured null-reason taxonomy | **Text column exists and is populated; no enum exists.** `is_null_reason` holds real, specific strings today (`"zero_denominator"`, `"missing:total_debt(2025)"`, `"negative_ratio_undefined_cagr"`, etc.) but with no fixed vocabulary or check constraint — a UI mapping these to friendly copy needs either a maintained string→copy dictionary or a real enum migration. Exposing the raw string via the API (same fix as above) is a prerequisite either way. |
| Total candidate count and coverage summary | **Genuinely absent.** The caller can derive it client-side (`len(matched) + len(excluded_missing_data) + len(excluded_inactive)`), but no single field or summary object exists. Real, if small, backend work. |
| Stable result/query identifier | **Genuinely absent.** No `query_id`/`result_id` anywhere in `/v1/screen` or `/v1/ask` responses. Real backend work. |
| A preserved return path from company page to result state | Not checked against the new `apps/app` implementation as part of this pass — verify before treating as still open. |

These are product contracts, not merely visual details. Five of the
seven items above are `screener/resolve.py`/`query.py` field-selection
fixes against data that is already correct and already stored — the
lowest-risk, highest-leverage next step for "trust UI" work is that pass,
not new schema design.

---

## 20. Design-system organization and handoff

### 20.1 Figma structure

If Figma is used, organize the file as:

1. `00 Foundations` — color, type, spacing, grid, elevation, icons.
2. `01 Primitives` — buttons, inputs, selects, tabs, badges, dialogs.
3. `02 Data Components` — metric cells, tables, freshness, source detail.
4. `03 Product Components` — query, filters, results, company sections.
5. `04 Patterns & States` — loading, empty, error, ambiguous, responsive.
6. `05 Screens` — desktop and mobile page compositions.
7. `06 Prototype & Test` — the validated task flows.

Use variables/tokens and component variants. Name layers and states in
implementation language, not arbitrary visual names.

### 20.2 Code organization

Recommended shared layers:

- design tokens as CSS custom properties;
- primitives with documented variants;
- financial formatting utilities with tests;
- shared metric catalog/generated types;
- table and state patterns;
- page-specific compositions.

Avoid copying the current company-page local styles into each new page.
Move to a small shared system before the second production screen makes
duplication expensive.

### 20.3 Component documentation

For each component record:

- purpose and when not to use it;
- anatomy;
- content rules;
- variants;
- interaction and keyboard behavior;
- loading/empty/error/disabled states;
- responsive behavior;
- accessibility requirements; and
- representative tests.

---

## 21. Validation framework

### 21.1 Five critical usability tasks

1. Run “companies with ROE above 30%” and explain what Scrooner understood.
2. Resolve the ambiguity in “revenue growth above 15%.”
3. Build debt-to-equity between 0 and 1 using structured filters.
4. Open a match and prove which value/period caused it to pass.
5. Find the latest insider transaction and open its filing source.

### 21.2 Success criteria

| Measure | Initial target |
|---|---:|
| Supported query interpreted successfully | ≥90% in scripted supported tasks |
| Ambiguous query executed without resolution | 0% |
| User identifies why a company matched | ≥80% without assistance |
| User finds metric period and definition | ≥80% within 30 seconds |
| Structured reference screen completed | ≥80% without assistance |
| Keyboard-only completion of core screen | 100% in QA |
| Critical accessibility violations | 0 at release |
| Accidental loss of query during retry/edit | 0 in tested flows |

These targets validate usability, not product-market fit. Retention,
repeat screen runs, saved-screen reuse, and paid conversion require real
beta behavior.

### 21.3 Product analytics events

Capture events without logging sensitive free-form text by default:

- query_started;
- interpretation_succeeded;
- interpretation_ambiguous;
- interpretation_unsupported;
- screen_run;
- screen_zero_results;
- coverage_detail_opened;
- result_company_opened;
- why_matched_opened;
- metric_source_opened;
- screen_saved;
- saved_screen_rerun; and
- limit_encountered.

Attach safe structured properties such as number of predicates, metric
names, operator types, result count bucket, duration, and error category.
Review whether raw query text is needed before collecting it.

---

## 22. UI execution sequence

This framework changes the sequence slightly by placing shared design
foundations before page styling.

> **Status, updated 2026-08-22: the core Astro, Next.js, and shared-system
> phases are implemented and verified.** `apps/app` (Next.js) implements the structured filter builder,
> validated query construction, loading/zero/missing-coverage/validation/
> service-error states, company links, plain-English interpretation with
> ambiguity/unsupported resolution, one explicit interpret-and-run action, the interpreted-to-structured
> conversion, and a "Why matched" detail — verified with passing Vitest,
> ESLint, and production-build gates plus backend pytest coverage (see
> `doc/consultant/10_Day_08_Screener_UI_Evidence.md` and `11_...`).
> Foundation tokens and primitives (Phase 0) are implemented once in
> `packages/design-system` and consumed by both frontend applications; see
> design doc 13 for the verified contract. Treat
> Phases 0-4 as **"audit against the real implementation," not "build"** —
> re-reading them as a fresh build brief risks duplicating working,
> tested code. Phase 5 is partially implemented; its remaining validation
> boundaries are listed below.

### Phase 0 — Foundation contract

- Freeze the core proposition and terminology in this document.
- Create tokens and shared page shell.
- Define the metric catalog contract and formatting rules.
- Build primitives and the table/state foundation.
- Create low-fidelity desktop/mobile flows for the five validation tasks.

### Phase 1 — Day 8 structured vertical slice ✅ built, see `doc/consultant/10_Day_08_Screener_UI_Evidence.md`

- Structured filter builder.
- Validated query construction.
- Result table with chosen metrics and periods.
- Loading, zero, missing coverage, validation, and service-error states.
- Company links.
- Frontend contract and interaction tests.

### Phase 2 — Day 9 plain-English differentiator ✅ built, see `doc/consultant/11_Day_09_Explainable_Query_UI_Evidence.md`

- Query composer.
- Interpretation view.
- Ambiguous and unsupported resolution.
- One explicit **Show matches** interpret-and-run action for valid language.
- Conversion between interpreted criteria and editable structured filters.
- “Why matched” detail.

**Updated boundary, 2026-08-22:** company-page and structured-catalog curation
are complete and guarded by the rendered contract. Parser vocabulary (§9.4)
still trails the catalog and remains a product gap. Global/searchable
autocomplete is also not complete.

### Phase 3 — Company-page redesign ✅ core presentation built

- Shared public header and company search.
- Company identity/price hierarchy.
- Consolidated metric system.
- Tabbed financial statements.
- Ownership and filing presentation.
- Accessible null reasons. Metric-level source lineage remains open because the
  result/API contract does not expose all stored provenance yet.

### Phase 4 — Homepage and trust pages 🟨 public entrance built

- Product-first Astro homepage and shared public shell. ✅
- Methodology/data coverage. Open.
- Pricing when limits are locked. Open.
- Saved-screen and auth experience. Open.

### Phase 5 — Validation and refinement 🟨 engineering pass built

- Structural keyboard/semantic/accessibility implementation pass. ✅
- Responsive QA over homepage, catalog, AAPL, and screener at 1440px and exact
  390px, including nulls and wide local table overflow. ✅
- Both production builds, frontend tests, design-system governance, docs, and
  dependency-free rendered contract. ✅
- Five task-based usability sessions and formal screen-reader review. Open.
- Automated accessibility scanning and 200% zoom task validation. Open.
- Performance budgets and pixel baselines against frozen fixtures. Open.

---

### Company-page compact research-workspace addendum (2026-08-21)

The public homepage and public company page share one visual identity, header,
footer, and token system, but they intentionally use different density:

- the homepage remains a calm, explanatory marketing surface;
- the company page is a compact research workspace;
- the first company surface combines identity, delayed-price context, key
  ratios, and a short factual profile;
- strengths and risks are compared together;
- financials, ownership, and filings precede the exhaustive metric catalogue;
  and
- complete metric groups use collapsed disclosure by default.

This supersedes any interpretation of Phase 3 that turns every company-page
section into a large standalone card. The competitive reference establishes a
scan pattern, not feature scope: unsupported charts, peers, recommendations,
follow actions, exports, or premium prompts must not be simulated.

Implementation and render evidence are recorded in
`doc/learnings/screener-reference-density-and-research-flow.md`.

## 23. Definition of design-ready

UI implementation is design-ready when:

- the proposition and page hierarchy are accepted;
- the four reference screens can be represented by the builder;
- the exact API-to-display unit conversions are documented;
- metric names, definitions, units, and formatting are available from one source;
- desktop and mobile wireframes cover all core states;
- primitives and data-table rules are defined;
- accessibility behavior is specified;
- no UI implies unsupported OR logic, broad AI understanding, complete
  coverage, real-time prices, or investment recommendations; and
- the five usability tasks have a testable prototype or implementation path.

---

## 24. Design review checklist

Before merging any major UI:

### Product clarity

- Can a first-time visitor explain Scrooner in one sentence?
- Is the primary action obvious?
- Does the screen reveal rather than hide the interpreted criteria?
- Is there any unsupported promise?

### Financial trust

- Is each important value labeled with unit and period?
- Can a user reach its definition and source?
- Are delayed/stale/missing states explicit?
- Are null and zero distinct?
- Is any generated prose being mistaken for financial truth?

### Hierarchy and density

- Are values more prominent than their containers?
- Are related items closer than unrelated items?
- Can one visual layer be removed without losing meaning?
- Has card overuse created unnecessary borders or padding?
- Are numbers aligned for comparison?
- Does the screen preserve the adapted 60–30–10 balance, with accent
  color at or below 10% and used only for action or meaning?

### Interaction

- Is there one primary action in the current state?
- Is the action label specific?
- Does the user retain work after error or sign-in?
- Are hidden options genuinely secondary?
- Are ambiguous or partial queries blocked from execution?

### Accessibility and responsive behavior

- Does the flow work by keyboard?
- Is focus visible and correctly restored?
- Are contrast and target sizes compliant?
- Is information understandable without color?
- Does it work at 320px and 200% zoom?
- Are data tables still comparable on mobile?

### Engineering quality

- Does the UI send the exact validated API schema?
- Are Decimal values preserved until display formatting?
- Are important states tested?
- Are design tokens/components reused?
- Does the production build pass without production credentials?

---

## 25. Final recommendation

Do not begin with a visual redesign of every page. Build the product's
distinctive loop first:

> **Ask → show matches → verify interpretation → understand why → inspect source.**

That loop is the Scrooner product. A familiar Screener.in-like density
and simplicity should make the loop feel effortless, while Scrooner's
visible interpretation and SEC-grade evidence make it meaningfully
different.

The winning interface will not be the one with the most charts, cards,
or AI decoration. It will be the one where a serious investor can form a
complex screen in seconds, trust what the system did, and verify the
answer without leaving the workflow.
