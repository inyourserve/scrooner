# Verifier: 30-company debt slot records V2 (scrooner-25, 03eeea5), 2026-10-24

Role: Data Verifier (Verifier 3). Object: `SLOT-RECORDS-30SET-V2-2026-10-24.md`, `results/thirty_debt_records_v2.jsonl` (173 records) and `results/replay30_v2_report.json` on `origin/work/scrooner-25/slot-records` @ 03eeea5. Read-only, no DB connection (production = lane 3 before-images in the report). SEC: about 260 requests at most 1.7 req/s with the declared `SEC_USER_AGENT`, one process at a time (several 503s, backed off). Downloads deleted at the end; free disk 8.0 GB or more throughout. Fresh seed `random.Random(20261025)`, excluding every cell read in pass 1.

## Verdict
- **Replay cells: PASS.** 0 wrong slot values in 54 cells read: 22 former failures plus 32 fresh cells. All FILING-CHECKED on the R pages.
- **Record set: NOT YET RELEASABLE.** 8 records have wrong members or classes; none of them has a replay cell (findings R1-R4 below):
  - 4 MSFT records and 1 GOOG record would publish wrong values today: their facts are in core.fact.
  - 1 AMZN, 1 AVGO and 1 TSLA record are wrong too. Today they hard-stop, so they show no value rather than a wrong one.
  - GE has a separate open question (item 2).

## (1) The 22 previous failures: all right now
| Set | V2 slot vs face | Locators |
|---|---|---|
| KO 13 cells | 13/13 equal the face (e.g. 2018-09-28 44,837 = 12,973 + 6,341 + 25,523; 2019-03-29 44,267; 2019-06-28 45,075; 2025-09-26 47,416 = 2,319 + 1,920 + 43,177) | 0000021344-18-000042, -19-000028, -19-000034 R4; 0001628280-25-046054 R4; the other 9 from pass 1 |
| ORCL 8 cells 2016-11..2019-02 (and 2015-02, -08, -11) | 11/11 equal the face (e.g. 2017-11-30 60,669 = 2,499 + 58,170; 2018-11-30 58,038) | 0001193125-17-087309, -17-287455, -17-372232, -18-090646 R2; 0001564590-18-023315, -18-031113 R2; 0001193125-15-407703 R2 |
| GE 2021-12-31 | 35,185 = 10-K face | 0000040545-22-000008 R4 |
| AMD records 2016-12, 2017-12, 2018-12 | `LinesOfCreditCurrent` now a member | 0000002488-18-000042 R5 |
| AMAT 2015 eras | custom AP line now `excluded_combined_nondebt` | 0000006951-15-000034 R4 |

## (2) GE 2018-12-31 `ge:ShortTermDebtAssumed`
The face (0000040545-19-000014 R4) has three column blocks: consolidated, GE, GE Capital.
- In the consolidated block, "Short-term borrowings assumed by GE" is 0, and so is "Long-term borrowings assumed by GE". In the GE and GE Capital blocks the two lines are 4,207 / 2,684 and 32,054 / 19,828.
- They are GE Capital borrowings assumed by the parent: an intercompany presentation that eliminates on consolidation.
- Consolidated debt = 12,849 ST + 1,875 non-recourse + 95,234 LT = 109,958M.

**Answer:** both "assumed" lines should get the SAME treatment. Today `LongTermDebtAssumed` is a member and `ShortTermDebtAssumed` is uncovered. Either both are members (consolidated value 0) or both are excluded with the reason "intercompany assumption, 0 in the consolidated column". The total is unchanged either way, provided only the consolidated (undimensioned) context is read.

Note: `NonRecourseBorrowings...` here is also a custom `ge_` tag, so GE 2018 cannot be computed from core.fact. It needs the instance reader.

## (3) Tag-name "discrepancy": no conflict
- **ORCL 2015** face tag is `LongTermNotesPayable` (0001193125-15-098586 R2; -15-407703 R2). The builder is right.
- **AMD 2018 H1** face tag is `DebtCurrent` "Short-term debt, net" 223 (0000002488-18-000068 R4). The 10-Ks print `LinesOfCreditCurrent`.
- My rejection note named `LongTermNotesAndLoans` only for ORCL's 2016-11+ eras and `LinesOfCreditCurrent` only for the AMD 10-K records. Both readings are true for their own filings: the tag changes between eras.

## (4) Fresh seeded sample
Class frames (my re-derivation from the V2 report): fragment 76 (35 holds), precision 63, composition 70, prod-higher 8. Pool = frame minus the cells read in pass 1 minus KO/ORCL: fragment 17 holds + 32 others, precision 50, composition 57, higher 2.

| Class | Cells (all slot RIGHT) | Production |
|---|---|---|
| Fragment, holds (5) | CSCO 2018-01-27 39,366; 2025-07-26 28,093; 2025-10-25 28,089; 2026-04-25 31,303; 2026-07-25 29,533 (0000858877-18-000004, -25-000111, -25-000171, -26-000078, -26-000132) | wrong 5/5 (22.9-30.4B: drops most short-term debt) |
| Fragment (5) | WMT 2016-04-30 50,022; 2021-07-31 46,322; 2023-01-31 44,622; 2024-07-31 47,001 (0000104169-16-000088, -21-000058, -23-000020, -24-000141); CVX 2019-12-31 26,973 (0000093410-20-000010) | wrong 5/5. WMT = LTD current + noncurrent only: drops short-term borrowings and finance leases, so it is wrong on either perimeter. CVX = the LongTermDebt pattern |
| Precision (10) | UNH 2015-09-30; MRK 2019-09-30, 2023-03-31, 2024-06-30; INTC 2015-12-26; CSCO 2015-07-25, 2016-01-23; LRCX 2019-12-29, 2020-03-29, 2025-06-29 | wrong 7 (MRK $0.1B-rounded, UNH -135, INTC +37, CSCO -2/-3). LRCX 3 = `LongTermDebt` borrowings perimeter (perimeter flip, not proven wrong) |
| Composition (10) | UNH 2016-06-30, 2016-09-30, 2016-12-31, 2017-03-31, 2018-06-30, 2025-12-31; COST 2018-11-25, 2019-02-17, 2020-08-30; LRCX 2021-06-27 | wrong 9 (UNH 0.18-1.37B low, COST +33 to +48); LRCX = borrowings perimeter |
| Prod-higher (2 = whole fresh pool) | CVX 2023-12-31 20,836 (0000093410-24-000013 R5); JNJ 2023-12-31 29,332 (0000200406-24-000013 R3) | wrong 2/2 |

Hard stops: ABBV 2015-06-30 prints Short-term borrowings blank (no fact) with face 4,007 + 27,116 = 31,123 (0001104659-15-057641 R5). The missing-member hard stop turns this computable cell into unavailable. Not a wrong value, but over-strict: allow a member whose face cell is blank in that filing.

## (5) Scan of all 173 records against their evidence filings
No face debt line is missing from members or exclusions (my label and tag net, one filing per record). Defects found the other way: members that are NOT face debt lines.
- **R1 Securities lending payable as debt:** MSFT 2014-12..2017-12 (4 records) and GOOG 2015-09..2016-12 (1 record) list `DepositsReceivedForSecuritiesLoanedAtCarryingValue` as `borrowing`.
  - On the face it is "Securities lending payable": MSFT 430M at 2014-12-31 (0001193125-15-020351 R5); GOOG 3,266M at 2015-09-30 beside debt of 5,231M (0001652044-15-000005 R2).
  - The undimensioned facts exist (SEC companyconcept), so these slots would publish total debt inflated by these amounts (GOOG +62%).
  - The debt card does not list it as debt. Exclude it, or get a Standardization Lead ruling.
- **R2 AMZN 2019-03..2026-06:** custom `amzn_LeaseLiabilityNoncurrent` "Long-term lease liabilities" (33,275M at 2019-03-31, 0001018724-19-000043 R6) is classed `borrowing`. It contains operating leases (ledger row 117), so it must be combined/operating with the finance part located, or excluded. Today it is a custom tag, so the cell hard-stops.
- **R3 Members taken from note roles, not the face:**
  - GE `LongTermAndNonRecourseBorrowings` (guarantor condensed consolidating note), 4 records 2017-09..2020-03.
  - AVGO `IntercompanyLoanPayableCurrent/LongTerm` (condensed consolidating note; intercompany, eliminates). AVGO 2019-11-03 face = 2,787 + 30,011 = 32,798, 0001730168-19-000144 R2.
  - TSLA `LongTermDebtCurrent` (VIE note), 2016-12..2018-09.
  - None has an undimensioned fact, so these records hard-stop: AVGO 2018-2021 and TSLA 2016-2018 show unavailable although the face is computable. If such a fact existed, it would double count.
  - Fix: members only from the face statement role.
- **R4 Coverage miss:** TSLA 2016-12..2018-09 face "Current portion of solar bonds and promissory notes issued to related parties" 100,000K and "Solar bonds issued to related parties" 100K (`DueToRelatedPartiesCurrent/Noncurrent`; 0001564590-18-002956 R2) are debt lines. The coverage net missed them, so the slot would be 100.1M low.
- Harmless flags: MU redeemable convertible notes (mezzanine), RPAY 2018 SPAC-era note, operating-lease members (excluded from totals).

## (6) Five companies not checked before (record vs a mid-era face, slot computed from SEC companyconcept, periodic forms, latest filed; DATA-INFERRED that this equals core.fact)
| Company | Cells | Result |
|---|---|---|
| NVDA | 2023-01-29: 1,250 + 9,703 = 10,953 (0001045810-23-000017 R5); 2016-10-30: 1,011 + 1,982 + 7 = 3,000 (0001045810-16-000353 R4) | right |
| NFLX | 2017-12-31: 6,499.4 (0001065280-18-000069 R6); 2023-12-31: 399.8 + 14,143.4 = 14,543.3 (0001065280-24-000030 R7) | right |
| LLY | 2016-12-31: 1,937.4 + 8,367.8 = 10,305.2 (0000059478-17-000098 R4); 2022-12-31: 16,238.6 (0000059478-23-000082 R5) | right |
| AVGO | 2023-10-29: 1,608 + 37,621 = 39,229 (0001730168-23-000096 R3) right; 2019-11-03 blocked by R3 | right / blocked |
| CAT | 2017-12-31: members are 6 custom segment tags (0000018230-18-000042 R5); 2023-12-31: debt only per segment member (0000018230-24-000009 R5), no undimensioned LTD in companyconcept | not computable from core.fact. A hard stop is correct; needs a member-sum or instance reader (ledger row 60) |

## Production total_debt errors found this pass (FILING-CHECKED)
- CSCO 2018-2026: drops most short-term debt (5 holds).
- WMT 2016-2024: LTD current + noncurrent only (4).
- CVX 2019 and 2023: the LongTermDebt / DebtCurrent patterns.
- UNH 2015-2025: 0.13-1.37B low (7).
- MRK: $0.1B rounding (3).
- COST: +33 to +48M (3).
- INTC 2015: +37M.
- CSCO 2015-16: -2 to -3M.
- JNJ 2023: +1,469M.
- KO 2018-2019: missing 11-13B of commercial paper (fixtures).
- ORCL 2015-2019: current portion only (11 cells).
- LRCX: perimeter flips between borrowings and lease-inclusive by period.

## Untested
- BO variant (dropped from verdicts).
- Mid-era filings beyond those named. The scan reads one filing per record and matches by label regex, so a debt line with an unusual label can still escape (the TSLA solar bonds did).
- Production's KO -0.3B gap 2023+.
- JNJ's cause.
- The 28 fresh-pool cells not drawn.
- GE values (custom tags).

## Next actions (owner scrooner-25)
1. Members only from the face statement role. This removes the GE guarantor-note, AVGO consolidating-note and TSLA VIE-note members.
2. Exclude securities lending payable (MSFT, GOOG) unless the Standardization Lead rules otherwise.
3. Reclass AMZN's custom lease line as combined, operating-lease-inclusive.
4. Add "bonds" / related-party notes to the coverage net (TSLA).
5. Give GE's two "assumed by GE" lines the same treatment.
6. Let a member whose face cell is blank pass the hard stop (ABBV).
7. Re-run, then a Verifier re-check of MSFT 2014-12-31, GOOG 2015-09-30, AVGO 2019-11-03, TSLA 2017-12-31 and GE 2018-12-31 as fixtures.
