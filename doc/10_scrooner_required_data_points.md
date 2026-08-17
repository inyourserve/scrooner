# Screener for US Investors — Required Data Points

**Status: Finalized v1.0**

Reference: Reliance Industries page on Screener.in (India). Goal: define what a US-based
self-directed investor needs to see on an equivalent stock page, where the Indian
version's data model needs to change vs. carry over, and — new in this revision —
exactly what to pull from SEC EDGAR to source it.

Priority key: **P0** = must-have for MVP, **P1** = strong differentiator, **P2** = premium/advanced.

---

## 1. Quick Snapshot (top-of-page ratio block)

Equivalent to Screener's `top-ratios` block, adapted for US expectations.

| Data point | Priority | Notes |
|---|---|---|
| Market Cap | P0 | |
| Current Price + Day Change % | P0 | Not from EDGAR — needs a market-data feed |
| 52-Week High / Low | P0 | Not from EDGAR — needs a market-data feed |
| Trailing P/E | P0 | Price (market feed) ÷ EPS (EDGAR) |
| Forward P/E | P0 | Needs analyst estimates — not on EDGAR |
| PEG Ratio | P0 | Growth-adjusted valuation — heavily used in US, absent in Indian version |
| EPS (TTM) | P0 | EDGAR: `EarningsPerShareDiluted` |
| EPS (Forward / Next FY estimate) | P0 | Needs analyst estimates — not on EDGAR |
| Book Value / Price-to-Book | P0 | EDGAR: `StockholdersEquity` |
| Dividend Yield | P0 | EDGAR: `CommonStockDividendsPerShareDeclared` |
| Dividend Payout Ratio | P1 | Derived from EDGAR dividend + net income tags |
| Beta (5Y monthly) | P0 | Not from EDGAR — needs price history |
| Shares Outstanding (+ trend) | P0 | EDGAR: `CommonStockSharesOutstanding` (also on cover page of every filing) |
| Average Volume (10D/3M) | P1 | Not from EDGAR — needs a market-data feed |

---

## 2. Valuation Multiples

| Data point | Priority | Notes |
|---|---|---|
| EV/EBITDA | P0 | |
| EV/Sales | P0 | |
| Price/Sales | P0 | |
| Price/Free Cash Flow | P1 | More trusted than P/E by many US value investors |
| Price/Book | P0 | |
| Historical median multiple bands (5Y/10Y) | P1 | Requires storing our own computed history — EDGAR gives raw inputs only |

---

## 3. Profitability & Margin Quality

| Data point | Priority | Notes |
|---|---|---|
| Gross Margin (trend, 5–10yr) | P0 | |
| Operating Margin (trend) | P0 | |
| Net Margin (trend) | P0 | |
| Return on Equity (ROE) | P0 | |
| Return on Invested Capital (ROIC) | P0 | Preferred over ROCE in US analysis |
| Return on Assets (ROA) | P1 | |
| Margin trend direction flag (expanding/compressing) | P1 | Auto-generated insight, like Screener's pros/cons |

---

## 4. Cash Flow (heavily weighted for US investors — GAAP-skeptical culture)

| Data point | Priority | Notes |
|---|---|---|
| Free Cash Flow (FCF), trailing 5–10yr | P0 | Computed: CFO − CapEx |
| FCF Margin | P0 | |
| FCF Yield (FCF / Market Cap) | P0 | Core "is this cheap" metric for US quality investors |
| Cash from Operations | P0 | |
| CapEx (and CapEx as % of revenue) | P1 | |
| FCF vs. Net Income divergence flag | P1 | Flags earnings-quality issues |
| Stock-Based Compensation (SBC) as % of revenue | P1 | Very US-specific concern; add-back adjusted FCF |

---

## 5. Balance Sheet Health

| Data point | Priority | Notes |
|---|---|---|
| Total Debt | P0 | |
| Debt / Equity | P0 | |
| Net Debt / EBITDA | P0 | |
| Interest Coverage Ratio | P0 | |
| Current Ratio | P0 | |
| Quick Ratio | P1 | |
| Cash & Equivalents | P0 | |
| Goodwill & Intangibles (as % of assets) | P2 | Flags acquisition-driven balance sheets |

---

## 6. Growth Metrics

| Data point | Priority | Notes |
|---|---|---|
| Revenue Growth (YoY, 3Y/5Y/10Y CAGR) | P0 | |
| EPS Growth (YoY, 3Y/5Y/10Y CAGR) | P0 | |
| FCF Growth (3Y/5Y CAGR) | P1 | |
| Forward Revenue Growth Estimate (next FY) | P0 | Not on EDGAR — analyst consensus needed |
| Forward EPS Growth Estimate (next FY) | P0 | Not on EDGAR — analyst consensus needed |
| Estimate Revision Trend (last 90 days) | P1 | Not on EDGAR |

---

## 7. Capital Allocation & Shareholder Returns

| Data point | Priority | Notes |
|---|---|---|
| Buyback Yield | P0 | EDGAR: `PaymentsForRepurchaseOfCommonStock` |
| Total Shareholder Yield | P1 | Composite of dividend + buyback yield − dilution |
| Dividend History / Growth Streak | P1 | Built from EDGAR dividend tag history |
| Share Count Dilution Trend (5–10yr) | P0 | EDGAR: `CommonStockSharesOutstanding` over time |

---

## 8. Ownership & Insider Activity

| Data point | Priority | Notes |
|---|---|---|
| Institutional Ownership % | P0 | Derived from Form 13F aggregation (see Section 14) |
| Institutional Ownership Trend (QoQ change) | P1 | Derived from Form 13F history |
| Insider Buying/Selling Activity (last 6–12 months) | P0 | EDGAR Form 4 — direct source, high-signal |
| Short Interest % of Float | P0 | Not on EDGAR — needs FINRA/exchange short-interest data |
| Days to Cover (Short Interest Ratio) | P1 | Not on EDGAR |
| Top Institutional Holders | P2 | EDGAR Form 13F |

---

## 9. Analyst & Market Sentiment

All items in this section are **not available on EDGAR** and require a third-party data
vendor (e.g. an estimates/consensus feed):

| Data point | Priority | Notes |
|---|---|---|
| Analyst Rating Distribution | P0 | External vendor |
| Average Price Target (+ range) | P0 | External vendor |
| Price Target vs. Current Price | P0 | External vendor |
| Number of Analysts Covering | P1 | External vendor |
| Earnings Surprise History (beat/miss, 8 quarters) | P0 | Actuals from EDGAR 10-Q/8-K; estimates from external vendor |
| Guidance Track Record | P1 | Guidance language extracted from 8-K/earnings press releases (EDGAR); scoring logic built in-house |

---

## 10. Business Quality / Narrative

| Data point | Priority | Notes |
|---|---|---|
| Revenue by Segment | P0 | EDGAR: XBRL segment reporting tags (`us-gaap:SegmentReportingDisclosure...`) in 10-K |
| Revenue by Geography | P1 | EDGAR: geographic segment XBRL tags, when disclosed |
| Customer Concentration | P2 | Extracted from 10-K risk factors / notes (text, not XBRL) |
| Auto-generated Pros/Cons checklist | P0 | Computed in-house from the metrics above |
| Moat / Competitive Position summary | P1 | AI-generated from 10-K "Business" and "Risk Factors" sections (full text, not XBRL) |

---

## 11. Standard Financial Statements (carry over from Indian version)

Same structure as Screener's India tables, sourced from EDGAR XBRL:

- Quarterly Results (10-Q) — Revenue, Expenses, Operating Profit, OPM%, Other Income, Interest, D&A, Pre-tax Profit, Tax Rate, Net Profit, EPS
- Annual Profit & Loss (10-K, 10yr)
- Balance Sheet (10-K, 10yr)
- Cash Flow Statement (10-K, 10yr)
- Standard Ratios table (Debtor Days, Inventory Days, Payables, Cash Conversion Cycle, ROCE/ROIC)

---

## 12. Peer / Sector Comparison

| Data point | Priority | Notes |
|---|---|---|
| Peer comparison table | P0 | Computed from our own EDGAR-sourced dataset across companies |
| Sector/Industry classification | P0 | Use SIC code from EDGAR company record as a fallback; GICS is preferred but is a licensed taxonomy (not on EDGAR) |
| Relative valuation vs. sector median | P1 | Computed in-house |

---

## 13. Documents & Filings

| Data point | Priority | Notes |
|---|---|---|
| 10-K / 10-Q filing links | P0 | EDGAR — direct source |
| 8-K material event filings | P1 | EDGAR — direct source |
| Earnings Call Transcripts + AI Summary | P0 | Not on EDGAR — transcripts come from IR sites/vendors; EDGAR only has the press release exhibit (8-K Ex-99.1) |
| Proxy Statement (DEF 14A) — exec comp, insider holdings | P2 | EDGAR — direct source |
| Credit Ratings (S&P/Moody's/Fitch) | P1 | Not on EDGAR — needs rating agency feed |

---

## 14. SEC EDGAR — Finalized Data Collection Plan

This section defines exactly what to pull from EDGAR, via which API, and what it covers.
Everything here is free, requires no API key, but does require a compliant `User-Agent`
header identifying the app and a contact email, and should stay under **10 requests/second**
per SEC's fair-access policy.

### 14.1 Core APIs to integrate

| API | Endpoint pattern | What it gives us |
|---|---|---|
| Company Tickers | `https://www.sec.gov/files/company_tickers.json` | Master list mapping ticker → CIK (Central Index Key) — needed to resolve any other lookup |
| Submissions API | `https://data.sec.gov/submissions/CIK##########.json` | Entity metadata (name history, SIC code, exchange, fiscal year end) + full filing history/index (up to 1,000 most recent filings, all form types) |
| Company Facts API (XBRL) | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | Every standardized XBRL financial fact ever reported by that company, across all filings — this is the primary source for Sections 1–7 and 11 above |
| Company Concept API (XBRL) | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/{Tag}.json` | Single-metric time series for one company (e.g. just `Revenues`) — useful for targeted/incremental pulls instead of the full company-facts payload |
| Frames API (XBRL) | `https://data.sec.gov/api/xbrl/frames/us-gaap/{Tag}/{Unit}/{Period}.json` | One fact, across **all** companies, for a given period — this is how we'd build sector/peer medians efficiently without pulling every company's full facts file |
| Full Text Search | `https://efts.sec.gov/LATEST/search-index?q={query}&forms={form}` | Keyword search across filing text — useful for scanning risk factors, guidance language, customer concentration disclosures |
| Bulk Data | Nightly ZIP archives (`submissions.zip`, `companyfacts.zip`) at `https://www.sec.gov/Archives/edgar/daily-index/` / bulk data page | For initial backfill/bootstrap of the whole database rather than company-by-company API calls |

### 14.2 XBRL tags (`us-gaap` namespace) to collect per company

This is the concrete field list to pull via the Company Facts / Company Concept API for
every ticker we track. Group by statement:

**Income Statement**
- `Revenues` (or `RevenueFromContractWithCustomerExcludingAssessedTax`)
- `CostOfRevenue` / `CostOfGoodsAndServicesSold`
- `GrossProfit`
- `OperatingExpenses`
- `OperatingIncomeLoss`
- `InterestExpense`
- `IncomeLossFromContinuingOperationsBeforeIncomeTaxes...`
- `IncomeTaxExpenseBenefit`
- `NetIncomeLoss`
- `EarningsPerShareBasic`
- `EarningsPerShareDiluted`
- `WeightedAverageNumberOfDilutedSharesOutstanding`
- `ShareBasedCompensation`

**Balance Sheet**
- `Assets`
- `AssetsCurrent`
- `CashAndCashEquivalentsAtCarryingValue`
- `Liabilities`
- `LiabilitiesCurrent`
- `LongTermDebtNoncurrent`
- `ShortTermBorrowings` / `DebtCurrent`
- `StockholdersEquity`
- `CommonStockSharesOutstanding`
- `Goodwill`
- `IntangibleAssetsNetExcludingGoodwill`
- `InventoryNet`
- `AccountsReceivableNetCurrent`
- `AccountsPayableCurrent`

**Cash Flow Statement**
- `NetCashProvidedByUsedInOperatingActivities`
- `PaymentsToAcquirePropertyPlantAndEquipment` (CapEx)
- `NetCashProvidedByUsedInInvestingActivities`
- `NetCashProvidedByUsedInFinancingActivities`
- `PaymentsOfDividends` / `CommonStockDividendsPerShareDeclared`
- `PaymentsForRepurchaseOfCommonStock`
- `ProceedsFromIssuanceOfLongTermDebt`
- `RepaymentsOfLongTermDebt`

**Segment / Disclosure (from 10-K footnotes, XBRL-tagged)**
- Segment revenue and operating income (`us-gaap:SegmentReportingInformation...` context-dimensioned facts)
- Geographic revenue breakdown, where disclosed

### 14.3 Filing types to ingest, by purpose

| Form | Purpose | Feeds section(s) |
|---|---|---|
| 10-K | Annual financials, full-year business/risk narrative | 1–7, 10, 11 |
| 10-Q | Quarterly financials | 1–7, 9, 11 |
| 8-K | Material events; Ex-99.1 earnings press releases (often contain guidance language, non-GAAP reconciliations) | 9 (guidance tracking), 13 |
| DEF 14A (Proxy) | Executive compensation, board/insider ownership detail | 13 (P2) |
| Form 3 | Initial insider ownership statement (new officer/director/10%+ holder) | 8 |
| Form 4 | Insider transactions (buys/sells) — the core insider-activity feed | 8 |
| Form 5 | Annual insider transaction summary (catches anything not reported on time via Form 4) | 8 |
| Schedule 13D / 13G | Beneficial ownership >5% — activist/large-holder disclosures | 8 |
| Form 13F | Institutional manager quarterly holdings — aggregate to get institutional ownership % and top holders | 8 |
| S-1 / S-3 / 424B | New issuance/registration — dilution early-warning signal | 6, 7 |

### 14.4 What EDGAR does NOT cover (must be sourced elsewhere)

- Real-time/delayed stock price, volume, 52-week range, beta
- Analyst estimates, ratings, price targets, estimate revisions
- Short interest and days-to-cover
- Credit ratings (S&P/Moody's/Fitch)
- Earnings call audio/transcripts (EDGAR only has the press release exhibit, not the call itself)
- GICS sector/industry classification (EDGAR gives SIC code, which is coarser and dated)

These require a market-data vendor and/or a transcript/estimates provider — flagged
throughout Sections 1–13 above wherever relevant.

### 14.5 Operational notes

- **Access requirement:** SEC requires a declared `User-Agent` header (app name + contact email) on every request; no API key needed.
- **Rate limit:** Stay at or below 10 requests/second; SEC will temporarily block IPs that exceed this.
- **Update cadence:** Company Facts/Submissions data updates in near real time as filings are accepted (submissions typically reflect within seconds; XBRL facts within about a minute). A daily sync per tracked company is sufficient for MVP; move to the real-time submissions feed later for "new filing" alerts.
- **Bootstrap strategy:** Use the nightly bulk ZIP (`companyfacts.zip`) for the initial load across all tracked tickers rather than one API call per company, then switch to incremental per-company polling for updates.

---

## What NOT to carry over directly

- **"Promoter Holding %"** — doesn't exist in US corporate structure; replace with Institutional Ownership (Form 13F) + Insider activity (Form 4).
- **ROCE as headline metric** — US investors respond better to ROIC.
- **Dividend-payout-as-quality-signal** — many great US companies (growth tech) pay no dividend; don't over-index pros/cons on this like the Indian version does.
- **BSE/NSE-style sector taxonomy** — use SIC (from EDGAR) as a fallback, GICS if licensed.

---

## Summary: Where the real differentiation lives

The base financials (P&L, balance sheet, cash flow, standard ratios) are commoditized —
every US broker and Yahoo Finance already shows them, and EDGAR gives us a free, direct,
standardized source for all of it. The wedge for a "Screener for US investors" is:

1. **FCF-centric quality metrics** (FCF yield, FCF vs. net income divergence, SBC dilution) — addresses US investors' distrust of GAAP earnings, computable entirely from EDGAR tags.
2. **Capital allocation tracking** (buybacks, total shareholder yield, dilution trend) — computable from EDGAR tags.
3. **Insider + institutional ownership signals** — direct from EDGAR Forms 4 and 13F, high-engagement data points not well-surfaced by mainstream free tools.
4. **Forward estimates + guidance track record** — the estimates side needs a paid/external feed, but guidance-language extraction and beat/miss tracking against it can be built from EDGAR 8-K/10-Q data.
5. **Auto-generated pros/cons, tuned to these signals** — Screener's biggest UX win, ported to US-relevant checks, computed in-house from the EDGAR-sourced dataset.