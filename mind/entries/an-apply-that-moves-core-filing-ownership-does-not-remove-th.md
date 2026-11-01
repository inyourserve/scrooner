---
id: an-apply-that-moves-core-filing-ownership-does-not-remove-th
title: An apply that moves core.filing ownership does not remove the previous owner's facts: normalizer/facts.py upserts and never deletes
kind: lesson
tags: shared-accession, facts, normalizer, apply
paths: pipeline/src/scrooner_pipeline/normalizer/facts.py
evidence: DATA-INFERRED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/src/scrooner_pipeline/normalizer/shared_accession_cleanup.py
---
After entity.shared_accession_primary_filer@1 moved 499 combined filings to their primaries (2026-10-31), the four co-registrant subsidiaries (Entergy Arkansas, SCE, SoCalGas, Consumers Energy) still held 1,771 authoritative core.fact rows and 600 canonical cells with the PARENT's consolidated numbers, because a 'normalize facts' rerun is an upsert keyed by (company, concept, unit, period, filing): nothing deletes a fact whose filing no longer belongs to the company. Any rule that changes filing ownership needs its own demote-and-archive step (rule entity.shared_accession_demote_coregistrant_facts@1 does: demote, archive cells via canonical_archive, reason rows, before-image, rollback). Never claim 're-normalization drops them' without reading the writer.
