# Verify: Debt V5.2 (origin/work/scrooner-25/slot-records 46af7b7), 2026-10-25

Verifier 2. FILING-CHECKED. Seed random.Random(20261104) for the flagged draw.

## Result: GATE PASSES. All 19 published values checked are right. Flags are informational and their reasons are right; two flags can be cleared.

## Named cells
| Cell | Published | Filing | Verdict |
|---|---|---|---|
| AMAT 2023-10-29 | 5,561M | 0000006951-23-000041 R5: short-term debt 100 (commercial paper, R71) + long-term debt 5,461; R72: principal 5,500 - discount 11 - costs 28 = 5,461, earliest maturity the 3.900% notes due 2025 (no current maturities at Oct 2023) | right (my V5.1 "hold right" is superseded: zero current maturities is proven by the note) |
| COST 2025-08-31 | 5,788M | 0000909832-25-000101 R5: LTD excl. current 5,713; R50: gross 5,805 - discounts/costs 17 = 5,788 carrying, current portion 75 (inside other current liabilities), R51 maturities 2025 = 75 | right; the "unreconciled" flag can be cleared: 5,805 - 17 - 75 = 5,713 exactly |
| MA 2017-12-31 | 5,424M | 0001141391-18-000009 R2/R72: LTD 5,424, maturities in next twelve months 0 | right |
| CVX 2024-12-31 | 24,541M lease-incl. / 23,995M borrowings | 0000093410-25-000009 R5 4,406 + 20,135 (incl. finance leases 546); R107 short-term debt already holds current maturities 4,012 net of the 8,250 reclass | right (lane3 32,791 double-counts the reclass) |

## 15 flagged cells (frame 143 flagged cells since 2015 at LRCX, UNH, WMT, CSCO, COST, INTC, CVX; max 3 per company)
| Cell | Face (R page) | Published | Flag reason | Verdict |
|---|---|---|---|---|
| CSCO 2026-01-24 | 8,719 + 21,367 (0000858877-26-000021 R2) | 30,086 | note LongTermDebt excludes CP | right / reason right |
| CSCO 2022-01-29 | 2,502 + 8,969 (0000858877-22-000004 R2) | 11,471 | same | right |
| CSCO 2017-01-28 | 4,451 + 30,471 (0000858877-17-000004 R2) | 34,922 | same | right |
| CVX 2019-12-31 | 3,282 + 23,691 incl. finance leases 282 (0000093410-20-000010 R5; R94 current maturities inside STD) | 26,973 / borrowings 26,691 | note vs face reclass | right |
| CVX 2015-06-30 | 2,621 + 29,210 + capital leases 79 (0000093410-15-000031 R5) | 31,910 / 31,831 | same | right |
| LRCX 2021-09-26 | 6,368 + 4,988,964K debt and finance leases (0000707549-21-000155 R4); note carrying 4,961,249K (R59) | 4,995,332K lease-incl.; borrowings variant 4,995,332K | lease perimeter | lease-incl. right; borrowings variant WRONG if shown (should be 4,961,249K) - keep it informational |
| LRCX 2021-03-28 | 825,434 + 4,991,613K (0000707549-21-000089 R4); note 5,774,263K (R60) | 5,817,047K both | same | lease-incl. right; borrowings variant wrong if shown |
| LRCX 2023-06-25 | 8,358 + 5,003,183K (0000707549-23-000102 R5); note 4,965,365K (R81) | 5,011,541K / 4,965,365K | same | both right |
| COST 2022-02-13 | 0 + 6,658 (0000909832-22-000005 R4; R29 face value 6,694 - 36) | 6,658 | principal vs carrying | right |
| COST 2019-05-12 | 1,699 + 4,799 (0000909832-19-000013 R2; R31 6,529 - 31) | 6,498 | same | right |
| COST 2021-02-14 | 95 + 7,522 (0000909832-21-000003 R4; R32 7,661 - 44) | 7,617 | same | right |
| INTC 2018-12-29 | 1,261 (CP 500 + current 761, R77) + 25,098 (0000050863-19-000007 R4) | 26,359 | CP | right |
| INTC 2016-04-02 | 3,594 (CP 921 + current 2,606 - costs 8, R65) + 21,775 (0000050863-16-000125 R4) | 25,369 | CP | right |
| UNH 2017-12-31 | 2,857 + 28,835 (0000731766-18-000005 R2) | 31,692 | aggregate (CP inside the combined line) | right |
| WMT 2020-07-31 | borrowings 357 + 5,553 + 40,959; finance leases 549 + 4,673 (0000104169-20-000042 R4) | 46,869 / 52,091 | both perimeters | right |

## Notes
- LRCX's borrowings variant equals the lease-inclusive face sum in eras whose face line combines debt and finance leases (2021-03-28, 2021-09-26); it is wrong as a borrowings figure. Do not surface it; use the note carrying total when a borrowings value is needed.
- The COST flag rule should accept "gross - unamortized - current = noncurrent" as a reconciliation.
