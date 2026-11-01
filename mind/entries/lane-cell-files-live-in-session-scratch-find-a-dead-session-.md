---
id: lane-cell-files-live-in-session-scratch-find-a-dead-session-
title: Lane cell files live in session scratch: find a dead session's file and copy it out before a wipe
kind: howto
tags: cells, handoff, scratch
paths: 
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01

unmerged_paths: data-team/strategy/handoff/INCOME-STATEMENT-2026-11-01.md
---
When a lane session restarts, its emitted cell file may exist only under /private/tmp/claude-501/-Users-vikash-scrooner/<old-session-uuid>/scratchpad/cells/<family>/ (cells.jsonl.gz + manifest.json). Find it with find /private/tmp -iname '*<family>*'. Verify with gzcat cells.jsonl.gz | shasum -a 256 against manifest sha256 (uncompressed) and row count, then cp -p to a durable non-tmp path (used: ~/scrooner-cells-safe/<family>-<sha8>/). This is a local copy, not a production write, so it needs no founder words. Bucket upload to fsn-notes/cells/<family>/<date>/ still does. Done for is_core 2026-11-01 (281,761 rows, 77f5846a).
