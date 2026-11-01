---
id: shared-accession-apply-rebuild-the-plan-from-the-dry-run-che
title: Shared-accession apply: rebuild the plan from the dry-run checkpoints with zero SEC requests; the checkpoint 'error' field is an exception repr, not http_404, so both resume rules would re-fetch 430 misses
kind: howto
tags: shared_accession, SEC budget, checkpoints, apply
paths: 
evidence: CODE-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/scripts/shared_accession_apply.py; pipeline/scripts/shared_accession_dryrun.py
---
Checkpoints A_filings/B_carriers/C_headers.jsonl lived in another session's scratchpad (/private/tmp/claude-501/-Users-vikash-scrooner/17dab105-*/scratchpad/sharedacc, 192 MB); copy them before use. Main's phase_c re-fetches every checkpointed miss with an error and the 1c0a952 fix only exempts error == 'http_404', but SECClient raises, so misses are stored as 'HTTPStatusError(...)' and 430 accessions (x up to 3 folders) would be re-fetched: more than the remaining SEC budget. A local, uncommitted edit treating every checkpointed miss as final reproduced plan digest c601ca6212f52840 (499 moves) exactly with 0 SEC requests; the driver's own plan-digest and 5-table digest checks are the safety net. Applied to production 2026-10-31 06:35 UTC; follow-on normalize/map stages run with --ciks; resolve-statement-fallbacks, resolve-conflict-fills and build-coverage-matrix have no --ciks on main.
