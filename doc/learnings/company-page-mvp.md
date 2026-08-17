# Company Page MVP — Statement Classification + /stock/[ticker]

## A real gap found by comparing my own build against my own reference doc

Doc 17's own analysis (extracted from Screener.in's real HTML, not assumed) documented that Quarterly Results and the annual Profit & Loss/Balance Sheet/Cash Flow are separate sections on the real page. Building the statement table, that distinction got lost — a single merged table, sorted by `period_end`, was implemented first. The bug this caused: a company's FY period and its Q4 period share the same `end_date` (Q4 is the fiscal year's own last quarter), so sorting by date alone put "FY 2025" between "Q3 2025" and "Q4 2025" with no stable, sensible order. Caught by reading the actual rendered page text, not by reasoning about the SQL. Fixed by splitting `getStatement()` on `fiscal_period = 'FY'` vs. `in ('Q1','Q2','Q3','Q4')`, matching the two-section structure doc 17 had already documented from the real reference — the fix was really "build what the reference doc already said," not a new design decision.

## Reusing Mapper's frozen resolution logic instead of writing new logic that could drift

The statement classification work (new canonical concepts for `cost_of_revenue`, `total_assets`, etc.) writes to the exact same `analytics.canonical_concept`/`concept_mapping` tables Mapper's frozen `mapper/concepts.py` already owns, using the identical upsert SQL pattern — but as new, separate code, not a modification to the frozen module. Verified directly, not assumed: after seeding and rerunning `resolve-facts`, the original 17 concepts' `canonical_fact` row count was checked and confirmed unchanged (7,904, exactly what it was before this session's work) — proof the extension was purely additive, not a silent regression of already-verified Mapper output.

## A second taxonomy-drift confirmation, this time for a statement-only tag

`CostOfGoodsAndServicesSold` and `CostOfRevenue` both appear for the same companies across different years — checked directly whether they're alternates or summands before mapping either, the same question Mapper's Day 1 already had to answer for `revenue`. MSFT's 2016/2017 filings report *identical* values under both tags in the same years, confirming alternates (a taxonomy transition), not summands. Treated with the same `first_match`, priority-ordered mapping Mapper already uses for exactly this pattern — no new mapping philosophy needed, the existing one generalized correctly to a new tag.

## Verification summary

- Statement math cross-checked, not just eyeballed: AAPL's Total Liabilities + Stockholders' Equity = Total Assets exactly (275,746 + 107,520 = 383,266) for the same real quarter.
- Income statement FY2025 revenue ($416.16B) and net income ($112.01B) match the exact same figures independently verified via `edgartools` earlier in this session (Mapper Day 6/doc 11b) — three independent checks (Scrooner's own pipeline, `edgartools`, and now this rendered page) now agree to the same real numbers.
- Real edge cases from the existing golden-10 exercised, not just the easy case: Block's ticker-change history respected exactly (`/stock/xyz` resolves, `/stock/sq` correctly 404s, matching Company Master 4a's `effective_to` logic); NKE's known missing `OperatingIncomeLoss` (a real, already-documented Mapper Day 3 finding) renders as an honest null on the page, not a fabricated or hidden value.
- A nonexistent ticker correctly 404s.

## Why it matters going forward

The FY/Q4 same-end-date collision will recur for every non-calendar-fiscal-year company (already known to include AAPL, MSFT, NKE in the golden set) anywhere a future feature naively sorts periods by date alone without also partitioning by granularity (FY vs. quarterly). Worth remembering as a standing rule for any new period-ordered view, not just this one page.
