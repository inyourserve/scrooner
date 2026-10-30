# Verify: D&A / capex replay V3 (origin/work/scrooner-25/slot-records fd9b6be), 2026-10-26

Verifier 2. Reports d_and_a_replay_v3_report.json / capex_replay_v3_report.json read as committed; each drawn cell checked on the cash-flow R page of its own accession (76 accessions fetched, nothing kept on disk). Seed random.Random(20261107). FILING-CHECKED unless marked.

## Result: GATE FAILS on the new face-column rule. Every published value checked is right (60 of 60), but the rule throws away right face values at scale: 7 of the 10 drawn full-year / year-to-date / Q1 not_a_face_column cells, plus ABBV FY2020, are printed on the face.

## 1. V2 findings
- ABBV Q4 2020: fixed. No D&A cell for 2020-10-01..12-31; capex Q4 is no_facts_this_period (production still holds the derived 279M, information only).
- KRUS Q3 FY2021 (2021-03-01..05-31, 0001564590-21-036462): fixed, now not_a_face_column. The 9-month 3,314K is published and matches the face.

## 2. Publishable draw: 30 D&A + 30 capex, all 60 values printed on the face in the cell's column
Examples: AMZN Q3 2018 D&A 3,778; TSLA FY2017 1,636,003K; TXN Q1 2017 139+80+11 = 230; GE 6M 2018 2,695+1,171; META FY2020 capex 15,115 (production 15,163 is the one that is wrong); KO FY2018 capex 1,347 (production 1,548 is wrong); NFLX 9M 2020 349,567K; AAPL 6M FY2015 5,586 (broad 5,741 adds intangibles 155).
Perimeter calls for the standardization lead (the values match the face; whether the slot is the full capex is a definition question):
- CAT (2016 9M 0000018230-16-000715, 2026 Q1): narrow = "Capital expenditures - excluding equipment leased to others" 807. The face prints "Expenditures for equipment leased to others" 1,393 as a separate line. A reader adding up CAT's capex would get 2,200.
- MA and GE: broad adds capitalized software (MA FY2024 474 + 720 = 1,194, which is production's value).

## 3. 15 not_a_face_column cells (10 full-year, YTD or Q1; 5 mid-year quarters)
| Cell | Face shows | Verdict |
|---|---|---|
| INTC capex 6M 2021 (0000050863-21-000030) | 7,574 | right value thrown away |
| CAT D&A 9M 2021 (0000018230-21-000260) | 1,766 | right value thrown away |
| CAT D&A 9M 2020 (0000018230-20-000297) | 1,815 | right value thrown away |
| ABBV D&A Q1 2022 (0001551152-22-000017) | 198 + 1,855 | right value thrown away |
| ABBV D&A Q1 2017 (0001551152-17-000016) | 103 + 271 | right value thrown away |
| MSFT capex 6M FY2022 (0001564590-22-002324) | 11,675 | right value thrown away |
| MU capex FY2022 (0000723125-22-000048) | 12,067 | right value thrown away |
| CSCO D&A 6M FY2024, MSFT D&A 9M FY2025 | custom "Depreciation, amortization, and other" line | blank right, reason wrong (custom member, not "not a face column") |
| AMZN 2015-10-01..12-31 (10-K) | 12-month column only | right |
| GOOG Q2 2018 capex, CVX Q2 2025, PG Q2 FY2022, MU Q2 FY2026, RPAY Q3 2024 | YTD column only | right |
Also ABBV FY2020 10-K (0001551152-21-000008): D&A 666 + 5,805 and capex 798 are printed; both cells are not_a_face_column.

Cause: each company has ONE section record whose total tag is the continuing-operations element (e.g. ABBV's record covers 2014-2026 with NetCashProvidedByUsedInOperatingActivitiesContinuingOperations). In these filings the filer tagged the plain NetCashProvidedByUsedInOperatingActivities / InvestingActivities for the column (non-derived, same accession; DB check on 7 cells), so `sec["total"] in day` fails. The DB check is DATA-INFERRED; ABBV FY2020 and CAT 2016 confirm on the face (FILING-CHECKED), where the filer uses the ContinuingOperations abstract with the plain total. Scale: 277 D&A and 374 capex not_a_face_column cells are full-year, YTD or Q1 length, against 813 / 60 mid-year quarters.
Fix: count a column as a face column if the filer tagged any of the operating or investing totals (plain or continuing-ops) for that (start, end) in the accession. Better still, test that the member's own context appears in the CF presentation (R page or FSN pre/num). Report a custom-line cell as needs_instance_reader.

## 4. AMD FY2025 (0000002488-26-000018)
Face investing section: "Purchases of property and equipment (974)", then two investment lines, then a separate "Payments for (Proceeds from) Productive Assets (38)" (standard element label, no company wording), then net investing (5,533). A reader calls capex 974. The 38 is a separate printed line whose nature the face does not state. The replay's 1,012 comes from putting PaymentsForProceedsFromProductiveAssets (class net_capex) in NARROW beside PP&E. That element is normally a net-capex TOTAL; here it is a sibling. Publish 974. Add the 38 only if the 10-K notes show it is property spending.
Also AMD FY2025 D&A: face prints "Depreciation and amortization" 750 and "Amortization" 2,254. Narrow 750 leaves out the 2,254 because AdjustmentForAmortization is classed other_amort, but the 2025 9-month narrow (2,253) includes the intangible amortization (AmortizationOfIntangibleAssets). So the FY narrow understates by about 2.25B. That the 2,254 is acquisition-intangible amortization is DATA-INFERRED from its size matching the quarterly intangible-amortization facts. FY2025 D&A should be 3,004.
