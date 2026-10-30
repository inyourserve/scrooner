# Verify: retirement Family B, plan 11 (work/data-engineer/derivation-gate bcc32c8; dryrun_B11_keep), 2026-10-26

Verifier 2. Seed random.Random(20261117). Files: B_proxy_form_cells.csv, B_proxy_form_scale_check.csv, B_proxy_form_proxy_only_recheck.csv, B_proxy_form_promote_facts_before_image.csv. Income statements read with the kit on main (ea51058: `select_income_statement`, `net_income_lines`, `RPage.column(months=)`, `printed_unit`), plus my own reader for 6 pages: about 90 requests, nothing on disk. Read-only DB on one connection with a 20s timeout. FILING-CHECKED unless marked.

## Result: GATE FAILS narrowly.
- **1 over-rounded value shown:** company 2993 Q4 2025 shows 18M. The nine-month input is printed "$ 60.0" in millions (0001628280-25-049844), so its unit is 0.1M, not 1M. Q4 = 77,800K - 60.0M = 17.8M.
- The plan's scale ignores printed decimals: it uses the page scale only.
- Everything else checked is right.

## 1. The 19 scale cells (inputs read on each filing's own column)
**Exact, right:**
- GIS 614.9M = 2,593.9 - 1,979.0 (attributable)
- Leggett 52.8M = 309.8 - 257.0 (attributable)
- MCD 1,903.4M
- CACC 151.9M = 247.9 - 96.0
- AKTX -5,298K = -17,298 - (-12,000), both in thousands
- company 1833: -7.9M = -365.9 - (-358.0)
- 3592: 17.2M, -21.1M, 12.2M. One 10-Q prints "(49,000,000.0)" under a "€ in Millions" header; the values reconcile.
- AXTA (3678) 43.6M = 191.6 - 148.0 (attributable)
- FTNT 526.2M
- GME 131.3M (nine months printed 0.0)

**Rounded to millions, right** (one input really is printed in whole millions):
- BAH 193,000,000 (FY 935)
- TJX 1,038,000,000 (FY 3,498)
- TDS -506M (nine months "6")
- 1559: 14M (nine months "40")
- ABNB (2929) 319M. Its FY is printed "$ 1,893,000,000" in whole dollars. The plan's 1,000,000 scale for that page comes from the header phrase "shares in Millions", so the outcome is acceptable but for the wrong reason. The kit's `multiplier` misreads the same header.

**Over-rounded: 2993, 18M against 17.8M** (above).

**Hidden: 1694 (Ambac) Q4 2022.** This is a page-parsing gap, not an unverifiable value.
- The statement is "Consolidated Statements of Total Comprehensive Income", combined (0000874501-25-000032 in thousands; 0000874501-23-000150 in millions).
- The figure is FY attributable 522,380K minus nine-month attributable 347M = 175M at the coarse unit. The stored proxy value is 175.12M.
- Also, the kit classes "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest" as `nci`. It is the NCI-inclusive total.

## 2. (a) 20 of 42 cohort proxy_only_source removals: 20 right, no false removal
- **Calendar-period duplicates whose fiscal-period cell exists with the filed value:** ONTO x4 (e.g. 2020-12-27..2022-01-01 142,349K), VFC x2 (-189,716K), DRI (1,206.7M), HAS x2. Confirmed in analytics.canonical_fact.
- **No periodic filing under that CIK for the period:** successor CIKs VNOM x3, BLK, PNFP; ALGM partial period; VAL predecessor + successor.
- **CLX FY2026 x3:** removal right, but this is still the ingestion gap (0000021076-26-000034, 0 facts).

## 3. (b) 15 of 1,019 re-promoted facts: values right
- Each re-promoted fact equals its filing's face, e.g. Caleres FY2023 attributable 171,391K (0000014707-26-000053), Fossil -157,088K / -102,671K (0000883569-26-000017), LNG FY2021 -2,343M.
- **Finding: 13 of the 15 already have an AUTHORITATIVE copy of the same value from the original filing.** Promoting the later copy leaves two authoritative facts for one (company, tag, period) until the Stage 2e dedupe re-runs (release-plan step 3).
- Confirm that dedupe collapses them, or promote only where no authoritative copy exists (true for LNG and Caleres here).

## What remains before Family B can be applied (updated)
1. Rounding unit = page scale x 10^-printed decimals (`printed_unit`), not page scale alone (2993 shows 18M, should be 17.8M). Take the scale from the money phrase, never from "shares in Millions" (ABNB). Re-verify the 19 cells.
2. Read combined "Total Comprehensive Income" statements (Ambac 1694) so a derivable quarter is shown, not hidden.
3. Kit: classify "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest" as the NCI-inclusive total, not `nci`. Take the multiplier from the money phrase only.
4. Re-promotion: avoid two authoritative copies (13/15 sampled), or show on a dry-run that Stage 2e dedupe leaves exactly one.
5. Route the CLX FY2026 ingestion gap (0000021076-26-000034). The 3 CLX cells stay removed until it lands.
6. Founder confirmation that full-year cells follow HIDE (46 proxy_filed_copies_disagree).
7. Review the apply transaction on a dry-run write with restore (1,314 demote, 1,019 promote, 7,671 metric recomputes; migration 0098 + fact_authority_retired).
8. Sample the population outside the cohort for the face-release and scale rules.
9. Record the ruling and the `--original-basis` off switch in doc 02.
10. After apply: certification (I1-I11) on the touched companies and a 10-cell live-site spot check against the filings.
