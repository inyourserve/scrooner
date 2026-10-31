# Verify: capex release 2 fills v17 (origin/work/cash-flow/da-capex 8201835, release2_fills_cells.jsonl, 1,781 inserts), 2026-11-03

Seed 20261103, 14 fills, plus the CVNA related-party cell (in release 1; no CVNA cell is among the fills). Evidence class: FILING-CHECKED (cash-flow R page). Verifier 2 (scrooner-bc).

## Result
**NO (one label class).** 11 of 12 readable fills right; GSAT x2 not readable (line or column). Wrong: BXP Q1 2023 takes "Building and other capital improvements" (39,100K) but omits "Construction in progress" (119,682K), BXP's development spend on PP&E. REIT development or construction lines are capex like INSW's vessels; the right value is 158,782K.
- CVNA FY2019 (release 1): "Purchases of property and equipment, including $6,282 in 2019 from related parties" 230,538K is right; purchases from a related party are still capex.
- Note: RRC FY2022 excludes "Acreage purchases" (30,885K) instead of holding. Under the v16 rule, oil and gas acquisition lines hold the cell (FANG). Make the two consistent.

| Ticker | Period | Face | Value | Verdict |
|---|---|---|---|---|
| MTB | 9M 2022 | Capital expenditures, net (126,810) | 126,810K | right |
| ETR | 6M 2024 | Construction/capital expenditures (2,124,279), Entergy block | same | right |
| ES | FY2021 | Investments in PP&E (3,175,080) | same | right |
| ES | Q1 2022 | (764,594) | same | right |
| SNA | FY2023 | Capital expenditures (95.0) | 95M | right |
| GSAT | Q1 2024 | network upgrades line not matched on the page | 1,901K | not graded |
| GSAT | FY2021 | column not parsed | 6,307K | not graded |
| TPG | Q1 2025 | Purchases of fixed assets (6,347) | same | right |
| ETR | Q1 2019 | (951,629) | same | right |
| CHDN | 6M 2024 | maintenance (34.8) + project (257.2) | 292.0M | right |
| BXP | Q1 2023 | Construction in progress (119,682); Building and other capital improvements (39,100) | 39,100K | **wrong: 158,782K** |
| RRC | FY2022 | oil and gas properties (456,505,000) + field service (682,000); acreage purchases excluded | 457,187K | right (see note) |
| INSW | FY2019 | vessels (36,607) + other property (574) | 37,181K | right |
| CVNA (release 1) | FY2019 | purchases of P&E incl. from related parties (230,538) | 230,538K | right |

SEC requests: 30.
