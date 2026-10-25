# Verifier: 30-company debt slot records V4 (scrooner-25, 9696f27), 2026-10-24

Role: Data Verifier (Verifier 3). Object: V4 records (`results/thirty_debt_records_v2.jsonl`, 173 records; the hand-off said 174) and `results/replay30_v2_report.json` @ 9696f27. Read-only, no DB. SEC: about 420 requests at most 1.7 req/s with `SEC_USER_AGENT`, one process. Downloads deleted at the end; free disk 8 GB or more.
To find candidate filings for the rule test I used scrooner-25's FSDS cohort extract (`fsds_cohort/cohort_pre_rows.jsonl.gz`, 1,000 companies). It served only as a locator; every verdict below rests on the filing's R page and `_cal.xml`.

## Verdict: GATE FAILED (1 wrong slot value); the new face-admission rule is UNSOUND as written
- Custom-tag gate: PASS. Every record with a custom member (CAT pre-2020-09, KO 2014-18, GE non-recourse, TSLA, RPAY; 24 records) carries `custom: true`, and every replay cell that touches one is `needs_instance_reader`.
- Caveat on that state: those cells still carry a partial `slot_lease_inclusive` (GE 2015-12-31 194,519M, RPAY 2020-03-31 5.5M). Null the value in that state so no consumer can publish it.
- Note-role members: none remain.

### W1: COST 2018-09-02 slot 6,487M is wrong; the correct value is 6,577M (production is right)
- The FY2018 10-K face shows only "Long-term debt, excluding current portion" 6,487 (0000909832-18-000013 R2). The 90M current portion sits inside another current line.
- The debt note gives total carrying value 6,577 = 90 current + 6,487 (R39). The next 10-Q prints "Current portion of long-term debt" 90 for 2018-09-02 (0000909832-19-000003 R2).
- The era record (members: `LongTermDebtNoncurrent` only) cannot see a current-maturity balance that the face folds into another line.
- Rule: compare the era's sum with the filer's own debt-note total (`LongTermDebt` carrying value plus short-term borrowings) and flag a gap. Do not take the face alone as complete.
- This does not change my V2 verdict on COST 2018-11-25: slot 6,480 is right there (current portion 0; production's 6,514M is face value before 34M of issuance costs; 0000909832-18-000022 R32).

## Fixtures
| Fixture | Face (R) | V4 state / slot | Verdict |
|---|---|---|---|
| GE 2015-12-31 | 49,860 + 3,083 (custom non-recourse) + 144,659 = 197,602M (0000040545-17-000010 R5) | `needs_instance_reader` | RIGHT state (custom member). Null the partial 194,519 |
| RPAY 2020-03-31 | 5,502K + 240,955K (custom LTD) = 246.5M (0001564590-20-024317 R2) | `needs_instance_reader` | RIGHT state. Null the partial 5.5M |
| AVGO 2019-11-03 | 2,787 + 30,011 = 32,798M (0001730168-19-000144 R2) | 32,798M (`LongTermDebtCurrent` admitted from the face) | RIGHT |
| TSLA 2017-12-31 | 10,314,868K (0001564590-18-002956 R2) | `needs_instance_reader` (custom related-party convertible line) | RIGHT state; the VIE-note member is gone |
| MSFT 2014-12-31 | 28,308M (0001193125-15-020351 R5) | 28,308M | RIGHT |
| GOOG 2015-09-30 | 5,231M (0001652044-15-000005 R2) | 5,231M | RIGHT |
| ABBV 2015-06-30 | 4,007 + 27,116 = 31,123M, short-term row blank (0001104659-15-057641 R5) | `not_computable_missing_member` | Honest hard stop (no printed filer total exists to confirm the blank). The value would be right |

## (a) The `face_line_not_in_statement_cal` rule
Method: I simulated the rule per filing (statement-role cal children of the four liability parents vs. standard face debt lines with a side by name) and judged each admitted line on the R page. In the 33-company set the rule fires once (AVGO 2018-04..2021-01), and correctly.

**Admits correctly (6 filings):**
- AVGO 0001730168-18-000019 R2: "Current portion of long-term debt" 117.
- LMCA 0001558370-19-007718 and -19-010666 R2: debt rows under an empty cal; the consolidated undimensioned row is right.
- Allison 1411207 0001193125-25-257624 R2: LTD current 5 + noncurrent 2,393, no cal file.
- Antero 0001558370-17-003802 R2: long-term debt 4,775,302K.
- NFG 0000070145-19-000013 R4: "Long-Term Debt, Net of Current Portion" 2,132,488K, under `CapitalizationLongtermDebtAndEquity`.
- EW 0001099800-16-000044 R2: "Accounts receivable securitization program" 430 and "Long-term debt due currently" 161.

**Admits WRONGLY (6 filings):**
1. **Component under a face subtotal (double count).** CenterPoint 0001130310-26-000008 R6: "Other long-term debt, net" 19,902 (`OtherLongTermDebtNoncurrent`) is part of "Total long-term debt, net" 20,566, which is a member. Dominion 0001193125-15-363617 R6: "Long-term debt" 19,790 is part of "Total long-term debt" 23,245. Watsco 0001193125-25-041730 R4: revolver 0 and finance leases 15,475 are parts of "Total long-term obligations" 337,190. That WSO total also contains 321,715 of operating leases, so the member itself is wrong too.
2. **A total row admitted beside its own parts.** ICE 0001571949-17-000003 R2: `LongTermDebt` 6,364 = 2,493 + 3,871 (both members). Textron 0000217346-21-000019 R4: `LongTermDebt` 3,707 = 509 + 3,198 in the Manufacturing block.
3. **Asset-side line with a debt-like name.** NFG 0000070145-19-000013 R4: "Unamortized Debt Expense" 14,922 (`UnamortizedLossReacquiredDebtNoncurrent`) sits above Total Assets, yet it would be admitted as noncurrent debt.

Also: `...Abstract` header rows (KMI, CNP, D, PSEG, WSO) match the net and would be admitted with no fact, turning a computable cell into a hard stop.

**Required guards before the rule is used beyond AVGO:**
- (i) Admit only rows between total assets and total liabilities (or liabilities and equity).
- (ii) Never admit a row whose presentation parent or next total row is itself a member, and never a row equal to the sum of members.
- (iii) Skip `Abstract` tags.
- (iv) Tie admitted + members + other face liability rows to the printed LiabilitiesCurrent / Liabilities totals, or hold.

## (b) Fresh draw (`random.Random(20261027)`, excluding every cell read in passes 1-3)
Frames: fragment 76 (fresh pool 35), precision 63 (35), composition 70 (42), production-higher 8 (pool 0).

Replay cells (10), slot right in 9 of 10:
- CVX 2015-06-30 31,910 (0000093410-15-000031 R5); 2021-12-31 31,369 (0000093410-22-000019 R5).
- CSCO 2019-04-27 23,698; 2026-01-24 30,086 (0000858877-19-000007, -26-000021 R2).
- LRCX 2016-12-25 2,726,608K (0000707549-17-000010 R4).
- MRK 2022-06-30 31,663 (0000310158-22-000030 R4).
- INTC 2016-10-01 27,616 (0000050863-16-000153 R4).
- JNJ 2024-12-29 36,634 (0000200406-25-000038 R3).
- UNH 2017-12-31 31,692 (0000731766-18-000005 R2).
- **COST 2018-09-02 WRONG (W1).**

Production wrong in 9 of 10: right only at COST 2018-09-02; the LRCX cell is its borrowings-only perimeter.

Custom-tag companies (5 record cells, no replay cells exist): the face lines are custom on the R page, the record flags each one `custom: true`, so the state is `needs_instance_reader`. Right in 5 of 5:
- KO 2016-12-31 and 2017-06-30: `ko_LoansAndNotesPayable` 12,498 and 14,355 (0000021344-17-000009, -17-000026 R4).
- CAT 2016-12-31 and 2019-06-30: 6 `cat_` segment lines each (0000018230-17-000041 R5, -19-000224 R6).
- TSLA 2015-06-30: `tsla_ConvertibleNotesAndOtherDebtPayable*` 632,162K + 1,988,089K (0001564590-15-006666 R2).

## (c) Re-scan of all 173 records (from the records' own role and custom fields)
- 0 members sit only on note roles.
- 24 records carry custom members, all flagged.
- 0 members lack the custom key.
- 1 face-admitted member (AVGO), right.
- I did not repeat the face-line coverage scan (V2 found no missing line).

## Production errors found this pass
- CVX 2015 and 2021 (LongTermDebt pattern).
- CSCO 2019 and 2026 (drops short-term debt).
- MRK ($0.1B rounding).
- INTC +65M.
- JNJ +1,749M.
- UNH -625M.
- COST 2018-11-25 face value instead of carrying value.

## Next actions (scrooner-25)
1. Add the four guards to `face_line_not_in_statement_cal`. Fixtures: CNP 0001130310-26-000008, D 0001193125-15-363617, WSO 0001193125-25-041730, ICE 0001571949-17-000003, TXT 0000217346-21-000019, NFG 0000070145-19-000013 (must not admit) and AVGO, LMCA, Allison, AR, EW (must admit).
2. Debt-note tie-out per cell: era sum vs. the filer's `LongTermDebt` carrying total plus short-term lines; a gap goes to review (COST 2018-09-02).
3. Null `slot_lease_inclusive` in the `needs_instance_reader` state.
4. Re-run; I then re-check COST 2018-09-02 and the 12 rule fixtures.
