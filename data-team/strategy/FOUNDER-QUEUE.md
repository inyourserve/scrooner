# Founder queue

Items that need the founder's own typed words. Work continues around each one; nothing blocks on this file.
Newest first. When an item is approved, move it to doc 02 (decision register) and strike it here.

## Open

1. **Product page hides (storage).** Founder said "Decide later" on 2026-11-16.
   - What: one per-cell display-state table keyed (company, data point, period), holding the hide basis and evidence accession. It supersedes the written-but-unapplied migration 0127 (`shown_from`).
   - Until applied: the coverage export is the source of truth and the stock page shows every line.
   - Size: from the latest display export (see `data-team/strategy/top100-display-summary-*.csv`).
   - Sentence: "I approve the per-cell display-state migration for hidden rows and years, keyed by company, data point and period, with hide basis and evidence accession."
2. **Nightly hybrid path on** (`FSN_NIGHTLY_STAGE` / `HYBRID_NEW_PATH`). Gated on the end-to-end test of the onboarding chain; Dhairya brings the sentence when that passes.

## Covered by existing approvals (run without asking)

- Top-100 per-company reruns on Actions: "complete the task on automation", 2026-11-16.
- add-dim-notes loads 1 and 2: "Yes, run the load", 2026-11-16.
- Missing filings into fsn.* for the top-110 (pipeline-fsn-load-filings.yml): "everything approved", 2026-11-14 (FSN ingest of missing filings for the top-110).
- ONE-PATH steps 1-6 under their gates: approved 2026-11-16 (doc 02 e304d0a9).
