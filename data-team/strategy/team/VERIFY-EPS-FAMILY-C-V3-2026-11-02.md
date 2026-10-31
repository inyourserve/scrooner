# Verify: EPS Family C v3 changed cells (origin/work/per-share/eps-never-derive f598495, dryrun-v3/changed_cells_vs_v2.csv; digest e19bd607...), 2026-11-02

All 15 changed cells. Evidence class: FILING-CHECKED (statement or quarterly-data R pages of each new_accession). Verifier 2 (scrooner-bc).

## Result
**YES.** 15 of 15 right; the rest of v2 passed earlier (VERIFY-EPS-FAMILY-C-2026-11-01).

| Company | Cells | Period | Face | New value | Stored | Verdict |
|---|---|---|---|---|---|---|
| 5103 (CIK 1728951) | basic, diluted | 6 months to 2018-12-31 | 10-K 0001564590-19-005137 statement of operations, 6-month column: 0.26 / 0.26 | 0.26 | 0.25 (v2 had 0.13) | right |
| 5580 (CIK 1780312) | diluted, diluted_resolved x2 | Q3 2020, Q2 2020 | 10-Qs 0001213900-20-036663 / -021916: basic and diluted loss per share (0.01) for each 3-month column | -0.01 | 0 | right |
| 3354 Charter | basic, diluted, resolved x2 | Q4 2015 | 10-K 0001091667-16-000396 quarterly data: -1.09 / -1.09 | -1.09 | -1.10 (derived) | right |
| 3028 (CIK 1567683) | basic | Q4 2014 | 10-K 0001567683-15-000003 quarterly data: Dec. 31, 2014 basic 0.02 | 0.02 | -0.03 (derived) | right |
| 3000 News Corp | basic x2, diluted | Q4 FY2015 | 10-K 0001193125-15-288946 quarterly schedule: -0.65 basic and diluted | -0.65 | -0.65 | right (V1 avoidable hold now published) |
| 3000 News Corp | diluted | Q4 FY2016 | 10-K 0001193125-17-257248 quarterly schedule: 0.15 | 0.15 | 0.15 | right |

SEC requests: 24. One DB read (company 5580 CIK).
