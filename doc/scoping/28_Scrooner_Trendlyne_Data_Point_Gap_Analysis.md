# Doc 28 — Trendlyne Data Point Gap Analysis

**Status: Draft (2026-08-21) — a scoping proposal, not a build plan.** Prompted by a real reference page the user added at `doc/html/trendlyne-apple.html` (Trendlyne's live Apple stock page, captured 2026-08-20) and the instruction to sharpen the data moat by learning what a comparable product surfaces that Scrooner doesn't. Cross-references that page's actual content — extracted and read in full, not recalled from memory — against doc 10's master P0/P1/P2 inventory, doc 26's Screener gap analysis, `DATA_COVERAGE.md`, and today's own utilization-study build (doc `core-fact-utilization-study.md`). Every "new, feasible" candidate below was checked live against the real database before being recommended; every "already covered" or "already excluded" item was confirmed against an existing doc rather than assumed.

## What Trendlyne shows that Scrooner already has (no gap)

Confirmed by direct comparison, not assumption: Market Cap, PE (TTM), PEG, Price/Book, Institutional holding %, Revenue growth (qtr YoY, TTM), ROE, Net Profit growth (qtr, TTM), Operating Profit Margin, Piotroski Score, the full quarterly P&L line series (Revenue, Cost of Revenue, Gross Profit, Opex, Operating Profit, PBT, Tax, Net Income, EPS, EBIT, EBITDA, D&A), insider transactions (Form 4), institutional/13F holders, and dividend corporate actions. Trendlyne's "Check Before You Buy" checklist is functionally the same idea as `apps/site`'s already-built Pros/Cons checklist. Nothing here is a gap.

## Deliberately excluded already — confirmed against doc 02, not re-litigated here

These are real, prominent sections of the Trendlyne page, but doc 02 already made an explicit, named MVP exclusion covering each:

| Trendlyne section | doc 02 exclusion |
|---|---|
| Technical Analysis (EMA/SMA, RSI, MACD, MFI, ADX, ATR, CCI, ROC, Williams %R, Support/Resistance/Pivot, Delivery-vs-Volume) | "technical indicators" |
| Analyst Price Target, Consensus Recommendation (Buy/Sell/Hold counts), Forecaster (revenue/EPS estimates + "hit rate") | "analyst forecasts" |
| Real-time-feeling intraday price/volume ticking | doc 02's price vendor decision already locked delayed data (Alpaca `delayed_sip`), not real-time |
| Board Meetings (under Corporate Actions) | Not an SEC filing convention — this is an NSE/BSE announcement concept (scheduled board meeting dates ahead of Indian quarterly results); no US EDGAR equivalent exists to source it from |

None of these are new information — they confirm existing scope decisions rather than surface gaps.

## Genuinely new, real, and feasible — ranked by verified value

### 1. R&D Expense as its own canonical concept
Trendlyne's quarterly table breaks out "RnD Exp." as its own line, separate from "Admin Plus Selling Exp." — Scrooner currently only has SG&A-family tags in doc 26's unmapped-tag backlog, no R&D concept at all. **Checked live: `us-gaap:ResearchAndDevelopmentExpense` resolves for 5 companies, 427 authoritative facts** — real, single-tag, immediately mappable the same way `sbc`/`inventory` were. Enables a genuine new metric, R&D Intensity (R&D / Revenue), a standard quality/growth signal especially relevant for tech names — exactly the kind of company this product's target user cares about most. Cheapest, highest-confidence item on this list.

### 2. Ownership composition breakdown by holder category
Trendlyne shows ownership as a real breakdown — Insider % / Fund Company % / Mutual Fund % / Other % — not one aggregate "institutional ownership" number. Scrooner's `institutional_ownership_pct` metric already collapses everything into a single percentage. **Checked live: `core.institutional_ownership` has `filer_name`/`filer_cik` but no `filer_type`/holder-category column at all** — replicating Trendlyne's split needs a real, new classification layer (e.g. cross-referencing each 13F filer CIK against SEC's own registrant-type data, or a curated name-pattern ruleset), not just a regrouping of existing columns. Genuinely valuable (an "is this fund-heavy or insider-heavy" signal is more useful than one blended %) but a real build item, not a freebie — don't understate the effort the way this doc's own predecessor (`core-fact-utilization-study.md`) understated the `total_debt` widening risk before it was corrected.

### 3. Historical institutional-ownership trend (quarter-over-quarter, not a snapshot)
Trendlyne charts institutional/MF/insider holding % changing month-to-month ("Institutional Investors holding remains unchanged at 76.67% in Jul 2026"). **Checked live before assuming this was cheap: `core.institutional_ownership.report_period` has 73 distinct dates stored, but 50,786 of all rows belong to a single window (2026-03-31) — every other period is a handful of late-filed amendments, not real historical depth.** This directly matches doc 19/`pipeline/CLAUDE.md`'s own honest description of Stage 4 as "one recent filing window." A real ownership trend needs genuinely new bulk-13F fetches for multiple past quarters, the same shape of work as Stage 4 itself, repeated — not a display change on data already collected. Correcting an assumption I'd have otherwise carried into a recommendation.

### 4. Interest Income as its own concept
Scrooner has `interest_expense` (feeds `interest_coverage_ratio`) but no `interest_income` counterpart — Trendlyne's quarterly table separates "Interest Income" from "Interest Exp. Non Operating." **Checked live: `us-gaap:InvestmentIncomeInterest` resolves for 7 companies, 372 facts** (a cleaner match than the two other interest-income tag variants checked, which cover only 1-2 companies each). Enables a real Net Interest Income figure, useful for cash-rich balance sheets (this project's own golden-10 includes several).

### 5. P/E-vs-its-own-history valuation check
Trendlyne's "PE Valuation Check" states whether a stock is over/undervalued right now vs. its own historical PE range, both current and 1-year-forward. This is real and valuable, but it's not a new finding — doc 26 Tier 4 already named "valuation vs. history" as a real gap blocked on deeper historical price coverage, which is itself gated on Alpaca's price history accumulating past its 2026-08-17 integration date. No new recommendation here, just a second confirmation the same gap is worth prioritizing once enough price history exists.

## Real, but needs an explicit scope call before any build decision

### Beta (1-month/3-month/1-year/3-year)
Trendlyne shows Beta as a standalone stat, separate from its Technical Analysis section. Unlike RSI/MACD (trade-timing signals doc 02 already excluded by name), Beta is a classic risk/valuation stat (CAPM-style cost-of-equity input), arguably fundamental-adjacent rather than technical-analysis-adjacent. It's also fully computable from data Scrooner already owns once enough price history accumulates (a regression of the stock's own returns against a market-index proxy) — no new data source needed. Flagging this as a genuine gray area rather than silently bucketing it into "technicals" or building it unprompted — worth a founder call the same way doc 02's other open items are, not a default yes or no.

### Politician (Congressional) trading disclosures
A real, distinctive section on Trendlyne's US stock pages — periodic transaction reports under the STOCK Act, filed by members of Congress. This is genuinely interesting insider-adjacent alternative data, but it does **not** come from SEC EDGAR at all (House/Senate financial disclosure systems are separate from SEC filings) — it would require a brand-new external source, the same tier of decision as doc 02's other still-open vendor questions, not a Collector extension. Named here for completeness, not recommended for this pipeline without an explicit sourcing decision.

## What's NOT recommended

Trendlyne's DVM (Durability/Valuation/Momentum) composite scores are a real differentiator but proprietary methodology with no disclosed formula — not something to reverse-engineer or approximate. "Normalized Income"/"Normalized EBITDA" (analyst-style one-time-item adjustments) require judgment calls about what counts as non-recurring that XBRL doesn't structurally encode — a vendor/analyst function, not a raw-data extraction, and out of character for this project's "never fabricate, never guess" discipline.

## Ranked summary

1. R&D Expense concept + R&D Intensity metric — cheapest, highest-confidence, zero new fetch.
2. Interest Income concept + Net Interest Income — same tier, zero new fetch.
3. Ownership composition breakdown by holder category — real value, needs a new filer-classification layer (not free).
4. Historical institutional-ownership trend — real value, needs genuinely new multi-quarter 13F bulk fetches (not free, same shape as Stage 4's original build).
5. Beta — needs an explicit scope call (fundamental-adjacent risk stat vs. "technical indicator" exclusion) before any build decision.
6. Politician trading disclosures — needs an explicit new-data-source decision, same tier as doc 02's other open vendor questions.

Nothing in this document is built. Items 1-2 are the natural next build step if the utilization-study pattern (goodwill, basic EPS, cash-flow reconciliation) continues; items 3-6 each need a real decision or a real multi-quarter fetch before they're buildable, not just a docs update.
