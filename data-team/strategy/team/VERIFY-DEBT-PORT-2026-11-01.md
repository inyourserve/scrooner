Under test: origin/work/balance-sheet/fsn-port-fixes 362b391 (gate pins: pipeline/scripts/slot_records/results/bs_port_gate_2026-11-01/expected_diffs.json). Baselines: report_v4.json and bs_records_v3.jsonl on main.
Seed 20261101 (md5('20261101:'+key), distinct keys per class). Drawn: restated 8, verdict_differs 8, note_lease_differs 5 (all distinct keys in the class), overlap_removed 8, equity_block_guard 8. SEC requests: 265 (sec.gov only, <= 3.4/s). Verifier session scrooner-c3, read-only.

# Verify: balance-sheet/debt FSN port, the five changed classes (2026-11-01)

## Result in one paragraph

**Status: partly BLOCKED.**
- **The new debt values are not graded.** The port's new values are not committed anywhere. Only their SHA-256 pins are (`gate/new/debt_replay.json`, `gate/company/debt_records.jsonl`, `bs_records.jsonl` in outputs.sha256), and expected_diffs.json holds only key, class and reason. So I cannot say right or wrong for most new values.
- **What I did instead.** For every drawn cell I opened the filing the port's rule selects (the latest accepted print of the instant on a balance-sheet face) and wrote down the value the port should produce. The **"Correct value"** column below is filing-checked. Grading the port becomes a lookup once the outputs are published.
- **Equity-block guard, graded fully** (it is a classification question the face answers): **7 of 7 utility reclasses are WRONG; 1 not graded.**
- **The one new value I can see is right:** WMT 2026-01-31 = 51,523 (stated in BS-PORT-FIXES §3).
- **Four traps the outputs must be checked against:**
  - **META 2018-12-31:** a filer context error would put 418 where 0 is correct.
  - **NVDA 2017-01-29:** the latest copy hides the noncurrent capital lease (6).
  - **AMZN 2016-12-31:** v4 used gross lease payments.
  - **GOOG 2024-12-31:** v4 missed 1,677 of finance leases.

## What is needed to finish

**Builder: commit or publish the outputs pinned in outputs.sha256** (`gate/new/debt_replay.json`, `gate/company/debt_records.jsonl`, `gate/company/bs_records.jsonl`) at 362b391. With them, each row below takes seconds.

## 1. latest_accepted_print_restated (45 cells; 8 drawn)

All values in $ millions (KKR in $ thousands). "First copy" is the face sum in the period's own filing. "Correct value" is the face sum in the latest accepted filing that prints the instant.

| key | first copy (accession, page) | correct value under rule 3 (accession, page) | note |
|---|---|---|---|
| DVN 2017-12-31 | 115 + 10,291 = 10,406 (0001564590-18-002582 R4) | **115 + 6,749 = 6,864** (0001564590-19-003382 R4) | Long-term debt falls by 3,542 in the 2018 10-K comparative because EnLink is recast as held for sale/discontinued. This follows rule 3, but it is a basis change (consolidated debt to continuing operations). Flag it to the Standardization Lead. |
| AAPL 2015-09-26 | 8,499 + 2,500 + 53,463 = 64,462 (0001193125-15-356351 R5) | **8,499 + 2,500 + 53,329 = 64,328** (0001628280-16-020309 R5) | Debt issuance cost reclass (ASU 2015-03) |
| EMR 2015-09-30 | 2,553 + 4,289 = 6,842 (0000032604-15-000051 R5) | **2,552 + 4,289 = 6,841** (0000032604-16-000105 R5) | |
| KKR 2015-12-31 | 18,730,017 ($K) (0001404912-16-000009 R2, first block) | **18,714,597** ($K) (0001404912-17-000005 R2, first block) | ASU 2015-03. Read the consolidated block, not the later VIE blocks |
| AMZN 2016-12-31 | 7,694 + current portion 1,056 + capital lease PV 9,077 = 17,827 (0001018724-17-000011 R6, R48, R51) | **7,694 + 1,056 + capital lease 4,000 current + 5,080 long-term = 17,830**; borrowings 8,750 (0001018724-18-000005 R6, R63, R65, R66) | **v4 had 18,156 and was wrong by 329.** It added 9,406, which is AMZN's GROSS minimum payments tagged `CapitalLeaseObligations` (R51: gross 9,406, imputed interest 329, PV 9,077). The new value must not use 9,406. |
| AJG 2015-12-31 | 245 + 2,075.0 = 2,320.0 (2,457.0 with premium financing 137) (0001193125-16-457703 R4) | **245 + 2,071.7 = 2,316.7** (2,453.7 with premium financing) (0001193125-17-038619 R4) | Whether premium financing borrowings count as debt follows the record's members. Either way, 3.3 lower. |
| BRKR 2015-12-31 | 0.7 + 266.0 = 266.7 (0001047469-16-010532 R2) | **0.6 + 265.2 = 265.8** (0001047469-17-001114 R2) | The 10-K/A 0001047469-16-016725 has no XBRL statements (no FilingSummary), so it is correctly not a candidate |
| HD 2016-01-31 | 350 + 77 + 20,888 = 21,315 (= v4) (0000354950-16-000060 R2) | **350 + 77 + 20,789 = 21,216** (0000354950-17-000005 R2) | |

## 2. latest_accepted_print_verdict_differs (62 cells; 8 drawn)

I cannot see the new verdicts. The face facts below are what any verdict must be consistent with.

| key | latest accepted face (accession, page) | finding |
|---|---|---|
| META 2025-12-31 | The 10-Q 0001628280-26-066773 R2 prints the 2025-12-31 column: long-term debt 58,744. It has no lease detail page. | This is the new `latest_copy_lacks_note_finance_lease` blank. The 10-K 0001628280-26-003942 R61 prints FinanceLeaseLiability 1,184 at that date, giving 58,744 + 1,184 = **59,928**. The 10-Q does not contradict the 10-K note; it only omits it. **My reading: avoidable hold.** Design §4 is about not swapping in an older value for a fact the latest copy prints; it should not blank a fact the latest copy simply does not repeat. This answers BS-PORT-FIXES §4 item 2. **Founder or Dhairya to rule.** |
| META 2022-12-31 | 9,923 + FinanceLeaseLiability **690** (current 90, noncurrent 600) (0001326801-24-000012 R3, R64) = **10,613** | The first copy has 687 (129/558), 0001326801-23-000013 R65. The later 10-K recast the lease split. The correct value is 10,613, not 10,610 |
| NI 2024-12-31 | 604.6 + 1,281.2 + 12,074.5 = **13,960.3** (0001111711-26-000027 R6), same as the first copy | Capitalization-format utility. If the new verdict is a hold, it is the equity-block guard (section 5), not a value problem |
| DIS 2025-09-27 | The 10-Q 0001744489-26-000057 R4 prints 6,711 + 35,315 = **42,026**, same as the 10-K | Lease note not read. If the verdict is `latest_copy_lacks_note_finance_lease`, the same ruling as META 2025 applies |
| ET 2022-12-31 | 2 + 48,260 = **48,262** in both copies (0001276187-24-000024 R2) | No value change. The verdict change must come from the record or face test. Not graded |
| MSFT 2015-06-30 | 4,985 + 2,499 + 27,808 = **35,292** in both copies (0001193125-16-662209 R5) | Equals v4. Not graded |
| BX 2018-12-31 | Total Liabilities 15,170,564 ($K) in both copies | My reader did not capture BX's "Loans Payable" line. Not graded |
| GE 2019-12-31 | Multi-block face (GE, GE Capital, consolidated). My column pick was inconsistent | Needs a hand read. Not graded |

## 3. latest_accepted_print_note_lease_differs (7 rows = 5 distinct keys; all drawn)

| key | correct value | evidence | finding |
|---|---|---|---|
| **META 2018-12-31** | **0** (no debt, no finance lease) | 0001326801-19-000009 R2 has no debt line. The FY2019 10-K 0001326801-20-000013 R49 shows financing cash flows from finance leases of 0 for 2018 (ASC 842 adopted 2019-01-01) | **Trap.** In R47 of the FY2019 10-K, "Lease liabilities, non-current $418" sits in the **Dec. 31, 2018** column, but 473 = 55 + 418 is the 2019 total. This is a filer context error. **If the port now shows 418 for 2018-12-31, it is WRONG.** The class name ("the latest copy's note lease differs") suggests it does. |
| MSFT 2017-06-30 | **9,072 + 1,049 + 76,073 + 2,538 = 88,732** | 0001564590-18-019062 R4 face, R103 total finance lease liabilities 2,538 at 2017-06-30 (ASC 842 retrospective) | v4 had 86,194 (the first copy had no finance-lease liability). The latest copy gives 88,732. Right under rule 3 if the port adds 2,538 |
| GOOG 2024-12-31 | **10,883 + 999 + 1,677 = 13,559**; borrowings 11,882 | 0001652044-26-000018 R3 (face 10,883, now tagged LongTermDebtNoncurrent), R67 (face value 12,000, current 999, net 10,883), R61 (finance lease 1,677 = 235 + 1,442 in "accrued expenses" and "other long-term liabilities") | **v4 (11,882) was wrong by 1,677.** The debt note shows 10,883 is notes only, so the leases sit outside it. 13,559 is right. Note: the first copy ALSO prints 1,677 (0001652044-25-000014 R61). Its combined face tag blocked the add, not a missing fact |
| NVDA 2017-01-29 | **796 + 1,983 + 6 + 4 = 2,789** | First copy 0001045810-17-000027 R4 (capital lease noncurrent 6 on the face), R50 (current 4) | **Trap.** The latest copy 0001045810-18-000010 R4 no longer prints the capital-lease line, and R49 shows only "leases payable" 4. A port that reads only the latest copy gives 2,783, **wrong by 6**. v4 (2,795) was wrong by +6 (double count) |
| ET 2015-12-31 | not graded | No finance-lease fact found in either copy's lease pages | Needs the port's note source |

## 4. note_finance_lease_overlap_removed (17 cells; 8 drawn)

The arithmetic of the fix is confirmed against the face. The face already carries finance-lease members, so the note adds only what no member carries.

| key | correct value (face) | old value | page |
|---|---|---|---|
| WMT 2021-01-31 | 224 + 3,115 + 491 + 41,194 + 3,847 = **48,871** | about 53,209 (+ note total) | 0000104169-21-000033 R4 = 0000104169-22-000012 R5 |
| WMT 2023-01-31 | 372 + 4,191 + 567 + 34,649 + 4,843 = **44,622** | about +5,410 | 0000104169-23-000020 R5 = -24-000056 R5 |
| WMT 2024-01-31 | 878 + 3,447 + 725 + 36,132 + 5,709 = **46,891** | about +6,434 | 0000104169-24-000056 R5 = -25-000021 R5 |
| WMT 2026-01-31 | 6,596 + 3,542 + 856 + 34,624 + 5,905 = **51,523**. **The port's stated value 51,523 is RIGHT** | 58,284 (wrong; +6,761 = 856 + 5,905 counted twice) | 0000104169-26-000055 R5; latest 10-Q 0000104169-26-000154 R4 identical |
| NVDA 2016-01-31 | 1,413 + 0 + 10 + current 4 = **1,427** | v4 1,437 | 0001045810-16-000205 R4; current 4 from 0001045810-17-000027 R50 |
| NVDA 2017-01-29 | **2,789** (see 3) | v4 2,795 | as above |
| NVDA 2017-04-30 | 215 + 1,984 + 4 + current 5 = **2,208** | v4 2,212 | 0001045810-17-000075 R4, R40 |
| NVDA 2017-07-30 | 84 + 1,984 + 3 + current 5 = **2,076** | v4 2,079 | 0001045810-17-000123 R4, R40 |

## 5. equity_block_guard (76 records; 8 drawn): 7 WRONG, 1 not graded

The guard treats a liability line that prints after the equity block as an equity component until "Total capitalization". At capitalization-format utilities, long-term debt prints exactly there: after common equity and inside Total capitalization. It is still debt, a liability. In every sampled filing the v3 member set ties to the face, and the guard's reclass breaks it.

| record (cik, accession) | face (page) | tie with LTD as a liability | verdict on the reclass |
|---|---|---|---|
| NI 0001111711-17-000032 | R5: equity 4,191.1, LTD 5,590.7, Total Capitalization 9,781.8, current 3,664.1, other 5,190.0, total 18,635.9 | 4,191.1 + 5,590.7 = 9,781.8; 9,781.8 + 3,664.1 + 5,190.0 = 18,635.9 | **WRONG** |
| NI 0001111711-18-000021 | R5: 4,506.2 / 7,286.8 / 11,793.0 / 3,226.2 / 5,079.3 / 20,098.5 | ties | **WRONG** |
| NI 0001111711-19-000022 | R5: 5,779.6 (incl. preferred 880) / 7,110.1 / 12,889.7 / 4,015.2 / 4,985.0 / 21,889.9 | ties | **WRONG** |
| FE 0001031296-17-000056 | R5: equity 6,406, LTD 21,089, total capitalization 27,495 | 6,406 + 21,089 = 27,495 | **WRONG** |
| FE 0001031296-18-000015 | R5: 3,925 / 21,115 / 25,040 | ties | **WRONG** |
| FE 0001031296-20-000016 | R4: 6,814 / 20,821 / 27,635 | ties | **WRONG** |
| AWK 0001564590-15-003448 | R2 ($K): equity 4,992,938, LTD 5,428,901, redeemable preferred 14,296, total capitalization 10,436,135 | ties | **WRONG** |
| BX 0001193125-26-082531 (`record_split_by_equity_block_guard`) | R2 prints Total Liabilities 25,827,803 directly, with redeemable NCI after it | No capitalization block | Not graded (the new record is unseen). Any record that does not give 25,827,803 is wrong |

These fail safe: the builder says the identity tie then withholds the cell. So they are **false holds, not wrong shown values**. Action: end the guard's equity block at the first "Total capitalization" or `CapitalizationLongtermDebtAndEquity` subtotal, and keep debt-tagged lines (`LongTermDebt*`, `*CapitalLeaseObligations`) as liabilities inside it. Re-verify: these 7 records plus 5 more NI/AWK/FE records.

## Findings for the builder

1. Publish the pinned outputs. Then grade sections 1-4 against the "Correct value" column.
2. **META 2018-12-31:** guard against note facts whose instant has no matching face column or cash-flow support (filer context error 418, 0001326801-20-000013 R47).
3. **NVDA 2017-01-29:** when the latest copy drops a face lease line that an earlier copy printed, do not let the total fall by that amount.
4. **AMZN 2015-2016:** `CapitalLeaseObligations` holds GROSS payments in AMZN's notes (R51). Use the present value, or current + long-term.
5. **`latest_copy_lacks_note_finance_lease`:** my reading is that this is an avoidable hold when the latest copy is a 10-Q that does not repeat the 10-K note (META 2025-12-31). This needs a ruling.
6. **Equity-block guard:** 7/7 wrong. Fix as in section 5.
7. **DVN 2017:** the latest print changes the basis (discontinued operations). Ask the Standardization Lead whether rule 3 should apply to such recasts.

## Requests and disk

265 sec.gov requests through the rate-limited reader (0.3 s spacing). Downloads were deleted at the end. No database reads or writes for this verdict; inputs came from git only.

## Untested scope

- The new values themselves, for every class except WMT 2026-01-31.
- Verdict class: ET, MSFT 2015, BX and GE were not graded.
- Lease class: ET 2015 was not graded.
- The 268 same-value cells, the 103 covering-record cells, the A1 window cells and the D era classes were not drawn.
