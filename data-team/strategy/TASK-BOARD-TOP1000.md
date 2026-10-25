# Task board: top-1,000 companies, full coverage and correct values

Owner of this page: scrooner-25 (core engine lane), with lane B/C lines supplied by Dhairya (scrooner-a5). Updated on every push. Founder request 2026-10-25: list every task, show done / wip / blocked / not started, keep it current. If this page and THE-PLAN.md disagree on direction, THE-PLAN wins; this page only tracks state.

States: **done** = verified and on main or applied; **wip** = being built, evidence named; **blocked** = waiting on a named thing; **not started**.

## 0. The scoreboard (what the user would see today)

**Task count (39 tasks, 2026-10-25 late night): done 12 (31%), in progress 16 (41%), blocked 1 (3%), not started 10 (26%). Remaining 27 (69%).**

History floor 2014-01-01 (founder, corrected 2026-10-25): FY2015 year-over-year growth keeps its prior year; nothing before 2014 is kept.

** By what a user sees: 0% (nothing is switched on in production yet; the first switch-on waits on migrations 0098-0100 being applied and the Verifier's batch samples).**

| Number | Value | Source | Goal |
|---|---|---|---|
| Certified companies | 0 | `analytics.company_certification` (0 rows, live 2026-10-25) | 1,000 |
| Companies whose cells have changed in production because of this programme | 0 | every fix is on a branch, dry-run, flag off | 1,000 |
| Reasonless blanks, cohort v1.1 | 13,354 of 161,533 cells | coverage table rebuilt 2026-10-23, snapshot 2026-10-24 | 0 |
| Valued cells, cohort v1.1 | 124,029 (76.8%) | same | every cell valued or reasoned |
| Wrong-value findings, certify dry-run | 37,681 at 898 companies | run 40094543570 (2026-10-24), 92 of 103 shards completed; 11-shard rerun 40169529802 running | 0 |
| Slot-record cells filing-checked by the Verifier today | 0 wrong of 112 + 55 + 123 + 80 + 27 (BS) and 19 (debt) | VERIFY-* files 2026-10-25 | every shown cell |
| Review findings, certify dry-run | 181,450 (I11 history 135,396) | same | classified |

Plain reading: a lot has been built and verified on branches, and nothing has reached a user yet. The chain that unblocks production writes is: apply migrations 0098-0100 (needs the founder's go in scrooner-4d's session) -> quiet window -> flag-on dry-run -> Verifier zero-wrong -> release.

### Wrong values by cause (certify dry-run, 92 shards; where the 37,681 come from)

| Cause (invariant) | Findings | Data points | Owner / fix | State |
|---|---|---|---|---|
| Per-share value derived by subtraction (I8) | 14,816 | basic/diluted EPS, effective tax rate | Period Engineer: per-share derivation ban (B2) | wip, flag off |
| Split basis mixed in one series (I9) | 8,034 | shares outstanding, EPS, DPS | Period Engineer: split re-base (B2) | wip, 194/194 clean class passed Verifier; other_changed class being fixed |
| Total liabilities = assets - equity, NCI added wrongly (I1) | 4,532 | total_liabilities | scrooner-25 slot records BS totals (B1 replacement) | wip, 14/16 anchors pass |
| Statement arithmetic does not tie (I6) | 6,245 | gross profit, opex, net income, operating income | perimeter families (slot records) + Standardization rulings | not started as slot families |
| Stale / wrong-period value shown (I3, I4, I5) | 3,009 | mixed | stale guards (lane 2 branches, flag off) | wip, flag off |
| Effective tax rate on YTD/derived inputs (I8) | 5,079 | effective_tax_rate_reported | **no owner yet** | not started |
| Other (I2) | 53 | | | |

11 shards did not complete in that run (S000, S024, S047, S056, S065, S068, S073, S078, S085, S101, S102); the rerun is scrooner-4d's.

## 1. Foundations and gates

| # | Task | State | Evidence / blocker | Next |
|---|---|---|---|---|
| F1 | Cohort v1.1 = exactly 1,000 companies, hashed | done | hash b13474512c425192, AMD 10 | none |
| F2 | Honest coverage measure (latest period has value) | done | migration 0096 applied; scoreboard E1 c4a375d | re-extract after each release |
| F3 | Certification suite I1-I11 (dry-run) | done | 7028d17, workflow on main 8a4d3a1 | I12/I13 reserved, need structure tables |
| F4 | Certify dry-run over the whole cohort | wip: 92/103 shards aggregated; the 11 missing shards rerunning (run 40169529802, scrooner-4d) | writes nothing (dry-run default) | aggregate the 11 shards into the wrong-value table; decide when the suite may write certification_finding |
| F5 | Migrations 0098-0100 (reason store, split tables, cell evidence, registrant, audit) | **done: applied to production 2026-10-25** (founder in scrooner-4d's session; 8 new tables present, empty; period_gap constraint includes per_share_not_filed_separately) | | reason rules and split re-base can now dry-run against real tables |
| F6 | Migration for `analytics.company_slot_record` (the mapper table) | written (0110, claimed in doc 53; on branch work/scrooner-25/slot-records; NOT applied) | cannot land on main before 0101-0109 exist (contiguity check) | Data Engineer lanes write 0101-0109; then 0110 merges and is applied with the first switch-on |
| F7 | Four scheduled workflows green | wip -> mostly done (scrooner-4d 2026-10-25): sanity baseline reset at the founder's instruction (gate passes; 2 critical / 15,619 major recorded, quick_ratio regressed +240 with NO cause found: an accepted debt until B7 lands), nightly refresh fixed (039141a), dead letters 0; certify rerun of the 11 shards running (40169529802) | the quick_ratio +240 needs a root cause, not just a baseline | fold the certify aggregate in when 4d sends it |
| F8 | Parallel execution of heavy jobs (replaces "quiet window and clock G", founder 2026-10-25: "move faster, thread, shard, multiple connections") | wip (budgets proposed) | scrooner-4d: max_connections 90, pooler reserves ~15, nightly refresh ~8; proposal max 4 heavy shards at once (4-8 connections), never alongside the 16:05Z refresh. Dhairya: 8 pooler connections total for data-team agents | Dhairya + 4d agree the budget, then run sharded |
| F9 | Companyfacts storage dedupe + history floor | wip: floor is **2014-01-01** (founder to Dhairya, 2026-10-25); the purge that started at 2015-01-01 is being corrected by scrooner-4d (stop at the 2014 line, restore any 2014 rows from the verified backup); hash-dedupe of raw companyfacts next | | final counts from scrooner-4d |
| F10 | Approver policy (agents only, approver != preparer, founder signs novel definitions) | done (founder confirmed 2026-10-25: "approved, dhairya understand this") | THE-PLAN 7.1 to be closed by Dhairya | none |

## 2. Core engine: company slot records (lane A, scrooner-25)

The slot record is the mapper: per company, per statement line, the tags that compose the total in that company's own filing, keyed by era. Branch `work/scrooner-25/slot-records` (68ed251). Nothing from this lane is in the database yet.

| # | Task | State | Evidence | Next |
|---|---|---|---|---|
| A1 | Cohort FSDS asset: all statements, 1,000 companies, 2015q1-2026q3 | done | cohort_pre_rows.jsonl.gz 110 MB + bs dims 120 MB (local) | reuse for every family |
| A2 | Era detection (face fingerprint per filing, boundaries, cal fallback chain) | done | era_detect.py, bs_totals_detect.py | generalize per family |
| A3 | Total debt family, 33 companies | **done for 33 companies: Verifier gate PASSED on V5.2** (VERIFY-DEBT-V52: 19/19 published values right, 15 flagged cells right; AMAT 2023-10-29 5,561M and COST 2025-08-31 5,788M confirmed right) | 100 agree with lane 3, 215 disagree (lane 3 double counts), 159 flagged, 0 holds beyond 4 instance-reader and 3 missing-member cells | debt rollout after BS batch 2 passes (Dhairya sequence) |
| A4 | Face-admission guards + 12 must/must-not fixtures | built, 15/15 fixture expectations pass; awaiting Verifier 3 | face_admission.py (Abstract, liabilities zone, cal descendant/total/component of a member, replay value tie); EW's two lines are not in the FSDS face rows of 0001099800-16-000044, so that fixture needs an R-page re-read | Verifier 3: 12 fixtures + COST 2018-09-02 on debt V5 |
| A5 | Balance-sheet totals family, 19 companies | **done for 19 companies: Verifier gate PASSED; every cell now has a value** | V3.2: 851 identity ties, 0 gaps, 0 holds, 16/16 anchors pass (TRGP and AWK now values, not holds); the 123 instance-reader cells filled and tying. Not switched on: a shared-table write behind a flag with dry-run, Release Manager review and rollback | Verifier recheck of the 123 filled cells; 0110 merge; flag-gated switch-on |
| A6 | FASB taxonomy balance-attribute CSV (replaces lexical non-liability guard) | done (fetched) | us-gaap 2025 elements CSV (name, balance, periodType, abstract; 1.5 MB) on the branch; one fetch, generic UA, zip deleted | wire as the structural guard in bs_totals_detect / face_admission (lexical stays as fallback) |
| A7 | Instance reader for custom-tag values (API never has them) | done for the BS family | 123 held cells filled from the filings' own instances (AWK 46, TRGP 46, DVN 30, BRKR 1), every one ties the identity; mezzanine per class of stock read per axis; 338 requests, downloads deleted | Verifier recheck of the 123 cells; reuse for debt (GE 2, RPAY 2) |
| A8 | D&A and capex families | wip: member-level gate V2 built and run on the 36-company set | G1 printed root line / G2 composition tie; children never summed beside their parent. D&A: 2,053 publishable cells, production differs on 45 (INTC shows ~265M where the face says 8,711M), blank on 599; 602 need the instance reader. Capex: 2,532 publishable, production differs on 73 (KO 1,675M vs 1,750M), 77 hold without a statement cal. Nothing proposed | Verifier draw requested (SLOT-RECORDS-DA-CAPEX-GATE-DESIGN) |
| A9 | Remaining families for the 18 metrics: revenue, net income attributable to parent, operating income, shares, EPS (never derived), CFO, dividends, buybacks, interest expense, tax | not started | each inherits statement-role + coverage rules | one family at a time, Verifier each |
| A10 | Scale each family from 19-33 companies to 1,000 | **BS: 999 companies have slot records** (printed-total 702 + face-sum 297); Verifier passed batches 1 (80/80) and the census (27/27); batch 2 (378 ties, 0 withheld) and batches 3-5 (30 zero-request companies, 620-instant manifest) await the Verifier; zero-cal trial: 5,356 of 5,653 face-sum cells tie with no cal file; ~149 cals (~300 requests) left for 130 failing eras + 19 no-structure eras. 0110-shaped rows exported for all 999 (26,646, proposed). DEBT: sized (953 companies would need a cal at 2 requests each); zero-cal re-measure being built before any fetch | Verifier on batches 2-5; then the 43 failing-era companies under the 60-request ceiling; debt re-measure result to Dhairya | A10 BS batches, then debt |
| A11 | Format-change gate (new 10-K/10-Q fingerprint vs record -> hold cells) | not started | design in EXCEPTION-RULE-REGISTER-DESIGN | after F6 |
| A12 | Production wiring: slot records feed `*_resolved` values behind a flag | not started | needs F5, F6, quiet window | after A10 for the first family |

## 3. Root fixes (lane B, Dhairya; lines as of 2026-10-25 11:45 IST)

| # | Task | State | Evidence | Blocker / next |
|---|---|---|---|---|
| B1 | Live total-liabilities identity bug (5,252 cohort cells, 185 companies) | wip | identity-fix v2 branch (interim, frozen); hold-writer a277d8d; dry-run only | superseded by A5; waits on BS V1 Verifier recheck |
| B2 | Split re-base + per-share derivation ban | wip | work/period-engineer/split-rebase d7fdefd; clean classes 194/194 Verifier pass; other_changed class being fixed | Verifier 1 recheck; flag on in quiet window |
| B3 | Reason rules (5 flag-gated rules; 7,724 pending closures need audits) | wip (unblocked 2026-10-25: 0098-0100 applied) | work/data-engineer/reason-rules cddbf7e, dry-run only | dry-run against the live reason store, Verifier sample, then flag on |
| B4 | Total debt via slot records | wip | = A3/A4 | scrooner-25 |
| B5 | Common equity + W10 share-date anchor | not started | lane2-w10-anchor branch has the anchor rule (300-company sample, 0 regressions) | dispatch |
| B6 | Interest expense 2024 taxonomy tag (~1,500 companies) | not started | tag exists only from the 2024 taxonomy; needs an era rule | design era rule, then dispatch |
| B7 | quick_ratio treats missing inventory as zero (live bug) | wip | work/data-engineer/quick-ratio-fix, flag off | dry-run, Verifier |
| B8 | Effective tax rate wrong values (5,079 findings) | not started, owner Data Engineer (Dhairya 2026-10-25) | certify I8 | dispatch after lane 3 + Period Engineer fixes (3-agent cap) |
| B9 | 10-Q filed but zero facts (companyfacts lacks the accession; ~200 filings) | not started | detector branch lane2-ingestion-detector; fallback reader not built | Data Engineer + Tag Expert |
| B10 | Statement-arithmetic wrong values (I6: gross profit, opex, NI, OI; 6,245 findings) | not started, owner Data Triage to classify first (Dhairya 2026-10-25) | certify I6 | classify, then slot-record families |

## 4. Verify and release (lane C)

| # | Task | State | Next |
|---|---|---|---|
| C1 | Verifier 2: TRGP, AWK, BRO + BS V1 recheck | wip | answers back to scrooner-25 |
| C2 | Verifier 1: split other_changed recheck | waiting on Period Engineer | |
| C3 | Verifier 3: COST 2018-09-02 + 12 fixtures on debt V4.1 | not dispatched | after A4 |
| C4 | Release Manager push path | done | pushes work since founder's permission rules |
| C5 | First production release train (any flag turned on in prod) | not started | F5 + F8 first |

## 5. Reason layer and templates (every blank gets a reason)

| # | Task | State | Next |
|---|---|---|---|
| R1 | 8 cell states + reason store (migration 0100) | done (applied 2026-10-25) | populate via the reason rules |
| R2 | Reason rules closing the 13,354 reasonless blanks | wip (unblocked; B3) | dry-run, Verifier, flag on |
| R3 | Group/template model (66 sector rows, visible metric set per group, doc 50) | draft, not built | Sector Analyst + Standardization rulings |
| R4 | Reasons shown on the company page (apps/app) | not started | after R1 |

## 6. Founder decisions
Decided 2026-10-25 (to scrooner-25): (1) migrations 0098-0100: go ahead; (2) storage dedupe authorized, and delete all data before 2015-01-01; (3) approver policy: agents only, confirmed; (4) no quiet windows or clock G: shard, thread, multiple connections, finish the job.
Still open: show unaudited 8-K Q4 earnings figures, labelled? (THE-PLAN 7.2); load SEC Notes data sets after a size pilot? (THE-PLAN 7.3).

## 7. Movement log (newest first)
- 2026-10-25 (night, consolidation): founder asked for reusable code to save tokens: common.py (cal loader, statement children, same-accession fetches, rounding unit, SEC client, face rows) + run_bs.sh one-command runner; regressions unchanged. Debt zero-cal re-measure over 999 companies: only 24.8% of cells publish on a note tie, so debt needs the filer's calc graph; per-filing fetch would be ~2,143 files; proposed to Dhairya: SEC Financial Statement and Notes data sets (cal.tsv in bulk, ~47 zips) instead of per-filing fetches.
- 2026-10-25 (night, go on zero-request batches): batches 3-5 selected (30 companies, 20 with reading B) with one combined Verifier manifest; slot-record rows exported for all 999 cohort companies (proposed). Debt zero-cal re-measure next; no debt fetch without Dhairya's go.
- 2026-10-25 (night, estimate): zero-cal trial over the 271 remaining face-sum companies: 5,356 of 5,653 cells tie with no cal file (identity-chosen taxonomy-total reading); only 130 eras at 43 companies plus 19 no-structure eras still need their own cal (~300 requests for the whole remaining BS rollout). Estimate sent to Dhairya; batch 3 waits on his go.
- 2026-10-25 (night, later): Dhairya's budget warning answered in progress: a zero-cal trial over the 271 remaining face-sum companies is running (database only) to measure how many eras tie on taxonomy totals alone; no batch 3 fetch until the estimate is accepted.
- 2026-10-25 (night, batch 2): BS batch 2 run (ALB, EPD, TMUS, RYN, BURL, MXL, BBIO, SBAC, MNST, STZ): final 378 ties, 0 withheld (TMUS/ALB resolved by a taxonomy-total alternative reading the identity chooses), 45 wait on the instance reader; rollout rule: borrowed cal first, the era's own cal only where the identity fails (34 eras, 68 requests). SEC usage ~1,228 of 2,600. Verifier draw requested.
- 2026-10-25 (night, late): Verifier PASSED debt V5.2 (19/19), BS batch 1 (80/80) and all 9 census printed totals (27/27). Batch 2 cleared and selected (ALB, EPD, TMUS, RYN, BURL, MXL, BBIO, SBAC, MNST, STZ; 10 cals). D&A/capex member-level gate built: first publishable cells, 45 + 73 production differences for the Verifier. Debt rollout approved in sequence after BS batch 2.
- 2026-10-25 (late night): founder applied migrations 0098-0100 in scrooner-4d's session (8 tables present); pre-2015 purge running there. Blocked count 5 -> 2 (sanity/health workflows; Verifier 1 split recheck). BS cross-check: Vornado, Carlyle, US Foods now tie; 9 companies with unexplained printed-total gaps handed to the Verifier.
- 2026-10-25 (night, after limit reset): BS rollout batch 1 done (JPM, BAC, TRV, PLD, DUK, GE, EMR, WMT, T, VLO): 453 identity ties, 0 withheld, 2 SEC requests; Verifier manifest pushed. Census rerun with two mezzanine fixes running. Debt V5.2 queued for Verifier (AMAT 2023-10-29, COST 2025-08-31 first).
- 2026-10-25 (after limit reset): Verifier cleared the BS family for the 1,000-company rollout (123 instance-filled cells, no wrong shown value). BS census over 698 no-cal companies: 621 tie at every instant. Debt V5.2: holds -> flags per Verifier. D&A/capex resumed with a filing-side gate; first gate too strict, redesign queued. EW fixture dropped (no such Edwards balance sheet).
- 2026-10-25 (late night): BS totals family complete on 19 companies: 851 ties, 0 gaps, 0 holds, 16/16 anchors; the 123 instance-reader cells filled from the filings' own instances (338 SEC requests). Debt V5.1: COST-class current-maturities rule and LongTermDebt note-tie on every cell (185 cells to review, 0 published beside a gap). FASB 2025 element CSV fetched. 0110 DDL written. SEC usage ~1,138 of 1,300; free disk 7.9 GB.
- 2026-10-25 (night): founder: "complete all the tasks by today itself, ask everyone to work hard" relayed to Dhairya and scrooner-4d. Core engine: 0110 DDL written (F6); face-admission guards built, 15/15 fixtures pass (A4); instance reader built and running on AWK/BRKR (A7). Debt V5 replay on 33 companies: 0 face lines admitted, 1 rejected (NFG-type asset-side line), no regressions.
- 2026-10-25 (evening): Verifier 2 filing-checked BS V2: 112/112 shown values right. V3 pushed with its four fixes: 728 ties, 0 gaps, 0 holds; MCK and ET now tie at every instant; GE's 12 false gaps gone. First slot-record family with zero known wrong values on 19 companies; switch-on waits on the Verifier's draw and the slot-record table migration.
- 2026-10-25 (later): BS totals V2 pushed on work/scrooner-25/slot-records: 0 holds (was 292), 699 identity ties (was 429), 14/16 anchors + 2 correct holds, no face-sum value published without an identity tie; 143 cells wait on the instance reader. Owners assigned by Dhairya: effective tax rate -> Data Engineer; I6 arithmetic -> Data Triage. scrooner-4d re-dispatched the 11 missing certify shards and fixed the nightly refresh (039141a). Relayed approvals are not accepted for production writes: the founder must type the migration go and the delete authorizations in Dhairya's and 4d's sessions.
- 2026-10-25 (founder): four blockers cleared (migrations go, dedupe + pre-2015 delete, approver policy, parallel execution instead of quiet windows). Blocked count 7 -> 3 (sanity/health workflows, Verifier 1 recheck, B1 parked). F5 and F9 move to wip/authorized; F10 done.
- 2026-10-25 (later): Verifier BS V1 verdict in: gate fails on AWK (11 instants), 129 avoidable holds, BRKR custom-equity member; three fixes queued to scrooner-25 (A5). BRO anchor corrected to 2018-12-31.
- 2026-10-25: board created. Certify dry-run aggregated for the first time: 37,681 wrong-value findings at 898 companies, 92/103 shards; effective tax rate (5,079) has no owner. Lane B/C states from Dhairya. Core engine: debt 33 companies Verifier-passing, BS totals 14/16 anchors, nothing in DB.
