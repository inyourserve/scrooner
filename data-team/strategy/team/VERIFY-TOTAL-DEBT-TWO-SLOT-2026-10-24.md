# Verifier sample: total debt rebuilt as two slots (branch lane3-total-debt @1260ea2), 2026-10-24

Role: Data Verifier. Inputs: `scratchpad/debt_slots2_lease_inclusive.jsonl` (default perimeter, 218 changed instants) and `debt_slots2_borrowings_only.jsonl` (161), both at the 10 pilot companies.
- No DB writes. One light read with one connection, 20s timeout and 2 backends: LLY stored totals at three dates.
- Evidence: SEC balance-sheet R pages of the filing for each instant, plus that filing's own facts through SEC companyconcept where a line sits in a note (current portion of debt, finance-lease liabilities). Everything is FILING-CHECKED unless marked.

**Verdict: GATE FAILS by one row.** 26 of 27 shown new values match the carrying debt under their stated perimeter. TSLA 2018-09-30 does not.
- 3 holds are FALSE: the stored value was right.
- 2 shown values carry the label "finance leases not determined" although the filing does determine the leases (a label defect, not a wrong number).

## Sample (seed `random.Random('20261024-twoslot')`)
Frame: 218 lease-inclusive changes: AMZN 54, MSFT 50, AVGO 32, AAPL 25, MU 20, TSLA 17, GOOG 16, NVDA 2, LLY 1, META 1.

| Stratum | Cells | Draw |
|---|---|---|
| 1 TSLA 2017-03..2018-09 | 6 | all |
| 2 GOOG holds | 4 | all |
| 3 MU | 1 named + 10 random | of 19 |
| 4 LLY 2014-03-31, 2016-12-31, 2023-12-31 | 3 | unchanged by the fix, so the stored value is what is shown |
| 5 GOOG 2023-12-31 + AAPL "not determined" | 1 + 3 random | of 15 |
| 6 Random, other changed cells | 10 | of 191 |
| 7 Blank-to-value | 2 | all |

Total: 40 cells.

## 1. TSLA
Face total = current debt and capital leases + current related-party notes + noncurrent debt and capital leases + noncurrent related-party convertible notes. The rule's own lease-inclusive perimeter is used.

| Instant | Fix | Stored | Face total | Verdict | Locator |
|---|---|---|---|---|---|
| 2018-09-30 | **shown 11,776,417K** | 8,665,163K | 2,106,538 + 9,669,879 + **2,634** = 11,779,051K | **WRONG**: misses the noncurrent "Convertible senior notes issued to related parties" line (2,634K, 0.02%) | 10-Q 0001564590-18-026353 R2 |
| 2018-06-30 | hold | 8,626,114K | 2,020,685 + 82,500 + 9,510,696 + 2,594 = 11,616,475K | hold correct (stored wrong) | 10-Q 0001564590-18-019254 R2 |
| 2018-03-31 | hold | 8,219,577K | 1,915,530 + 82,500 + 8,761,070 + 2,556 = 10,761,656K | hold correct | 10-Q 0001564590-18-011086 R2 |
| 2017-09-30 | hold | 9,049,729K | 324,224 + 100,000 + 9,581,616 + 2,481 = 10,008,321K | hold correct | 10-Q 0001564590-17-021343 R2 |
| 2017-06-30 | hold | 6,755,563K | 716,533 + 100,000 + 7,122,862 + 2,444 = 7,941,839K | hold correct | 10-Q 0001564590-17-015705 R2 |
| 2017-03-31 | hold | 6,927,937K | at least 829,080 + 7,148,416 + 10,440; one current related-party row is not rendered | hold correct | 10-Q 0001564590-17-009968 R2 |

The missing 2,634K is a face line in the filing's XBRL. The plan says this related-party convertible fact is not in our store, so it is an ingestion gap (the fallback reader), but the shown cell is still wrong. It should be held, like 2017-06/09, until the line is readable.

## 2. GOOG holds (are they false holds?)
GOOG's face "Short-term debt" includes the current capital-lease obligation, and "Long-term debt" is noncurrent debt.

| Instant | Stored | Face | Verdict | Locator |
|---|---|---|---|---|
| 2015-09-30 | 5,231M | short-term debt 3,237 (incl. capital leases 238) + LTD 1,994 = 5,231 | **FALSE HOLD** (stored right, lease-inclusive) | 10-Q 0001652044-15-000005 R2 |
| 2016-03-31 | 5,208M | 3,221 (incl. leases 223) + 1,987 = 5,208 | **FALSE HOLD** | 10-Q 0001652044-16-000021 R2 |
| 2016-06-30 | 4,203M | 2,219 (incl. leases 220) + 1,984 = 4,203 | **FALSE HOLD** | 10-Q 0001652044-16-000032 R2 |
| 2018-03-31 | 5,273M | short-term 1,329 (CP 1,300 + current leases 29) + LTD 3,973 (noncurrent notes 3,944 + leases 29) = 5,302 lease-inclusive; borrowings 5,244 | hold correct (stored matches neither) | 10-Q 0001652044-18-000016 R2 |

Mechanism of the false holds: DebtCurrent = CommercialPaper + CapitalLeaseObligationsCurrent. The "current total explained by its parts" test ignores the current lease fact as a part.

## 3. MU (lease-inclusive face lines "Current debt" + "Long-term debt")
- 10 random instants, all **right**. Each new value equals face current + face noncurrent, exactly as in the previous report (sums verified there), and is unchanged from v1:
  - 2020-09-03 6,643; 2022-03-03 7,076; 2022-09-01 6,906; 2023-06-01 13,245; 2023-08-31 13,330; 2024-05-30 13,258; 2024-11-28 13,785; 2025-02-27 14,355; 2025-11-27 11,756; 2026-09-03 5,179.
  - The finance-lease facts filed for these instants support the lease-inclusive reading.
- 2021-09-02, hold. Face 155 + 6,621 = 6,776 lease-inclusive (10-K 0000723125-21-000065 R4). FinanceLeaseLiabilityCurrent 154/155 = DebtCurrent 155, and noncurrent finance lease 649, so borrowings = 6,621 - 649 = 5,972.
  - The stored 5,968M matches neither, so the hold is **correct**.
  - It is avoidable: the current line equals the current lease fact, so 6,776 is derivable. This is a coverage item.

## 4. LLY (unchanged: the stored value is shown)
| Instant | Shown | Face | Verdict | Locator |
|---|---|---|---|---|
| 2014-03-31 | 5,264.4M | 9.1 + 5,255.3 | right (no false hold now) | 10-Q 0000059478-14-000102 R4 |
| 2016-12-31 | 10,305.2M | 1,937.4 + 8,367.8 | right | 10-K 0000059478-17-000098 R4 |
| 2023-12-31 | 25,225.3M | 6,904.5 + 18,320.8 | right | 10-K 0000059478-24-000065 R5 |

No finance-lease fact is filed at these dates.

## 5. "Not determined" cells (shown = borrowings slot)
| Cell | Shown | Filing | Verdict |
|---|---|---|---|
| GOOG 2023-12-31 | 12,870M | notes 11,870 + current 1,000 = 12,870 (borrowings right). Face "Long-term debt" 13,253 = notes + finance leases 1,383; current finance lease 363 is filed as a fact | borrowings right; **label defect**: leases ARE determined by the filing; lease-inclusive = 14,616 (10-K 0001652044-24-000022 R3) |
| AAPL 2024-03-30 | 104,590M | CP 1,997 + term 10,762 + 91,831 | right; no lease figure in the 10-Q, so "not determined" is legitimate (10-Q 0000320193-24-000069 R4) |
| AAPL 2025-03-29 | 98,186M | 5,982 + 13,638 + 78,566 | right (10-Q 0000320193-25-000057 R4) |
| AAPL 2024-12-28 | 96,799M | 1,995 + 10,848 + 83,956 | right (10-Q 0000320193-25-000008 R4) |

## 6. Random other changed cells (10)
| Cell | Shown | Filing | Verdict | Locator |
|---|---|---|---|---|
| AVGO 2024-02-04 | 75,901M | face current 2,433 + LTD 73,468 (incl. finance leases 59 + 39) | right | 10-Q 0001730168-24-000023 R2 |
| AMZN 2017-09-30 | 25,747M (nd) | LTD 24,710 + current 1,037 | borrowings right; leases not checked in the note | 10-Q 0001018724-17-000135 R6 |
| AMZN 2024-06-30 | 73,221M | 54,889 + 7,429 + 76 + finance leases 1,439 + 9,388 | right | 10-Q 0001018724-24-000130 R6 |
| AVGO 2019-05-05 | 37,548M (nd) | 3,537 + 34,011 | right (borrowings) | 10-Q 0001730168-19-000101 R2 |
| AMZN 2023-06-30 | 81,647M | 63,092 + 3,997 + 1,100 + 3,024 + 10,434 | right | 10-Q 0001018724-23-000012 R6 |
| MSFT 2022-09-30 | 63,252M | 3,248 + 45,374 + finance leases 14,630 | right | 10-Q 0001564590-22-035087 R4 |
| AMZN 2024-12-31 | 68,393M | 52,623 + 5,017 + 151 + 1,375 + 9,227 | right | 10-K 0001018724-25-000004 R7 |
| AAPL 2025-12-27 | 90,509M (nd) | 1,997 + 11,827 + 76,685 | right | 10-Q 0000320193-26-000006 R4 |
| AVGO 2018-08-05 | 17,604M (nd) | 117 + 17,487 | right | 10-Q 0001730168-18-000039 R2 |
| TSLA 2012-03-31 | 365,908K | 20,194 + 340,323 + capital leases 1,670 + 3,721 | right | 10-Q 0001193125-12-225825 R2 |

## 7. Blank-to-value (2)
| Cell | Shown | Filing | Verdict |
|---|---|---|---|
| NVDA 2016-01-31 | 1,427M | convertible short-term debt 1,413 + capital leases 4 + 10 | right (10-K 0001045810-16-000205 R4) |
| NVDA 2015-01-25 | 1,384M (nd) | Long-term debt (convertible) 1,384,342K; the face also shows "Capital lease obligations, long term" 14,086K (+ current 3,414K) | borrowings right; **label defect**: leases are on the face; lease-inclusive = 1,401.8M (10-K 0001045810-15-000036 R5) |

## Tally
| | Checked | Right | Wrong | Notes |
|---|---|---|---|---|
| Shown new values | 27 | 26 | **1** (TSLA 2018-09-30) | 2 label defects (GOOG 2023, NVDA FY2015) |
| LLY shown stored values | 3 | 3 | 0 | |
| Holds | 10 | 7 correct | 3 **false holds** (GOOG 2015-09, 2016-03, 2016-06) | MU 2021-09-02 and GOOG 2018-03 are correct but avoidable holds |

## To the owner (lane 3) before release
1. Hold any lease-inclusive face-line total when the balance sheet has another debt face line not covered by a stored fact. The fix: hold TSLA 2018-09-30 until the related-party convertible line is ingested.
2. Count the current lease fact as a part when explaining DebtCurrent (CommercialPaper + CapitalLeaseObligationsCurrent). This fixes the three GOOG false holds, and MU 2021-09-02 where DebtCurrent equals the current lease fact.
3. Do not label "finance leases not determined" when a lease face line or lease fact exists for the instant (NVDA FY2015 face line; GOOG 2023 facts filed). Either add them, or label the cell "borrowings only".
4. Then draw a fresh sample.
