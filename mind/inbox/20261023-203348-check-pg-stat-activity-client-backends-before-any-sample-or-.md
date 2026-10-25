---
id: check-pg-stat-activity-client-backends-before-any-sample-or-
title: Check pg_stat_activity client backends before any sample or batch read; stop above 12
kind: gotcha
tags: db, pooler, process
evidence: DATA-INFERRED
source: 2026-10-23 RF-13/RF-14 sample workers
created: 2026-10-23
verified: 2026-10-23
---
On 2026-10-23 select count(*) from pg_stat_activity where backend_type='client backend' returned 18 (26 total) while the engineering lanes were idle, above the data chief's cap of 12 (team limit 14). Workers stopped without retrying. Re-check about every 30 minutes with one count query; resume only at or below 12; do not hunt for or end other sessions' connections; if above 12 on two checks tell the chief of staff.
