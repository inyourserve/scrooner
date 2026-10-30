# Verify: retirement Family B, plan 2 (work/data-engineer/derivation-gate 356af1c; dryrun_B2_keep), 2026-10-25

Verifier 2. Cohort 783 cells (672 replaced, 60 proxy_only_source, 51 proxy_filed_copies_disagree). Seed random.Random(20261106), one cell per company per set. FILING-CHECKED where an accession/R page is cited, else DATA-INFERRED (core.fact rows).

## Result: GATE FAILS. Replacements show net income INCLUDING noncontrolling interests for 118 cohort cells at 19 companies (DATA-INFERRED count), because `net_income` ranks `ProfitLoss` (priority 2) above `NetIncomeLossAvailableToCommonStockholdersBasic` (priority 3). And the disagreement rule hides values that are filed, including precise copies that only differ from a later rounded copy.

## 1. Earlier cases
| Cell | Plan | Filing | Verdict |
|---|---|---|---|
| MA FY2024 | 12,874M from 0001141391-26-000013 | R3 2024 column: Net Income 12,874 | right |
| JPM FY2021 | 48,334M from 0000019617-24-000225 | R3 2021 column 48,334 | right |
| CHE FY2021 | 268,550K from 0001562762-24-000045 | R2 2021 column 268,550 | right (a second CHE cell, stored -193,656,450, proxy-only, removed: right) |
| GIS FY2024 | 2,496.6M from 0001628280-26-046466 | NetIncomeLoss 2,496.6M in that filing (DATA-INFERRED; R page not matched by my reader); attributable figure as on 0001193125-24-168943 R2 | right |
| CAT FY2023 | 10,332M from 0000018230-26-000008 | R3: "Profit of consolidated and affiliated companies" 10,332 includes NCI; profit attributable to common 10,335 | **WRONG** (NCI-inclusive) |
| TXRH FY2023 | 313,675K from 0001104659-26-021292 | R4: incl. NCI 313,675; attributable 304,876 | **WRONG** |
| Q4: CMG, LW, MKTX, NFLX, TJX | replaced with the 10-K-derived Q4 (282,086K; 129.6M; 69,627K; 607,429K; 1,773M) | DATA-INFERRED (derived from the 10-K FY minus the 9M) | fixed |

## 2. 20 of the cohort replacements >= 10% or scale (96 such cells)
Right 15: scale fixes CHE 2024, CACC 2021, SUNB, and the 10-K-derived Q4 replacing a proxy-derived Q4 (RBRK, KYMR, ED, ANET Q4 2024 801M, HUBS, HSIC, GTLB, MET, TKO, DT, Q); LNG FY2025 5,330M (NetIncomeLoss, attributable).
**Wrong 5 (NCI-inclusive ProfitLoss chosen over the attributable line):** FCX FY2021 5,365M vs attributable 4,306M (0000831259-22-000009 R3); PCG FY2023 2,256M vs income available for common 2,242M (0001004980-24-000014 R3); WELL FY2022 160,568K vs 141,214K, APA FY2021 1,313M vs 973M, OHI FY2021 428,302K vs 416,739K (DATA-INFERRED, same tag pattern). The stored proxy figures (attributable) were the right concept, two of them in the wrong scale.
Reach: of 672 cohort replacements, 191 use ProfitLoss; 118 of those (19 companies: CAT x5, THC x5 with 1,311M vs 611M in FY2023, AM, ...) sit beside a different attributable fact in the same filing.

## 3. 15 of the 51 proxy_filed_copies_disagree removals
- Rounding only, not vintages (false removals: the precise filed copy should win): SM FY2024 770,293K vs later 770,000K; WDAY FY2022 29,373K vs 29,000K; NOW FY2021 230,141K vs 230,000K.
- Genuine restatements (copies are different vintages): CHWY FY2021 -73,817K -> -75,207K; GEN FY2023 1,349M -> 1,334M; LII FY2024 806.9M -> 811.1M; OMF FY2022 878M -> 872M; UNM FY2021 824.2M -> 981M (LDTI); RGA FY2022 623M -> 517M; EQH FY2023 1,302M -> 1,283M; LYV FY2023 563.3M -> 556.9M; FRHC FY2025 84.65M -> 76.29M; JXN FY2021 3,183M -> 3,417M (8-K recast); AR FY2022 restated; FIS FY2023 -6,654M -> -6,655M. Each cell is blanked although the latest periodic copy is filed. The rest of the dataset uses "latest filed"; hiding these is a policy change that needs a ruling, not a verifier pass. Recommendation: publish the latest periodic copy (with the vintage recorded), as elsewhere.

## 4. 15 of the 60 proxy_only_source removals
Right 14: calendar-period duplicates of 52/53-week or shifted fiscal years whose 10-K cell exists under its own period (DRI FY2026 2025-05-26..2026-05-31, ONTO FY2024, VFC FY2025, HAS FY2023); successor CIKs without the old 10-Ks (VNOM, BLK, PNFP); predecessor-plus-successor proxy sums (VAL 2021, EXE 2021, WULF 2021); proxy-derived quarters with no periodic Q4 (VRSN Q4 2021, UNM Q4 2022, CHE Q4 2025 -188M, ALGM partial period).
CLX FY2026: the stored proxy 601M is "Net earnings" incl. NCI (attributable 587M, 0000021076-26-000034 R3), so removal is not a false removal, but our core.fact has no FY2026 net income from that 10-K at all: an ingestion gap to route.

## Required before apply
1. Net income replacement must prefer the attributable line (NetIncomeLoss, else NetIncomeLossAvailableToCommonStockholdersBasic) over ProfitLoss; ProfitLoss only when no attributable fact exists and the filer has no NCI.
2. A disagreement that is only rounding is resolved to the precise copy, not hidden.
3. Vintage disagreements: follow the dataset's latest-filed rule (or get a ruling); do not blank silently.
4. Route CLX FY2026 (10-K facts missing).
