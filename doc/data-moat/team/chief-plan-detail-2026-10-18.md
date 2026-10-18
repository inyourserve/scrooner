# Data Chief plan: how to improve coverage (critique of the mentor position, milestones A-E, first two weeks)

Date: 2026-10-18. Role: Scrooner Data Chief (AI coordinator and founder decision-support; not an accounting approver, not a CPA).
Objective: answer "company-by-company, metric-by-metric, tag-by-tag, or map all tags?" with a plan the team can start Monday.
Scope: planning only. Inputs read: infra map (20), Chief role (10), release worksheet (04), runbook (06), doc 56, team log, decisions.md, headline sections of the Standardization Lead proposals.
Authorized actions and limits: READ-ONLY. No DB, no network, no repo edits, no commits. This file is the only artifact.
Task status: **PARTIAL**. The plan is complete; every live-number check below is **NOT_RUN** (no query executed in this session). All figures are quoted from the files named, as claims with their date, not remeasured.

---

## 0. Measured fact vs assumption (read this first)

Quoted from the repo (measured by others, dated, **not re-measured here**):
- Snapshot 2026-10-13 (stale 5 days): concept 86.32% (78 concepts), metric 74.61% (82 metrics), score 79.75%; 578,789 of 848,578 matrix cells have a value (68.2%); gap_reason populated on 193,196 cells (22.8%); line_not_presented_in_filing 13,903 cells (log Round 4, track 3).
- Only 61 mapped-tag-filed-but-empty cells (doc 56). About 90 of 12,372 tags are approved/provisional/preference; 64% of facts are under unmapped tags (doc 56).
- Mentor's tag-reach figures (12,013 unmapped; 342 at >=1000 companies, 740 at >=500, 1,679 at >=200, 3,534 at <=5): from the tag library, not in the files I read. **Unverified by me.** Doc 56's FSDS figures (342 tags in 200+ *filings*, 788 in 50+ filings) are on a different unit (filings, one quarter, 2025q4). The two "342" figures must not be read as the same fact.
- period_gap about 254k cells, about 57.6k Q4/quarter not derived. Q4 input-state samples disagree by sample and method: 0/60 clean (n=60), about 3% clean (n=1,200), about 2% clean (n=3,587). Say "0-3% clean" and never "3%" alone. No-9M-source share ranges 30% to 68% across samples. Full-population split is NOT measured.
- 39 of 52,464 sampled canonical_fact rows (0.07%, 150-company sample, 8 concepts) store a value that differs from an authoritative same-tag copy. Verifier n=5 hand-picked: 2 true source errors, 2 genuine recasts, 1 rounding, 0 stored-right.
- Derived weighted-average share facts: in a sample, 914 authoritative negative Q4 rows (log Round 4b). Code fixed 2026-10-17 (46399a6, 7825b47); DB rows stale until reprocess (whether reprocess happened: unknown).
- No adopted release policy ("data-team-pack-draft"); no qualified human accounting reviewer identified (Standardization Lead blocker B7).

Assumptions I am making (flagged where used): nightly jobs are unstable but not permanently broken; a transactional diff or a company-subset replay can stand in for staging (a real staging DB is NOT confirmed; infra map describes one shared Supabase); the full-population recompute may still be running (ListAgents first, always).

---

## A. Critique of the mentor's position

The core instinct (family by reach, not company-by-company, not "map all tags") is right. These are the things wrong, missing or risky.

1. **Correctness is ranked after coverage; the policy says the opposite.** Release worksheet class "Wrong published value": correct or withdraw before expanding coverage. There are known wrong-value classes sitting in the product now: stored value differs from an authoritative copy (39 sampled rows), mislabeled period columns and full-year-under-quarter-label errors (Verifier, 2 of 5 cells), and stale negative derived weighted-average shares. Order item "(3) quarter gaps" depends on the same upstream conflict fix. These belong in milestone B, before any new-concept apply, not as a footnote.
2. **"A cycle that does not move a number does not count" is a Goodhart trap, and the number is under-specified.** (a) Adding concepts grows the denominator: 24 new concepts at low initial coverage can *lower* the 86.32% average. Report on a fixed denominator and the new one side by side. (b) Many of the 24 face lines (retained earnings, par value, shares authorized, APIC) may feed no locked metric; reach by company count is breadth moat, not metric reach. The mentor's "metric -> missing concepts -> companies" chain is right but the step was never run: `metric_definition_input` inventory is NOT_RUN (blocker B10). (c) A rejected or held mapping that prevents a wrong number is a successful cycle; count decisions and defects prevented separately from cells gained. Add a guard number (wrong-value rate, sanity mismatches) that must not worsen.
3. **Step 1 "denominators/applicability honesty (~14k line_not_presented cells)" can itself inflate coverage.** `line_not_presented_in_filing` is evidence, not proof (the probe saw 14-34% of values we hold with no face line; a disclosure may live in notes). Dropping those cells from the denominator is exactly "improving coverage by shrinking the denominator." Do it as three-state reporting (value / proven-absent-from-face / unknown) with both denominators published, and never score it as progress. It is measurement work, not a gain.
4. **The loop's "apply" step has no approver.** "Standardization Lead defines, Verifier reads" is two AI contexts. No adopted policy, no accounting reviewer. New exact mappings and any combined/component/fallback substitution stay proposals. Without a named human or an adopted rule, the loop produces proposals forever. Also two *existing* approved fallbacks (diluted_eps p3 combined tag, net_income p3 with 38.6% pair disagreement, unremeasured) violate the drafted combined-line policy; grandfather-or-revisit is undecided and those feed live metrics.
5. **"Never company-by-company" overshoots.** Root causes are per-filing events (a restatement, a mislabeled amended filing, a custom extension), and verification is inherently per issuer-period. Correct statement: *select and fix* by rule family, *verify* by issuer-period sample, and weight reach by company band (top 100/1,000, doc 56 targets), because a tag filed by 200 large companies matters more to users than one filed by 400 shells. Raw company count as the sort key is a proxy, not the goal.
6. **Verification sample size is unspecified, and small n is easily over-read.** With n=12 and zero failures the 95% upper bound on the failure rate is about 25% (rule of three). It supports "failures are not common," never a rate. Pair with full-population code checks.
7. **Mapping-apply is heavy on a shared pooler.** Migration plus reprocess per family on ~5.2k companies, DB ~46 GB, ~15 shared connections, other sessions busy. Not mentioned: one family at a time, lane claims (doc 53), `ListAgents`, `statement_timeout`, rollback by mapping version.
8. **Q4 handling: the stored-value decision (latest-filed as restated, 2026-10-18) interacts with derivation.** Using restated FY with an original 9M input mixes bases (pack rule: never mix). The decision fixes the *stored* basis; derivation needs same-vintage pairing as an explicit step. Whether derivation may use conflict-filled values is still an open founder/accounting call.
9. **"Map all tags" is correctly rejected but the long tail is not free to ignore.** Custom tags are 9.2% of face lines (doc 56, 2025q4 FSDS); if concentrated in large issuers, they cost real user-visible cells. Unmeasured; keep a golden-set path rather than a flat "never."

---

## B. Plan: milestones A-E (runbook sequence)

Principles: one root-cause family per batch; code for enumeration and arithmetic; Verifier reads originals first and sees the proposer rationale second; a family stops on any critical discrepancy; every claimed gain is re-measured on the same denominator before and after.

### Milestone A: scope fixed and fresh, honest baseline (days 1-5)
Entry: none.
Work (owner role):
- A1 Reproduce baseline with query text and watermark: `max(snapshot_date)` in `analytics.coverage_snapshot`, matrix cell counts, `company_data_point_coverage.gap_reason` populated share, `company_population` counts. (Triage, Data Engineer)
- A2 Diagnose why the snapshot stopped 2026-10-13 and whether nightly snapshot runs again (`pipeline-refresh.yml` stage timing lines; remember cancelled-run logs are deleted). (Data Engineer)
- A3 Three-state ledger: VALUE / PROVEN_ABSENT_FROM_FACE / UNKNOWN per (company, concept, fiscal year), fed by `company_data_point_coverage`, `company_filing_line_evidence`, `period_gap`. Publish both denominators. (Triage with Lane A/B; no change to how `has_value` is set, doc 53 rule 2)
- A4 `metric_definition` / `metric_definition_input` inventory: for each of the 82 metrics, which canonical concepts, and for each of the 24 face lines, which metrics (probably none) feed on it. (Triage)
- A5 Reconcile the three counts: findings (~51k open), unique root causes, affected cells. (Triage)
- A6 Fix the population ledger: 13 FPI-only and 83 no-10-K inside `real_operating_company` (4,815): report with and without. (Triage)
- A7 Draft release policy (section D below) and put the founder decisions (section G). (Chief)
Number it must move: no coverage number. Deliverable is a published baseline: `coverage_snapshot` with today's `snapshot_date`; `gap_reason` populated share (22.8% -> target 100% of empty cells); a written UNKNOWN/applicable KPI.
Exit: snapshot written three consecutive nightlies (or a documented cause); KPI published with query text; metric-input map exists; policy draft in the founder's hands.
Risks: nightly cannot be stabilized (then manual snapshot with watermark and state it); DB read-only state or hang (check `show default_transaction_read_only`, stop issuing queries, do not retry through).
Team decides: all of A except policy adoption. Founder: KPI choice, population (G1, G2).

### Milestone B: wrong values out, upstream conflicts handled, one independently checked correction (days 3-15, overlaps A)
Entry: A1 baseline exists (so the effect is measurable).
Work:
- B1 "Authoritative same-tag copy wins" fix for canonical_fact (the 39-row class), with the precision tie-break and the restated-basis carve-outs from decisions.md. Owner: Data Engineer (code), Period Engineer (spec of conflict classes). Check with Lane F first (doc 53).
- B2 Deterministic label-error detectors: ~90-day value equal to the annual value; 12-month-ago value equal to current. Dry-run table first; population counts before any action. (Period Engineer)
- B3 Reprocess weighted-average derived facts (window-weight code already live). (Data Engineer; heavy job, ListAgents first)
- B4 Q4/quarter census, full population, in company chunks (the dry-run classifier commit 324d514 is the starting point): classes clean / conflicting / no 9M source / chain available / non-additive (EPS, never subtracted). Same-vintage pairing rule written. (Period Engineer)
- B5 Verifier: list the 39 rows plus a 12-case fresh sample for the fix; read originals first. (Verifier)
Numbers to move (re-measure with the same seed `authcount-2026-10-17`, 150 companies, 8 concepts): same-tag mismatches 39 of 52,464 -> expected 0 except documented different-basis rows; authoritative negative weighted-average share rows (sample showed 914 negative Q4) -> 0; `period_gap` rows by `gap_cause` for `q4_not_derived` split by new sub-cause, with every row carrying a cause (acceptance from doc 56 W1). Guard: sanity mismatch counts and Frames exact-match rate (99.69% on 28,187 pairs, doc 56) must not worsen.
Exit: 0 critical in the Verifier sample; full rerun of the seed sample; regression diff shows zero changed values outside the family; rollback exercised on a company subset; log entry written.
Risks: the fix changes values shown to users (that is the point; list screener membership changes in the packet); extrapolation "about a thousand rows" is unverified; the open question "why did the 39 slip past" may be a stale-ness issue, not grouping (owner's read).
Team decides: implementation within decisions.md. Founder/accounting: whether conflict-filled values may feed derivation (G3).

### Milestone C: repeatable bounded batches + adopted policy; first concept families (weeks 3-6)
Entry: B exit; policy adopted (or an explicit founder note that batches continue in "proposal only" mode).
Work per family, in order: Tag Mapper evidence -> Standardization Lead definition -> Verifier -> full-population coexistence (code) -> reviewer decision per policy -> committed migration + reprocess -> re-measure -> log.
- C1 Wave-1a families that need the fewest holds (retained earnings, common stock value, preferred stock value, additional_paid_in_capital primary tag, operating lease ROU asset, interest paid and taxes paid primary tags). Apply the Standardization Lead's holds literally: APIC-common fallback, `IncomeTaxesPaid` fallback, generic SharesIssued/Outstanding, IFRS retained earnings stay HELD.
- C2 Weighted-average basic/diluted concepts (after B3 so stale negatives are gone).
- C3 Share-count concepts last (split/restatement policy B9 unresolved).
- C4 In parallel, Period Engineer: derive the additive allowlist cells that B4 proved clean and same-vintage; dry-run table, Verifier sample, then apply.
- C5 Decide grandfather-or-revisit for diluted_eps p3 and net_income p3 (measure the real disagreement: the 38.6% is a repo comment, unremeasured).
Numbers to move (all names re-measured from `analytics.*`): `concept_mapping` approved/provisional row count; `canonical_fact` rows per new concept; `company_data_point_coverage` VALUE vs UNKNOWN per new concept on the **fixed** denominator (original 78 concepts) and on the **new** denominator, both published; `period_gap` cells fixed (derived fills) by cause; `metric_value` non-null counts only for metrics that actually consume the new concepts (from A4). A cycle with zero cells moved is recorded as a decision cycle, not a coverage cycle.
Exit: each family shows 0 critical in its Verifier sample, coexistence table recorded in `tag_concept_verdict` via `record-verdict`, unchanged values elsewhere, rollback tested.
Risks: reprocess load on a shared pooler; new concepts diluting the average; combined-line leakage; sign conventions (reported sign kept, no abs()).
Team decides: sequencing, evidence thresholds within the adopted policy. Needs human: definitions that change perimeter (D, F list).

### Milestone D: sector pilots (weeks 6-10)
Entry: C has at least 5 applied families and the policy adopted.
Work: banks first (Sector Analyst): select cohort by `core.company.sic_code`, read original statements, list lines (G&A, labor, provision for credit losses, deposits, loans), produce template + metric matrix; insurers and mortgage REITs separate; REIT and pre-revenue biotech after. FDIC source (doc 32b) as an independent comparator only, never a stored value (decisions.md locked rule). (Sector Analyst, Standardization Lead, Verifier)
Numbers to move: the 1,339 companies with revenue but no cost of revenue/gross profit (Financials 560, Healthcare 247, Real Estate 159, 2026-10-17) re-bucketed into template-applicable / proven-absent / unknown via `company_population` + `company_filing_line_evidence`; metric availability on the Financials band (top 1,000 launch-readiness rules, doc 53). Fixed-denominator reporting holds.
Exit: bank template verified on a cohort sample with 0 critical; unsupported metrics listed explicitly.
Risks: template guesses drive applicability (hypotheses, not facts); bank lines are mostly custom/extension tags.
Human reviewer required (bank/insurance/REIT accounting).

### Milestone E: expansion backed by observed throughput (weeks 10+)
Entry: D pilot done; measured decision throughput and marginal gain per family.
Work: top tags by weighted reach (740 unmapped at >=500 companies, per mentor, unverified), Wave 2 nature-of-expense lines, FSDS ingestion only after the size pilot (one quarter, rows/bytes/index growth reported, doc 56 W2; DB is 46 GB), long tail via golden set and company-level exceptions, custom-tag resolution last.
Numbers to move: UNKNOWN/applicable by band (top 100/1,000/all), monthly trend; throughput = verified families per week.
Exit: monthly UNKNOWN falling, never rising; expansion paused when the guard number worsens.

---

## C. Cadence, verification budget

Weekly cadence (one active worker plus one reviewer context; manual invocation; no permanent loops):
- Monday: Chief reconciles last week's ledger (baseline timestamp, defects, cells corrected, deltas on the fixed denominator), picks at most one next root-cause family, sets call caps. Data Engineer reports nightly health (snapshot date, per-stage timings).
- Tue-Wed: Tag Mapper / Period Engineer / Sector Analyst produce evidence and proposals for the chosen family; Standardization Lead defines.
- Wed-Thu: Verifier reads originals for the sample; code does full-population checks.
- Thu: Chief packet to the reviewer(s); decisions recorded (`record-verdict`, `record-finding`).
- Fri: Data Engineer applies approved migrations (committed, number claimed in doc 53) and reprocesses off-peak; Triage re-measures after the nightly snapshot; Chief logs.
- Triage runs continuously: queue hygiene, root-cause grouping, denominator ledger.

Verification budget (proposal; assumptions marked):
- Per new-mapping family: 12 issuer-period cases = 4 largest filers by reach (user-visible), 4 named counterexample issuers, 4 seeded random; 30 cases for families reaching >=1,000 companies or feeding a locked screener metric. Each case about 4 SEC requests (observed: 30 requests for 8 cells, about 3.75). So 50-120 requests per family, about 500-1,000 for the first 10 families.
- SEC limit: declared User-Agent, about 10 req/s aggregate; one SEC fetch process at a time; Verifier reads can run sequentially at 1-2 req/s, so the binding constraint is Verifier time and tokens, not SEC. Token cost: unknown (no telemetry); do not quote dollars.
- Quarter derivations: 50 cases per rule family for the first allowlist (cap from the pack's 50 representative cases per run), stratified by cause class and by whether the company restated.
- Checked by code on the whole population: coexistence agreement per tag pair (same context, same unit, same period) and disagreement magnitudes; balance sheet identity (assets = liabilities + equity), retained earnings roll-forward, cash-flow subtotal identities; sign and scale (>=10x) outliers; units; no non-target concept changes in the diff; lineage present for every changed value (`source_fact_ids`); `timeseries_outlier_check`, `metric_plausibility_check`, SEC Frames self-consistency; yfinance only as comparator.
- Limitation to state in every packet: the Verifier reads SEC R-pages, which render the same XBRL the pipeline ingests, so shared-XBRL errors are invisible; that is not a parser-independent check (edgartools gives some independence, doc 12).

---

## D. Release-policy proposal (04 worksheet, concrete values; DRAFT until the founder adopts)

| Field | Proposed value | Note |
|---|---|---|
| Owner / rollback owner | Founder owns policy; Data Engineer is rollback owner | |
| Policy version | `data-policy-v1-2026-10` | adopt date: founder fills |
| Universe | US-listed 10-K filers, `real_operating_company`; report with and without the 13 FPI-only and 83 no-10-K | count 4,815 per 2026-10-17, remeasure |
| Forms / history | 10-K and 10-Q; US-GAAP; data from 2015-01-01 (History gate doc 38) | IFRS and 20-F/40-F out |
| Templates | Industrial + Core set live; Bank, REIT, Pre-revenue biotech as pilots; Insurance and mortgage REIT unsupported until reviewed | |
| Freshness SLA | new filings visible within 2 business days; breach alerts the Data Engineer | assumption: nightly daily job works |
| Auto-apply (no per-cell approval) | (1) re-run of an already-approved exact mapping on newly filed facts; (2) additive derivation on an allowlist (revenue, cost lines, net income, cash-flow flow items), authoritative same-vintage inputs, no conflict, Decimal, full lineage | never EPS, share counts, ratios, weighted averages by subtraction |
| Needs reviewer decision | any new exact mapping or concept definition; any combined/component/fallback substitution; sector formulas; derivation from conflict-filled inputs; non-additive derivation | proposals only |
| Evidence to reach "verified" for a new mapping | full-population same-context coexistence reported; >=95% agreement within 1% against the claimed equivalent where a comparator tag exists, or documented perimeter difference; every counterexample issuer read by the Verifier; 12 cases (30 if reach >=1,000 companies or metric-feeding) with 0 critical | thresholds are proposals; a sample never proves a rate |
| Critical discrepancy | wrong entity, wrong sign, scale >=10x, wrong period, attribution (consolidated vs segment, class), or a change in screener inclusion for a top-1,000 company traced to a wrong value | any one stops the family |
| Non-critical | rounding, different-basis restated vs original with lineage, label differences | log, no stop |
| Conflict quarantine | disagreement >15% (existing conflict-fill bar) is not published as standardized and not used in derivation | preserve source values |
| Stored basis for restated periods | latest-filed as restated (decided 2026-10-18) with the label-error carve-out and precision tie-break | recommend accounting review |
| Never | missing, unknown, not-applicable, not-separately-disclosed to zero | reported zeros kept |
| Regression gate | golden-10 plus a fixed set of >=10 banks and REITs; diff of values outside target concept = 0 rows; sanity/Frames/plausibility not worse | |
| Rollback | revert migration + reprocess prior mapping version; tested on a company subset before full reprocess; evidence kept | staging DB not confirmed |
| Monitoring | Chief weekly metric + defect report; NOT_IMPLEMENTED items listed as such until built | |
| Coverage targets | provisional from doc 56 section 4 (top100 99/top1,000 97/all 93 on VALUE + PROVEN_ABSENT): **do not adopt until the three-state baseline exists**; interim rule: UNKNOWN falls monthly, wrong-value incidents trend to zero | pack forbids inventing a target before a measured baseline |

---

## E. Honest coverage reporting

- Headline: UNKNOWN cells / applicable cells (doc 56 moat KPI), plus the three counts side by side: VALUE, PROVEN_ABSENT_FROM_FACE, UNKNOWN. The label is "not shown on the statements," not "does not exist"; notes-lookup path stays open.
- Two denominators always published: **fixed** (the 78 concepts / 82 metrics / 4,815 companies as of this baseline) and **current** (new concepts, new applicability). A gain is credited only on the fixed denominator. Reclassification (applicability, population cleanups) is shown as a separate line, never as a gain.
- Every snapshot shows its `snapshot_date`, population definition and whether `gap_reason` is populated; stale or unpopulated means the number is labeled "stale/unmeasured."
- Never mix per-company averages with cell counts; state which.
- Quality reported next to coverage: wrong-value incidents found, sampled critical rate with n and the rule-of-three bound, never a "% correct."
- "nothing relevant filed" is described as "none of our tags filed," not as absence.

---

## F. Items needing a human accounting reviewer (AI cannot clear these)

1. Perimeter-changing definitions: APIC vs APIC-common, income taxes Paid vs Net (company 612 contradicts the gross/net reading), preferred value (74% reported zeros in the sample; mezzanine/APIC-preferred counterexamples), combined lines.
2. Grandfather or revisit diluted_eps p3 (combined tag) and net_income p3 (attribution).
3. Window-weight derivation for weighted-average shares (founder adopted; supporting comparison was against yfinance, a comparator; approximation accuracy quoted from code comments).
4. Restated-basis policy (latest-filed as restated) and whether derivation may use conflict-filled values.
5. Bank, insurance, REIT, biotech templates and their metrics.
6. Split/restatement treatment for new share-count concepts.
7. Any claim that a line is "proven absent" for an economic reason rather than a presentation reason.
If no human is available: keep these out of published metrics and show sourced as-reported data where safe (pack rule).

---

## G. Founder decisions (only the founder can make)

1. Headline KPI: UNKNOWN/applicable (with the three-state split) instead of coverage %. (Recommend yes.)
2. Population: whether FPI-only and no-10-K filers are excluded from the operating denominator, and whether to report both.
3. Whether derivation may use conflict-filled values within the 15% bar, or conflicts are resolved upstream first (this plan assumes upstream first).
4. Name or hire the accounting reviewer (person or firm) and adopt the release policy in section D, or state that batches stay proposal-only.
5. Targets (doc 56 section 4) after the baseline exists; freshness SLA; acceptable wrong-value ceiling.
6. FSDS ingestion approval (3 fiscal years first, with a size pilot) and any DB-size/budget limit (46 GB today).
7. Template scope for W3 (suggested: Industrial, Bank/Insurance, REIT, Pre-revenue biotech) and which sectors the product promises at launch.
8. Budget for model calls and Verifier time (no telemetry exists; caps instead of dollars).
Team can decide itself: ordering inside a milestone, sample stratification, code design of the conflict fix within decisions.md, queue organization, which family to run each week, thresholds for non-critical findings.

---

## H. First two weeks by role (10 working days; "d" = day)

Chief
- d1: write task.json for A and B; ListAgents; claim the migration number in doc 53 if the schema is needed. d2: reconcile baseline; publish the baseline. d3: draft the founder packet (G1-G4). d4: review the metric-input map; decide which concept families matter by metric reach, not tag count. d5: weekly report 1. d6-d8: rank B results; hold or release B1. d9: choose C family 1; d10: report 2.
Data Triage
- d1: baseline queries with watermark. d2: three-state ledger design. d3: population cleanup counts (FPI, no-10-K). d4-d5: findings -> root-cause groups; publish denominator ledger. d6-d7: `metric_definition_input` inventory. d8-d10: re-measure after each nightly snapshot; update the ledger.
Data Engineer
- d1-d2: diagnose snapshot stop and gap_reason (annotations, per-stage timings). d3: fix or document. d4-d5: B1 code on a branch, tests, mutation check, test it the way CI invokes it. d6-d7: check `weighted-average reprocess` plan, ListAgents, run on a company subset first. d8: subset rollback exercise. d9-d10: full reprocess if load allows; `yfinance_statement_line` bloat note stays queued (not this fortnight).
Period Engineer
- d1: contact Lane F (scrooner-2b). d2-d4: full-population Q4 census in company chunks (set statement_timeout, backgrounded). d5: classes + same-vintage pairing rule. d6-d7: label-error detectors dry-run. d8-d10: dry-run table of clean additive candidates (no writes) for Verifier.
Tag Mapper
- d1-d3: C1 families' coexistence queries on the full population (read-only). d4-d5: counterexample lists with accession locators this time (the first round gave none). d6-d10: finish families 1-4 of the Wave-1a list; remaining 14 of 24 lines queued by weighted reach after A4.
Standardization Lead
- d1-d3: finalize combined-line policy text and the C1 definitions with the Verifier's counterexample reads. d4-d5: dispositions for diluted_eps p3 / net_income p3 as a question to the reviewer. d6-d10: definitions for next families; read `resolve.py` (blocker B6) and run the consumer inventory with Triage.
Data Verifier
- d1-d3: build the fixed regression set (golden-10 + banks + REITs) with source locators. d4-d5: the 39 rows plus 12 fresh cells for B1. d6-d8: counterexample issuers for C1 families. d9-d10: Q4 dry-run candidates (25 cells). SEC requests sequential, one process.
Sector Analyst
- d1-d5: bank cohort selection (SIC), read 10 original statements, list lines; d6-d10: draft template and metric matrix (proposal). No applicability edits to the denominator yet.

Weekend of week 1: nothing heavy unattended; nightly watch only.

---

## I. What NOT to do

- Do not map all tags; do not map any tag from a single company's evidence (decisions.md).
- Do not add a concept without a full-population coexistence check; 5-row samples are not evidence.
- Do not map combined lines as plain lines; do not apply held fallbacks.
- Do not subtract EPS or share counts to derive quarters; do not fall back to non-authoritative inputs in derivation.
- Do not shrink denominators to improve a percentage; do not report average-of-averages as coverage.
- Do not publish a "% correct" from a sample; do not claim 99%.
- Do not treat yfinance, Frames or FDIC as stored-value sources.
- Do not run a heavy job without ListAgents, a statement_timeout plan, and a rollback; do not run two SEC fetch processes.
- Do not touch `apps/app` or screener code; do not edit shared coverage modules without telling the lane owner.
- Do not count a zero-row update as a fix, or a cycle as progress because messages returned.
- Do not change the DB schema outside a committed migration; do not `git add -A`.
- Do not claim staging, human review, or cost figures that do not exist.

---

## J. Status ledger

| Item | State |
|---|---|
| This plan | proposed (file only) |
| Release policy D | draft, not adopted |
| All live numbers | quoted, NOT_RUN here |
| Code changes | none; B1-B3 not implemented |
| Wave-1a families | proposed by Tag Mapper/Standardization Lead; nothing applied to `concept_mapping` |
