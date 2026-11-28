# Verdict: cohort request top100-9f9397e4059e (2026-11-29): FAIL

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Stage 5 Certify, M3.
Request: `requests/top100-cohort-request-2026-11-29.md` (8d3930898). Coverage sha256 `5899d7d9625ed9a153dfed8f7d18da25b88169bec0809ff980784fc85a91e7a6`, judge `cohort_cert@1+draw_check@3`.

## Verdict: FAIL, on the census

The request's own census reports 2,130 FAIL rows across the 96 companies, with OPEN cells (1,513) the largest family. A shown cell that is OPEN is not a proven value or an evidenced hide (founder 2026-11-16), and under the certification method (CERTIFICATION-METHOD-2026-11-16.md) any census FAIL fails the certificate, whatever the sample shows. The 136 debt and other REVIEW rows would also block a PASS.

The sample result (0 wrong of 598, 95% upper bound 0.4997%, 20 reads by scrooner-data-verifier all MATCH) is noted. It does not change the verdict, and I have not re-run it, because the census decides.

## No cohort certificate is issued, and the per-company registry is unchanged

- A single cohort certificate that "replaces per-company certification" is a change of method. Neither doc 02 nor the certification method records it. It reached the approver only relayed by a peer session ("everything is approve"). Until the founder's decision is recorded in doc 02 with the founder's own words, certification stays per company: one coverage sha per company, n = 199, census plus sample, one `registry.csv` row per ticker.
- The registry has no cohort row type. `registry.csv` is unchanged by this verdict.
- When the method is recorded, a cohort draw can serve as the sample for each company in it. The census still has to pass per company, and the registry row stays per ticker. A cohort-wide PASS can't cover a company whose own cells fail.

## What moves a company to PASS fastest

1. File a per-company request (`requests/<T>-request-<date>.md`, coverage sha) for each company whose census is clean. I'll draw them in batches as they land.
2. The checker false positives f1 flagged (C cash, AXP deposits, QCOM custom tag) are census rule work. Each should become a fix in display_cert or draw_check, with a test that fails without it, under the stage 4/5 owner. They are not grounds to pass a company over a FAIL.
