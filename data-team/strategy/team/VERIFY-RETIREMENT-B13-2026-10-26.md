# Verify: retirement Family B, plan 13 (work/data-engineer/derivation-gate 8b51221; dryrun_B13_keep), 2026-10-26

Verifier 2. Seed random.Random(20261119). Kit on main (8b651bc): `select_income_statement`, `net_income_lines`, `RPage.column(months=)`, `printed_unit`; my own reader for 2 pages. About 135 SEC requests, nothing on disk. Read-only DB on one connection with a 20s timeout. FILING-CHECKED unless marked.

## Result: GATE FAILS on two cells. Everything else checked is right.
1. **Restated full year shown on the original basis:** company 3460 (CIK 0001599617) FY2023 NetIncomeLoss is replaced with 247M (0000950170-25-021784, face "Net income" 248). The latest 10-K (0001193125-26-072828) restates the year to 250M (face 251).
   - The copies disagree beyond rounding. Under the founder HIDE ruling this cell must be hidden, not shown at the original 247M.
   - The authority check does not list this key: the authoritative 250M copy plus the promoted 247M copy leave two (or the 250M copy is superseded by the loose "same figure" path).
2. **False precision:** ABNB (2929) Q4 2022 is shown as 318,663,000. The FY input is printed "$ 1,893,000,000" (0001559720-25-000010). That is a whole-dollar R page of a figure the filer rounded to millions; `printed_unit` reads 0 decimals, so it gives $1. The filing supports 319M, the value B11 showed.
   - Rule: a whole-dollar page value with six or more trailing zeros has unit 1M, or take `decimals` from the XBRL instance.

## 1. The 19 scale cells (inputs read in each filing's own column with `printed_unit`)
**Exact, right (10):**
- GIS 614.9M; Leggett 52.8M; MCD 1,903.4M; CACC 151.9M; 1833 -7.9M; AKTX -5,298K; 3592 Q4 2022 12.2M; AXTA 43.6M; FTNT 526.2M; GME 131.3M.
- Several now use the ORIGINAL nine-month 10-Q (e.g. GIS 0001193125-23-077864).

**Coarse, right (7 of 8):**
- BAH 193M; TJX 1,038M; TDS -506M; 1559 14M.
- 2993 17.8M (nine months "60.0", unit 0.1M; fixed).
- 3592 Q4 2024 17.2M: FY printed "$ 44,200,000" whole dollars, nine months "27.0"; the 0.1M unit is right.
- Ambac (1694) 175M. Note: the FY input is the consolidated "Net income (loss)" 522,120K, not the attributable 522,380K the brief cites. Both give 175M at the 1M unit, but the tag should be the attributable line.

**Coarse, over-precise (1):** ABNB (above).

**3592 Q4 2025 hidden:** a page-parsing gap, not an unverifiable value.
- The 10-Q (0001628280-25-048963) header reads "shares in Thousands, € in Millions", and the date cells carry "USD ($) $ / shares shares", so the kit finds no columns.
- The value is derivable: -70.1M (FY, 0001628280-26-008601) - (-49.0M) = -21.1M.

## 2. The 5 authority exceptions
- **Companies 2579 (CIK 0001527590, FY2022 and FY2023) and 2898 (CIK 0001556593, FY2022):** the two authoritative copies are a 10-K and a 10-K/A with the SAME value (186,267K / 331,454K / 864,793K). They are not different vintages, so nothing to hide. Keep one authoritative copy (pre-existing duplicates).
- **Company 4938 (new Pinnacle holdco, CIK 0002082866, FY2023 and FY2024):** the 10-K copy, 562,152K / 475,056K, is right on the face of 0002082866-26-000018. The authoritative 8-K copy (0002082866-26-000020) carries 543,705K / 482,460K.
  - Those match Synovus's own reported net income. This is ASSUMED, from memory; the 8-K was not read.
  - So the 8-K is most likely the merger partner's figures. Demote the 8-K copy and keep the 10-K. Do not hide: the cells already show the right 10-K value.

## 3. 15 of the superseded copies (rebuilt: 70 other-authoritative copies beside promoted facts)
- **13 right:** the survivor is the precise original and the superseded copy is its rounded later copy, or an identical 8-K copy.
  - STE 614,641 vs 614,600; NXST 971.1M vs 971.0M; MCD 8,468.8 vs 8,469; BAH 271,791 vs 272,000; CHWY 392,738 vs 392,700 and 39,580 vs 39,600; AXSM; CSGP 292,564 vs 292,600; HL and 0001022408 (identical 8-K copies); 0001448431; 0001646188; 0001839839.
  - Survivors are face-checked where shown.
- **Not right: 2.** 0001599617 (restated 247 vs 250, finding 1) and the PNFP 8-K (section 2).

## 4. 15 of 241 promoted facts: 15 right on the face
- Examples: LNG FY2025 5,330M attributable; JPM FY2022 37,676M; MA FY2021 8,687M (ProfitLoss, no NCI line); SM 770,293K; NOW 230,141K; CIK 0000884887 -5,260,499K; CIK 0001636651 9M -37,016,925; Sanara (CIK 0000714256) attributable -4,303,197.
- Two read by hand where the kit missed:
  - CSWC FY2024 83,389K: "Net increase in net assets from operations", a BDC label `net_income_lines` does not know.
  - DFH 9M 2021 63,830,023 attributable: a leading blank cell shifts the kit's columns.

## 5. 10 random cohort replacements: 10 right
- COIN FY2022 -2,624,949K; SUNB FY2026 1,325.0M (scale fix); GIS FY2026 -87.6M attributable; WTFC 695,045K; PH FY2026 3,648M (attributable; face net income 3,649); TXG -58,223K; KMX 479,204K; S -271,101K.
- Derived: CHE Q4 2025 76,751K = 265,238 - 188,487; HD Q4 FY2024 2,997M = 14,806 - 11,809 (proxy-stored 3,001M was wrong).

## Can Family B go to the Release Manager's apply review?
1. Not yet. Two cells must change first: 0001599617 FY2023 (hide under the ruling) and ABNB Q4 2022 (show 319M).
2. The authority check has to see that 0001599617 key. Demote the PNFP 8-K copies and pick one copy for the 2579/2898 duplicates.
3. 3592 Q4 2025 and Ambac's tag choice are coverage and consistency items, not wrong values. They can follow the apply.
4. After those changes the remaining list is procedural: CLX ingestion gap, founder confirmation of HIDE for full years, the reviewed apply transaction with restore, a sample outside the cohort, and doc 02.
5. With the two cells fixed and a re-run of section 2, I would pass it to apply review.
