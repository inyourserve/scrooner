# Family C release 1: derived EPS quarters (retire.derived_per_share_cells@1 + pershare.never_derive_ttm@1)

Module `pipeline/src/scrooner_pipeline/mapper/per_share_release.py` (dry-run / apply / restore). Flags default OFF; nothing applied.

## What it does
21,894 EPS cells at 929 cohort companies (cell lists: `../dryrun-v4/COUNTS_TO_CELL_LISTS.json`): remove 21,117 with a reason (Q4 not filed separately 15,675; not captured 5,440; copies disagree 2), replace 314 (filed 10-K/10-Q fact 204; FSN filed value 110, with cell_evidence), review 463 (untouched). Facts demoted (never deleted): 10,952. Metric values to recompute: 25,655.

Digest `de049d472a3b02c5df8ef7e4fb892dc0010ced1b4128d4f60e8917e8cdeee845` (v4). v4 is a re-cut of the Verifier's v3 (`e19bd607...`, verify/eps-family-c-v3-2026-11-02, 15/15): the only difference is 10 canonical_fact ids at company 3710 that the nightly re-issued (`../dryrun-v4/changed_cells_vs_v3.csv`); values, sources and facts are identical.

## Guards
apply refuses unless both rules are ON, `--confirm RELEASE-PER-SHARE-C-1`, the digest equals PACKAGE.json, `analytics.fact_authority_retired` and `analytics.slot_protected_cell` (0113) exist, and the plan RE-BUILT from the live database has exactly this digest (any drift refuses: re-run the dry run and re-cut). One transaction: rule_run, fact before-image + demotion, cell archive + write, FSN evidence, slot protection for the 110 FSN-sourced cells. restore(run_id) undoes cells, facts and protection.

The nightly re-issues canonical_fact ids (delete-then-insert), which changes the digest without changing content: run the dry run right before the apply; a refusal means re-cut, not a data problem.

## Prerequisites (each blocks the apply)
1. Migration for `analytics.fact_authority_retired` (shared with Family B; not written on main; next free number 0114 per doc 53). Founder's words to apply.
2. Family B's Normalizer deriver gate (`normalizer/derived.py` on review/family-b-split) on main and running in the nightly. Without it the next Normalizer run re-derives the EPS quarters this release demotes.
3. In the same step as the apply, recompute metrics for `touched_company_ids_<run_id>.txt` (scrooner-map calculate, ttm-returns, ttm-margins, growth, calculate-price-metrics) with `pershare.never_derive_ttm@1` ON; otherwise the TTM/P-E/growth stages derive per-share values again.

## Order relative to Family B (retire.proxy_form_cells@1) and W3 (source.periodic_form_only@1)
**C can apply before B and before W3.** Evidence (read-only, 2026-10-31):
- C and B are disjoint: none of C's 10,952 demoted facts is on a proxy form (10-K 10,758, 10-K/A 146, 10-Q 37, 8-K 7, 20-F 4); all 204 filed replacements are 10-K/10-K/A/10-Q facts; C has no cell at Pinnacle (company 4938). B's scope is facts filed on DEF 14A-family forms.
- C and W3 overlap in 7 derived facts whose filing is an 8-K (companies 5306, 5544 x2, 3600 x2, 5347 x2). Applying W3 first can change Stage 2e outcomes and make C's digest stale (a re-cut, not an error). Applying C first is consistent with W3 (C demotes them; W3 then ignores 8-K facts anyway).
- One caveat: do not restore C on its own after W3 has applied. C's restore writes back `is_authoritative = true` for those 7 8-K facts; re-run Stage 2e after such a restore (the same caveat B15 records for B and W3).
