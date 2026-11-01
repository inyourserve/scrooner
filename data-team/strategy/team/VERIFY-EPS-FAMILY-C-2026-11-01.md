# Verify: EPS Family C (origin/work/per-share/eps-never-derive; scan 48c632e, plan bcfc796, dry run v2 b0ed74d digest d5f21dae...), 2026-11-01

Seed 20261101. Files: v1 outcomes nc_fsn_outcomes.json and C_per_share_derived_cells.csv (bucket, hash-checked); v2 lists replace_with_fsn_value.csv (97), replace_with_filed_fact.csv (204), remove_per_share_filed_copies_disagree.csv (15), fsn-cells/axis_only_holds.csv (106 cells, 228 copies). The sample was drawn from v1. Every verified replacement was matched to v2 by canonical_fact_id and carries the same value there. Evidence class: FILING-CHECKED (income statement and quarterly-data R pages). Verifier 2 (scrooner-bc).

## Result
**NO (one class, 2 cells).** CIK 1728951 basic and diluted EPS for 2018-07-01..2018-12-31 (a 6-month period) take the FSN value 0.13. The scan used qtrs=1, a one-quarter value: EarningsPerShareBasicAndDiluted at 2018-12-31. The filing's own face (10-K 0001564590-19-005137, statement of operations) prints 0.26 for that 6-month column. Both cells are still in v2.
- Replacements otherwise right: 8 of 8 graded.
  - UNH Q4 2019 3.68 diluted / 3.74 basic (quarterly data note).
  - Waters Q4 2019 3.15 basic / 3.12 diluted vs stored 3.08 (a large-difference case).
  - Waters Q2 2020 1.98; 1331520 Q3 2014 0.41; 1739104 Q4 2018 0.04.
  - AAL Q4 2020 -3.81 (filed fact; stored derived -3.57).
  - UNH Q4 2014 1.55 not graded (quarterly page parsed without that column).
- Removals: "not filed separately" 5 of 5 right, and "not captured" 3 of 3 readable right. Those 10-Ks (FY2020+) carry no quarterly-data page, so Q4 is not printed.
- Copies disagree, avoidable: News Corp 3 months to 2015-06-30 is removed as "copies disagree", but the 10-K quarterly schedule prints -0.65 twice, equal to the stored value. Removing it removes a right value.
- Axis-only holds: 3 of 3 rightly held for review (MAA 2019 on ParentCompany/LimitedPartner axes; Yum 2017 continuing-operations segment only; HR 2017 ParentCompany axis).

## Findings for the builder
1. **FSN duration must match the cell:** take qtrs = the cell's duration in quarters (2 for a 6-month cell), never qtrs=1 for a multi-quarter period. Re-verify 1728951 2018-07-01..2018-12-31 = 0.26.
2. **Copies disagree:** when the copies disagree but the original filing prints a value, prefer the original's printed value with provenance, as for other families (News Corp -0.65).
3. UNH Q4 2014 and the 1660134 removal were not graded (page layouts).

## Requests and disk
SEC requests: 91. Bucket reads: 2 archives (hash-checked). DB: one connection to map removals to filings.
