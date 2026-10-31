# Verify: capex release 1, single-member cut (origin/work/cash-flow/da-capex 3042c8f, capex_release1_cells.jsonl, 1,475 cells, sha256 d2a31e45... confirmed), 2026-11-04

Seed 20261104, 15 cells. File check: 0 cells with more than one member. Evidence class: FILING-CHECKED (each cell's whole investing section on the cash-flow R page). Verifier 2 (scrooner-bc).

## Result
**YES.** In 14 of 14 readable cells, the value equals the single printed capex line, and it is the only PP&E/capex outflow in the investing section. The other lines are acquisitions, securities, investments, insurance or proceeds, all rightly left out. HWM FY2019: investing section not parsed (kit), not graded.

| Ticker | Period | Capex line (value) | Other investing lines present (excluded) |
|---|---|---|---|
| AXSM | 9M 2022 | Purchases of equipment (521,251) | business combination |
| RGEN | 6M 2015 | Purchases of PP&E (1,736,695) | marketable securities |
| ALB | 6M 2024 | Capital expenditures (1,026,936K) | acquisitions, securities, equity investments |
| WAT | 6M 2025 | Additions to PP&E and software capitalization (48,336K) | acquisitions, investments |
| QXO | 6M 2025 | Capital expenditures (19.7M) | acquisition |
| IQV | 9M 2016 | Acquisition of property, equipment and software (78,076K) | trading securities, COLI, affiliates |
| BDX | 9M FY2021 | Capital expenditures (766M) | acquisitions, other |
| OSK | FY2024 | Additions to PP&E (281.0M) | acquisitions, sale of businesses |
| LAD | Q1 2018 | Capital expenditures (42,004K) | acquisitions, other investments, asset sales |
| HWM | FY2019 | Capital expenditures (586M) | section not parsed |
| AXTA | Q1 2023 | Purchase of PP&E (41.4M) | swap settlements |
| WDAY | 9M FY2016 | Purchases of P&E (96,252K) | securities, business combinations, cost-method investments |
| FAF | Q1 2022 | Capital expenditures (43M) | securities, secured financings |
| CWEN | 9M 2015 | Capital expenditures (16M) | drop-down acquisitions, affiliates |
| CHWY | FY2023 | Capital expenditures (143,282K) | acquisition, securities |

SEC requests: 30.
