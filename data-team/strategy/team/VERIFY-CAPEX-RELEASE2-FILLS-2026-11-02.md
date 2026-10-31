# Verify: capex release 2 fills, v13 rules (origin/work/cash-flow/da-capex, release_capex_1/capex_release2_fills.jsonl, 2,228 cells, unchanged since 74e14f7), 2026-11-02

Seed 20261102, 15 cells. Evidence class: FILING-CHECKED (cash-flow R page). Verifier 2 (scrooner-bc).

## Result
**NO (1 wrong, 2 to decide).** 10 of 13 readable right; IBKR and KTOS pages not parsed.
- Wrong: INSW Q1 2023 takes only "Expenditures for other property" (524K). The face also prints "Expenditures for vessels, vessel improvements and vessels under construction" (66,722K), which is the main PP&E line, so capex = 67,246K.
- Leak: JEF 9M 2021 "Acquisitions of property, equipment and leasehold improvements, and other assets" (115,998K). The "and other assets" label is the combined-with-other class; hold it, as on the buyback side.
- Definition: FANG 9M 2023 adds "Property acquisitions" (1,193M) to drilling/completions (1,948M) and midstream (104M). Asset acquisitions of oil and gas properties versus capex is a perimeter call.
- Note: ETR 6M 2015 excludes "Nuclear fuel purchases" (165,704K), while D Q1 2025's line includes nuclear fuel by its own label. Utilities differ by presentation; consistent as printed.

## Cell table
| Ticker | Period | Face | Value | Verdict |
|---|---|---|---|---|
| ETR | 6M 2015 | Construction/capital expenditures (1,095,926), Entergy block | 1,095,926K | right |
| IBKR | Q1 2025 | page not parsed | 16M | not graded |
| D | Q1 2025 | Plant construction and other property additions incl. nuclear fuel (3,213), Dominion block | 3,213M | right |
| JEF | 9M 2021 | "... leasehold improvements, and other assets" (115,998) | 115,998K | leak: hold |
| KNX | FY2020 | Purchases of P&E (521,067) | same | right |
| MTB | 9M 2020 | Capital expenditures, net (125,370) | same | right |
| CMS | FY2021 | Capital expenditures excl. finance lease (2,076) | 2,076M | right |
| CHRD | 9M 2017 | Capital expenditures (443,649) | same | right |
| NE | Q1 2024 | Capital expenditures (166,610) | same | right |
| INSW | Q1 2023 | vessels (66,722) + other property (524) | 524K | **wrong: 67,246K** |
| CFG | FY2024 | Capital expenditures, net (122) | 122M | right |
| NEE | 6M 2024 | FPL (4,260) + other (106) | 4,366M | right |
| CHRD | FY2019 | (869,221) | same | right |
| FANG | 9M 2023 | D&C (1,948) + midstream (104) + property acquisitions (1,193) | 3,245M | definition question |
| KTOS | FY2019 | page not parsed | 26.3M | not graded |

## Findings for the builder
1. Lines "Expenditures for vessels / vessel improvements / vessels under construction" are PP&E capex (shipping), like aircraft or rigs.
2. Capex members labelled "... and other assets" go to the combined hold.
3. Founder call: oil and gas "Property acquisitions" in capex or not.

SEC requests: 30.
