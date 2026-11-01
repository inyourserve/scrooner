Under test: loaded production cells in analytics.canonical_fact (no branch). is_core = slot.is_core@1 runs 6dc12c14 / 09bd8b56 at e096f44; capex_da_cash_debt = cells.capex_da_cash_debt@1 run 9f1a0908 at 0161636 (its rule_run.finished_at is NULL). Repo read at 753d56e.
Seed 20261101. Companies: MSFT (CIK 789019) and HD (CIK 354950), 40 cells each. SEC requests: 156 (155 through the rate-limited reader at <= 3.4/s, plus 1 reachability check; 7 of the 155 were retries on a wrong accession guess that returned 404). Verifier session scrooner-c3, read-only (DB reads only, through the Supabase MCP, with statement_timeout set on every query).

# Verify: MSFT and HD, loaded is_core + capex_da_cash_debt (2026-11-01)

Status: **finished.** All 80 drawn cells were opened in their filings, plus one targeted check outside the draw. Nothing blocked the work. One thing needs re-checking: rule_run 9f1a0908 shows no finish time, so confirm the capex load is complete.

## Result

| family | shown checked | right | wrong | blanks drawn | blank reason right | blanks that should have a value |
|---|---|---|---|---|---|---|
| is_core | 37 (HD 21, MSFT 16) | 37 | **0** | 5 (MSFT) | 0 | 5 |
| capex_da_cash_debt | 25 (HD 13, MSFT 12) | 25 | **0** | 13 (HD 6, MSFT 7) | 7 | 6 |
| **total** | **62** | **62** | **0** | **18** | **7** | **11** |

Shown split:
- **is_core HD (21):** 5 FY face, 5 Q face, 6 derived Q4, 5 FY NI from the "restated" stratum.
- **is_core MSFT (16):** 5 FY, 5 Q, 6 derived Q4.
- **capex_da_cash_debt HD (13):** 3 FY capex, 5 Q capex, 5 cash.
- **capex_da_cash_debt MSFT (12):** 3 FY capex, 5 Q capex, 4 cash.

Blank split:
- **is_core (5, all MSFT):** 462046 GP, 462059 NI, 462043 OI, 462066 NI, 462146 cost of revenue. All 5 should have a value.
- **capex_da_cash_debt (13):** HD D&A x6, MSFT D&A x6, MSFT cash 239623. 7 have the right reason: the 6 MSFT D&A and HD 258921. 6 should have a value: 5 HD D&A and MSFT cash.
- **Targeted, outside the draw:** 5 more is_core blanks, MSFT 2016-09-30.

**Wrong shown cells: none.** No shown value differs from its filing. GATE (zero wrong shown values): PASS for both families.

**Blanks that should have a value: 11 in the draw, plus 5 targeted.** They are listed under "Withheld cells (avoidable holds)" below.

## Release recommendation: the 17,981 `held_pending_verifier` capex-family cells

Population, from a live read of analytics.cell_blank_reason: 17,981 cells, 518 companies, 29 runs.
- **D&A: 10,312 cells** (`da_multi_member_unverified`). This includes 158 cells in 14 companies with `da_class=multi_member_ties_is`.
- **Capex: 7,669 cells** (`multi_member_composition_unverified`).
- **No held cell stores a candidate value** (0 of 17,981 have a value in input_refs). So there is no value I could have checked, and "release" would publish numbers no verifier has seen.

**Recommendation: do not release them as a block. Reclassify them first, then release by verified stratum.**

1. **The hold class is wrong for single-line filers.** In my sample, 5 of 6 HD D&A holds are not multi-member: HD's cash-flow statement prints one "Depreciation and amortization" line (DepreciationDepletionAndAmortization) through FY2024. Those cells are a direct face read, or FY minus 9M / 6M minus 3M of that one line. Only FY2025+ HD prints two lines. So `da_multi_member_unverified` was assigned per company, not per filing, and part of the 10,312 is likely the same easy single-line case. I measured this in one company only, so the share is unknown.
2. **Before any release:** the builder recomputes each held cell's class per filing (count the printed D&A/capex lines in that accession's CF R page) and writes the candidate value plus its accession and lines. Single-line cells then become ordinary face cells or derived cells.
3. **Then a verifier draw on candidate values.** Use seed 20261101, about 15 cells per stratum: D&A single-line, D&A two-line summed, D&A `multi_member_ties_is`, capex single-line and capex multi-member. Read each against the R page. Release a stratum only at 0 wrong shown values. Do the `multi_member_ties_is` D&A stratum first (158 cells, ties to the income statement, smallest and best-evidenced). Do multi-member capex last, because capex composition (PP&E plus software, plus or minus non-cash) is a definition question for the Standardization Lead, not a verifier call.
4. **My sample does not support releasing any capex hold.** I drew no held capex cells. HD and MSFT capex were all shown, and all right.

## Method

Cells come from analytics.canonical_fact (rule_run_id not null, families is_core and capex_da_cash_debt). Blanks come from analytics.cell_blank_reason. For every cell I opened the cited accession's FilingSummary.xml and its IS, CF or BS R page on sec.gov. Columns were matched by end date (within 7 days) and by duration ("N Months Ended"), and rows by face label, with the XBRL element recorded. Scale was read from the page header. For derived quarters, both input filings were opened. For blanks, I opened the original filing and the latest later filing that prints the column (Quarterly Information notes in 10-Ks). Values were never taken from core.fact. The reader is filing_kit.parse_rpage plus a raw row and element dump. No cell was a parser disagreement, so nothing needed a hand re-read beyond the capex sign check: outflows print in parentheses and the positive value is correct.

## Sample

The draw was stratified and ordered by md5('20261101:'||id) within each stratum.

| stratum | HD | MSFT |
|---|---|---|
| derived Q4 (FY - 9M) | 6 | 6 |
| "restated/latest" (a later fact for the same period differs) | 6 | 0 (none exist: MSFT's restated periods are blank) |
| FY face, is_core | 5 | 5 |
| FY face, capex | 3 | 3 |
| Q face, is_core | 5 | 5 |
| Q face, capex (3-month column) | 5 | 5 |
| cash (instant) | 4 | 4 |
| blanks with a reason | 6 | 12 |

The HD "restated" stratum turned out not to be restatements. The differing later facts are DEF 14A pay-versus-performance figures rounded to $10M (for example 16,430 vs 16,433), plus one stray 10-Q fact. The shown cells match their 10-K faces.

## Cell table (shown values, all RIGHT)

Values are in $ millions, as printed. Page = R file in the cited accession.

| id | co | concept | period end | shown | accession | page | face |
|---|---|---|---|---|---|---|---|
| 368767684 | HD | cash | 2019-02-03 | 1,778 | 0000354950-19-000010 | R2 | 1,778 |
| 368767711 | HD | cash | 2022-01-30 | 2,343 | 0000354950-22-000070 | R3 | 2,343 |
| 368767729 | HD | cash | 2024-01-28 | 3,760 | 0000354950-24-000062 | R3 | 3,760 |
| 368767735 | HD | cash | 2024-10-27 | 1,531 | 0000354950-24-000240 | R2 | 1,531 |
| 368767670 | HD | cash | 2017-07-30 | 4,830 | 0000354950-17-000032 | R2 | 4,830 |
| 368767655 | HD | capex FY | 2016-01-31 | 1,503 | 0000354950-16-000060 | R8 | (1,503) |
| 368767664 | HD | capex FY | 2017-01-29 | 1,621 | 0000354950-17-000005 | R8 | (1,621) |
| 368767718 | HD | capex FY | 2023-01-29 | 3,119 | 0000354950-23-000059 | R8 | (3,119) |
| 368767640 | HD | capex Q | 2014-05-04 | 287 | 0000354950-14-000017 | R6 | (287) |
| 368767667 | HD | capex Q | 2017-04-30 | 458 | 0000354950-17-000014 | R6 | (458) |
| 368767685 | HD | capex Q | 2019-05-05 | 681 | 0000354950-19-000024 | R7 | (681) |
| 368767703 | HD | capex Q | 2021-05-02 | 524 | 0000354950-21-000147 | R7 | (524) |
| 368767712 | HD | capex Q | 2022-05-01 | 704 | 0000354950-22-000158 | R7 | (704) |
| 369187001 | HD | cost of revenue FY | 2018-01-28 | 66,548 | 0000354950-18-000019 | R4 | 66,548 |
| 369186892 | HD | NI FY | 2019-02-03 | 11,121 | 0000354950-19-000010 | R4 | 11,121 |
| 369186897 | HD | NI FY | 2020-02-02 | 11,242 | 0000354950-20-000015 | R4 | 11,242 |
| 369186964 | HD | GP FY | 2022-01-30 | 50,832 | 0000354950-22-000070 | R5 | 50,832 |
| 369186864 | HD | OI FY | 2026-02-01 | 20,890 | 0001628280-26-019436 | R5 | 20,890 |
| 369186907 | HD | NI FY | 2022-01-30 | 16,433 | 0000354950-22-000070 | R5 | 16,433 |
| 369186912 | HD | NI FY | 2023-01-29 | 17,105 | 0000354950-23-000059 | R5 | 17,105 |
| 369186917 | HD | NI FY | 2024-01-28 | 15,143 | 0000354950-24-000062 | R5 | 15,143 |
| 369186922 | HD | NI FY | 2025-02-02 | 14,806 | 0000354950-25-000085 | R5 | 14,806 |
| 369186927 | HD | NI FY | 2026-02-01 | 14,156 | 0001628280-26-019436 | R5 | 14,156 |
| 369186874 | HD | NI Q | 2014-11-02 | 1,537 | 0000354950-14-000047 | R4 | 1,537 |
| 369186828 | HD | OI Q | 2018-04-29 | 3,381 | 0000354950-18-000034 | R4 | 3,381 |
| 369186836 | HD | OI Q | 2019-11-03 | 3,947 | 0000354950-19-000066 | R4 | 3,947 |
| 369186848 | HD | OI Q | 2022-05-01 | 5,929 | 0000354950-22-000158 | R4 | 5,929 |
| 369186970 | HD | GP Q | 2022-07-31 | 14,483 | 0000354950-22-000193 | R4 | 14,483 |
| 369186875 | HD | NI Q4 derived | 2015-02-01 | 1,379 | -15-000008 R4 / -14-000047 R4 | | 6,345 - 4,966 |
| 369186952 | HD | GP Q4 derived (14 wk) | 2019-02-03 | 9,027 | -19-000010 R4 / -18-000065 R4 | | 37,160 - 28,133 |
| 369186842 | HD | OI Q4 derived | 2021-01-31 | 4,083 | -21-000089 R4 / -20-000103 R4 | | 18,278 - 14,195 |
| 369186784 | HD | revenue Q4 derived | 2022-01-30 | 35,719 | -22-000070 R5 / -21-000234 R4 | | 151,157 - 115,438 |
| 369187039 | HD | cost of revenue Q4 derived | 2025-02-02 | 26,670 | -25-000085 R5 / -24-000240 R4 | | 106,206 - 79,536 |
| 369186799 | HD | revenue Q4 derived | 2025-02-02 | 39,704 | -25-000085 R5 / -24-000240 R4 | | 159,514 - 119,810 |
| 368725805 | MSFT | cash | 2015-09-30 | 5,431 | 0001193125-15-350718 | R5 | 5,431 |
| 368725816 | MSFT | cash | 2016-12-31 | 8,468 | 0001564590-17-000654 | R5 | 8,468 |
| 368725866 | MSFT | cash | 2022-06-30 | 13,931 | 0001564590-22-026876 | R4 | 13,931 |
| 368725872 | MSFT | cash | 2023-03-31 | 26,562 | 0000950170-23-014423 | R4 | 26,562 |
| 368725801 | MSFT | capex FY | 2015-06-30 | 5,944 | 0001193125-15-272806 | R7 | (5,944) |
| 368725882 | MSFT | capex FY | 2024-06-30 | 44,477 | 0000950170-24-087843 | R6 | (44,477) |
| 368725900 | MSFT | capex FY | 2026-06-30 | 115,948 | 0001193125-26-323660 | R6 | (115,948) |
| 368725815 | MSFT | capex Q | 2016-12-31 | 1,988 | 0001564590-17-000654 | R7 (3-month col) | (1,988) |
| 368725844 | MSFT | capex Q | 2020-03-31 | 3,767 | 0001564590-20-019706 | R6 | (3,767) |
| 368725871 | MSFT | capex Q | 2023-03-31 | 6,607 | 0000950170-23-014423 | R6 | (6,607) |
| 368725878 | MSFT | capex Q | 2023-12-31 | 9,735 | 0000950170-24-008814 | R6 | (9,735) |
| 368725898 | MSFT | capex Q | 2026-03-31 | 30,876 | 0001193125-26-191507 | R6 | (30,876) |
| 369158197 | MSFT | revenue FY | 2014-06-30 | 86,833 | 0001193125-14-289961 | R2 | 86,833 |
| 369158321 | MSFT | revenue FY | 2019-06-30 | 125,843 | 0001564590-19-027952 | R2 | 125,843 |
| 369158569 | MSFT | cost of revenue FY | 2024-06-30 | 74,114 | 0000950170-24-087843 | R2 | 74,114 |
| 369158519 | MSFT | GP FY | 2026-06-30 | 225,465 | 0001193125-26-323660 | R2 | 225,465 |
| 369158412 | MSFT | OI FY | 2026-06-30 | 155,237 | 0001193125-26-323660 | R2 | 155,237 |
| 369158424 | MSFT | NI Q | 2016-03-31 | 3,756 | 0001193125-16-550254 | R2 | 3,756 |
| 369158323 | MSFT | revenue Q | 2019-03-31 | 30,571 | 0001564590-19-012709 | R2 | 30,571 |
| 369158389 | MSFT | OI Q | 2021-03-31 | 17,048 | 0001564590-21-020891 | R2 | 17,048 |
| 369158338 | MSFT | revenue Q | 2022-03-31 | 49,360 | 0001564590-22-015675 | R2 | 49,360 |
| 369158568 | MSFT | cost of revenue Q | 2023-09-30 | 16,302 | 0000950170-23-054855 | R2 | 16,302 |
| 369158257 | MSFT | revenue Q4 derived | 2014-06-30 | 23,382 | -14-289961 R2 / -14-157088 R2 | | 86,833 - 63,451 (also printed: R128 Quarterly Information 23,382) |
| 369158423 | MSFT | NI Q4 derived | 2015-06-30 | -3,195 | -15-272806 R2 / -15-144151 R2 | | 12,193 - 15,388 (also printed: R131 (3,195)) |
| 369158444 | MSFT | NI Q4 derived | 2021-06-30 | 16,458 | -21-039151 R2 / -21-020891 R2 | | 61,271 - 44,813 |
| 369158502 | MSFT | GP Q4 derived | 2022-06-30 | 35,436 | -22-026876 R2 / -22-015675 R2 | | 135,620 - 100,184 |
| 369158400 | MSFT | OI Q4 derived | 2023-06-30 | 24,254 | 0000950170-23-035122 R2 / -23-014423 R2 | | 88,523 - 64,269 |
| 369158464 | MSFT | NI Q4 derived | 2025-06-30 | 27,233 | 0000950170-25-100235 R2 / -25-061046 R2 | | 101,832 - 74,599 |

## Withheld cells (avoidable holds): blanks the filing gives a value for

| blank id | co | data point | period | reason given | what the filing shows |
|---|---|---|---|---|---|
| 258839 | HD | D&A Q | 2016-05-01 | held_pending_verifier ("sum of several printed lines") | One line, "Depreciation and Amortization" (DepreciationDepletionAndAmortization): 486. 0000354950-16-000065 R6, 3-month column |
| 258894 | HD | D&A Q | 2016-07-31 | same | One line: 6M 978 (0000354950-16-000082 R6) - Q1 486 = 492 |
| 258908 | HD | D&A Q4 | 2021-01-31 | same | One line: FY 2,519 (0000354950-21-000089 R7) - 9M 1,853 (0000354950-20-000103 R7) = 666 |
| 258848 | HD | D&A FY | 2021-01-31 | same | One line: 2,519. 0000354950-21-000089 R7 |
| 258855 | HD | D&A Q | 2024-04-28 | same | One line: 837. 0000354950-24-000152 R7 (re-printed as 785 + 52 intangibles in 0000354950-25-000165 R7, sum 837) |
| 462046 | MSFT | GP Q4 | 2014-06-30 | mixed_vintage | Printed 3-month column, not derived. Original 15,787 (0001193125-14-289961 R128 Quarterly Information). **Latest print 15,749** (0001193125-15-272806 R131, recast) |
| 462059 | MSFT | NI FY | 2016-06-30 | restated_copies_disagree | Original 16,798 (0001193125-16-662209 R2). **Latest print 20,539** (0001564590-18-019062 R2, ASC 606 restated) |
| 462043 | MSFT | OI Q4 | 2017-06-30 | mixed_vintage | Printed 3-month column. Original 5,330 (0001564590-17-014900 R127). **Latest print 7,682** (0001564590-18-019062 R125) |
| 462066 | MSFT | NI Q | 2026-09-30 | no_filed_column_for_period | 36,629. 10-Q 0001193125-26-436133 R2, filed 2026-10-28, already in core.filing |
| 462146 | MSFT | cost of revenue Q | 2026-09-30 | no_filed_column_for_period | 29,720 total (2,471 product + 27,249 service). Same 10-Q, R2 |
| 239623 | MSFT | cash | 2026-09-30 | not_captured | 20,281. Same 10-Q, R4 |

Under decision 02 (2026-11-01 FSN store, rule 3: "the winner for a cell is the latest accepted print"), the three MSFT restatement cells should show the latest print. `restated_copies_disagree` and `mixed_vintage` do not apply when a later filing prints the column.

**Targeted, outside the seed.** MSFT 2016-09-30 Q (revenue, cost of revenue, GP, OI, NI) is blank with `no_filed_column_for_period`. The 10-Q 0001193125-16-742796 R2 prints the 3-month column: 20,453 / 7,844 / 12,609 / 5,225 / 4,690. The latest print, 0001564590-18-019062 R125 (restated), gives revenue 21,928, GP 14,084, OI 6,715, NI 5,667. The same reason sits on MSFT capex Q 2016-09-30 (`value_lineage_unresolved`, not opened).

## False holds and correct blanks

- MSFT D&A, 6 of 6 correct (239481, 239421, 239441, 239498, 239445, 239450). Each CF page prints only "Depreciation, amortization, and other" (msft_DepreciationAmortizationAndOther): 0001193125-14-380252 R7, 0001193125-15-144151 R7, 0001564590-22-002324 R6, 0001564590-22-035087 R6, 0000950170-23-014423 R6, 0000950170-25-010491 R6. This is a combined line, so `line_presented_combined_with_others` is right.
- HD D&A Q 2025-08-03 (258921): the reason is accurate. From FY2025 HD prints two lines: "Depreciation and amortization, excluding amortization of intangible assets" (DepreciationDepletionAndAmortization) and "Intangible asset amortization". If the two lines are accepted as a sum, the value is 6M (1,720 + 278) - Q1 (855 + 139) = 1,004 (0000354950-25-000217 R7, 0000354950-25-000165 R7).

## Findings for the builder

1. HD D&A: the `da_multi_member_unverified` hold is applied to all 63 HD D&A cells. HD prints a single D&A line through FY2024, so those cells are avoidable holds. Only from FY2025 does HD split out intangible amortization. Action: classify per filing by the printed lines, not per company. Re-verify: the 5 cells above plus a FY2025 cell.
2. MSFT restatements: `restated_copies_disagree` and `mixed_vintage` blank cells where a later accepted print exists. That contradicts rule 3, which says the latest print wins. The 10-K Quarterly Information note is a printed 3-month column (R128, R125, R131). Action: take the latest print, and read the 10-K Quarterly Information R page as a quarter source. Re-verify: 462046, 462059, 462043, and all MSFT FY2016-FY2017 cells.
3. `no_filed_column_for_period` is false for MSFT 2016-09-30 (the 10-Q face prints it) and for 2026-09-30 (filed 2026-10-28, before the load). The 2026-09-30 case probably means the FSN quarterly set does not contain the filing yet. Action: the reason should say "filing newer than the FSN set" (or fill it from the filing), and the 2016-09-30 lineage needs a look. Re-verify: these six cells.
4. capex_da_cash_debt: the capex_da_cash_debt run (9f1a0908) has `finished_at` NULL in analytics.rule_run, although its cells are live. Check that the run completed.
5. No D&A or debt cells are shown for MSFT and HD in capex_da_cash_debt. Only capex and cash are loaded for these two, so the "D&A" and "debt" parts of the family were not testable here.

## Requests and disk

There were 156 sec.gov requests: 155 through a rate-limited reader (0.3 s spacing) and 1 reachability check. 7 of the 155 were retries on a 404 from a wrongly guessed HD accession. Downloads were cached in the session scratchpad and deleted at the end. No pipeline/.env exists in this container. The User-Agent is the repo's declared one from doc/data-moat/team/top1000/tools/sec_rpages.py.

## Untested scope

- Only the cited accession was checked for each shown cell. I did not check whether a later print exists with a different value for shown cells; the sampled faces agree with comparatives seen incidentally.
- Debt and D&A shown values were not tested (none loaded for MSFT or HD). There were no MSFT "restated" shown cells to test. Other companies were not sampled.
- The cell_proof verdicts were not read.
