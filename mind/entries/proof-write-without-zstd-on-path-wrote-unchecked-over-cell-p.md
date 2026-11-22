---
id: proof-write-without-zstd-on-path-wrote-unchecked-over-cell-p
title: Proof --write without zstd on PATH wrote UNCHECKED over cell_proof (2026-11-13)
kind: gotcha
tags: proof, cell_proof, incident
paths: pipeline/src/scrooner_pipeline/proof/fsn.py, pipeline/src/scrooner_pipeline/jobs/proof.py
evidence: CODE-CHECKED
status: active
source: cfb40054 on main; run_proof110.sh/proof_one.sh under xargs
created: 2026-11-13
verified: 2026-11-13
---
Cause: scrooner-proof run --write launched from xargs with a minimal PATH; zstd not found, every FSN quarter treated as missing, so cells were marked UNCHECKED. Impact: 172,228 UNCHECKED + 3,789 DISAGREE overwritten for the 110 companies; no served values changed; the guard applies at rewrite time and reads each cell's last DISAGREE row; held cells are not served so they are not re-proven and their 1,862 pre-incident DISAGREE rows stayed intact. Fix: rerun with PATH set, plus code guard (cfb40054): require_zstd() before any work, DecompressError (not a FileNotFoundError, so distinct from quarter-not-in-bucket) aborts the whole run before the upsert; exit code 2. Tests: pipeline/tests/unit/test_proof_zstd_guard.py, mutation-checked. Lesson: a batch job launched via xargs/cron must export PATH; a proof run must fail, not degrade, when its tools are missing.
