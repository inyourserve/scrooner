# Stock page UX and information-architecture plan — 2026-09-02

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

> **Status:** Planning only. No frontend implementation is authorized by this
> document itself.
>
> **Scope:** `/stock/{ticker}` information hierarchy, component behavior,
> wording, responsive presentation, evidence, and validation.
>
> **Goal:** Help a self-directed fundamental investor move from orientation to
> a defensible research decision without turning Scrooner into a stock-rating
> or recommendation product.

## 1. Why another redesign is necessary

The current page contains useful data, but its hierarchy still partly follows
the shape in which data was added:

- company metrics;
- checklist observations;
- financial statements;
- peers;
- workforce and segments;
- insider activity;
- institutional and fund summaries;
- beneficial ownership;
- filings; and
- the full metric catalogue.

That is a complete inventory, not yet a complete investor workflow. An investor
does not begin with “Which table should I open?” The investor begins with:

1. What does this company do and what drives it?
2. Is the business improving or deteriorating?
3. Is the business economically good?
4. Can its balance sheet survive adversity?
5. What expectations are already embedded in the price?
6. Is management allocating capital in shareholders' interests?
7. What changed recently, and what evidence should I inspect?

The next design must make those questions visible before it exposes the filing
and database structure.

## 2. Research basis

### 2.1 Investor-analysis guidance

- The SEC's [How to Read a 10-K](https://www.sec.gov/answers/reada10k.htm)
  identifies the business description, material risks, MD&A, operations,
  liquidity/capital resources, known trends, and financial statements as the
  core materials for understanding a company.
- The SEC's [Beginner's Guide to Financial
  Statements](https://www.sec.gov/about/reports-publications/investorpubsbegfinstmtguide)
  explains that the balance sheet, income statement, cash-flow statement, and
  MD&A answer different but related questions; the interface should not flatten
  them into interchangeable numbers.
- CFA Institute's [Company Analysis: Past and
  Present](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/company-analysis-past-and-present)
  begins with the business model, then revenue drivers, profitability, working
  capital, capital investment, capital structure, peers/industry, valuation,
  and risk.
- Scrooner's existing decision-dataset analysis correctly argues for five
  decision groups: Business, Financial Safety, Valuation, Shareholder
  Alignment, and Recent Change. This plan refines that idea using what the page
  can honestly support today.

### 2.2 Information-UX guidance

- Nielsen Norman Group's [Progressive
  Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)
  establishes that what appears initially communicates importance. Therefore,
  raw transaction lists and audit metadata must not receive the same initial
  prominence as decision signals.
- NN/g's [Layer-Cake Pattern of Scanning
  Content](https://www.nngroup.com/articles/layer-cake-pattern-scanning/)
  treats headings and subheadings as a page-level mini information
  architecture. Headings must use clear investor language and reveal the page
  sequence when scanned alone.
- W3C's [Tables Tutorial](https://www.w3.org/WAI/tutorials/tables/) requires
  semantic header/data relationships and recommends captions for orientation.
- The [GOV.UK table component](https://design-system.service.gov.uk/components/table/)
  recommends right-aligning comparable numeric columns.

## 3. Product stance

The page must help investors **research**, not tell them what to buy.

### Must do

- Summarize verified facts.
- Show direction and period, not only current values.
- Explain why a metric matters.
- Compare like with like.
- Surface missing or stale data honestly.
- Link every derived conclusion to inspectable evidence.
- Separate fact, deterministic interpretation, and limitation.

### Must not do

- Produce a single stock score.
- Label a stock “good,” “bad,” “cheap,” or “expensive” without an explicit,
  reviewable comparison rule.
- Treat insider or institutional activity as a buy/sell recommendation.
- Mix annual, quarterly, and TTM values without visible period labels.
- Sum overlapping Form 13F and N-PORT ownership.
- infer qualitative claims that are not supported by collected filings.
- use green/red merely to decorate positive/negative numbers; color must encode
  a defined direction and also have a text label.

## 4. Primary user and primary task

### Primary user

A serious self-directed investor who understands common financial terms but
does not want to decode SEC forms, XBRL concepts, or Scrooner's internal metric
names.

### Primary task

> “Help me decide whether this company deserves deeper research, and make it
> easy to verify the evidence that shaped that decision.”

### Secondary tasks

- Check the latest quarter.
- Compare the company with relevant peers.
- Inspect financial-statement history.
- Understand leverage, liquidity, and cash generation.
- Review insider and professional-owner behavior.
- Find recent material filings.
- Verify the period, source, and definition of a metric.

## 5. Target page hierarchy

```text
1. Company identity
2. Business description and current context
3. Decision summary
   ├─ Growth
   ├─ Profitability & returns
   ├─ Cash & financial strength
   ├─ Valuation
   └─ Shareholder alignment
4. What changed recently
5. Financial performance trends
6. Peer comparison
7. Ownership & alignment
8. Business detail
9. Recent material events
10. Financial statements
11. Ratios, definitions, and source evidence
```

This differs from the current page in three important ways:

1. The top is organized by investor decisions, not statement categories.
2. Current values must be paired with direction/context.
3. Raw statements and exhaustive metrics remain available but no longer define
   the first reading sequence.

## 6. Above-the-fold specification

### 6.1 Company identity bar

**Question answered:** “Am I looking at the correct security, and how fresh is
the market context?”

#### Content order

1. Company name
2. Ticker and exchange/status
3. Sector / SEC industry
4. Official website
5. Latest price
6. Price timestamp and delayed/live status

#### Wording

- `$189.42`
- `Delayed · 16:00 ET`
- `No market price available` instead of a standalone dash
- `Official website ↗`

#### Do not show initially

- CIK
- EIN
- phone
- raw metric-coverage count

Those belong in `Company details`.

### 6.2 Business description

**Question answered:** “What does the company sell, to whom, and through which
reported businesses?”

#### Content

- Two-to-four sentence factual description.
- Up to three factual context points when available:
  - largest reported revenue segment;
  - number of reported segments;
  - employee count and annual direction.

#### Rules

- Do not generate a “moat” claim.
- Do not claim recurring revenue, customer concentration, or geography unless
  collected evidence supports it.
- Link context points to the detailed Business section.

### 6.3 Decision summary

**Question answered:** “Does this company merit deeper research?”

Use five **decision rows**, not five decorative cards. Each row contains:

```text
Decision label
Primary metric        Current value
Direction             Comparison period
One-sentence meaning
```

#### Growth

- Primary: Revenue growth, 3-year CAGR
- Secondary: Latest YoY revenue growth
- Context: EPS growth where valid
- Example meaning: `Revenue expanded 12.4% annually over three years.`

#### Profitability & returns

- Primary: ROIC
- Secondary: Operating margin
- Context: margin direction, ROE with leverage caveat
- Example meaning: `ROIC is 18.2%; operating margin is stable versus last year.`

#### Cash & financial strength

- Primary: Free-cash-flow margin or FCF
- Secondary: Net debt/EBITDA or debt/equity
- Context: interest coverage/current ratio depending on industry
- Example meaning: `Free cash flow is positive; leverage is 1.4× net debt/EBITDA.`

#### Valuation

- Primary: P/E when meaningful
- Secondary: FCF yield
- Context: EV/EBITDA or P/S depending on available denominator
- Example meaning: `Trades at 24.6× trailing earnings; FCF yield is 3.1%.`
- Never say `cheap` without a peer/history comparison.

#### Shareholder alignment

- Primary: share-count change
- Secondary: buyback/shareholder yield
- Context: insider ownership and open-market activity
- Example meaning: `Diluted shares increased 2.3% YoY; insiders were net sellers over 12 months.`

#### Null behavior

If a primary metric is unavailable:

- show `Not available`;
- show the exact reason beneath it;
- do not silently substitute a weaker metric;
- keep the row in place so absence is visible.

## 7. “What changed recently” strip

**Question answered:** “What deserves attention since the previous comparable
period?”

Show at most four changes, ranked by materiality and data confidence:

1. Revenue growth acceleration/deceleration
2. Operating-margin expansion/contraction
3. Leverage or liquidity deterioration/improvement
4. Share dilution/buyback change
5. Insider net buying/selling
6. Institutional ownership movement
7. Material 8-K event

Only four appear initially. Remaining changes belong under `View all changes`.

Each item must include:

- direction in words;
- magnitude;
- comparison period;
- affected metric;
- evidence link or route.

Example:

> **Operating margin expanded 1.8 percentage points**  
> 24.2% in FY2026 vs 22.4% in FY2025

Avoid generic labels such as `Positive` or `Negative` without the underlying
change.

## 8. Financial performance section

**Question answered:** “Is performance improving consistently?”

### Primary presentation

Use a compact trend table showing the latest five annual periods and latest
eight quarters for a curated set:

- Revenue
- Revenue growth
- Operating margin
- Net income
- EPS
- Cash from operations
- Free cash flow
- Diluted shares

### Interaction

- Toggle: `Quarterly` / `Annual`
- Default: Quarterly for recent momentum
- Keep latest period visually highlighted
- Keep row labels sticky
- Use one unit label above the table

### Optional visual

A future chart is justified only for relationships that become clearer
visually:

- revenue with operating margin;
- FCF with net income;
- shares outstanding over time.

Every chart must have the table as its accessible equivalent. Do not add a
price chart merely to imitate another product.

## 9. Peer comparison

**Question answered:** “Is this result strong or weak for this kind of
business?”

### Table columns

1. Company
2. Market cap
3. Revenue growth, 3Y
4. Operating margin
5. ROIC
6. Net debt/EBITDA
7. P/E or FCF yield

### Rules

- Include the subject company as a highlighted row.
- Compare identical metric definitions and compatible periods.
- State whether matching is exact SEC industry or broader sector.
- If market cap/valuation is missing across peers, omit the column rather than
  render a column of dashes.
- Do not order by one metric and imply it is an overall rank.

### Wording

- Heading: `Peer comparison`
- Helper: `Companies in the same SEC industry; values use the latest comparable period.`
- Disclosure: `How peers are selected`

## 10. Ownership and alignment

**Question answered:** “Are managers and professional owners aligned, and are
they adding or reducing exposure?”

### Initial surface: three rows

#### Insiders

- Insider ownership
- 12-month net open-market buying/selling
- Buyers vs sellers
- Largest discretionary purchase
- Text direction: `Net buyers`, `Net sellers`, or `No open-market activity`

#### Institutions

- Latest reported ownership
- Percentage-point change from prior quarter
- Managers adding/opening vs reducing/exiting
- Report date
- Text direction: `Ownership increased/decreased/unchanged`

#### Mutual funds

- Latest reported ownership
- Change from prior reporting period
- Funds adding/opening vs reducing/exiting
- Report date
- Text direction

### Important limitation

Display once, beside the section heading:

> `Reported filing data, not live positions. Institutional and mutual-fund
> totals overlap and must not be added.`

### Progressive disclosure

- `View insider transactions`
- `View institutional holders`
- `View mutual-fund holders`
- `View reported holders above 5%`

Do not repeat four-card metric grids inside every subsection. Use aligned rows
with one primary value and two supporting facts.

## 11. Business detail

**Question answered:** “What operational drivers and concentration risks sit
behind the consolidated numbers?”

### Segment mix

- Latest comparable period only by default
- Segment name
- Reported revenue
- Share of disclosed segment total
- Rank largest to smallest
- Explicit unit and period

### Workforce

- Latest employee count
- YoY absolute and percentage change
- Two-year history only when that is all the filing evidence supports
- Avoid automatically treating hiring as positive or contraction as negative

### Interpretation rule

The interface may say:

- `Revenue is concentrated: the largest reported segment is 63% of the total.`
- `Reported workforce contracted 8.2% YoY.`

It must not say:

- `This is a strong segment.`
- `Layoffs improved efficiency.`
- `Hiring indicates growth.`

Those require evidence the current dataset does not contain.

## 12. Recent material events

**Question answered:** “What changed that historical ratios may not yet show?”

### Initial list

At most five items, prioritizing:

1. 8-K material events
2. latest 10-Q
3. latest 10-K
4. ownership filings with active intent
5. other recent filings

### Row anatomy

```text
[Form] Plain-language event title
Filed date · material item category
View SEC filing ↗
```

### Filters, only when supported

- `All`
- `Reports`
- `Material events`
- `Ownership`

Do not add empty filters or filters that only rearrange five rows.

## 13. Financial statements

**Question answered:** “Can I inspect the primary accounting evidence?”

Keep the existing tabs:

- Quarterly Results
- Income Statement
- Balance Sheet
- Cash Flow

This section moves after the decision-oriented research flow. It is evidence,
not the first explanation.

### Table requirements

- `<caption>` describing company, statement, units, and period direction
- `scope="col"` for period headers
- `scope="row"` for line items
- sticky row names and latest period
- numeric alignment right
- no color-only meaning
- horizontal scroll cue on small screens
- maximum eight periods initially
- `View full history` only when more history exists

## 14. Ratios, definitions, and evidence

**Question answered:** “How was a value defined and where did it come from?”

### Category order

1. Valuation
2. Growth
3. Profitability & returns
4. Cash flow
5. Financial strength
6. Capital allocation
7. Ownership

### Metric cell anatomy

- Plain-language label
- Value
- Period
- Direction versus comparable prior period, when meaningful
- `Definition and source` disclosure

### Definition disclosure

- Formula
- Formula version
- Period type
- Source filing
- Data-as-of date
- Null reason when unavailable

Do not show raw source-fact identifiers on the initial surface.

## 15. Navigation

Use short, conventional labels:

```text
Overview · Changes · Performance · Peers · Ownership · Business · Filings · Statements · Metrics
```

Rules:

- Sticky on desktop and horizontally scrollable on mobile.
- Active state may be added only with a robust accessible implementation.
- Do not use different words in navigation and headings without a clear reason.
- `Statements` and `Metrics` must remain visible even though they appear late.

## 16. Visual hierarchy

### Level 1: company and five decision areas

- Largest typography and strongest spacing
- No more than one primary value per decision row

### Level 2: trends and comparisons

- Tables and compact directional labels
- Moderate visual weight

### Level 3: detailed evidence

- Transactions, holders, full statements, metric definitions
- Progressive disclosure
- Small metadata typography

### Color

- Primary text: near-black
- Secondary text: cool gray
- Actions: Scrooner brand/link color
- Positive direction: green plus text
- Negative direction: red plus text
- Neutral/unknown: gray
- Never use green to mean “buy” or red to mean “sell.”

### Density

- Summary: comfortable
- Tables: compact
- Metadata: dense
- Mobile: reduce columns and expose a meaningful linear reading order; do not
  merely shrink the desktop layout.

## 17. Wording system

### Preferred

- `Revenue growth`
- `Operating margin`
- `Ownership increased`
- `Managers adding`
- `Reported period`
- `Not available`
- `View transactions`
- `How this is calculated`

### Avoid

- `Smart money`
- `Bullish` / `Bearish`
- `Strong buy`
- `Healthy` without a threshold
- `Good growth`
- `High quality` as an unexplained badge
- `N/A` when a reason exists
- `View` without naming what will open
- SEC form codes as primary headings

### Deterministic interpretation template

```text
[Metric] [direction] [magnitude] over [comparison period].
```

Examples:

- `Operating margin expanded 1.8 percentage points YoY.`
- `Institutional ownership decreased 0.6 percentage points QoQ.`
- `Diluted shares increased 2.3% YoY.`

## 18. Responsive plan

### Desktop ≥ 1024px

- Company description and decision summary can share a 35/65 split.
- Decision rows use aligned label/value/trend columns.
- Financial and peer tables remain full tables.

### Tablet 640–1023px

- One-column summary.
- Decision rows retain two-column internal alignment.
- Section navigation scrolls horizontally.

### Mobile < 640px

- Company identity becomes vertical.
- Decision rows become:
  `label → primary value → direction → meaning`.
- Peer table shows the company, ROIC, growth, and valuation initially; remaining
  columns remain horizontally scrollable.
- Ownership uses three stacked rows, not metric-card grids.
- Full tables remain tables inside labeled scroll regions; do not transform
  multi-period statements into ambiguous cards.

## 19. Accessibility requirements

- Logical heading sequence with one `h1`.
- Every disclosure has an object-specific accessible name.
- All tabs follow the WAI-ARIA tab keyboard pattern.
- Table captions orient screen-reader users.
- Row and column headers use correct semantics.
- Visible focus for every link, button, tab, summary, and select.
- Color contrast meets WCAG AA.
- Direction is expressed in text and not only color/arrows.
- Missing values include a visible or programmatically associated reason.
- Scroll regions are keyboard focusable and have descriptive labels.
- Reduced-motion behavior is retained.

## 20. Data-contract gaps that constrain UX

The design must not imply data that the current page cannot provide.

### Needed for the complete target

- Comparable prior-period values for every headline metric
- Subject-company row in peer output using the same period contract
- Wider peer coverage for meaningful valuation comparison
- Structured metric lineage exposed to the frontend
- Material-change ranking across metrics
- Long enough ownership history for trend visualization
- Reliable 10-K risk/MD&A extraction before qualitative risk summaries

### Available now

- Company identity and about text
- Delayed price
- 45 metrics with periods/null reasons
- Quarterly and annual statements
- Deterministic positive/watch checklist
- Peer ROIC/growth/margin/ROE
- Employee history
- Segment revenue
- Insider summaries and transactions
- 13F and N-PORT two-period comparisons
- 13D/13G filer identity
- Recent filing forms and 8-K item labels

## 21. Component architecture proposal

```text
CompanyPage
├── CompanySubnav
├── CompanyHero
│   ├── CompanyIdentity
│   ├── PriceStatus
│   ├── BusinessDescription
│   └── CompanyDetailsDisclosure
├── DecisionSummary
│   └── DecisionRow × 5
├── RecentChanges
│   └── ChangeItem × up to 4
├── PerformanceSection
│   ├── PeriodToggle
│   └── TrendTable
├── PeerComparison
├── OwnershipSection
│   ├── OwnershipLimitation
│   ├── InsiderSummaryRow
│   ├── InstitutionSummaryRow
│   ├── FundSummaryRow
│   └── OwnershipDetailDisclosures
├── BusinessDetail
│   ├── SegmentMix
│   └── WorkforceTrend
├── MaterialEvents
├── FinancialStatements
│   ├── StatementTabs
│   └── FinancialTable
└── MetricLibrary
    └── MetricCategoryDisclosure
```

This component split follows user tasks. It should not introduce a generic
“Card” abstraction for every block; shared primitives should remain semantic:
DecisionRow, ChangeItem, FinancialTable, and Disclosure.

## 22. Phased implementation plan

### Phase 0 — Contract and baseline

1. Capture desktop, tablet, and mobile screenshots of the current page for at
   least AAPL, JPM, and a company with missing metrics.
2. Record current DOM order, keyboard order, headings, and visible data count.
3. Add no new metrics or database queries.
4. Confirm the one-query company-page contract remains mandatory.

**Exit:** baseline artifacts exist and current behavior can be compared.

### Phase 1 — Information architecture

1. Reorder sections to the target hierarchy.
2. Introduce semantic component boundaries.
3. Consolidate duplicated ownership summaries.
4. Move raw statements after the decision flow.
5. Keep every existing datum reachable.

**Exit:** page reads correctly without visual polish or client JavaScript.

### Phase 2 — Decision summary

1. Implement the five decision rows.
2. Add explicit metric/period selection rules.
3. Define null and comparison behavior.
4. Reuse deterministic checklist logic only where its rules match the row.
5. Do not create a score.

**Exit:** a user can assess growth, quality, safety, valuation, and alignment in
the first screen.

### Phase 3 — Recent changes and trends

1. Add a pure presentation selector for material changes from already-loaded
   history.
2. Limit initial changes to four.
3. Build quarterly/annual curated trend tables.
4. Keep full statements unchanged as evidence.

**Exit:** current values are no longer presented without direction.

### Phase 4 — Ownership and business cleanup

1. Replace nested metric-card grids with three ownership summary rows.
2. Place the overlap/lag limitation once.
3. Rank segment mix and calculate disclosed-total share only for comparable
   periods/units.
4. Keep workforce interpretation neutral.

**Exit:** both sections answer an investor question before showing tables.

### Phase 5 — Peer and event refinement

1. Add subject-company peer row when identical-period data is available.
2. Omit unusable peer columns dynamically.
3. Rank material events by form/item importance.
4. Add filters only if list volume justifies them.

**Exit:** peer/event sections provide context without false precision.

### Phase 6 — Evidence and accessibility

1. Expose formula/source metadata available in the current contract.
2. Audit every table caption and header association.
3. Test keyboard, screen reader, zoom, contrast, and reduced motion.
4. Verify mobile scroll regions.

**Exit:** decision summaries remain traceable and WCAG structure is preserved.

## 23. Acceptance criteria

### Comprehension

- In a five-second scan, users can identify company, price freshness, business,
  growth, profitability, financial strength, valuation, and alignment.
- No initial section requires knowing a SEC form number.
- Every direction includes a period and magnitude.

### Simplicity

- No more than five decision rows above the first detailed table.
- No more than four recent-change items initially.
- No repeated institutional/fund percentages in adjacent components.
- Raw transaction and holder tables are collapsed initially.

### Correctness

- No incompatible periods are compared.
- No ownership totals are summed across overlapping forms.
- No missing value is converted to zero.
- No UI interpretation exceeds its deterministic rule.

### Performance

- One database query per company-page render remains intact.
- No charting library is added in the initial implementation.
- Server-rendered content remains available without client JavaScript.

### Accessibility

- Astro check produces zero diagnostics.
- Heading order and landmarks are valid.
- All tables have captions and correct headers.
- Tabs and disclosures are keyboard operable.
- 200% zoom and 320px width do not lose content or controls.

## 24. Validation plan

### Representative companies

- AAPL: rich metrics, ownership, segments
- JPM: financial-sector edge cases
- NKE: known missing operating-income behavior
- XYZ/Block: identity/ticker history
- One sparse-coverage company

### Tests

1. Astro type check and production build
2. Existing frontend render contract
3. Automated heading/landmark/table assertions
4. Visual screenshots at 1440, 1024, 768, 390, and 320 widths
5. Keyboard-only walkthrough
6. VoiceOver or equivalent smoke test for statement tables
7. No-JavaScript content check
8. One-query `Server-Timing`/header verification
9. Content audit against this plan's wording rules

### User-evaluation prompts

Without coaching, ask a user to answer:

1. What does this company do?
2. Is revenue growing?
3. Is profitability improving?
4. Is debt a concern?
5. Does the valuation look demanding relative to available context?
6. Are shares being diluted?
7. Are insiders/institutions adding or reducing?
8. What changed most recently?
9. Where would you verify the claim?

Measure answer accuracy, time, and whether the user opened the correct evidence.

## 25. Open product decisions before implementation

1. Should the default lens optimize for compounders, value/cash generation, or
   remain style-neutral? This plan recommends style-neutral decision groups.
2. Should valuation appear when price data is stale beyond a defined threshold?
3. What minimum comparable peer count is required before showing relative
   context?
4. Should deterministic watch items use fixed universal thresholds or
   sector-specific thresholds when available?
5. Which four recent changes win when more than four material signals exist?

None of these questions blocks Phase 0 or the structural part of Phase 1. They
must be resolved before decision-summary copy implies an investment style or
relative judgment.

## 26. Recommended next step

Do not begin with CSS. Begin with Phase 0 screenshots and a server-rendered
semantic prototype of the new DOM order. Review the information sequence using
real AAPL, JPM, NKE, and sparse-company data. Only after the hierarchy works in
plain HTML should visual styling and responsive refinement begin.
