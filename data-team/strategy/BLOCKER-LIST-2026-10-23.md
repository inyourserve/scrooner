# Blocker list, 2026-10-23 (Ritwik, compiled from the files; nobody was woken)

Written for: Dhairya (execution) and the founder (what is still blocking). Method: for every signed condition of every head and role review (and my own product block) I checked whether a DOCUMENT or COMMIT shows it closed. Sources read: the ten reviews and the Gate A check in `data-team/strategy/team/`, docs 44-50, the freeze register, `doc/data-moat/team/PLAN.md`, `origin/main` after `git fetch` (head c2253c2), `gh run list`, `git branch -r`, and four read-only database checks at 2026-10-23 20:4x IST (one connection, 15 s timeout). I did not run any workflow, apply anything or message any agent. The mind was searched first: queries 'blocker', 'freeze register' returned no entry (logged as knowledge gaps); 'release train rollback flag' returned only the Q4-EPS lesson. A condition is CLOSED only where a file or commit shows it; "plan text closed" means the document records the decision but the build or evidence does not exist yet, and counts as OPEN here.

## 0. Totals

86 conditions: **20 CLOSED**, **28 plan text closed but build/evidence OPEN**, **28 OPEN**, 8 STANDING rules, 2 not yet due. Truly closed (document or commit): 20 of 86 (23%).

## 1. The blockers that stop the clock G (Gate A cannot start). Corrected 2026-10-23 per Dhairya: G3 done, G4 and G5 restated, push permission restated

| # | Blocker | State 2026-10-23 | Evidence | Who can clear it |
|---|---|---|---|---|
| G1 | Four scheduled workflows green, one at a time | RED | refresh 39974455449 in progress since 15:00Z; sanity failed 10-18..10-22 (last 39838371297); Frames failed 10-19 (39327427688); health-check failed 10-19 (39263442979); none of the three re-run | scrooner-4d dispatches; the sanity failure cause is not recorded in any file I read |
| G2 | Founder's go for migrations 0096/0097 in his own words in scrooner-4d's session | NOT GIVEN (kept per Dhairya) | live DB: certification_finding table absent, has_value_any_period absent; PLAN.md last section | founder |
| G3 | VACUUM of core.fact (blocks Gate A per Dhairya) | DONE (corrected 2026-10-23 per Dhairya/scrooner-4d) | live DB 2026-10-23: `pg_stat_user_tables` core.fact last_vacuum 2026-10-23 14:59:32Z (confirmed by me). scrooner-4d reports 4m48s and 1.52M dead rows removed (not verified by me); current n_dead_tup estimate is 4,778,711, which is not the 14.2M earlier figure, and may include rows created by the refresh run that started 15:00Z | cleared |
| G4 | Migration 0100 (reason and evidence stores) committed to main before G, applied with 0096/0097 | WRITTEN ON BRANCH, NOT MERGED, NOT APPLIED (corrected per Dhairya; verified) | `git ls-tree origin/work/data-engineer/lane1-p1-primary-filer-v2`: pipeline/db/migrations/0100_cell_evidence_reason_registrant_audit.sql (reason-store commits ef0c513, 3b801ac; also on origin/work/data-engineer/lane1-reason-store 2edaed0); 0098/0099 written schema-only on origin/work/period-engineer/migrations-0098-0099 cb2c688. Doc 53 on main still says 'claimed, not written' until the Release Manager merges | Release Manager merge (push permission staged) |
| G5 | Quiet heavy-slot window; pooler/app backends within the team cap of 14 for the apply and for E0 | NOT SHOWN AS MET (rewritten per Dhairya/scrooner-4d) | the 14-backend cap counts pooler/app backends, not all client backends. `pg_stat_activity` grouped by application_name, 2026-10-23 20:5x IST: Supavisor client backend 5 (+1 Supavisor auth_query), PostgREST 1, postgres_exporter 1, my own psql 1 ('(none)' client backend), plus background workers (Supavisor parallel workers 2, pg_cron, pg_net, autovacuum, walwriter, checkpointer...). So pooler/app backends are about 6 here, under 14; the earlier '21' counted platform backends. Whether a heavy slot is free is scrooner-4d's check (`gh run list`: refresh still in progress). DB 47 GB of 60 | scrooner-4d |
| G6 | Founder approval of the freeze register is not recorded (delegation recorded; Dhairya approved, reversible); sector-row catalog and AMD 9 excluded | PARTIAL (kept per Dhairya) | PLAN.md last section | founder / me for the catalog (PR1) |

Cleared already: VACUUM of core.fact (last_vacuum 2026-10-23 14:59:32Z), 0097 amendment (ab63ca7), certify workflow (2cfc569), migration claims 0098-0106 in doc 53 (4110566), held branches pushed, shared-tree backup branch, per-agent worktree rule, Gate A identity/registrant mechanism confirmed, baseline scoreboard check 59/59.

## 2. Blockers that do not stop G but stop a later gate

| Item | Stops | State | Default if undecided |
|---|---|---|---|
| Named accounting reviewer (item 3) | D(F), Tier 3, every REPLACED cell, the 21 AC cards + AC-22..26 | not named | cells stay hidden with a reason; D(NF) proceeds |
| Synonym-class release rule (item 11) | Tier 2 vocabulary fills | not approved | fills wait for the accountant |
| Restatement display basis (item 12) | Q4 backfill (about G+14 at the earliest, in practice behind versioning) | not approved | block mixed-basis Q4 |
| id 1840 reverse-acquisition history basis (item 16) | the Q3 2026 10-Q of CIK 906107 (due about Nov 9) | not approved | hold: do not ingest that history under CIK 906107 |
| Shared-tree reset (Part B) | clean working tree | not approved | stay on worktrees |
| Release Manager push permission | any later push reaching origin | PARTIALLY EXERCISED (corrected per Dhairya): pushes to origin/main succeeded through c2253c2 (e271b9c, 7e146f5, 2163ec2, 4aa3503, e30716c, c2253c2); the classifier then DENIED later ones, even after a relayed go-ahead. Staged, not pushed to main: the docs batch, work/sector-analyst/groups, work/period-engineer/migrations-0098-0099, the lane -v2 branches (some -v2 branches are on origin, e.g. lane1-p1-primary-filer-v2) | founder permission needed for the staged pushes |
| Sanity workflow failing 5 days in a row | G1 | cause unknown in the files | fix before the dispatch |

## 3. Condition-by-condition (CLOSED only where a document or commit shows it)

### Engineering Head (scrooner-4d)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| E1 | Four scheduled workflows (refresh, Frames, sanity, health-check) proven green, one at a time, before Gate A | OPEN | gh run list 2026-10-23 20:4x IST: refresh 39974455449 in_progress (started 15:00Z); sanity last 39838371297 FAILURE 10-22 (fails 10-18..10-22); Frames last 39327427688 FAILURE 10-19; health-check last 39263442979 FAILURE 10-19 | G (clock) |
| E2 | Gate B is release trains (not 12 releases) | PLAN TEXT closed, build OPEN | doc 49 section 4 (R1-R4, Gate B about G+27) + 7.1; no train has run | Gate B |
| E3 | cell_state as latest-period view + defect register first; full history only after size check | PLAN TEXT closed, build OPEN | doc 49 2.1 and 7.12 item 8; branch origin/work/data-engineer/lane2-cell-state-0102 exists, not on main; migration 0102 claimed in doc 53 (4110566), not written | Gate C |
| E4 | Registrant rule = shared-accession primary-filer rule; Verifier confirms Entergy before code | PLAN TEXT closed, build OPEN | Verifier confirmation CLOSED: team/GATE-A-IDENTITY-REGISTRANT-CHECKS.md (origin/main); code branches origin/work/data-engineer/lane1-p1-primary-filer and -v2, not on main | Gate B (R2b) |
| E5 | 0097 amended to ^I[0-9]+$; certify workflow in heavy-db-jobs before the 1.5 h run | CLOSED | 0097 amended: commit ab63ca7 (origin/main; I[0-9]+ check + rule_id, rule_version, suite_version, certify_run_id, suite_run_at; NOT applied); workflow: commit 2cfc569 (.github/workflows/pipeline-certify.yml: group heavy-db-jobs, timeout 150, dry-run default). Residual: one manual dry-run log not on file | - |
| E6 | Heavy-job windows per section (b); at most 4 agent DB sessions; bulk SEC files on a runner, not the Mac | STANDING rule in force | rule in force: PLAN.md process rules; SEC fetch rule (3 processes, 5 req/s) recorded by Dhairya; live check 2026-10-23: pg_stat_activity 21 connections | all gates |
| E7 | WO-1 and WO-10 dates re-baselined (WO-1 about 31-40 -> about 140 engineer-days; WO-10 about 10-12) | CLOSED | doc 49 section 4 three-lane re-derivation + 7.12; doc 47 v2 | - |
| E8 | Founder go for 0096/0097 and plan acceptance given in scrooner-4d's own session first | OPEN | live DB 2026-10-23: analytics.certification_finding absent and has_value_any_period column absent (0096/0097 NOT applied); PLAN.md last section: go "not approved ... in the founder's own words in scrooner-4d's session" | G (clock), Gate A |

### Data Head (Data Chief)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| D1 | All 28 themes have an owner and acceptance test by Gate A exit | PLAN TEXT closed, build OPEN | team/WO-ADDENDA-2026-10-22.md (origin/main e271b9c) section 3; doc 47 v2 section B; register A19 "drafted, pending review"; no review recorded | Gate A |
| D2 | W12 corrected: revenue-total guard is a build item | PLAN TEXT closed, build OPEN | correction CLOSED in docs 46 (W12), 47 v2 A.1, 49 7.2; guard code not built (no match for the guard markers in pipeline/ or apps/backend/ at 2026-10-22) | Gate B |
| D3 | Freeze register approved with the state-model decision | PLAN TEXT closed, build OPEN | approved UNDER DELEGATION by Dhairya 2026-10-23 (PLAN.md last section), excluding the sector-row catalog and AMD 9; founder approval not recorded (register approver = founder) | Gate A (A12) |
| D4 | Synonym-class release rule adopted by founder; Gate D split non-financial/financial | PLAN TEXT closed, build OPEN | Gate D split CLOSED in doc 49 section 4 and PLAN.md item 15; item 11 NOT approved (PLAN.md last section) | Tier 2 vocabulary fills |
| D5 | Slot calendar (heavy DB, SEC fetch, Release Manager queue) exists before any gate date is quoted; dates re-baselined from it | OPEN | register A16 "draft exists, undated (G unset)"; doc 49 section 4 dates marked PROVISIONAL; no dated slot rows in doc 53 (checked ledger rows 0098-0106 only) | all dated gates |
| D6 | Failure test 1 judges correct value-filled cells, hidden-by-guard separate | CLOSED | doc 49 section 5 and 7.2; register section 4 AMD 7 (K1@1 never a target; K1c; K1b) | - |
| D7 | W10 has one fix (balance-sheet-date anchor) | PLAN TEXT closed, build OPEN | ruling CLOSED: doc 49 7.3 item 5; design OPEN: Standardization Lead card DC-SHARE-COUNT-DATE-2026-10-22.md is PROPOSAL ONLY (PLAN.md); branches lane2-w10-alone/-anchor on origin, not on main | Gate B (R2) |
| D8 | Certify precision AND recall per invariant (rule) on the 986 run before any invariant gates | OPEN | register A10/A11 pending; no data-team/strategy/gate-a/rule_precision_recall.csv on origin/main; commit 4aa3503 reports recall 73% -> 96% on training gold cells, "not yet validated on held-out shards" (not the 986 run) | Gate A |
| D9 | Verifier independence: no family verified by its proposer/tuner | STANDING rule in force | doc 47 v2 D and doc 49 section 5; assignment table = WO-ADDENDA section 4 (drafted); no violation recorded | each release |

### Period Engineer (WO-2)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| PE1 | Split basis added to WO-2 as item 6; Gate B date for the split class set | PLAN TEXT closed, build OPEN | doc 49 7.3 and section 4 (train R4); branch origin/work/period-engineer/migrations-0098-0099 cb2c688 = schema only; migration 0099 claimed, not applied | Gate B (R4) |
| PE2 | No-derived Q4 EPS/DPS ships only as RU-1 (all companions together) | PLAN TEXT closed, build OPEN | doc 49 section 4 R3; code on origin/held/ru1-per-share 91c6171, not on main; round-1 branches; flag/dry-run/Verifier sample not yet run | Gate B (R3) |
| PE3 | Standardization Lead decides dividend yield / TTM EPS / P/E basis by day 3; approves additive A/B list before the Mapper gate | OPEN | register A18 "NOT DONE"; team/DC-*.md cards (SHARE-COUNT-DATE, COMMON-EQUITY-BVPS, INTEREST-EXPENSE) are PROPOSAL ONLY per PLAN.md; PLAN.md: asks AC-13/AC-14 + NA-2 to the Standardization Lead outstanding | Gate B (R3) |
| PE4 | Founder/accountant decides restatement display basis before the Q4 backfill (day 14) | OPEN | PLAN.md last section: items 12 and 16 NOT approved; default = block mixed-basis Q4 | Q4 backfill (not Gate B) |
| PE5 | W10 one owner; XOM moves from calendar to successor-CIK item | PLAN TEXT closed, build OPEN | ruling CLOSED (doc 49 7.3; Dhairya); successor-CIK link build OPEN (XOM id 5351, predecessor 0000034088 not in core.company per freeze register section 6) | Gate B/C |
| PE6 | Additive allowlist enforced at the Mapper, not the Normalizer | PLAN TEXT closed, build OPEN | doc 49 7.3 item 6; implementation not on main | Gate B (R3) |
| PE7 | "Never delete" = archive-then-replace for canonical_fact | PLAN TEXT closed, build OPEN | Dhairya ruling (doc 49 7.3); migration 0098 claimed (4110566), file on branch cb2c688; not applied (any apply of 0098 NOT approved, PLAN.md) | Gate B (R3) |
| PE8 | Lane F agrees to the period_completeness edit; certify I9 stays independent | OPEN | no document found showing lane F's agreement (PLAN.md asks scrooner-2b; no reply recorded in the files read) | Gate B (R3) |

### Standardization Lead (WO-5)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| SL1 | Named accountant before any AC card changes a displayed value (until then hidden with a reason) | OPEN | PLAN.md: item 3 NOT approved; no accountant named in any file; Dhairya preparing options | D(F), Tier 3, all REPLACED cells |
| SL2 | Held total-debt guards released only with persisted blank reasons, fallback-overcount cases checked/blanked, floor 2% hide-only | PLAN TEXT closed, build OPEN | conditions recorded in doc 49 section 4 R3 and 7.4; code origin/held/total-debt-guards 1a1cf25; reason store on origin/work/data-engineer/lane1-reason-store (2edaed0, fb50eb4), migration 0100 written on branch, not merged/applied | Gate B (R3) |
| SL3 | Revenue disagreement guard built; docs 46/47 corrected | PLAN TEXT closed, build OPEN | docs corrected (46, 47, 49 7.2); guard not built | Gate B |
| SL4 | Per-share non-derivation ships with price_metrics anchor fix, new period_gap cause, reviewed retirement dry-run | PLAN TEXT closed, build OPEN | same as PE2; retirement dry-run script ru1_retire_dryrun.py on the held branch; not run | Gate B (R3) |
| SL5 | Real definition versioning before any history backfill | PLAN TEXT closed, build OPEN | design: team/DEFINITION-VERSIONING-SPEC.md (shared tree, UNTRACKED); register A13 "NOT DONE" until accepted by both heads; migration 0105 claimed, not written | before Q4/history backfill |
| SL6 | NA-7 and NA-9 count as MINOR only if founder policy accepts filing-proven source selection | OPEN | tied to item 11 (NOT approved) | Tier 2 |

### Verifier (WO-6)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| V1 | "Not disclosed" = audited deterministic detector + census (not open every not-presented cell) | PLAN TEXT closed, build OPEN | plan text CLOSED (doc 49 7.5, C1); detector not built/audited (G+18..G+35 window) | D(NF) entry |
| V2 | Sample tiers K/P/H/V/V+/census adopted | PLAN TEXT closed, build OPEN | doc 49 section 5 and 7.5; Triage frames: scoreboard/frames/verifier_queue_v2_1_2026-10-20.csv (origin/main 5a87aa3); no family sample file yet | each release |
| V3 | Every check card names its independent evidence | CLOSED | team/VERIFIER-CHECK-CARDS.md (shared tree, UNTRACKED) + GATE-A-IDENTITY-REGISTRANT-CHECKS.md section 4 (origin/main); practice is per run | - |
| V4 | Second-reader subsample (10%) before a detector audit counts toward a denominator change | OPEN | second reader exists (3 readers agree on 309 rows over 5 filings, GATE-A file); the 10% subsample is part of the unrun audit | D(NF) entry |
| V5 | Capacity: two Verifier sessions through Gate C (or Gate B slips) | STANDING rule in force | Dhairya ruling (doc 49 7.5); usage limit hit twice 2026-10-21/22; whether two sessions run is not shown by any file | Gate B/C |
| V6 | Gate A precision per RULE; re-measure the 36 precision on the top-986 run | OPEN | register A11; no rule_precision_recall.csv on origin/main | Gate A |
| V7 | Headline certification: FSDS reconciliation by code first; [VERIFY] FSDS lag | OPEN | DE reconciliation (7 days, lane 3) not built; FSDS-lag check not shown in any file | Gate D |
| V8 | Public error rate only from a separate rotating random audit (300 cells a month) | NOT YET DUE | plan text CLOSED (doc 49 7.5, doc 48 amendments); audit not due before the first public certified cohort | public claim only |

### Release Manager (WO-9)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| RM1 | WO-9 text corrected; RU-1 and total-debt guards held on non-main branches | CLOSED | doc 47 v2 A.1, doc 49 7.8; origin/held/ru1-per-share (91c6171) and origin/held/total-debt-guards (1a1cf25) exist on origin, not on main | - |
| RM2 | Flag (default OFF), per-family dry-run mode and before-image/restore script exist before the first value-changing train | OPEN | branches origin/work/data-engineer/lane1-rule-flags(-v2) and lane3 stacks exist; nothing on main; no restore script on main; reviewed by no one in the files read | Gate B |
| RM3 | Part A worktrees adopted; shared tree salvaged incl. the 2 local-only commits | CLOSED | origin/backup/shared-main-746b80f exists (git branch -r 2026-10-23); PLAN.md process rule; work/* branches show per-agent worktrees. (Part B reset still needs the founder go: separate item.) | - |
| RM4 | Migration claims written in doc 53 on origin before files are committed | CLOSED | commit 4110566 (doc 53: 0098-0106 claimed, next free 0107). Applies to each later number. | - |
| RM5 | Release Manager never dispatches workflows; slot row in doc 53 first | STANDING rule in force | rule in force; slot rows for trains not in doc 53 yet (see D5) | each train |
| RM6 | Gate B date reconciled with the post-R4 certify; calendar acknowledges 4 trains | CLOSED | doc 49 section 4 (four trains R1-R4; three-lane Gate B about G+27) + 7.8 | - |

### Sector Analyst (WO-4)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| SA1 | Add about 60 versioned sector rows; D1 defined over catalog_version before the register is approved | PLAN TEXT closed, build OPEN | plan text CLOSED (doc 49 2.1, register AMD 2); catalog NOT final: doc 50 review (PLAN.md line 244) found 4 groups with no defining row (non-bank lender, crypto, exchange, insurance broker) and at least 7 wrong tag leads; correction owed by Ritwik (PR1) | Gate A (register) / Gate C |
| SA2 | Gate C = groups frozen + template v1 lists + detector spec + W9 overlay; detectors audited G+18..G+35 as D(NF) entry | CLOSED | doc 49 section 4 Gates C and D(NF), 7.9 | - |
| SA3 | Group audit drawn/adjudicated by a Verifier lane; 3.25 Verifier-days; Reader 2 on 10% | PLAN TEXT closed, build OPEN | plan CLOSED (doc 49 5, 7.9); frame drawn: scoreboard/frames/group_audit_DRAFT_groups_seed20261022.csv (origin/main); audit not run | Gate C |
| SA4 | Retire "zero wrong in 30 per group" for groups over 60; use the supported wording | CLOSED | doc 49 section 5 group audit standard | - |
| SA5 | Overlays and excluded-with-reasons first-class in the enum; keyed by company_id, effective-dated, history_status | CLOSED | register section 1 [AMD 3] + 2.1 (doc 49) | - |
| SA6 | Cohort re-drawn first; freeze file v2.1 cut after the P1 reload | OPEN | P1 not on main (branches only); register section 6 cohort v1.1 rule; no cohort v1.1 file on origin | Gate A/C |
| SA7 | Release Manager commits the audit manifest/scripts; no SEC bulk file on the Mac | CLOSED | data-team/strategy/data/s2_group_audit/, data/r4_sector/, tools/ on origin/main (commit e271b9c); Mac free disk checked 2026-10-22: 6.4 GB | - |
| SA8 | Standardization Lead names/formulas by G+3; Tag Expert answers by G+8; accountant gates only REP cells | OPEN | Tag Expert sector run COMPLETE (PLAN.md 2026-10-22; cards untracked); Standardization Lead row formulas not seen in any file; G unset | Gate C |
| SA9 | SEC slot: S3 and S8 as single-process blocks inside the 3-process / 5 req/s rule | STANDING rule in force | SEC fetch rule recorded (PLAN.md) | - |

### Data Triage (WO-7)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| T1 | RT-1 reconciliation passes before any new number; RT-2 unexplained = 0 before a headline | PLAN TEXT closed, build OPEN | RT-1 CLOSED: baseline 59/59 (commit 557f577; doc 49 note); RT-2 unexplained = 0 not shown | founder headline |
| T2 | K1 never quoted without K1c; "latest-period" wording corrected | CLOSED | docs 44/48/49 corrections (commit 7e146f5); register section 4 AMD 7 (commit 2163ec2). K1@1/K1c@1 ratification at Gate A: open | - |
| T3 | 0097 amendment adds suite_version, certify_run_id, rule_id | CLOSED | commit ab63ca7 (origin/main), not applied (see E8) | - |
| T4 | A20 regression list built (listed columns) and reviewed | OPEN | no gate_b_regression_list.csv on origin/main or in the shared tree (ls 2026-10-23) | Gate B |
| T5 | Verifier evidence carries observed/sample_seed/frame_size | OPEN | no cell_evidence.jsonl in any tree; frames carry seeds (seed20261022) but no evidence rows | Gate A |
| T6 | Reason-to-class map v1 reviewed once by the Chief; unmapped reasons = 0 | PLAN TEXT closed, build OPEN | map v2.1 on origin/main (5a87aa3, c2253c2; Chief second review a-f applied); "unmapped = 0" statement not read by me | scoreboard |
| T7 | Product head names the K14b analytics source or removes it | CLOSED | doc 49 7.10 item 5 and doc 47 (WO-10 item added 2026-10-23) | - |
| T8 | DB runs follow the gate (14 connections, one connection, 60 s, chunks); first live extract E0 scheduled | OPEN | E0 not run (needs pooler quiet and the 0096/0097 apply); connections 21 at 2026-10-23 20:4x IST | Gate A (K1c baseline) |
| T9 | K9 numerator labelled REPORTED | STANDING rule in force | labelling rule (Triage review) | - |

### Tag Mapper (WO-3)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| TM1 | Founder adoption of the time-bridge class before narrow-class fills | OPEN | PLAN.md: item 11 NOT approved | Tier 2 fills |
| TM2 | Versioned company-and-era-scoped rule store (A13) with 0098 applied for the before-image | OPEN | spec DEFINITION-VERSIONING-SPEC.md untracked; 0098 not applied | Tier 2 fills |
| TM3 | Final census after R2/R3 and the cohort re-draw | NOT YET DUE | depends on R2/R3 and P1; not due | Tier 2 |
| TM4 | Doc 53 slot rows for scans and a named Verifier lane for WO-3.1 | OPEN | no slot rows (see D5) | Tier 2 |
| TM5 | WO-3 scope corrections | CLOSED | doc 49 7.11; doc 47 | - |
| TM6 | Regression-clean list frozen | OPEN | no regression_clean_companies.csv on origin/main or in the shared tree | Gate A |

### Data Engineer (WO-1)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| DE1 | Gate B re-quoted from lane totals or a third lane | CLOSED | doc 49 section 4 + 7.12; branches origin/work/data-engineer/lane1-*, lane2-*, lane3-* show three lanes | - |
| DE2 | Single 0097 amendment; 0100 committed before G and applied in S1 | PLAN TEXT closed, build OPEN | 0097 amendment CLOSED (ab63ca7); 0100 WRITTEN ON BRANCH (origin/work/data-engineer/lane1-p1-primary-filer-v2, ef0c513, 3b801ac), not merged to main, not applied; doc 53 on main still says 'claimed, not written' | G (clock) |
| DE3 | No concept-level guard ships until cell_blank_reason exists and the guard writes its reason there | PLAN TEXT closed, build OPEN | plan text CLOSED; branches lane1-reason-store (2edaed0, fb50eb4) and lane1-p1-primary-filer-v2 hold 0100 and the store API; not on main; not applied | Gate B |
| DE4 | Migration numbering/claims; thin cell_state DDL committed by K+14 | PLAN TEXT closed, build OPEN | claims CLOSED (4110566); 0102 DDL on branch lane2-cell-state-0102, not on main (0100 is on branches, see G4) | Gate C |
| DE5 | W3 + WO-23 one Stage 2e change set with a population dry-run and one periodic-forms constant; W3 and P1 precede cohort-dependent figures; D0 re-versioned after P1 | OPEN | branches lane1-stage2e-authority(-v2) exist; no population dry-run output on file; P1 not on main | Gate B (R2a/R2b) |
| DE6 | P1 starts only after the Verifier confirms the Entergy mechanism | CLOSED | team/GATE-A-IDENTITY-REGISTRANT-CHECKS.md (origin/main); P1 branches created after it | - |
| DE7 | Held guards committed by the Release Manager before any lane edits concept_fallback.py / derived.py; merge order ratified | OPEN | held code is pushed to held/* branches (not main); lanes rebuilt on lane 1 v2 stack; merge-order ratification not shown | Gate B |
| DE8 | cell_state v0 as a table with run id + active view after a 20 s explain check; fallback = view + snapshots | OPEN | no explain check output on file | Gate C |
| DE9 | Chief tells the Period Engineer the Q4 backfill waits for versioning | PLAN TEXT closed, build OPEN | plan text CLOSED (doc 49 7.12 item 9); notification not shown in files | before Q4 backfill |
| DE10 | Founder items D-1, D-2, D-4 decided; decision 16 before the Q3 10-Q is ingested (default: hold) | PLAN TEXT closed, build OPEN | D-1, D-2, D-4 CLOSED under delegation (PLAN.md 2026-10-23, reversible); decision 16 NOT approved (default hold stands) | Q3 10-Q of CIK 906107 (about Nov 9) |

### Product head (Ritwik)

| ID | Condition | Status | Evidence | Blocks |
|---|---|---|---|---|
| PR1 | Sector-row catalog and visible metric sets, corrected | OPEN | doc 50 (draft v0) found defective by the Sector Analyst (PLAN.md line 244: 4 groups without a defining row, at least 7 wrong tag leads); my correction is owed | Gate A (register) / Gate C |
| PR2 | K1c headline beside K1@1; K1@1 never a target; 73.35% is a proxy, baseline = E0 | CLOSED | register section 4 AMD 7; doc 49 7.10, 7.13; doc 48 amendments | - |
| PR3 | K14b removed; WO-10 company dimension item | CLOSED | doc 49 7.10 item 5; doc 47 final WO-10 line (added 2026-10-23) | - |
| PR4 | Named accountant for REPLACED cells and D(F) | OPEN | same as SL1 | D(F), Tier 3 |
| PR5 | No new metrics/sources/vendors before T1/T2 certified | STANDING rule in force | doc 43 section 4 kill list; doc 49 | - |
| PR6 | Dates ASSUMED ranges re-baselined at Gate A and each gate; promise wording | STANDING rule in force | doc 49 section 4 (PROVISIONAL), section 1 | - |
| PR7 | 116 valued-with-reason EV cells checked by the Verifier before K1c is quoted publicly | OPEN | list: scoreboard/lists/valued_with_reason_2026-10-20.csv (origin/main); no Verifier verdict file; Chief ordered them first in the Verifier queue | public K1c |

## 4. Calendar re-derived for the open items (ASSUMED; no date is set until G1-G5 are cleared)

G needs G1 (three more workflow runs, one per slot, the sanity failure unexplained), G2, G4 (0100 merged to main), G5 (a free heavy slot); G3 (VACUUM) is done. Earliest case (updated 2026-10-23 per Dhairya's corrections): refresh finishes tonight, sanity dispatched Sat 10-24 night, Frames Sun 10-25, health-check Mon 10-26, and the founder gives his go by Mon 10-26, and 0100 is merged to main by then: G = Tue 10-27. Any sanity re-failure, a later founder go or an unmerged 0100 moves G one-for-one. Offsets (working days after G, three Data Engineer lanes, doc 49 section 4): Gate A G+4; Gate B G+27 (range G+21..G+38); Gate C G+31; D(NF) G+58 (range G+48..G+75); E G+103 (range G+90..G+125). Holidays (Thanksgiving Nov 26-27, Dec 24-Jan 1, MLK Jan 18) are not removed from the counts; human approvals (founder, accountant) may slip by them.

| Scenario | G | Gate A | Gate B | Gate C | D(NF) | E |
|---|---|---|---|---|---|---|
| Earliest | Tue 2026-10-27 | Mon 11-02 | Thu 12-03 | Wed 12-09 | Fri 2027-01-15 | Fri 2027-03-19 |
| Base | Mon 2026-11-02 | Fri 11-06 | Wed 12-09 | Tue 12-15 | Thu 2027-01-21 | Thu 2027-03-25 |
| Late | Mon 2026-11-09 | Fri 11-13 | Wed 12-16 | Tue 12-22 | Thu 2027-01-28 | Thu 2027-04-01 |
Time-boxed decisions inside these scenarios: item 16 before the Q3 10-Q of CIK 906107 (about Nov 9; default hold); item 12 before the Q4 backfill; the accountant before D(F). Gate B cannot be earlier than about G+23 whatever the lanes (serial chain F1 -> W3 -> P1 -> identity, doc 49 section 4). Risks to the dates that are not in the table: the sanity workflow cause; Verifier capacity (two sessions) after two usage-limit stops on 2026-10-21/22; the 114 moved-company evidence rows (up to +3 days at Gate C).

## 5. What I could not verify
I did not read every line of `PLAN.md` (about 400 lines) or open any branch's code; branch existence is evidence of work started, never of a closed condition. "No file on origin/main" statements are from `git ls-tree` of origin/main after `git fetch` at head c2253c2 and from `ls` of the shared tree. Condition wording is shortened from each review's sign-off section. Statuses are mine, from files, and should be checked by the Chief or Triage; I did not wake the agents.
