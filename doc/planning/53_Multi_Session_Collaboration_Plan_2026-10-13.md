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
| B. Concept applicability, filing-line evidence, nightly/CI | scrooner-f9 (confirmed) | migration 0093, `parsers/filing_line_evidence.py`, `scripts/applicability_probe.py`, `probe-filing-lines` in `jobs/map.py`; small edits in `coverage_matrix.py`, `company_coverage_dashboard.py`, `coverage_snapshot.py`; `scripts/lib/sharded.sh`, `reprocess_recent_filers.sh`, `normalizer/conflict_latest_filed.py`; the nightly/CI watch | Evidence layer; adds gap_reason `line_not_presented_in_filing` on absent cells (has_value stays false, unchanged) plus a separate denominator adjustment in `coverage_snapshot.py`; later a ~50 min single-process SEC fetch pass | Phase 3 classifier (first choice) |
| C. Data sanity, ticket fixes, coverage denominators | scrooner-64 (confirmed) | Committed work only: `coverage_matrix.py`, `coverage_snapshot.py` denominator fixes, doc 50. No uncommitted files. | Running the whole-population sanity re-measure (`timeseries`, `identities`, `plausibility`), then the rate-limited `scrooner-sanity run` | Re-run `period_completeness` + `snapshot-coverage` for final numbers; Phase 3 design is **offered for handoff** |
| G. Site caching scope, type/lint cleanup | scrooner-ff (confirmed, free) | Committed work only: `apps/backend/reference_data.py`, `routers/reference_data.py`, `tests/test_reference_data.py`, `apps/app/lib/company/referenceData.ts`, the 7 call sites + `cache.py`/`main.py` additions, doc 54, `doc/learnings/2026-10-13-sitewide-caching-built.md`. No uncommitted files. | Done: built (4f0e80a), then a real CI regression it caused (force-dynamic removed from 5 flat pages + sitemap.ts + the directory route broke `next build`'s static prerender, since it now fetches apps/backend with nothing running at build time) found by f9 and fixed same day (a275335), both verified live against a real build with the backend made unreachable on purpose. CI (`CI` workflow) green as of 6032f91. | Free. Declined the mypy/Ruff handoff twice (no pipeline context; f9 took it, 806b0a4). Available for new work. |
| F. `data_limit` ticket triage (cockpit tickets) | scrooner-2b (confirmed) | Committed work only: `sanity/period_completeness.py` (classifier), migrations 0089/0090, `tests/unit/test_period_completeness.py`. No uncommitted files. | Finishing `resolve-conflict-fills` then a whole-population `period_completeness` (heavy DB, ~1h, started 10:36 IST) after the `basic_eps` backfill | (1) cash-flow `...ContinuingOperations` tag mapping (migration 0095), (2) Q4 / YTD-quarter ticket analysis (about 26k open), (3) non-trading status via yfinance (decision needed from founder), (4) accepted from f9: widen conflict-latest-filed |
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

**Next free number: 0107** (0098-0106 claimed 2026-10-22 below, none written/applied on main yet). Claim a number here BEFORE writing the file, and never skip one: `scripts/check_migrations.py` requires 0001..N contiguous, and a gap turns CI red for everyone.

| Number | Owner | Purpose | State |
|---|---|---|---|
| 0092 | scrooner-98 | `coverage_group_snapshot` | applied, committed |
| 0093 | scrooner-f9 | `company_filing_line_evidence` | applied, committed (`a18dd40`) |
| 0094 | scrooner-f9 | reserved no-op (restores contiguity after 0095 was committed first) | committed |
| 0096 | data-engineer (top-1000 B0a) | `company_data_point_coverage.has_value_any_period` (old ever-filled figure kept) | written and committed, NOT applied (apply after scrooner-82's D2) |
| 0097 | data-engineer (top-1000 P1) | `analytics.certification_finding` + `analytics.company_certification` (certification suite output) | written and committed, NOT applied |
| 0095 | scrooner-2b | map `...ContinuingOperations` cash-flow tags as fallbacks (investing, financing, CFO) | committed (`e7c1b25`) |
| 0098 | Period Engineer | per-share `gap_cause` CHECK + `analytics.canonical_fact_retired` | claimed, not written/not applied (file written on a held branch only) |
| 0099 | Period Engineer | split tables `split_event` + `filing_share_basis` | claimed, not written/not applied |
| 0100 | Data Engineer (lane 3) | `cell_evidence` (append-only), `cell_blank_reason` (keyed by dates), `core.filing_registrant`, `core.company_identity_audit`, rule_run manifest | claimed, not written/not applied |
| 0101 | Data Engineer | minimal definition registry (`metric_definition_active` view + one-active-per-name unique index) | claimed, not written/not applied |
| 0102 | Data Engineer | thin `cell_state` table with run id | claimed, not written/not applied |
| 0103 | Period Engineer | `core.derived_fact_input` | claimed, not written/not applied |
| 0104 | (unassigned) | `company_group` + `metric_template` (after design review) | claimed, not written/not applied |
| 0105 | (unassigned) | output_versioning | claimed, not written/not applied |
| 0106 | (unassigned) | `slot_observation` (optional) | claimed, not written/not applied |

## scrooner-98 queue (lane A)

Ordered; each item ends with a commit, push and a line in this doc.

1. Visually verify `/app/data-coverage` (headless Chrome screenshot) once a logged-in session is available. Not yet possible from this machine, so it needs the user.
2. **Launch-readiness check (built 2026-10-13).** Add a `launch_readiness` section to `/v1/data-coverage/groups` and the page. It reports, per band, pass/fail against rules set up front: average core coverage at least 85%, no sector in the band below 60%, fewer than 10% of companies below 60%. Today this says the top 1,000 passes except Financials, and the top 2,000 does not pass.
3. **Fixable gaps in the top 1,000-2,000** (the "fix first" list): gross margin and ROIC (inputs that do not resolve, mapper tag coverage), interest coverage, FCF yield (capex and CFO TTM), current ratio (no recorded reason). Each fix: investigate with raw tags first, change the mapper, rerun for affected companies only, confirm the grouped snapshot moved.
4. **Financials and Real Estate.** Check which core metrics are really inapplicable to banks versus unmapped. Where inapplicable, the right fix is sector-specific metrics ([doc 33](../execution-plans/33_Scrooner_Sector_Specific_Metrics_Plan.md), FDIC source in doc 32b), not forcing the 20 industrial metrics. Coordinate with lane B, which is producing the applicability evidence.
5. **Dividend yield.** About 1,159 top-2,000 companies lack it; at least 699 have no dividend history. Decide how the dashboard shows non-payers (a real "no dividend" value, or excluded with a stated reason) with the user; do not change the raw lens silently.

## Where to attack first: top 1,000 (measured 2026-10-13)

Missing values among the top 1,000 by market cap, core 20 metrics, split Financials versus everything else. Raw lens, no exclusions.

| Metric | Financials | Other sectors | What the gap really is | Lane |
|---|---|---|---|---|
| Dividend yield | 45 | 433 | Mostly non-payers. A product decision (show "no dividend", or exclude), not a data fix | A + user |
| Gross margin | 127 | 145 | Other sectors: 28 REITs, 11 electric utilities, oil and gas, railroads. They report no gross profit line. Reasons: `incomplete:subtract` 85, `incomplete:gross_profit_resolved` 58 | B (line evidence) |
| ROIC | 112 | 169 | 66 `incomplete:total_debt_resolved`; about 76 `incomplete:ttm_operating_income`. The total_debt part may already be improved by 64's convertible-notes fallback; re-measure first | C |
| Interest coverage | 104 | 191 | Same operating income / interest expense inputs | C, B |
| FCF yield | 71 | 200 | Capex and CFO TTM (cash-flow tag mapping) | F (migration 0095) |
| Current ratio | 116 | 59 | 45 Real Estate, 10 Industrials unexplained; Financials do not present a current/non-current split | B |
| Operating margin | 82 | 57 | Bank-style statements | B / sector metrics |

Reading: roughly half of the top-1,000 gap is Financials and Real Estate, which present statements differently, so the 20 industrial metrics cannot be filled for them by tag mapping. That needs sector-specific metrics ([doc 33](../execution-plans/33_Scrooner_Sector_Specific_Metrics_Plan.md)) or an honest "not presented" state from lane B's evidence layer. The other half is ordinary mapping work in lanes C and F. Lane A does not edit the mapper for these; it re-measures after each lane lands and records the movement in the dashboard history.

## Handoffs offered (scrooner-f9)

| Item | Proposed owner |
|---|---|
| mypy: 93 errors, and Ruff on 3 files | **scrooner-64 (confirmed, 2026-10-13).** The job was actually crashing with 1 error ("Duplicate module named 'reference_data'", from doc 54's apps/backend/reference_data.py), hiding ALL real signal -- fixed with `--explicit-package-bases` (commit `806b0a4`). mypy now runs clean and surfaces 81 real findings in 27 files, not yet fixed (touches files other lanes own -- concept_fallback.py, coverage_snapshot.py, mapper/ttm.py, price_metrics.py, derived.py, revenue_parser.py, pilot.py, insider_summary.py, yfinance_financials/*, apps/backend reference_data.py/main.py). Ruff format debt cleared for the 4 committed files that had it (whitespace only); watchlists.py/test_watchlists.py left untouched (orphaned, unowned per the stale-work section below). |
| Cross-tag `cfo` `quarter_not_derived` | scrooner-64 |
| Widen conflict-latest-filed to more tags | scrooner-2b (accepted 2026-10-13; queued after the Q4/YTD analysis) |

**scrooner-f9 on Phase 3 (period-conditional classifier): yes, as the step after the evidence layer, in two gated steps.** It is a different problem from lane B's evidence layer, even though both aim at "genuinely doesn't apply". Lane B answers *company-level* questions for concepts many companies never report (inventory, R&D, goodwill, gross profit, ...) by reading the company's own filing. Phase 3 is *period-level*: universally reported concepts (cash flow, EPS, income tax) missing only for pre-merger shell years. Order of work:

1. Finish and land the evidence layer first (0093, `filing_line_evidence`, the three coverage modules, the SEC pass).
2. Phase 3 step 1 only: sample the `cash_flow_investing` / `cash_flow_financing` gap population and verify the SPAC-merger-timing pattern generalizes past the three companies doc 50 traced. **No classifier is built until that is verified**, and the result goes in doc 50, including if the answer is "it does not generalize".
3. Phase 3 step 2 (design and build, keyed off a company's first full post-transition fiscal year, not SIC): only if step 2 holds. If another session has capacity sooner (scrooner-ff is idle), it can take step 1 now; tell me and I will not duplicate it.

Evidence-layer facts other lanes can rely on: it will **not** change how `has_value` is set. It adds one `gap_reason` value, `line_not_presented_in_filing` (the company's latest 10-K/10-Q shows no such line on the face of its balance sheet / income statement, with the accession stored), and `line_in_filing_not_extracted` (the line is there and we have no value: a real, ranked worklist). Absence from the face is evidence, not proof (measured 14-34% of the time we HAVE a value without a face line), so the dashboard text says "not shown on the statements", not "does not apply".

Watchlist feature (`apps/app/.../watchlist`, `apps/backend/routers/watchlists.py`): scrooner-98 confirms it is **not** lane A's. **No session claims it**: 64, 2b, ff, f9 and 98 each say they do not own it.

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
- scrooner-64 confirmed none of the files are theirs; scrooner-f9 and scrooner-98 own only committed work or named files; scrooner-2b and scrooner-ff also own none of them. **Nobody owns the ~50 remaining files** (watchlist, alerts, account, admin app, design-system, header/company-page restyle, sanity/mapper edits): they look like orphaned work from earlier or ended sessions, or from the user's own editor. This needs the user to say keep or discard; no session should commit or delete them meanwhile. Each owner session: commit your files with named `git add`, or say in this doc that they are scratch and can be discarded. Nobody else deletes them.

## Known working-tree breakage

`next build` fails in the shared working tree on uncommitted, ownerless WIP in `apps/app/components/public/HeaderMenu.tsx` (an `as const` array where only one entry has `action`, so `link.action` on line 33 does not type-check). Committed `main` does not contain it, so deploys from `main` are unaffected, but anyone running a local build hits it. Reported by scrooner-ff. Fix belongs to whoever finishes the watchlist-nav work; the user decides that (see the orphaned files above).

## Status log

- 2026-10-13: lane A shipped grouped coverage (commits `3309830` and the follow-up dashboard commit). Lane B announced migration 0093 and the shared-module edits.

- 2026-10-13: lane B shipped the filing-line evidence layer (`a18dd40`: migration 0093, `parsers/filing_line_evidence.py`, `probe-filing-lines`, gap reasons in `coverage_matrix.py`, dashboard wording, snapshot denominators). Population SEC pass run sharded (4 shards, ~100 companies/min); results go in `doc/learnings/`. `validate_latest_filed_vs_frames.py` committed for lane F's tag widening. scrooner-ff declined the mypy/Ruff handoff: unowned.
- 2026-10-13: scrooner-ff shipped site-wide caching from doc 54 (commit 4f0e80a): cached backend directory/sector/industry endpoints, five pages moved off direct Postgres queries.
- 2026-10-17: user asked to close all 5 running sessions. See [doc 55](55_Session_Handoff_and_Close_Out_2026-10-17.md) for the full close-out snapshot — what's committed, what's still open (lane C's `cfo` `quarter_not_derived` investigation is genuinely unfinished, not resolved), and the orphaned-files decision that needs the founder.
- 2026-10-17: **scrooner-ff lane closed out, session ending (user closing sessions to save tokens).** Final state, so a fresh session can pick up from files alone, no conversation memory needed: doc 54 (site-wide caching) is fully built and verified (`4f0e80a` build, `a275335` fix for the force-dynamic/build-time-prerender CI regression it caused — see that commit's message and `doc/learnings/2026-10-13-sitewide-caching-built.md`'s addendum for the full story and the generalizable rule, also now in root `CLAUDE.md`). `main` is green on the `CI` workflow as of `6032f91` and still green through this session's own later commits (`d99e8f9`, `e721759`). Lane G has zero uncommitted files and no open task. Declined-not-owned: mypy/Ruff cleanup (scrooner-f9 took it, `806b0a4`), the watchlist feature (nobody claims it, see "Handoffs offered" above), and the orphaned ~50-file stale-work pile (see "Stale uncommitted work" above — still needs a founder keep/discard call, not touched by this lane). Not re-verified this session, so check before trusting: whether `apps/app/components/public/HeaderMenu.tsx`'s working-tree-only type error (see "Known working-tree breakage" above) has since been fixed or committed by whoever owns the watchlist-nav work — last known state was still broken, uncommitted, unowned.
