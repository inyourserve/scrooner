---
id: fsn-store-mapper-never-sees-parentheticals-eq-ci-or-un-state
title: FSN store mapper never sees parentheticals, EQ, CI or UN statements: shares outstanding and DPS starve; stmt class can be wrong
kind: gotcha
tags: fsn, line_map, shares_outstanding, dividends_per_share, parenthetical, statement-class
paths: pipeline/src/scrooner_pipeline/fsn_store/mapping.py, data-team/tags/playbooks/README.md
evidence: CODE-CHECKED
created: 2026-11-09
verified: 2026-11-09
---
fsn_store/mapping.py reads only fsn.line stmt in (BS,IS,CF) and marks every inpth line 'excluded'. Latest-10-K measure 2026-11-09 (632 cos with line_map): CommonStockSharesOutstanding in BS parenthetical at 407 cos and EQ at 254, but shares_outstanding_resolved mapped at 18; CommonStockDividendsPerShareDeclared on EQ parenthetical 215 + EQ face 35, DPS mapped 64. SEC's stmt class can be wrong: GATX 0000040211-26-000018 real IS is stmt=CI (R6), Revvity 0000031791-26-000012 IS is stmt=UN (R4), blanking all IS concepts. Also: in fsn.value non-dimensional = dim_id=0 and coreg='' (not NULL); fsn.line holds statement lines only, notes are only in fsn.value. Detail: branch docs/tag-expert-playbooks ebc8dcc.
