# Verify: total-liabilities dry-run, slot vs production (origin/work/scrooner-25/slot-records 8fdb9ca), 2026-10-26

Verifier 2. Seed random.Random(20261118).
- **Files:** results/bs_dryrun_total_liabilities_summary.json and _cells.jsonl. The cells file holds only the 3,769 slot_differs and 230 slot_holds cells. I rebuilt agree and fill cells read-only from the builder's replay reports (census, facesum_rest, v19, batch6) plus production: 941 companies, 31,982 agree, 50 fills (claimed 952 / 32,236 / 88), so the agree and fill draws come from that reconstruction.
- **Claimed:** agree 32,236; differs 3,769 (256 printed_total, 3,513 face_sum); fills 88; would-hide 230.
- **Method:** each cell's balance sheet from its own accession, read with the kit on main (`fetch_statements` + `face_liabilities`): 380 requests. 14 cells where the kit failed or disagreed were re-read by hand. Nothing kept on disk. Read-only DB on one connection with a 20s timeout. FILING-CHECKED.

## Result: GATE PASSES. 0 wrong slot values in 175 slot values checked (140 differs + 20 fills + 15 agree).
- **Production is wrong in 140 of 140 sampled differences.**
- **Would-hide:** 15 sampled; production right in 6, wrong in 9.

## Cell table by stratum (production vs face; slot vs face)
| Stratum (population) | Sampled | Slot right | Production wrong | 95% lower bound on production-wrong rate |
|---|---|---|---|---|
| printed_total differs (256) | 60 | 60 | 60 | 95.1% |
| face_sum A, <=1% (192) | 6 | 6 | 6 | 60.7% |
| face_sum A, 1-10% (251) | 6 | 6 (2 by hand: MCK) | 6 | 60.7% |
| face_sum A, >10% (145) | 6 | 6 (TRGP by hand) | 6 | 60.7% |
| face_sum B, <=1% (1,335) | 18 | 18 (SYY, LYB by hand) | 18 | 84.7% |
| face_sum B, 1-10% (973) | 17 | 17 (OMC x2, 0000098362, LEA by hand) | 17 | 83.8% |
| face_sum B, >10% (394) | 9 | 9 | 9 | 71.7% |
| face_sum no reading, <=1% / 1-10% / >10% (65 / 125 / 33) | 18 | 18 (EMR by hand) | 18 | 84.7% (pooled) |
| **all differences (3,769)** | **140** | **140** | **140** | **97.9%**, i.e. at least about 3,690 of the 3,769 production values are wrong |
| fills (88) | 20 | 20 (OMC 2026-06-30 by hand) | n/a | - |
| agree, control (32,236) | 15 | 15 | 0 | - |

Notes:
- The lower bounds are exact one-sided 95% binomial bounds with 0 exceptions (1 - 0.05^(1/n)). Small strata are wide only because they are small; no stratum showed a right production value.
- 14 of the 140 production errors are under 0.1%. They are wrong but small: e.g. SYY 20,682,155K vs face 20,613,213K.

## Largest production errors in the sample
- CIK 0002041610 2025-06-30: production **-17,111M**; the face is an empty pre-spin shell, total L&E $0 (0002041610-25-000013 R4). Slot 0 is right.
- CIK 0001780312 2020-06-30: 25.9M vs printed Total Liabilities 8,256,307 (0001213900-20-021916).
- CIK 0001324404 2024-12-31: 11,088M vs 5,874M = 13,466 - 7,592 (0001324404-25-000006).
- EMR 2022-09-30: 31,260M vs 19,356M = 35,672 - 16,316 (0000032604-22-000041).
- CIK 0001090012 2015-09-30: 27,177M vs 18,429M (0001193125-15-365650).
- TRGP 2018-06-30: 10,411.9M vs 8,115.3M = CL 1,953.3 + LTD 5,392.5 + 35.5 + 519.2 + 214.8 (0001564590-18-020681). Production includes the Series A preferred and NCI.
- Printed totals: CIK 0000354190 2017 10,610M vs 8,732.5M; CIK 0001973266 2024 4,969M vs 3,981M; CIK 0001618732 2017 521M vs 678M (production too LOW).

## Would-hide cells (15 of 230): decide hide vs keep
**Production RIGHT (6), hiding them loses a right value:**
- WEC 2020-09-30 24,862.9M = CL 2,840.0 + LTL 22,022.9; WEC 2021-12-31 27,875.2M (0000107815-20-000277, -22-000116). The capitalization layout prints no total-equity line.
- CIK 0001116942 2018-10-01, CIK 0000889331 2016-07-02, FDX 2026-02-28 (64,929M), CIK 0001646972 2020-06-20.

**Production WRONG (9), hiding is right:**
- CIK 0000764622 2021-12-31: 16,212M vs 15,981,762K (subtotals).
- CIK 0001130464 x6, e.g. 2019-12-31: 5,196,334K vs 5,094,388K. Production adds NCI 101,946K.
- KMB 2016-06-30: 14,802M vs 14,282M plus redeemable preferred 64; KMB 2021-09-30 also wrong.

**Recommendation:** hide the would-hide set except where the face gives the value (the WEC-style capitalization subtotals and the 4 others). Better, teach the reader those layouts so the 6 show the filed value.

## Findings for the kit owner (14 hand reads)
- Mezzanine not subtracted when the L&E label names it ("Total Liabilities, Redeemable Noncontrolling Interests and Equity": MCK; "Temporary Equity - Redeemable NCI": OMC; LYB).
- Scale taken from "shares in Thousands" (EMR shown x1000).
- Balance sheet with duplicate date columns (0000098362).
- Standard-label total "Liabilities" not read (PEP 62,930).
- Bare "Equity" total not read (LEA).
- Capitalization layouts without a total-equity line (WEC).

## Untested
- The 2,621 production cells with no slot cell (the reader never produced one; production is shown unverified).
- Strata beyond the drawn cells.
- The 11 companies outside my reconstruction.

**Requests and disk:** about 390 SEC requests; downloads deleted; free disk 6 GB.
