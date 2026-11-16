# Founder queue

Items that need the founder's own typed words. Work continues around each one; nothing blocks on this file.
Newest first. When an item is approved, move it to doc 02 (decision register) and strike it here.

## Open

- **Migration 0129 (fixed search_path on 8 trigger functions), written, replay-proven in CI, NOT applied.** Clears 8 Supabase advisor warnings `function_search_path_mutable`; metadata-only. File `pipeline/db/pending/0129_trigger_function_search_path.sql` (number 0129 taken because it was free in doc 53; the request said 0130). Approval sentence: "I approve migration 0129 (fixed search_path on 8 trigger functions) for the dev database."

- **Shares outstanding = shares issued − treasury shares (same filing).** Founder decision 2026-11-01 (doc 02, item 4) says "EPS and instants are never derived"; Dhairya's revised ruling of 2026-11-16 would show shares outstanding as issued minus treasury when both are printed in the same filing's own column (balance-sheet face or parenthetical), with both signed parts as evidence. The serving path is built and dormant (c32da4c0); the Tag Expert flips DERIVE_SHARES=1 only after this amendment. About 312 cells.
  - Sentence: "I amend the 2026-11-01 instant rule: shares outstanding may be shown as shares issued minus treasury shares when both are printed in the same filing's own column."
- **Proof rule resolver_beats_combined** (branch `proof/resolver-wins-over-combined`, b501fd23; ONE-PATH: the resolver decision is the single source). When the resolver's structural row holds a cell, an older company_tag_map "combined" status no longer vetoes it; the cell is still checked against the filing's own line. It is a rule-scoped change (only cells a combined row spans are re-proved, no global re-prove). It lifts the veto on 70 open cells; 52 of them already show the resolver's value (AMGN, ANET, AAPL, ABBV, PANW, CAT, COST).
  - Sentence: "I approve the resolver_beats_combined proof rule (branch proof/resolver-wins-over-combined) for merge to main."
- **Proof rules stated_zero and text_stated** (branch `proof/stated-zero-2026-11-16`, head 39db00aa, CI green run 43819412338). A cell whose value the filing states in words is PROVEN when the resolver row carries the exact quote, locator, accession and a matching period. A stated zero needs the value to be 0; a text-stated value must be nonzero and equal the stated figure. These are two new rules under the rule-scoped proof system, so only those cells are re-proved (no global re-prove). Serving and display are already on main (3b83973a, edf2cfa1); Ritwik samples these cells in every certification. First cells: MCK R&D FY2021-26.
  - Sentence: "I approve the stated_zero and text_stated proof rules (branch proof/stated-zero-2026-11-16) for merge to main."
0a. **Apply the pending migration set 0124-0128 to the dev database** (Data Engineer, 2026-11-16). One approval for the whole set; 0127 is dropped (listed in `pipeline/db/migrations/SKIPPED.txt`).
   - Sentence: "I approve migrations 0124-0128 (verifier_check, company_tag_map dims, metric lineage, company x tag x metric library; 0127 skipped) for the dev database."
   - Files are in `pipeline/db/pending/`. CI proof for every line below: Actions run 43812642996 (Pending migrations replay, a fresh Postgres 16 with all committed migrations 0001-0123, then 0124, 0125, 0126, 0128 in order, one smoke SELECT per created object and column, plus guard checks for 0124 and 0125). Nothing has been applied to any shared database.
   - 0124 `analytics.verifier_check`: the Verifier's filing checks as data, writable only by a session that sets `scrooner.writer = 'verifier'`. Run 43812642996, smokes: table, guard raises. New table; rollback is `drop table`.
   - 0125 `analytics.company_tag_map.dims`: the FSN segment string so member-only lines (e.g. cost of sales by ProductOrService) and a single class-of-stock member can be mapped; replaces the overlap trigger function. Run 43812642996, smokes: column, constraint, function. The value-path code that uses it is on branch work/engineering/tagmap-dims, not on main; the column defaults to '' so nothing on main changes.
   - 0126 metric lineage: nullable `metric_value.formula_fingerprint` and `registry_version`, plus read-only views `v_company_metric_inputs` and `v_company_metric_status`. Run 43812642996, 5 smokes.
   - 0128 tag library: `analytics.tag_library_entry`, `analytics.resolver_decision` and the read-only view `company_tag_metric`. New objects only; rollback is `drop view` and two `drop table`. Run 43812642996, 3 smokes. Its rebuild (`pipeline-tag-library-rebuild.yml`, dry run first, then apply=true) is a separate step after the tables exist; the 2026-11-16 dry run gave `tag_library_entry` 2,757 rows and `resolver_decision` 68,849 rows.
   - The numbers move from `pending/` into `migrations/` (contiguity check passes with 0127 skipped) in the commit that applies them.

0. **Load the 42 missing filings into fsn.* for the top-110** (pipeline-fsn-load-filings.yml, apply=true).
   - The list is data-team/strategy/fsn-missing-filings-2026-11-16.csv: 11 recent Q3 10-Qs, MRVL FY2021 10-K, and 10-K/A and 10-Q/A amendments.
   - The dry run (Actions run 43762675045) writes nothing; its plan is in that run's artifact.
   - Insert-only for those accessions. It runs on Actions at 2 SEC req/s.
   - Sentence: "I approve loading the 42 missing filings in fsn-missing-filings-2026-11-16.csv into fsn.* for the top-110."
1. **Product page hides (storage).** Founder said "Decide later" on 2026-11-16.
   - What: one per-cell display-state table keyed (company, data point, period), holding the hide basis and evidence accession. It supersedes the dropped migration 0127 (`shown_from`, now listed in SKIPPED.txt).
   - Until applied: the coverage export is the source of truth and the stock page shows every line.
   - Size: from the latest display export (see `data-team/strategy/top100-display-summary-*.csv`).
   - Sentence: "I approve the per-cell display-state migration for hidden rows and years, keyed by company, data point and period, with hide basis and evidence accession."
2. **Nightly hybrid path on** (`FSN_NIGHTLY_STAGE` / `HYBRID_NEW_PATH`). Gated on the end-to-end test of the onboarding chain; Dhairya brings the sentence when that passes.

## Covered by existing approvals (run without asking)

- Top-100 per-company reruns on Actions: "complete the task on automation", 2026-11-16.
- add-dim-notes loads 1 and 2: "Yes, run the load", 2026-11-16.
- ONE-PATH steps 1-6 under their gates: approved 2026-11-16 (doc 02 e304d0a9).

## Repository settings (GitHub-ops, 2026-11-16; approved cleanup, needs admin hands)

### R1. Delete the 182 merged or patch-equivalent branches (GitHub-ops, 2026-11-16)

The cleanup was approved. The agent's delete was blocked by its safety classifier, so it needs a person.

- **List, with SHAs:** [`doc/infra/deleted-branches-2026-11-16.txt`](../../doc/infra/deleted-branches-2026-11-16.txt). Every branch on it is merged into main or has all its commits in main. Branches with unique work are not on it.
- **Delete** (from a clone of the repository, on main after PR #15 merges):
  `grep -v "^#" doc/infra/deleted-branches-2026-11-16.txt | awk '{print $3}' | xargs -n 20 git push origin --delete`
- **Restore any one:** `git push origin <sha>:refs/heads/<branch>`, with the SHA from the list.
- Alternatively, allow branch deletion for the GitHub-ops cloud session and it will run this itself.

### R2. Protect main: land through PRs with auto-merge on green (GitHub-ops, 2026-11-16)

Exact settings are in [`doc/infra/GITHUB.md`](../../doc/infra/GITHUB.md), section "Protecting `main`". In short:
- Settings, General: turn on **Allow auto-merge** and **Automatically delete head branches**.
- Settings, Rules, Rulesets: create a ruleset for the default branch.
  - Require a PR, with 0 approvals.
  - Required checks: `Detect changed areas`, `Python tests and correctness lint`, `Migrations, documentation, and secrets`, `Next.js frontend tests and production build`.
  - Block force pushes and deletion.
  - Bypass: the GitHub Actions app, for the hourly coverage and certification-request commits.
- Then root `CLAUDE.md`'s rule "A commit on `main` is pushed in the same turn" becomes "land through a PR with `gh pr merge --auto`".

Why: 13 red CI runs in a row on main on 11-14, and main red again 11-15 20:53-21:30 (a test edit left in commit 12b975f8).

### R3. From 2026-11-23: delete the 7 retired workflow files (GitHub-ops)

They have been disabled since 11-16 through `vars.ALLOW_RETIRED_WORKFLOWS`.
- No action is needed unless someone set that variable during the week.
- GitHub-ops opens the deletion PR on 11-23; it only needs a merge.

## Definition call: derived instants from printed lines in the same filing (Dhairya, 2026-11-17)

Founder decision 2026-11-01 (doc 02, "company-wise FSN statement store", item 4) says "EPS and instants are never derived". Two chief-of-staff rulings compute an instant the filing does not print as one line, from lines it does print in the SAME filing:
- total_liabilities = L&SE total − total equity incl. NCI − mezzanine (ruling C2, 2026-11-13; already served as DERIVED, flagged derived_not_printed);
- shares_outstanding = shares issued − treasury shares, both printed in the same BS face/parenthetical, only when no outstanding count is printed (2026-11-17; ~312 cells; matches the filer's own outstanding count exactly wherever one exists: PM all years, LIN, CVX). Held OFF (DERIVE_SHARES) until you decide.

Dhairya recommends allowing both (every input printed, same filing, flagged derived, Ritwik samples). EPS stays never derived.
Sentence to type (Dhairya's session is fine): "I approve derived instants from printed lines in the same filing for total_liabilities and shares_outstanding (issued minus treasury); EPS stays never derived."
