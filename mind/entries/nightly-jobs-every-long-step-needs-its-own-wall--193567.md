---
id: nightly-jobs-every-long-step-needs-its-own-wall--193567
title: Nightly jobs: every long step needs its own wall-clock cap AND a per-statement `statement_timeout` that fits it
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
The pooler default is 2 min, so any full-population scan/delete (coverage matrix, snapshot, tag library, sanity time-series/plausibility writes) must `set statement_timeout` itself; a reconnect after a dropped socket gets a fresh 2-min default and the dead session's row locks linger, so retried writes need `set local statement_timeout = '10min'`. `scripts/lib/sharded.sh` enforces `STAGE_TIMEOUT_SECS` (default 1800) per stage so one hung shard can't burn the 180-min job cap; the reprocess exits non-zero naming killed stages. **Logs of a cancelled GitHub run are deleted (404 BlobNotFound)**, so per-stage timing lines in the script output are the only record of what hung (found 2026-10-17 after four cancelled nightlies).
