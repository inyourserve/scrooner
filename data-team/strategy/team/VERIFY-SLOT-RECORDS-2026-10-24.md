# Verifier sample: debt slot records (scrooner-25, origin/work/scrooner-25/slot-records @4033145), 2026-10-24

Role: Data Verifier. Read-only, no DB. SEC access went through the shared flock limiter at 4 requests/s with `SEC_USER_AGENT` only, one process, cached; downloads deleted afterwards.

Evidence: for every filing, the balance-sheet R page's rows, each with its XBRL tag (`defref`) and printed value, compared with the record's members. FILING-CHECKED throughout.

Seeds: `random.Random('20261024-slots')` for the era sample and `random.Random('20261024-slots-mid')` for the between-boundary checks.
- Frame: 14 era records over 142 filings (MU 48, AAPL 47, MSFT 47) and the 10 replay-cell observations in `cells_debt_slots.jsonl`.
- Checked: 28 era filings (the first and last filing of every era, plus a 10-K or 10-Q where needed), 6 mid-era filings, 10 replay cells. 44 filings in total.

**Verdict: GATE FAILS on the class labels, not on the compositions.**
- Every record's member tags equal exactly the debt lines printed on the face, in all 44 filings.
- No format change is missed, and every reported boundary is real.
- But the `class` field is wrong on 2 tags:
  - MU's two members: `LongTermDebtAndCapitalLeaseObligations` is labelled `finance_lease` but is a combined debt-plus-finance-lease line; `DebtCurrent` is labelled `borrowing` but contains the current finance lease. This affects all 3 MU era records.
  - GOOG 2015-2016 `DebtCurrent` is labelled `borrowing` but includes current capital leases (3 replay cells).
- Any slot math that reads `class` to split borrowings from leases would be wrong for these records.
- AAPL (4 era records) and MSFT (7) are fully right.

## 1. Era records (composition vs face)
| Co | Era (period range, observations) | Filings checked (first / last / extra) | Face debt lines (tag: printed value) | Record | Verdict |
|---|---|---|---|---|---|
| MU | 0: 2014-12-04..2019-08-29 (20) | 10-Q 0000723125-15-000010 R4; 10-K 0000723125-19-000094 R4 | DebtCurrent "Current debt" 1,168 / 1,310; LongTermDebtAndCapitalLeaseObligations "Long-term debt" 4,608 / 4,541 | same two tags | composition right; **class wrong**: LTD&CLO labelled `finance_lease`, should be `combined`. The 2014-15 face also shows mezzanine "Redeemable convertible notes" 53 (`mu:ConvertibleDebtEquity`), correctly outside total debt |
| MU | 1: 2019-11-28..2026-05-28 (27) | 10-Q 0000723125-19-000174 R4 (first); 10-Q 0000723125-26-000015 R4 (last); 10-K 0000723125-20-000082 R4 | Current debt 462 / 582 / 270; Long-term debt 5,188 / 5,140 / 6,373; plus operating-lease line | same + `OperatingLeaseLiabilityNoncurrent` (class operating_lease, correctly not debt) | composition right; **class wrong** (as era 0). DebtCurrent also includes the current finance lease: 2021-09-02 DebtCurrent 155 = FinanceLeaseLiabilityCurrent 155 (10-K 0000723125-21-000065 R4) |
| MU | 2: 2026-09-03 (1) | 10-K 0000723125-26-000023 R4 | Current debt 491; Long-term debt 4,688; no operating-lease line | same | composition right; class wrong |
| AAPL | 0: 2014-12-27..2015-03-28 (2) | 10-Q 0001193125-15-023697 R4; 10-Q 0001193125-15-153166 R4 | CommercialPaper 3,899 / 3,799; LongTermDebt 32,504 / 40,072 | same | right |
| AAPL | 1: 2015-06-27..2019-12-28 (19) | 10-Q 0001193125-15-259935 R4 (first); 10-Q 0000320193-20-000010 R4 (last); 10-K 0000320193-19-000119 R4 | CP + LongTermDebtCurrent + LongTermDebtNoncurrent (e.g. 5,980 + 10,260 + 91,807) | same | right |
| AAPL | 2: 2020-03-28..2020-06-27 (2) | 10-Q 0000320193-20-000052 R4; 10-Q 0000320193-20-000062 R4 | OtherShortTermBorrowings "Commercial paper and repurchase agreement(s)" 10,029 / 11,166 + term debt current + noncurrent | same | right |
| AAPL | 3: 2020-09-26..2026-06-27 (24) | 10-K 0000320193-20-000096 R4 (first); 10-Q 0000320193-26-000020 R4 (last) | CP + term debt current + noncurrent (e.g. 1,997 + 11,007 + 71,340) | same | right |
| MSFT | 0: 2014-12-31..2016-06-30 (7) | 10-Q 0001193125-15-020351 R5; 10-K 0001193125-16-662209 R5 | ShortTermBorrowings "Short-term debt" + LongTermDebtCurrent + LongTermDebtNoncurrent (8,299 + 1,749 + 18,260; 12,904 + 0 + 40,783) | same | right |
| MSFT | 1: 2016-09-30 (1) | 10-Q 0001193125-16-742796 R5 | ShortTermBorrowings 14,536 + LongTermDebtNoncurrent 60,154; no current-LTD line | same | right (real one-quarter change) |
| MSFT | 2: 2016-12-31..2017-06-30 (3) | 10-Q 0001564590-17-000654 R5; 10-K 0001564590-17-014900 R5 | three lines again (25,065 + 599 + 59,306; 9,072 + 1,049 + 76,073) | same | right |
| MSFT | 3: 2017-09-30..2018-06-30 (4) | 10-Q 0001564590-17-020171 R4; 10-K 0001564590-18-019062 R4 | three lines + operating lease liabilities (5,768 / 5,568) | same + op lease | right |
| MSFT | 4: 2018-09-30..2023-06-30 (20) | 10-Q 0001564590-18-024893 R4; 10-K 0000950170-23-035122 R4 | current LTD + LTD (6,497 + 69,733; 5,247 + 41,990), no short-term line | same | right |
| MSFT | 5: 2023-09-30..2025-06-30 (8) | 10-Q 0000950170-23-054855 R4; 10-K 0000950170-25-100235 R4 | CommercialPaper "Short-term debt" 25,808 / 0 + current LTD + LTD | same | right |
| MSFT | 6: 2025-09-30..2026-06-30 (4) | 10-Q 0001193125-25-256321 R4; 10-K 0001193125-26-323660 R4 | current LTD + LTD (7,832 + 35,376; 9,227 + 31,067) | same | right |

None of these companies prints a total-debt line on the face, so "sum equals printed total" means: the sum of the record's members equals the sum of the printed debt lines. That holds in every filing above, because the member sets are identical to the face lines.

## 2. Format-change boundaries
- **Every reported change is real on the face:**
  - MU: operating-lease line appears 2019-11-28 (ASC 842) and is gone in the FY2026 10-K.
  - AAPL: current/noncurrent split from 2015-06-27; `OtherShortTermBorrowings` line in Q2-Q3 FY2020; back to CommercialPaper in the FY2020 10-K.
  - MSFT:
    - no current-LTD line at 2016-09-30;
    - operating-lease line from 2017-09-30 (early ASC 842 adoption);
    - short-term debt line off from 2018-09-30;
    - commercial paper on from 2023-09-30 and off from 2025-09-30.
- **No missed change.** The 6 mid-era filings match their era records exactly:

| Co | Mid-era filings checked |
|---|---|
| MU | 10-Q 0000723125-21-000032; 10-Q 0000723125-24-000007 |
| AAPL | 10-Q 0001628280-16-017809; 10-Q 0000320193-26-000006 |
| MSFT | 10-K 0001564590-19-027952; 10-K 0001564590-21-039151 |

  In addition, every observation inside each era carries that era's fingerprint (0 non-matching).

## 3. Replay cells (compositions vs face)
| Cell | Face lines | Record | Verdict |
|---|---|---|---|
| TSLA 2018-09-30 (10-Q 0001564590-18-026353 R2) | LTD&CLO current 2,106,538 + LTD&CLO 9,669,879 + `tsla:ConvertibleSeniorNotesIssueToRelatedPartiesNonCurrent` 2,634 = **11,779,051K** | the same three tags | **right** (full composition including the custom tag; the value needs the instance read, as the stage-2 note says) |
| GOOG 2023-12-31 (10-K 0001652044-24-000022 R3) | LTD&CLO "Long-term debt" 13,253 (+ operating leases 12,460) | same | right (face carries no current debt; current 1,000 and leases 363 are note-only) |
| GOOG 2015-09-30 / 2016-03-31 / 2016-06-30 (10-Q 0001652044-15-000005, -16-000021, -16-000032 R2) | DebtCurrent "Short-term debt" 3,237 / 3,221 / 2,219 + LTD&CLO 1,994 / 1,987 / 1,984 | same tags | composition right; **class wrong**: DebtCurrent labelled `borrowing` although it includes current capital leases 238 / 223 / 220 (CapitalLeaseObligationsCurrent facts) |
| NVDA 2015-01-25 (10-K 0001045810-15-000036 R5) | LongTermDebt 1,384,342K + CapitalLeaseObligationsNoncurrent 14,086K | same | right |
| ABBV 2022-03-31 (10-Q 0001551152-22-000017 R5) | ShortTermBorrowings 12 + LTD&CLO current 9,940 + LTD&CLO 63,522 | same | right |
| ABBV 2017-12-31 (10-K 0001551152-18-000014 R5) | 400 + 6,015 + 30,953 (`LiabilitiesOtherThanLongtermDebtNoncurrent` correctly excluded) | same | right |
| CVX 2015-03-31 / 2014-09-30 (10-Q 0000093410-15-000020, -14-000049 R5) | ShortTermBorrowings 3,908 / 5,665 + LongTermDebtNoncurrent 29,960 / 19,960 + CapitalLeaseObligationsNoncurrent 65 / 84 | same | right |
| AAPL 2020 Q2/Q3, MU 2021-09-02 | see era table | | right (MU class as above) |

## 4. Authority gaps
- NVDA FY2015: the face prints `us-gaap_LongTermDebt` **1,384,342K** (10-K 0001045810-15-000036 R5). Confirmed. The stage-2 report says every stored copy is non-authoritative; that is a triage item for the conflict-resolution owner.
- GOOG 2023-12-31: the face prints `LongTermDebtAndCapitalLeaseObligations` **13,253M** (10-K 0001652044-24-000022 R3) = notes 11,870 + noncurrent finance leases 1,383. Confirmed.

## Misses / to the owner (scrooner-25)
1. Classes: when a line's tag is LTD&CLO, LongTermDebtAndCapitalLeaseObligationsCurrent, or a `DebtCurrent` that holds a lease component (MU, GOOG 2015-16), class it `combined`. Use the filer's calc children or a same-instant lease fact. Re-emit MU's 3 era records and the 3 GOOG cells.
2. Optional: carry a `mezzanine_excluded` note where a convertible sits in temporary equity (MU 2014-15 `mu:ConvertibleDebtEquity`; LRCX), so the exclusion is explicit.
3. With those fixed the records can go to the migration step.
