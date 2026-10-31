# Verify: capex release 2 fills v16 (origin/work/cash-flow/da-capex 31fa9f6, release2_fills_cells.jsonl, 1,865 inserts), 2026-11-02

INSW Q1 2023 plus 14 seeded (20261102). Evidence class: FILING-CHECKED (cash-flow R page). Verifier 2 (scrooner-bc).

## Result
**NO (one label class).** 12 of 15 right; INSW fixed. PSX x2 publish "Capital expenditures and investments", which is capex combined with investments. Hold it like JEF's "and other assets" (v16 rule). GLW's "Purchase of equipment for related party" is a small perimeter question.

| CIK | Period | Face | Value | Verdict |
|---|---|---|---|---|
| INSW 1679049 | Q1 2023 | vessels (66,722) + other property (524) | 67,246K | right |
| INGR 1046257 | 6M 2017 | Capital expenditures, net of proceeds on disposals (144) | 144M | right (net as printed) |
| GLW 24741 | 9M 2018 | Capital expenditures (1,629) + Purchase of equipment for related party (63) | 1,692M | perimeter question (related-party equipment) |
| CMS 811156 | 6M 2022 | (1,088) | 1,088M | right |
| FNF 1331875 | 9M 2025 | PP&E, capitalized software and title plants (113) | 113M | right (combined PP&E line) |
| GSAT 1366868 | FY2024 | network upgrades (6,823); intangibles excluded | 6,823K | right |
| ES 72741 | FY2019 | Investments in PP&E (2,911,489), Eversource block | same | right |
| LLY 59478 | Q1 2024 | (986.3) | same | right |
| EIX 827052 | 6M 2018 | (2,159), Edison block | same | right |
| ADP 8670 | FY2026 | Capital expenditures (196.6); intangibles excluded | 196.6M | right |
| PSX 1534701 | 6M 2021 | "Capital expenditures and investments" (711) | 711M | **leak: combined with investments** |
| LYFT 1759509 | FY2023 | P&E and scooter fleet (149,819) | same | right |
| IBKR 1381197 | Q1 2017 | (6) | 6M | right |
| SO 92122 | 6M 2016 | Property additions (3,486,000,000), Southern block | same | right |
| PSX 1534701 | Q1 2025 | "Capital expenditures and investments" (423) | 423M | **leak (same)** |

## Findings for the builder
1. Extend the "and other assets" hold to "Capital expenditures and investments" and similar "... and investments" labels (PSX). Phillips 66's line includes equity-affiliate investments.
2. Perimeter list: "Purchase of equipment for related party" (GLW).

SEC requests: 30.
