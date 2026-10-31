# Verify: buybacks run 3 (origin/work/cashflow/cfo-buybacks 587b581, results/cf_run3), 2026-11-01

Seed 20261101. Files: buybacks_prod_differs.json (184), buybacks_prod_blank.json (630), buybacks_cells.jsonl.gz. Evidence class: FILING-CHECKED (cash-flow R page of each claimed accession). Verifier 2 (scrooner-bc).

## Result
**Buybacks: YES.** 15 of 15 differences right (slot = printed repurchase line); 5 of 5 blanks right in value.
- Run-2 misses all held now:
  - ROST 9M 2020, 9M 2015 and FY2019: perimeter_multiple_repurchase_lines.
  - LDOS FY2020: buyback_combined_with_other_items.
  - AAON Q1 2025: sign_unclear.
  - FIS Q1 2015: perimeter_line_unresolved.
- AXS no longer appears in the blank list.
- DPZ 24 weeks to 2015-06-14 is still listed blank, but production holds 97.634M at 2015-06-14, the same value. The label end (2015-05-31) is 14 days from the period end, so a +-10-day window misses it. Match on the period, not a date window.
- Definition question: CCL FY2022 counts "Purchase of treasury stock under the Stock Swap Program" (87M) as a buyback. Production 0. Carnival's swap pairs plc share sales with Corp share purchases; perimeter call.

## Cell table
| Stratum | Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|---|
| diff | BLDR | 6M 2023 | (1,414,489); accrued +12,762 excluded | 1,414,489K | 1,381,988K | right |
| diff | CCI | Q1 2018 | (33) | 33M | -33M | right |
| diff | NRG | FY2022 | (606) | 606M | 600M | right |
| diff | AUR | FY2021 | 0 | 0 | 754.59M | right |
| diff | ZETA | FY2024 | (42,185) | 42,185K | 41,080K | right |
| diff | AMD | 6M 2025 | (1,227); withholding (76) excluded | 1,227M | 1,200M | right |
| diff | AMD | 9M 2025 | (1,316) | 1,316M | 1,300M | right |
| diff | UI | Q1 FY2016 | (53,818) | 53,818K | 63.3M | right |
| diff | DHI | Q1 FY2025 | (1,055.7); mortgage facility and withholding excluded | 1,055.7M | 1,100M | right |
| diff | EOG | Q1 2020 | (4,655) | 4,655K | 5M | right |
| diff | IR | 6M 2025 | (510.2) | 510.2M | 510.7M | right |
| diff | CCL | FY2022 | purchases 0; Stock Swap Program (87) | 87M | 0 | definition question |
| diff | CMCSA | FY2016 | (5,000); debt repurchases excluded | 5,000M | 5,352M | right |
| diff | OTEX | Q1 FY2024 | (53,085) | 53,085K | 0 | right |
| diff | SCCO | 9M 2015 | (724,352) | 724,352K | 724.4M | right |
| blank | DPZ | 24 wks to 2015-06-14 | (97,634) | 97,634K | production has 97.634M (14 days off) | value right; not a blank |
| blank | SHW | FY2021 | (2,752.3); proceeds +11.7 excluded | 2,752.3M | blank | right |
| blank | BAM | Q2 2025 | 0 | 0 | blank | right |
| blank | BPOP | 6M 2025 | net payments (236,203) | 236,203K | blank | right |
| blank | AAON | 6M 2015 | (6,444) | 6,444K | blank | right |

## Requests and disk
SEC requests: 40. DB: one connection for 5 blank rechecks.
