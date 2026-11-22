---
id: standard-extract-plan-step-broke-when-75175bed-split-resolve
title: Standard extract plan step broke when 75175bed split resolver-all110 into resolver/<TICKER>.csv; default CIK list now the directory
kind: gotcha
tags: extract, resolver, workflows
paths: .github/workflows/pipeline-standard-extract.yml, scripts/ci/run_extract_sql.py
evidence: CODE-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
The plan step globbed data-team/tags/line_map/resolver-all110-*.csv under set -e; after the per-company split the glob matched nothing and the step failed. Fixed in 107acf10: default = data-team/tags/line_map/resolver (dir), run_extract_sql.py ciks --csv accepts a directory, list verified identical to the old 110 CIKs. Lesson: any rename of the resolver output must grep .github and scripts for the old glob (pipeline-tag-library-rebuild.yml also watched only the old file). The last extract run before the fix (43928679894, 11-16) had succeeded; 'no successes' was stale.
