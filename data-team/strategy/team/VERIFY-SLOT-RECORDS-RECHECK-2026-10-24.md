# Verifier recheck: six re-emitted slot records (origin/work/scrooner-25/slot-records @56c4a1a), 2026-10-24

Role: Data Verifier. Read-only, no DB. SEC access: `SEC_USER_AGENT` only, at most 4 req/s through the shared limiter; downloads deleted afterwards. All evidence FILING-CHECKED.

**Verdict:**
- **The six records are right.** MU's 3 era records and the GOOG 2015-09 / 2016-03 / 2016-06 cells now carry the correct class labels, and their member sets and era boundaries are unchanged from the run I filing-checked earlier.
- **One rule-level finding:** `COMBINED_TAGS` labels every `DebtCurrent` as `combined` from the tag name alone. At four companies in our total-debt samples, the filings show no lease part inside that line, so the label is applied blindly there.

## 1. The six records
| Record | Members (unchanged) | New class | Filing evidence | Verdict |
|---|---|---|---|---|
| MU era 0 (2014-12-04..2019-08-29, 20 filings) | DebtCurrent, LongTermDebtAndCapitalLeaseObligations | both combined | FY2019 10-K 0000723125-19-000094 R79: the debt schedule includes "Capital lease obligations"; current total 1,310 contains FinanceLeaseLiabilityCurrent 223 | right |
| MU era 1 (2019-11-28..2026-05-28, 27) | same + OperatingLeaseLiabilityNoncurrent (operating_lease, excluded) | both combined | 10-K 0000723125-21-000065 R4: "Current debt" 155 = FinanceLeaseLiabilityCurrent 155; "Long-term debt" 6,621 includes noncurrent finance leases 649 | right |
| MU era 2 (2026-09-03, 1) | DebtCurrent, LTD&CLO | both combined | 10-K 0000723125-26-000023 R4 (491 + 4,688; finance-lease facts at the date) | right |
| GOOG 2015-09-30 | DebtCurrent, LTD&CLO | both combined | 10-Q 0001652044-15-000005 R2: "Short-term debt" 3,237 includes CapitalLeaseObligationsCurrent 238 | right |
| GOOG 2016-03-31 | same | both combined | 10-Q 0001652044-16-000021 R2: 3,221 includes 223 | right |
| GOOG 2016-06-30 | same | both combined | 10-Q 0001652044-16-000032 R2: 2,219 includes 220 | right |

Member sets: 0 differences across all 51 MU lines (48 observations + 3 eras). Era boundaries are identical (period_from / period_to). The GOOG members are identical to the replay cells checked earlier.

## 2. Is `combined` applied only where a lease part exists? No: it is applied by tag name
The new rule labels `DebtCurrent` combined whenever the tag appears, not when the filing shows a lease part. I checked the filings of the companies whose face line is `DebtCurrent`, using two sources:
- the same-date lease facts;
- the 10-K's lease-location rows (the "[Extensible Enumeration]" balance-sheet location of each lease liability).

| Company (10-K) | Face line on `DebtCurrent` | Lease part shown inside it? | Should be |
|---|---|---|---|
| MU (0000723125-21-000065) | "Current debt" | yes: FinanceLeaseLiabilityCurrent 155 = DebtCurrent 155 | combined |
| GOOG 2015-16 | "Short-term debt" | yes: current capital leases 238 / 223 / 220 | combined |
| MRK (0001628280-24-006850, 2023-12-31) | "Loans payable and current portion of long-term debt" 1,372 | **no**: no finance-lease fact; the operating-lease location is "Accrued and other current liabilities" (R78) | borrowing |
| INTC (0000050863-24-000010, 2023-12-30) | "Short-term debt" 2,288 | **no** finance-lease fact at the date; only an operating-lease location (R83) | borrowing |
| CSCO (0000858877-25-000111, 2025-07-26) | "Short-term debt" 5,232 | **no** finance-lease fact; operating leases in other current / long-term liabilities (R82) | borrowing |
| UNH (0000731766-24-000081, 2023-12-31) | "Short-term borrowings and current maturities of long-term debt" 4,274 | **no** lease fact at the date | borrowing |
| KO, ABBV | not DebtCurrent (KO `NotesAndLoansPayableCurrent`; ABBV `LongTermDebtAndCapitalLeaseObligationsCurrent`, whose face label names finance leases) | ABBV yes, KO no | unaffected by `COMBINED_TAGS` |

What this does: the over-labelling does not produce a wrong value, because combined lines are never mapped as either side alone. But a borrowings-only figure can never be produced for MRK, INTC, CSCO or UNH, and any rule that holds or blanks combined lines would hide correct values there.

**To the owner (scrooner-25):** keep `combined` for `DebtCurrent` / `DebtNoncurrent` only when a same-instant finance or capital lease fact exists and is located in that line. The evidence can be the filer's calc child, the lease-location extensible-list value, or the arithmetic (lease fact ≤ line, and the borrowing parts alone do not explain the line). Otherwise label it `borrowing`. With that change I have nothing open on these records.
