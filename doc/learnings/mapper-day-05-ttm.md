# Mapper Day 5 — TTM and Growth Windows

## Verified the reconstruction approach before building on it

Before implementing trailing-4-quarter TTM aggregation, checked whether it would even reproduce a known-correct number: summed AAPL's four quarterly `operating_income` facts for FY2024 (Q1 $40.373B + Q2 $27.900B + Q3 $25.352B + Q4 $29.591B) and got exactly `$123,216,000,000` — AAPL's actual reported FY2024 operating income, to the dollar. This is also a real cross-check on Normalizer Stage 2g's Q4 derivation, Stage 3b's resolution, and Stage 2b's fiscal_year/fiscal_period labeling all still being mutually consistent three phases later.

## Growth metrics: straightforward, verified exactly

`revenue_growth_yoy`/`3y_cagr` and `eps_growth_yoy`/`3y_cagr` compare same-fiscal_period values across fiscal years (Q1 vs year-ago Q1, FY vs year-ago FY), never mismatched periods — this is what keeps seasonality from distorting the comparison, unlike Day 3's naive-annualization problem. AAPL FY2024: revenue YoY growth computed as 2.0220%, matching `391,035/383,285 - 1` by hand exactly; 3Y CAGR computed as 2.2470%, matching `(391,035/365,817)^(1/3) - 1` exactly.

## The strongest verification of the whole Mapper phase: two independent code paths agree to full precision

Doc 11's Day 5 gate calls for TTM figures matching manual 4-quarter sums — went further and checked whether TTM-at-a-Q4-boundary (Stage 3e's trailing-quarter code) equals the FY figure Stage 3d computed independently, since mathematically they must be identical (Q4's trailing 4 quarters *are* Q1+Q2+Q3+Q4, the same quarters that make up the fiscal year). AAPL FY2021 ROIC: Stage 3d's direct FY calculation and Stage 3e's TTM calculation both produced `0.6432163420699880117275573775` — identical to the last digit, from two separately-written code paths that never call each other. This is about as strong a confirmation as this project's methodology can produce without an external data source.

## No new bugs found this day — first time that's happened

Every prior Normalizer and Mapper day (9 of 9 so far) found at least one real bug via verification. Day 5 didn't, and that itself is worth being honest about rather than either pretending zero bugs is unremarkable or manufacturing a finding to keep the pattern going: it's the direct payoff of Day 4's completeness-check fix and Day 3's FY-only restriction — building Stage 3e strictly on top of already-hardened Stage 3d logic (the trailing-quarter lookups reuse the same `canonical_fact` data and the same "require every expected input, not just any" discipline) meant the design mistakes that would have shown up here were already caught one stage earlier.

## Verification summary

- 1,369 growth values computed (433 null — mostly `missing:prior_period` for early years with no 1yr/3yr-ago comparable, and gross-margin-style industry gaps carrying through), 440 TTM ROIC/ROE values computed (358 null, same underlying causes as Stage 3d's FY-only nulls: NKE's missing `operating_income`, JPM's bank-structure gaps).
- Reran both jobs — identical stats on rerun (1,369/433 and 440/358), confirming idempotency.
- `analytics.metric_value`: 6,058 total rows, 57 MB total DB — comfortably within the free-tier budget.

## Why it matters going forward

The Q4-boundary TTM-vs-FY cross-check is a reusable verification pattern worth remembering for Stage 3f (or any future metric work): whenever a new derived-window calculation should mathematically reduce to an already-verified value at a boundary condition, checking that boundary is stronger evidence than checking the general case alone, because it tests two independently-written implementations against each other rather than checking one implementation's output against a manually-recalled figure.
