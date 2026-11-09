---
id: a-dropped-pooler-connection-makes-conn-rollback-raise-per-co
title: A dropped pooler connection makes conn.rollback() raise: per-company loops must use common/errors.safe_rollback (FSN load shards died, 2026-11-09)
kind: gotcha
tags: fsn, load, pooler, rollback, reliability
paths: pipeline/src/scrooner_pipeline/fsn_store/load.py, pipeline/src/scrooner_pipeline/common/errors.py
evidence: CODE-CHECKED
source: FSN write run 42561798991 shards 4/6/7
created: 2026-11-09
verified: 2026-11-09
---
fsn_store.load.run caught a company failure and called conn.rollback(); when the Supabase pooler had dropped the connection, rollback() itself raised OperationalError and killed the whole shard. Now: if conn.closed or conn.broken, reconnect (load.run(connect=...)) and retry the company once; otherwise safe_rollback. The pilot loop does the same. Tests kill the backend with pg_terminate_backend(pg_backend_pid()) mid-company (pipeline/tests/unit/test_fsn_production_scale.py).
