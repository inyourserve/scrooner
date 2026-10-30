# 48. Data head review of the master plan (docs 46/47): theme coverage, data critical path, one-time-solution test, risks, sign-off (Data Chief, 2026-10-22)

Role: Data Chief (data-team/10), acting as data head in the three-head plan finalization (product head Ritwik, data head, engineering head scrooner-4d). Objective: verify Ritwik's theme mapping independently, lay out the data-side critical path, test the plan for anything that would force a redo, and sign or set conditions. Scope: planning only. No code, no commits, no DB writes, Ritwik's files not edited. Numbering note: `48-HANDOVER-TO-DHAIRYA-...` already exists in this folder; this file is a separate 48.
Evidence labels: FILING-CHECKED (FC, inherited from the cited report; I opened no filing), DATA-INFERRED (DI), CODE-READ (what our code does or does not contain), MEASURED (my live read-only query today), ASSUMED.

## 0. Commands actually run and what they showed
- Read: data-team/20, 21, 22, 10, 33, 34, 36 (precision sections), 37; strategy/40-ROOT-CAUSE-GATE, 41-TEMPLATE, 42, 43, 44, 45, 46, 47, 48-HANDOVER; team/R5, R6 (backlog, kill criteria), R8, S1, S2, S3 (sections 0-1, 4-11), S4, S5; ALL-SHARDS-ROOT-CAUSES.md (all 461 lines); doc/data-moat/team/PLAN.md; doc 53 migration ledger lines.
- `git log` on `certification/`, `mapper/coverage_matrix.py`, `expanded_metrics.py`/`ttm.py`/`normalizer/derived.py`; `git status`; `git diff --stat -- pipeline/src` (17 files, +2,540/-393 uncommitted, incl. all of `certification/`, `concept_fallback.py` total-debt guards R1/R5, `derived.py` per-share no-derive).
- `grep -rln` for the revenue-total guard (`revenue_total_undecidable`, `two_totals`, "contract-revenue subtotal") in `pipeline/`, `apps/backend`, `data-team/strategy/tools`: **no match**. CODE-READ: the revenue-total disagreement guard that doc 47 W12 and WO-9 call "held, already built" does not exist in code; data-team/37 is a design and a 30-case test plan.
- Two read-only queries (one connection, `statement_timeout` 20s, read-only transaction; 11 client backends at start). MEASURED 2026-10-22: `analytics.certification_finding` and `company_certification` do not exist and `has_value_any_period` does not exist, so **0096 and 0097 are still not applied**; `company_data_point_coverage` was rebuilt 2026-10-21 18:31 UTC, **after** doc 44's measured baseline (build 2026-10-20 18:52), so doc 44's numbers are one rebuild stale; `max(snapshot_date)` in `coverage_snapshot` = 2026-10-21; database 47 GB (plans say 46).
- `python3 mind/mind.py search` (one query; no hit changed anything here).
- NOT_RUN: any filing fetch, any heavy query, any re-count of doc 44/46 numbers.

## 1. Theme coverage: independent mapping of the 28 shard themes to doc 47 work orders
Method: each theme's mechanism and exemplars in ALL-SHARDS-ROOT-CAUSES.md section 3 matched against the numbered items in doc 47 section 4 (not doc 46's backlog: doc 47 is what the teams execute). "Owner" = a WO item that builds the fix (a Verifier sample alone is not an owner). "Acceptance" = a stated pass/fail test.

| Theme | Doc 47 items that address it | Owner | Acceptance test | My verdict (Ritwik's) | What is missing |
|---|---|---|---|---|---|
| T1 revenue partial/sub-line (about 109 FC) | WO-9 release "revenue-total guard"; WO-6 sample; WO-3.2 structure report; WO-5.1 bank/insurer revenue | **none for the guard** | none in 47 (data-team/37 section 8 has one) | PARTLY (partly) | Guard is not built (CODE-READ above). Builder needed (Data Engineer). Adopt 37 section 8 (30 cases, 30 of 30) as acceptance. The per-company structural rule on the 201-206 companies needs a WO item. Insurers (MET 724M vs 19,154M) are not under any suppression today |
| T2 operating income derived / non-face (about 44 FC wrong) | WO-5.1 (EBITDA when no OI line) only | **none** | none | UNOWNED (partly) | No guard for the existing Revenue minus `OperatingExpenses` fallback (168 companies, S023) whose own code comment admits 10-15% misses (PLAN.md 2026-10-18); segment-note OI read as consolidated (MET, HONA, MOG-A); pretax-labelled OI (AFG, ELS, ledger). Live wrong values; belongs in Tier 0 |
| T3 zero-fact latest filing / filing absent | WO-1.8 detector + reader with 50-filing match | Data Engineer | reader: 100% on 50 filings; detector: none (doc 48 K12 is a target, not a test) | PARTLY (covered) | "Filing row never registered" (HPQ, MDB, JKHY, IREN, HEI, SJM, OLLI, DG, DE) is a collector/index gap, not a companyfacts lag: add a submissions-vs-`core.filing` detector |
| T4 shares, market-cap basis, per-share cascade | WO-1.7 cover-date anchor; WO-2.2 pairing rule; WO-1.9 scale checks (detection) | partly | AAPL 7.36 (anchor only) | PARTLY (partly) | **Market-cap publish guard (33 M) has no owner**: AKTX $1.27T, TBLA $999B, SPCX understated are live. Multi-class cover sum and ADS ratio (33 M R1/R2) unowned. WO-1.7 and WO-2.2 are two fixes for one defect (see section 3) |
| T5 stale series counted as filled | WO-2.1 W2 (TTM age only) | partly | Verifier AAL | PARTLY (partly) | `_resolved` concepts ignoring the latest-period rule (S065) and non-TTM staleness: no owner. K7 re-measure after 9e77357: no owner |
| T6 true zero blank; total_debt | WO-9 debt guard (built, held: CODE-READ `concept_fallback.py` R1/R5); WO-3.1 vocabulary; WO-5.1 C1 | yes | WO-6 30-filing sample | COVERED (covered) | Evidenced-zero (Z) detector for debt/dividends/buybacks (S3 2.1, Lane B "extend filing-line evidence to cash-flow rows") has no WO item; WO-4.3 covers `not_presented` only |
| T7 wrong or missing reasons | WO-4.4 (W9 only); WO-1.5 `cell_state` | partly | reasonless = 0 | PARTLY (covered) | The financial-institution reason on 142 non-financials, the REIT-interest reason on 189 equity REITs, `no_dividend_history` at 502 payers (33 Q) are not named. If `cell_state` inherits today's reason rules, wrong reasons survive with a code. Needs "every reason rule gated on the company's own facts; zero contradicted reasons in the cohort" |
| T8 negative / meaningless ratios (W6/W7) | WO-6.2 sample only | **none** | RDDT/PFE sample | UNOWNED builder (covered) | Neither W6 nor W7 is in WO-1 or WO-2. Builder: Data Engineer (`ttm._growth_value`, `price_metrics`, `expanded_metrics`, `ratio.py`). S3 items 1 and 3 make the final wording an accountant call; the interim NM state is a guard and needs none |
| T9 fiscal labels | WO-2.1 W5 (24 companies) | Period Engineer | none | PARTLY (covered) | Shards show 224 companies / 322 duplicate-label groups since 2024 (S022) and 35-38 January-window cases; 24 is the cohort TTM-blocking subset. Acceptance: label derived from FY start/end equals SEC `fy`/`fp` for every cohort period since 2015 |
| T10 recast / restated / missing quarters | WO-2.4 restatement basis, W4 | Period Engineer | HON sample | PARTLY (partly) | **Split table** (NVDA about 216 cells, GOOG double entry, WMT double adjust, AAPL shares; data-team/36) has no WO item though Gate B requires NVDA fixed. **Matching copies treated as conflicts** (33 F: ANET whole balance sheet, 82 tag-periods in S006) has no WO item |
| T11 net income basis, equity incl. NCI | WO-5.1 attributable; WO-1.4 authority gate (DEF 14A) | partly | none | PARTLY (partly) | The definition-free guard (33 I: suppress where source is `ProfitLoss` and non-zero NCI exists for the context) is not in Tier 0. FCX TTM about 42% high is live |
| T12 capex, D&A, interest, AR tags | WO-3.1, 3.3 | Tag Mapper | coexistence + zero-wrong sample | COVERED (covered) | Release-tier problem, see section 2.4 |
| E1 institutional-ownership overcount | none (47 section 6 defers ownership) | **none** | none | UNOWNED (added) | Doc 46 added it to Tier 2; doc 47 dropped it. Cell is honestly blank, so not a trust emergency, but it is an unowned theme |
| E2 scale/unit errors | WO-1.9 certify check (detection) | detection only | none | PARTLY (partly) | Fixes for found cases unowned: MOS DPS 220,000 / yield 12,246 (live), CHE NI 249,624 dollars, PLXS negative revenue, `EntityPublicFloat` x1000. Needs a Tier 0 publish guard |
| E3 EPS per class / non-standard EPS tag | none | **none** | none | UNOWNED (partly) | `IncomeLossFromContinuingOperationsPerDilutedShare` (ABNB, HXL), per-class EPS (V, BRK, GOOGL) not in WO-3 |
| E4 dividends / DPS | WO-3.1, WO-5.1 DPS policy, WO-2.3 never derive DPS | yes | Visa FY DPS in Gate B | COVERED (covered) | none beyond the `PaymentsOfOrdinaryDividends` coexistence already listed |
| E5 MLP/LP tags | WO-4.2 midstream variant (template only) | **none for vocabulary** | none | UNOWNED (added) | `PartnersCapital*`, `DistributionMadeToLimitedPartner*` not in WO-3 |
| E6 multi-registrant filings | WO-1.3 | Data Engineer | Entergy Arkansas check on 0000065984-26-000174 | COVERED (added) | none |
| E7 identity defects | WO-1.2 | Data Engineer | zero CIK/name/ticker disagreements or each logged | COVERED (added) | none |
| E8 10-KT transition filings | none | **none** | none | UNOWNED (added) | Zero 10-KT rows in `core.filing` (S027); FERG. Doc 46 put it in Tier 2; doc 47 dropped it. Collector form allowlist + R5 rule B4 TRANSITION_PERIOD |
| E9 predecessor / successor / IPO history | WO-2.5 | Period Engineer + Company Master | none stated | COVERED (covered) | Acceptance: each link FILING-CHECKED (8-K12B/G3 or 10-K predecessor statement) |
| E10 population / scope | WO-13 founder confirmations; WO-4.1 exclusions | partly | none | PARTLY (partly) | Status scan for Form 25/15 and 20-F/40-F (33 P: WBD still `active` at $77.8B, NUTR, BMO, BNS, AEM, CNI, IAU, SLV) has no builder |
| E11 sector templates | WO-4 | Sector Analyst | zero wrong in 30 per group | COVERED (covered) | Bank NII extraction (USB R4) sits in WO-3.1: fine |
| E12 gross margin from a partial cost line | none | **none** | none | UNOWNED (added) | Doc 46 added the 33 N guard to Tier 0; doc 47 has no item. UNH 88.6%, ELV 89.1%, CVX 43.6% gross margins are live |
| E13 Q4/TTM, YTD cash flow | WO-2.1-2.3 | Period Engineer | MasTec | COVERED (covered) | Calendar-aware windows must land with W1 (section 3) |
| E14 face line present, concept blank | WO-3.1 | Tag Mapper | per mapping | COVERED (covered) | Derived total liabilities (about 25 companies) is a calculated value: needs a Standardization rule |
| E15 reporting currency | WO-1.9 certify check (detection) | detection only | none | PARTLY (added) | Serve-time suppression of price ratios for non-USD reporters (33 R: CP, IMO) unowned |
| E16 provenance | WO-10.2 "why this number"; WO-1.4 authority | partly | screenshot | PARTLY (covered) | Market cap with NULL `source_fact_ids` (META, ABNB, NET, CME, DDOG, V) has no fix owner; the panel cannot show a lineage that does not exist |

Tally (my mapping, 28 themes): covered 9 (T6, T12, E4, E6, E7, E9, E11, E13, E14); partly 12 (T1, T3, T4, T5, T7, T9, T10, T11, E2, E10, E15, E16); unowned 7 (T2, T8 builder, E1, E3, E5, E8, E12).
Main disagreement with doc 46 section 8: four of its seven "added" themes (E1, E5, E8, E12) and two of its "partly, ADD x" items (T2 guard, T4 market-cap guard) never reached doc 47's work orders; W6/W7/W8 have a Verifier sample but no builder; W12's revenue guard is counted as built when it is a design.
Work orders without an acceptance test: WO-7, WO-8, WO-1 items 6, 9, 10, WO-3.2-3.3, WO-4.2, WO-5.2.

## 2. Data-side critical path (WO-2 to WO-8, with the WO-1/WO-9 dependencies they cannot avoid)

### 2.1 The two serialized resources that set the real calendar
1. **Heavy DB slot** (`heavy-db-jobs`, one at a time, never during D1/D2 or the nightly window): applying 0096/0097 plus the coverage rebuild; the 986 certify dry-run (about 1.5 h); every cohort recompute/reprocess that makes a mapper or normalizer change live; full-population coexistence scans. Serve-time guards (the `sector_applicability` pattern) need NO heavy slot, only a light dry-run: that is the main parallelism lever for Tier 0.
2. **SEC fetch slot** (infra map rule 6: one SEC fetch process at a time, about 10 req/s aggregate). The Verifier (about 30 filings per family and per group audit), the Sector Analyst (660 unopened corporates plus captive finance) and Gate D headline checks (100 companies x FY + quarter) all draw on it. The plan treats them as parallel; under the rule they are not. Unblock request (Dhairya, not the founder): either one shared fetch queue with an explicit priority order, or relax to at most 3 processes with an aggregate cap of 5 req/s.
3. A third, softer queue: the Release Manager (one session, commits only named paths) and the 2,540-line uncommitted `certification/` and guard diff that must be reviewed before anything depending on it ships.

### 2.2 Sequence and dependencies
| Step | Days (ASSUMED) | Work | Needs before | Hands off |
|---|---|---|---|---|
| A0 | 0-1 | Founder: accept plan, approve state enum and "Not disclosed", internal-row removal, name the accountant. Chief: freeze register (section 3.0), slot calendar, traceability fixes to doc 47 (Ritwik edits) | none | frozen enum + rule-ID scheme to every builder |
| A1 | 0-1 | RM: review and commit `certification/` diff and the held total-debt and per-share guards (tests rerun, ruff, CI mypy) | founder accept | committed code to DE |
| A2 | 1-2, heavy | DE: apply 0096/0097, coverage rebuild, certify dry-run on the 986 (one connection) | A1, quiet window from scrooner-4d | findings table to Verifier and Triage |
| A3 | 1-3, light DB + SEC | Read-only Tier 0 hit lists (W1, W2, W3, W6, W7, W8, W10, T2, T4 market cap, E12, E2, E15, T11 guard); Verifier precision AND recall per invariant on the 986 output (30 flagged + 30 passed each) | A2 for precision; none for hit lists | per-family hit lists + precision to Chief |
| A4 | 3 | Gate A: Triage reconciles measured vs doc 46; Chief re-ranks on a one-third deviation | A2, A3 | ranked Tier 0 batch |
| B1 | 3-8, no heavy | Serve-time guards in one rule registry: total debt, revenue-total (build), market cap, gross margin, OI derived-not-face, NM states (W6/W7), currency, scale, ProfitLoss+NCI; each dry-run, Verifier 30, RM commit | A4, rule registry | live guards; hidden-by-mistake counts to Triage |
| B2 | 4-9, then ONE heavy | Mapper/normalizer Tier 0 changes batched into one release train: W1+W2 (date-based windows), TSY $0 default, W3 authority gate, W10 single anchor fix, split table, id 1840, registrant gate; each family dry-run + Verifier separately, one cohort recompute, per-family rollback flag | A4; split-table filing checks (SEC slot) | recomputed metrics; certify re-run |
| B3 | 10 | Gate B: every W item and every FC wrong value on the regression list (section 6) corrected or hidden with a reason | B1, B2 | |
| C1 | 8-15, migration | DE: `company_group`, `metric_template`, `cell_state`, durable evidence table (claim 0098+ in doc 53; design review first); Sector Analyst audits; groups v2 frozen for corporate, bank, insurer, REIT | WO-4 audits (SEC slot); founder metric sets | Triage scoreboard v1 |
| C2 | 12-15, heavy | Pass-through reasons in the metric engine (594 + 285 cells), reason-rule audit, sector-only row gating; one recompute | C1 | K2 = 0 |
| D | 15-45 | Tier 2 one family at a time (vocabulary scans are heavy; normalizer derivation needs reprocess); feed reader; successor links; T1 headline verification | C; accountant for composition items | T1 certified non-financials |
| D-acct | from day 1 | Accountant packet: S3 section 7 (13 items), R3 5.9, C1, C4, bank/insurer/REIT revenue, restatement basis (S3 item 13) | accountant named | approved definitions with fixtures |
What runs in parallel under the one-connection and heavy-jobs rules: everything in A0/A1, A3's hit lists (light, index-backed, chunked by company ids, 60s) beside A2's heavy job, B1 beside B2's build work, Sector Analyst filing reads beside any DB work (but not beside other SEC fetchers), Standardization/accountant work at any time. Never in parallel: A2 with any other heavy job; two recomputes; a coexistence scan with a recompute.

### 2.3 What each data hand-off must carry
- WO-2 Period Engineer -> Verifier: dry-run table (company, concept, period, old, new, input fact ids incl. the 9M fact, formula id), negative fixtures (12/12/12/16, 53-week, transition, stub), MasTec/AAL/HON cases first.
- WO-3 Tag Mapper -> Standardization Lead -> Verifier: decision.json with full-population coexistence counts, overlap-year equality per company (section 2.4), counterexamples, era range; never a 5-row sample.
- WO-4 Sector Analyst -> Data Engineer: group per company with effective dates and evidence accession; audit log (30 per group, zero wrong); list of moved companies.
- WO-5 Standardization -> accountant -> Data Engineer: definition with version, FC fixture set, alternatives; nothing reaches code without the accountant mark.
- WO-6 Verifier -> Chief/RM: per-decision verdicts, wrong rows AND correct-but-hidden rows, locators; never a blanket pass.
- WO-7 Triage -> Chief/Dhairya: scoreboard with query text and watermark (`max(checked_at)`, `max(snapshot_date)`), both denominators, hidden-by-guard count.
- WO-8 Chief -> Dhairya: ranked batch (at most 10 families, 50 cases), unblock requests, failure-test results.

### 2.4 Where the accountant blocks, and where the plan says he does not but he does
- Blocks as planned: Tier 3 (EBITDA without OI line, D&A/capex composition, C1 finance leases, C4 capitalized software, DPS policy, NI attributable, bank/REIT/insurer revenue and capex, S3 section 7).
- **Also blocks, not stated in 46/47:** (a) Tier 2 vocabulary that adds a second tag to a concept is a "fallback across tags", which PLAN.md release tiers (line 29) make proposal-only until an accountant approves. Unblock: the founder adopts one narrow eligible class now: "company-scoped tag switch where the filer's own face row carries the same value in the overlap year (each 10-K repeats 2-3 years), no coexisting component tag for the same context, coexistence checked population-wide". That covers the 2024 `InterestExpenseNonoperating` switch and `PaymentsToAcquireOtherPropertyPlantAndEquipment` (LLY) without a perimeter call; multi-line sums stay accountant-gated. (b) Gate D "T1 certified" for financials: bank, insurer and REIT REPLACED cells are defects until approved, so the roughly 15-20 financials in the top 100 cannot certify without the accountant. Doc 48's default ("T1 certification excludes those cells") contradicts the certified definition (every template cell non-defect). State Gate D as "T1 non-financials certified; financials certified only if the accountant has ruled".
- Does not block: every Tier 0 guard (blank-with-reason only), W1/W2/W3/W5/W10, cell_state, group audits, ingestion, identity, registrant gate.

## 3. One-time-solution test

### 3.0 Freeze register (decided once at Gate A; a change after it is a versioned event with a diff, never an edit)
State enum (doc 47 section 1 list) and wording keys; rule-ID scheme `family.rule@version` that every guard, reason and state cites; denominators D0 = fixed all-cells 160,718 for the 986 (never changes) and D1 = template cells per `template_version`; group enum; cell key = (company, period, data_point) from day one, computed for the latest period first and 2015+ next (building latest-only and then re-keying for history is a redo); `cell_state` is a rebuildable derived table, and Verifier evidence (accession, locator, rule version) lives in a separate durable table that a rebuild never deletes (the recurring shared-table delete-scope bug, pipeline/CLAUDE.md).

| Tier | What would force a redo | Control that prevents it |
|---|---|---|
| 0 trust | Guards emit free-text reasons, then `cell_state` replaces them (reasons rewritten twice) | Guards emit the frozen enum + rule ID from the first release |
| 0 | Tier 0 adds more hard-coded suppression lists, then Tier 1 replaces them with `metric_template` (code rebuilt) | One rule registry keyed by (group, data_point, rule) used by serve-time guards now; Tier 1 migrates rows, not code |
| 0 | W1 TTM fixed on fiscal labels, then W5 relabels periods and the TTM windows move | W1 uses date-based contiguous windows (S5 B8, R5 B3); labels then matter only for display |
| 0 | W10 fixed twice: WO-1.7 "latest non-null row" display fallback, then WO-2.2 pairing rule | Choose one before build: anchor per-share balance-sheet metrics on the balance-sheet date with a stated share-date rule. Reject "latest non-null" (it can surface an older row and fights the staleness guard) |
| 0 | NM wording for growth over a negative base, then the accountant prefers an absolute-change measure | NM is a state, not a value; an accountant ruling adds a new metric version, nothing is backfilled |
| 0 | Guard thresholds tuned after the Verifier sample | Threshold is part of the rule version; a change re-runs the dry-run and the sample |
| 1 classify | Coverage claims made on D1, then the 29 `_resolved` twins and internal rows are removed, then groups move (114 moved; 660 corporates unopened) | Report D0 always; D1 claims only after the group audit, with `template_version`; any version change publishes a reconciliation of old vs new |
| 1 | `cell_state` assigns not_presented / evidenced_zero from "no mapped tag" (S4: 28% of reasonless blanks are present-not-captured) | No state other than defect without tag-agnostic filing evidence or an audited detector (30 per group, zero false); detector version tied to its audit |
| 1 | Group membership wrong (captive finance untested; BDC rule was broken) | Effective-dated `company_group` with evidence; K4; quarterly re-audit; `cell_state` recomputed by code so a move is cheap |
| 1 | Founder rejects the state model after backfill | Approval of the enum is an A0 exit criterion |
| 2 capture | A mapping regresses for new periods (AMT per-period pin; WMT incremental resolve differs from full) | Company-level preferences apply to future periods; invariant "incremental resolve = full resolve" as a test; nightly incremental certify reopens the company; every FC case becomes a regression fixture |
| 2 | Multi-line compositions shipped, then the accountant chooses another perimeter (D&A, capex, debt with leases) | Composition items wait for the accountant; only overlap-year-proven synonyms ship (section 2.4) |
| 2 | Q4 derivation shipped before same-vintage pairing (HON 58M) | Allowlist, B1 same vintage and B2 discontinued-ops guard ship in one release |
| 2 | Revenue fixed by another precedence tweak, then the structure rule (doc 37) chooses differently | T1 gets the guard now and the structure rule as the only real fix; no interim precedence change |
| 2 | Fallback reader values differ from companyfacts | 50-filing 100% match before use; source recorded in lineage |
| 3 definitions | A definition changes after backfill (finance leases, NI attributable) | `definition_version` on concept and template; reported and standardized values stored separately (R3); affected cells stay suppressed until approval, never published on a provisional definition; recompute is a code rerun |
| 4 certification | Certify suite changes (precision demotion, new I12/I13) after companies are certified | Certification state carries suite version and date; any suite change re-certifies the cohort; badge shows version and date |
| 4 | Precision measured on 20 megacaps only (data-team/36: S001/S002, 850 findings, 95.5%) and recall unknown | K11 re-measured on the 986 run, per invariant, precision and recall, before any invariant gates certification |
Rollback for every tier: additive migrations; per-family rule flag; delete-then-insert writes scoped by (company, concept, status); first live run separate from the code commit.

## 4. Biggest risks, each with a test
| # | Risk | Test (weekly unless stated) |
|---|---|---|
| R8-1 | Denominator theatre | Value-filled CORRECT cells on D0 must rise. Amended: Tier 0 hides about 750+ known-wrong values and guards may hide thousands more (revenue guard reach is up to 1,556 companies with both tags, S047), so total value-filled can fall; report valued, hidden-by-guard and FC-wrong-removed separately and judge the first, not the total |
| R8-2 | Building on projections and an unproven instrument | Gate A by day 3 with precision AND recall per invariant on the 986; else stop new builds |
| R8-3 | Infrastructure before visible fixes | By day 10 every FC wrong value on the regression list (section 6) fixed or hidden |
| 4 | Two serialized resources make the dates fiction | Day 2: slot calendar listing every heavy job and SEC-fetch batch to Gate D; if demand exceeds available windows, re-baseline dates before claiming them |
| 5 | Unowned live wrong values (T2, T4 market cap, E12, E2 MOS) survive Gate B because they are not W items | Gate B checklist built by Triage from ALL-SHARDS FC exemplars plus data-team/36, not from W1-W12 alone |
| 6 | Data Engineer overload (WO-1 has 10 items; section 6 adds about 10) | Count open DE items per week; if more than 5 are on the critical path, move serve-time guards or mapper items to a second lane (Period Engineer or a second engineer session) |
| 7 | Verifier capacity and independence | Opens per week vs plan; no family verified by the agent that proposed or tuned it (the certify precision study and S4 were both Verifier-authored) |
| 8 | A guard hides correct values | Hidden-by-mistake count in every 30-sample; any non-zero fixes the guard before the next family |
| 9 | Accountant never named | Day 10 check; if unnamed, Gate D restated as non-financial T1 and Tier 2 limited to the synonym class |
| 10 | Large uncommitted diff in a shared tree is committed half-reviewed or lost | RM commits `certification/` alone with tests before any guard; `git log origin/main..HEAD` empty after each push |
| 11 | Session usage limits or DB restarts during heavy writes leave partial state | Every write idempotent and resumable from a log; a forced kill test on the dry-run path |
| 12 | Population reach far beyond the sample (30 filings validate a rule touching thousands) | Full-population dry-run diff reviewed, stratified sample by group and era, not a uniform 30 |

## 5. Projection vs measurement, and what to re-measure after Tier 0
MEASURED (live queries; still subject to the watermark): 160,718 cells / 123,326 valued / 37,392 blank / 13,349 reasonless (doc 44, build 2026-10-20; the table has since been rebuilt, so re-run); period_gap causes; 89 zero-fact filings; S4 mechanism (9,564 concept cells with zero canonical rows, 3,723 metric cells with zero rows, 62 ownership); S1 14,992 cascade cells reproduced; W-register counts from replicas on our tables (W1 47/159 and 62/99, W2 81/61/30, W3 229 rows, W5 24, W10 1,427/718, W6 123+122, W7 117/24/36) are DATA-INFERRED but exact counts.
PROJECTED from samples or models: the 55% / 38% / 4% roll-up and "about 14,300 defects / 20,500 evidenced" (doc 46, model on S4's n=40 with intervals of about 14 points); U0 destinations 4,400 / 4,200 / 3,700; +5,441 cells and the 80.1% fill (S1 upper bound); the 85-86% ceiling; group sizes beyond the 258 opened; certify precision 95.5% (20 companies); "750+ wrong values removed" (sum of DI counts); total-debt 10-15% headline wrong (estimate); Item 302 filed Q4 at 75% (FSDS); Verifier 400-500 opens; storage 0.35/1.3 GB; every duration.
Re-measure after Tier 0 (before Gate C targets are believed): K1 on D0 split into valued / hidden-by-guard (doc 48's Gate C target of 77.6% assumes +1,427 from W10 and ignores the cells Tier 0 hides); K2 reasonless (guards change reasons); K7 stale-as-current after 9e77357 (the 78% is pre-guard); the S1 cascade split (W10 removes 1,503 engine cells); class shares from `cell_state` v0 replacing S4's model; certify precision and recall on the 986; group counts after the 660-corporate review; the unresolved count contradictions in ALL-SHARDS section 5 (683 companies vs cells, 3,433 companies vs cells, 497 vs 477 shares) before any of them is quoted.

## 6. WO-8 (Data Chief), rewritten, and changes to the other work orders
WO-8 Data Chief (owner: me; accountable: Dhairya):
1. A0: freeze register (section 3.0) to the founder with decisions 1-4; acceptance: approved enum, rule-ID scheme, D0/D1, cell key, evidence-table rule in writing.
2. Day 2: slot calendar (heavy DB, SEC fetch, RM queue) with scrooner-4d; acceptance: every Gate B/C job has a window.
3. Traceability matrix (section 1) kept current: 28 of 28 themes with an owner and an acceptance test by Gate A exit; plus the Gate B regression list (every FC wrong value in ALL-SHARDS and data-team/36, one row per company-cell, owner, state).
4. Weekly ranking under the cap (10 families, 50 cases); reconcile the last batch before choosing the next; release-train composition for each heavy window.
5. Failure tests (section 4) every Friday with doc 48 section 2.5 integrity checks; red result stops new builds and goes in the founder one-pager.
6. Re-baseline after Tier 0 and at each gate (section 5 list); one-third rule.
7. Verifier independence assignment; lane and migration-number arbitration (doc 53).
8. Daily note: shipped, blocked, next, unblock request.
Changes to the others (for Ritwik to fold into doc 47; I have not edited it):
- WO-1 Data Engineer: add builders for T2 OI guard plus audit of the Revenue minus `OperatingExpenses` fallback; T4 market-cap publish guard (33 M R3/R4); E12 gross-margin guard (33 N); W6/W7 NM states; W8 remove the TSY $0 default; the revenue-total guard (data-team/37 section 4 guard part); T11 ProfitLoss+NCI guard; E2 scale and E15 currency publish guards; unindexed-filing detector; 10-KT collection; population status scan (Form 25/15, 20-F/40-F); `_resolved` latest-period rule; reason-rule audit (33 Q); market-cap lineage. Resolve item 7 to the single balance-sheet-date anchor. Item 5: rebuildable `cell_state` plus durable evidence table, keyed by period from day one. If this overloads one engineer, split serve-time guards into a second lane.
- WO-2 Period Engineer: add the split table (R8 rank 5; NVDA, GOOG, WMT, AAPL, TSLA; refresh not insert-only; Gate B depends on it) and matching-copies dedupe (33 F, decimals-interval test) jointly with the DE; date-based windows ship with W1; restatement basis waits on S3 item 13 (interim: block mixed basis); acceptance tests for items 2, 3, 5.
- WO-3 Tag Mapper: add E3 (continuing-ops and per-class EPS), E5 (partnership equity and distributions); split every item into "synonym class" (section 2.4) vs "composition" (accountant); revenue via the doc 37 structure rule, acceptance its section 8 (30 of 30).
- WO-4 Sector Analyst: add the evidenced-zero (Z) detector audit beside `not_presented`; E10 exclusions list; captive finance stays in item 1.
- WO-5 Standardization: list S3 section 7's 13 items and R3 5.9 with a requested ruling date; draft the synonym-class release rule for founder adoption; derived total liabilities rule (E14).
- WO-6 Verifier: precision and recall on the 986 run; independence rule; the Gate B regression list as the sample frame; SEC-slot priority order.
- WO-7 Triage: acceptance = reproducible scoreboard queries with watermark; first task reconcile the section 5 contradictions; classify the 1,076 unexamined cells with a second 40-cell draw.
- WO-9 Release Manager: commit `certification/` first; the revenue-total guard cannot be "released" until built.

## 7. Sign-off
**SIGNED WITH CONDITIONS.** The architecture (states, templates, rule families, one release path, certification) is right and is a one-time design; the execution layer has gaps that would force rework or leave live wrong values. Conditions, each to be met before Gate A exits:
1. The 7 unowned themes (T2, T8 builder, E1, E3, E5, E8, E12) and the missing pieces of the 12 partly-covered ones get an owner and an acceptance test in doc 47 (section 1 and 6 here).
2. W12 corrected: the revenue-total guard is a build item, not a release item (CODE-READ, no code exists); data-team/37 section 8 is its acceptance.
3. The freeze register (section 3.0) is approved with the founder's state-model decision.
4. The accountant dependency is restated: the synonym-class release rule is adopted by the founder (or vocabulary fills wait for the accountant), and Gate D distinguishes non-financial from financial T1.
5. A slot calendar for the heavy DB slot and the SEC fetch slot exists before any gate date is quoted; dates re-baselined from it.
6. Failure test 1 is amended to judge value-filled correct cells, with hidden-by-guard reported separately.
7. W10 has one fix (balance-sheet-date anchor).
8. Certify precision and recall are measured per invariant on the 986 run before any invariant gates certification.
9. Verifier independence: no family is verified by its proposer or tuner.
Status of this review: COMPLETE for planning. Untested scope: I opened no filing; counts are inherited from the cited reports except the section 0 measurements; WO durations are not re-estimated; R1, R2, R3, R4, R7 were read only through their headings and the citations in other documents. Next action: Dhairya passes conditions 1-2 and 4-7 to Ritwik for doc 47 v2 and to scrooner-4d for the slot calendar; the founder gets conditions 3 and 4 with decisions 1-4.
