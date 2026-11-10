---
id: canonical-archive-replace-rows-logs-replaced-even-when-the-0
title: canonical_archive.replace_rows logs 'replaced' even when the 0113 slot guard skips the update (share_basis vs FSN-protected keys)
kind: gotcha
tags: slot_protected_cell, share_basis, canonical_archive, fsn_write
paths: pipeline/src/scrooner_pipeline/mapper/canonical_archive.py, pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py, pipeline/db/migrations/0113_slot_protected_cell.sql
evidence: CODE-CHECKED
source: work/fsn/cell-format-v1-2 trace 2026-11-10
created: 2026-11-10
verified: 2026-11-10
---
share_basis.write_company (split.event_basis@1, manual only, flag off by default) writes through canonical_archive.replace_rows/archive_and_remove without scrooner.slot_writer. On a key the FSN loader protected (--protect: valued keys with value, blanks with null), the 0113 trigger returns null and logs slot_protected_write_skipped, so the FSN cell stands. But replace_rows has already inserted a 'replaced' archive row and counts stats['replaced']; archive_and_remove likewise logs a removal that did not happen. A split-rebase-restore from that archive is also skipped by the guard. So no value fight, but the archive/stats overstate changes on protected keys. Since CELL-FORMAT v1.2, FSN writes 6/9-month EPS TP cells, so YTD EPS keys are protected too.
