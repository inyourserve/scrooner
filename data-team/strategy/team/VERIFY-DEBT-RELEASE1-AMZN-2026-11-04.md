# VERIFY: debt release 1, AMZN cells (2026-11-04)
Branch work/cash-flow/da-capex 4af9a25, results/release_debt_1/debt_release1_updates.jsonl (46 AMZN cells). Seed 20261104, 3 cells, FY2023 forced. Verifier 2 (scrooner-bc). 86 SEC requests.

## Result: YES, 3 of 3 right
| Cell | Borrowings (face LTD + note current portion) | Finance leases (note) | Release value |
|---|---|---|---|
| 2023-12-31, 0001018724-24-000008 | 58,314 + 8,494 = 66,808 | PV of finance leases 12,109 (Operating and Finance Lease Reconciliation) | 78,917 |
| 2020-03-31, 0001018724-20-000010 | 23,437 + 1,311 = 24,748 | PV of finance leases 26,319 | 51,067 |
| 2018-06-30, 0001018724-18-000108 | 24,638 + 31 = 24,669 | capital lease obligations, current 6,600 + noncurrent 9,000 = 15,600 (Commitments and Contingencies, Principal Contractual Obligations) | 40,269 |

- 12,109 is the right FY2023 figure. The 10,077 inside the face "Long-term lease liabilities" (77,297) is only the NONCURRENT finance portion. The current 2,032 sits in accrued expenses.
- Production's 67,329 / 24,849 / 24,770 is face value of debt and leaves out finance leases.

## Findings for the builder
1. The 2018 capital lease figure comes from a $0.1B-rounded footnote, so it has a ±50M rounding range. AMZN's pre-2019 filings print no capital-lease line on the balance sheet. Label these cells "rounded source" if the UI shows precision.
2. Financing obligations (build-to-suit) are not added. That is in line with option (b), which covers finance leases only.
