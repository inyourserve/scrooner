---
id: heavy-db-jobs-concurrency-group-serializes-six-workflows-one
title: heavy-db-jobs concurrency group serializes six workflows; one pending run per group, cron times no longer mean anything
kind: gotcha
tags: workflows, concurrency, db
evidence: DATA-INFERRED
source: doc/learnings/2026-10-24-github-workflows-deep-dive.md
created: 2026-10-24
verified: 2026-10-24
---
refresh, sanity, frames, tag-library, recompute and certify share concurrency group heavy-db-jobs. GitHub keeps only one pending run per group, so a queued daily run can be replaced. Observed: refresh cron 12:23 UTC started 17:18-18:45 UTC; sanity 15:17 created 19:xx; run durations 91-414 min. The group is a workaround for a small database (256 MB shared buffers), not a design.
