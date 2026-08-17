# 18 — Scrooner: Expanded Metric Scope, Screener.in Gap Analysis, and the $100/Year Question

Prompted directly: "screener html has more data why we have less... scope more metric... so we can charge $100 from users." This doc does three things: (1) accounts honestly for why the built page has less than Screener.in's real page, (2) cross-references doc 10's already-done P0/P1/P2 inventory against doc 02's locked 18-metric list to find real, currently-buildable gaps, (3) proposes tiers toward a premium-worthy page — **without** silently expanding doc 02's locked list, which this project's own discipline treats as a real decision requiring explicit confirmation, not an ad-hoc addition (CLAUDE.md: *"~15–20 metrics / ~10 operators guardrail for MVP — not permission to expand ad hoc"*).

> **Status:** Draft (2026-08-17) — a scoping proposal, not a build plan. Nothing in this doc is locked until the user confirms which tier(s) to commit to. **Owner:** Founder / Product · **Review:** Once a tier is chosen, promote the relevant rows into doc 02 and write the actual build plan.

---

## 1. Why the built page has less than Screener.in's — three different reasons, not one gap

Doc 17 already scoped this per-section, but the honest accounting is three genuinely different kinds of "less," worth separating because they need different fixes:

| Reason | Examples | Fix |
|---|---|---|
| **Blocked on a vendor decision already flagged** | Market Cap, Current Price, Stock P/E, Dividend Yield, price chart | Close doc 02's still-open market-price vendor decision (unchanged ask from before) |
| **Data doc 10 already scoped but doc 02 didn't lock into the MVP 18** | EV/EBITDA, Quick Ratio, Buyback Yield, FCF Growth, ROA, and others — §2 below | **This is the real, addressable gap this doc is about** |
| **Needs new data collection or a new vendor entirely, bigger than "add a metric"** | Insider activity (Form 4), institutional ownership (Form 13F), analyst estimates, short interest, credit ratings, business-description text | A real, separate scope decision each — §3/§4 below, not solved by this doc |

**The page isn't "missing" data by accident — doc 02 deliberately locked a narrower 18-metric MVP list out of doc 10's fuller P0 inventory, for MVP-scope reasons ("kill scope aggressively").** That was the right call for *shipping something first*. It's a different question from "is 18 enough to charge $100/year for" — which is what's actually being asked now.

---

## 2. Tier A — real gaps, computable *right now*, zero new SEC collection

Checked live against the golden-8 before listing anything here, same discipline as every other metric-mapping decision this project has made — not copied from doc 10 without verifying the underlying tags actually exist in what's already collected.

| Metric | Doc 10 priority | Formula | Data readiness (checked live) |
|---|---|---|---|
| Quick Ratio | P1 | (Current Assets − Inventory) ÷ Current Liabilities | `InventoryNet` present for 5/8 golden companies (industry-structural: banks/BDCs genuinely don't carry inventory — same expected-null pattern as everywhere else) |
| Return on Assets (ROA) | P1 | Net Income ÷ Total Assets | Both inputs already resolved (`net_income` canonical, `total_assets` — new from doc 17's statement work) |
| FCF Growth (3Y/5Y CAGR) | P1 | Same YoY/CAGR pattern already built for revenue/EPS, applied to `fcf` | `fcf` already computed (Mapper); the growth-calculation code (`ttm.py`) already generalizes to any metric, not revenue/EPS-specific |
| Share Count Dilution Trend | P0 | `shares_outstanding` YoY change | `WeightedAverageNumberOfDilutedSharesOutstanding` present for **8/8** golden companies — the single most complete tag checked this session |
| SBC as % of Revenue | P1 | `ShareBasedCompensation` ÷ `revenue` | `ShareBasedCompensation` present for 7/8 |
| FCF vs. Net Income Divergence Flag | P1 | A checklist rule, not a new metric — `abs(fcf − net_income) / net_income > threshold` | Both inputs already resolved; this is a Pros/Cons checklist rule (doc 17 Sec 5 pattern), not new pipeline work |
| Net Debt / EBITDA | P0 | (`total_debt` − `cash_and_equivalents`) ÷ EBITDA | EBITDA needs `operating_income` (real) + D&A. D&A is fragmented across 3 tag variants (`DepreciationDepletionAndAmortization`, `Depreciation`, `DepreciationAmortizationAndAccretionNet` — 4-6 of 8 companies each) — genuine taxonomy drift, needs the same `first_match` curation as every other composite concept, not a blocker, just real work |
| EV/EBITDA, EV/Sales | P0 | Enterprise Value (Market Cap + Debt − Cash) ÷ EBITDA or Revenue | **Blocked on price**, same as the original 6 — EV needs Market Cap. Formula-lockable now, computable once 4b has real data, exactly like the original 6. |
| Buyback Yield, Total Shareholder Yield | P0/P1 | `share_buybacks` ÷ Market Cap (+ dividend yield) | `share_buybacks` already resolved (doc 17's statement work); **blocked on price** for the yield form, though "buybacks as % of shares outstanding" (no price needed) is a real, immediately-buildable alternative |

**9 real candidate metrics, of which 6 are buildable with zero price dependency at all** (Quick Ratio, ROA, FCF Growth, Dilution Trend, SBC%, FCF/NI divergence) — the other 3 (Net Debt/EBITDA needs D&A curation first; EV/EBITDA, EV/Sales, buyback/shareholder yield need price) split cleanly into "curate a composite concept" (same Mapper-Day-1-shaped work already proven) and "blocked on the same already-flagged decision," not new categories of problem.

---

## 3. Tier B — real, needs new SEC data collection (bigger than "add a metric")

| Data point | Doc 10 priority | What's actually needed |
|---|---|---|
| Insider Buying/Selling Activity | P0 | Form 4 collection — a new Collector form type, not currently fetched at all |
| Institutional Ownership % + Trend | P0/P1 | Form 13F aggregation — a new Collector form type, plus new aggregation logic (13F filings are filed by the *institution*, not the company — a materially different collection shape than everything built so far) |
| Revenue by Segment / Geography | P0/P1 | XBRL segment-dimensioned facts — technically already flowing through the Collector's raw payload, but Normalizer/Mapper never parse the dimensional (segment axis) structure, only top-line facts |

None of these are "just add a metric" — each is a real, separately-scoped Collector/Normalizer extension, closer in size to a mini version of a whole prior phase than to Tier A's curation work. Not solved here; flagged so the size difference from Tier A is visible before anyone assumes otherwise.

---

## 4. Tier C — needs an external vendor (same category as the price/LLM decisions already flagged)

Analyst Rating Distribution, Price Target, Forward P/E, Forward EPS, Estimate Revision Trend, Earnings Surprise History (estimates half), Short Interest, Credit Ratings, Earnings Call Transcripts. Doc 10 already correctly tagged every one of these as "not on EDGAR." **Not proposing a vendor here** — same discipline as the market-price and LLM decisions: flagged, not assumed, and this doc doesn't add a third open vendor decision without being asked to.

---

## 5. Does 18 (or 18+Tier A) actually support $100/year? — the honest business read

Doc 10's own conclusion (§"Summary: Where the real differentiation lives") already named this, worth restating because it directly answers the question: **the base financials are commoditized — every broker and Yahoo Finance already show P&L/balance sheet/cash flow/standard ratios for free.** The current 18 (Tier A included) stays in that commoditized zone — better *sourced* (traceable to the exact filing, never guessed) and better *presented* (plain English, deterministic screening) than free tools, but not differentiated on breadth alone.

Doc 10's own answer for what actually justifies paying: **FCF-centric quality signals, capital allocation tracking, and insider/institutional ownership signals** — not more ratios, but signals mainstream free tools don't surface well. Of those three, capital allocation (Tier A: buybacks, dilution trend, FCF divergence) is buildable now; insider/institutional ownership (Tier B) is the one with real, distinct product pull and is **not** buildable without new Collector scope.

**Honest conclusion**: Tier A meaningfully strengthens the page (worth doing) but doesn't, by itself, cross into "worth $100/year" territory the way Tier B's ownership signals would. That's a real product finding, not a reason to avoid Tier A — just don't let building Tier A create the impression the $100/year question is now answered.

---

## 6. Recommendation — explicit, not assumed

1. **Confirm Tier A for the locked metric list** — this doc proposes it, doesn't lock it. Doc 02's guardrail exists specifically so this kind of addition gets a deliberate yes, not an ad-hoc one.
2. **Treat Tier B (insider/institutional ownership) as the real next scope decision for the premium case** — a genuine new phase, not a metric addition, and the thing doc 10 itself already flagged as the actual differentiator.
3. **Leave Tier C alone** — three open vendor decisions (price, LLM, now estimates/ratings) would be a real pattern worth pausing on, not stacking further without evidence of demand for each.

---

## What this doc does *not* decide

- Whether to actually add Tier A to doc 02's locked list — proposed, not confirmed.
- Whether to build Tier B (Form 4/13F collection) — flagged as the real differentiator, not scheduled.
- Any new vendor (estimates, short interest, credit ratings) — explicitly not proposed here, same discipline as price/LLM.
