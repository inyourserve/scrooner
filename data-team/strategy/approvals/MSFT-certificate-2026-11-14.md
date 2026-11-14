# MSFT certificate (Ritwik cloud, approver, 2026-11-14): PASS

**Certified:** MSFT (company_id 4), the FY template of 552 cells for FY2015-FY2026. Coverage file `data-team/strategy/certification/MSFT-coverage-2026-11-14.csv` at main **8ecdbfde**, proof `cell_proof_v15_2026-11-14`. 516 PROVEN, 36 REASON, 0 DISAGREE, 0 UNCHECKED, 0 BLANK. Every row has an accession and an R page.

## Evidence

All checks were made against the SEC filing itself (sec.gov R pages and XBRL), never against our own tables.

| Check | Result |
|---|---|
| Random PROVEN sample, seed `msft-final-2026-11-14`, 32 cells, all years and statements | 32/32 match the filing's printed value at the cited accession, tag and FY column |
| Random REASON sample, same seed, 5 cells | 5/5: each cites its own FY 10-K, and the cited page prints the combined line |
| All 36 REASON cells cite a filing that presents their year | 36/36 (35 their own 10-K; D&A FY2025 the FY2026 10-K, which carries the FY2025 column) |
| total_debt, all 12 FY, full perimeter (face short-term debt and commercial paper, current and long-term debt, note finance leases, pre-842 capital leases) | 12/12 |

**Error bound.** 0 errors in 37 random cells: Clopper-Pearson 95% upper bound **7.78%** for MSFT alone. This is a per-company screen; the 0.10% target is the pooled bound across all certified companies. The total_debt sweep covers every year, so it is a census, not part of the random count.

**total_debt detail:**
- FY2015: 35,292 = 4,985 + 2,499 + 27,808 (FY2015 10-K R5). No capital lease obligations are disclosed for June 30, 2015.
- FY2016: 54,247 = 12,904 + 0 + 40,557 (FY2017 10-K 0001564590-17-014900 R5), plus capital leases of 25 in other current liabilities and 761 in other long-term liabilities. Both are verified on R102 of that filing ('Current capital lease obligations ... $25'; 'Long-term capital lease obligations ... 761') and in the R24 note text. This corrects the 53,461 failed in the first final draw.
- FY2017-26: face debt plus 'Total finance lease liabilities' from each filing's own lease note: 2,538 and 4,301 (R103), 6,574 (R101), 9,496 (R95), 12,541 (R93), 14,902 (R94), 17,067 and 27,145 (R100), 46,172 (R90), 66,594 (R92). All 10 sums equal the served value.

**History of this certificate:**
- The first sample (2026-11-13) found the total_debt perimeter error: c66e832a, corrected in 6070148d.
- The first final draw (847725da) failed on FY2016 capital leases (ca2a8b64).
- Between 847725da and 8ecdbfde, the only changed cell is total_debt FY2016 (53,461 to 54,247), which is re-checked above.
- The Verifier's independent samples are in data-team/strategy/certification/.

## Conditions and limits

1. **Locator gap to close (does not block, because the value is verified and the cell has a locator):** in the `parts` column of total_debt FY2016, the two capital-lease parts end in an empty R page (`...@0001564590-17-014900#`). Fill them with `R102`.
2. **Scope:** this certifies the evidence for the cells listed. It does not authorize any production write: the load still needs the founder's own typed words in the session that applies it (CLAUDE.md).
3. **Change control:** a change to any of these 552 cells, a proof-version bump that changes a verdict, or a new filing period voids this certificate for the affected cells until they are re-sampled.
