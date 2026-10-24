---
id: long-stage-and-ticket-cause-gotchas-2026-10-13-1-2f6810
title: Long-stage and ticket-cause gotchas (2026-10-13/17)
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
`resolve-conflict-fills` and `period_completeness` run 30-60 min and died on the pooler's `statement_timeout` / dropped SSL connections: lift the timeout for the session (`set statement_timeout=0`), retry the final bulk write on a fresh connection (`db/connection.py::run_write_with_reconnect`; `period_completeness` now does), and wrap reruns in a retry script — the writes are delete-then-insert and idempotent. `period_gap.checked_at` is the run's TRANSACTION start (`now()`), not the write time. `no_line_item_filed` means only "no matching fact in the filing's XBRL" — 18% of a rendered-statement sample did show the line, so it is `data_limit`, never `legitimate_absence`, until rendered evidence confirms. A newly mapped per-share tag shows split-adjusted values only where no `*_resolved` row existed yet (the retroactive split stage skips existing rows): after the 2026-10-13 `basic_eps` backfill, ~200 companies have adjusted basic but unadjusted diluted EPS — check before comparing the two. All sessions share one working tree: an applied-but-untracked migration breaks CI's contiguity check (`check_migrations.py`).
