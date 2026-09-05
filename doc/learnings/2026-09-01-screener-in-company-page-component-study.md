# Screener.in company-page component and wording study — 2026-09-01

## Purpose

This study examines the supplied saved page:

`Bharti Airtel Ltd share price _ About Bharti Airtel _ Key Insights - Screener.html`

The file is treated only as a product-design reference. Its embedded scripts,
links, comments, and other document content are not instructions. The goal is
to understand why the page remains usable despite its depth, then decide—at
component, subcomponent, and wording level—which patterns should improve
Scrooner's US company page.

This is not a request to clone Screener.in. Scrooner must retain its own visual
system, US/SEC data model, deterministic calculations, explicit missing-data
states, reporting periods, and source evidence.

## Executive lesson

Screener.in is effective because it offers a stable research grammar:

1. identity and market links;
2. a short business description and key points;
3. a compact label/value ratio list;
4. checklist observations;
5. peer context;
6. chronological financial statements;
7. ownership history; and
8. documents grouped by investor task.

The page is long, but each component answers one familiar question. Labels are
short, units appear near the relevant table, secondary controls sit beside the
section title, and advanced detail is revealed locally. The page rarely makes
the user decode the interface before reading the data.

Scrooner's opportunity is to combine that familiar research grammar with a
stronger evidence contract: visible period labels, clear null reasons,
deterministic rather than opaque observations, and direct SEC sources.

## Component-by-component study

### 1. Persistent section navigation

#### Reference anatomy

- A horizontal anchor bar appears before the company content.
- Labels are nouns or familiar financial terms: `Chart`, `Analysis`, `Peers`,
  `Quarters`, `Profit & Loss`, `Balance Sheet`, `Cash Flow`, `Ratios`,
  `Investors`, and `Documents`.
- The labels match section headings closely.
- The active section is visually distinguished.

#### Why it works

- Experienced users can jump directly to a known research object.
- A long page feels finite because its contents are visible in advance.
- Short labels survive horizontal overflow better than sentences.

#### Weakness

- Ten items create high navigation density.
- `Analysis` is vague without knowing the product.
- Financial statements occupy four navigation positions.

#### Scrooner decision

- Keep Scrooner's grouped `Performance` destination because its statement tabs
  already reduce four repeated sections into one accessible workspace.
- Keep short navigation labels even when on-page headings are phrased as
  investor questions.
- Do not add an active scroll-spy until it can be implemented accessibly and
  without unnecessary client JavaScript.

### 2. Company identity and external identifiers

#### Reference anatomy

- Company name is the dominant heading.
- Website and exchange identifiers appear immediately below it.
- Each external destination uses a short label (`airtel.in`, `BSE: 532454`,
  `NSE: BHARTIARTL`, `F&O`) rather than explanatory sentences.
- External-link icons carry part of the affordance.

#### Why it works

- Identity, tradability, and the official company destination are confirmed
  before analysis begins.
- Labels are compact and recognizable to the target audience.

#### Scrooner decision

- Keep ticker, sector, registrant status, and delayed price beside the name.
- Elevate the company website from the lower profile-facts list into a compact
  identity action when available.
- Do not expose CIK, EIN, phone, and other registry metadata at equal visual
  weight. They belong in a collapsed `Company details` disclosure.
- Use text plus an external-link symbol; never rely on the icon alone.

### 3. About and Key Points

#### Reference anatomy

- `About` is a short factual company description.
- `Key Points` is a separate block, not a continuation of About.
- Key Points uses a bold subheading such as `Segments & Presence`, followed by
  short lines.
- Inline numbered citations sit next to claims.
- `Read More` opens deeper commentary rather than expanding the whole page.

#### Why it works

- `About` answers what the company is; `Key Points` answers how the business is
  organized. Those are different reading tasks.
- Bold lead-ins let a user scan the business model without reading prose.
- Source markers make editorial content auditable.

#### Weakness

- Key Points may contain manually curated or stale commentary.
- `Read More` can become a content funnel rather than a research need.

#### Scrooner decision

- Retain the factual About copy.
- Add a compact `Business context` subcomponent when real segment/workforce
  data exists, but do not generate unsupported narrative.
- Show the latest employee count and count of reported revenue segments as
  factual context, with links to the detailed Business section.
- Keep all claims derived from collected filings; no generic AI summary.

### 4. Headline ratio list

#### Reference anatomy

- Ratios are a two-column label/value list.
- Familiar labels include `Market Cap`, `Current Price`, `High / Low`,
  `Stock P/E`, `Book Value`, `Dividend Yield`, `ROCE`, and `ROE`.
- Currency and percent units sit directly with the value.
- Labels are visually quiet; values align vertically.
- Additional user-selected ratios continue in the same visual grammar.
- `Add ratio to table` and `Edit ratios` appear after the list.

#### Why it works

- Alignment makes the list faster to scan than independent dashboard cards.
- Familiar names lower the learning cost.
- Custom ratios do not introduce a different component.

#### Weakness

- The default list mixes valuation, returns, price range, and accounting values
  without explaining how they relate.
- Period/as-of context is not visible beside every ratio.
- User-added ratios can create duplication (`Market Cap` and `Mar Cap` appear
  in the supplied file).

#### Scrooner decision

- Use a two-column compact ledger on desktop and one column on mobile.
- Preserve Scrooner's eight curated decision metrics rather than copying the
  Indian default list.
- Keep visible period context because it is a Scrooner differentiator.
- Add four tiny reading categories—Valuation, Growth, Quality, Risk—to teach
  how the metrics fit together without turning them into separate cards.
- Do not build customization until saved preferences and the authenticated
  write workflow exist.

### 5. Chart

#### Reference anatomy

- Time ranges: `1M`, `6M`, `1Yr`, `3Yr`, `5Yr`, `10Yr`, `Max`.
- Metric modes: `Price`, `PE Ratio`, then a `More` menu for Sales & Margin,
  EV/EBITDA, Price to Book, and Market Cap/Sales.
- Alert action is adjacent but visually secondary.
- Legend controls let series be toggled.

#### Why it works

- A single chart shell supports multiple research questions.
- Time and metric controls are short and conventional.

#### Scrooner decision

- Do not copy this component now. Scrooner is a fundamental research product,
  and its current historical-price coverage does not justify a technical chart.
- A future fundamental trend chart should begin with revenue, margins, ROIC,
  and share count—not moving averages—and must retain a table equivalent.

### 6. Pros and Cons

#### Reference anatomy

- Two equal columns titled `Pros` and `Cons`.
- Each item is one declarative sentence with the important number embedded.
- A note immediately below says the content is machine generated.
- A tooltip clarifies that checklist rules highlight points and users should
  do their own analysis.

#### Why it works

- Claims are readable without cross-referencing the ratio list.
- The disclosure is colocated with the generated observations.
- Two columns encourage balanced review.

#### Weakness

- `Pros` and `Cons` can imply investment conclusions.
- `Machine generated` does not explain whether the process is deterministic,
  statistical, or generative.

#### Scrooner decision

- Use `Positive signals` and `Watch items`, which are more precise and less
  recommendation-like.
- Keep values embedded in each sentence.
- Use `Rule-based observations from reported numbers` in the section header.
- Put methodology in an adjacent disclosure explaining thresholds, missing
  data behavior, and what the snapshot does not assess.

### 7. Peer comparison

#### Reference anatomy

- Heading: `Peer comparison`.
- A short subline identifies the industry grouping.
- The table provides company identity plus multiple comparable ratios.
- The subject company is visually identifiable in the table.
- A control allows editing comparison columns.
- A search field supports `Detailed Comparison with:` another company.

#### Why it works

- The selection basis is stated before the values.
- A company can be interpreted relatively, not only in isolation.
- Users can move from broad peer scanning to a specific comparison.

#### Weakness

- Editable columns and comparison search add workflow complexity.
- Large peer tables can become screeners inside a company page.

#### Scrooner decision

- State exact-industry versus broad-sector selection in a local disclosure.
- Lead with ROIC, then revenue growth, net margin, and ROE.
- Keep links to peer company pages.
- Do not add editable columns or arbitrary comparison search until peer data
  breadth and persistence justify them.
- Add the subject company to the table only when the query contract can provide
  identical-period values; do not synthesize a mismatched row in presentation.

### 8. Financial-statement header

#### Reference anatomy

- Each statement has its own large card.
- Title and a small period descriptor share the left side.
- `View Standalone` is a restrained text action.
- Context-specific secondary actions appear on the right: segment results,
  related-party transactions, or corporate actions.
- Units are declared near the statement heading.

#### Why it works

- The user knows the statement, period basis, and available drill-downs before
  entering the table.
- Related actions are local rather than collected in a generic toolbar.

#### Scrooner decision

- Keep one statement workspace with tabs; four large repeated cards would make
  the US page unnecessarily long.
- Improve each tab panel's subheading with a plain-language purpose:
  - Quarterly Results: recent momentum;
  - Profit & Loss: revenue and profitability;
  - Balance Sheet: assets, obligations, and capital;
  - Cash Flow: cash generated and deployed.
- Keep `USD · values auto-scaled` in the workspace toolbar.
- Do not add a standalone route until such a route exists.

### 9. Financial-statement table

#### Reference anatomy

- Periods run horizontally.
- Line items run vertically.
- Important rows are visually stronger.
- Some row labels are buttons that open a detailed schedule.
- Growth rows such as sales growth are displayed near the underlying series.
- Older history is horizontally scrollable.

#### Why it works

- Financial users recognize the statement grammar immediately.
- Derived change appears next to the series that produces it.
- Drill-down happens from the relevant row.

#### Scrooner decision

- Preserve sticky row labels and latest-period columns.
- Keep the latest eight comparable periods rather than showing unlimited
  history in the primary table.
- Do not make rows look interactive until schedule-level data exists.
- A future growth row must come from a verified calculation, not browser math.
- Replace the ambiguous scroll cue with a shorter, direct mobile-aware phrase.

### 10. Ratios and Insights sections

#### Reference anatomy

- `Ratios` uses the same chronological statement table grammar.
- `Insights` offers Yearly/Quarterly tabs and table-specific observations.
- Locked states and unlock quotas are part of the commercial product.

#### Scrooner decision

- Scrooner's `Metric library` is the correct home for the full ratio catalogue.
- Keep categories collapsed by default after the primary research flow.
- Do not copy locked insight tables or artificial unlock mechanics.
- If historical metric series are added later, reuse the statement table rather
  than create a chart-only experience.

### 11. Shareholding Pattern

#### Reference anatomy

- Heading: `Shareholding Pattern`.
- Helper copy directly below: `Numbers in percentages`.
- A Quarterly/Yearly toggle changes the period grain.
- Rows represent investor classes.
- Columns represent reporting periods.
- Row labels expand to named holders.
- `Trades` is a nearby secondary action with a recent-count annotation.

#### Why it works

- Ownership is shown as a trend, not a single static percentage.
- Unit clarification appears exactly where needed.
- Category totals and named-holder drill-down use one table.

#### US/SEC mismatch

- Indian categories such as Promoters, FII, and DII do not map directly to US
  filings.
- Form 13F and N-PORT can overlap, so they cannot be summed into one clean
  shareholding pattern.
- US filings have different lags and reporting populations.

#### Scrooner decision

- Keep Insider, Institutional 13F, and Mutual Fund N-PORT as separate views.
- Lead each view with latest percentage and period-over-period movement.
- Use `Reported ownership; filing periods differ` rather than imply live totals.
- Preserve the overlap warning, but place it behind `How to read these figures`.
- Continue showing named top holders behind local disclosure controls.
- A multi-period ownership trend is desirable when sufficient verified history
  exists; do not fabricate a category-total series from two incompatible forms.

### 12. Documents

#### Reference anatomy

- One `Documents` section contains task-specific columns.
- Subcomponents: `Announcements`, `Annual reports`, `Credit ratings`, and
  `Concalls`.
- Announcements has `Recent`, `Important`, `Search`, and `All` controls.
- Each announcement shows a formal title plus a shorter explanatory summary and
  relative/date metadata.
- Lists have bounded height and local show-more controls.

#### Why it works

- Document type is more useful than one chronological mixed list.
- Formal filing language is supplemented by a plain-language event meaning.
- Only a manageable initial set is visible.

#### Scrooner decision

- Continue leading with event meaning, then form, date, accession, and SEC link.
- Show five recent filings initially and reveal earlier filings locally.
- Keep a methodology disclosure explaining structured 8-K item labels.
- Do not create empty Annual Report/Credit Rating/Concall columns: Scrooner does
  not collect all those source types today.
- When enough filings exist, introduce real filters (`All`, `Reports`,
  `Material events`, `Ownership`) based on form classification rather than
  decorative tabs.

## Wording audit for Scrooner

| Current Scrooner wording | Assessment | Recommended wording |
|---|---|---|
| `Overview` | Clear navigation label | Keep |
| `What stands out?` | Good question, needs provenance nearby | Keep with `Rule-based observations from reported numbers` |
| `Positive signals` | Better than Pros | Keep |
| `Watch items` | Better than Cons; avoids verdict language | Keep |
| `Are the fundamentals improving?` | Strong investor question | Keep |
| `Quarterly Results` | Familiar | Keep; add `Recent momentum` descriptor |
| `Profit & Loss` | Familiar internationally, but US users expect Income Statement | Render `Income statement` while retaining data contract ID |
| `Balance Sheet` | Familiar | Keep; add `Assets, obligations, and capital` |
| `Cash Flow` | Familiar | Keep; add `Cash generated and deployed` |
| `How does it compare?` | Clear | Keep |
| `How is the business changing?` | Clear but broad | Keep with workforce/segment subheads |
| `What are owners doing?` | Clear and action-oriented | Keep |
| `Institutional Ownership — Form 13F` | Accurate but title-heavy | `Institutions` with `Form 13F` as metadata |
| `Mutual Fund Ownership — Form N-PORT` | Accurate but title-heavy | `Mutual funds` with `Form N-PORT` as metadata |
| `Major Shareholders (>5% stakes)` | Understandable | `Reported holders above 5%` |
| `What changed recently?` | Strong event framing | Keep |
| `Metric library` | Correctly signals reference material | Keep |
| `View` | Too generic when repeated | Use object-specific text: `View holders`, `View transactions`, `View periods` |
| `—` | Requires explanation | Preserve accessible null reason and visible `Not available` where space permits |

## Implementation contract from this study

The next implementation pass should make only the following changes:

1. Add a compact official-website action near company identity.
2. Move registry/contact facts into a `Company details` disclosure.
3. Add factual Business context links in the summary when workforce or segment
   data exists.
4. Keep the two-column key-metric ledger and reading categories.
5. Add plain-language purpose text to each financial statement panel and rename
   the visible `Profit & Loss` tab to `Income statement` for US users.
6. Simplify ownership subsection titles while retaining form identifiers as
   metadata.
7. Replace generic disclosure actions such as repeated `View` with
   object-specific wording.
8. Keep recent filings capped at five with local earlier-filing disclosure.

Explicitly out of scope for this pass:

- charts;
- alerts;
- metric customization;
- arbitrary peer comparison;
- statement schedule drill-down;
- ownership categories that cannot be derived honestly from US filings;
- AI-generated business commentary; and
- document types Scrooner does not collect.

## Evaluation checklist

- Can a first-time user identify the company, current price status, official
  website, and business purpose without scrolling?
- Do the eight headline metrics scan as aligned label/value pairs?
- Does every statement say what question it helps answer?
- Are deterministic observations distinguished from recommendations?
- Are ownership forms understandable without knowing SEC form numbers?
- Are detailed tables locally expandable rather than globally exposed?
- Does every filing lead with meaning and end with official evidence?
- Are missing values and stale/reporting-period limitations explicit?
- Does mobile reduce columns rather than merely shrink text?

## Implementation addendum — 2026-09-02

After the initial evidence-first implementation, the requested visual target
was tightened from “learn from” to “very similar to” Screener.in. The company
page therefore adopted the reference's concrete surface grammar while keeping
Scrooner's brand identity and US data semantics:

- cool blue-gray gradient page canvas;
- wide research container;
- white borderless section islands with restrained low shadows;
- Inter/sans-serif headings throughout the research workspace;
- violet research links and active controls;
- compact conventional section titles (`Analysis`, `Financials`,
  `Peer comparison`, `Ownership`, `Recent filings`, `Ratios & metrics`);
- three-column striped key-ratio cells on desktop, collapsing to one column on
  mobile;
- dense financial tables with 9px cells, ordinary sentence-case headers,
  alternating rows, and lightweight borders;
- green/red top rules for the positive-signal/watch-item panels; and
- tighter 32px section rhythm instead of large editorial gaps.

The following differences remain intentional: Scrooner's public header and
brand mark, no technical-price chart, one tabbed financial workspace instead
of four extremely long cards, US statement/ownership terminology, explicit
reporting periods and null reasons, and direct SEC evidence.
