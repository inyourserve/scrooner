# Verifier confirmation sample: total-debt fix v3 (branch lane3-total-debt @8d9e080), 2026-10-24

Role: Data Verifier. Input: `scratchpad/debt_slots4_lease_inclusive.jsonl` (default perimeter, 215 changed instants at the first 10 cohort companies). No DB use.

Evidence:
- The balance-sheet R page of the filing for each instant (FILING-CHECKED).
- That filing's own facts through SEC companyconcept for lines inside notes: current maturities, finance or capital lease liabilities.

**Verdict: GATE FAILS. It does not pass, so do not start the population dry-run yet.**
- 2 shown values are wrong: AAPL 2020-03-28 and 2020-06-27. Both miss the face line "Commercial paper and repurchase agreements", tagged `OtherShortTermBorrowings`.
- 1 shown value has a precision defect: NVDA FY2015 uses a rounded convertible-notes fact instead of the face line in thousands.
- Every cell named in the brief is now right or correctly held. No false holds were found.

## 1. Cells named in the brief
| Cell | Fix v3 | Filing | Verdict | Locator |
|---|---|---|---|---|
| TSLA 2018-09-30 | hold (stored 8,665,163K) | 2,106,538 + 9,669,879 + related-party convertible 2,634 = 11,779,051K | **hold right** (stored wrong) | 10-Q 0001564590-18-026353 R2 |
| GOOG 2015-09-30 | resolves = stored 5,231M (unchanged) | short-term debt 3,237 (incl. capital leases 238) + LTD 1,994 | right; earlier false hold removed | 10-Q 0001652044-15-000005 R2 |
| GOOG 2016-03-31 | 5,208M | 3,221 + 1,987 | right | 10-Q 0001652044-16-000021 R2 |
| GOOG 2016-06-30 | 4,203M | 2,219 + 1,984 | right | 10-Q 0001652044-16-000032 R2 |
| GOOG 2018-03-31 | hold (stored 5,273M) | 1,329 + 3,973 = 5,302 lease-inclusive; borrowings 5,244; stored matches neither | **hold right** | 10-Q 0001652044-18-000016 R2 |
| MU 2021-09-02 | 6,776M | "Current debt" 155 + "Long-term debt" 6,621 (lease-inclusive; DebtCurrent 155 = current finance lease) | right | 10-K 0000723125-21-000065 R4 |
| NVDA 2015-01-25 | 1,401.5M = 1,384 + 17.5 | face "Long-term Debt" 1,384,342K + capital leases 14,086K + 3,414K = **1,401,842K** | **precision defect**: 0.34M (0.02%) short because the rounded `ConvertibleDebtNoncurrent` 1,384M replaces the face `LongTermDebt` 1,384,342K of the same filing (ledger rule: a rounded copy never replaces a precise one). Counted wrong | 10-K 0001045810-15-000036 R5 |
| GOOG 2023-12-31 | 12,870M "finance leases not determined" | notes 11,870 + current 1,000 = 12,870 (borrowings right). The noncurrent finance lease 1,383 is authoritative; only the current half (363 vs 283) and the 13,253 line are conflicted copies | number right as borrowings; **label imprecise**: leases are partly determined. Suggested label: "finance leases incomplete (current portion in conflict)". Not counted wrong | 10-K 0001652044-24-000022 R3 |

## 2. Fifteen new random shown cells
Frame: 154 shown instants not checked in either earlier report, plus all MU rows for the MU draw. Seed `random.Random('20261024-v3')`: one forced pick each for MU, AVGO, AMZN and MSFT, then 11 random.

| # | Cell | Shown | Filing | Verdict | Locator |
|---|---|---|---|---|---|
| 0 | MU 2024-02-29 | 13,722M | 344 + 13,378 (lease-inclusive) | right | 10-Q 0000723125-24-000007 R4 |
| 1 | AVGO 2019-08-04 | 37,565M (nd) | 3,537 + 34,028 | right | 10-Q 0001730168-19-000118 R2 |
| 2 | AMZN 2018-09-30 | 40,328M | LTD 24,684 + current 44 + capital leases 6,900 + 8,700 | right (pre-842 capital leases; built-to-suit financing obligations not included: perimeter note) | 10-Q 0001018724-18-000159 R6 |
| 3 | MSFT 2024-12-31 | 81,047M | 0 + 5,248 + 39,722 + finance leases 36,077 | right | 10-Q 0000950170-25-010491 R4 |
| 4 | AMZN 2016-03-31 | 15,709M | 8,219 + 90 + 3,200 + 4,200 | right | 10-Q 0001018724-16-000227 R7 |
| 5 | MSFT 2019-09-30 | 77,360M | 3,017 + 66,478 + 7,865 | right | 10-Q 0001564590-19-037549 R4 |
| 6 | AMZN 2012-12-31 | 4,955M | 3,084 + 579 + 555 + 737 | right (pre-2015) | 10-K 0001193125-13-028520 R7 |
| 7 | AAPL 2023-12-30 | 108,040M (nd) | 1,998 + 10,954 + 95,088 | right | 10-Q 0000320193-24-000006 R4 |
| 8 | MSFT 2020-03-31 | 75,220M | 3,748 + 62,862 + 8,610 | right | 10-Q 0001564590-20-019706 R4 |
| 9 | AVGO 2025-11-02 | 65,136M (leases 0) | short-term 3,152 + LTD 61,984 | right as a number; "finance_leases=0" has no lease fact behind it (zero not proven), so the label should be "not determined" | 10-K 0001730168-25-000121 R3 |
| 10 | TSLA 2013-03-31 | 455,538K | 50,841 + 388,785 + 5,452 + 10,460 | right (pre-2015) | 10-Q 0001193125-13-212354 R2 |
| 11 | AVGO 2025-02-02 | 66,579M | short-term 5,653 + LTD 60,926 (lease-inclusive face lines) | right | 10-Q 0001730168-25-000021 R2 |
| 12 | **AAPL 2020-06-27** | **102,207M** | "Commercial paper and repurchase agreements" **11,166** (`OtherShortTermBorrowings`) + term debt 7,509 + 94,048 + finance leases 650 = **113,373M** | **WRONG**: omits the short-term borrowing line | 10-Q 0000320193-20-000062 R4 |
| 13 | MSFT 2023-06-30 | 64,304M | 5,247 + 41,990 + 17,067 | right | 10-K 0000950170-23-035122 R4 |
| 14 | MSFT 2025-06-30 | 89,323M | 0 + 2,999 + 40,152 + 46,172 | right | 10-K 0000950170-25-100235 R4 |

## 3. Same mechanism, found by following #12 (not part of the random draw)
AAPL `OtherShortTermBorrowings` is filed at three instants: 2019-09-28 (5,980M), 2020-03-28 (10,029M) and 2020-06-27 (11,166M).
- **2020-03-28 is shown as 100,126M**, also without the 10,029M line: **WRONG**. The 10,029M value is the SEC companyconcept fact at 2020-03-28 (the Q2 FY2020 10-Q). I did not open its R page, so this is DATA-INFERRED for the face read, but the mechanism is FILING-CHECKED at 2020-06-27.
- 2019-09-28 is not changed by the fix. Whether its stored value includes the 5,980M line is UNTESTED.

## Tally (this round)
| | Checked | Right | Wrong | Other |
|---|---|---|---|---|
| Shown values, named cells (GOOG x3 stored, MU, NVDA, GOOG 2023) | 6 | 5 | 1 (NVDA precision) | GOOG 2023 label imprecise |
| Shown values, random | 15 | 14 | 1 (AAPL 2020-06-27) | AVGO 2025-11-02 label (zero not proven) |
| Shown values, mechanism follow-up | 1 | 0 | 1 (AAPL 2020-03-28, DATA-INFERRED face) | |
| Holds | 2 (TSLA 2018-09, GOOG 2018-03) | 2 correct | 0 false holds | |

## To the owner (lane 3)
1. Add `OtherShortTermBorrowings` (and any short-term borrowing tag found on the face) to the short-term slot. Re-test AAPL 2019-09-28, 2020-03-28 and 2020-06-27.
2. Prefer the most precise copy of the same line: NVDA FY2015 face `LongTermDebt` 1,384,342K over the rounded `ConvertibleDebtNoncurrent` 1,384M.
3. Labels: never write finance_leases=0 without a filed zero (AVGO FY2025). Use "incomplete" when only one lease half is authoritative (GOOG 2023).
4. Then I re-check items 1-2 and draw a further 15 random cells. If those are clean, the population dry-run can start.
