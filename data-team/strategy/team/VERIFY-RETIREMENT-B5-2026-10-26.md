# Verify: retirement Family B, plan 5 (work/data-engineer/derivation-gate de9e6b7; dryrun_B5), 2026-10-26

Verifier 2. Cohort 783 cells reproduced (625 replaced; 60 proxy_only_source, 46 proxy_filed_copies_disagree, 24 derived_mixed_vintage, 20 derived_from_rounded_input, 8 proxy_nci_inclusive_only). Seed random.Random(20261111). Income statements fetched for 12 accessions (2 pages not matched), plus core.fact reads (one connection, 20s timeout). Each derived quarter recomputed as original-vintage precise full year minus original nine months. FILING-CHECKED where a face is cited, else DATA-INFERRED.

## Result: GATE FAILS narrowly.
- **Wrong values shown:** 2 of the 15 sampled derived replacements are built from rounded inputs (STE, HOOD), which the new rounded-input check misses.
- **Good quarters hidden:** 2 of the 15 sampled derived removals were exact (HUBS, BAH).
- All B4 findings are fixed.

## 1. B4 findings
- **MA, 10 cells released: right.** 12,874 / 11,195 / 14,968 on 0001141391-26-000013 R4, and 9,930 on -25-000011. The face has one "Net Income" line and no NCI line.
- **EQH Q4 2021 removed: right.** The original-vintage Q4 would be -439 - (-693) = 254M; not produced.
- **EQH Q4 2022 replaced with 62M:** restated FY 2,153 minus restated nine months 2,091. One vintage, so right (DATA-INFERRED).
- **EQH FY2021-FY2024 removed as proxy_filed_copies_disagree:** these are original vs LDTI-restated vintages. This is the open B2 policy question. The latest 10-K copy (e.g. FY2022 2,153M) is filed and hidden; it needs a ruling.
- **ST FY2023 -3,909K: right.**
- **ST Q4 2023 removed: right.** -202,229 = rounded -3,900 - 198,329. The good value -202,238 is derivable.
- **LNG FY re-promoted: right** (-2,343 / 1,428 / 9,881). The 3 Q4 cells stay removed until the Normalizer runs (accepted).
- **CLX FY2026: still 0 facts from 0000021076-26-000034;** both cells stay removed (right; ingestion gap open).

## 2. SM Q4 2024 and WDAY Q4 FY2022
- **SM Q4 2024 187,985K: removal right.** It equals the rounded FY 770,000 (0000893538-26-000032) minus the nine months 582,015. The precise original FY 770,293 (-25-000008) gives **188,278K**, a good value that is not produced.
- **WDAY Q4 FY2022 -73,626K: removal right.** It equals rounded 29,000 minus 102,626. The precise 29,373 (-22-000030) gives **-73,253K**, also not produced.
- Same pattern: SM Q4 2023 247,231 (good 247,111) and WDAY Q4 FY2023 -125,948 (good -125,697).

## 3. 15 of the 44 derived removals
- **Right 13:** MLM 283.4 (good 282.5), EQH, CHWY Q4 FY2021 -64,992 (good -63,609), MRVL 6.2M (6,168K), HIG 735 (729), ST, BAH Q4 FY2023, CHWY Q4 FY2024 31,906 (34,263), AXSM (-33,976,136), ANET garbage (613,636K), OKTA (-241,186K), RCL (-1,356,968K), SM.
- **False removals 2** (the stored value equals the precise same-vintage derivation):
  - HUBS Q4 2022 -15,636K = -112,749 - (-97,113), removed as mixed_vintage only because a restated FY copy (-107,347) exists.
  - BAH Q4 FY2024 127,956K = 605,706 - 477,750, removed as rounded_input although the precise copy gives exactly that value.
- In all 15 the right quarter is derivable from the precise original-vintage copies already in core.fact. Recommendation: derive Q4 from the precise original copies instead of only removing.

## 4. 15 of the derived replacements (182 by my count, not 77)
- **Right 12:** GME x2, IT, CPAY, VRSN x2 (ProfitLoss, no NCI), RBRK -114,889K, ETSY 109,548K, CACC 122.0M, TGTX, BJ, NCLH.
- **WRONG 2 (built from rounded inputs):**
  - STE Q4 FY2025 145.7M against the precise 614,641 - 468,969 = 145,672K. The 2026 10-K prints 614.6 (0001628280-26-039136 R4).
  - HOOD Q4 2021 -423M against -3,686,432 - (-3,263,165) = -423,267K. The 2023 10-K prints (3,687) (0001783879-24-000054 R4).
- **Concept slip 1:** CAG Q4 FY2025 uses ProfitLoss (1,152.5, includes NCI) while the attributable FY is 1,152.4. That is 0.1M, but it is the NCI-inclusive tag.

## 5. 10 random replacements
Right 10 on the face or in DB:
- AXSM -130,402,992; BKNG 5,404M; QLYS 107,992K; DKS 1,519,871K; DOCS 154,783K; EGP 157,557K (attributable; incl. NCI 157,638); WTFC 823,844K; FCX 4,306M.
- HL -84,217K and WELL 336,138K are DATA-INFERRED (statement page not matched).

## Required before apply
1. The rounded-input check must compare each input against the precise copy (STE, HOOD).
2. Only call a value mixed-vintage when the values actually differ across vintages (HUBS, BAH); do not judge by filing dates alone.
3. Re-derive removed quarters from the precise original copies.
4. Rule on vintage-disagreement removals (EQH).
5. Use the attributable tag for CAG quarters.
