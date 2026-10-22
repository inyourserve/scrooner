# 44. Measured baseline, top 986 (Ritwik, 2026-10-21) — Gate 1 of doc 42

Method: four read-only queries on the live database, one connection each, statement_timeout 60s, cohort = 986 non-excluded companies in doc/data-moat/team/top1000/shards.csv. Pooler 15 of 60 connections. `analytics.company_data_point_coverage` last built 2026-10-20 18:52 UTC. The table has `has_value` (latest period) and no `has_value_any_period`, so migration 0096 is NOT applied; the figures below are the corrected (latest-period) measure. Evidence class: MEASURED (live query), not projection.

## Result vs the R1 projection
| Measure | R1 projection | Measured |
|---|---|---|
| Cells (986 x 163) | 160,718 | 160,718 |
| Valued cells | ~123,900 (77.1%) | 123,326 (76.7%) |
| Blank cells | ~36,800 | 37,392 |
| Blanks with no reason | 13,349 (shard baseline) | 13,349 (35.7% of blanks) |
Projection error on fill: 0.4 points. Gate 1 rule (re-rank if any bucket is off by more than one third): the period causes below are within 1% of R1/data-team/34 figures, so no re-rank.

## Blank reasons (top, count of blank cells)
(none) 13,349; incomplete:numerator 3,522; line_not_presented_in_filing 2,314; incomplete:add 1,802; missing:ebitda_ttm 1,641; negative_ratio_undefined_cagr 968; incomplete:denominator 890; incomplete:subtract 847; line_in_filing_not_extracted 654; missing:fcf_ttm 602.

## Where the blanks sit (data points with most blanks; noreason = blank with no reason recorded)
collaborative_arrangement_revenue 982 (982 noreason); bdc_total_investment_income 957 (957); employee_count 925 (925); net_interest_income 892 (88); net_cash_per_share 865 (0); net_lease_revenue 861 (861); book_value_per_share 851 (1); interest_coverage_ratio 788 (15); piotroski_f_score 710 (8); rnd_intensity 643 (6); cash_conversion_cycle 598; operating_expenses 580; dividends_pct_fcf 563; margin_expanding_3yr 535; cash_returned_to_shareholders 530; interest_income 521; research_and_development 508; inventory_days 498.
Reading: three rows are sector-only lines counted against nearly every company (collaborative-arrangement revenue 982/986 blank, BDC total investment income 957, net-lease revenue 861) and one is a non-XBRL fact (employee_count 925). Together 3,725 blanks (9.96% of all blanks, 28% of the 13,349 reasonless ones). A group template removes the first three by definition (2,800 cells) with no new data; employee_count needs a source decision.

## Period gaps (top 986, `analytics.period_gap`)
no_mapped_tag 8,324; q4_not_derived 5,767; quarter_not_derived 5,320; no_line_item_filed 1,876; not_in_sec_feed 1,796; filing_not_processed 851; conflict_material 785; conflict_split 59; not_resolved 25; conflict_rounding 3. (data-team/34 baseline: 8,600 / 5,801 / 5,345 — consistent.)

## Ingestion
89 10-Q/10-K filings since 2026-07-01 with zero facts, in 89 companies (9.0% of the cohort).

## Immediate consequences for the plan
1. Gate 1 passed on fill and period gaps; plan stands.
2. Quick win with no new data and no accountant: gate the 3 sector-only rows by group (2,800 cells, 1.7 points of all cells) as the first template change.
3. 13,349 reasonless blanks: 3,725 are the four rows above; the remaining ~9,600 need the per-row reason rules (doc 42 WP2.3).
4. Migration 0096 still needs applying so the any-period overcount is retired from the stored table.
5. The 89 zero-fact filings go to the ingestion detector/reader (WP3.5).
