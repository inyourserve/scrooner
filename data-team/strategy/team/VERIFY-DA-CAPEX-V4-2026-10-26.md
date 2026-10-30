# Verify: D&A / capex replay V4 (origin/work/scrooner-25/slot-records 72e275a), 2026-10-26

Verifier 2. Reports d_and_a_replay_v4_report.json / capex_replay_v4_report.json. Each drawn cell checked on the cash-flow R page of its own accession (115 accessions, nothing kept on disk). Seed random.Random(20261110). FILING-CHECKED unless marked.

## Result: zero wrong shown values in the draw (gate passes on wrong values). False drops remain: 38 full-year/YTD cells at AVGO, KRUS and RPAY whose faces print the value. Their slot record has no cash-flow section, so the face-column test can never pass.

## 1. Newly publishable (were not_a_face_column in V3): 30 D&A + 30 capex
All 60 equal the face in a column of the cell's own length (6 named + 54 random). Named:
- ABBV FY2020 D&A 666 + 5,805 = 6,471, and capex 798 (0001551152-21-000008).
- CAT 9M 2020 D&A 1,815 and 9M 2021 D&A 1,766.
- INTC 6M 2021 capex 7,574.
- MSFT 6M FY2022 capex 11,675.
- MU FY2022 capex 12,067.
The one 24-week COST column ("6 Months Ended", 683M) is also right.

## 2. Production-wrong cells
- META FY2020 capex: replay 15,115M = face; production still holds 15,163M.
- KO FY2018 capex: replay 1,347M = face; production still holds 1,548M.
The replay is right in both; production must take the replay value.

## 3. 15 of the three-month exclusions (795 D&A + 47 capex)
All 15 are right to exclude. Each 10-Q prints only the year-to-date column (6 or 9 months; COST 8 or 6 months), and WMT's 10-K prints only 12 months.
GE Q3 2015 (0000040545-15-000114): the header lists 3, 9 and 12 months, but the 3-month cells are empty; values sit only in the 9-month column.

## 4. The other exclusions (not three-month)
| Cells | Face | Verdict |
|---|---|---|
| KRUS D&A 5 (6M/9M/FY FY2025, 6M/9M FY2026), e.g. 0000950170-25-052106 | "Depreciation and amortization" 6,596 in the 6-month column, operating total printed | **false drops** (production 6,596 etc. is right) |
| AVGO capex 25 (6M/9M/FY FY2018-FY2026), e.g. 0001730168-22-000094 | "Purchases of property, plant and equipment" (302), investing total printed | **false drops** |
| RPAY capex 8 (FY2023 .. 6M 2026), e.g. 0000950170-24-023102 | "Purchases of property and equipment" (733), investing total printed | **false drops** |
| RPAY D&A FY2019 (0001564590-20-011183) | 29,980,000 sits in a column with no operating total, beside predecessor (to Jul 10) and successor columns 6,222,917 / 23,756,888 | right to exclude (combined predecessor + successor, not one reporting period) |
| COST D&A 5 (16-week fiscal Q4) | the 10-K prints only 52/53 weeks | right to exclude |

Cause of the false drops: these records carry `section: null`. All AVGO capex records, KRUS D&A from 2025-02-28 and RPAY capex from 2023-12-31 have no section, so `face_column = bool(sec) and ...` is always false.
Fix: when the record has no section, test for any operating (D&A) or investing (capex) total tag (plain or ContinuingOperations) filed for the same (start, end) in the accession.

Untested: newly publishable cells outside the 60 drawn; the rest of the three-month set.
