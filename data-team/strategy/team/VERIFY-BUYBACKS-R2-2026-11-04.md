# VERIFY: buybacks release 1 re-cut under the founder perimeter ruling (2026-11-04)
Branch work/cashflow/buybacks-r2 b89398e, release_buybacks_1 (473 cells, sha256 d51bdb22) and its source run results/cf_run6. Seed 20261104: EMR FY2024 forced, 3 publishable cells with an excluded member beside the buyback line (from 620), 2 `excluded_only` cells (from 670). Verifier 2 (scrooner-bc). 14 SEC requests.

## Result: YES, 6 of 6 right
| Cell | Published | Face (financing section) |
|---|---|---|
| EMR FY2024 (0000032604-24-000041) | 435M | "Purchases of common stock" (435). "AspenTech purchases of common stock" (208) is a subsidiary's buyback, excluded |
| GPN FY2022 (0001123360-23-000009) | 2,921,307K | "Repurchases of common stock" (2,921,307). "Share-based compensation plans" (38,601) excluded; NCI distributions are not buybacks |
| GRMN 6M 2018 (0001615774-18-007281) | 0 | "Purchase of treasury stock under share repurchase plan" printed 0. "Related to equity awards" (6,900) excluded |
| 790051 Q1 2017 (0001628280-17-004465) | 0 | "Repurchases of common stock" printed 0.0. "Proceeds from exercise of stock options, net" (5.4) excluded |
| 1581280 FY2021 excluded_only (0001104659-21-142700) | none | the only line is "Repurchases of common stock for income tax withholding" (10,849) |
| COIN Q1 2020 excluded_only (0001679788-21-000010) | none | the only line is "Issuance of common stock upon exercise of stock options, net of repurchases" (+432) |

## Notes
- The two published zeros are printed zeros, so they are values, not blanks.
- Kit: GPN's header "$ in Thousands, € in Millions" with "USD ($)" sub-columns breaks parse_rpage's column read, so I read it by hand.
