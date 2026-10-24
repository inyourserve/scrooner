# Verifier sample: total-debt fix V4 (branch lane3-total-debt @6ac6f59), 2026-10-24

Role: Data Verifier.

Inputs:
- `scratchpad/debt_v4_PILOT_lease_inclusive.jsonl` (227 changed).
- `scratchpad/debt_v4_MORE _lease_inclusive.jsonl` (the filename contains a space): 410 changed at 23 of 30 more cohort companies.

DB use: one light read (one connection, 20s, 6 backends) for the stored AAPL 2019-09-28 and KO 2019-12-31 totals.

Evidence:
- Balance-sheet R page of the filing for each instant (face line, tag, value).
- That filing's own facts through SEC companyconcept for note-only lines.
- All FILING-CHECKED unless marked.

Seed: `random.Random('20261024-v4')`.

**Verdict: GATE FAILS.**
- All 7 named cells are right.
- 4 of 19 verified shown cells from the 30-company scan are wrong, from 2 mechanisms (ABBV x2, CVX x2).
- 8 of the 20 reviewed holds are false holds: the stored value was right. 7 of them come from one cause, a face-line DebtCurrent whose parts are not separately tagged.

## 1. Named cells
| Cell | Shown | Filing | Verdict | Locator |
|---|---|---|---|---|
| AAPL 2019-09-28 | 108,047M (stored, unchanged) | CP 5,980 + term debt 10,260 + 91,807 (pre-ASC 842, no finance leases) | right | 10-K 0000320193-19-000119 R4 |
| AAPL 2020-03-28 | 110,155M | CP and repurchase agreement 10,029 (`OtherShortTermBorrowings`) + 10,392 + 89,086 + finance leases 648 | right | 10-Q 0000320193-20-000052 R4 |
| AAPL 2020-06-27 | 113,373M | 11,166 + 7,509 + 94,048 + 650 | right | 10-Q 0000320193-20-000062 R4 |
| NVDA 2015-01-25 | 1,401,842K | face LongTermDebt 1,384,342K + capital leases 14,086K + 3,414K | right (precise copy now used) | 10-K 0001045810-15-000036 R5 |
| AVGO 2025-11-02 | 65,136M (nd) | short-term debt 3,152 + LTD 61,984 (= filed LongTermDebt 65,136; the 67,120 "combined" fact is principal) | right; label honest | 10-K 0001730168-25-000121 R3 |
| GOOG 2023-12-31 | 12,870M "incomplete" | notes 11,870 + current 1,000; only the noncurrent lease half (1,383) is authoritative | right; label honest | 10-K 0001652044-24-000022 R3 |
| KO 2019-12-31 | 42,763M (stored, unchanged) | Notes and loans payable 10,994 (contains OtherShortTermBorrowings 987, not double counted) + current maturities 4,253 + LTD 27,516 | right | 10-K 0000021344-20-000006 R4 |

## 2. Twenty shown cells from the 30-company scan (frame 319 shown, excluding named)
| Cell | Shown | Filing | Verdict | Locator |
|---|---|---|---|---|
| **CVX 2015-03-31** | **33,868M** (r1 path) | ST debt 3,908 + LTD 29,960 + **capital lease obligations 65** | **WRONG**: misses the noncurrent capital-lease face line (lease-inclusive default) | 10-Q 0000093410-15-000020 R5 |
| **CVX 2014-09-30** | **25,625M** (r1) | 5,665 + 19,960 + **capital leases 84** | **WRONG**, same (pre-2015) | 10-Q 0000093410-14-000049 R5 |
| **ABBV 2022-03-31** | **73,462M** (lease-inclusive face lines) | **short-term borrowings 12** + current debt and finance leases 9,940 + 63,522 = 73,474 (= stored) | **WRONG**: drops the short-term borrowings line | 10-Q 0001551152-22-000017 R5 |
| **ABBV 2017-12-31** | **36,968M** (filer DebtAndCapitalLeaseObligations) | **short-term borrowings 400** + 6,015 + 30,953 = 37,368 (= stored) | **WRONG**, same | 10-K 0001551152-18-000014 R5 |
| LRCX 2016-09-25 | 4,331,178K | 952,999 + 3,378,179 (convertible notes in temporary equity excluded) | right | 10-Q 0000707549-16-000085 R4 |
| LRCX 2017-03-26 | 2,682,585K | 905,288 + 1,777,297 | right | 10-Q 0000707549-17-000056 R4 |
| UNH 2018-06-30 | 35,055M | 2,959 + 32,096 | right | 10-Q 0000731766-18-000030 R2 |
| UNH 2023-12-31 | 62,537M | 4,274 + 58,263 | right | 10-K 0000731766-24-000081 R3 |
| CSCO 2016-07-30 | 28,643M | 4,160 + 24,483 | right | 10-K 0000858877-16-000117 R2 |
| MRK 2019-12-31 | 26,346M | 3,610 + 22,736 | right | 10-K 0000310158-20-000005 R4 |
| MRK 2020-09-30 | 28,741M | 2,420 + 26,321 | right | 10-Q 0000310158-20-000030 R4 |
| MRK 2022-03-31 | 31,794M | 1,208 + 30,586 | right | 10-Q 0000310158-22-000011 R4 |
| MRK 2023-09-30 | 34,859M | 887 + 33,972 | right | 10-Q 0001628280-23-036717 R4 |
| INTC 2015-12-26 | 22,670M | 2,634 + 20,036 | right | 10-K 0000050863-16-000105 R4 |
| INTC 2019-12-28 | 29,001M | 3,693 + 25,308 | right | 10-K 0000050863-20-000011 R4 |
| WMT 2017-04-30 | 46,497M | 2,617 + 3,256 + 33,774 + capital lease and financing obligations 599 + 6,251 | right | 10-Q 0000104169-17-000029 R4 |
| WMT 2021-10-31 | 43,016M | 447 + 1,575 + 36,425 + finance leases 508 + 4,061 | right | 10-Q 0000104169-21-000072 R4 |
| WMT 2010-10-31 | 56,794M | facts: 7,352 + 5,196 + 40,803 + 347 + 3,096 | right (pre-2015; face not rendered, filing facts) | WMT 10-Q for 2010-10-31 (facts) |
| WMT 2010-01-31 | 41,320M | facts: 523 + 4,050 + 33,231 + 346 + 3,170 | right (pre-2015, facts) | WMT 10-K FY2010 (facts) |
| JNJ 2011-01-02 | 16,756M | no R pages for this 10-K; facts: ShortTermBorrowings 7,617 vs DebtCurrent 7,600 | NOT-VERIFIED (pre-2015) | 10-K 0000950123-11-018128 |

Mechanisms of the 4 wrong cells:
- **(a) ABBV:** the lease-inclusive face-line path (and the filer aggregate `DebtAndCapitalLeaseObligations`) omits a separate `ShortTermBorrowings` face line. In both cases the stored value was right.
- **(b) CVX:** the legacy r1_containment path does not add the noncurrent `CapitalLeaseObligationsNoncurrent` face line under the lease-inclusive default.

## 3. Twenty of the 91 value-to-blank cells (14 of the 43 "current total not explained by its filed parts", 6 others)
| Cell | Stored | Face | Verdict | Locator |
|---|---|---|---|---|
| MRK 2013-12-31 | 25,060M | DebtCurrent "Loans payable and current portion of LTD" 4,521 + LTD 20,539 = 25,060 | **FALSE HOLD** | 10-K 0000310158-14-000009 R4 |
| MRK 2014-12-31 | 21,403M | 2,704 + 18,699 | **FALSE HOLD** | 10-K 0000310158-15-000005 R4 |
| INTC 2012-03-31 | 7,450M | "Short-term debt" 362 (CP 273 + untagged rest) + 7,088 | **FALSE HOLD** | 10-Q 0001193125-12-212253 R4 |
| INTC 2024-06-29 | 53,029M | 4,695 (CP 3,200 + untagged) + 48,334 | **FALSE HOLD** | 10-Q 0000050863-24-000124 R4 |
| UNH 2023-06-30 | 65,589M | "Short-term borrowings and current maturities" 6,321 (CP 4,400 + untagged) + 59,268 | **FALSE HOLD** | 10-Q 0000731766-23-000053 R2 |
| UNH 2023-09-30 | 63,369M | 5,290 (CP 2,600 + untagged) + 58,079 | **FALSE HOLD** | 10-Q 0000731766-23-000064 R2 |
| UNH 2024-03-31 | 73,637M | 9,787 (CP 7,300 + untagged) + 63,850 | **FALSE HOLD** | 10-Q 0000731766-24-000155 R2 |
| CSCO 2017-04-29 | 30,470M (LongTermDebt) | "Short-term debt" 4,248 + LTD 28,222 = 32,470 | hold right (stored wrong); face total reachable | 10-Q 0000858877-17-000010 R2 |
| CSCO 2019-04-27 | 20,415M | 7,777 + 15,921 = 23,698 | hold right; reachable | 10-Q 0000858877-19-000007 R2 |
| CSCO 2024-10-26 | 20,117M | 12,364 + 19,623 = 31,987 | hold right; reachable | 10-Q 0000858877-24-000030 R2 |
| CSCO 2025-04-26 | 25,105M | 6,422 + 22,857 = 29,279 | hold right; reachable | 10-Q 0000858877-25-000033 R2 |
| CSCO 2025-10-25 | 24,613M | 6,725 + 21,364 = 28,089 | hold right; reachable | 10-Q 0000858877-25-000171 R2 |
| CSCO 2026-07-25 | 22,872M | 10,161 + 19,372 = 29,533 | hold right; reachable | 10-K 0000858877-26-000132 R3 |
| CSCO 2011-01-29 | 27,393M | no rendered face (old R format) | NOT-VERIFIED (pre-2015) | - |
| UNH 2015-12-31 (r7) | 6,634M (current only) | 6,634 + LTD 25,460 = 32,094 | hold right | 10-K 0000731766-16-000058 R2 |
| PG 2015-06-30 (r7) | 11,579M | "Debt due within one year" 12,021 + 18,329 = 30,350 | hold right | 10-K 0000080424-15-000070 R5 |
| ORCL 2012-11-30 (r5) | 1,250M | 1,250 + 18,507 = 19,757 | hold right (pre-2015) | 10-Q 0001193125-12-513009 R2 |
| LRCX 2021-12-26 (related-party/debt-only rule) | 4,961,645K (LongTermDebt) | lease-inclusive face lines 6,201 + 4,988,121 = 4,994,322K | hold right (stored wrong); avoidable: both face lines share one perimeter | 10-Q 0000707549-22-000012 R4 |
| GE 2015-10-09 (r7) | 2,000M | no periodic filing has this period end (a note-date instant) | hold right: not a reporting date | - |
| AMAT 2010-08-01 (r5) | 206M | facts 1.848 + 204.438 = 206.3M (face not rendered) | likely FALSE HOLD (right within rounding; pre-2015; DATA-INFERRED face) | - |

**Cause of the 7 false holds (and of the 6 CSCO holds whose correct value is reachable): not a vocabulary gap.** In each case `DebtCurrent` is itself the face line: "Loans payable and current portion of long-term debt", "Short-term debt", "Short-term borrowings and current maturities". The filer tags only part of it (commercial paper, or nothing) and leaves the current-maturity part untagged at that instant. The parts test then cannot explain the face line. Proposed rule: accept `DebtCurrent` when it is presented on the balance sheet (presentation linkbase or face R page). Keep the parts test for note-only DebtCurrent (the TSLA case). This turns the 7 false holds into shown values equal to the stored ones, and shows the CSCO face totals.

## Tally
| | Checked | Right | Wrong | Not verified |
|---|---|---|---|---|
| Named cells | 7 | 7 | 0 | 0 |
| Shown, 30-company scan | 20 | 15 | **4** (ABBV x2, CVX x2) | 1 (JNJ 2011) |
| Holds reviewed | 20 | 10 correct holds | **8 false holds** (7 FILING-CHECKED + AMAT DATA-INFERRED) | 2 (CSCO 2011; GE non-period instant counted as a correct hold) |

## To the owner (lane 3)
1. Add a separate `ShortTermBorrowings` face line in the lease-inclusive face-line and filer-aggregate paths (ABBV).
2. Add the noncurrent capital-lease face line to the r1_containment path under lease_inclusive, or route those cells through r8 (CVX).
3. Accept a face-presented `DebtCurrent` as the current block without part reconciliation (MRK, INTC, UNH false holds; CSCO reachable totals).
4. Treat LRCX-type pairs as lease-inclusive face lines when the debt-only subtotal equals the borrowings inside them.
5. Then a fresh sample. Releasing this version is not yet supported.
