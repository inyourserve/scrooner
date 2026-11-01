---
id: after-the-shared-accession-re-own-the-four-former-owners-eai
title: After the shared-accession re-own, the four former owners (EAI, SCE, SoCalGas, Consumers) KEEP their facts on the moved filing: the facts stage upserts and never deletes, and the rule module says so
kind: gotcha
tags: shared_accession, orphan facts, wrong value, subsidiaries
paths: pipeline/src/scrooner_pipeline/normalizer/facts.py
evidence: DATA-INFERRED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/src/scrooner_pipeline/normalizer/shared_accession.py
---
The dry-run report (38-SHARED-ACCESSION-DRYRUN-2026-10-31.md) said the subsidiaries' parent-quarter rows would be dropped on re-normalization; they were not. normalize facts logged skipped_no_filing for all of them (142: 467, 1079: 394, 1080: 600, 1165: 384) but core.fact insert is ON CONFLICT DO UPDATE with no delete, and the module docstring states non-primary facts are NOT deleted (Verifier decides). Live after the apply: 1,772 orphan facts and 600 canonical rows (164/172/154/110) of the four subsidiaries still carry the parent's consolidated quarter (accessions 0000065984-26-000283, 0000827052-26-000059, 0001032208-26-000045, 0000811156-26-000032). Needs a flag-gated demotion/delete rule with its own dry run, not a hand delete.
