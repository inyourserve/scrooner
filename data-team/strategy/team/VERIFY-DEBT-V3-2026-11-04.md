# VERIFY: total debt v3, finance leases included (2026-11-04)
Branch work/cash-flow/da-capex fd88e43, pipeline/scripts/slot_records/results/debt_fsn_pilot_v1/report_v3.json. Seed 20261104 over `prod_differs`: 5 MSFT, 5 HD (HD 2016-01-31 forced), 2 KO, 2 AAPL/META. Verifier 2 (scrooner-bc). 130 SEC requests (pilot v1 reads included).

## Result: YES, 14 of 14 right
- **Borrowings tie to the face in all 14.** Each slot borrowings figure equals the sum of the printed balance-sheet debt lines:
  - MSFT 2025-03-31: 2,999 + 39,882 = 42,881.
  - HD 2016-01-31: 350 + 77 + 20,888 = 21,315. Production shows 427 and omits long-term debt.
  - KO 2015-03-31: 14,383 + 2,040 + 26,087 = 42,510. Production shows 28,127 and omits loans and notes payable.
  - AAPL 2020-09-30: 4,996 + 8,773 + 98,667 = 112,436.
  - META 2023-12-31: 18,385.
- **Finance leases equal the note total in 7 of 7.** MSFT 39,214 / 4,301 / 8,610 / 11,518 / 15,584 match "Total finance lease liabilities" (Supplemental Balance Sheet Information). AAPL 661 = 24 + 637 (ROU Assets and Lease Liabilities). META 690 = present value 90 + 600 (Maturities of Lease Liabilities). Every one is filed in other or accrued liabilities, so adding it does not double-count.
- **HD:** finance leases are already inside the face debt lines, and v3 adds nothing from the note. HD 2024-01-31: face 1,368 + 42,743 = 44,111 = slot lease-inclusive. Borrowings are 40,843, and the 3,268 gap equals finance lease liabilities 268 + 3,000 in the lease note.
- **KO "Loans and notes payable": YES, it is debt.** The Debt and Borrowing Arrangements note shows commercial paper of 4,040 out of 4,379 (2025-06-30) and 250 out of 332 (2026-03-31). The rest is short-term bank loans.
- **AMZN custom lease elements (pilot v1 question): NO, keep them out.** The face line "Long-term lease liabilities" (78,277 at 2024-12-31) combines operating and finance leases. Operating leases are not debt (decision 27, Decision 3). Take the finance-lease part from the note, the way MSFT/AAPL/META are handled. v2 holding AMZN as `debt_lease_member_unverified` is right.

## Findings for the builder
1. MSFT records list `OperatingLeaseLiabilityNoncurrent` as a member, yet its value is correctly left out of both totals. Drop it from the member list so a later code path cannot add it.
2. AMZN: build from LongTermDebtNoncurrent + the note's current portion (5,017 at 2024-12-31) + FinanceLeaseLiability from the lease note. Re-verify once built.

## Untested scope
JNJ, GOOG, NVDA, PG not drawn. META `prod_blank` (29) and `current_maturities_unverified` (22) were not drawn.
