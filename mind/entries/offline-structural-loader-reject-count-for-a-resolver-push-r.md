---
id: offline-structural-loader-reject-count-for-a-resolver-push-r
title: Offline structural_loader reject count for a resolver push: read_claims(Path(resolver dir)) with dummy env
kind: howto
tags: resolver, pre-push, structural_loader
paths: pipeline/src/scrooner_pipeline/mapper/structural_loader.py
evidence: CODE-CHECKED
status: active
source: resolver .88 bc46d0ec
created: 2026-11-22
verified: 2026-11-22
---
From the worktree's pipeline dir: export dummy DATABASE_URL, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SEC_USER_AGENT (Settings needs them at import; no DB is touched), then PYTHONPATH=$PWD/src <venv python> -c 'from pathlib import Path; from scrooner_pipeline.mapper import structural_loader as s; c,r,n=s.read_claims(Path("../data-team/tags/line_map/resolver")); print(len(c),len(r))'. The argument must be a Path, not a str. At .88: 70,681 claims, 32 rejects (quarterly-sum DPS component_sum rows, pre-existing); a text_stated 0 is refused, so reads of 0 must carry stated_zero (X118).
