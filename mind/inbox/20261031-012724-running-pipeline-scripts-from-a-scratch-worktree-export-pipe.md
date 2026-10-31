---
id: running-pipeline-scripts-from-a-scratch-worktree-export-pipe
title: Running pipeline scripts from a scratch worktree: export pipeline/.env, use the pipeline venv, set SSL_CERT_FILE from certifi
kind: howto
tags: worktree, env, fsn-notes, supabase-storage
paths: pipeline/scripts/split_rebase_cohort_dryrun.py, pipeline/scripts/slot_records/fsn_upload.py
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
(1) settings (pydantic) reads .env from the cwd, so a worktree run fails with 'database_url Field required': run 'set -a; . /Users/vikash/scrooner/pipeline/.env; set +a' first. (2) The system python3 (3.14 framework build) has no CA bundle: urllib calls to the Supabase storage API (fsn-notes bucket) fail CERTIFICATE_VERIFY_FAILED; use pipeline/.venv/bin/python with SSL_CERT_FILE=$(pipeline/.venv/bin/python -c 'import certifi;print(certifi.where())'). (3) Test worktree code with PYTHONPATH=<worktree>/pipeline/src, else the venv's editable install imports the shared tree. (4) No 'timeout' binary on this Mac.
