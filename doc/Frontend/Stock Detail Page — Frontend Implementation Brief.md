# Stock Detail Page — Frontend Implementation Brief

## 1. What I Want

I am sharing the HTML of this Screener.in stock page as a **functional and UX reference**:

`https://www.screener.in/company/RELIANCE/consolidated/`

The objective is **NOT to blindly copy Screener's HTML, CSS, branding, colours or code**.

I want us to understand:

- how the page is structured
- what information is shown
- how dense financial data is presented
- how users navigate between sections
- how financial tables behave
- which rows are expandable
- how consolidated vs standalone data is handled
- how mobile horizontal tables should work
- how loading/empty states should behave
- how reusable this structure can be across thousands of companies

Then build **our own reusable Stock Details Page UI** using our design system and our APIs.

Think of Screener as the **information architecture and interaction benchmark**, not as the final visual design.

---

# 2. Core Product Goal

This page should answer:

> "I searched for a company. Now give me everything important I need to understand and analyse that company without jumping across multiple pages."

The page should work for:

- a beginner checking basic company information
- an investor looking at financial statements
- an analyst comparing multi-year performance
- a user researching valuation
- a user comparing the company with peers
- a user examining ownership/shareholding
- a user reviewing company documents

The page should therefore be:

**Information-dense, but extremely easy to scan.**

Do not turn it into a collection of oversized cards with huge empty spaces.

Financial information density is important.

---

# 3. Important Engineering Principle

Do NOT build this page specifically for Reliance.

Everything must be component-driven and data-driven.

The same frontend should render:

- Reliance
- HDFC Bank
- Infosys
- Apple
- Microsoft
- NVIDIA
- any other supported stock

Company-specific values must come from API responses.

There should be effectively zero hardcoded company financial data in the components.

---

# 4. Suggested Page Architecture

The overall page should be:

```text
Stock Detail Page
│
├── Stock Header
├── Sticky Section Navigation
│
├── Company Summary
│   ├── Company Information
│   ├── About
│   ├── Key Points
│   └── Key Metrics
│
├── Price / Financial Chart
│
├── Analysis
│
├── Peer Comparison
│
├── Quarterly Results
│
├── Profit & Loss
│
├── Balance Sheet
│
├── Cash Flow
│
├── Financial Ratios
│
├── Shareholding / Ownership
│
└── Documents
```

Each major section should be implemented as an independent component.

Example:

```text
StockPage
 ├─ StockHeader
 ├─ StockSectionNav
 ├─ StockOverview
 ├─ StockChart
 ├─ StockAnalysis
 ├─ PeerComparison
 ├─ QuarterlyFinancials
 ├─ IncomeStatement
 ├─ BalanceSheet
 ├─ CashFlowStatement
 ├─ FinancialRatios
 ├─ Shareholding
 └─ CompanyDocuments
```

---

# 5. Sticky Section Navigation

At the top of the stock page, after the primary site navigation/header, create an in-page navigation.

Suggested items:

- Overview / Summary
- Chart
- Analysis
- Peers
- Quarters
- Profit & Loss
- Balance Sheet
- Cash Flow
- Ratios
- Shareholding
- Documents

Clicking an item should smoothly scroll to that section.

Example:

```text
Summary | Chart | Analysis | Peers | Quarters | P&L |
Balance Sheet | Cash Flow | Ratios | Shareholding | Documents
```

### Expected behaviour

As the user scrolls:

- section navigation remains sticky
- currently visible section becomes active
- URL hash may update
- clicking a tab scrolls to the correct section
- sticky header must not cover section headings

Example:

`/stocks/reliance-industries#profit-loss`

This is especially useful for sharing deep links.

### Mobile

Make the navigation horizontally scrollable.

Do not squeeze 10+ navigation labels into two lines.

---

# 6. Stock Header

The header should immediately establish:

- company name
- ticker
- exchange
- current/last price
- price movement
- percentage movement
- data timestamp/status

Example:

```text
Reliance Industries Ltd

₹1,322
+₹19.50 (+1.50%)

NSE: RELIANCE
BSE: 500325

Last updated: 04 Sep 2026
```

If our price is delayed, explicitly show it:

```text
15 min delayed
```

or:

```text
Previous close
```

Never allow users to incorrectly interpret delayed/end-of-day data as live data.

---

# 7. Price Movement

Price change visual treatment:

Positive:

```text
+1.50%
```

Negative:

```text
-1.50%
```

Neutral:

```text
0.00%
```

Use our standard positive/negative colour tokens.

Do not hardcode arbitrary colours inside individual components.

---

# 8. Header Actions

Depending on product scope/API availability, support actions like:

- Add to Watchlist
- Set Alert
- Share
- Export
- Compare

Do not implement Screener-specific features such as "Notebook" simply because they exist in the HTML.

Only implement actions relevant to our product.

---

# 9. Company Identity / External Identifiers

Where available display:

```text
NSE: RELIANCE
BSE: 500325
ISIN: INE002A01018
```

For US stocks:

```text
NASDAQ: AAPL
CUSIP: ...
```

Do not leave empty labels.

If data doesn't exist, hide that item.

---

# 10. Company Overview

The first major content block should contain two concepts:

### A. Company Description

A short explanation of what the company does.

Example:

```text
About Reliance Industries
```

Then 2–4 lines.

If the description is long:

```text
Read more
```

should expand it inline.

Do not redirect the user to another page just to read the company description.

---

# 11. Key Company Points

Create a separate block for important company-specific observations.

Possible examples:

- major subsidiaries
- business segments
- revenue concentration
- ownership structure
- geographic exposure
- acquisitions
- material structural information

This should be API/CMS-driven.

It is different from "About".

**About = what the company is.**

**Key Points = important things an investor should know about the company.**

---

# 12. Key Metrics

Create a compact metrics area.

Initial metrics can include:

```text
Market Cap
Current Price
52W High
52W Low
P/E
P/B
Book Value
Dividend Yield
ROE
ROCE
Face Value
```

Depending on market/company, additional metrics may include:

```text
Enterprise Value
EV/EBITDA
EPS
PEG
Debt / Equity
Current Ratio
Free Cash Flow
Revenue
Net Profit
```

### Important

Do not make each metric a giant card.

This area needs to remain compact.

Something like:

```text
Market Cap          ₹17.89L Cr
Current Price       ₹1,322
52W High / Low      ₹1,612 / ₹1,250
P/E                 23.9
Book Value          ₹668
Dividend Yield      0.45%
ROCE                10.3%
ROE                 8.91%
```

is preferable to 10 oversized tiles.

---

# 13. Metric Formatting

Frontend should handle formatting centrally.

Examples:

```text
17890010000000
```

should not appear directly.

It should display according to market/locale rules.

India examples:

```text
₹17.89 Lakh Cr
₹1,322.50
₹88,167 Cr
```

US examples:

```text
$3.42T
$418.75
$97.3B
```

Percent:

```text
8.91%
```

Ratio:

```text
23.9x
```

where appropriate.

Frontend should receive either:

1. raw value + metadata, or
2. raw + formatted value from backend.

But formatting rules should be consistent across the entire application.

---

# 14. Null Data Handling

Never render:

```text
P/E: null
ROE: undefined
Dividend Yield: NaN
```

Depending on importance:

Either:

```text
—
```

or hide the metric entirely.

Use one consistent rule.

---

# 15. Chart Section

The chart should be an actual reusable interactive component.

Time ranges:

```text
1M
6M
1Y
3Y
5Y
10Y
MAX
```

Do not fetch all historical data on every button click if it can be cached efficiently.

---

# 16. Chart Metrics

The initial/default chart:

```text
Price
```

Eventually support additional analytical overlays/modes such as:

```text
Price
P/E
P/B
EV/EBITDA
Sales & Margin
Market Cap / Sales
```

Price mode may additionally support:

```text
50 DMA
200 DMA
Volume
```

Do not tightly couple the chart library with stock-page business logic.

Build something approximately like:

```text
<StockChart
  symbol={symbol}
  range={range}
  metric={metric}
  series={series}
/>
```

---

# 17. Chart Loading

When range changes:

Do NOT blank the entire section.

Keep chart dimensions fixed and show a chart-level loader/skeleton.

Avoid layout shift.

---

# 18. Chart Error State

If historical price data fails:

```text
Unable to load chart data.
Retry
```

The rest of the stock page should remain usable.

A failed chart API must not crash the complete page.

---

# 19. Analysis Section

Create an investor analysis/insights section.

Conceptually similar to:

```text
Strengths
Weaknesses
```

or:

```text
Pros
Cons
```

Examples:

```text
Strength
Revenue has grown consistently over 5 years.

Risk
ROE has remained below the sector median.
```

These observations may eventually come from:

- rule engine
- research data
- backend calculations
- AI layer

The frontend should therefore receive generic insight objects.

Example:

```json
{
  "type": "positive",
  "text": "Revenue CAGR has remained strong over the last 5 years."
}
```

Do not hardcode analysis logic on frontend.

---

# 20. Analysis Disclaimer

If insights are machine-generated/algorithmic, provide an appropriate disclaimer.

For example:

```text
Insights are generated using financial data and predefined analytical rules and should not be considered investment advice.
```

---

# 21. Peer Comparison

Create a peer comparison section.

Top of section can show the company's classification:

```text
Sector
Energy

Industry
Oil, Gas & Consumable Fuels

Sub-industry
Refineries & Marketing
```

If applicable, show indices the company belongs to.

---

# 22. Peer Comparison Table

The current company must be visually distinguishable from peers.

Suggested columns:

```text
Company
Price
Market Cap
P/E
P/B
ROE
ROCE
Dividend Yield
Revenue Growth
Profit Growth
```

Columns may ultimately become configurable.

Architecture therefore should not assume exactly 8 permanent metrics.

Conceptually:

```json
{
  "columns": [],
  "rows": []
}
```

---

# 23. Peer Navigation

Company names in peer table should be clickable.

Example:

```text
Tata...
ONGC
BPCL
```

Clicking a company should open:

```text
/stocks/{company-slug}
```

Prefer internal routing without a full application reload.

---

# 24. Current Company Highlight

If user is viewing Reliance:

```text
Reliance Industries
```

must be visually highlighted in the peer table.

Do not make users search for the company inside its own comparison table.

---

# 25. Financial Tables — Global Rule

The most important reusable frontend component on this page is the financial table.

We should NOT separately implement completely different table code for:

- quarterly results
- P&L
- balance sheet
- cash flow
- ratios
- ownership

They should reuse a strong generic financial-table system wherever practical.

Conceptually:

```text
FinancialTable
 ├── title
 ├── subtitle
 ├── periods[]
 ├── rows[]
 ├── expandable rows
 ├── formatting
 ├── sticky columns
 └── responsive behaviour
```

---

# 26. Financial Table UX

Desktop:

- metric names on left
- time periods horizontally
- values right aligned
- first column remains easy to follow
- consistent row heights
- subtle separators
- minimal unnecessary borders

Example:

```text
               FY22     FY23     FY24     FY25

Revenue        7.2L     8.7L     9.0L     9.6L
Expenses       6.0L     7.3L     7.4L     8.0L
EBITDA         ...
Net Profit     ...
```

---

# 27. Mobile Financial Tables

Do NOT transform large financial statements into hundreds of vertically stacked cards.

Use horizontal scrolling.

The metric-name column should ideally remain sticky while periods horizontally scroll.

Example:

```text
| Metric        | FY23 | FY24 | FY25 | → |
```

This is essential.

Financial tables naturally require horizontal movement on small screens.

---

# 28. Quarterly Results

Create:

```text
Quarterly Results
```

with quarter periods horizontally.

Example:

```text
Jun 2025
Sep 2025
Dec 2025
Mar 2026
Jun 2026
```

Core rows:

```text
Revenue / Sales
Expenses
Operating Profit
Operating Margin %
Other Income
Interest
Depreciation
Profit Before Tax
Tax %
Net Profit
EPS
```

Backend data may contain additional rows.

Frontend should render based on the row configuration returned.

---

# 29. Expandable Quarterly Rows

Rows like:

```text
Sales +
Expenses +
Other Income +
Net Profit +
```

may contain children.

Clicking `+` should expand a breakdown.

Example:

```text
Revenue
  ├─ Refining
  ├─ Retail
  ├─ Digital
  └─ Other
```

The interaction should occur inline.

Do not navigate away.

---

# 30. Expansion Contract

A financial row should be able to conceptually support:

```json
{
  "label": "Revenue",
  "values": [],
  "expandable": true,
  "children": []
}
```

If the API returns children lazily:

```text
click +
→ call schedule/breakdown API
→ loader inside row
→ render child rows
```

Do not reload the complete statement.

---

# 31. Consolidated vs Standalone

Very important.

Where both datasets exist, clearly indicate:

```text
Consolidated
```

and allow:

```text
View Standalone
```

or use a toggle:

```text
Consolidated | Standalone
```

I prefer the toggle approach if the API structure supports it.

The user must always know which dataset they are viewing.

This applies to:

- Quarterly Results
- Profit & Loss
- Balance Sheet
- Cash Flow
- Ratios

---

# 32. Preserve Selection

If possible, when the user changes:

```text
Consolidated → Standalone
```

the selection should apply consistently to subsequent financial sections.

Do not make users switch it six times.

This can be stored in page-level state:

```text
financialMode = consolidated | standalone
```

---

# 33. Profit & Loss

Create:

```text
Profit & Loss
```

Use annual financial periods.

Example:

```text
FY2018
FY2019
...
FY2026
TTM
```

Possible rows:

```text
Revenue
Expenses
Operating Profit
OPM %
Other Income
Interest
Depreciation
PBT
Tax
Net Profit
EPS
Dividend Payout %
```

---

# 34. TTM

If TTM is provided, visually distinguish it from audited financial-year data.

Do not assume:

```text
TTM = latest FY
```

They are separate periods.

---

# 35. Growth Summary

Below/alongside P&L, support calculated summaries.

Examples:

### Revenue Growth

```text
3Y CAGR
5Y CAGR
10Y CAGR
TTM Growth
```

### Profit Growth

```text
3Y CAGR
5Y CAGR
10Y CAGR
TTM Growth
```

### Return metrics

Potential:

```text
Stock Price CAGR
ROE
```

This should also be data-driven.

---

# 36. Balance Sheet

Create:

```text
Balance Sheet
```

Possible rows:

```text
Equity Capital
Reserves
Borrowings
Other Liabilities
Total Liabilities

Fixed Assets
CWIP
Investments
Other Assets
Total Assets
```

Support expandable rows such as:

```text
Borrowings +
Other Liabilities +
Fixed Assets +
Other Assets +
```

---

# 37. Balance Sheet Integrity

Do not calculate totals on frontend unless explicitly required.

Backend should preferably supply:

```text
Total Assets
Total Liabilities
```

Frontend is responsible for display, not financial-statement accounting logic.

---

# 38. Cash Flow

Create:

```text
Cash Flow
```

Core rows:

```text
Cash from Operating Activities
Cash from Investing Activities
Cash from Financing Activities
Net Cash Flow
Free Cash Flow
```

Possible calculated ratios can also be shown, for example:

```text
CFO / Operating Profit
```

---

# 39. Negative Numbers

Financial-table negative values must be distinguishable but do not overuse aggressive red styling.

Example:

```text
-₹12,450 Cr
```

Formatting should remain legible.

Parentheses can be considered depending on our financial-design convention:

```text
(12,450)
```

Pick one convention globally.

---

# 40. Financial Ratios

Create:

```text
Ratios
```

Possible rows:

```text
Debtor Days
Inventory Days
Payable Days
Cash Conversion Cycle
Working Capital Days
ROCE
ROE
```

The actual list must come from backend/configuration.

Do not create stock-specific frontend logic.

---

# 41. Shareholding / Ownership

Create:

```text
Shareholding Pattern
```

or for international support potentially:

```text
Ownership
```

Provide separate views:

```text
Quarterly
Yearly
```

Possible rows for Indian equities:

```text
Promoters
FII / FPI
DII
Government
Public
Number of Shareholders
```

For US stocks, backend may provide different holder categories.

Therefore frontend needs a generic holder-category structure.

---

# 42. Shareholding Percentage Formatting

Ownership:

```text
50.48%
17.19%
21.10%
```

Number of shareholders:

```text
4,651,863
```

Do not append `%` to non-percentage rows.

Formatting metadata should make this explicit.

---

# 43. Expandable Ownership Rows

Rows such as:

```text
Promoters +
FII +
DII +
Public +
```

can eventually show underlying major holders.

Architecture must allow child rows.

Example:

```text
FII
 ├─ Fund A
 ├─ Fund B
 └─ Fund C
```

---

# 44. Documents

Create a company documents/disclosures section.

The frontend should be generic enough for multiple document types.

Possible categories:

```text
Announcements
Annual Reports
Credit Ratings
Earnings Calls / Concalls
Transcripts
Investor Presentations
```

---

# 45. Announcements

Each announcement item should support:

```text
Title
Date
Short summary
Source
Document link
Category
Importance
```

Example UI:

```text
28 Aug 2026

Reliance announces...

Short summary of the disclosure.

View Filing →
```

Avoid displaying raw exchange metadata unnecessarily.

---

# 46. Announcement Filtering

Support, when backend makes the data available:

```text
Recent
Important
All
Search
```

Search should ideally operate against API/server-side data if document count becomes large.

---

# 47. Annual Reports

Display reports in descending order:

```text
Annual Report 2026
Annual Report 2025
Annual Report 2024
...
```

Click should open/download the original source document.

Clearly identify source where relevant:

```text
BSE
NSE
SEC
Company IR
```

---

# 48. Earnings / Concalls

When available, support:

```text
Transcript
AI Summary
Investor Presentation
Audio / Recording
```

This architecture will eventually become useful for our own AI/research layer.

Do not build every AI functionality in frontend now.

Just keep the component architecture extensible.

---

# 49. Section IDs

Each major page section should have a permanent semantic identifier.

For example:

```text
#overview
#chart
#analysis
#peers
#quarterly-results
#profit-loss
#balance-sheet
#cash-flow
#ratios
#shareholding
#documents
```

Do not use random/generated DOM IDs for these anchors.

---

# 50. API Independence

Components should not directly contain hardcoded API URLs scattered throughout JSX.

Avoid:

```javascript
fetch("/api/reliance/quarter-results")
```

inside presentation components.

Prefer:

```text
service layer
        ↓
query/data hook
        ↓
normalised data
        ↓
component
```

Example:

```text
useStockFinancials(symbol)
useStockPeers(symbol)
useStockOwnership(symbol)
useStockDocuments(symbol)
```

Exact implementation depends on our existing architecture.

---

# 51. Independent API Loading

Ideally the entire stock page should NOT wait for every API before rendering.

Example:

```text
Company Header API       → render
Summary API              → render
Chart API                → render
Financials API           → render
Peers API                → render
Documents API            → render
```

Slow documents should not block current price and key metrics.

---

# 52. Lazy Loading

Sections much lower on the page can be lazy-loaded when useful.

Particularly:

- documents
- old historical datasets
- shareholder breakdown
- peer details

But avoid obvious delays once the user reaches the section.

Prefetching around viewport proximity is acceptable.

---

# 53. Skeletons

Use skeletons that roughly match the final shape.

Examples:

### Header

```text
████████████
██████
```

### Metrics

multiple compact rows

### Tables

column/row skeleton

Do not use a single giant spinner for the entire page.

---

# 54. Empty State

There is an important difference between:

**Loading**

and

**No data available.**

Example empty state:

```text
Shareholding data is not available for this company.
```

Do not show an infinite skeleton if API successfully returned no records.

---

# 55. API Error Handling

Every section should fail independently.

Example:

```text
Unable to load peer comparison.

Retry
```

The page must continue functioning.

A failed document endpoint must never make the stock page show a 500 screen.

---

# 56. Responsive Behaviour

Breakpoints should follow our design system.

### Desktop

- wide content container
- compact metric layouts
- full section navigation
- tables use maximum available horizontal space

### Tablet

- columns may collapse
- navigation scrolls horizontally
- financial tables remain tables

### Mobile

- stock header simplified
- actions condensed
- nav horizontally scrollable
- horizontal financial tables
- sticky first column where feasible
- long descriptions collapsed
- no microscopic text

---

# 57. Do Not Hide Important Financial Data on Mobile

Mobile should not mean:

```text
Desktop: 12 years
Mobile: only 3 years
```

unless product explicitly decides this.

The preferred behaviour is:

```text
horizontal scroll
```

allowing access to the full dataset.

---

# 58. Number Alignment

Financial values must be right aligned.

Example:

```text
Revenue           85,234
Net Profit         7,321
EPS                34.22
```

This makes comparisons materially easier.

Do not center-align financial numbers.

---

# 59. Period Alignment

Time periods should consistently correspond to the same columns.

Sticky/table implementation must not allow headers and cells to become misaligned.

This should be heavily tested on:

- Chrome
- Safari
- mobile Chrome
- mobile Safari

---

# 60. Font

Use our application font/design system.

Do not import Screener's font simply because its HTML contains that dependency.

---

# 61. CSS

Do not reuse Screener CSS files.

Do not depend on:

```text
cdn-static.screener.in
```

for any UI styling or assets.

Build everything inside our own design system.

---

# 62. Icons

Replace Screener-specific icon classes with our icon system.

Do not use:

```text
icon-circle-up
icon-chat-ai
icon-right
```

from their site.

Use our own icon package.

---

# 63. External Assets

Do not hotlink:

- Screener logos
- Screener icons
- Screener CSS
- Screener JavaScript
- Screener static assets

The provided HTML is for understanding functionality.

---

# 64. No Screener JavaScript Dependency

Things like:

```javascript
CompanyChart.setActive()
Utils.setActiveTab()
Modal.openInModal()
```

are examples of their implementation.

Do NOT copy these functions.

Recreate the behaviour natively using our framework.

---

# 65. Accessibility

Important interactive controls need:

- keyboard navigation
- visible focus state
- semantic buttons
- table semantics
- `aria-label` where needed
- useful tooltip accessibility
- adequate contrast

Do not make clickable `<div>` elements if they should be buttons.

---

# 66. Tooltips

Financial terms may have optional tooltips:

```text
ROCE ⓘ
P/E ⓘ
TTM ⓘ
```

Tooltip content should come from our definitions/configuration.

Do not hardcode a tooltip component separately for every metric.

---

# 67. Table Row Metadata

A robust table row object should approximately support:

```json
{
  "key": "revenue",
  "label": "Revenue",
  "type": "currency",
  "unit": "crore",
  "values": {},
  "expandable": true,
  "children": []
}
```

This is not a mandatory backend contract.

It illustrates what the frontend must be capable of rendering.

---

# 68. Period Metadata

Do not rely only on human labels like:

```text
Mar 2026
```

Prefer structured period metadata.

Example:

```json
{
  "period": "2026-03-31",
  "label": "Mar 2026",
  "type": "FY"
}
```

Possible types:

```text
QUARTER
FY
TTM
LTM
```

This will avoid sorting problems later.

---

# 69. Units

Financial sections must clearly communicate units.

Example:

```text
₹ Crore
```

or:

```text
$ Million
```

Do not force users to guess the unit.

Ideally the API provides:

```text
currency
scale
unit
```

---

# 70. Indian + US Compatibility

Do not build assumptions such as:

```javascript
currency = "₹"
unit = "Crore"
exchange = "NSE"
```

into common components.

The same system must potentially support:

```text
INR
USD

Crore
Million
Billion

NSE
BSE
NASDAQ
NYSE
```

---

# 71. Dates

Do not perform fragile string parsing such as:

```javascript
label.split(" ")
```

on financial periods.

Use structured dates.

Display formatting should happen separately.

---

# 72. SEO / SSR

Important stock information should ideally be present in initial HTML/server rendering where our architecture allows it.

Especially:

- company name
- stock price/data status
- description
- key metrics
- financial tables
- major headings

Do not make the entire stock page an empty shell dependent on client-side JS if avoidable.

This matters for:

- SEO
- LLM discovery
- page speed
- accessibility
- sharing

---

# 73. Heading Structure

Use semantic headings.

Example:

```text
H1: Reliance Industries Share Price & Financials

H2: About Reliance Industries
H2: Reliance Industries Share Price Chart
H2: Reliance Industries Analysis
H2: Reliance Industries Peer Comparison
H2: Reliance Industries Quarterly Results
H2: Reliance Industries Profit & Loss
H2: Reliance Industries Balance Sheet
H2: Reliance Industries Cash Flow
H2: Reliance Industries Financial Ratios
H2: Reliance Industries Shareholding Pattern
H2: Reliance Industries Documents
```

Do not create multiple unrelated H1s.

---

# 74. URL Structure

Stock page architecture should support clean URLs.

Example:

```text
/stocks/reliance-industries
/stocks/apple
/stocks/nvidia
```

If our existing routing convention differs, follow the current application standard.

---

# 75. Performance

This page can become heavy.

Be careful with:

- 10+ years financial data
- many charts
- hundreds of document links
- peer comparison
- nested expandable tables

Avoid unnecessary re-rendering of complete tables when one row expands.

Memoisation/virtualisation may be used when justified.

Do not prematurely virtualise tiny tables.

---

# 76. Avoid Layout Shift

Components need reasonable predetermined dimensions.

Especially:

- chart
- metrics area
- table header
- document loader

When APIs resolve, content should not cause violent page movement.

---

# 77. Desktop Width

Financial statements benefit from width.

Do not unnecessarily constrain tables to a narrow blog-content width.

Use a wider application container for the stock page.

---

# 78. Visual Philosophy

Our visual style should be:

```text
Professional
Clean
Financial
Dense
Fast
Trustworthy
Minimal
```

Not:

```text
Over-designed
Huge gradient cards
Massive shadows
Too much empty space
Social-media-dashboard style
```

This is a research product.

Data is the hero.

---

# 79. Consistency

All financial sections should use the same:

- heading style
- table styling
- unit placement
- period formatting
- loading behaviour
- error states
- row expansion interaction
- consolidated/standalone control
- horizontal-scroll behaviour

Do not individually design every statement.

---

# 80. What to Take From the Supplied Screener HTML

Take inspiration from:

- information architecture
- compact data presentation
- sticky section navigation
- long financial histories
- expandable financial rows
- consolidated/standalone switching
- horizontal time-series statements
- chart range switching
- chart metric switching
- peer comparison
- quarterly/yearly ownership
- structured company documents
- independent major page sections

---

# 81. What NOT to Copy

Do not copy:

- Screener branding
- Screener logo
- exact typography
- exact colours
- exact card styling
- HTML markup line-for-line
- their CSS classes
- their JavaScript
- analytics scripts
- authentication UI
- premium UI
- Screener AI UI
- account navigation
- their internal URLs
- their CDN assets
- their tracking implementation

Those things are irrelevant to our requirement.

---

# 82. Ignore From Supplied HTML

The supplied source contains lots of code that has nothing to do with our stock page.

Ignore things such as:

- Plausible tracking
- analytics scripts
- Screener account menu
- logout
- CSRF implementation
- premium upsells
- Screener AI modal implementation
- their site navigation
- their CSS imports
- their PWA configuration
- their CDN paths
- their Django-specific implementation

We only care about the stock-detail experience.

---

# 83. Component Reusability

Please avoid creating something like:

```text
RelianceQuarterTable.jsx
```

Instead:

```text
QuarterlyResultsTable.jsx
```

receiving company data through props/state.

Similarly:

```text
FinancialStatementTable
OwnershipTable
DocumentList
PeerTable
StockMetric
StockChart
SectionHeader
```

should be reusable.

---

# 84. Suggested Frontend State

Page-level state may include:

```text
selectedFinancialMode
selectedChartRange
selectedChartMetric
activeSection
ownershipPeriod
expandedRows
```

Do not put everything into one enormous component state object.

---

# 85. Deep Linking

If user opens:

```text
/stocks/reliance-industries#shareholding
```

the browser should land around Shareholding.

Same for:

```text
#quarters
#profit-loss
#balance-sheet
```

This should also work after client-side navigation.

---

# 86. Loading Priority

Recommended priority:

### Priority 1

```text
Company identity
Price
Basic metrics
```

### Priority 2

```text
Description
Chart
Analysis
```

### Priority 3

```text
Quarterly financials
Annual financials
```

### Priority 4

```text
Peers
Ownership
Documents
```

Actual API architecture may affect this.

---

# 87. Data Freshness

Where relevant, show freshness.

Examples:

```text
Price updated 15 min ago

Financials updated after Q1 FY27 results

Shareholding as of Jun 2026
```

Users should know whether they are looking at current or historical information.

---

# 88. Do Not Fake Data

During frontend development, mock data is fine.

But mock data must be clearly isolated.

Example:

```text
/mocks/stockDetails.ts
```

Once API integration starts, there should be no silent fallback where real company pages accidentally display Reliance mock values.

---

# 89. Analytics

Important interactions should eventually be trackable.

Examples:

```text
stock_chart_range_changed
stock_chart_metric_changed
financial_mode_changed
financial_row_expanded
peer_company_clicked
document_clicked
stock_section_clicked
ownership_period_changed
```

Do not couple event analytics deeply to visual components.

Use our tracking utility.

---

# 90. Acceptance Criteria

I will consider the frontend implementation ready when:

### Page

- [ ] Any stock can be loaded using dynamic data.
- [ ] No Reliance-specific financial values are hardcoded.
- [ ] Major sections render independently.

### Navigation

- [ ] Sticky section navigation works.
- [ ] Active section is visible.
- [ ] Mobile navigation horizontally scrolls.
- [ ] Anchor/deep links work.

### Header

- [ ] Company name/ticker render dynamically.
- [ ] Price/change render correctly.
- [ ] Data timestamp/status is visible.
- [ ] Missing data doesn't break layout.

### Metrics

- [ ] Metrics are compact.
- [ ] Currency/percent/ratio formatting is consistent.
- [ ] Null values are handled gracefully.

### Chart

- [ ] Chart displays successfully.
- [ ] Time range switches work.
- [ ] Metric switches are architecture-ready.
- [ ] Chart has loading/error states.

### Financial Statements

- [ ] Quarterly results implemented.
- [ ] P&L implemented.
- [ ] Balance Sheet implemented.
- [ ] Cash Flow implemented.
- [ ] Ratios implemented.
- [ ] Consolidated/Standalone supported when data exists.
- [ ] Expandable rows work.
- [ ] Tables horizontally scroll on mobile.
- [ ] Values and headers remain aligned.

### Peers

- [ ] Peer table is dynamic.
- [ ] Current company highlighted.
- [ ] Company navigation works.

### Ownership

- [ ] Shareholding/ownership table works.
- [ ] Quarterly/yearly switch works.
- [ ] Expandable holder categories are supported.

### Documents

- [ ] Documents are grouped properly.
- [ ] Announcement list works.
- [ ] Annual reports work.
- [ ] External documents open correctly.
- [ ] Empty states work.

### Engineering

- [ ] Components are reusable.
- [ ] No Screener CSS/JS dependencies.
- [ ] No copied tracking scripts.
- [ ] API failures are section-level.
- [ ] Mobile/tablet/desktop tested.
- [ ] Page doesn't suffer major layout shifts.
- [ ] Data components are compatible with more than one market.

---

# 91. MVP Priority

Do not block MVP by implementing every tiny feature in Screener.

## P0 — Must Have

1. Stock Header
2. Company About
3. Key Metrics
4. Sticky Section Navigation
5. Price Chart
6. Quarterly Results
7. Profit & Loss
8. Balance Sheet
9. Cash Flow
10. Ratios
11. Peer Comparison
12. Ownership/Shareholding
13. Responsive tables
14. Loading/error/empty states
15. Dynamic API integration

## P1 — Strongly Recommended

16. Analysis/Insights
17. Consolidated vs Standalone
18. Expandable financial rows
19. Documents
20. Annual Reports
21. Announcements
22. Chart metric switching
23. Deep-linked sections

## P2 — Later

24. User-selectable metrics
25. Custom peer columns
26. Alerts
27. Export
28. AI summaries
29. Document AI
30. Advanced chart overlays
31. User-customised ratios

---

# 92. Final Expected Result

I should be able to give the frontend a stock identifier like:

```text
RELIANCE
```

or:

```text
AAPL
```

and supply the corresponding API responses.

The frontend should automatically produce a complete, polished stock-analysis page without us redesigning or rewriting components for every company.

The closest way to describe the requirement is:

> **Build the information depth and usability of Screener's company page, but using our own design system, our own component architecture, our own APIs and a structure capable of supporting Indian and US equities at scale.**

The frontend should optimise for:

> **Maximum useful financial information with minimum friction.**

When there is a conflict between making the page look decorative and making financial data easier to analyse, choose **data usability**.