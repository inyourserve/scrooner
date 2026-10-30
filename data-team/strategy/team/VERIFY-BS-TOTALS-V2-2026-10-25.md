# Verify: BS totals V2 (origin/work/scrooner-25/slot-records 24684b4), 2026-10-25

Verifier 2. Method: read-only copy of the branch's `bs_replay.py` with a per-instant dump (reproduced 699 ties / 12 gaps, 136 needs_instance_reader, 5 not computable; one connection, 20s). For each sampled cell the balance-sheet R page of the cell's own accession was opened (114 filings) and the face liabilities derived independently of our members: the printed "Total liabilities" row, else the L&E total minus the last equity total minus printed mezzanine rows; every mismatch read by hand. One reader. FILING-CHECKED unless marked. Seed random.Random(20261030).

## Result: GATE PASSES for shown values in this sample: 0 wrong of 112 shown cells checked. Not yet safe to switch on: 4 false holds (one class) and 3 latent misclassifications that become wrong values once the instance reader fills custom facts.

## 1. AWK (all 46 instants, all 23 era records)
Every instant is needs_instance_reader: no value shown. Right. Composition when the reader fills: 2016-2026 eras use the custom "Total long-term debt" subtotal + current + regulatory/other + CIAC, which reproduces the face (2017-12-31: 6,498 + 2,325 + 3,998 + 1,276 = 14,097, 0001410636-18-000076 R2; 2016-06-30: 12,553). LATENT: the same custom subtotal (`LongTermDebtIncludesRedeemablePreferredStockAtRedemptionValue`; 2014-15 eras `RedeemablePreferredStockAtRedemptionValue`) is ALSO listed in `mezzanine_face`, so the identity would subtract it twice and withhold a right value (or, with a borrowed graph, tie wrongly). Remove it from the mezzanine slot.

## 2. 30 of the 129 formerly held ties (random; NI 8, WMT 8, MCK 6, EMR 3, ET 2, AWK 2, BRKR 1)
28 shown, all right (20 matched by the automated face check; the 8 WMT cells matched after I read them by hand: my checker's mezzanine pattern caught "Nonredeemable noncontrolling interest"; e.g. WMT 2023-07-31 255,121 - 85,327 - redeemable NCI 232 = 169,562 = ours, 0000104169-23-000097 R4). The 2 AWK cells are needs_instance_reader (no value). No false hold left in this group.

## 3. BRO (CIK 0000079282), all 47 instants
46 ties, all 46 equal the face (LSE - total equity). 2019-01-01 is not computable: correct, that column is the ASC 842 adoption column of the Q1 2019 10-Q, not a balance-sheet date. Anchor 2018-12-31 equity 3,000,568K passes.

## 4. GE's 12 gaps
All 12 slot values equal GE's printed consolidated "Total liabilities" (e.g. 2019-06-30 255,980 on 0000040545-19-000053 R6; 2020-06-30 221,233 on 0000040545-20-000046 R3; 2021-09-30 198,172; 2022-12-31 150,206). The face itself ties (312,109 = 255,980 + 56,129). The gap (-132M to -498M) is the cross-check's: `MEZZ_FALLBACK` subtracts `RedeemableNoncontrollingInterestEquityCarryingAmount` (408M at 2019-06-30, 171M at 2021-09-30), which is not a line on GE's face. Shown values right; the fallback is a defect for records with `requires_identity_tie` (an off-face fact can withhold a right value or make a wrong one tie). Read the mezzanine only from the record's face slots.

## 5. 25 random ties across 14 companies (AJG, BRKR, BX, DIS, EMR, ET, FE, KKR, MCK, NI, OXY, T, VLO, WMT; max 2 each; cells checked in earlier rounds excluded)
25 of 25 right (6 against a printed total, 19 by LSE - equity - mezzanine).

## 6. Anchors
BRKR 2019-03-31 1,298.7 = 2,242.3 - 921.6 - 22.0 (0001104659-19-027788 R2): right. 14/16 anchors pass at the values from my earlier reports; TRGP and AWK are needs_instance_reader (correct holds).

## False holds (not computable while the face gives the value)
DVN 2018-09-30 (0001564590-18-027813 R4): the record's member `LiabilitiesOfDisposalGroupIncludingDiscontinuedOperationNoncurrent` is blank on the face for that column (held-for-sale lines only in the Dec 2017 column); face L = 20,172 - 8,898 = 11,274 = the sum of the other members (3,224 + 5,791 + 1,103 + 613 + 543). Same mechanism (DATA-INFERRED): DVN 2018-06-30, 2018-12-31, ET 2018-03-31. Rule: a member printed blank in that column of the same face is zero, not missing.

## Latent misclassifications (held today only because the element is custom)
- MCK 12 instants (2017-06..2020-03 eras): member `OtherCapital` is the EQUITY row "Other (1)" (0000927653-18-000010 R4). Filling it would put equity into liabilities (the v0 class). Extend the equity guard to "OtherCapital" / position after the equity header.
- ET 2016-03-31: member `ConvertiblePreferredUnits` is "Series A Convertible Preferred Units 0" in the EQUITY section (0001276187-16-000165 R2).
- AWK: subtotal double-listed as liability member and mezzanine (above).

## Untested
TRGP/DVN/MCK values after an instance reader, borrowed-graph records (2 of 338), second reader.
