# Verifier sample: root fix #1, total debt from balance-sheet carrying lines (2026-10-24)

Role: Data Verifier. Object: branch `work/data-engineer/lane3-total-debt` @c405a05 (flag OFF), its dry-run before/after file `scratchpad/debt_carrying_cohort.jsonl` (167 changed instants at the 10 pilot companies). Read-only; no DB query was needed (the before/after file plus SEC filings). Scope: top-1000 pilot companies.

**Verdict: GATE FAILS.** 3 of 37 checked new values are wrong (TSLA 2017-03-31, 2017-06-30 and 2017-09-30), all from one mechanism. A fourth (GOOG 2023-12-31) does not match the printed lines because it uses a different lease perimeter (definition question; counted separately). In addition, 3 of the 9 value-to-blank cells hide a correct stored value, and the other 6 replace a wrong value with a blank where the right value can be read off the face.

## Sample
- Frame: 167 changed instants. NVDA and META are unchanged.

| Company | Changed instants |
|---|---|
| AMZN | 53 |
| AVGO | 31 |
| MSFT | 28 |
| MU | 20 |
| AAPL | 17 |
| TSLA | 10 |
| GOOG | 6 |
| LLY | 2 |

- Mandatory cells (36): all 20 MU, all 10 TSLA, all 9 value-to-blank (7 of them TSLA), AAPL Q3 FY26, GOOG FY2025, AMZN FY2025 and AMZN Q2 2026. That is more than the 30 requested, so I checked all of them.
- Plus 10 seeded random cells from the remaining 131: `random.Random('20261024-totaldebt').sample(sorted(rest), 10)`.
- 46 cells in total, all FILING-CHECKED:
  - Balance-sheet R page of the 10-K/10-Q whose period of report equals the instant.
  - Where the current portion is not printed on the face (AMZN, GOOG), the filing's own LongTermDebtCurrent / ShortTermBorrowings facts, read through SEC companyconcept, plus the data-team/35 note reads.
  - One stale cached SEC page (TSLA Q2 2018 R2) was refetched.
- Criterion: total debt = current + noncurrent debt carrying lines per the filing. The perimeter is reported where a filer's printed line includes finance or capital leases.

## Results
| Group | n | New value right | New value wrong | Stored (before) right | Stored wrong |
|---|---|---|---|---|---|
| MU (all) | 20 | 20 | 0 | 0 | 20 |
| TSLA new values (2017) | 3 | 0 | **3** | 0 | 3 |
| Named: AAPL Q3 FY26, GOOG FY2025, AMZN FY2025, AMZN Q2 2026 | 4 | 4 | 0 | 0 | 4 |
| Random | 10 | 9 | 0 (+1 definition: GOOG 2023) | 0 | 10 |
| **All new values** | **37** | **33** | **3** (+1 definition) | 0 | 37 |
| Value-to-blank | 9 | - | - | 3 right (LLY 2014-03-31, TSLA 2011, TSLA 2012) | 6 wrong |

So the stored values were wrong in 43 of 46 sampled cells; the fix makes 33 of 37 new values right.

### Root cause of the 3 wrong new values (one mechanism)
At TSLA the rule takes `DebtCurrent` from the debt note and adds the face line `LongTermDebtAndCapitalLeaseObligations`. Three things go wrong:
- **Perimeter mix.** `DebtCurrent` is debt only, including related-party notes but excluding capital leases. The noncurrent line includes capital leases.
- **Omitted line.** The face line "Convertible senior notes issued to related parties" (noncurrent) is dropped.
- **Wrong acceptance rule.** The rule "DebtCurrent at or above the sum of the listed parts (TSLA-shaped) is accepted" is what lets this through.

Face totals (current + current related-party notes + noncurrent + noncurrent related-party convertible):

| Instant | Face total (FILING-CHECKED) | New value | Note |
|---|---|---|---|
| 2017-06-30 | 716,533 + 100,000 + 7,122,862 + 2,444 = **7,941,839K** | 7,883,146K = DebtCurrent 760,284 + 7,122,862 | |
| 2017-09-30 | 324,224 + 100,000 + 9,581,616 + 2,481 = **10,008,321K** | 9,957,122K | |
| 2017-03-31 | at least 829,080 + 7,148,416 + 10,440 = 7,987,936K | 8,112,153K | one current related-party row is not rendered in R2 (current liabilities sum 174,231K short of the total); the new value matches no coherent sum |

### Value-to-blank (9)
| Cell | Stored | Filing | Verdict |
|---|---|---|---|
| AAPL FY2015 (r7) | 10,999M (CP + current only) | CP 8,499 + current 2,500 + LTD 53,463 = 64,462 (10-K 0001193125-15-356351 R5) | stored wrong; blank is better, but **a value should be shown** (needs the conflict-resolved noncurrent fact) |
| LLY 2014-03-31 (r8) | 5,264.4M | 9.1 + 5,255.3 = 5,264.4 (10-Q 0000059478-14-000102 R4) | **stored right; blank hides a correct value** (false hold) |
| TSLA 2011-12-31 (r8+r5) | 276,251K | LTD 7,916 + 268,335 = 276,251 excl. capital leases 3,897 (10-K 0001193125-12-081990 R2) | stored right (borrowings only); pre-2015, outside the display window |
| TSLA 2012-12-31 (r8+r5) | 452,336K | 50,841 + 401,495 = 452,336 excl. leases (10-K 0001193125-13-096241 R2) | stored right; pre-2015 |
| TSLA 2014-06-30 (r5) | 593.7M (current convertible only) | 593,712 + 1,767,024 = 2,360,736K excl. leases (10-Q 0001193125-14-303175 R2) | stored wrong; **value should be shown** |
| TSLA 2014-09-30 (r5) | 597.6M | 597,626 + 1,786,635 = 2,384,261K excl. leases (10-Q 0001193125-14-403635 R2) | stored wrong; **value should be shown** |
| TSLA 2018-03-31 (r8) | 8,219.6M (LongTermDebt) | 1,915,530 + 82,500 + 8,761,070 + 2,556 = 10,761,656K (10-Q 0001564590-18-011086 R2) | stored wrong; **value should be shown** |
| TSLA 2018-06-30 (r8) | 8,626.1M | 2,020,685 + 82,500 + 9,510,696 + 2,594 = 11,616,475K (10-Q 0001564590-18-019254 R2) | stored wrong; **value should be shown** |
| TSLA 2018-09-30 (r8) | 8,665.2M | 2,106,538 + 9,669,879 + 2,634 = 11,779,051K (10-Q 0001564590-18-026353 R2) | stored wrong; **value should be shown** |

### Perimeter (definition question, not counted wrong)
The lease perimeter differs across companies. A face line that includes leases is taken as printed:
- MU: "Long-term debt" is tagged LongTermDebtAndCapitalLeaseObligations.
- TSLA: "debt and capital leases".

Borrowings-only is used where the filer tags the notes separately (GOOG, AMZN). At GOOG 2023-12-31 the printed "Long-term debt" 13,253M includes finance leases 1,383M; the new value 12,870M = notes 11,870 + current 1,000 excludes them. The same perimeter is used at GOOG 2025 (face line 46,547 excludes leases), so GOOG is internally consistent. The cross-company perimeter (ledger row 53) is a coupled definition decision for the Standardization Lead.

## Per-cell verdicts (new value unless noted; FILING-CHECKED)
| # | Co | Instant | Before | After | Filing total | New | Stored | Accession, locator |
|---|---|---|---|---|---|---|---|---|
| 1 | AAPL | 2026-06-27 | 84,297M | 84,344M | CP 1,997 + term debt 11,007 + 71,340 | right | wrong | 10-Q 0000320193-26-000020 R4 |
| 2 | GOOG | 2025-12-31 | 49,085M | 48,543M | LTD 46,547 + current 1,996 (note) | right | wrong | 10-K 0001652044-26-000018 R3; LongTermDebtCurrent fact |
| 4-23 | MU | 20 instants 2020-09-03..2026-09-03 | 2,792-12,434M | 5,179-15,541M | "Current debt" + "Long-term debt", every sum exact (e.g. 2026-09-03 491 + 4,688; 2025-08-28 560 + 14,017; 2023-11-30 908 + 12,597) | 20 right | 20 wrong | 10-K 0000723125-26-000023 R4, -25-000028 R5, -24-000027 R5, -23-000054 R5, -22-000048 R5, -21-000065 R4, -20-000082 R4; 10-Q -22-000036, -24-000019, -24-000007, -24-000047, -23-000077, -25-000021, -22-000004, -25-000046, -22-000072, -23-000022, -23-000041, -25-000009, -22-000016 (R4) |
| 24 | AMZN | 2026-06-30 | 133,320M | 132,549M | 128,894 + 3,330 + 325 | right | wrong | 10-Q 0001018724-26-000026 R6 (+ R44/R45 per data-team/35) |
| 25 | AMZN | 2025-12-31 | 69,291M | 68,851M | 65,648 + 2,748 + 455 | right | wrong | 10-K 0001018724-26-000004 R7 (+ R69) |
| 27 | TSLA | 2017-03-31 | 6,927.9M | 8,112.2M | at least 7,987.9M, see above | **wrong** | wrong | 10-Q 0001564590-17-009968 R2, R60 |
| 31 | TSLA | 2017-06-30 | 6,755.6M | 7,883.1M | 7,941.8M | **wrong** | wrong | 10-Q 0001564590-17-015705 R2 |
| 32 | TSLA | 2017-09-30 | 9,049.7M | 9,957.1M | 10,008.3M | **wrong** | wrong | 10-Q 0001564590-17-021343 R2 |
| 36 | AMZN | 2016-12-31 | 8,838M | 8,750M | LTD 7,694 + current 1,056 | right | wrong | 10-K 0001018724-17-000011 R6 |
| 37 | MSFT | 2015-12-31 | 44,400M | 44,429M | 3,000 + 750 + 40,679 | right | wrong | 10-Q 0001193125-16-441821 R5 |
| 38 | AMZN | 2021-09-30 | 51,376M | 51,055M | 50,055 + 1,000 | right | wrong | 10-Q 0001018724-21-000028 R6 |
| 39 | AVGO | 2023-04-30 | 39,271M | 39,311M | 1,117 + 38,194 | right | wrong | 10-Q 0001730168-23-000064 R2 |
| 40 | AMZN | 2023-03-31 | 70,572M | 70,184M | 67,084 + 2,000 + ST 1,100 | right | wrong | 10-Q 0001018724-23-000008 R6 |
| 41 | AMZN | 2022-03-31 | 50,553M | 50,237M | 47,556 + 2,681 | right | wrong | 10-Q 0001018724-22-000013 R6 |
| 42 | AVGO | 2023-10-29 | 39,184M | 39,229M | 1,608 + 37,621 | right | wrong | 10-K 0001730168-23-000096 R3 |
| 43 | AMZN | 2021-03-31 | 33,227M | 33,024M | 31,868 + 1,156 | right | wrong | 10-Q 0001018724-21-000010 R6 |
| 44 | GOOG | 2023-12-31 | 14,746M | 12,870M | printed LTD 13,253 (incl. finance leases 1,383) + current 1,000; notes-only 12,870 | definition (borrowings-only) | wrong | 10-K 0001652044-24-000022 R3 |
| 45 | AAPL | 2023-07-01 | 109,293M | 109,280M | 3,993 + 7,216 + 98,071 | right | wrong | 10-Q 0000320193-23-000077 R4 |
The 9 value-to-blank cells (#0, #3, #26, #28-30, #33-35) are in the table above.

For AMZN and GOOG the current portion and short-term borrowings sit inside accrued liabilities on the face. Their values come from the filing's own facts (SEC companyconcept for the named accession) and, for the named cells, the debt-note reads in data-team/35.

## Required before release (to the owner, lane 3)
1. Remove the "DebtCurrent at or above the parts is accepted" path, or require DebtCurrent and the noncurrent line to share a lease perimeter. Add every noncurrent debt face line, including related-party convertible notes. Re-test TSLA 2017.
2. LLY 2014-03-31: the hold fires on a correct "short-term borrowings and current maturities" + "long-term debt" pair. Find why the overlap test failed and re-test.
3. Value-to-blank where the face gives the total (AAPL FY2015; TSLA 2014 and 2018): the hold is safer than the old wrong values, but each should show the filed total once its lines are readable. Track this as a coverage item, not a release blocker for this fix.
4. Lease perimeter: get one decision from the Standardization Lead (MU and TSLA lease-inclusive; GOOG and AMZN borrowings-only).
5. Draw a fresh sample after the fix, including a lease-perimeter stratum and the 131 non-sampled instants.
