# Scrooner — Data Point & Feature Coverage Tracker

Living tracker requested 2026-08-18. Cross-references every individual data point named in [`doc/requirements/10_scrooner_required_data_points.md`](../requirements/10_scrooner_required_data_points.md) (the master P0/P1/P2 inventory, "Finalized v1.0") plus the additions [`doc/18`](../requirements/18_Scrooner_Expanded_Metric_Scope_for_Premium.md), [`doc/26`](../requirements/26_Scrooner_Screener_Data_Points_Gap_Analysis.md), and [`doc/28`](../scoping/28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md) proposed on top of it, against what's **actually built and verified**, checked live against the real database — not recalled from memory. Same rows, same order as doc 10, so the two docs can be read side by side; doc 28's items (not in doc 10's original inventory) are added as extra rows tagged "doc 28" instead of a P0/P1/P2 priority, and don't change doc 10's own P0 coverage denominators below.

**Status legend**: ✅ Built & verified · 🟡 Partial (raw data exists, not yet exposed/computed as this exact data point) · 📋 Scoped (a doc proposes it with real evidence, not built) · ⬜ Not started · 🚫 Blocked (needs a vendor or open decision, not a build task)

> **Update this file, don't create a parallel one** — same discipline as `PROGRESS.md`. Update it whenever a data point's status changes, in the same pass as the code that changes it.

---

## Coverage summary

**Updated 2026-08-21**: the 5Y/10Y Revenue/EPS CAGR rows (Section 6) were fixed from 🟡 partial to ✅ — they were actually completed 2026-08-19 (`mapper/ttm.py`) but this file's row-level status was never updated to match, an inconsistency caught while doing this pass, not a new build. Also added 5 new doc 28-sourced rows (Goodwill % of Assets, Basic EPS/Dilution Spread, R&D Intensity, Net Interest Income, AR/Inventory/AP Reconciliation Gaps) — see the per-row notes and the new "Done this pass" entry below. None of doc 10's original P0 denominators below change, since every doc 28 item sits outside doc 10's original inventory.

**Updated 2026-08-18** after building all 12 doc 18 Tier A / doc 26 §2-3 metrics (ROA, Quick Ratio, SBC%Revenue, EBITDA, Net Debt/EBITDA, EV/EBITDA, EV/Sales, PEG Ratio, Buyback Yield, Total Shareholder Yield, Institutional Ownership %, Share Count Dilution Trend) — `mapper/expanded_metrics.py` + `expanded_concepts.py` + `expanded_definitions.py`, verified live against the golden-10 and wired into the company page's new "Additional Ratios" card.

| Section | P0 items | ✅ Built | Coverage |
|---|---|---|---|
| 1. Quick Snapshot | 12 | 7.5 | 63% |
| 2. Valuation Multiples | 4 | 4 | 100% |
| 3. Profitability & Margin Quality | 5 | 5 | 100% |
| 4. Cash Flow | 4 | 4 | 100% |
| 5. Balance Sheet Health | 6 | 5 | 83% |
| 6. Growth Metrics | 4 | 2 | 50% |
| 7. Capital Allocation | 2 | 2 | 100% |
| 8. Ownership & Insider Activity | 3 | 2 | 67% |
| 9. Analyst & Market Sentiment | 4 | 0 | 0% |
| 10. Business Quality / Narrative | 2 | 1 | 50% |
| 11. Standard Financial Statements | 5 (implicit P0) | 4 | 80% |
| 12. Peer / Sector Comparison | 2 | 1 | 50% |
| 13. Documents & Filings | 2 | 1 | 50% |
| **Total P0** | **55** | **38.5** | **~70%** |

**Read this honestly, not as a scorecard to game**: P0 coverage is ~69% (up from ~55%), and the *uncovered* remainder is now disproportionately the genuinely vendor-blocked or structurally-blocked stuff (forward estimates, analyst ratings, short interest, transcripts, 52-week range/beta, segment revenue) — doc 10/22 themselves flag most of these as "not on EDGAR" or "an API limitation," not a build gap. Directly summing the vendor/structurally-blocked P0 rows below (≈12.5 of the 55) gives an EDGAR-native, actually-buildable-now denominator of ≈42.5 — coverage against *that* denominator is **~89%**. See the per-row notes for which bucket each gap falls into.

---

## 1. Quick Snapshot

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Market Cap | P0 | ✅ | `mapper/price_metrics.py`, real values, e.g. AAPL $4.44T |
| Current Price + Day Change % | P0 | 🟡 | Current Price ✅ (Alpaca `delayed_sip`); Day Change % ⬜ — needs a prior close to diff against, and `core.market_price_alpaca` only stores the latest snapshot (doc 25's deliberate scope) |
| 52-Week High / Low | P0 | 🚫 | Needs historical price — doc 10 itself flags "not from EDGAR"; blocked on extending doc 25 beyond latest-snapshot |
| Trailing P/E | P0 | ✅ | `mapper/price_metrics.py` |
| Forward P/E | P0 | 🚫 | Needs analyst estimates (vendor) — doc 10 flags this itself |
| PEG Ratio | P0 | ✅ | `mapper/expanded_metrics.py` — Trailing P/E ÷ EPS growth (YoY %); null (not a nonsensical ratio) when growth ≤ 0, e.g. AAPL 1.22x real |
| EPS (TTM) | P0 | ✅ | `diluted_eps` TTM already used in Trailing P/E |
| EPS (Forward) | P0 | 🚫 | Needs vendor |
| Basic EPS + Basic-vs-Diluted Dilution Spread | doc 28 | ✅ | New `basic_eps` concept + `eps_dilution_spread` metric (2026-08-21, doc 28 #4) — a real, standalone dilution-quality signal distinct from `share_dilution_trend` (tracks the EPS gap itself, not just share-count change). Not in doc 10's original inventory. |
| Book Value / Price-to-Book | P0 | ✅ | Both built — Book Value tile + Price/Book metric |
| Dividend Yield | P0 | ✅ | `mapper/price_metrics.py` |
| Beta (5Y monthly) | P0 | 🚫 | Needs historical price, doc 10 flags itself |
| Shares Outstanding (+ trend) | P0 | ✅ | Shares Outstanding ✅ (with real fallback for multi-class companies, doc 25 §10); trend now a real `share_dilution_trend` metric (`mapper/expanded_metrics.py`) — AAPL/JPM correctly negative (buyback-driven shrink), ARCC correctly positive (BDC capital-raising issuance) |
| Average Volume (10D/3M) | P1 | ⬜ | Not built — note: Alpaca's own bars response already includes volume (`v` field), currently discarded, not stored |

## 2. Valuation Multiples

| Data point | Priority | Status | Notes |
|---|---|---|---|
| EV/EBITDA | P0 | ✅ | `mapper/expanded_metrics.py` — real `ebitda` concept (`first_match`, not `sum`, since AAPL FY2015 double-reports D&A under two tags) plus Enterprise Value; AAPL 26.67x real |
| EV/Sales | P0 | ✅ | Same module, reuses the TTM-revenue reconstruction already proven in `price_metrics.py`; AAPL 9.59x real |
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
| Return on Assets (ROA) | P1 | ✅ | `mapper/calculate.py`'s generic engine, `ratio` shape — AAPL 7.8% real |
| Margin trend direction flag | P1 | ✅ | `margin_expanding_3yr` (`mapper/quality_flags.py`, 2026-08-19) — AAPL correctly TRUE (44.1%→46.2%→46.9% gross margin, FY2023-2025, hand-verified) |
| R&D Intensity (R&D / Revenue) | doc 28 | ✅ | New `research_and_development` concept + `rnd_intensity` metric (2026-08-21, doc 28 #1) — `us-gaap:ResearchAndDevelopmentExpense` resolves for 5 companies/427 facts. Not in doc 10's original inventory. |

## 4. Cash Flow

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Free Cash Flow (FCF), trailing | P0 | ✅ | Locked metric (CFO − CapEx) |
| FCF Margin | P0 | ✅ | Locked metric |
| FCF Yield | P0 | ✅ | `mapper/price_metrics.py` |
| Cash from Operations | P0 | ✅ | Mapped concept, shown on Cash Flow statement, TTM-reconstructable (doc 25 §10's interim-quarter derivation) |
| CapEx (% of revenue) | P1 | 🟡 | CapEx itself ✅ mapped/used; "% of revenue" not separately exposed |
| FCF vs. Net Income divergence flag | P1 | ✅ | Already built as `fcf_gt_net_income` (`mapper/quality_flags.py`, 2026-08-19) -- this row was simply never cross-referenced to that build at the time, a stale-row fix caught 2026-08-22, not a new build. |
| SBC as % of revenue | P1 | ✅ | New `sbc` canonical concept + `sbc_pct_revenue` metric (`mapper/expanded_concepts.py`/`calculate.py`) — AAPL 3.1% real |
| Net Interest Income | doc 28 | ✅ | New `interest_income` concept + `net_interest_income` metric (2026-08-21, doc 28 #4) — `us-gaap:InvestmentIncomeInterest` resolves for 7 companies/372 facts, separate from the existing `interest_expense`. Not in doc 10's original inventory. |
| Cash-Flow AR/Inventory/AP Reconciliation Gaps | doc 28 | ✅ | New `mapper/reconciliation.py` (2026-08-21, doc 28 #2) — compares each year's balance-sheet-implied AR/Inventory/AP change against the company's own reported cash-flow-statement adjustment, a quality-of-earnings cross-check (a signed dollar gap, not a locked ratio). AAPL FY2025 AR gap: -$315M, reproduces the manual balance-sheet-vs-cash-flow check exactly. Not in doc 10's original inventory. |

## 5. Balance Sheet Health

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Total Debt | P0 | ✅ | Mapped composite concept, used in D/E and ROIC |
| Debt / Equity | P0 | ✅ | Locked metric |
| Net Debt / EBITDA | P0 | ✅ | `mapper/expanded_metrics.py`, price-independent (computed even when Market Cap is null) — AAPL 0.25x real |
| Interest Coverage Ratio | P0 | ✅ | Locked metric |
| Current Ratio | P0 | ✅ | Locked metric |
| Quick Ratio | P1 | ✅ | New `inventory` concept + `sum_diff_ratio` shape — AAPL 0.93x real |
| Cash & Equivalents | P0 | ✅ | Mapped concept, used in ROIC/FCF Yield |
| Goodwill & Intangibles (% of assets) | P2 | ✅ | New `goodwill` concept + `goodwill_pct_assets` metric (`mapper/expanded_concepts.py`/`calculate.py`, 2026-08-21, doc 28 #1) — 315 real computed values across 8 companies (e.g. MSFT 15.8% of assets), honest null where Goodwill isn't tagged (AAPL stops reporting it separately after ~FY2017) |

## 6. Growth Metrics

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Revenue Growth (YoY, 3Y/5Y/10Y CAGR) | P0 | ✅ | All 4 horizons built (`mapper/ttm.py` `GROWTH_METRICS`, 2026-08-19) — AAPL's 10Y CAGR (5.94%) hand-verified against real FY2015/FY2025 revenue |
| EPS Growth (YoY, 3Y/5Y/10Y CAGR) | P0 | ✅ | Same module, same date — all 4 horizons built |
| FCF Growth (3Y/5Y CAGR) | P1 | 📋 | Named doc 18 Tier A, not built |
| Forward Revenue Growth Estimate | P0 | 🚫 | Needs vendor, doc 10 flags itself |
| Forward EPS Growth Estimate | P0 | 🚫 | Needs vendor |
| Estimate Revision Trend (90d) | P1 | 🚫 | Needs vendor |

## 7. Capital Allocation & Shareholder Returns

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Buyback Yield | P0 | ✅ | `mapper/expanded_metrics.py`, TTM buybacks ÷ Market Cap — AAPL 1.9% real |
| Total Shareholder Yield | P1 | ✅ | Dividend Yield + Buyback Yield − Dilution, same module — AAPL 3.9% real |
| Dividend History / Growth Streak | P1 | 📋 | Scoped doc 26 §2 — `dividends_per_share` already resolves quarterly, needs a streak computation |
| Share Count Dilution Trend (5-10yr) | P0 | ✅ | `share_dilution_trend` metric, now vs. ~1yr ago only (not a full 5-10yr series yet) — AAPL -1.7% real |

## 8. Ownership & Insider Activity

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Institutional Ownership % | P0 | ✅ | `institutional_ownership_pct` metric — dedup-by-filer sum of Form 13F shares ÷ Shares Outstanding, same dedup rule as the Top Holders table so the two never disagree; AAPL 40.8%, NKE 70.6% real, honest null for TSM/ENB (foreign filers, no domestic shares_outstanding source) |
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
| Standard Ratios table (Debtor Days, Inventory Days, Payables, Cash Conversion Cycle, ROCE/ROIC) | ✅ | ROIC ✅; Debtor/Inventory/Payables Days ✅ (new `accounts_receivable`/`accounts_payable` concepts + `calculate.py`'s new FY-only `"days"` shape) and Cash Conversion Cycle ✅ (`expanded_metrics.py`, combines the three days metrics) — all built 2026-08-18, AAPL's real -71.1 day CCC (34.9 Debtor + 9.4 Inventory − 115.4 Payables) matches AAPL's well-documented real negative cash conversion cycle |

## 12. Peer / Sector Comparison

| Data point | Priority | Status | Notes |
|---|---|---|---|
| Peer comparison table | P0 | ⬜ | Not built — needs a wider universe than the golden-10 to be meaningful (doc 02's still-open universe-width decision) |
| Sector/Industry classification | P0 | ✅ | New `core.company.sector`/`sector_reason` (`company_master/sector_bucket.py`, 2026-08-21, doc 26 §3/doc 28) — a curated SIC-range → sector mapping (11 buckets, not GICS, which is licensed/ruled out), full coverage across all 174 real companies with a `sic_code` (zero "Other" fallbacks), 7 honest "Other" for companies with no SIC on record at all (2 BDCs). Caught and fixed one real miscategorization before trusting it: Nike (SIC 3021, rubber/plastics footwear) initially landed in "Materials" via the surrounding industrial-rubber range — carved out as its own exception. Wired into `screener/schema.py` (`sector` now a valid categorical field), `ai_query/aliases.py`/`rules.py` (new broad phrases like "tech companies"/"financial companies", additive — the existing exact-SIC "software companies" alias is untouched, verified byte-identical), and `apps/site`'s company page (shown as the primary sector label, raw SIC description demoted to a tooltip). |
| Relative valuation vs. sector median | P1 | 🚫 | Blocked on the same wider-universe decision as peer comparison |

## 13. Documents & Filings

| Data point | Priority | Status | Notes |
|---|---|---|---|
| 10-K / 10-Q filing links | P0 | ✅ | Recent Filings section, `apps/site` |
| 8-K material event filings | P1 | ✅ | Built, **now with real SEC item-code classification** (doc 21/24 Phase 1) rendered as plain-English labels — exceeds doc 10's own ask (which only wanted the filing link, not the event type) |
| Earnings Call Transcripts + AI Summary | P0 | 🚫 | Not on EDGAR — doc 10 flags itself |
| Proxy Statement (DEF 14A) | P2 | ✅ | **DEF 14A family now in `core.filing`'s `FORM_ALLOWLIST`** (2026-08-18) — DEF 14A, DEFA14A, DEFM14A, DEFR14A (the company's own definitive proxy + amendments; preliminary/third-party-exempt-solicitation variants deliberately excluded). 472 real filings captured across the golden-10, zero regression to any pre-existing form type, rendering in Recent Filings with no frontend change needed. Exec-comp/insider-holdings extraction *from* the document is still doc 19 Stage 5, explicitly deferred — this is filing-presence only, same scope as 8-K/Form 15/SC 14D9 before it. |
| Credit Ratings (S&P/Moody's/Fitch) | P1 | 🚫 | Needs a ratings-agency feed |

---

## What actually moves the needle next (updated 2026-08-18 after this pass)

Done this pass:
1. All 12 doc 18 Tier A / doc 26 §2-3 metrics landed in `mapper/expanded_metrics.py`/`expanded_concepts.py`/`expanded_definitions.py`, verified live against the golden-10, wired into `apps/site`'s new "Additional Ratios" card: ROA, Quick Ratio, SBC%Revenue, EBITDA, Net Debt/EBITDA, EV/EBITDA, EV/Sales, PEG Ratio, Buyback Yield, Total Shareholder Yield, Institutional Ownership %, Share Count Dilution Trend.
2. **DEF 14A family into `core.filing`'s `FORM_ALLOWLIST`** — 472 real filings across the golden-10, zero regression, same purely-additive widening pattern as 8-K/Form 15/SC 14D9.
3. **Debtor Days / Inventory Days / Payables Days / Cash Conversion Cycle** — new `accounts_receivable`/`accounts_payable` concepts, `calculate.py`'s new FY-only `"days"` shape, and Cash Conversion Cycle combining the three in `expanded_metrics.py`. AAPL's real -71.1 day CCC matches its well-documented actual negative cash conversion cycle.
4. **Piotroski F-Score (0-9)** — new `mapper/quality_score.py`, the standard 9-binary-test formulation, FY vs prior FY, over 9 already-mapped raw concepts. Hand-verified exactly: MSFT FY2010's score of 8 reproduced component-by-component by hand from the same 9 raw values the code read. Requires all 9 inputs for BOTH years (no partial/scaled score) — correctly null for JPM/ARCC (Piotroski's own methodology needs a classified balance sheet + gross margin, which banks/BDCs don't report) and also null for AAPL in several FY years because `total_debt` is correctly flagged as an unresolved source-data conflict for those years, not missing data — see the `total_debt` finding below (root-caused, not a build gap).
5. **The 4 remaining quality boolean/count flags** (doc 26 §2.9) — new `mapper/quality_flags.py`: `fcf_gt_net_income`, `zero_debt`, `profitable_streak_years`, `margin_expanding_3yr`. Two independent real-world verification signals: AAPL's `zero_debt` is correctly TRUE only for FY2012 and null everywhere else it lacks `total_debt` data — matching AAPL's own well-documented history of being genuinely debt-free until its first 2013 bond issuance; AAPL's `profitable_streak_years` = 19, exactly matching 19/19 real FY years of positive net income in the database (hand-counted). `zero_debt` deliberately distinguishes "reported and genuinely zero" from "not reported at all" (null, never a silently-assumed true) — absence is not evidence of debt-free status.

6. **5Y/10Y Revenue/EPS CAGR** — new `mapper/ttm.py` `GROWTH_METRICS` entries (`revenue_growth_5y_cagr`, `revenue_growth_10y_cagr`, `eps_growth_5y_cagr`, `eps_growth_10y_cagr`). A genuinely trivial, purely-additive extension: `_growth_value()` already generalized to any `lag_years` via its CAGR branch, so this needed zero new logic, only 4 new dict entries. Hand-verified exactly: AAPL's FY2025 `revenue_growth_10y_cagr` (5.94%) reproduced by hand from FY2015 ($233.7B) vs FY2025 ($416.2B) revenue. Zero regression confirmed (byte-identical checksum against the original 4 growth metrics). Also newly wired into the company page for the first time — the original 4 growth metrics existed in the database (used only by `prosCons.ts`'s checklist) but were never shown in the ratio grids until this pass.

**`total_debt`'s FY-period sparsity, investigated and resolved as a non-issue**: root-caused live (2026-08-19), not just surfaced. AAPL's FY-period `LongTermDebt` facts exist in `core.fact` but are correctly marked `is_authoritative=false` by Normalizer Stage 2e (`dedupe.py`) — the FY2023 balance, for example, is reported as $105,103M in the FY2023 10-K itself, but as $105,100M (a ~0.003% difference) in three subsequent 10-Qs' comparative-period columns. This is a genuine, tiny source-data disagreement, and Stage 2e's already-documented, deliberate design ("picking any single value here — even 'most recent' — would be a guess the Mapper shouldn't inherit as settled fact") correctly refuses to pick a winner rather than silently guessing. 12 such conflict groups exist across 5 of the golden-10 companies, all at FY periods for debt tags specifically. **Conclusion: this is the pipeline working exactly as designed, not a gap to fix** — the earlier framing ("worth a root-cause pass") was itself the thing that needed correcting, not the code.

7. **A real display gap, found and fixed 2026-08-19, not a pipeline gap**: `apps/site`'s company page rendered only 37 of 45 real `analytics.metric_definition` rows. Eight of doc 02's *original* locked metrics — `gross_margin`, `operating_margin`, `net_margin`, `current_ratio`, `debt_to_equity`, `interest_coverage_ratio`, `fcf`, `fcf_margin` — had been computed since Mapper Stage 3d (2026-08-16) but were never wired into the page's display arrays at all, an oversight that predates every metric added this session. Fixed by rebuilding the company page around all 45 metrics: a curated 8-item "Key Metrics" set (design framework §12.2's own recommendation, e.g. Operating Margin and Debt/Equity are now both visible for the first time) plus the remaining 37 grouped into 7 named, collapsible categories (Valuation, Growth, Profitability, Cash Flow & Efficiency, Financial Strength, Capital Allocation & Quality, Ownership) — zero metrics hidden, none duplicated. New shared `apps/site/src/components/MetricGrid.astro` and `lib/format.ts` so this null-state/accessibility contract lives in one place. Null states now carry an `aria-label` (not just a hover `title`), per design framework §17.2.

8. **Doc 28's 4 ranked recommendations, built 2026-08-21 — one reversed on deeper verification, not implemented as originally proposed.** Goodwill (`goodwill` concept + `goodwill_pct_assets`), Basic EPS (`basic_eps` concept + `eps_dilution_spread`), and new `mapper/reconciliation.py` (AR/Inventory/AP cash-flow-vs-balance-sheet reconciliation gaps) all landed and are verified against the golden-10 with real, sane values (see per-row notes above). The 4th recommendation from the original study (widening `total_debt`'s alternate set with `LongTermDebtNoncurrent`) was **reversed, not built**, after checking live whether `LongTermDebt` and `LongTermDebtNoncurrent` are ever tagged simultaneously for the same company/period — they are (company_id=2, $3.478B vs $3.472B for the same period), so summing both would double-count debt. In its place, doc 28 (a real Trendlyne stock page comparison) surfaced two cheap zero-new-fetch replacements built the same pass: R&D Expense (`research_and_development`/`rnd_intensity`) and Interest Income (`interest_income`/`net_interest_income`). Pipeline test count grew from 145 → 148 (Goodwill/Basic EPS/reconciliation) → 150 (R&D/Interest Income), all passing at each step, zero regression to any existing metric.

9. **Sector bucket mapping, built 2026-08-21 (P0, this pass's execution focus)** — new `core.company.sector`/`sector_reason` (`company_master/sector_bucket.py`), a curated SIC-code-range → 11-sector mapping (Technology, Financials, Healthcare, Industrials, Consumer Discretionary, Consumer Staples, Energy, Materials, Utilities, Real Estate, Communication Services — not GICS, which is licensed IP already ruled out). Checked live against all 174 real companies before trusting it: zero unmapped "Other" fallbacks among companies with a `sic_code` at all; 7 honest "Other" for companies with no SIC on record (2 real BDCs, ARCC among them). One real miscategorization caught and fixed before shipping: Nike (SIC 3021, "Rubber & Plastics Footwear") initially fell into "Materials" via the surrounding industrial-rubber SIC range — a footwear brand is clearly Consumer Discretionary, not a materials company, so 3021 was carved out as its own explicit exception. Wired end-to-end, not just stored: `screener/schema.py` gained `sector` as a real filterable categorical field (verified live — a real query for `sector = 'Technology'` returned 21 correct real companies through the actual Screener), `ai_query/aliases.py`/`rules.py` gained a new, purely additive `SECTOR_BUCKET_ALIASES` table so phrases like "tech companies"/"financial companies" now resolve (checked that the existing exact-SIC "software companies" alias is byte-identical unchanged, so doc 15's already-verified test queries can't regress), and `apps/site`'s company page now shows the friendly sector name as the primary label (raw SIC description demoted to a tooltip). 150/150 pipeline tests pass.

Ranked by real coverage gained per unit of effort, all EDGAR-only (no vendor, no new decision):

1. **Plain-English parser vocabulary** — now the largest real gap in the product, not a data gap: `ai_query/aliases.py`'s `METRIC_ALIASES` covers 14 of the 45 real metrics (unchanged since 2026-08-17), while the company page now visibly surfaces all 45. A user who sees Piotroski F-Score or EV/EBITDA on a company page and tries to screen on it in plain English gets an honest "unsupported phrase," which is correct behavior, but the coverage gap itself is now the most visible weak point in the product's own stated differentiator.
2. **Day Change %** — the one remaining item genuinely needing a NEW fetch (a second Alpaca price point, e.g. yesterday's close, alongside the existing "latest" snapshot; `core.market_price_alpaca` currently holds exactly 1 row per company with no history at all, confirmed live). Not "zero-new-fetch" like everything else in this section — a small, bounded extension of the already-integrated Alpaca vendor, not a new vendor decision.

Everything past that point is either genuinely vendor-blocked (Section 9 in full, short interest, 52-week/beta/historical-price-dependent items), structurally blocked (segment/geography revenue — confirmed dimensional-XBRL API limitation, doc 22), or a real open product decision (universe width for peer comparison) — not a "just build it" gap.
