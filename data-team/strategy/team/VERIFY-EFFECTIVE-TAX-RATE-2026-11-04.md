# Verify: effective tax rate, Family A retirement (origin/work/per-share/effective-tax-rate bb5604d), 2026-11-04

Seed 20261104. Revised brief: no computed rates are written; the computable cells become removals. Draw: 15 computable-list removals, the 2 review cells with |rate| > 1, 5 other removals across reasons, all 7 replacements. Evidence class: FILING-CHECKED (income statement and Income Taxes (Details) R pages). Verifier 2 (scrooner-bc).

## Result
**YES.**
- **Computable-list removals:** 15 of 15. The filing prints tax and pretax, but no effective-tax-rate line on the income statement, and the stored values were derived and wrong:
  - INTC Q3 2015: stored 0.043; printed 1,144 / 4,253 = 26.9%;
  - COST Q1 FY2020: stored -0.007; 134 / 1,249 = 10.7%;
  - 1066 Q4 2015: stored -0.729; benefit 41,249 on 113,699 = -36.3%;
  - 4689 Q2 2025: stored 0.132; 101 / 199 = 50.8%.
  - Not showing a derived rate removes wrong values.
- **The 2 review cells (|rate| > 1):** CRM Q3 FY2016 (tax 68,548 / pretax 43,391 = 158%) and 1069183 Q2 2023 are removed with the rest; nothing derived is shown.
- **Other removals:** 5 of 5 right. They are derived Q4 or quarter rates with no filed rate for the period:
  - LLY Q4 2024, HWM Q4 2022, MCD Q4 2021, 4077 Q4 2016 (stored -3.46);
  - FANG Q3 2016 (stored -0.004; the face prints a 600K pretax loss and 0 tax).
- **Replacements:** 7 of 7 equal the filed rate. Mettler-Toledo (1037646) "Income Taxes (Details)" prints "Effective Income Tax Rate Reconciliation, Percent" for the 3-month column:

| Quarter | Filed (10-Q) | Replacement | Stored (removed) |
|---|---|---|---|
| Q2 2018 | 22.40% | 0.224 | -0.004 |
| Q3 2020 | 21.40% | 0.214 | 0.015 |
| Q3 2021 | 17.70% | 0.177 | -0.007 |
| Q3 2022 | 20.00% | 0.200 | 0.008 |
| Q3 2023 | 19.70% | 0.197 | 0.006 |
| Q3 2024 | 18.30% | 0.183 | 0.016 |
| Q3 2025 | 19.20% | 0.192 | 0.001 |

## Note
Some filers print the rate only in the tax note (as MTD does). The computable-list check covered the income statement; a filed note rate would show up as an XBRL fact and a replacement, not a removal.

SEC requests: 72.
