# Founder queue

Items that need the founder's own typed words. Work continues around each one; nothing blocks on this file.
Newest first. When an item is approved, move it to doc 02 (decision register) and strike it here.

## Open

0. **Load the 42 missing filings into fsn.* for the top-110** (pipeline-fsn-load-filings.yml, apply=true).
   - The list is data-team/strategy/fsn-missing-filings-2026-11-16.csv: 11 recent Q3 10-Qs, MRVL FY2021 10-K, and 10-K/A and 10-Q/A amendments.
   - The dry run (Actions run 43762675045) writes nothing; its plan is in that run's artifact.
   - Insert-only for those accessions. It runs on Actions at 2 SEC req/s.
   - Sentence: "I approve loading the 42 missing filings in fsn-missing-filings-2026-11-16.csv into fsn.* for the top-110."
1. **Product page hides (storage).** Founder said "Decide later" on 2026-11-16.
   - What: one per-cell display-state table keyed (company, data point, period), holding the hide basis and evidence accession. It supersedes the written-but-unapplied migration 0127 (`shown_from`).
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
