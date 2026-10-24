---
id: ci-pg-dump-pg-restore-must-match-the-postgres-service-versio
title: CI pg_dump/pg_restore must match the postgres service version
kind: gotcha
tags: ci, postgres, backup
paths: scripts/ci/pgbin, .github/workflows/ci.yml, scripts/verify_backup_restore.sh
evidence: CODE-CHECKED
status: active
created: 2026-10-22
verified: 2026-10-22
---
Runner client tools drifted newer than the postgres:16 service; pg_restore failed with unrecognized configuration parameter transaction_timeout (2026-10-21). Fix: scripts/ci/pgbin/ shims run the tools from the postgres:16 image (commit bab75b8). Keep the image tag equal to the service tag. Fix unproven until CI run 39720553769 finishes.

[2026-10-22] Curator: dropped scripts/ci/pgbin from paths because it is not in main's tree yet (commit bab75b8 exists but is not on a local branch); re-add when it lands.
