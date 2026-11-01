# VERIFY: capex release 2a (2026-11-04)
Branch work/cash-flow/da-capex c1ed0c8, results/release_capex_2a (3,203 cells, 130 companies, sha256 7d88867e). Seed 20261104: 3 cells per class across 6 classes. Ruling checked against: decision register 2026-11-04 item 3. Verifier 2 (scrooner-bc). 42 SEC requests.

## Result: YES, 18 of 18 right
Every value equals the sum of its member lines, and every member is a printed investing line in the cited filing's own period column.

| Class | Cells | Verdict |
|---|---|---|
| leased | DE Q1 FY2026 256 + 432 "Cost of equipment on operating leases acquired"; FTAI 9M 2024 2,968 + 622,366 "Acquisition of leasing equipment"; OSK 6M FY2019 50.6 + 12.2 "equipment held for rental" | YES 3/3 |
| software | SNPS Q1 FY2021 27,779 + 1,011; VRT FY2020 44.4 + 8.3; APPF 9M 2021 5,166 + 18,511 | YES 3/3 |
| discontinued | EQT FY2018 2,964,924 + 732,727; ESE 6M FY2020 21,211 + 4,280 software + 1,728 (printed below the continuing subtotal); AMD FY2025 974 + 38 | YES 3/3 |
| turnaround | PBF 6M 2017 220,446 + 214,375; VLO Q1 2018 356 + 220 + 28 VIE capex; VLO 9M 2015 1,186 + 509 | YES 3/3 |
| ti_cip | BXP Q1 2021 CIP 119,496 + improvements 32,717 + TI 93,201; BXP 6M 2023 235,331 + 78,344 + 135,743; TRNO Q1 2021 140 + 7,867 | YES 3/3 |
| acquisition_exclusion | SM 9M 2020 419,777 (excludes 7,075 property acquisitions); MTDR 9M 2023 855,468 + 75,609 + 2,964 = 934,041 (excludes 120,586 property acquisitions; production's 2,619,772 includes the 1,608,427 Advance business acquisition); EXE Q1 2020 501 + 11 (excludes 6) | YES 3/3 |

## Notes for the builder (no change needed to pass)
- AMD's 38 is tagged `PaymentsForProceedsFromProductiveAssets`, a NET tag (payments less proceeds). It sits inside the discontinued-operations investing block. Keep it, but record that it is net.
- VLO "Acquisition of undivided interests" (85) is excluded under "an acquisition is not capex". That goes beyond the ruling's oil-and-gas wording, so confirm it with Dhairya if challenged.
- TRNO's line combines buildings, improvements and leasing costs. It cannot be split on the face, and including it is in line with the TI ruling.
- FTAI "Deposits for acquisitions of aircraft and engines" (162,708) is left out. That is right because deposits are not yet assets, but re-check if the leased class gets wider.

## Untested scope
447 `prod_blank` cells were not drawn separately (the BXP/TRNO/SM picks are among them).
