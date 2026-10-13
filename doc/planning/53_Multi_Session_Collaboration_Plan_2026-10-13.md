# Multi-Session Collaboration Plan (2026-10-13)

**Why this doc exists.** Several Claude sessions work this repo against one shared dev Supabase instance. On 2026-10-13 `git status` showed ~55 uncommitted files from unknown owners, some days old, and two sessions were about to edit the same coverage modules. This doc fixes who owns what, what is queued, and the rules that stop collisions. It supersedes nothing: the backlog it assigns comes from [doc 52](52_Scrooner_Coverage_and_Ticket_Backlog_Replan_2026-10-11.md) and the launch question (can we launch with the top 1,000-2,000 companies).

**Owners fill in their own rows.** Each session edits only its own section, then commits and pushes in the same turn. Status of rows marked *unconfirmed* was inferred from `git status`/file ages, not stated by the session.

## The launch question this all serves

Grouped coverage (migration 0092, `/app/data-coverage`) gives the baseline on 2026-10-13, core 20 V1 metrics, ranked by market cap, every company counted:

| Group | Avg coverage | Companies below 60% |
|---|---|---|
| Top 100 | 89.05% | 5.0% |
| Top 1,000 | 87.03% | 4.6% |
| Top 2,000 | 83.98% | 7.75% |
| All 5,213 | 70.31% | 26.4% |

Weakest sector in the top 1,000: Financials (71.4%), then Real Estate (77.3%). Biggest missing metrics in the top 2,000: dividend yield, gross margin, ROIC, interest coverage, FCF yield. Goal: raise these numbers; the dashboard records the history.

## Lanes

| Lane | Session | Owns (files / tables) | Current task | Next |
|---|---|---|---|---|
| A. Coverage dashboard and launch readiness | scrooner-98 | `mapper/coverage_groups.py`, `routers/data_coverage.py`, `components/data-coverage/*`, migration 0092, 0094+ | Verify the new dashboard sections visually, then write the launch-readiness check | See "scrooner-98 queue" |
| B. Concept applicability and filing-line evidence | scrooner-f9 | migration 0093 (`company_filing_line_evidence`), `parsers/filing_line_evidence.py`, `probe-filing-lines` command, small edits in `coverage_matrix.py`, `company_coverage_dashboard.py`, `coverage_snapshot.py` | Building evidence layer; later a ~50 min SEC fetch pass (single process) | Reported by f9 |
| C. Data sanity, ticket fixes, coverage denominators | scrooner-64 (confirmed) | Committed work only: `coverage_matrix.py`, `coverage_snapshot.py` denominator fixes, doc 50. No uncommitted files. | Running the whole-population sanity re-measure (`timeseries`, `identities`, `plausibility`), then the rate-limited `scrooner-sanity run` | Re-run `period_completeness` + `snapshot-coverage` for final numbers; Phase 3 design is **offered for handoff** |
| D. Frontend redesign (workspace, watchlist, alerts, company page) | *unconfirmed* | `apps/app/app/app/*`, `components/layout/*`, `components/public/*`, `components/scrooner/*`, `packages/design-system`, `apps/admin` | Uncommitted restyle, oldest files dated 2026-10-02 | Land or discard (see "Stale work") |
| E. Backend (watchlists) | *unconfirmed* | `apps/backend/routers/watchlists.py`, `tests/test_watchlists.py`, `main.py` | Watchlist endpoints, uncommitted | Commit with D |

## Rules (apply to everyone)

1. **Migrations.** 0093 is f9's. Claim the next number by adding a line to the table below *before* writing the file, and apply only a migration that is committed.
2. **Shared modules.** `mapper/coverage_matrix.py`, `coverage_snapshot.py`, `company_coverage_dashboard.py` belong to lane B this week. Lane C (scrooner-64) has already committed its denominator fixes there; it rebases before further edits and tells B first. Lane A reads `analytics.company_data_point_coverage` and does not edit them. If lane B changes how `has_value` or `gap_reason` is set, it tells lane A, because the grouped snapshot reads that table.
3. **Never `git add -A` or `git add .`.** The tree holds other sessions' work. Add named files. If a file you changed also holds someone else's uncommitted edits, split your change into a new file or stage a hand-built blob (`git hash-object -w` + `git update-index --cacheinfo`) rather than committing their work.
4. **Commit and push in the same turn** (standing rule in CLAUDE.md).
5. **Heavy jobs.** `ListAgents` first; message any peer shown `busy`. The pooler allows about 15 connections in total. One SEC fetch process at a time, sharing the rate limiter. Use `set statement_timeout=0` and chunk big analytics queries.
6. **Gitignored name trap.** A directory named `coverage` is gitignored. Use `data-coverage` or similar.
7. **Tell the owner before touching their lane.** Use `SendMessage` with one first line stating the change.

### Migration claims

| Number | Owner | Purpose | State |
|---|---|---|---|
| 0092 | scrooner-98 | `coverage_group_snapshot` | applied, committed |
| 0093 | scrooner-f9 | `company_filing_line_evidence` | in progress |
| 0094 | free | claim here | |

## scrooner-98 queue (lane A)

Ordered; each item ends with a commit, push and a line in this doc.

1. Visually verify `/app/data-coverage` (headless Chrome screenshot) once a logged-in session is available. Not yet possible from this machine, so it needs the user.
2. **Launch-readiness check.** Add a `launch_readiness` section to `/v1/data-coverage/groups` and the page. It reports, per band, pass/fail against rules set up front: average core coverage at least 85%, no sector in the band below 60%, fewer than 10% of companies below 60%. Today this says the top 1,000 passes except Financials, and the top 2,000 does not pass.
3. **Fixable gaps in the top 1,000-2,000** (the "fix first" list): gross margin and ROIC (inputs that do not resolve, mapper tag coverage), interest coverage, FCF yield (capex and CFO TTM), current ratio (no recorded reason). Each fix: investigate with raw tags first, change the mapper, rerun for affected companies only, confirm the grouped snapshot moved.
4. **Financials and Real Estate.** Check which core metrics are really inapplicable to banks versus unmapped. Where inapplicable, the right fix is sector-specific metrics ([doc 33](../execution-plans/33_Scrooner_Sector_Specific_Metrics_Plan.md), FDIC source in doc 32b), not forcing the 20 industrial metrics. Coordinate with lane B, which is producing the applicability evidence.
5. **Dividend yield.** About 1,159 top-2,000 companies lack it; at least 699 have no dividend history. Decide how the dashboard shows non-payers (a real "no dividend" value, or excluded with a stated reason) with the user; do not change the raw lens silently.

## Unassigned backlog (from doc 52)

| # | Item | Needs | Suggested lane |
|---|---|---|---|
| 1 | Fresh yfinance sanity, plausibility, identity, time-series re-run | In progress (scrooner-64) | C |
| 2 | Parser 4: SEC bulk-data lag (about 2,391 tickets) | **Founder decision**, then build | B after decision |
| 3 | Phase 3 period-conditional applicability classifier (SPAC merger timing) | Verify the pattern on more companies, then design. scrooner-64 offers handoff; doc 50 Phase 3 has the writeup. Overlaps lane B's evidence layer, so B or an idle session picks it up, not both | B (first choice) |
| 4 | Re-measure coverage after 1 | `period_completeness` + `snapshot-coverage` | A (reads results) |

## Stale uncommitted work (needs an owner decision)

About 50 modified or untracked files predate today, some by 11 days. Examples: `apps/app/app/app/account`, `alerts`, `watchlist`, `data-coverage/data-coverage.module.css`, `components/layout/StatusPage.tsx`, `WorkspaceHeader.tsx`, `apps/admin/`, `apps/backend/routers/watchlists.py`, `pipeline/src/scrooner_pipeline/sanity/*`, `mapper/expanded_concepts.py`, `ai_query/screen_templates.json`. Until owners commit or discard them:

- The working-tree `data-coverage/page.tsx` still differs from the committed one because lane D has not committed its redesign. Lane A's committed page uses only committed components.
- scrooner-64 confirmed none of the files are theirs; scrooner-f9 and scrooner-98 own only committed work or named files; 2b and ff have not replied. Each owner session: commit your files with named `git add`, or say in this doc that they are scratch and can be discarded. Nobody else deletes them.

## Status log

- 2026-10-13: lane A shipped grouped coverage (commits `3309830` and the follow-up dashboard commit). Lane B announced migration 0093 and the shared-module edits.
