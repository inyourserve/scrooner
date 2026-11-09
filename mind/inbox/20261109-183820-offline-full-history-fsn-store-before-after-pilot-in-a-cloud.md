---
id: offline-full-history-fsn-store-before-after-pilot-in-a-cloud
title: Offline full-history FSN store + before/after pilot in a cloud session (no bucket, no production)
kind: howto
tags: fsn, pilot, measurement, cloud, sec
paths: pipeline/src/scrooner_pipeline/fsn_store/extract_sec.py, pipeline/src/scrooner_pipeline/fsn_store/shard.py, data-team/47-fsn-store/IS-STRUCTURE-BATCHES-2026-11-09.md
evidence: CODE-CHECKED
created: 2026-11-09
verified: 2026-11-09
---
To measure a mapping change over full history without the fsn-notes bucket or production: (1) for each set 2014q1..2025q3 and 2025m10..2026m10, extract_sec.download_zip (sequential, sec.gov) then extract_sec.filter_set(zf, ciks) + write_zst into <cache>/<set>/<set>_<table>.tsv.zst (the shard cache layout; ~60 sets, ~1h with 3 filter workers). (2) monkeypatch shard.list_periods to return [] and set dummy SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY (shard.download calls _storage() before checking the cache), then shard.run(out, {cik: prod_company_id}, periods, cache). (3) local Postgres 16: scripts/ci/bootstrap_supabase.sql + every migration; insert core.company with the PRODUCTION ids (the pilot calendar is keyed by company_id; ids, sic, fye are in the cohort artifact reports.json), seed every concept_rules/*.jsonl, load.load_company each dir. (4) copy the DB twice (create database X template Y) and run 'uv run --project pipeline scrooner-fsn pilot --ciks ...' from a worktree of each code version; diff report.json per_data_point and cells/*/cells.jsonl.gz keyed (company_id, data_point_name, period_grain, fsn_end, basis). Gotcha: a new mapping in a LATER filing can change an existing shown value through select's latest-copy rule (restated comparatives), so always diff cells, not only coverage. Scripts used: session 2026-11-09 tag & mapping expert (branch work/tag-expert/is-interest-structure).
