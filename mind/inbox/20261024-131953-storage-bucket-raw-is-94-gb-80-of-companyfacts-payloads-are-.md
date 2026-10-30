---
id: storage-bucket-raw-is-94-gb-80-of-companyfacts-payloads-are-
title: Storage bucket raw is 94 GB; 80% of companyfacts payloads are byte-identical refetches
kind: gotcha
tags: storage, capacity, collector
paths: data-team/strategy/team/DATA-CONSUMPTION-AUDIT-2026-10-24.md
evidence: DATA-INFERRED
source: audit 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
storage.objects: companyfacts 79 GB/44,630 objects, only 8,829 distinct (cik,sha256) = 16 GB; latest-only 11 GB; growth 7-10 GB/week; 92% of last 9 days fetches duplicate. Hash-dedupe before upload.
