# Founder queue

Things only the founder (repository admin) can do. Each item has exact steps. Nothing here blocks other work. Add new items at the bottom; mark done items with the date.

## 1. Delete the 182 merged or patch-equivalent branches (GitHub-ops, 2026-11-16)

The cleanup was approved. The agent's delete was blocked by its safety classifier, so it needs a person.

- **List, with SHAs:** [`doc/infra/deleted-branches-2026-11-16.txt`](../../doc/infra/deleted-branches-2026-11-16.txt). Every branch on it is merged into main or has all its commits in main. Branches with unique work are not on it.
- **Delete** (from a clone of the repository, on main after PR #15 merges):
  `grep -v "^#" doc/infra/deleted-branches-2026-11-16.txt | awk '{print $3}' | xargs -n 20 git push origin --delete`
- **Restore any one:** `git push origin <sha>:refs/heads/<branch>`, with the SHA from the list.
- Alternatively, allow branch deletion for the GitHub-ops cloud session and it will run this itself.

## 2. Protect main: land through PRs with auto-merge on green (GitHub-ops, 2026-11-16)

Exact settings are in [`doc/infra/GITHUB.md`](../../doc/infra/GITHUB.md), section "Protecting `main`". In short:
- Settings, General: turn on **Allow auto-merge** and **Automatically delete head branches**.
- Settings, Rules, Rulesets: create a ruleset for the default branch.
  - Require a PR, with 0 approvals.
  - Required checks: `Detect changed areas`, `Python tests and correctness lint`, `Migrations, documentation, and secrets`, `Next.js frontend tests and production build`.
  - Block force pushes and deletion.
  - Bypass: the GitHub Actions app, for the hourly coverage and certification-request commits.
- Then root `CLAUDE.md`'s rule "A commit on `main` is pushed in the same turn" becomes "land through a PR with `gh pr merge --auto`".

Why: 13 red CI runs in a row on main on 11-14, and main red again 11-15 20:53-21:30 (a test edit left in commit 12b975f8).

## 3. From 2026-11-23: delete the 7 retired workflow files (GitHub-ops)

They have been disabled since 11-16 through `vars.ALLOW_RETIRED_WORKFLOWS`.
- No action is needed unless someone set that variable during the week.
- GitHub-ops opens the deletion PR on 11-23; it only needs a merge.
