# Scrooner Financials Display Specification (Final)

**Status:** Final v2 — merges the ChatGPT-authored draft (v1) with the educator-lens
review and prior competitor naming study
**Product:** Scrooner
**Applies to:** US-listed company detail pages
**Product principle:** KISS BORING — make financial statements simple to scan, consistent
across companies, traceable to source filings, and impossible to misunderstand.

---

## Changelog from v1 (what this merge adds)

Everything in v1 is preserved. This version adds, in place, the items the review
surfaced:

1. **Plain-English explainer per metric** — a `plain_english_note` field and a
   tap/hover UI requirement, so every Investor View row teaches, not just displays.
2. **Auto-generated Signal chips on the Financial Overview** — a small, strictly
   data-derived narrative layer (Section 4), scoped tightly so it doesn't bloat this
   spec into a full pros/cons feature.
3. **`glossary_link` field per metric** — ties each row to its matching educational
   pillar page (per `content-marketing-plan.md`'s Pillar A), closing the loop between
   the content strategy and the product surface.
4. **Explicit `<title>`/meta naming convention** alongside the existing visible-H1
   convention (Section 2), carried over from `financial-statements-naming-study.md`.
5. **EBITDA formula defined and versioned**, matching the discipline already required
   for Free Cash Flow (Section 6/10) — EBITDA has more than one common definition, so
   this closes a gap the review flagged.
6. **Clarified "Latest Reported Quarter"** as a UI shortcut on the Balance Sheet, not a
   separate computation path (Section 7).
7. Minor consistency notes (nav-label short forms are intentional, not a bug).

Everything else — the section naming decisions, the row lists, the sector templates,
the data-provenance schema, the MVP scope — is retained from the original draft largely
as written, because the review validated it as accurate and independently convergent
with our own competitor research.

---

## 1. Objective

The Financials section should help an investor answer four questions quickly:

1. Is the business growing?
2. Is profitability improving or weakening?
3. Is the balance sheet healthy?
4. Is reported profit converting into cash?

Scrooner should provide complete financial statements without showing every accounting
detail by default. Important investor metrics must be visible immediately; detailed
reported rows should remain available through expansion.

**Added principle:** every metric shown must also be explainable in one plain-English
sentence, on demand, without leaving the page. Scrooner's edge isn't having more rows
than competitors — it's that a first-time investor can understand every row they see.
Displaying a correct number a beginner can't interpret is only half the job.

---

## 2. Final section names

Use US-market terminology consistently.

| Proposed name | Final name | Decision |
| --- | --- | --- |
| Apple Inc. Quarterly results | **Apple Quarterly Financial Results** | Use as the compact recent-performance table |
| Apple Inc. Profit & Loss | **Apple Income Statement** | Replace "Profit & Loss" with the standard US term |
| Apple Inc. Balance sheet | **Apple Balance Sheet** | Keep |
| Apple Inc. cash flow | **Apple Cash Flow Statement** | Use singular "Statement" |

### Navigation labels

Use shorter labels in tabs or the section navigation:

- Overview
- Quarterly Results
- Income Statement
- Balance Sheet
- Cash Flow
- Ratios

(These shorten the full section names above — e.g. "Quarterly Financial Results"
becomes "Quarterly Results" in the tab. This is intentional: full name as the page H1,
short label in navigation chrome. It is not an inconsistency to reconcile.)

### Page and section headings (visible H1)

- `{Company Name} Financials`
- `{Company Name} Financial Overview`
- `{Company Name} Quarterly Financial Results`
- `{Company Name} Income Statement`
- `{Company Name} Balance Sheet`
- `{Company Name} Cash Flow Statement`
- `{Company Name} Financial Ratios`

Example: **Apple Income Statement**, not "Apple Inc. Profit & Loss." Use the short/common
company name — drop "Inc./Corp./Co./Ltd." from the visible heading.

### `<title>` tag and meta description (new)

The visible H1 and the page's indexable `<title>`/meta description are not the same
string and should not be forced to match:

- **Visible H1:** short name + statement — `Apple Balance Sheet`.
- **`<title>` tag / meta description:** full legal name + ticker + statement —
  `Apple Inc. (AAPL) Balance Sheet`.

Rationale: the ticker and legal suffix disambiguate companies that share a common name
and match how investors actually type exact-match search queries ("AAPL balance
sheet"), while the visible H1 stays clean and readable for a human looking at the page.
Given the product's SEO thesis depends on thousands of independently indexed pages
(per `What we are building`), this distinction should be a template-level rule applied
to every statement page and every ticker, not a per-page decision left to whoever builds
the page.

---

## 3. Recommended information architecture

```text
Financials
├── Financial Overview
├── Quarterly Financial Results
├── Income Statement
├── Balance Sheet
├── Cash Flow Statement
└── Financial Ratios
```

Every statement should have two presentation levels:

1. **Investor View — default:** Important rows, growth rates and margins.
2. **Detailed View:** Complete normalized statement with expandable company-reported rows.

The default must always be Investor View.

---

## 4. Financial Overview

This is a compact summary displayed before the full statements.

### Default metrics

- Revenue — TTM
- Revenue Growth — TTM YoY
- Gross Margin — TTM
- Operating Margin — TTM
- Net Income — TTM
- Net Margin — TTM
- Diluted EPS — TTM
- Free Cash Flow — TTM
- Free Cash Flow Margin — TTM
- Cash and Short-Term Investments — latest reported quarter
- Total Debt — latest reported quarter
- Net Cash / Net Debt — latest reported quarter
- Return on Invested Capital — TTM or latest fiscal year
- Five-Year Share Dilution / Buyback Rate

### Optional trend chart

Allow investors to switch one simple chart between:

- Revenue
- Operating Income
- Net Income
- Diluted EPS
- Free Cash Flow

Do not place several charts on the page by default.

### Auto-generated Signal chips (new)

Show up to **four** short, auto-generated signal chips directly under the default
metrics — a narrow, strictly data-derived narrative layer, not a full pros/cons feature.
Each signal is computed only from data already present on this page (no new data source
required) and must be traceable to the underlying figures it's based on (tap to see the
calculation, same provenance discipline as every other metric in Section 10).

Candidate signals, computed from the statements already specified in this document:

- Revenue growth trend (accelerating / decelerating / flat, based on YoY over the last
  3–4 quarters)
- Margin trend (expanding / compressing, based on 3-year gross or operating margin
  direction)
- Net cash / net debt trend (strengthening / weakening balance sheet)
- Diluted share count trend (buying back / diluting, 5-year direction)

Example: "🟢 Operating margin has expanded for 3 straight years" or "🔴 Diluted share
count is up 8% over 5 years — existing shareholders are being diluted."

**Scope boundary:** this is deliberately narrow. A fuller pros/cons checklist covering
business-quality signals outside these four statements (moat, insider buying,
institutional ownership, customer concentration — per `us-investor-data-points.md`
Section 10) is a separate feature living on the company's main Overview page, not this
Financials section. This spec only owns the four signals above, because they're the
ones derivable purely from the data this document already defines.

---

## 5. Quarterly Financial Results

### Purpose

Show whether the company's growth, margins and cash generation are accelerating or slowing.

### Period coverage

- Show the latest **8 quarters** by default.
- Allow expansion to at least **12 quarters**.
- Display both the fiscal quarter and exact period-end date.
- Example: `Q3 FY2026` with tooltip/subtext `Quarter ended Jun 27, 2026`.
- Show the newest quarter first.
- Display `USD in millions, except per-share data` above the table.

### Default rows

| Row | Source/type |
| --- | --- |
| Revenue | Reported/standardized |
| Revenue Growth YoY | Calculated |
| Gross Profit | Reported or calculated |
| Gross Margin | Calculated |
| Operating Income | Reported |
| Operating Margin | Calculated |
| Net Income | Reported |
| Net Margin | Calculated |
| Diluted EPS | Reported |
| Diluted EPS Growth YoY | Calculated |
| Operating Cash Flow | Reported or derived discrete quarter |
| Free Cash Flow | Calculated |

Every row in this default set ships with a plain-English explainer at MVP (see Section
10's `plain_english_note` field) — this table is often the first thing a new user reads,
so it's the highest-priority place for the explainer requirement, not an
afterthought.

### Expandable rows

- Revenue by business segment
- Revenue by geographic segment
- Cost of Revenue
- Research and Development
- Selling, General and Administrative
- Total Operating Expenses
- Interest Income
- Interest Expense
- Other Income/Expense
- Income Before Tax
- Income Tax Expense
- Effective Tax Rate
- Basic EPS
- Basic Weighted Average Shares
- Diluted Weighted Average Shares
- Capital Expenditures
- Stock-Based Compensation
- Share Repurchases
- Dividends Paid

### Company-specific KPIs

Company-specific segment data should be displayed separately and must not be hard-coded
into the universal statement template.

For Apple, examples include:

- iPhone Revenue
- Mac Revenue
- iPad Revenue
- Wearables, Home and Accessories Revenue
- Services Revenue
- Products Revenue
- Americas Revenue
- Europe Revenue
- Greater China Revenue
- Japan Revenue
- Rest of Asia Pacific Revenue

### Quarterly cash-flow derivation

US 10-Q cash-flow values can be cumulative year-to-date. Store the reported cumulative
value and calculate the standalone quarter where required:

- Q1 standalone = Q1 three-month value
- Q2 standalone = six-month value − Q1 value
- Q3 standalone = nine-month value − six-month value
- Q4 standalone = annual value − nine-month value

Required internal fields:

- `reported_ytd_value`
- `derived_quarter_value`
- `is_derived`
- `derivation_formula`

Derived values must be identifiable in the tooltip or methodology documentation.

Note: this derivation applies to **cash-flow items only**. Income-statement line items
(Revenue, Gross Profit, Operating Income, Net Income, EPS) are already reported
discretely per quarter in the 10-Q and require no derivation — do not apply this logic
outside the cash-flow rows in this table.

---

## 6. Income Statement

### Period controls

- Annual
- Quarterly
- TTM

### Recommended history

- MVP: 5 annual periods, TTM and 8 quarterly periods
- Target: 10 annual periods and 12–20 quarterly periods
- Paid/deep-history option: 15–20 annual periods and up to 40 quarters

### Default Investor View rows

#### Revenue and gross profit

- Revenue
- Revenue Growth
- Cost of Revenue
- Gross Profit
- Gross Margin

Use **Revenue** as the standardized label. Preserve company-reported labels such as "Net
Sales" in metadata or a tooltip.

#### Operating performance

- Operating Expenses
- Operating Income
- Operating Margin
- EBITDA
- EBITDA Margin

EBITDA must be labelled **Calculated** unless the company directly reports it using a
clearly defined methodology. **Default Scrooner formula (new):**

`EBITDA = Operating Income + Depreciation & Amortization`

This formula and its components must be stored and versioned exactly as required for
Free Cash Flow in Section 8 — EBITDA has more than one common industry definition
(operating-income-based vs. net-income-based, which diverge for companies with large
non-operating income or expense), so a silently-changed definition would break historical
comparability the same way an unversioned FCF formula would.

#### Profit

- Income Before Tax
- Income Tax Expense
- Effective Tax Rate
- Net Income
- Net Margin

#### Per-share data

- Basic EPS
- Diluted EPS
- Basic Weighted Average Shares
- Diluted Weighted Average Shares
- Diluted Shares Growth

Diluted Shares Growth is strategically important because Scrooner users should be able
to identify dilution and sustained buybacks.

**Plain-English requirement (new):** EBIT, EBITDA Margin, Effective Tax Rate, and
Weighted Average Diluted Shares are accounting-fluent terms that a first-time investor
will not recognize on sight. Keep them in Investor View — hiding them behind Detailed
View would be a worse trade-off than the KISS BORING principle intends — but every one
of them must ship with its `plain_english_note` explainer at MVP, not deferred to a
later release. These four rows are the highest-value candidates for the explainer
requirement in this statement.

### Detailed View rows

- Product Revenue
- Service Revenue
- Research and Development
- Selling, General and Administrative
- Other Operating Expenses
- Interest Income
- Interest Expense
- Net Interest Income/Expense
- Other Non-Operating Income/Expense
- Net Income Attributable to Non-Controlling Interests
- Net Income Attributable to Common Shareholders
- Depreciation and Amortization
- EBIT
- Stock-Based Compensation
- Restructuring Charges
- Acquisition-Related Charges
- Discontinued Operations
- Comprehensive Income
- Company-specific reported line items

### Metrics below the statement

- Revenue CAGR — 3Y, 5Y and 10Y
- EPS CAGR — 3Y, 5Y and 10Y
- Net Income CAGR — 3Y, 5Y and 10Y
- Average Gross Margin — 3Y and 5Y
- Average Operating Margin — 3Y and 5Y
- Average Net Margin — 3Y and 5Y
- Diluted Shares CAGR — 3Y and 5Y

---

## 7. Balance Sheet

Balance-sheet values represent a position at a specific date. Do **not** show a TTM
balance-sheet column.

### Period controls

- Annual
- Quarterly
- Latest Reported Quarter

**Clarification (new):** "Latest Reported Quarter" is a UI shortcut, not a separate data
path — it renders the same first column the "Quarterly" toggle already shows, pinned as
a one-tap default for users who only want the most recent position. It does not require
its own query or storage; implement it as a display-layer default, not a third
computation branch.

### Default Investor View rows

#### Assets

- Cash and Cash Equivalents
- Short-Term Investments
- Cash and Short-Term Investments
- Accounts Receivable
- Inventory
- Total Current Assets
- Property, Plant and Equipment
- Goodwill and Intangible Assets
- Total Assets

#### Liabilities

- Accounts Payable
- Short-Term Debt
- Long-Term Debt
- Total Debt
- Total Current Liabilities
- Total Liabilities

#### Equity and financial position

- Shareholders' Equity
- Net Cash / Net Debt
- Working Capital
- Book Value
- Book Value Per Share

### Detailed View rows

- Other Current Assets
- Long-Term Investments
- Goodwill
- Intangible Assets
- Deferred Tax Assets
- Other Non-Current Assets
- Current Portion of Long-Term Debt
- Accrued Expenses
- Deferred Revenue
- Operating Lease Liabilities
- Deferred Tax Liabilities
- Other Current and Non-Current Liabilities
- Common Stock and Additional Paid-In Capital
- Retained Earnings
- Accumulated Other Comprehensive Income/Loss
- Treasury Stock
- Non-Controlling Interest
- Tangible Book Value
- Tangible Book Value Per Share
- Company-specific reported line items

### Calculated balance-sheet metrics

- Net Cash / Net Debt
- Working Capital
- Current Ratio
- Quick Ratio
- Debt-to-Equity
- Debt-to-EBITDA
- Book Value Per Share
- Tangible Book Value Per Share

Naming rule:

- If cash and relevant investments exceed total debt, display **Net Cash**.
- If total debt exceeds cash and relevant investments, display **Net Debt**.

### Metrics below the statement

- Cash Growth — 3Y and 5Y
- Debt Growth — 3Y and 5Y
- Net Cash/Net Debt Trend
- Working Capital Trend
- Current Ratio
- Debt-to-Equity
- Debt-to-EBITDA
- Book Value Per Share CAGR — 3Y and 5Y

---

## 8. Cash Flow Statement

### Period controls

- Annual
- Quarterly
- TTM

### Default Investor View rows

- Cash Flow from Operating Activities
- Capital Expenditures
- Free Cash Flow
- Free Cash Flow Growth
- Free Cash Flow Margin
- Acquisitions
- Debt Issued/Repaid
- Share Repurchases
- Dividends Paid
- Stock-Based Compensation
- Net Change in Cash

### Detailed View rows

#### Operating activities

- Net Income
- Depreciation and Amortization
- Stock-Based Compensation
- Deferred Income Taxes
- Change in Accounts Receivable
- Change in Inventory
- Change in Accounts Payable
- Change in Deferred Revenue
- Change in Other Working Capital
- Other Non-Cash Items
- Cash Flow from Operating Activities

#### Investing activities

- Capital Expenditures
- Acquisitions
- Purchases of Investments
- Sales and Maturities of Investments
- Purchases of Intangible Assets
- Other Investing Activities
- Cash Flow from Investing Activities

#### Financing activities

- Debt Issued
- Debt Repaid
- Common Stock Issued
- Share Repurchases
- Dividends Paid
- Other Financing Activities
- Cash Flow from Financing Activities

#### Cash reconciliation

- Effect of Foreign Exchange Rates
- Net Change in Cash
- Beginning Cash Balance
- Ending Cash Balance

### Calculated investor metrics

- Free Cash Flow
- Free Cash Flow Growth
- Free Cash Flow Margin
- Free Cash Flow Per Share
- Capital Expenditures as % of Revenue
- Operating Cash Flow / Net Income
- Net Buybacks
- Cash Returned to Shareholders
- Shareholder Yield

Default Scrooner formula:

`Free Cash Flow = Cash Flow from Operating Activities − Capital Expenditures`

The formula and its underlying components must be stored. If another definition is
introduced later, it must have a separate metric identifier. (EBITDA in Section 6 now
carries the same requirement.)

### Metrics below the statement

- Operating Cash Flow CAGR — 3Y, 5Y and 10Y
- Free Cash Flow CAGR — 3Y, 5Y and 10Y
- Average Free Cash Flow Margin — 3Y and 5Y
- Operating Cash Flow / Net Income
- Capital Expenditure CAGR
- Stock-Based Compensation as % of Revenue
- Share Repurchases as % of Free Cash Flow
- Dividends as % of Free Cash Flow

---

## 9. Display and interaction rules

### Required metadata

Display above every table:

- Reporting currency
- Display unit: thousands, millions or billions
- Fiscal year-end month
- Fiscal period
- Period ending date
- Filing type: 10-K, 10-Q or relevant filing
- Filed date
- Restatement status, when applicable
- Source filing link

### Table controls

- Annual / Quarterly / TTM, where applicable
- USD Millions / USD Billions
- Investor View / Detailed View
- Standardized / As Reported, when supported
- Value / Growth / Margin
- 5Y / 10Y / Max
- Download CSV

### Formatting

- Pin the metric-name column.
- Show the newest period first.
- Keep primary metrics visible; place accounting detail behind expandable rows.
- Use indentation to show parent and child rows.
- Emphasize Revenue, Operating Income, Net Income, Total Assets, Total Debt, Operating
  Cash Flow and Free Cash Flow.
- Use parentheses for negative reported amounts.
- Use green/red only for meaningful improvement or deterioration, not simply because a
  cash-flow line is positive or negative.
- Use `—` for genuinely unavailable values; never convert missing values to zero.
- Tooltips must distinguish Reported, Standardized, Derived and Calculated values.

### Two-layer tooltip system (new)

Every metric name in Investor View carries **two distinct tap/hover layers** — don't
conflate them into one tooltip:

1. **Provenance layer** (already specified above): Reported vs. Standardized vs. Derived
   vs. Calculated, plus the formula where applicable.
2. **Comprehension layer** (new): the `plain_english_note` — one sentence explaining
   what the metric means and why an investor should care, written the way a person
   explains it out loud, not the way an accountant defines it. Where a matching
   educational pillar page exists (per `content-marketing-plan.md`), include a "Learn
   more" link using the `glossary_link` field (Section 10). At MVP, ship the sentence
   for every default/Investor View row across all four statements even if
   `glossary_link` is still empty for most metrics — the explainer is the higher-priority
   half of this requirement, the link can fill in as pillar content ships.

### Mobile behavior

- Freeze the row-label column.
- Open at the newest period.
- Allow horizontal scrolling through older periods.
- Do not reduce text to an unreadable size.
- Retain expansion controls for detailed rows.

---

## 10. Data classification and provenance

Every displayed value should carry:

- `company_id`
- `metric_id`
- `standardized_label`
- `reported_label`
- `statement_type`
- `period_type`
- `fiscal_year`
- `fiscal_quarter`
- `period_start_date`
- `period_end_date`
- `filed_date`
- `form_type`
- `currency`
- `unit`
- `value`
- `source_filing_url`
- `source_fact/tag`
- `is_reported`
- `is_standardized`
- `is_derived`
- `is_calculated`
- `calculation_formula`
- `restatement_version`
- `plain_english_note` *(new)* — one-sentence, spoken-register explanation of the metric
- `glossary_link` *(new, optional at MVP)* — URL to the matching Pillar-A educational
  page from `content-marketing-plan.md`, when one exists

### Data priority

1. Company-reported fact from the applicable filing
2. Standardized fact mapped from the reported fact
3. Derived period value
4. Calculated investor metric

Scrooner must never present a calculated metric as if it were directly reported by the
company.

---

## 11. Sector-specific templates

A universal corporate statement cannot be applied blindly to every US-listed company.

| Company type | Template |
| --- | --- |
| Technology, industrial, consumer and healthcare companies | Standard corporate |
| Banks and lenders | Banking |
| Insurance companies | Insurance |
| REITs | REIT |
| Pre-revenue and development-stage companies | Simplified corporate |

### Banks and lenders

Do not emphasize gross profit, conventional EBITDA or conventional free cash flow.
Prioritize:

- Interest Income
- Interest Expense
- Net Interest Income
- Net Interest Margin
- Provision for Credit Losses
- Non-Interest Income
- Non-Interest Expense
- Net Income
- Diluted EPS
- Total Loans
- Total Deposits
- Non-Performing Loans
- CET1 Ratio
- Book Value Per Share
- Tangible Book Value Per Share
- Return on Assets
- Return on Equity

### Insurance companies

Prioritize:

- Premiums Earned
- Investment Income
- Claims and Policy Benefits
- Underwriting Income
- Combined Ratio
- Book Value Per Share
- Investment Portfolio
- Insurance Reserves
- Return on Equity

### REITs

Prioritize:

- Revenue
- Net Operating Income
- Funds from Operations
- Adjusted FFO
- FFO Per Share
- AFFO Per Share
- Occupancy Rate
- Net Debt / EBITDA
- Dividends Per Share
- AFFO Payout Ratio

### Fallback rule

If a company cannot be safely mapped to its sector template:

- Show normalized universal rows where confidently available.
- Provide an As Reported detailed statement.
- Do not manufacture a zero or force an inappropriate metric.

---

## 12. MVP scope

### Must ship

#### Quarterly Financial Results

- 12 default rows
- Latest 8 quarters
- YoY growth and margins
- Standalone-quarter derivation for cumulative cash-flow facts
- Plain-English explainer on every default row *(new)*

#### Income Statement

- Approximately 20–25 standardized rows
- Five annual periods plus TTM
- Eight quarterly periods
- Expandable reported detail
- EBITDA formula defined and versioned, same discipline as FCF *(new)*
- Plain-English explainer on every Investor View row, especially EBIT, EBITDA Margin,
  Effective Tax Rate, and Diluted Weighted Average Shares *(new)*

#### Balance Sheet

- Approximately 25–30 standardized rows
- Five annual periods
- Latest quarterly balance sheet
- Net Cash/Net Debt, Working Capital and Book Value Per Share
- Plain-English explainer on every Investor View row *(new)*

#### Cash Flow Statement

- Approximately 20–25 standardized rows
- Five annual periods plus TTM
- Eight quarterly periods where reliable
- Strong emphasis on Operating Cash Flow, Capital Expenditures, Free Cash Flow, Buybacks
  and Dividends
- Plain-English explainer on every Investor View row *(new)*

#### Financial Overview

- Up to four auto-generated Signal chips (revenue growth trend, margin trend, net
  cash/debt trend, dilution trend), each traceable to its underlying data *(new)*

#### Trust requirements

- Filing date
- Period end date
- Currency and unit
- Source filing link
- Reported/calculated indicator
- Missing-value handling
- Visible-H1 vs. `<title>`/meta naming convention applied consistently across every
  ticker and statement page *(new)*

### Can wait until after MVP

- Twenty years of history
- Full Standardized / As Reported switching for every issuer
- Custom table rows
- Excel export
- Advanced chart builder
- Normalized/adjusted earnings
- Analyst estimates inside the financial statements
- Detailed sector KPIs for every industry
- Full business-quality pros/cons checklist (moat, insider activity, institutional
  ownership) — belongs to the company Overview page, not this Financials section
  *(new, scope boundary)*
- Full `glossary_link` content coverage — ship the field and the plain-English sentence
  at MVP; backfill links to pillar pages as that content is published *(new)*

---

## 13. Acceptance criteria

The implementation is acceptable when:

1. Section names follow the final naming standard.
2. Investor View opens by default.
3. A user can understand growth, profitability, balance-sheet strength and cash
   conversion without opening Detailed View.
4. Quarterly cash-flow values are not mistakenly presented as discrete quarters when
   they are cumulative.
5. TTM is not shown for balance-sheet values.
6. Missing values are not converted to zero.
7. Calculated and derived values are labelled correctly, including EBITDA carrying an
   explicit, versioned formula the same way Free Cash Flow does.
8. Every displayed value can be traced to a filing, source fact or stored formula.
9. Banks, insurers and REITs do not inherit misleading corporate metrics.
10. The tables remain readable on mobile and desktop.
11. Every Investor View metric has a plain-English explainer visible on tap/hover,
    distinct from the provenance tooltip. *(new)*
12. The Financial Overview shows no more than four auto-generated signal chips, each
    traceable to the underlying figures used to compute it. *(new)*
13. The visible H1 (short name + statement) and the `<title>`/meta tag (legal name +
    ticker + statement) both follow their respective conventions on every statement
    page. *(new)*

---

## 14. Final product decision

Scrooner will combine the simplicity of Screener.in with terminology and statement
structures appropriate for US-listed companies.

The product should not become a raw financial-data dump. It should:

- Show the important rows first.
- Preserve complete details behind expansion.
- Add investor-relevant growth, margin, cash-conversion and dilution metrics.
- Keep every number traceable to the original filing or a documented formula.
- Use specialized templates where the standard corporate model is inappropriate.
- Explain every number in plain English on demand, and link out to deeper education
  where it exists. *(new)*

> **Final principle: Show complete financial statements, but make the important numbers
> impossible to miss — and impossible to misunderstand.**

---

## Appendix: Competitor naming cross-check

For reference, the naming decisions in Section 2 were independently validated twice —
once by this document's original ChatGPT draft, once by a separate competitor study
(`claude/financial-statements-naming-study.md`) built from live pages on Screener.in,
GuruFocus, Yahoo Finance, stockanalysis.com, and Macrotrends:

| Convention | Evidence |
| --- | --- |
| "Income Statement," not "Profit & Loss" | Universal across every US-facing competitor checked (Yahoo, GuruFocus, Macrotrends, stockanalysis, WSJ, ycharts) |
| "Cash Flow Statement," full form | Macrotrends and stockanalysis both use the full form as the page heading |
| Drop "Inc." from the visible header | stockanalysis.com and Macrotrends both use the short name only in the H1 |
| No dedicated "Quarterly Results" page on US sites | US competitors fold quarterly data into an Annual/Quarterly toggle on each statement; the dedicated quarterly table is a deliberate Screener.in-style differentiator, not a gap |

Full detail, row-by-row data-point mapping to EDGAR XBRL tags, and the complete
competitor comparison table are preserved in `claude/financial-statements-naming-study.md`
for reference; this document supersedes it for section-naming decisions specifically,
and folds its recommendations in directly above.
