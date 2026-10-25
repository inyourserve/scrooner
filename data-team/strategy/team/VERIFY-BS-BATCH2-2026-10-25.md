# Verify: BS rollout batch 2 (origin/work/scrooner-25/slot-records b69294f), 2026-10-25

Verifier 2. Every manifest instant (first, last, every boundary era; 97 cells, 97 filings) checked on the balance-sheet R page of its own accession; face liabilities derived independently (printed "Total liabilities", else L&E total - total equity - printed mezzanine). FILING-CHECKED.

## Result: GATE PASSES for shown values: 90 of 90 shown cells right. 7 sampled cells are withheld (TMUS 6, ALB 1) where the face gives the value: avoidable holds, no wrong value shown.
| Company (CIK) | Manifest cells | Shown, right | Notes |
|---|---|---|---|
| SBAC (0001034054), STZ (0000016918), BURL (0001579298), MNST (0001288469) | 4 / 9 / 2 / 9 | all | |
| RYN (0000052827) | 12 | 12 | mezzanine "Noncontrolling interests in the Operating Partnership / redeemable OP units" (from 2020) kept outside liabilities, e.g. 2020-06-30 3,769,267 - 1,913,958 - OP units = 1,745,089K (0000052827-20-000201 R4) |
| MXL (0000865752) | 6 | 6 | |
| EPD (0001061219) | 6 | 6 | partnership; Series A cumulative convertible preferred units (49.1M, mezzanine from 2020) correctly outside: 63,736.2 - 26,104.7 - 49.1 = 37,582.4 (0001061219-20-000040 R2) |
| BBIO (0001743881) | 16 | 16 (printed totals) | the 17 "printed-total identity gaps" are the redeemable convertible NCI mezzanine line (e.g. 23K at 2025-09-30); printed TL 2,920,979K right (0001743881-25-000012 R2) |
| ALB (0000915913) | 17 | 16; 2015-03-31 withheld | withheld value is derivable: 9,794,759 - 3,247,330 = 6,547,429K on the face |
| TMUS (0001283699) | 16 | 10; 6 withheld | withheld values are derivable: e.g. 2018-03-31 current 12,357 + total long-term liabilities 36,771 = 49,128M (0001283699-18-000026 R2); TMUS prints both subtotals, so the face sum is current + long-term subtotal |
My first automated pass mis-read 23 cells (a leading blank column on old R pages and an unrecognised OP-units mezzanine label); all 23 were re-read and match.

## For scrooner-25
TMUS and ALB: use the printed section subtotals ("Total current liabilities" + "Total long-term liabilities") as the members; the double count comes from summing their children too. Re-verify those 19 withheld cells after the fix.
