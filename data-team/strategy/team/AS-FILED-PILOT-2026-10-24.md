# As-filed face-statement extractor: prototype and measurement (2026-10-24)

Role: Data Engineer. Read-only (no DB writes, no migration). Branch `work/data-engineer/as-filed-pilot` off origin/main. Code: `pipeline/scripts/as_filed_pilot/` (stdlib parser, run with `python3 -I`). Small results tables: `pipeline/scripts/as_filed_pilot/results/*.csv`. Raw extractions stayed in the scratchpad (3.3 MB gz, not committed).

Labels: FC = FILING-CHECKED (read from the filing's own SEC data: FSDS built from the filing's XBRL, or the filing's `_cal.xml`), DI = DATA-INFERRED.

## 1. Route chosen and why
SEC Financial Statement Data Sets (FSDS) quarterly zips, not per-filing instances. One request per quarter (47 requests for 2015q1-2026q3) gives `sub` (filing), `pre` (statement, report, line, label, parenthetical flag, negating), `num` (value, end date, quarters, unit, dimension members) for every filing, against about 4 requests per filing for instance + presentation + calculation (about 1,800 for 453 filings). Cost of the choice, all FC and listed in section 6: month-rounded dates, 4-decimal values, no calculation linkbase, face statements only.

Extractor output per (presentation line x fact): tag, taxonomy/version, custom flag, label, value, end, quarters (start is derived, approximate), unit, dimension members, statement (BS/IS/CF), report, line, parenthetical flag, negating flag, `is_total` (heuristic), filing form/period/fy/fp/filed.

## 2. Run measures
| Item | Value |
|---|---|
| Filings parsed | 461 (346 10-Q, 115 10-K), all 10 companies, 2015Q1 to 2026Q3 filings |
| SEC requests | 47 FSDS zips + 1 test + 4 extra FSDS (ABBV, CVX) + 16 (8 filings: index + cal) = 68 |
| Bytes / time | 4.41 GB downloaded, 1,242 s of download, about 27 min wall for the 47-quarter loop; parse about 6 s per quarter |
| Rate / process | 4 req/s ceiling through the shared `CrossProcessRateLimiter`, one process, declared User-Agent |
| Disk | one zip at a time, deleted after use; free space never below 6.9 GB |
| Output | 98,711 non-dimensioned face facts (BS/IS/CF), 3.3 MB gz |
| Face facts per filing | about 214 non-dimensioned (BS+IS+CF, all period columns) |

Filing coverage vs `core.filing` (467 10-K/10-Q/10-K/A/10-Q/A since 2015-01-01): 453 matched. Not in FSDS, 14: 9 amendments (5 TSLA Part III 10-K/A, GOOG x2, META x2 10-K/A, MU 10-Q/A; none has statements), 4 filed after the newest FSDS quarter (MU 10-K 2026-10-09, TSLA and META 10-Q 2026-10-22, DI), and one real FSDS miss: AVGO 10-Q period 2026-02-01 filed 2026-03-11 (cause not checked). In FSDS but not in `core.filing`, 8: Google Inc (CIK 1288776) FY2014 10-K and three 2015 10-Qs, Broadcom Ltd (CIK 1441634) FY2015 10-K and three 10-Qs. Our store has no filing rows for those predecessor registrants (their numbers reach us only as comparatives of later filings), DI.

## 3. Comparison with what we store (core.fact, same accession)
Key: tag, unit, period end (month-rounded), quarters. 453 filings with stored facts.

| Result | Facts | Share |
|---|---|---|
| Face fact reproduced exactly by the API/stored value | 92,215 | 93.4% |
| Value differs | 186 | 0.19%: 185 `CommonStockParOrStatedValuePerShare` (FSDS reads 0.0000, stored 0.00001: FSDS 4-decimal truncation, FC AAPL 0001193125-15-023697) and 1 discontinued-ops EPS |
| Custom (extension) tag, absent from the API by design | 6,310 | 6.4% (extractor ADDS these) |
| Non-custom face fact absent from stored | 0 | 0% |
| Stored us-gaap facts of those filings that the face route reproduces | 92,215 of 192,055 | 48%: the rest are note facts, which FSDS num.txt does not carry |
| Stored facts under a face tag that sit in other columns (quarterly tables, notes) | 8,978 | the filing-only route drops these |

Reading (DI, from the counts): where a line is on the face, the API value is the filing value, to the last digit, for every non-custom tag in 10 companies and 11 years. The API is therefore a sound value feed; the errors live in tag choice, composition, basis (split, vintage) and in the 6.4% custom tags.

Headline cells with a deliberately tiny presentation rule (not the standardization layer) vs stored `analytics.canonical_fact` (`headline.py`, `results/headline_vs_canonical.csv`):
| Concept | Agree (any vintage) | Disagree | No stored cell |
|---|---|---|---|
| revenue (presentation total line, else first revenue-tag line) | 714 | 4 (LLY FY2016 + 3 quarters: stored 18,312.8M vs 21,222.1M printed in every 10-K that shows it; stored carries the Elanco recast basis, ledger row 70, DI link) | 17 |
| total_assets | 438 | 0 | 15 |
| cfo | 476 | 0 | 38 |
| net_income | 744 | 1 (TSLA 2017-06 6M: my rule picked ProfitLoss -798.6M, stored NetIncomeLoss -666.7M; rule artifact) | 22 |
| diluted_eps | 503 | 204, all explained as stored = as-filed / split ratio (below) | 11 |

Diluted EPS 204 disagreements by ratio (stored vs latest as-filed): /20 x44 (AMZN 2022 split, GOOG 2022 split: consistent), /4 x28 (AAPL 2020: consistent), /10 x43 (AVGO 2024: consistent), /15 x20 (TSLA: consistent), /400 x31 (GOOG pre-2022: the 20:1 split applied twice, ledger row 74), /16 x33 (NVDA pre-2021: 4:1 applied twice, no 10:1, ledger row 65), /3 x5 (TSLA; ratio not verified). The as-filed number plus the filing date is exactly what a split table needs to decide the basis. Net: the extractor does not break these; the stored split basis is wrong in at least 64 of the 204 (DI, ratios only).

Revenue total tag by filer (presentation total line, FC from FSDS pre/num): NVDA `Revenues` throughout; LLY `Revenues`; GOOG `Revenues` (606 tag sits on component lines); META `Revenues` to 2017, 606 tag from 2018; AMZN `SalesRevenueNet` to 2017, 606 tag from 2018; TSLA `Revenues` to 2022, 606 tag from 2023; MSFT `SalesRevenueNet` to 2017, 606 tag from 2018; AVGO, MU, AAPL `SalesRevenueNet` then `Revenues` (FY2018) then the 606 tag. The face "Total" line picks the right tag in every filing; the stored revenue equals it in 714 of 718 cells.

## 4. Known wrong cells
Cells (16): AAPL 2020-03-28 and 2020-06-27 (commercial paper), TSLA 2018-09-30, GOOG 2023-12-31, NVDA FY2015, MU 2021-09-02, ABBV 2022-03-31 and 2017-12-31, CVX 2015-03-31 and 2014-09-30, GOOG 2015-09/2016-03/2016-06, revenue total vs 606 (one class), AAPL FY2018 EPS, GOOG Q2 2022 EPS. ABBV and CVX are outside the 10; their four filings were read with the same extractor (FSDS 2022q2, 2018q1, 2015q2, 2014q4, 4 requests).

"Filing-only" = FSDS face lines in presentation order, no API. "Hybrid" = API values, with the line set (slot) decided from the filing's presentation and calculation linkbase: the debt-family children of the filing's own LiabilitiesCurrent / Liabilities / (note) debt total. Calc linkbases fetched for 8 filings (`_cal.xml`).

| # | Cell | What the filing shows (FC) | Filing-only | Hybrid (cal slot + API value) |
|---|---|---|---|---|
| 1 | AAPL 2020-03-28 | face `OtherShortTermBorrowings` 10,029M + term debt 10,392M + 89,086M; cal: both borrowing tags are children of LiabilitiesCurrent (0000320193-20-000062 cal; -20-000052 FSDS) | right lines, exact values | fixed; API equal 10,029M |
| 2 | AAPL 2020-06-27 | `OtherShortTermBorrowings` 11,166M + 7,509M + 94,048M, cal as above (0000320193-20-000062) | right | fixed; API equal |
| 3 | TSLA 2018-09-30 | custom `ConvertibleSeniorNotesIssueToRelatedPartiesNoncurrent` 2,634K on the face, cal child of Liabilities (0001564590-18-026353) | right: FSDS carries the custom fact | slot found, value ABSENT from the API (custom tag): not fixed without a filing read |
| 4 | GOOG 2023-12-31 | face LTD 13,253M includes finance leases; face has no lease line; debt-note cal: `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` = `DebtInstrumentCarryingAmount` + `FinanceLeaseLiability` (0001652044-24-000022 cal role DebtLongTermDebtDetails) | fails: finance-lease facts (363 current, 1,746 total) are note facts, not in FSDS | fixed: perimeter from the note cal, values from the API (363 and 1,746 present as non-authoritative copies, DI) |
| 5 | NVDA FY2015 | face `LongTermDebt` 1,384,342K, capital lease long-term 14,086K; cal: LongTermDebt is a child, `ConvertibleDebtNoncurrent` is not (0001045810-15-000036) | right | fixed; API holds 1,384,342K |
| 6 | MU 2021-09-02 | face `DebtCurrent` 155M + `LongTermDebtAndCapitalLeaseObligations` 6,621M = 6,776M, both cal children (0000723125-21-000065) | right | fixed; API equal, filer aggregate 6,776M also present |
| 7 | ABBV 2022-03-31 | face `ShortTermBorrowings` 12M, cal child of LiabilitiesCurrent (0001551152-22-000017) | right | fixed; API equal |
| 8 | ABBV 2017-12-31 | `ShortTermBorrowings` 400M on the face (0001551152-18-000014) | right | fixed; API equal |
| 9 | CVX 2015-03-31 | face `CapitalLeaseObligationsNoncurrent` 65M, cal child of Liabilities (0000093410-15-000020) | right | fixed; API equal |
| 10 | CVX 2014-09-30 | same line 84M (0000093410-14-000049) | right | fixed; API equal |
| 11-13 | GOOG 2015-09, 2016-03, 2016-06 | face `DebtCurrent` is a cal leaf (3,237M, 3,221M, 2,219M); the commercial paper plus current capital lease split is only in the notes (0001652044-15-000005, -16-000021, -16-000032) | total current debt right; split not available | fixed: API holds `CapitalLeaseObligationsCurrent` 238M, 223M, 220M (authoritative) |
| 14 | Revenue total vs 606 | face total line decides the tag; stored equals it in 714 of 718 cells | right | right (API value equals the face tag value) |
| 15 | AAPL FY2018 diluted EPS | as filed 11.91 (0000320193-18-000145); API raw 11.91 | value right | value right; the wrong value is the `_resolved` split-adjusted row (0.7275 style), outside both routes |
| 16 | GOOG Q2 2022 diluted EPS | as filed 1.21 (0001652044-22-000071); API raw 1.21; `_resolved` row 0.0605 (/20 again) | value right | value right; wrong adjusted row, outside both routes |

Score (16 cells):
- Filing-only: 10 fixed (1, 2, 3, 5, 6, 7, 8, 9, 10, 14), 3 partial (11-13: total right, composition missing), 1 fails (4), 2 not fixed because the error is the split basis (15, 16, value read right).
- Hybrid: 13 fixed (1, 2, 4, 5, 6, 7, 8, 9, 10, 11-13, 14), 1 not fixed (3: the custom value is not in the API), 2 not fixed (15, 16: split basis).
- The two routes fail on different cells: filing-only fails where the fact is note-level (4, composition of 11-13); the hybrid fails where the fact is a custom extension tag (3). Hybrid plus a filing read for custom tags would cover 14 of 16; the last two need the split table.
- Stored-correct cells the extractor would break: none at value level except FSDS's own 4-decimal truncation (185 par-value cells, 0.19% of face facts). At cell level, going filing-only would drop the 52% of stored us-gaap facts that are note facts, and 8,978 face-tag facts in other columns.

Heuristic check (`is_total`): vs the filer's own cal parents on 6 filings (513 face tags): precision 96/96 (no false totals), recall 96/131 = 73%. The misses are parents in note trees (e.g. `DebtCurrent`, `InventoryNet`), not face totals. The calc linkbase is not in FSDS; a total flag from FSDS alone is a label/tag heuristic.

## 5. What still needs the standardization layer
- Concept mapping: face tag to canonical concept (the extractor gives the tag and the total flag; `Revenues` vs 606 vs `SalesRevenueNet` varies by filer and year; NetIncomeLoss vs ProfitLoss needs a rule, see TSLA).
- Perimeter policy: lease-inclusive or borrowings-only, current maturities inside "short-term debt", refinancing reclass (DC-TOTAL-DEBT-LEASE-PERIMETER).
- Restatement choice: a period appears in up to 6 filings; stored equals the latest in some cells and the original in others (e.g. revenue 19 latest-only, 6 original-only; EPS 64 and 14). The extractor exposes every vintage with its filing date; the choice is a rule.
- Split basis: all 204 EPS disagreements are basis, not extraction; needs split_event and a filed-after-split rule (GOOG 2022 Q2).
- TTM, Q4 derivation, YTD to quarter subtraction: untouched; the extractor returns the filing's own columns (qtrs 1, 2, 3, 4).
- Notes and custom facts: note-level facts (finance leases, D&A components outside the CF face) from the API; custom tags (6.4% of face facts) need a filing read (instance) because the API drops them.
- Predecessor registrants (8 filings) and amendments.

## 6. FSDS limits found (FC unless stated)
1. `ddate` is rounded to the nearest month-end (AAPL 2020-03-28 reads 2020-03-31; MU 2021-09-02 reads 2021-08-31); no start date, only `qtrs`. Matching must round our dates the same way (first match attempt without this showed 11,001 false "absent" facts, MU and AVGO). Exact period dates need the instance.
2. Values have 4 decimals (par 0.00001 reads 0.0000); per-share facts carry uom `USD`, not `USD/shares`.
3. `num.txt` has face facts only (48% of stored us-gaap facts reproduced); `pre.txt` must be sorted by (report, line); no calculation linkbase; no amendments with statements (10-K/A Part III only).
4. One filing in 453 is missing from FSDS (AVGO 10-Q 2026-02-01), cause not checked (DI).

## 7. Recommendation (for the founder's hybrid)
Keep the API as the value feed (93.4% exact on face facts, 0 non-custom face facts missing). Use the filing, not for values, but for the slot record: face statement order, the total line, and the filer's calc tree (cal.xml: 8 filings, 2 requests each) to say which tags make up a face total. Two additions the API cannot give: custom extension tags (6.4% of face facts; TSLA 2,634K) and exact period dates. Read the calc linkbase from the filing itself, not FSDS, because FSDS has none. Next test, cheap: build the slot record for debt, D&A and capex on the 30-company set from `_cal.xml` (2 requests per filing) and replay the 16 cells above as a regression set.

## 8. Reproduce
`run_all.sh <workdir> <worktree>/pipeline/src` (needs `SEC_UA`), `pull_stored.py` and `pull_canonical.py` (read-only), `compare.py`, `headline.py`, `known.py`, `show.py`, `fetch_filing_files.py` + `cal_tree.py` / `cal_totals.py`. Parsers read untrusted files and run with `python3 -I`.
