# Verify: D&A release 1 (slot.d_and_a@1; origin/work/cash-flow/da-capex b6d0ca4, results/release_da_1), 2026-11-02

Seed 20261102. Files: da_release1_cells.jsonl (586: 159 is_anchor, 386 single_line_clean, 41 single_line_ties_is) and da_release1_class_fills.jsonl (4,117). Evidence class: FILING-CHECKED (cash-flow and income-statement R pages). Verifier 2 (scrooner-bc).

## Result
- **Release 1: YES.** 15 of 15 right (5 per class).
- **Class fills: YES.** 10 of 10 right (3 anchor, 4 clean, 3 ties).

## Cell table
| Set | Class | Ticker | Period | Face | Value | Prod | Verdict |
|---|---|---|---|---|---|---|---|
| release | is_anchor | DUK | FY2025 | IS D&A 6,324 (CF DA&A incl. nuclear fuel 7,704) | 6,324M | 7,704M | right |
| release | is_anchor | PNW | FY2016 | IS D&A 485,829 | 485,829K | 565,011K | right |
| release | is_anchor | VNO | 6M 2025 | IS D&A (231,729); CF line includes financing-cost amortization | 231,729K | 241,538K | right |
| release | is_anchor | PNW | FY2022 | IS 753,195 | same | 817,814K | right |
| release | is_anchor | PNW | 9M 2020 | IS 459,257 | same | 515,742K | right |
| release | clean | SGI | 9M 2019 | D&A 66.7 (SBC and financing amortization excluded) | 66.7M | 86.7M | right |
| release | clean | STZ | FY2026 | Depreciation 418.7 | same | 420M | right |
| release | clean | ALLE | FY2022 | D&A 97.9 | same | 95.1M | right |
| release | clean | VLO | 9M 2017 | CF 1,496 (IS 1,457 + 39) | 1,496M | 39M | right |
| release | clean | SGI | 6M 2017 | D&A 39.7 | same | 42.3M | right |
| release | ties | CZR | 6M 2020 | CF = IS 99,372 | same | 99M | right |
| release | ties | RKT | FY2024 | CF = IS 112,917 | same | 89M | right |
| release | ties | HLT | 6M 2017 | CF (incl. discontinued) 176 = IS 176 | same | 169M | right |
| release | ties | ODFL | Q1 2026 | CF 92,308; IS 92,307 | 92,308K | 92,307K | right (1K rounding) |
| release | ties | RKT | FY2023 | CF = IS 110,271 | same | 88M | right |
| fill | is_anchor | XEL | 9M 2025 | IS D&A 2,200 (CF 2,216 + nuclear fuel 87) | 2,200M | blank | right |
| fill | is_anchor | EXC | 6M 2026 | IS 1,920 | same | blank | right |
| fill | is_anchor | AEE | FY2024 | IS 1,590 (Ameren block) | same | blank | right |
| fill | clean | VRSN | FY2021 | Depreciation of P&E 47,940 | same | blank | right |
| fill | clean | BK | 6M 2016 | CF D&A 748 | same | blank | right |
| fill | clean | EBAY | Q1 2019 | CF D&A 169 | same | blank | right |
| fill | clean | TT | 6M 2024 | CF 187.7 | same | blank | right |
| fill | ties | SRE | 9M 2016 | CF = IS 970 (Sempra block) | same | blank | right |
| fill | ties | SWX | 6M 2025 | CF = IS 231,076 | same | blank | right |
| fill | ties | FCFS | 9M 2016 | CF = IS 17,165 (market-lease line excluded) | same | blank | right |

## Findings for the builder
None blocking. ODFL shows the CF value when CF and IS differ by one unit; either is defensible at the printed precision.

## Requests and disk
SEC requests: 75. No DB access.
