# VERIFY: cell proof, first-10 run v4 (2026-11-04)
Branch work/engineering/cell-proof cbad442, data-team/43-cell-proof/first10-cells.jsonl.gz (v4: 10,548 PROVEN, 124 DISAGREE). Seed 20261104: 12 PROVEN printed-line cells, 8 PROVEN derived quarters, 10 DISAGREE. Verifier 2 (scrooner-bc). 95 SEC requests. Supersedes the v2 draw (VERIFY-CELL-PROOF-FIRST10-2026-11-04) for the error rate.

## Result
- **PROVEN: 0 of 20 wrong values.**
  - **Derived quarters: 8 of 8 tie** to two printed year-to-date lines: META CFO Q2 2025 and buybacks Q4 2023, JNJ tax Q4 2018 (2,702 - 2,622 = 80), HD capex/GP/tax, PG buybacks Q4 FY2015 (4,604 - 4,254 = 350), AAPL dividends Q2 FY2022. The labels differ between filings (PG "Payments for Repurchase of Common Stock" vs "Treasury stock purchases"), and the rule handles that.
  - **Printed-line cells: 11 of 12 printed on the statement.** NVDA gross profit Q4 FY2019 (1,207) is printed only in the 10-K "Quarterly Summary" note (0001045810-19-000023). It also ties as 7,171 - 5,964. The v2 off-face issue is smaller now, but it is still present.
- **DISAGREE: 4 of 10 real, 6 false.**
  - Real: MSFT total assets 2016-06-30 and HD current liabilities 2016-01-31 (original 10-K values, cited to the restating accession, see the v2 verdict).
  - Real: **AAPL dividends paid Q3 FY2017, shown 3,281, and Q4 FY2017, shown 3,252.** These are wrong shown values. The cash flow year-to-date lines give 9,499 - 6,134 = 3,365 (0000320193-17-000009, 0001628280-17-004790) and 12,769 - 9,499 = 3,270 (0000320193-17-000070).
  - False: AMZN CFO Q1 2017 (-1,619), Q2 2017 (3,850) and FY2018 (30,723), plus AMZN investing Q2 2017 (-5,274). Each is printed as the "Net cash provided by (used in)" line on the statement.
  - False: PG operating income FY2015 (11,049, printed).
  - False: PG operating income Q4 FY2020 (3,481 = 15,706 - 12,225).
  - `only_a_component_line_presented` fired falsely 6 of 6 times.

## Findings for the builder
1. AAPL dividends Q3/Q4 FY2017: production values match neither the printed lines nor the year-to-date subtraction. Trace their source facts, and check every AAPL quarterly dividends_paid cell for 2015-2019.
2. `only_a_component_line_presented` misses statement totals ("Net cash provided by (used in) operating activities", "Operating Income"). It should treat a line as a total when the line is the calc parent, not when another candidate contains it. Re-verify on these 6 cells.
3. Printed-line PROVEN still accepts note-only quarter values when the 10-K statement has only annual columns. Require the statement column, or prove the cell through the derived-quarter rule instead.

## Untested scope
UNCHECKED (528) and NOT_PRESENTED (943) were not drawn.
