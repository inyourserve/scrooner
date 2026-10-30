# Verify: release package 1, slot.bs_total_liabilities@1 (origin/work/scrooner-25/slot-records d2479c8), 2026-10-26

Verifier 2. Seed random.Random(20261123). Files: results/release_bs_total_liabilities_1/ (PACKAGE.json, bs_release_release1_cells.jsonl). Claimed: 3,533 cells at 354 companies = 3,441 sampled differences + 90 pre-fills + 2 hides. Faces read with the kit on main (8b651bc): 146 requests, plus 4 hand reads; nothing on disk. Read-only DB on one connection with a 20s timeout. FILING-CHECKED.

**Release 1 may ship: NO as packaged.** One wrong slot value was found (UPS 2017-12-31). YES once the 98 release-1 cells with a nonzero identity gap (UPS is one of them) and the 39 cells with no replay row are pulled or verified. The remaining 3,396 gap-0 cells can ship.

## Changed cells since my sample
None. All 3,441 release-1 differences carry the same slot value and rule as the file I sampled at 8fdb9ca. Changed and new cells (1,135 + 326 + 9) are in release 2.

## Draw (60 differences stratified like before, + 10 fills, + the 2 hides)
| Stratum | Drawn | Slot right | Production wrong |
|---|---|---|---|
| printed_total | 4 | 4 | 4 |
| face_sum A <=1% / 1-10% / >10% | 3 / 4 / 3 | 10 | 10 |
| face_sum B <=1% | 22 | **21** (MRK, SYY, Aramark by hand) | 22 |
| face_sum B 1-10% / >10% | 17 / 7 | 24 | 24 |
| fills | 10 | 10 | (blank) |
| hides | 2 | (no slot) | 2 |
| **Total** | 72 | **70 of 71 slot values** | **62 of 62** |

Production-wrong count in the draw: 60 of 60 differences, plus both hide cells.

## The wrong slot value
UPS 2017-12-31 (0001090727-18-000009 R2): slot 44,410M.
- The face gives 44,373M = current 12,708 + long-term debt 20,278 + pension 7,061 + deferred taxes 757 + self-insurance 1,765 + other 1,804. That equals total L&E 45,403 - total shareowners' equity 1,030.
- The slot is 37M too high: it includes "Deferred compensation obligations" 37, an EQUITY-section line, offset in equity by treasury stock (37).
- Its replay row says identity_ties with gap -7M against a tolerance of 8M. The footing tolerance let it through.
- Production (44,409M) is also wrong.

## Reach and the fix
- Of the 3,533 release-1 cells, 3,396 have a replay identity gap of exactly 0, 98 have a nonzero gap within tolerance (UPS among them), and 39 have no row in the replay reports I could read (DATA-INFERRED from the builder's census, facesum_rest, v19 and batch6 reports).
- Ship the 3,396. Hold the 98 + 39 for a check, or require gap = 0 (one printed unit at most) for face-sum cells.
- Exclude equity-section lines (deferred compensation obligations, AOCI components; see also BSX in batch 6) from the member set.

## The 2 hide cells
- CIK 0000764622 2021-12-31: production 16,212,282K vs face 15,981,762K.
- CIK 0001130464 2019-12-31: production 5,196,334K vs face 5,094,388K.
Both are confirmed wrong (as in my dry-run check), so hiding them is right. The face gives the right value for both, so filling them later would add coverage.

Untested: release 2; the 857 holds that stay on production; the 2,621 production cells without a slot cell.
