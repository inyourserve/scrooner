# 48. Engineering head review of docs 46 and 47 (scrooner-4d, 2026-10-22)

Written for: Ritwik (folds this into doc 49), the Data Chief, and the founder. Scope: feasibility, safety and sequencing of the execution layer. No database load was used for this review. Evidence labels: CODE-CHECKED (I read it on `origin/main` today), OBSERVED (seen in this session's runs), ASSUMED (my estimate, not measured). Effort is engineer-days for one engineer, excluding waiting for heavy-job windows.

## 0. State right now (so nobody plans on a wrong picture)
- CI is green on `bab75b8` (OBSERVED): the backup/restore step was fixed by running `pg_dump`/`pg_restore` from the `postgres:16` image.
- The scheduled refresh failed three days running (10-19, 10-20, 10-21), Frames failed 10-19, sanity failed 10-19/20/21 (OBSERVED). Refresh dispatch 39720953149 has been in its reprocess step for over an hour and is not yet proven green. Frames, sanity and health-check have not been re-run. Until all four pass, "the pipeline is healthy" is not a claim anyone can make, and Gate A should not start.
- Migrations 0096 and 0097 are on `origin/main` as files and are NOT applied. The code is safe without them: `coverage_matrix.py` checks `information_schema` for `has_value_any_period` before using it, and `certify` is a manual dry-run job (CODE-CHECKED). So there is no urgency penalty for waiting for the founder's go.
- The founder's "go" for 0096/0097 has not arrived in this session. Nothing has been applied.

## (a) What is not feasible or unsafe as written

1. **Heavy jobs are a single lane, and the plan's cadence needs more windows than the lane has.** One heavy DB job at a time (`heavy-db-jobs`, one running plus one pending, a newer pending run replaces an older one). The scheduled refresh uses a 7,000 s (117 min) reprocess budget inside a 180-min job cap, then sanity at about 19:20Z; Frames Monday 06:05Z (CODE-CHECKED, schedule times OBSERVED). Doc 47 asks for W1-W12 live by day 10, each with "a separate first live run" plus an invariant re-run (about 1.5 h) and a Verifier sample. That is 12+ serial heavy windows in 10 days. Not feasible as 12 releases. Fix: batch into three release trains (section c) and treat a window as a scarce resource in the doc 53 ledger.
   - Danger specific to the queue: a manual dispatch left pending can replace a pending scheduled run, silently skipping a night. Every manual heavy dispatch must be logged in doc 53 with the window, and checked against `gh run list` first.
2. **Connection budget.** `max_connections` is 60, but the session pooler gave only about 15 client connections across every service (CLAUDE.md, measured 2026-08-21). Doc 47 rule 5 says "one connection each", but there are 10 peer sessions plus `apps/app`, `apps/backend`, CI and jobs. Rule: at most 4 agent sessions hold a DB connection at once, the MCP `execute_sql` is not a bulk tool, and any job that needs more than 60 s sets its own `statement_timeout` through the pipeline connection (not MCP). Check `pg_stat_activity` before every heavy start.
3. **`cell_state` as written will not fit.** "Per (company, period, cell)" for all periods since 2015 is roughly 160k cells now for the top 986. At 5,216 companies and about 50 periods per concept the row count reaches tens of millions (ASSUMED: 20-40 M rows, 10-15 GB with indexes). The database is at 46 of 60 GB, and that cap is a plan limit, not a soft one. Fix: store `cell_state` for the latest period and the annual/quarter windows the page shows, plus the full defect register (exceptions only); derive history states on read. Do not build the full-history table for T3 without a size check first (same rule as the ingestion rule: size check before load).
4. **Registrant-context gate (WO-1 item 3) rests on an unsupported premise.** It says to attach a fact only when its `dei:LegalEntityAxis` context names the registrant. But the Company Facts API strips dimensional data entirely (doc 22, confirmed live). The Entergy Arkansas problem therefore cannot be fixed by reading context from the data we ingest. Likely mechanism (DATA-INFERRED, to be confirmed by the Verifier): in a combined filing, the API serves the non-dimensional, parent-level values under every co-registrant CIK. Workable fix: detect accessions that appear under more than one CIK, keep the fact only for the primary filer (the filing's own submission header names it), and make subsidiaries `excluded` or load their own statements from the filing instance. This changes the effort (section c) and needs a Normalizer authority rule, not a new gate on context.
5. **W3 (canonical facts only from periodic forms) demotes about 229 rows on a shared table.** It is safe only as the repair pattern used on 2026-10-18: save fact ids to `doc/data-moat/team/backups/`, run the pipeline's own reset-and-repromote through the recompute workflow with `ciks`, never hand-edited SQL. 229 rows are small, but the same code path serves the nightly, so it must not ship together with a W5 label repair in one release (two causes, one rollback).
6. **The certify run is about 1.5 h on 986 companies.** It reads `core.fact` heavily, so it is a heavy job: one window, sharded by company ids in at most 4 sequential chunks, its own `timeout-minutes`, in the `heavy-db-jobs` group. There is no certify workflow in `.github/workflows/` today (CODE-CHECKED); it has to be added before it runs unattended. Running it from a laptop competes with agents for the same 15 pooler connections.
7. **FSDS/FSN bulk files on an 8 GB Mac disk.** A quarter's `num.txt` is large (ASSUMED: many hundreds of MB unzipped). Do not download and unzip on the Mac. Run the structure pilot on a GitHub runner with streamed Range reads of `pre.txt`/`cal.tsv`/`sub.txt` only, delete after each file, and write only the measurement table (not the files) into the repo. K3 (5% join miss, SEC refusing Range reads) is the right stop rule; add: stop if the SEC User-Agent rate limit (10 requests per second) is approached.
8. **I12/I13 need a migration, not just code.** `analytics.certification_finding` has `check (invariant in ('I1'..'I11'))` (CODE-CHECKED, 0097). Adding I12 and I13 requires a new migration (claim a number in doc 53; 0098 is the next free one if nothing else has taken it) that replaces the constraint. Better: change 0097 before it is applied to allow `I\d+` so it is never rewritten. This is the cheapest moment: 0097 is unapplied.
9. **Gate A "days 0-3" bundles too much.** Apply 0096/0097, matrix rebuild, snapshot, certify dry-run and Verifier precision measurement are one heavy window each, plus review time. Three days only holds if the four workflows are green first and nothing else is queued. Re-baseline Gate A to start at "all four workflows green" rather than at a calendar date.
10. **"Held guards live by day 10" collides with working-tree state.** About 30 modified pipeline files are uncommitted in the shared working tree (certification/*, `derived.py`, `concept_fallback.py`, `tag_investigator.py` and their tests), and an applied-but-untracked migration breaks CI's contiguity check. The Release Manager must commit by named paths from a temporary worktree, and each guard must carry tests before it is pushed.

## (b) Execution order for migrations, coverage rebuild, certify and Tier 0

Window rule: heavy work starts only when `gh run list` shows nothing in progress, `pg_stat_activity` shows under 10 connections, and `ListAgents` shows no peer on a heavy job. Quiet window proposal (UTC): see section (f); the schedule is refresh 12:23, sanity 15:17 daily, Frames 06:05 and health-check 06:30 on Mondays (CODE-CHECKED crons). GitHub starts scheduled runs late (observed starts 17:24Z, 18:45Z, 19:20Z), so the real busy span is about 12:30-22:00Z. Founder gives the go to this session directly.

| Step | What | Needs | Rollback | Workflow / how | Window |
|---|---|---|---|---|---|
| 0 | Prove the 4 workflows green (refresh, Frames, sanity, health-check), one at a time | nothing to approve | n/a | `workflow_dispatch` each, sequentially | now, in progress |
| 1 | Amend 0097 so `invariant` accepts `I\d+` (before applying) | Release Manager commit, CI green | revert commit | normal push | any time |
| 2 | Apply 0096 (adds one nullable column; instant) with `lock_timeout = 5s`, then 0097 (two new tables) | founder "go" in this session | `alter table ... drop column has_value_any_period`; `drop table analytics.company_certification, analytics.certification_finding` (both new, no dependents) | psql through the pipeline migrator, not MCP | quiet window, 5 min |
| 3 | Coverage rebuild + snapshot | step 2 done, no queue | previous complete table stays (rebuild is one transaction); `has_value_any_period` can be ignored | `Full-population recompute` with `snapshot` true, no stages, or `scrooner-map build-coverage-matrix` + `snapshot-coverage` | quiet window, about 30-45 min under load (OBSERVED 15-27 min plus snapshot) |
| 4 | Certify dry-run on the top 986 (default writes nothing) | steps 2-3, a certify workflow in the `heavy-db-jobs` group | none needed for dry-run; the live (write) run is a separate decision, undone by `delete from analytics.certification_finding where found_at > :t` | new `pipeline-certify.yml`, 4 sequential shards, `timeout-minutes: 150` | quiet window, about 1.5 h |
| 5 | Verifier measures precision per invariant (30 flagged cells each) | step 4 output | n/a (read-only) | agent | after 4 |
| 6 | Tier 0 release train R1 (display and metric-time guards: W6/W7, W1/W2, W9, W10) | Verifier zero-wrong sample, Release Manager | revert commit, rerun metric stages for `ciks` touched | recompute `metric_stages` for the affected `ciks`, then snapshot | one window |
| 7 | Release train R2 (stored data: W3, W5, W8, identity id 1840, registrant rule) | backup of affected fact ids saved before the run, Verifier on Entergy/WTRG/id 1840 | restore ids from backup; revert commit | recompute with `ciks` (normalize and resolve stages) | one window, own day |
| 8 | Release train R3 (held guards: total-debt, no-derived Q4 EPS/DPS, revenue-total) | founder acceptance of plan, Verifier sample of about 30 filings including hidden-correct count | revert commit; rerun stages for the affected `ciks` | recompute | one window, own day |
| 9 | Certify re-run on the cohort after each train | previous train live | n/a | step 4 workflow | after each train |

Rules: never two trains in one window; never a train on a Monday before 08:00Z; every train's backup (affected ids and a `before` query of the numbers shown) is saved under `doc/data-moat/team/backups/` before the run; every first live run is on the smallest named `ciks` list that includes the Verifier's sampled companies, then widened.

## (c) Engineering work orders: feasibility, effort, what I would change

| WO | Item | Effort (days) | Verdict |
|---|---|---|---|
| WO-1 | 1 apply 0096/0097 | 0.5 + windows | feasible; fold in the I12/I13 constraint change |
| | 2 identity master check | 2 | feasible; compare CIK/name/ticker against the stored SEC submissions payloads (already in `raw.sec_submissions`), no new fetch |
| | 3 registrant-context gate | 5-7 | as written not feasible (premise, section a.4); redo as "shared-accession primary-filer rule" and make Entergy a hand-decided case first |
| | 4 authority gate W3 | 2 | feasible; ship with the 229-row backup |
| | 5 `cell_state` job | 8-10 | cut to latest-period + defect register for the cohort first (view over existing tables, 3 days), table only after a size check |
| | 6 `company_group` / `metric_template` | 5-7 | feasible; add only after group audit passes; a plain table with a loader, not a framework |
| | 7 cover-date anchor W10 | 1.5 | feasible; move into R1 |
| | 8 ingestion detectors / feed fallback | 3 detector; 5 fallback reader | detector yes; fallback reader after the 50-filing match gate, sequence after Gate C |
| | 9 certify I12/I13, currency, scale | 3-4 | feasible; behind precision gate (K2) |
| | 10 structure pilot | 3 | feasible as measurement on a runner; not on the Mac |
| | **WO-1 total** | **about 31-40** | not deliverable by Gate C (day 15) by one engineer; see sequencing |
| WO-9 | Release Manager | 0.5 per release, 3 trains plus fixes = 2-3 | not the bottleneck; the heavy-window lane is |
| WO-10 | Frontend/backend | 16-20 as written | cut to about 10-12 before Gate D |

Sequencing I would apply:
- **Gate B (day 10)** = three trains R1/R2/R3 above, not twelve releases. Everything display-only (W6, W7, W1, W2, W9, W10) goes in R1 because it changes no stored fact and rolls back by revert plus a metric rerun. Stored-fact work (W3, W5, W8, identity, registrant) is R2. The three held guards are R3 because they already exist and only need a Verifier sample.
- **Gate C (day 15)** is the schedule risk. Do `cell_state` v0 as a read-only view for the top 986 (no migration, 3 days) so the reasonless-blank count falls to zero before the table is designed. The `company_group`/template table and design review follow; do not claim template coverage numbers in doc 53 before the design review.
- **WO-10 cuts and order:** (1) template-only rendering for corporate and bank first (6 days), insurer/REIT after; (2) "why this number" panel from existing provenance (4 days); (3) certified badge and "certified only" filter only after T1 certification exists (2 days); (4) the public data-quality scorecard moves to Gate E (3 days). Each visual step needs a real headless-Chrome screenshot (standing rule). `force-dynamic` on flat pages that fetch from `apps/backend`; keep the app pool `max` below the shared pooler budget.
- Cut or defer: the structure pilot until Gate C is met; the fallback reader for feed lag (use the detector and a disclosed "latest 10-Q not in feed" state first); I12/I13 until I1-I11 precision is measured.

## (d) CI and hook requirements for the held guards

1. **Every guard ships with**: a unit test, a real-SQL test in a scratch schema (the `isolated_database_url` fixture; CI's `repository-integrity` job has a `postgres:16` service and `SCROONER_TEST_DATABASE_URL`), and a mutation check (revert the guard, the test must fail). Without the real-SQL test the 2026-10-18 sign-flip problem repeats.
2. **Pre-push hook** (`.githooks/pre-push`, on `origin/main`): runs `ruff format --check` and `mypy` on `pipeline/src` and `apps/backend` in a temporary worktree. Every held-guard file in the working tree (certification/*, `derived.py`, `concept_fallback.py`, `tag_investigator.py`) must pass both before push; tests under `pipeline/tests` are not format-checked, so do not run `ruff format` on the tests directory. Do not `--no-verify`.
3. **Make format and typing blocking only after they have stayed green for 7 days.** Today they sit in the "Advisory" job, which passes (OBSERVED, run 39720553769). Promoting to a required check on the first green day would let one transient dependency audit failure block releases. Keep `pip-audit`/`npm audit` advisory; make `ruff format --check` and `mypy` required later.
4. **Migrations**: the `check_migrations.py` rules apply (contiguous numbers, file ends with a semicolon, no trailing comment). Claim the number in doc 53 first. Never apply a migration that is not committed.
5. **Test-time impact (ASSUMED, not measured)**: each real-SQL test file adds on the order of tens of seconds on the CI Postgres service; ten guards add a few minutes to the Python job. CI no longer cancels on main (`cancel-in-progress` false), so queued runs stack: measure the Python job duration on the first guard release and split the real-SQL tests into their own job if it passes 15 minutes.
6. **New workflows** (certify, anything calling the DB) join `concurrency: heavy-db-jobs` with `cancel-in-progress: false`, set `timeout-minutes` explicitly and per-step caps, and are tested the way CI invokes them (after a `cd`, relative paths). `mind.yml` is untracked; confirm it makes no DB connection before it is committed.
7. **Rollback artifact**: each release commit message states the revert command and the `ciks` list to rerun.

## (e) Sign-off

**SIGNED WITH CONDITIONS** (engineering head, scrooner-4d, 2026-10-22). The architecture, the release path and the order (trust first, classify second, capture third, definitions in parallel) are sound and executable. Conditions:

1. All four workflows (refresh, Frames, sanity, health-check) are proven green before Gate A starts; Gate A's clock starts then.
2. Gate B is three release trains (R1/R2/R3), each in its own window, each with a saved backup and a named revert; not twelve separate releases.
3. `cell_state` is built as a latest-period view plus defect register first; a full-history table only after a size check against the 14 GB of remaining headroom.
4. WO-1 item 3 is rewritten as a shared-accession primary-filer rule (the data cannot supply `LegalEntityAxis`), and the Verifier confirms the mechanism on Entergy before any code.
5. 0097 is amended to accept `I\d+` before it is applied; a certify workflow in `heavy-db-jobs` exists before the 1.5-hour run.
6. Heavy-job windows follow section (b); at most 4 agent sessions hold DB connections; FSDS/FSN work runs on a runner, never on the Mac disk.
7. WO-1 and WO-10 dates are re-baselined by the estimates above (WO-1 about 31-40 engineer-days, WO-10 cut to about 10-12 before Gate D). If one engineer carries WO-1, Gate C (day 15) is not achievable for the group and template tables; `cell_state` v0 is.
8. Founder's "go" for migrations 0096/0097 and plan acceptance arrive in this session; until then nothing is applied or released.

NOT SIGNED items: none. Open for Ritwik to fold into doc 49: the three-train structure and the window calendar.

## (f) Slot calendar for the single heavy lane (added 2026-10-22 at Dhairya's request)

**Capacity.** Scheduled load (nominal UTC): refresh 12:23 daily (reprocess budget 117 min, job cap 180 min), sanity 15:17 daily, Frames 06:05 Monday, health-check 06:30 Monday (CODE-CHECKED). Real starts drift late and queue behind each other, so I treat 12:30-22:00Z as busy. Free span: about 22:00-12:00Z, 14 hours. Durations not measured by me: refresh and sanity (ASSUMED 2-3 h and 1-2 h; the first re-run is still going after 1 h 20 min); certify about 1.5 h (Verifier-measured); coverage rebuild plus snapshot 30-45 min (OBSERVED 15-27 min plus snapshot).
**Windows per day:** 2 heavy slots on a normal day (one 22:00-01:30Z, one 02:30-06:00Z, leaving 06:00-12:00 as slack), 1 on a Monday (Frames and health-check take 06:05-07:30). Rule: at most one stored-data train per day, never a train and a certify in the same slot.
**Light agents beside a heavy slot:** read-only Verifier work from SEC filings (no DB), document work, code and test work, single-connection index-backed reads of at most 100 companies per query. Not allowed beside a heavy slot: any chunked `core.fact` scan over more than 100 companies, anything using the MCP `execute_sql` in a loop, a second full-population job.

| Day (clock starts when all 4 workflows are green and the founder's go is in this session) | Heavy slot | Est. duration | Notes / light work beside it |
|---|---|---|---|
| D0 night | S1: apply 0096 + 0097 (after the `I\d+` amendment), then S2: coverage rebuild + snapshot | 5 min + 45 min | none; Verifier starts group-audit samples from filings |
| D1 night | S3: certify dry-run on the 986 (4 sequential shards) | 1.5 h | Verifier precision work reads the output next day |
| D2 | no heavy slot | | Verifier precision per invariant; cell_state view built and tested on 100-company chunks (DDL is a few seconds); R1 code and tests finished, Release Manager commits |
| D3 night | R1 train: display/metric guards (W6/W7, W1/W2, W9, W10) metric recompute for affected `ciks` + snapshot | 1.5-2.5 h | backup `before` numbers first |
| D4 night | certify re-run + cell_state view check on the 986 | 1.5 h | |
| D5-D6 | spare slots (R1 fixes, Verifier findings) | | R2 code, tests, backup list of affected fact ids |
| D7 night | R2 train: stored data (W3, W5, W8, identity id 1840, registrant rule) normalize + resolve + metrics for affected `ciks` | 2-3 h | one train only that day |
| D8 night | certify re-run | 1.5 h | |
| D9 | spare | | R3 sample by Verifier (30 filings, including hidden-correct count) |
| D10 night | R3 train: held guards (total-debt, Q4 EPS/DPS, revenue-total) normalize/resolve/metrics for affected `ciks` | 2-3 h | |
| D11 night | certify re-run + snapshot | 2 h | Gate B is therefore realistically day 11, not day 10, if each train passes its sample the first time |
| D12-D14 | 2-3 spare slots | | decision on the cell_state table after a size check; Tier 1 group gating; T1 certification starts |

Spare slots are the schedule's only buffer: one failed Verifier sample costs a train a full day plus a re-run. Windows needed in the first 15 days: 8 heavy slots used, 6-7 spare. If the refresh or sanity overruns into a window, the slot slips by a day, not by hours; do not squeeze.

**Pre-flight for every slot (copy into doc 53's ledger):** `gh run list --limit 5` shows nothing in progress or pending; `select count(*) from pg_stat_activity` under 10; `ListAgents` shows no peer on a heavy job; `show default_transaction_read_only` is off; the slot is written in doc 53 with owner and `ciks` list.

**SEC fetch rule (Dhairya's change to three processes, combined 5 req/s):** compatible with the pipeline. `sec_max_requests_per_second` is 8.0 aggregate and the shared limiter is an `flock` file used by every process on one machine (CODE-CHECKED `common/rate_limiter.py`), so three processes at a combined 5 req/s stay under it only if they all go through that limiter; a raw `curl` loop or a process using its own client does not. Different hosts do not share the lock: a GitHub runner and the Mac each have their own IP and budget, so keep each host at or under its own cap and do not run an agent bulk fetch on the Mac while the Mac also runs a pipeline fetch (add their rates). The runner has no different need; Range reads of the FSDS/FSN files count against the same SEC budget.
