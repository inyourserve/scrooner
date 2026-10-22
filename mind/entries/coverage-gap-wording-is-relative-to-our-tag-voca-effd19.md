---
id: coverage-gap-wording-is-relative-to-our-tag-voca-effd19
title: Coverage "gap" wording is relative to OUR tag vocabulary, so it is circular (audit 2026-10-17)
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
`company_concept_lineage`'s "nothing relevant filed" means none of our mapped/candidate tags were filed, not that the filing lacks the line; only ~90 of ~12.4k SEC tags are approved/provisional/preference, and 64% of `core.fact` rows sit under unmapped tags (`analytics.sec_tag_library`, `mapping_status='unmapped'`, sort by `active_company_count`). Mapped-tag-filed-but-no-value is ~0 (61 cells), so look for coverage loss in vocabulary, applicability and the denominator, not the pipeline. Before quoting a coverage number, check `max(snapshot_date)` in `analytics.coverage_snapshot` and that `company_data_point_coverage.gap_reason` is populated. Both were stale/empty on 2026-10-17 despite the handoff saying otherwise.
