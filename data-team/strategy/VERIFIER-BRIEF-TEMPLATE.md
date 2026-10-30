# Verifier dispatch brief (copy, fill, send)

Role: Verifier. Load skill `scrooner-verify-against-filing` and follow it. Do not re-derive the recipe.

**Verify:** <family and batch, e.g. "balance-sheet totals, batch 9">
**Under test:** branch `<branch>` commit `<sha>` (work in a separate worktree off it; push a branch only, never main)
**Seed:** <integer>
**Files:** <report/manifest paths, relative to the repo>
**Claimed counts:** <e.g. 886 ties, 28 withheld, 174 need the reader>
**Sample overrides:** <none | extra picks for named companies | all withheld cells>
**Request budget:** <max SEC requests, e.g. 400>; free-disk floor 4 GB.

## Deliver
- `data-team/strategy/team/VERIFY-<NAME>-<YYYY-MM-DD>.md` from `verdict_skeleton` (fixed sections).
- Gate: zero wrong shown values; avoidable holds and false holds listed separately.
- Appends: filing-lessons ledger rows, `mind.py add` for durable findings, one line per tag in `data-team/tags/feedback-inbox.md`.
- Final report: status (COMPLETE/PARTIAL/BLOCKED), commands run, evidence with accession + R page, untested scope, SEC request count, next action.

## Rules
SEC: sec.gov only, `SEC_USER_AGENT`, <= 4 req/s, delete downloads. No DB writes, no migrations. Evidence labels: FILING-CHECKED / DATA-INFERRED / ASSUMED; only FILING-CHECKED verifies a value.
