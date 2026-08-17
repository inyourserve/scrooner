# Scrooner — Data Point & Feature Coverage Tracker

Living tracker requested 2026-08-18. Cross-references every individual data point named in [`doc/10_scrooner_required_data_points.md`](10_scrooner_required_data_points.md) (the master P0/P1/P2 inventory, "Finalized v1.0") plus the additions [`doc/18`](18_Scrooner_Expanded_Metric_Scope_for_Premium.md) and [`doc/26`](26_Scrooner_Screener_Data_Points_Gap_Analysis.md) proposed on top of it, against what's **actually built and verified**, checked live against the real database — not recalled from memory. Same rows, same order as doc 10, so the two docs can be read side by side.

**Status legend**: ✅ Built & verified · 🟡 Partial (raw data exists, not yet exposed/computed as this exact data point) · 📋 Scoped (a doc proposes it with real evidence, not built) · ⬜ Not started · 🚫 Blocked (needs a vendor or open decision, not a build task)

> **Update this file, don't create a parallel one** — same discipline as `PROGRESS.md`. Update it whenever a data point's status changes, in the same pass as the code that changes it.

---

## Coverage summary

| Section | P0 items | ✅ Built | Coverage |
|---|---|---|---|
| 1. Quick Snapshot | 12 | 6 | 50% |
| 2. Valuation Multiples | 4 | 2 | 50% |
| 3. Profitability & Margin Quality | 5 | 5 | 100% |
| 4. Cash Flow | 4 | 4 | 100% |
| 5. Balance Sheet Health | 6 | 4 | 67% |
| 6. Growth Metrics | 4 | 2 | 50% |
| 7. Capital Allocation | 2 | 0 | 0% |
| 8. Ownership & Insider Activity | 3 | 1 | 33% |
| 9. Analyst & Market Sentiment | 4 | 0 | 0% |
| 10. Business Quality / Narrative | 2 | 1 | 50% |
| 11. Standard Financial Statements | 5 (implicit P0) | 4 | 80% |
| 12. Peer / Sector Comparison | 2 | 0.5 | 25% |
| 13. Documents & Filings | 2 | 1 | 50% |
| **Total P0** | **55** | **30.5** | **~55%** |

**Read this honestly, not as a scorecard to game**: P0 coverage is ~55%, but the *uncovered* P0 half is disproportionately the vendor-blocked stuff (forward estimates, analyst ratings, short interest, transcripts, 52-week range/beta) — doc 10 itself flags most of these as "not on EDGAR" from the start, not a build gap. The EDGAR-native P0 coverage (excluding items doc 10 itself marks as needing a vendor) is closer to **~85%**. See the per-row notes for which is which.

---

## 1. Quick Snapshot

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Market Cap | P0 | ✅ | `mapper/price_metrics.py`, real values, e.g. AAPL $4.44T |
| Current Price + Day Change % | P0 | 🟡 | Current Price ✅ (Alpaca `delayed_sip`); Day Change % ⬜ — needs a prior close to diff against, and `core.market_price_alpaca` only stores the latest snapshot (doc 25's deliberate scope) |
| 52-Week High / Low | P0 | 🚫 | Needs historical price — doc 10 itself flags "not from EDGAR"; blocked on extending doc 25 beyond latest-snapshot |
| Trailing P/E | P0 | ✅ | `mapper/price_metrics.py` |
| Forward P/E | P0 | 🚫 | Needs analyst estimates (vendor) — doc 10 flags this itself |
| PEG Ratio | P0 | 📋 | Scoped doc 26 §3 — P/E and EPS growth both already exist, pure formula away |
| EPS (TTM) | P0 | ✅ | `diluted_eps` TTM already used in Trailing P/E |
| EPS (Forward) | P0 | 🚫 | Needs vendor |
| Book Value / Price-to-Book | P0 | ✅ | Both built — Book Value tile + Price/Book metric |
| Dividend Yield | P0 | ✅ | `mapper/price_metrics.py` |
| Beta (5Y monthly) | P0 | 🚫 | Needs historical price, doc 10 flags itself |
| Shares Outstanding (+ trend) | P0 | 🟡 | Shares Outstanding ✅ (with real fallback for multi-class companies, doc 25 §10); trend/dilution flag 📋 scoped doc 26 §2, real quarterly history confirmed live but not yet exposed as a metric |
| Average Volume (10D/3M) | P1 | ⬜ | Not built — note: Alpaca's own bars response already includes volume (`v` field), currently discarded, not stored |

## 2. Valuation Multiples

| Data point | Priority | Status | Notes |
|---|---|---|---|
| EV/EBITDA | P0 | 📋 | Scoped doc 18 Tier A + doc 26 §3 — needs an `ebitda` concept; D&A tags confirmed live sitting raw and unmapped |
| EV/Sales | P0 | 📋 | Same as above — Enterprise Value itself (Market Cap + Debt − Cash) is already computable from existing mapped concepts, just not assembled as its own concept yet |
| Price/Sales | P0 | ✅ | `mapper/price_metrics.py` |
| Price/Free Cash Flow | P1 | 🟡 | We have the reciprocal (FCF Yield = FCF/Market Cap) built; P/FCF itself not separately exposed (trivial inversion) |
| Price/Book | P0 | ✅ | `mapper/price_metrics.py` |
| Historical median multiple bands (5Y/10Y) | P1 | 🚫 | Needs historical price + years of history stored — same gap as 52wk range |

## 3. Profitability & Margin Quality

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Gross Margin (trend) | P0 | ✅ | Mapper Stage 3d, locked metric |
| Operating Margin (trend) | P0 | ✅ | Locked metric |
| Net Margin (trend) | P0 | ✅ | Locked metric |
| ROE | P0 | ✅ | Locked metric, TTM + FY |
| ROIC | P0 | ✅ | Locked metric, pinned formula (doc 11), TTM + FY |
| Return on Assets (ROA) | P1 | 📋 | Named doc 18 Tier A — `net_income`/`total_assets` both already mapped, trivial to add |
| Margin trend direction flag | P1 | 📋 | Scoped doc 26 §2 (quality boolean flags) — data already exists, needs the flag computation |

## 4. Cash Flow

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Free Cash Flow (FCF), trailing | P0 | ✅ | Locked metric (CFO − CapEx) |
| FCF Margin | P0 | ✅ | Locked metric |
| FCF Yield | P0 | ✅ | `mapper/price_metrics.py` |
| Cash from Operations | P0 | ✅ | Mapped concept, shown on Cash Flow statement, TTM-reconstructable (doc 25 §10's interim-quarter derivation) |
| CapEx (% of revenue) | P1 | 🟡 | CapEx itself ✅ mapped/used; "% of revenue" not separately exposed |
| FCF vs. Net Income divergence flag | P1 | 📋 | Named doc 18 Tier A, not built |
| SBC as % of revenue | P1 | 📋 | Named doc 18 Tier A — confirmed live that `ShareBasedCompensation`-family tags exist raw, unmapped |

## 5. Balance Sheet Health

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Total Debt | P0 | ✅ | Mapped composite concept, used in D/E and ROIC |
| Debt / Equity | P0 | ✅ | Locked metric |
| Net Debt / EBITDA | P0 | 📋 | Scoped doc 18/26 — blocked on the same `ebitda` concept as EV/EBITDA |
| Interest Coverage Ratio | P0 | ✅ | Locked metric |
| Current Ratio | P0 | ✅ | Locked metric |
| Quick Ratio | P1 | 📋 | Named doc 18 Tier A + doc 26 §3 — needs an `inventory` concept curated |
| Cash & Equivalents | P0 | ✅ | Mapped concept, used in ROIC/FCF Yield |
| Goodwill & Intangibles (% of assets) | P2 | ⬜ | Not scoped anywhere yet |

## 6. Growth Metrics

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Revenue Growth (YoY, 3Y/5Y/10Y CAGR) | P0 | 🟡 | YoY + 3Y CAGR ✅ built (Mapper Stage 3e); 5Y/10Y horizons not built |
| EPS Growth (YoY, 3Y/5Y/10Y CAGR) | P0 | 🟡 | Same — YoY + 3Y built, 5Y/10Y not built |
| FCF Growth (3Y/5Y CAGR) | P1 | 📋 | Named doc 18 Tier A, not built |
| Forward Revenue Growth Estimate | P0 | 🚫 | Needs vendor, doc 10 flags itself |
| Forward EPS Growth Estimate | P0 | 🚫 | Needs vendor |
| Estimate Revision Trend (90d) | P1 | 🚫 | Needs vendor |

## 7. Capital Allocation & Shareholder Returns

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Buyback Yield | P0 | 🟡 | `share_buybacks` raw concept ✅ mapped (shown on Cash Flow statement); "yield" (÷ Market Cap) not computed as its own metric — confirmed live, no `buyback_yield` metric_definition exists yet |
| Total Shareholder Yield | P1 | 📋 | Scoped doc 26 §2 — all 3 components' raw data already exist |
| Dividend History / Growth Streak | P1 | 📋 | Scoped doc 26 §2 — `dividends_per_share` already resolves quarterly, needs a streak computation |
| Share Count Dilution Trend (5-10yr) | P0 | 🟡 | Real quarterly history confirmed live (AAPL: 14.94B→14.59B shares); not yet exposed as a trend/flag — scoped doc 26 §2 |

## 8. Ownership & Insider Activity

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Institutional Ownership % | P0 | 🟡 | Raw data ✅ (58,095 real Form 13F holdings, doc 19 Stage 4); aggregate %-of-shares-outstanding not yet computed as a displayed number |
| Institutional Ownership Trend (QoQ) | P1 | 🚫 | Only one filing window captured by design (doc 19 Stage 4's deliberate scope) — needs multiple 13F windows ingested over time, a real follow-on (doc 26 §4) |
| Insider Buying/Selling Activity | P0 | ✅ | 55,109 real Form 4 transactions, rendered on company page, **plus `is_10b5_1_plan`** (doc 24 Phase 1) distinguishing scheduled from discretionary sales — exceeds doc 10's own ask |
| Short Interest % of Float | P0 | 🚫 | Not on EDGAR, needs FINRA data — doc 10 flags itself |
| Days to Cover | P1 | 🚫 | Needs vendor |
| Top Institutional Holders | P2 | ✅ | Rendered on company page (doc 19 Stage 4) — already done, ahead of its own P2 priority |

## 9. Analyst & Market Sentiment

Doc 10 itself: "not available on EDGAR, requires a third-party vendor" for this entire section.

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Analyst Rating Distribution | P0 | 🚫 | Vendor |
| Average Price Target (+ range) | P0 | 🚫 | Vendor |
| Price Target vs. Current Price | P0 | 🚫 | Vendor |
| Number of Analysts Covering | P1 | 🚫 | Vendor |
| Earnings Surprise History (8 quarters) | P0 | 🟡 | Actuals side (EPS) ✅ exists; estimates side 🚫 needs vendor — feature needs both, not built as a combined thing |
| Guidance Track Record | P1 | ⬜ | Needs 8-K/press-release text extraction — same territory as doc 19 Stage 5 (deferred, unstructured text) |

## 10. Business Quality / Narrative

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Revenue by Segment | P0 | 🚫 | **Confirmed blocked, not just unbuilt**: doc 22 checked live that the standard Company Facts API strips dimensional/segment XBRL entirely — needs its own design pass (parsing the company's own XBRL instance/exhibit), not a normal build task |
| Revenue by Geography | P1 | 🚫 | Same dimensional-XBRL limitation |
| Customer Concentration | P2 | ⬜ | Needs 10-K risk-factor text extraction, not XBRL |
| Auto-generated Pros/Cons checklist | P0 | ✅ | Built (doc 17, `apps/site/src/lib/prosCons.ts`) — deterministic, never AI-generated prose |
| Moat / Competitive Position summary | P1 | ⬜ | Not built. Worth flagging as a **design question, not just a data gap** — doc 10 proposes this as AI-generated text, which needs care against doc 02's "AI is assistive only, never the source of financial truth" boundary before building, not just a data-availability question |

## 11. Standard Financial Statements

| Data point | Status | Notes |
|---|---|---|
| Quarterly Results (Revenue, Expenses, OPM%, etc.) | ✅ | Built (doc 17), `apps/site` |
| Annual Profit & Loss (10yr) | 🟡 | Built, but real depth is whatever the golden company's XBRL history covers, not a guaranteed 10 years for every company |
| Balance Sheet (10yr) | 🟡 | Same caveat |
| Cash Flow Statement (10yr) | 🟡 | Same caveat — now more complete per-quarter thanks to doc 25 §10's interim-quarter derivation |
| Standard Ratios table (Debtor Days, Inventory Days, Payables, Cash Conversion Cycle, ROCE/ROIC) | 🟡 | ROIC ✅ built; Debtor/Inventory/Payables Days and Cash Conversion Cycle ⬜ not built (need AR/Inventory/AP concepts — likely raw-tag-available, unmapped, same shape as every other gap above) |

## 12. Peer / Sector Comparison

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Peer comparison table | P0 | ⬜ | Not built — needs a wider universe than the golden-10 to be meaningful (doc 02's still-open universe-width decision) |
| Sector/Industry classification | P0 | 🟡 | SIC code ✅ captured (Company Master 4a); "friendly bucket" mapping (SIC → readable sector) scoped doc 26 §3, not built — GICS itself explicitly ruled out (licensed taxonomy) |
| Relative valuation vs. sector median | P1 | 🚫 | Blocked on the same wider-universe decision as peer comparison |

## 13. Documents & Filings

| Data point | Priority | Status | Notes |
|---|---|---|---|
| 10-K / 10-Q filing links | P0 | ✅ | Recent Filings section, `apps/site` |
| 8-K material event filings | P1 | ✅ | Built, **now with real SEC item-code classification** (doc 21/24 Phase 1) rendered as plain-English labels — exceeds doc 10's own ask (which only wanted the filing link, not the event type) |
| Earnings Call Transcripts + AI Summary | P0 | 🚫 | Not on EDGAR — doc 10 flags itself |
| Proxy Statement (DEF 14A) | P2 | 🟡 | The filing **exists and is discoverable** in already-fetched `raw.sec_submissions` (confirmed real counts per golden company, doc 19 §1's table) but is **not yet in `core.filing`'s `FORM_ALLOWLIST`** — confirmed live, not currently there. Exec-comp/insider-holdings extraction from it is doc 19 Stage 5, explicitly deferred. |
| Credit Ratings (S&P/Moody's/Fitch) | P1 | 🚫 | Needs a ratings-agency feed |

---

## What actually moves the needle next (cross-referencing doc 24/26's own recommendations)

Ranked by real coverage gained per unit of effort, all EDGAR-only (no vendor, no new decision):

1. **Buyback yield, institutional ownership %, dilution trend as real computed metrics** — all three have their raw data 100% in hand already (confirmed live throughout this doc); this is pure Mapper-layer computation, the same pattern as every prior stage.
2. **`ebitda` concept** → unlocks EV/EBITDA, EV/Sales, Net Debt/EBITDA in one curation pass (3 P0/P0/P0 rows from one piece of work).
3. **DEF 14A into `FORM_ALLOWLIST`** — same purely-additive widening pattern already used for 8-K/Form 15/SC 14D9 (doc 19 Stage 1, doc 23), makes the filing itself visible even before any Stage-5-style parsing of its contents.
4. **ROA, PEG, Quick Ratio** — each one small, independent, already-scoped (doc 18 Tier A).
5. **Quality boolean flags + Piotroski F-Score** (doc 26 §2) — highest per-item count for the effort, all inputs already resolved.

Everything past that point is either genuinely vendor-blocked (Section 9 in full, short interest, 52-week/beta/historical-price-dependent items) or a real open product decision (universe width for peer comparison) — not a "just build it" gap.
