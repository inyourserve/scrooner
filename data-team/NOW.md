# Scrooner now

Compact orientation only. Generated evidence and the task board win if this file becomes stale.

Updated: 2026-11-08 UTC (Dhairya, manager session `session_01GLmSDyzegqZw4JqC91z7XH`).

## Product objective

For the top 1,000 US companies, every displayed financial cell is either a filing-traceable correct value or a visible, evidenced reason. Never claim universal correctness; publish measured error rates.

## Operating model (founder, 2026-11-04; doc 02 "Locked data decisions")

The hybrid FSN-structure plus company-API build replaces old values in `analytics.canonical_fact` for the 1,000 companies. Load first, prove (`cell_proof`) right after, Verifier samples after; a failed draw means fix and reload. No old-table fallback, no switch view, no per-family patch packages.

## Scoreboard

- Certified companies: 0 / 1,000.
- 1,000-company FSN write (`pipeline-fsn-write.yml`, stage `select_write`, 16 shards, code_ref bc6ab31): founder approved 2026-11-08 ~17:49 UTC; scheduled to start ~21:32 UTC, after the nightly window. Earlier runs 41515572580 and 41708619888 stopped at the nightly-window preflight (nothing written).
- Latest full dry run (reported by the manager session 2026-11-06): 73.2% of template cells valued across 960 of 1,000 companies (top 100: 76.5%); one batch of 40 failed.

## In flight (no production writes)

| Lane | Branch | Next |
|---|---|---|
| Balance sheet: derived total liabilities, unclassified-balance-sheet reason (~94% of those gap keys, 380 companies) | `work/bs/derive-tl-current` | rebase on main, tests, PR, Verifier draw |
| Cash flow: FX identity tags, buyback/dividend detector, absent-line reasons (15-company sample: valued 51.4% to 58.0%) | `work/cashflow/fsn-gaps` | rebase, cohort dry run after the write finishes, PR, Verifier draw |
| Verifier reports 2026-11-01..03 | PR #2 (`verify/consolidated-2026-11-08`) | docs only; merge when CI green |

Merged 2026-11-08: PR #1 (3d093b3), the nightly refresh row-count alert fix plus CI flake and tag-library timeout fixes.

## Waiting on the founder

- Restore stage for any company whose `cell_proof` disagrees after the write (founder's typed words).
- Merging code PRs from the balance-sheet and cash-flow lanes after the Verifier draw.

## Canonical files

- Direction: `data-team/strategy/THE-PLAN.md`
- Execution state: `data-team/strategy/TASK-BOARD-TOP1000.md`
- Compact live view: `python3 scripts/agent_context.py`
- Decisions: `doc/foundational/02_Scrooner_Decision_Register.md`

Do not expand this file into a work log. Keep it under roughly 80 lines.
