# Verify: verifier kit live test 2 (origin/verifier-kit 7f1524c), 2026-10-26

Verifier 2. Same 25 hand-checked balance-sheet instants, run through the kit's own `fetch_statements` + `face_liabilities` (unmodified copy; my rate-limited client with SEC_USER_AGENT; 52 requests; nothing written to disk). Manifest: pipeline/tests/verification/fixtures/live_25.json. FILING-CHECKED.

**Result: 23 of 25 reproduced. 2 failures, both in face_liabilities.**
- One error was mine: in run 1 the BBIO instant was wrong. 0001743881-25-000012 is the Q3 2025 10-Q; the hand value 2,920,979,000 is the 2025-09-30 column, and the kit reproduces it. The manifest now has that instant.
- All 4 previous failure classes are fixed: report selection, element-suffixed numbers and [1] footnotes (JPM, HRL 2015, VMI), the L&E label variants (CAH, RYN, EPD, AWK, TYL, IDACORP 2023), and combined filings (DUK x2 now 81,768 / 113,204, DTE x2, LAMR).
- AWK's capitalization layout is now right: redeemable preferred stays inside debt (14,097 / 12,553 / 12,192). XEL is footed from its "Common stock" equity line (33,765). KHC mezzanine is right (20,761).

**Failures:**
1. IDACORP 2020-03-31 (0001057877-20-000138 R4): kit 4,174,571 vs face 4,136,679.
   - Correct reading: IDACORP block, "Total" 6,609,950 - "Total equity" 2,473,271.
   - The kit took 6,453,701 - 2,279,130 (the Idaho Power block below).
   - Cause: this 10-Q uses a bare "Total" both for total assets and for total L&E, so the first-registrant cut lands on the wrong "Total" row.
   - Fix: take the first bare "Total" that FOLLOWS an equity total, or match the L&E by value to the first "Total assets"/"Total" figure.
2. LDOS 2016-12-30 (0001336920-17-000014 R2): kit "no total equity line" vs face 5,985.
   - The face prints "Total liabilities and stockholders' equity" 9,132 BEFORE the stockholder's-equity section, then "Total equity" 3,147 (incl. NCI 12) and "Total stockholder's equity" 3,135.
   - Cause: the block is cut at the first L&E row, so the equity rows below it are never searched.
   - Fix: when no equity total precedes the L&E row, look in the rows between the L&E row and the next statement block or "Total assets".

**Use from now on:** yes. For balance-sheet face reading I will use the kit at 7f1524c. Wherever it returns "unavailable", or disagrees with the builder, I hand-read the cell and count those cells in each verdict.
