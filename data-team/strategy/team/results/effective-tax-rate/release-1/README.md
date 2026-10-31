# Effective tax rate release 1 (Family A, retire.derived_ratio_cells@1)

Module `pipeline/src/scrooner_pipeline/mapper/tax_rate_release.py` (dry-run / apply / restore). Flag default OFF; nothing applied.

- 5,662 derived effective_tax_rate_reported cells at 666 cohort companies: remove 5,655 with a reason, replace 7 with a filed rate. Facts demoted (never deleted): 5,688. Cell lists: `../SUMMARY_COUNTS_TO_CELL_LISTS.json` (the 1,422 whose printed tax and pretax lines exist are listed separately; they are removed too, since effective_tax_rate_reported is printed-only and the displayed gap metric computes tax / pretax itself).
- Digest `d8ee2b36d8c09622cdcd6fef35f8a6fd5388b6431c4d223330532fe896528cac`; live re-plan 2026-11-04: same digest, would apply. Verifier verify/effective-tax-rate-2026-11-04: 15/15 removals, 5/5 others, 7/7 replacements.
- Guards: rule ON, `--confirm RELEASE-TAX-RATE-A-1`, digest equal to PACKAGE.json, `analytics.fact_authority_retired` (migration 0116) present, and the plan re-built from the live database equal to the reviewed digest (stale refuses; re-cut). One transaction; before-images in canonical_fact_retired and fact_authority_retired; restore(run_id) undoes both.
- Tests: `tests/unit/test_tax_rate_release.py` (guards, mutation-checked) and `tests/unit/test_tax_rate_release_sql.py` (plan -> apply -> stale second apply -> restore on the real migrated schema; passes locally on a fully migrated database, skips in CI until SCROONER_TEST_DATABASE_URL and 0116 are present).
- Prerequisite: migration 0116 applied (founder's words). No metric recompute needed (only effective_tax_rate_gap reads these cells and goes blank for removed periods at its next run).
