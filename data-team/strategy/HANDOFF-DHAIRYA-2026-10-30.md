# HANDOFF: chief of staff (Dhairya) and the two peer sessions, 2026-10-30

Purpose: a new session starts here instead of replaying a long history. Read this file, then `AGENTS.md`, `data-team/NOW.md`, run `python3 scripts/agent_context.py`. Do not read old reports unless a task needs one; search with `mind/mind.py search "<term>"` first.

Status of this file: written from the main session's context on 2026-10-30. Anything dated 2026-10-27 or later was not seen by this author. Check `git log origin/main`, `doc/data-moat/team/PLAN.md` (append-only running log) and `data-team/strategy/TASK-BOARD-TOP1000.md` before acting.

## 1. The goal and the standing orders (founder, Vikash)

- First scope is the **top 1,000 US companies (cohort v1.1, exactly 1,000), Jan 2015 to date**. 100% coverage and 100% correct data. Everything else is dropped until this is done.
- Every cell is a correct value traceable to a filing, or a visible evidenced reason. Claim wording: "checked against the filing; error rate published". Never "100% correct".
- Judge progress only by: wrong values removed, reasonless blanks closed (13,349 baseline), K1c, certified companies (0 today).
- Root cause and scalable system, not point fixes. Design: companyfacts API as the value feed, a company-wise mapper (slot records from each filing's presentation and calculation tree), and a format-change gate on every new filing.
- At most 2 to 3 agents at a time (session token limits killed agents many times). The database allows 90 connections; the team cap is 30 backends; any agent doing read-only checks uses 1 connection.
- Use the mind: `mind/mind.py search` first, `mind/mind.py add` for every durable finding. Keep reports short; lead with scoreboard numbers.
- All-agent policy: the approver is never the preparer; the founder signs only novel definition calls. Restated periods whose copies disagree are HIDDEN, quarters and full years (founder ruling). Quick ratio formula unchanged; hidden where a current materials-and-supplies line exists.
- Production applies need the founder's own words typed in scrooner-4d's session; relayed approvals are not accepted. Do not launder permissions through another session.
- `SEC_USER_AGENT` (founder's contact) goes to sec.gov and data.sec.gov only, never any other host. At most 4 requests per second to SEC; budget tracked per session.

## 2. Where the work stands (as of 2026-10-27)

By what a user sees: 0%. Nothing is switched on in production. Certified companies 0 of 1,000. Certify dry-run baseline: 276,847 findings, 40,774 wrong_value at 977 of 986 cohort companies (the number to bring down). v1.1 extract: 163,000 cells, 123,287 valued (75.64%); the drop against the earlier snapshot is the 2014 floor (623 of 696 lost cells), 73 cells traced (52 floor, 21 resolve lag at 17 companies, to re-check after the next refresh).

Applied in production (founder-typed): migrations 0096 to 0100, 0111 (storage_object_retired, sec_companyfacts_unchanged_fetch), the 2014 floor purge and restore, storage dedupe (about 50 GB of duplicate objects retired, ledger in `/Users/vikash/scrooner-backups/pre2015-2026-10-25/`). NOT applied: migration **0101** (company_slot_record, on main c2c7844). To apply, the founder types in scrooner-4d's session: "Apply migration 0101 to the production database." (not required for total-liabilities release 1).

### Families (all on branches, flags OFF, dry-run only)

| Family | Branch (origin) | State | Next |
|---|---|---|---|
| Total liabilities (first release candidate) | `work/scrooner-25/slot-records` d2479c8; apply module `work/data-engineer/bs-tl-release1` 2da77d3 (LOCAL ONLY, push it) | Verifier sample: 200 of 200 differences production-wrong; at least 97.9% of 3,769 are wrong (about 3,690 wrong values at 358 companies). Release 1 NOT shippable as packaged: UPS 2017-12-31 slot wrong (counted "Deferred compensation obligations" 37M as a liability) | Repackage release 1 = only identity-gap EXACTLY 0 cells (about 3,396), exclude equity-section lines by position, move 98 nonzero-gap cells and 39 no-replay-row cells to release 2, new digest/before-image/rollback; add resolver guard so nightly resolvers cannot overwrite slot values; 10-company rehearsal with restore; Verifier fresh draw; Release Manager merge flag OFF; founder words for production write |
| Retirement Family B (per-share derivation from proxy: tax rate and DEF14A) | `work/data-engineer/derivation-gate` aaaf4cc (plan 14) | Verifier B14: ready for apply review NO, one cell: CSGP Q4 2023 shows 96,475,000, filing supports 96.5M (apply printed decimals to every derived quarter). 72 superseded facts, 240 re-promotions, 0 authority exceptions | Fix CSGP; URGENT Pinnacle 8-K demotion (below); then apply review with reviewed apply and restore plan, CLX ingestion gap, sample outside cohort |
| Split re-base and dividends | `work/period-engineer/split-rebase` 9b81a73 (run 6) | Verifier run 6 FAILED: 3 wrong dividends (LOGI Oct-Dec 2021 shows 0.95, right 0; AMT FY2022 shows 4.30, right 5.86; AMT FY2023 shows 6.31, right 6.45) | Full-year and YTD must agree with the company's own quarterly facts on the chosen basis; 3-month value equal to YTD in the same filing is a context error; release false holds (about 25 same-quarter declared-and-paid dividends; MSM 5.75, HL FY2020, WYNN Q1 2021, AHR, QXO FY2023, NAVN, NWSA, SWK, FORM); LLY FY2019 stays hidden (paid basis 2.58). One dividend basis per company (basis = tag with more filed quarters since 2015, tie Declared). Still open: LMT restated, PRAX x15, CBSH 2026 cells, HL Q3 2021 |
| Quick ratio and inventory@2 | `work/data-engineer/quick-ratio-fix` 787f3d5 | Verifier v5: sampled hides all right, 2 right values wrongly hidden (company 718332, two quarters, accession 0001140361-24-005023), 1 wrong kept (company 1590364 unclassified balance sheet), EOG 2015 wrong reason. Runtime already matches planner (0 at-risk stored cells today) | Fix the 3 items; OMC "Work in process" is a contract asset (ruled, record approved) |
| Shared accession (co-registrant) defect | `work/data-engineer/shared-accession` (worktree `/Users/vikash/scrooner-sharedacc`, uncommitted: staleness.py, status.py, facts.py, identity.py, shared_accession.py + 2 tests) | Nine cohort companies have NO financial data: ETR 694, ES 1008, SO 1081, CMS 1525, EIX 1576, AEE 2144, SRE 2503, TXNM 3562, CTVA 5394 (status "stale" since 2026-08-23; combined 10-K/10-Q accessions claimed by a co-registrant, e.g. ETR's under Entergy Arkansas). Rule `entity.shared_accession_primary_filer@1` never built; `core.filing_registrant` has 0 rows | Agent died on the limit before its dry-run; commit what exists, finish the read-only dry-run (full population, one connection), report recovered periods and any company that would lose data |
| Depreciation and capex | scrooner-25 slot records | V5 passed (task board); census 637/698 | continue per task board |
| Debt, BS totals | slot records | verified earlier, no wrong in 19 (debt) and 112+55+123+80+27 (BS) | debt at scale from the Notes cal rows |

### URGENT wrong value live today
Pinnacle's holdco 8-K (accession 0002082866-26-000020) carries Synovus's statements: 410 authoritative facts (187 tags) under company_id 4938. Production shows Pinnacle FY2025 net income 791,980K (Synovus) instead of the 10-K's 641,865K, and FY2024 482,460K. Needs a flag-gated demotion rule (own dry-run, before-image, restore) plus a scan for other companies where an authoritative 8-K accession carries another entity's statements.

### Verification tooling (on main, ff5aa5d and before)
`pipeline/src/scrooner_pipeline/verification/filing_kit.py` + skill `scrooner-verify-against-filing`: reads balance sheets and income statements from SEC R pages. Reproduces 25 of 25 (live fixture now 32 instants). Known gaps: cash-flow pages still use the old selector; BDC "Net increase in net assets from operations" label; leading blank cell shifts columns (DFH); headers with "€ in Millions" and "USD ($) $ / shares" in date cells (3592); ABNB-style whole-dollar pages rely on a six-trailing-zeros rule in the engineer's code.

### Notes data sets (FSN)
All 47 quarters 2014q1 to 2025q3 plus monthly files 2025_10 to 2026_09 uploaded to private bucket `fsn-notes` (about 26 GB; total must stay in the 100 GB Pro quota). Local copies kept: sub, cal, pre, num and manifests (about 0.6 GB). SEC request budget 2,600, used about 1,436 at last report. Multi-class share counts per class are in the num rows (BRK-A, UHAL, SUN, FWONA, BAM, PLNT): see `data-team/strategy/team/MULTI-CLASS-SHARES-FSN-2026-10-26.md`; BRK A:B ratio 1:1,500 flagged, not guessed; economic rights of PLNT/BAM class B and SUN C/D unchecked.

## 3. Open items by owner

- **Founder only:** type the 0101 apply sentence; the first flag-gated write of total liabilities release 1 (after Verifier clears the repackaged cells and the Release Manager reviews); migrations for `fact_authority_retired` (number unclaimed, doc 53 next free is 0112) and for any new table; later: show confirmed restatements instead of hiding; unaudited 8-K Q4 figures; accounting reviewer/book CPA; SIRI predecessor-entity history; screenshot for the bank-suppression change in `apps/app/components/company/FinancialTable.tsx` and `lib/company/db.ts` (held-UI rule: capture first).
- **Held code in the shared tree (needs flag and rebase, one release):** RU-1 per-share "never derive" policy: `normalizer/derived.py`, `mapper/ttm.py`, `price_metrics.py`, `concept_fallback.py`, `sanity/period_completeness.py`, new `common/derivation_policy.py`, `mapper/canonical_archive.py`, `scripts/ru1_retire_dryrun.py`, 8 tests, backups `doc/data-moat/team/backups/ru1_*`. Conflicts with newer main for four files.
- **scrooner-4d (engineering head, session socket `uds:/tmp/cc-socks/64972.sock`):** v1.1 extract and scoreboard done; open: re-check the 17 resolve-lag companies after the next refresh; classify wrong-value families I3 negative_on_nonnegative_concept (1,531), I5 quarters_do_not_sum_to_year (496), I4 statement_role_suspect (406) (note `data-team/strategy/team/WRONG-VALUE-FAMILIES-I3-I4-I5-2026-10-26.md` exists); coverage rebuild filter now `active OR cohort v1.1` (d888362) takes effect at the next nightly; re-run the certify dry-run after each fix lands to show the delta.
- **scrooner-25 (slot-record builder, socket `uds:/tmp/cc-socks/76336.sock`):** release package 1 (d2479c8) needs the repackage above; release 2 = 1,470 cells needing their own Verifier stratum; 663 "custom subtotal" holds need the printed-subtotal reading; 2,621 production cells with no slot cell classified (527 before first record, 754 between, 249 after last); face-admission guards and fixtures; instance reader; D&A/capex; debt at scale.
- **Kit builder:** cash-flow selector; BDC label; leading blank cell; "€ in Millions" headers.
- **Disk:** free 15 GB at last check (it dropped to 4 GB on 2026-10-26). Delete regenerable SEC downloads in scratchpad after use.
- **Process rules that were broken and fixed:** Release Manager must not reuse an existing worktree path (it reset the Data Engineer's `bs-tl-release1-guard` worktree on 2026-10-27; check that branch for lost resolver-guard edits); a verifier must not use production's value as proof; every release is behind a flag with a dry-run digest, before-image and rollback.

## 4. Agent roster (restart; old agent ids die with the old sessions)

Use the agent types in `.claude/agents/`: scrooner-data-chief (planning, independent approver), scrooner-data-engineer, scrooner-period-engineer, scrooner-data-verifier (Verifier 1 does split/dividends, Verifier 2 does families and releases), scrooner-standardization-lead (definitions, records), scrooner-tag-mapper, scrooner-tag-expert, scrooner-sector-analyst, scrooner-release-manager (temporary-worktree pushes; never applies migrations), scrooner-head-of-data-product, scrooner-data-triage, scrooner-mind-curator. Brief each from the table in section 2 with the branch, the verdict file and the exact fix list. Verdict files are in `data-team/strategy/team/` (`VERIFY-*-2026-10-26.md`; start with `VERIFY-BS-RELEASE1`, `VERIFY-RETIREMENT-B14`, `VERIFY-SPLIT-RUN6`, `VERIFY-QUICK-RATIO-5`).

Order of work for the next session (smallest steps first):
1. Push `work/data-engineer/bs-tl-release1` and the shared-accession worktree so nothing is local-only.
2. Pinnacle 8-K demotion rule (live wrong value).
3. Total-liabilities release 1 repackage, resolver guard, rehearsal, Verifier draw, Release Manager review, then ask the founder for the write.
4. CSGP fix, then apply review for Family B.
5. Split run 7 (three wrong dividends, false holds, one basis per company).
6. Quick ratio three-item fix and Verifier recheck.
7. Shared-accession dry-run, then the nine cohort companies recover data.
8. Re-run the certify dry-run and publish the delta on the task board.

## 5. Confidence (honest)

High that released families will be correct and traceable (gate is zero wrong shown values on a filing-checked sample; it catches real errors every round). Moderate on timing: first live fixes within days if production steps are not waiting on the founder; 3 to 5 weeks for all families across the 1,000 companies (estimate; session limits have cost days). Low that "100% correct" will ever be claimed; the claim is "checked against the filing, error rate published".

## 6. Working-tree note

The shared folder `/Users/vikash/scrooner` is on local main 746b80f: 186 commits behind and 8 ahead of origin/main (the 8 are backed up on `backup/local-main-2026-10-24`), 124 changed paths. Docs, agents and skills were pushed to main as 99bdf76 and ff5aa5d; what remains is held code, stale copies and scratch. Do not reset or clean the folder while other sessions use it. When all sessions are closed: back up the 124 paths to a folder outside the repo, then move the folder to origin/main.
