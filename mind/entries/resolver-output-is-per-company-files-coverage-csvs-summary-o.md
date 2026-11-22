---
id: resolver-output-is-per-company-files-coverage-csvs-summary-o
title: Resolver output is per-company files; coverage CSVs: summary only in git, export one company per flow job
kind: decision
evidence: CODE-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Since 2026-11-21 (main bb0d8b9d, 75175bed; Dhairya rule) the structural resolver output lives in data-team/tags/line_map/resolver/<TICKER>.csv (tools/split_resolver.py after resolve_all.py); readers use scrooner_pipeline.mapper.resolver_files (dir wins, single file fallback, conflict() flags both). The top100 flow exports only its own company (--company-ids) and the publish job merges the summary row (scripts/ci/top100_coverage_merge.py); the hourly export keeps rows of companies whose flow job is in flight and commits only top100-coverage-summary.csv (per-cell CSV is an artifact). No tracked file over 5 MB.
