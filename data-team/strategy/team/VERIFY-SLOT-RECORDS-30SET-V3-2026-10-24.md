# Verifier: 30-company debt slot records V3 (scrooner-25, 322d092), 2026-10-24

Role: Data Verifier (Verifier 3). Object: V3 records (174, written to `results/thirty_debt_records_v2.jsonl`, overwritten in place) and `results/replay30_v2_report.json` @ 322d092. Read-only, no DB. SEC: about 80 requests at most 1.7 req/s with `SEC_USER_AGENT`, one process. Downloads deleted at the end; free disk 9 GB or more.
Fixture slots with no replay cell were computed from SEC companyconcept data (periodic forms, latest filed, undimensioned). That this equals what core.fact gives is DATA-INFERRED.

## Verdict: GATE FAILED. 2 wrong slot values; 1 record defect not fixed
- **W1: the new blank-member verdict uses production as its evidence.** `replay30.py` adds `agrees_lease_inclusive_blank_member`: a missing member passes when the slot equals lane 3's before-image. That is the value under test, so the check is circular. The filer-aggregate path did not fire for any of the 5 cells. 2 of the 5 cells are wrong:
  - **GE 2015-12-31:** slot 194,519M = 49,860 + 144,659. The face also has "Non-recourse borrowings of consolidated securitization entities" 3,083M on custom `ge_NonRecourse...` (0000040545-17-000010 R5; as filed 0000040545-16-000145 R6: 49,892 + 3,083 + 145,301). Correct value 197,602M (latest-filed basis). Production is equally wrong.
  - **RPAY 2020-03-31:** slot 5.502M = current maturities only. Face "Long-term debt, net of current maturities" is 240,955,360 on custom `rpay_LongTermDebtExcludingLineOfCreditNoncurrent` (0001564590-20-024317 R2). Correct value 246.5M. Production is equally wrong.
  - The other 3 are right: ABBV 2015-06-30 31,123M (short-term borrowings printed blank, 0001104659-15-057641 R5), 2024-06-30 70,634M, 2024-09-30 71,079M (no short-term row on the face; 0001551152-24-000031 and -000040 R5). Right by luck of the face, not by the rule.
  - Rule: a missing member may be treated as blank only on face evidence (the cell is blank or absent in that filing, or the filer's own printed total ties). Never because production agrees. A custom-tag member that core.fact cannot hold must always hard-stop.
- **R3 not fixed: the statement-role rule passes note roles.** `BS_ROLE_RX` (`balance ?-?sheets?|financial ?position|financial ?condition`) also matches these role names:
  - `CondensedConsolidatingFinancialInformationBalanceSheetDetails` (AVGO)
  - `GuarantorFinancialInformationCondensedConsolidatingStatementOfFinancialPositionDetails` (GE)
  - `DisclosureVIEArrangements...InConsolidatedBalanceSheetsDetail` (TSLA)
  
  The same 8 note-role members as in V2 remain: GE `LongTermAndNonRecourseBorrowings` (4 records), TSLA `LongTermDebtCurrent` (1), AVGO `IntercompanyLoanPayableCurrent/LongTerm` and `LongTermDebtCurrent` (1 record; its only current member is the note copy). Fix: anchor to the statement role (FilingSummary MenuCategory "Statements", or a regex that rejects Details|Disclosure|Consolidating|Guarantor|Parenthetical).

## Fixtures
| Fixture | Face (accession, R) | Slot | Verdict |
|---|---|---|---|
| MSFT 2014-12-31 | 8,299 + 1,749 + 18,260 = 28,308 (0001193125-15-020351 R5) | 28,308; securities lending excluded | RIGHT |
| GOOG 2015-09-30 | 3,237 + 1,994 = 5,231 (0001652044-15-000005 R2) | 5,231 | RIGHT |
| AVGO 2019-11-03 | 2,787 + 30,011 = 32,798 (0001730168-19-000144 R2) | members still include the consolidating-note intercompany lines (no facts) -> hard stop | NOT FIXED (blocked, no wrong value) |
| TSLA 2017-12-31 | 796,549 + 9,415,700 + 2,519 + 100,000 + 100 = 10,314,868K (0001564590-18-002956 R2) | solar bonds now members. The VIE-note `LongTermDebtCurrent` member and the custom convertible line have no core.fact fact -> hard stop | value would be right; record still carries the VIE-note member |
| GE 2018-12-31 | consolidated 12,849 + 1,875 + 95,234 = 109,958 (0000040545-19-000014 R4) | both "assumed" lines excluded (right). Missing: guarantor-note member and custom non-recourse -> generic `not_computable_missing_member` | not wrong. NOT flagged as "partial / needs instance reader": there is no such state, only the generic missing member. Note: the latest-filed us-gaap copies sum to 101,725M, not 12,849 + 95,234; a later restated comparative, not traced |
| ABBV 2015-06-30 | 4,007 + 27,116 = 31,123 | 31,123 | RIGHT value. Passed through the circular production-match path, not the filer-aggregate confirmation |

## Fresh draw: `random.Random(20261026)`, excluding every cell read in passes 1-2
Frames: fragment 76 (fresh pool 40), precision 63 (40), composition 70 (47), production-higher 8 (fresh pool 0, all already read). 15 drawn (4/4/4, plus 3 top-ups from fragment/precision/composition because the higher pool was empty).

Slot RIGHT in 15/15:
- CSCO 2024-01-27 11,605; 2024-10-26 31,987; 2025-01-25 31,038 (0000858877-24-000003, -24-000030, -25-000007 R2).
- CVX 2017-12-31 38,763 = 5,192 + 33,477 + 94 (0000093410-18-000010 R5).
- WMT 2020-10-31 50,771 (0000104169-20-000076 R4).
- MRK 2020-09-30 28,741; 2023-12-31 35,055 (0000310158-20-000030 R4; 0001628280-24-006850 R5).
- INTC 2015-09-26 21,188 (0000050863-15-000072 R4).
- COST 2019-05-12 6,498 (0000909832-19-000013 R2).
- UNH 2018-03-31 35,585; 2018-12-31 36,554 (0000731766-18-000018, -19-000005 R2).
- LRCX 2017-03-26, 2018-12-23, 2019-03-31, 2020-12-27 (0000707549-17-000056, -19-000008, -19-000078, -21-000017 R4).

Production wrong in 11: CSCO 3, CVX, WMT (LTD only, 45,207), MRK 2 ($0.1B-rounded), INTC +34, COST +31, UNH 2 (1.3-1.4B low). LRCX 4 are on a borrowings perimeter (perimeter flip).

## Record re-scan (174 records, member roles from the records, cross-checked against the face reads above)
- 8 members sit only on note roles (R3 above). No other member lacks a statement role.
- I did not repeat the face-line coverage scan (V2 found no missing face line; V3 widened the net with `DueToRelatedParties`).
- Custom-tag members that core.fact cannot hold: GE non-recourse 2014-2020, RPAY `LongTermDebtExcludingLineOfCreditNoncurrent`, CAT segment tags pre-2020, KO `ko_LoansAndNotesPayable` 2014-18, TSLA convertible related-party line. These records must hard-stop, or be read from the instance. The W1 rule currently lets them through when production happens to agree.

## Production errors found this pass
- GE 2015-12-31: omits 3,083M non-recourse.
- RPAY 2020-03-31: 5.5M vs 246.5M.
- CSCO, WMT, CVX, MRK, INTC, COST, UNH as listed above.

## Next actions (scrooner-25)
1. Remove the production-match clause from `agrees_lease_inclusive_blank_member`. Accept a blank only from face evidence or the filer's own printed total, and always hard-stop on custom members.
2. Make the statement-role rule reject note roles. Fixtures: AVGO 2019-11-03 (expect 32,798M computable from the face members), TSLA 2016-12..2018-09, GE 2017-2020.
3. Add a distinct state for "needs instance reader (custom member)" (GE, RPAY, CAT, KO 2014-18) instead of the generic missing-member state.
4. Re-run. Then I re-check GE 2015-12-31, RPAY 2020-03-31, AVGO 2019-11-03 and TSLA 2017-12-31.
