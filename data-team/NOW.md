# Scrooner now

Compact orientation only. Generated evidence and the task board win if this file becomes stale.

Updated: 2026-11-08 UTC (Dhairya, manager session `session_01GLmSDyzegqZw4JqC91z7XH`).

## Product objective

For the top 1,000 US companies, every displayed financial cell is either a filing-traceable correct value or a visible, evidenced reason. Never claim universal correctness; publish measured error rates.

## Operating model (founder, 2026-11-04; doc 02 "Locked data decisions")

The hybrid FSN-structure plus company-API build replaces old values in `analytics.canonical_fact` for the 1,000 companies. Load first, prove (`cell_proof`) right after, Verifier samples after; a failed draw means fix and reload. No old-table fallback, no switch view, no per-family patch packages.

## Scoreboard

- Certified companies: 0 / 1,000.
- 1,000-company FSN write: run 42561798991 (2026-11-09 04:26 UTC, founder-approved, full SHA bc6ab31b...) WROTE NOTHING to canonical_fact (analytics.slot_protected_cell: 0 rows since 04:00); cancelled ~08:05 UTC. Load into fsn.* worked (893 companies), but step 8 `scrooner-fsn pilot` against production failed every company with QueryCanceled (statement timeout, ~3 min each; shards 0 and 2: 47/47 and 59/59), so no cells, and step 12 crashed on the empty out/cells glob. Shards 4/6/7 died in Load on `connection is lost` (rollback on a dead connection kills the shard). Cohort dry runs use a scratch DB, so they never hit this. Root cause and fix assigned to the balance-sheet lane. Earlier: run 42559698212 failed at checkout (short SHA); always pass the full SHA.
- Latest full dry run (reported by the manager session 2026-11-06): 73.2% of template cells valued across 960 of 1,000 companies (top 100: 76.5%); one batch of 40 failed.

## Priorities and owners (manager session, 2026-11-09 ~16:05 UTC)

| # | Priority | Owner (cloud session) |
|---|---|---|
| 1 | Top-100 FSN write (run 42649721096, code 1beb755, after PR #8's timeout fix), then cell_proof | manager |
| 2 | Post-write Verifier draw: 200 cells / 100 companies, answer key built from filings in advance | Verifier ("Scrooner production cells verification") |
| 3 | First certificates: what certifies a company, blockers, ranked plan (MSFT, HD, top 100) | Certification lead (was "Sector-template layer build") |
| 4 | Release case for held families (balance sheet, debt, capex, D&A) to add to the write | New cloud session "Family release prep" (session_01GLmSE3yJhPu25eryM5Zsen); the FSN-expert session stays read-only by its user's brief |
| 5 | Nightly refresh failure (normalize:facts, 7,000s budget), taken over from the unreachable CI/CD session; then rebase PR #4 | Cash-flow lane |
| 6 | Rebase PR #6; take over and review PR #5 (write vs nightly guard) | Balance-sheet lane |
| 7 | Full 1,000 write after tonight's refresh; then cohort dry runs for PR #4/#6 and a reload | manager |

Not reachable from cloud: the CI/CD session (needs a trusted device) and the Mac sessions (Remote Control off).

## In flight (no production writes)

| Lane | Branch | Next |
|---|---|---|
| Balance sheet: derived total liabilities, unclassified-balance-sheet reason (~94% of those gap keys, 380 companies) | draft PR #6 (`work/bs/derive-tl-current`, rebased, CI green) | Verifier PASS 2026-11-08 (verify/bs-derive-2026-11-08, 375e7f4): 33/33 sampled + 19/19 Kimberly-Clark mezzanine-fix keys right at head 5461439. Remaining: cohort dry run after the write, then ready for the founder |
| Cash flow: FX identity tags, buyback/dividend detector, absent-line reasons (15-company sample: valued 51.4% to 58.0%) | draft PR #4 (`work/cashflow/fsn-gaps-rebased`, CI green). Ruling (Dhairya): a printed 0 in the latest copy is served as 0 | Verifier PASS 2026-11-08 (verify/cf-gaps-redraw-2026-11-08, 4c64d769) at d1a0050: 0 wrong shown values, 21/21 new values, 15/15 cohort absent-line claims; scratch store on 60 cohort companies: CF gaps 6,272 to 283. Brixmor Q4 2015/16 buyback reason follow-up done (26063db). Remaining: cohort dry run after the write; CAD filers CP/IMO open pending the currency ruling |
| Verifier reports 2026-11-01..03 | PR #2 (`verify/consolidated-2026-11-08`) | docs only; founder to merge |
| Verifier verdicts 2026-11-08 (PR #4 and #6 passes) | PR #7 (`verify/2026-11-08-lane-verdicts`) | docs only; founder to merge (ledger conflict with PR #2 is trivial: keep both blocks) |
| FSN write vs nightly jobs: live two-way guard; nightly reprocess selects only filers with work left; normalizer_backlog from ingest time | PR #5 (CI/CD session, CI green before the 11-10 additions) | review (balance-sheet lane), founder to merge before tonight's refresh |

Merged 2026-11-08: PR #1 (3d093b3), the nightly refresh row-count alert fix plus CI flake and tag-library timeout fixes.

Nightly refresh (CI/CD session, 2026-11-10; fix in PR #5, not merged): run 42712874321 (11-09) did NOT fail in normalize:facts (rc 0); it ran out of the 7,000s budget (7,074s) with 1,017 companies, ~73% of which already had their filing's facts (the 4-day window is in calendar days, so Monday re-ran the Thu/Fri filers done Fri-Sun). Fix: select a filer only if its filing's facts are missing or arrived in the last 48h (live: 155 now vs 403 in-window filings; ~300 vs 1,017 on 11-09). Its gate alert normalizer_backlog was a weekend artifact (max filing_date read as midnight); now measured from core.filing.created_at, 5-day limit. Run 42507618224 (11-08) had the same cause: 1,414 companies, normalize:facts killed at its 1,800s stage cap (not an error of its own), budget out at 7,212s.

## Founder decisions 2026-11-09 (~21:40 IST, in the manager session)

- FSN-era certification ladder APPROVED, subject to a Verifier review (pending): checks_clean = I1-I11 pass, template- and reason-aware; reconciled = every headline cell PROVEN in cell_proof, none DISAGREE (replaces the FSDS reconciliation); verified = a recorded Verifier headline check; certified = all of these plus every template cell valued or reasoned. Source: CERTIFICATION-BLOCKERS-2026-11-09.md (branch work/certification-lead/blockers). Goes to doc 02 once the Verifier passes it.
- Sector-template seed (branch work/data-engineer/sector-templates-seed) APPROVED to apply once the Verifier passes it.

- FOUNDER APPROVAL 2026-11-09 ~22:10 IST (manager session): "Yes approved", in reply to: "I approve writing FSN values per (company, data point) on Ritwik's conditions C1-C8, and the top-100 and 1,000-company writes tonight once Ritwik clears the dry run." Ruling: branch review/ruling-done-gate-c4-2026-11-09. Every Ritwik condition stays binding (C7 cohort dry run first; Ritwik clears the C2 valued-to-blank table and the data_points list before each dispatch). The recorded founder decision of 2026-11-01 (doc 02, item 5) goes to doc 02 next.

## Waiting on the founder

- Restore stage for any company whose `cell_proof` disagrees after the write (founder's typed words).
- Merging PRs #2, #3, #5, #7 now; #4 and #6 after their cohort dry runs (the manager session may not merge).
- Currency ruling for CAD filers (RULINGS-CURRENCY-REIT-VINTAGE-2026-10-25.md, Ruling 1, PROPOSED).

## Canonical files

- Direction: `data-team/strategy/THE-PLAN.md`
- Execution state: `data-team/strategy/TASK-BOARD-TOP1000.md`
- Compact live view: `python3 scripts/agent_context.py`
- Decisions: `doc/foundational/02_Scrooner_Decision_Register.md`

Do not expand this file into a work log. Keep it under roughly 80 lines.
