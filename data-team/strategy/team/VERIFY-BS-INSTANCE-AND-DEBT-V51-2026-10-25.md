# Verify: BS instance-reader fill (V3.2) and Debt V5.1 (origin/work/scrooner-25/slot-records f09360d), 2026-10-25

Verifier 2. FILING-CHECKED unless marked. Seed random.Random(20261102).

## Result: GATE PASSES for shown values: 72 instance-filled BS cells and COST 2018-09-02 debt all right. Debt V5.1 holds far too much: in 20 sampled review cells the face value is right in all 20 (most should be flags, not holds), and 6 of the 8 current_maturities_unverified cells plus COST 2019-02-17 are false holds.

## 1. BS cells filled from the filings' own instances
Replay re-run (read-only copy, instance evidence as 4th arg): 851 ties, 0 gaps, 16/16 anchors reproduced.
| Set | Checked | Right | Notes |
|---|---|---|---|
| AWK, all 46 instants | 46 | 46 | e.g. 2015-12-31 12,192 = 17,241 - 5,049 (0001564590-16-013247 R2; redeemable preferred 12 inside capitalization); 2017-12-31 anchor 14,097 |
| TRGP random 15 | 15 | 15 | L = L&E - owners' equity - Series A preferred: 2017-06-30 13,918.4 - 6,935.2 - 203.3 = 6,779.9 (0001564590-17-015398); 2016-06-30 6,983.1; 2022-03-31 mezz 749.7; 2026-03-31 23,838.3 (no preferred) |
| DVN instance-filled 10 (incl. all 4 new blank-member cells 2020-03..12) | 10 | 10 | face L&E - equity equals ours in all 10; the blank members are standard (`DeferredTaxLiabilitiesNoncurrent` / `DeferredIncomeTaxesAndOtherTaxLiabilitiesNoncurrent`, held-for-sale) |
| BRKR 2019-12-31 | 1 | 1 | |
TRGP double-count check: in every sampled cell (10-Ks 2018-12-31, 2019-12-31, 2020-12-31 included) the dimensioned Series A value was read once (`dims:1`) and equals the face (e.g. 2020-06-30 297.0, 2018-12-31 245.7); no 2x value. Blank-member rule: only standard members were zero-filled in the sample.

## 2. Debt V5.1
**COST 2018-09-02 = 6,577M: right** (0000909832-18-000013 R39 carrying total; the Q2 FY2019 note 0000909832-19-000003 R32 shows face value 6,613 - 36 = 6,577 for that date).

**COST 2019-02-17 (0000909832-19-000003 R2, R32): face 1,698 + 4,794 = 6,492 is RIGHT.** The note's 6,525 is "Total long-term debt, Face value" (principal); less unamortized discounts and issuance costs 33 = 6,492 carrying. The review hold is a false hold: the note-tie compares the carrying face lines with a principal figure (ledger row 118: a note "total" can be gross principal).

**20 review cells (seeded, max 3 per company).** Face sum read on each balance sheet; reason for the note mismatch:
| Cell (accession) | Face debt lines | lane3 / note | Why the tie fails | Hold? |
|---|---|---|---|---|
| COST 2020-05-10 (0000909832-20-000009) | 1,497 + 7,598 = 9,095 | note face value 9,149 - 54 = 9,095 | principal vs carrying | false hold |
| COST 2021-11-21 (0000909832-21-000021) | 799 + 6,667 = 7,466 | 7,504 - 38 | same | false hold |
| COST 2020-08-30 (0000909832-20-000017) | 95 + 7,514 = 7,609 | lane3 7,657 | same (discount 48) | false hold |
| ABBV 2017-12-31 (0001551152-18-000014) | 400 + 6,015 + 30,953 = 37,368 | carrying 36,968 + STB 400 = 37,368 | note "gross" 37,612 used | false hold |
| ABBV 2018-12-31 (0001551152-19-000008) | 3,699 + 1,609 + 35,002 = 40,310 | 36,611 + 3,699 | same | false hold |
| CSCO 2017-07-29 (0000858877-17-000016) | 7,992 + 25,725 = 33,717 | lane3 30,472 (notes only, excl. CP) | perimeter: commercial paper on the face | false hold (flag) |
| CSCO 2025-07-26 (0000858877-25-000111) | 5,232 + 22,861 = 28,093 (STD = notes 1,749 + CP 3,482 + other 1) | lane3 24,611 | same | false hold (flag) |
| CSCO 2026-01-24 (0000858877-26-000021) | 8,719 + 21,367 = 30,086 | lane3 24,617 | same | false hold (flag) |
| UNH 2018-09-30 (0000731766-18-000040) | 1,500 + 32,053 = 33,553 | lane3 32,199 | CP inside "commercial paper and current maturities" | false hold (flag) |
| UNH 2021-12-31 (0000731766-22-000008) | 3,620 + 42,383 = 46,003 | lane3 44,632 | same | false hold (flag) |
| INTC 2018-12-29 (0000050863-19-000007) | 1,261 + 25,098 = 26,359 (STD = CP 500 + current LTD 761, R77) | lane3 25,859 | CP | false hold (flag) |
| WMT 2024-07-31 (0000104169-24-000141) | borrowings 3,195 + 1,495 + 35,364 = 40,054; + finance leases 786 + 6,161 = 47,001 | lane3 36,859 | short-term borrowings excluded by lane3 | false hold (flag) |
| HD 2016-01-31 (0000354950-16-000060) | 350 + 77 + 20,888 = 21,315 | lane3 427 (lane3 wrong) | | false hold |
| MRK 2020-03-31 (0000310158-20-000009) | 6,361 + 21,637 = 27,998 | 28,000 (rounded narrative) | rounding | false hold |
| MRK 2023-09-30 (0001628280-23-036717) | 887 + 33,972 = 34,859 | 34,900 | rounding | false hold |
| MRK 2024-09-30 (0001628280-24-045689) | 3,149 + 34,982 = 38,131 | 38,100 | rounding | false hold |
| MA 2024-03-31 (0001141391-24-000087) | 2,086 + 13,543 = 15,629 | 15,600 | rounding | false hold |
| LRCX 2016-09-25 (0000707549-16-000085) | 952,999 + 3,378,179 = 4,331,178K incl. capital leases | note carrying debt 4,323,830K | face lines combine debt and leases | right to hold the BORROWINGS slot (needs the note); lease-inclusive value right |
| LRCX 2020-03-29 (0000707549-20-000081) | 42,407 + 5,043,931 = 5,086,338K | note 5,071,741K | same | same |
| LRCX 2021-06-27 (0000707549-21-000136) | 11,349 + 4,990,333 = 5,001,682K | note 4,960,935K (column order in R75 is 2020, 2021) | same | same |
So 17 of 20 are false holds (the face carrying lines are the right total; the note tag is principal, notes-only, or a rounded narrative), and 3 (LRCX) are right to hold the borrowings slot because the face lines include finance leases. Rule proposal: tie the face sum to the note's CARRYING total (face value less unamortized discount/costs) and to commercial paper + notes; a difference explained by CP, rounding (<= one unit of the narrative's precision) or principal-vs-carrying is a flag, not a hold.

**8 current_maturities_unverified cells**
| Cell | Evidence | Verdict |
|---|---|---|
| CVX 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 (0000093410-23-000009 R5/R103; -24-000013 R106; -25-000009 R107; -26-000078 R104) | "Total short-term debt" (face) = CP + notes + current maturities + current finance leases - reclassified to long-term; face totals 1,964 + 21,375 = 23,339; 529 + 20,307 = 20,836; 4,406 + 20,135 = 24,541; 977 + 39,781 = 40,758 (all incl. finance leases) | current maturities ARE inside the face short-term line: verified. False holds. lane3 (27,389 / 25,379 / 32,791 / 50,699) double-counts the reclassified amount |
| AMAT 2026-04-26 (0001628280-26-037227 R4, R50) | Short-term debt 1,199 (CP 0, so current notes) + LTD 5,256 = 6,455 | false hold; lane3 7,654 double-counts 1,199 |
| MA 2017-12-31 (0001141391-18-000009 R2, R72) | LTD 5,424; maturities in next twelve months 0 | false hold (no current maturities) |
| AMAT 2023-10-29 (0000006951-23-000041 R5, R71) | STD 100 = commercial paper; whether a current note portion sits elsewhere is not shown in R71 | hold right (not verified) |
| COST 2025-08-31 (0000909832-25-000101 R5) | no current-portion face line; LTD excl. current 5,713; current portion inside other current liabilities (COST pattern); note values not read | hold right until the note carrying total is read |

## 3. EW fixture lines (430 securitization, 161 long-term debt due currently)
Not in any EW (Edwards Lifesciences, CIK 0001099800) balance sheet: the fixture is mis-attributed. EDGAR full-text search for the exact pair "Accounts receivable securitization program" + "Long-term debt due currently" returns only Energy Future Holdings / Energy Future Competitive Holdings / TXU / Oncor filings (276 hits, mostly 2006-2013, e.g. EFCH 10-Qs 0001445049-13-000016, 0001445049-12-000008; EFH 10-Q 0001193125-11-116857). EFCH's FY2015 10-K (0001445049-16-000016 R6) shows long-term debt due currently 31 and no securitization line, so the 430/161 pair is from an earlier Energy Future filing that I did not pin down. Recommendation: drop the EW fixture (or re-source it from the 30SET-V4 author's notes); it cannot be exercised on 0001099800-16-000044.

## Untested
TRGP/DVN cells outside the sample; the 165 review cells not sampled (expect the same mix); the borrowings/lease split at LRCX and WMT.
