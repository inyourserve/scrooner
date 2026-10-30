# Verify: retirement Family B, plan 10 (work/data-engineer/derivation-gate bfdfb05; dryrun_B10), 2026-10-26

Verifier 2. Seed random.Random(20261115). Cohort reproduced: 783 = 658 replaced + 125 removed (42 proxy_only_source, 46 proxy_filed_copies_disagree, 36 derived_inputs_disagree, 1 nci); derived_inputs_unverified = 0. Income statements read with my per-Report reader, because the kit's IS reader is still unreliable (B8 finding): 38 filings, about 76 requests, nothing on disk. Read-only DB on one connection with a 20s timeout. FILING-CHECKED unless marked.

## Result: GATE FAILS on the new coarse-scale rounding.
- The rounding unit is inferred from trailing zeros. Inputs printed with decimals that happen to be zero ("96.0", "4,274.0") or round thousands ("12,000") are treated as whole millions.
- **1 wrong value shown:** AKTX Q4 2025 shows -5,000,000. The face gives -17,298K - (-12,000K) = -5,298K (0001493152-26-013664, 0001493152-25-022390, both in thousands).
- **At least 6 over-rounded values** lose a printed digit (section 3).
- Everything else checked is right.

## 1. Released by the face check (18 rows = 9 cells x 2 concepts, plus MA's 10): all right
On every input filing's statement the bottom line is a single "Net income" tagged ProfitLoss, with no NCI or attributable line. The pre-tax "before Income Taxes, Noncontrolling Interest" label is correctly ignored.
- **VRSN Q4:** 2021 330,082K = 784,830 - 454,748 (0001014473-22-000007 / -21-000027); 2022 179.5 = 673.8 - 494.3; 2023 264.7 = 817.6 - 552.9; 2024 191.5 = 785.7 - 594.2; 2025 206.2 = 825.7 - 619.5.
- **SAIC Q4 FY2026:** 85 = 358 - 273 (0001571123-26-000029 / -25-000189).
- **company_id 1519 (CIK not looked up):**
  - Q4 FY2026 557,044 = 1,805,681 - 1,248,637.
  - Q4 FY2025 327,714 = 1,273,414 - 945,700.
  - Q4 FY2024 156,615 = 1,441,463 - 1,284,848.
  - The faces are in whole dollars with no NCI line, and they are combined-filing comprehensive-income pages.

## 2. EQH, HOOD, HUBS
Still hidden as derived_inputs_disagree (EQH Q4 2021-2024, HOOD Q4 2021, HUBS Q4 2022-2023). Right under the HIDE ruling.

## 3. Coarse-scale display (19 cells marked "rounded to 1,000,000")
**Acceptable** where an input really is printed in whole millions. These show a visibly rounded value:
- BAH Q4 FY2025 193,000,000 (FY 935 in millions, 0001628280-26-037521).
- TJX Q4 FY2023 1,038,000,000 (FY 3,498 in millions).
- TDS Q4 2023 -506M (9M "6" in millions).
- 0000821130 Q4 2023 14M (9M "40" in millions).

**Loss of a printed digit** (both inputs printed to 0.1M):
- GIS Q4 FY2023: 615M vs 614.9 = 2,593.9 - 1,979.0 (0001193125-24-072690).
- CACC Q4 2024: 152M vs 151.9 = 247.9 - 96.0 (0000885550-25-000124).
- MCD Q4 2022: 1,903M vs 1,903.4 = 6,177.4 - 4,274.0 (0000063908-23-000101).
- FTNT Q4 2024: 526M vs 526.2 (9M 1,219.0, 0001262039-25-000039).
- Leggett (company 664) Q4 2022: 53M vs 52.8 (9M 257.0, 0000058492-23-000030).
- Likely the same, not read: AXTA, GME, 3592, 1694, 1833, ABNB, 2993.

**WRONG:** AKTX -5M vs -5.298M.

Fix: take the rounding unit from the facts' XBRL `decimals` (or the printed precision on the R page), never from trailing zeros.

## 4. 10 random cohort replacements: 10 right
HD FY2024 14,806M; PNFP FY2023 562,152K; WELL FY2025 936,845K (attributable); RBRK FY2026 -348,828K; CROX FY2023 792,566K; AM FY2024 400,342K (attributable; DATA-INFERRED, the face shows 400,892 including preferred); KYMR Q4 2025 -86,981K = -311,351 - (-224,370); DKS Q4 FY2025 128,337K = 849,239 - 720,902; DT Q4 FY2022 929K = 52,451 - 51,522; VRSN Q4 2025.

## What remains before Family B can be applied
1. Derive the coarse rounding unit from XBRL decimals or printed precision, not trailing zeros (AKTX wrong; GIS, CACC, MCD, FTNT, 664 over-rounded). Re-run, then re-verify all 19.
2. Route the CLX FY2026 10-K ingestion gap (0000021076-26-000034 has 0 facts). Until it lands, both CLX cells stay removed.
3. LNG's earlier Q4s now derive correctly, but they depend on re-promoting 1,007 periodic facts. Verify the re-promotion step on a dry-run write before apply.
4. The 46 proxy_filed_copies_disagree FY cells (EQH FY, HOOD/HUBS FY) are hidden under the ruling. Confirm with the founder that full-year cells, not just quarters, follow HIDE.
5. Fix the kit's income-statement reader (note-page selection, dropped first column on 3M + YTD pages) before the Verifier relies on it for this family.
6. The apply step itself (demote 1,314 proxy facts, recompute 7,671 metric values) has never been verified. It needs a reviewed dry-run write plan with restore, per the shared-table rule.
7. Re-check the 42 proxy_only_source removals after step 3, in case a re-promoted periodic copy now gives a filed value.
8. Population outside the cohort is not sampled for the face-release and coarse-rounding rules (28 / 19 are population counts). Draw one sample there before a full apply.
9. Record the founder ruling and the off switch (`--original-basis`) in doc 02 / the decision register, so the behaviour is traceable.
10. After apply: run a certification diff (invariants I1-I11) on the touched companies, and spot-check 10 displayed cells on the live site against the filings.
