---
id: fresh-sec-ingestion-can-coexist-with-a-failed-nightly-public
title: Fresh SEC ingestion can coexist with a failed nightly publication chain
kind: gotcha
tags: nightly, ingestion, freshness, operations
paths: .github/workflows/pipeline-refresh.yml
evidence: CODE-CHECKED
status: active
source: Independent live audit 2026-11-21
created: 2026-11-21
verified: 2026-11-21
---
Eight consecutive pipeline-refresh GitHub runs through 2026-11-19 failed, while core.filing still reached filing_date 2026-11-18 and created_at 2026-11-19. Track freshness independently for ingestion, normalization, mapping, proof and serving; one latest-filing timestamp cannot prove end-to-end freshness.
