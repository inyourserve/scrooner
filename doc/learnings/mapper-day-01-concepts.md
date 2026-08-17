# Mapper Day 1 — Concept Mapping

## Two real correctness bugs caught before any resolver code ran

Before writing `mapper/concepts.py`, surveyed real tag co-occurrence across the golden-8 for all 17 canonical concepts (not just revenue/debt, already partly checked while planning doc 11). Two findings would have silently corrupted metrics if not caught:

### Bug 1: `total_debt` would have double-counted long-term debt for 6 of 7 companies

The plan (doc 11) called `total_debt` a "sum every mapped tag with data" composite. Checked whether any company reports both `LongTermDebt` (a combined figure) and the split `LongTermDebtCurrent`/`LongTermDebtNoncurrent` for the same period before trusting that design — 6 of 7 debt-reporting companies do. Verified the arithmetic directly on NKE: `LongTermDebt` equals `LongTermDebtCurrent + LongTermDebtNoncurrent` exactly, every period both are reported (e.g. FY2026: $7.942B = $X + $Y). Summing all three would have doubled the long-term component for most companies.

**Fix:** `LongTermDebt` is mapped alone for the long-term component; the split tags are not mapped at all. Verified `LongTermDebt` is present for every period the split tags are (plus more, since some quarterly filings only report the combined figure) — no coverage lost by dropping the split tags.

### Bug 2: a candidate revenue fallback tag was actually a subcomponent, not an alternative

JPM's `InterestAndFeeIncomeLoansAndLeases` looked like a plausible fourth revenue-tag alternative (alongside the two already-known bank/product-company tags) purely from its name and the fact only JPM uses it. Checked it against JPM's own `Revenues` figure for matching years before adding it: FY2024 shows `InterestAndFeeIncomeLoansAndLeases = $92.4B` against `Revenues = $177.6B` — roughly half, confirming it's loan/lease interest and fee income specifically, a *piece* of total revenue, not an alternative total.

**Fix:** excluded entirely. `InterestAndDividendIncomeOperating` (the other bank tag) was also checked and doesn't exactly equal `Revenues` either in years both are reported (FY2008: $73.0B vs $67.3B) — kept as a `provisional`, last-resort fallback rather than `approved`, with the discrepancy documented. Consequence, confirmed correct rather than patched around: JPM's revenue-dependent metrics are `null` for several fiscal years in the golden set — the honest outcome per doc 11's "null over guess" rule, not a bug to work around.

**Correction (2026-08-16, via doc 12's independent cross-check with `edgartools`):** the reason given above ("no reliable tag exists") was imprecise for at least FY2014. Direct query confirmed the data actually exists in our own pipeline — JPM's FY2014 `Revenues` is reported as $94.205B in the original FY2014 10-K, then revised to $95.112B in the following two 10-Ks' comparatives — but Stage 2e correctly marked all three instances `is_authoritative=false`, since that's a genuine unresolved value conflict (the same silent-revision pattern Normalizer Day 5 already documented for JPM's `DerivativeNotionalAmount`). So the accurate statement is: JPM's revenue is null for that year because Stage 2e correctly flagged a real conflict, not because no tag reports it — a more precise diagnosis, not a different outcome. Worth checking whether the same is true of the other listed gap years before citing this pattern again.

## Coverage report — real, and mostly explainable

170 (company, concept) pairs checked (10 companies × 17 concepts); 57 unresolved. 34 of those are ENB/TSM (2 companies × 17, 0 facts each, correctly excluded per the Normalizer's own scope decision — nothing to resolve). Of the remaining 23 (out of 136 pairs for the 8 fact-bearing companies, ~17%):

- **ARCC** (8 of its 17 unresolved): a BDC, not a product company — no `revenue`, `operating_income`, `gross_profit`, `current_assets`/`current_liabilities` concepts apply the way they do for AAPL/NKE. BDCs report differently (e.g. "Total Investment Income," an unclassified balance sheet) — genuinely needs its own tag survey, not yet done. Flagged for Stage 3a's next pass, not silently worked around.
- **JPM** (`capex`, `current_assets` unresolved): banks don't have a classified current/noncurrent balance sheet or a traditional capex line the way product companies do — same pattern as ARCC, industry-specific, correctly null.
- **GOOGL, RDDT** (`gross_profit` unresolved): neither tags an explicit Gross Profit line — common for tech companies that don't present a COGS-based income statement breakout.
- **Block, RDDT** (`dividends_per_share` unresolved): neither pays a dividend — correctly null, not a mapping gap.
- **Block, RDDT** (`shares_outstanding` unresolved): a real, worth-revisiting gap, not an industry-structural non-applicability like the ones above. Neither reports `CommonStockSharesOutstanding` or `dei:EntityCommonStockSharesOutstanding` as authoritative facts — both use `WeightedAverageNumberOfSharesOutstandingBasic` instead (a period-average EPS-denominator figure, not quite the same concept as a point-in-time share count). Deliberately not mapped as a substitute without more consideration — flagged, not patched.

## Why it matters going forward

Doc 11's own "Real problems" section named taxonomy drift, industry differences, and composite concepts as things to expect — this day confirmed that surveying real co-occurrence data *before* writing the resolver, not just before writing the mapping list, is where the composite-concept bug specifically would have been caught either way, but the JPM subcomponent bug only shows up by actually comparing values side by side. Two different verification techniques (co-occurrence survey, direct value comparison) each caught a different class of mistake — one wasn't a substitute for the other.
