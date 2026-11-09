---
id: fsn-value-reads-must-lead-with-filing-id-or-use-dim-id-0-a-c
title: fsn.value reads must lead with filing_id or use dim_id = 0: a (company_id, tag_id) read without dim_id walked every company and timed out the 1,000-company write
kind: gotcha
tags: fsn, index, statement_timeout, production-scale, pilot
paths: pipeline/src/scrooner_pipeline/fsn_store/select.py, data-team/strategy/team/FSN-WRITE-TIMEOUT-2026-11-09.md
evidence: CODE-CHECKED
source: FSN write run 42561798991; EXPLAIN on production 2026-11-09
created: 2026-11-09
verified: 2026-11-09
---
The only company index on fsn.value, idx_fsn_value_series (company_id, tag_id, ddate, qtrs) where dim_id = 0, is PARTIAL. A read with company_id + tag_id but no dim_id filter (members wanted) cannot use it: the planner falls back to the unique key (filing_id, tag_id, ...) with tag_id alone and walks every company's rows (EXPLAIN cost 846,820 for AbbVie's 247 tags on 35.6M rows). Scratch dry runs never show it (one shard). Fix: add filing_id = any(company filing ids) (cost 4,692), select.MEMBER_VALUES_SQL. Before shipping a per-company read on fsn.*, EXPLAIN it on production (read-only, statement_timeout 15s).
