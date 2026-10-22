# WO-REVIEW: Data Engineer review of WO-1 and the added Data Engineer work (docs 47 v2, 49, WO-ADDENDA) before execution (2026-10-22)

Role: Data Engineer (data-team/15). Objective: review WO-1 and every Data Engineer item added since (doc 47 v2 A/B/E, WO-ADDENDA WO-14..WO-28, freeze register, Gate A checks, Period Engineer and Standardization Lead reviews) before anyone executes: is each item doable, what input is missing, how many days, in what order, in which lane, which migrations, which acceptance scripts, what would force a redo, and a sign-off. Scope: review only. No code, no DB writes, no commits, no database connection opened (every database figure below is quoted from a cited report, label DATA-INFERRED), no SEC fetch.

Evidence labels: CODE-READ (I read the file in the shared working tree or `git show origin/main` on 2026-10-22), FILING-CHECKED (inherited from the cited report; I opened no filing), DATA-INFERRED (cited report, not remeasured), ASSUMED (my estimate). Days are engineer-days for one careful engineer including unit tests, a scratch-schema SQL test, a mutation check, the dry-run, and one round of fixes after the Verifier sample. They exclude waiting for heavy slots, Verifier turnaround and founder decisions.

Read: data-team 20, 21, 22 (all 80+ rows), 15, 34, 36 (item 2 and counts), 37 (sections 4, 8), strategy 47, 49 (sections 2.1, 4, 7, 8), FREEZE-REGISTER, WO-ADDENDA, 48-ENGINEERING-HEAD (slot calendar), 48-DATA-HEAD, WO-REVIEW-period-engineer, WO-REVIEW-standardization-lead (NA-8), RULE-REGISTRY-DRAFT, DEFINITION-VERSIONING-SPEC (sections 1, 6, 9, 10), GATE-A-IDENTITY-REGISTRANT-CHECKS, R6; code: `normalizer/identity.py` 285-311, `normalizer/facts.py` 70-100, `normalizer/dedupe.py` 1-80, `normalizer/derived.py` (diff), `mapper/concept_fallback.py` (employee count, total debt), `mapper/price_metrics.py`, `certification/model.py`, `common/derivation_policy.py`, migrations 0003, 0004, 0042, 0097; `git show origin/main` for `pipeline-certify.yml`, 0097 and doc 53; `ls .github/workflows`, `git status`.

## 0. Findings that change the plan (each CODE-READ unless marked)

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| F1 | **Concept-level hides have nowhere to store a reason.** `analytics.canonical_fact.value` is `numeric not null`, so a guard that hides a concept cell can only delete the row, and the blank is then reasonless again. The held total-debt guard counts its blocked reasons only in the returned `stats["blocked"]` dict (`concept_fallback.py` 688-690) and the writer deletes then inserts valued rows only (702-707). Std Lead 0.2 is therefore a schema problem, not a code tweak. | migration 0004 `canonical_fact`; `concept_fallback.py` 616-720 | A reason store (`analytics.cell_blank_reason`, keyed by dates) must exist before ANY R2 guard that hides a concept (revenue, OI, cost of revenue, net income/NCI, DPS, total debt). It is the first migration (0100), not a Gate C item. |
| F2 | **The 0097 amendment must be wider than the regex.** Origin `0097` has `check (invariant in ('I1'..'I11'))`, no `rule` or `rule_version` column (the rule name lives only in `evidence->>'rule'`, `certification/runner.py` 105), and `company_certification` has no `suite_version` or run date. `certification/model.py` also hard-codes `INVARIANTS = ("I1".."I11")`. Data Head condition 3 (certification state carries suite version and date) and per-rule precision (A11) cannot be met on the current schema. | `git show origin/main:.../0097_certification_tables.sql` lines 19-20; `model.py` 15 | A4 becomes: regex `^I[0-9]+$` + `rule text`, `rule_version int` on `certification_finding` + `suite_version text`, `suite_run_at timestamptz` on `company_certification` + the Python tuple. Free now (unapplied), a migration plus backfill later. |
| F3 | **W3 reaches far more than 229 rows.** Stage 2e groups every fact of a company with no form filter (`dedupe.py` `_load_fact_rows`, no join condition on form); one rounded DEF 14A pay-versus-performance copy de-authorizes all precise 10-K copies of that period (data-team/36 item 2, JPM). The 229 are the canonical rows whose source is non-periodic today. The cells that change when non-periodic copies leave the group are every group that contains one (DEF 14A XBRL exists for most large filers since 2022). Also: certify's `PERIODIC_FORMS` includes 20-F/40-F, `common/derivation_policy.PERIODIC_FORMS_DOMESTIC` does not. | `dedupe.py` 55-70; `model.py` 20-33; `derivation_policy.py` 29-40 | W3 needs a population dry-run (class counts: replaced, conflict-to-authoritative, unchanged, non-null-to-null), not only the 229-row backup. One shared periodic-forms constant. The JPM Q4 12,691M case (ledger 2026-10-22; fact 340493 via the priority-3 to-common tag) is repaired only if Stage 2e ignores non-periodic rows including derived ones, then the affected cells are re-promoted; demoting alone is a no-op on an already non-authoritative row. |
| F4 | **P1 needs per-accession SEC reads and a new table.** Company Facts carries no registrant information, so the primary filer comes from the instance default-context `dei:EntityCentralIndexKey` (or R1.htm) and the first FILER block of the submission header. `core.filing.accession_number` is `unique` and the upsert never updates `company_id` (`identity.py` 296-306); `facts.py` loads filings "for this company only". A link table and a fact re-attribution path are needed; subsidiary payloads (EAI's 467 facts) are the only source of the parent's Q2 2026 10-Q, so the loader must attribute a payload fact to the primary filer, not the payload CIK. Candidate accessions can be found without fetching, from accessions present in two or more CIKs' stored submissions lists (ASSUMED retained in `raw.sec_submissions`). | `identity.py`, `facts.py`; GATE-A section 3 | New table in 0100; SEC fetch only for candidates (ASSUMED low thousands, one limiter, about 10-20 min); quarantine path reused for the Vivmark hold (founder item 16). |
| F5 | **`cell_state` needs a table with a run id, not a bare view.** The freeze register (section 2) requires a run id, an active-run pointer and rollback by repoint; a view cannot give a reproducible scoreboard, and recomputing the latest-period joins over 17.0M-row `canonical_fact` and 13.3M-row `metric_value` on every page load is not serveable inside the 2-minute pooler timeout (ASSUMED; the first task is a 20 s `explain` on a 100-company chunk). Latest-period only is small: 986 x 163 = 160,718 rows per run (about 40 MB, ASSUMED), so the 14 GB headroom is not at risk. Either way it is DDL and needs a committed migration ("no migration" in doc 49 section 4 is wrong). | doc 49 s4 Gate C; freeze register s2; versioning spec s1 sizes | Table + active view + defect-register view in migration 0102 (thin DDL early, engine later). |
| F6 | **Three definitions of "current quarter" exist** (price_metrics EPS-or-revenue anchor 287-299, each concept's own anchor in expanded metrics, `staleness.py` latest `period_of_report`). `cell_state`, W2 and RU-1 all need one. | Period Engineer review 1b, 3.2 | One function in `common/`, used by all; otherwise states flip when one definition changes (a redo trigger, section 4). |
| F7 | **Migration numbering and need-by order conflict.** Doc 53 (local, uncommitted) reserves 0100-0102 for DE and Std Lead and 0103 for the Period Engineer, and says 0103 cannot be committed before 0100-0102 exist. Origin's doc 53 still says "next free 0098" and has no claims. The versioning spec needs three migrations of its own, `cell_state`, `company_group`, `metric_template` need more, and the Period Engineer needs 0103 for its Q4 lineage. One number cannot hold all of that and the need-by dates differ by weeks. | doc 53 local vs `git show origin/main`; spec s9 | Section 2.4. |
| F8 | **The 399-line held-guard diff and other shared-file edits collide.** `concept_fallback.py` (held total-debt, plus reason persistence, D-4, OI, cost), `derived.py` (held), `ttm.py` (RU-1 pass-through, W6/W7 `_growth_value`, W1/W2), `expanded_metrics.py` (W1, W6/W7, `_ebitda_ttm`, OI), `price_metrics.py` (RU-1 anchor, market cap guard, currency, lineage), `dedupe.py` (W3 + WO-23). Three or four owners per file inside two weeks. | grep of writers; Period Engineer review | A merge order set by the Chief and committed through the Release Manager's temporary worktree (section 2.3). |
| F9 | **The revenue-total guard hides many correct values by design** (doc 37: 15 of 22 sampled displayed periods were right; reach up to 4,479 company-periods at 201 companies, NA-8). It is buildable from tag coexistence (Revenues / RCFC / RegulatedAndUnregulatedOperatingRevenue / RevenuesNetOfInterestExpense undimensioned in the same context, differing beyond the decimals interval), which does catch EMR and NTAP (a bare `Revenues` fact beside the face RCFC). The hidden-correct counter is part of the build. | NA-8 (WO-REVIEW-standardization-lead 74-85); doc 37 s8 | 5 days with the counter; acceptance 30 of 30 is evaluable from the stored tags for the cases in doc 37 s2 (needs the case table as a fixture file). |
| F10 | **T2 (WO-14) has a generic part and a named-case part.** Steps 1, 2 and 4 (fallback census, identity check, OI equal to pretax) are computable from stored concepts. Step 3 (segment-note OI read as consolidated: MET, HONA, MOG-A) needs statement-role evidence the tags do not give; until the structure source exists those three are company-scoped holds in `cell_evidence` with a rule ID, and generic recall for that mechanism is UNMEASURED. | WO-14 text; ledger 2026-10-21 AFG/ELS | AT-14.3 passes by named cases; the plan must not claim the mechanism is closed. |
| F11 | **D-4 side effect.** `resolve_employee_count_fallback` creates a `core.period` instant row dated `date.today()` for each yfinance fill (`_find_or_create_instant_period`, 977-1000). Turning the tier off removes the canonical rows but leaves today-dated periods in `core.period`. They are harmless to the latest-period rule (expected period comes from filings), but they must not be counted as periods in any history test. | `concept_fallback.py` 962-1076 | Add the exclusion to the cell_state and `period_completeness` tests; do not delete `core.period` rows. |
| F12 | **Certify workflow exists on origin only.** `pipeline-certify.yml` (2cfc569) is on `origin/main`, not in the local tree (local main is 94 commits behind). It loops every campaign shard in one job (150 min cap, 1,800 s per shard, dry run by default), not "4 shards"; fine, but A6 should read "exists; one dry run as CI invokes it". I12/I13 as designed in R6 need structure tables that do not exist, so they can only be registered, not implemented, in Tier 0. | `git show origin/main:.github/workflows/pipeline-certify.yml` | A6 closes by a dry-run log; I12/I13 are reserved IDs in the constraint. |
| F13 | **R6's migration numbers (0098-0100) are stale** against the ledger. The structure pilot adds no migration (AT-1.10a); any later structure tables take new numbers. | R6 s4 vs doc 53 | Note only. |

## 1. WO-1 item by item, then the added work

Doable: Y = yes as scoped, Y* = yes with the change shown, N = not as written. Lane = my recommendation (lane 1 = authority/identity/state, lane 2 = metric-stage guards/certify/ingestion). Where the addenda assigned an item to a different lane I say so; the reason is balance (section 2.1).

### 1.1 WO-1 items 1-10

| # | Item | Doable? | Inputs missing | Days | Lane |
|---|---|---|---|---|---|
| 1 | Apply 0096/0097, confirm matrix rebuild | Y* (scrooner-4d applies; I prepare) | Founder go told to scrooner-4d directly (A2); 0097 amended with F2 columns and committed with CI green (A4); four workflows green (A1); 0100 committed in the same window so S1 applies it too | 1.5 (amend 1.5 incl. tests; apply monitoring in A-items) | 2 |
| 2 | Identity master check | Y* (rewritten per GATE-A: do not rename id 1840) | Rule for `display_name` (SEC name wins when the vendor name matches neither the SEC name nor a former name); per-CIK submissions JSON is in `raw.sec_submissions` (ASSUMED, check first); Company Master module owner told; founder-free | 4.5 (invariant vs stored submissions 1.5; id 1840 display name + EQR ticker history + market-cap hold 1; AVB/WBD status with accession 0.5; PSKY name/ticker 0.5; EAI bond ticker and no market cap 0.5; audit table and reverse script 0.5) | 1 |
| 3 | Registrant gate -> shared-accession primary-filer rule P1 | Y* with F4 | Verifier A14 (Entergy mechanism) first; SEC slot for candidate headers; link table in 0100; decision that non-primary registrants get no values (Gate A 3e consequence 3); first live run reviewed dry-run | 8 (candidate detector from submissions overlap 1.5; header/R1 reader through the shared limiter with cache 1.5; loader rule in `identity.py`/`facts.py` + link table + fact re-attribution 2.5; quarantine path 0.5; reload dry-run + reload of 9 parents + Entergy 1; scratch tests and fixtures 1) | 1 |
| 4 | Authority gate W3 (+ Stage 2e ignores derived rows from non-periodic filings) | Y* with F3 | One periodic-forms constant (domestic, decided with the Period Engineer: 20-F/40-F out of V1); population dry-run slot; backup of the 229 ids under `doc/data-moat/team/backups/`; WTRG 8-K 0001193125-26-124163 and JPM facts 182608846/340478/340493 as fixtures | 5 (Stage 2e filter + derived non-periodic rule 2; population dry-run and class report 1.5; reset-and-repromote through the recompute workflow with `ciks` 1; tests 0.5) | 1 |
| 5 | `cell_state` job | Y* with F5/F6 | Machine-readable S3 rulebook (rule ID, data point, condition, evidence locator type, state, wording key, propagation P1-P10) from Std Lead; founder D-1 (enum); one `current_quarter()` from Period Engineer; audited detectors from Sector Analyst (for not_presented/evidenced_zero only) | 8 = first cut 4 (reasonless = 0: value / derived / defect with default class and owner, reason pass-through by graph) + full engine 4 (P1-P10 propagation, precedence, NM, history_horizon, detectors) | 1 |
| 6 | `company_group` / `metric_template` | Y after Gate C | `group_assignment_v2.csv` frozen; template v1 cell lists (WO-4.2); design review signed (AT-1.6a) | 5 (loader 2, tables and rebuild-twice test 1.5, design note 0.5, D1 query and reconciliation 1) | 1 |
| 7 | Cover-date anchor (W10) | Y | Period Engineer's pairing rule with 10 filing-checked cases (one ticket, rule owner PE, implementer DE); share-date rule stated | 2 | 1 (after Gate B content; W10 adds cells, it does not remove a wrong value) |
| 8 | Ingestion detector + companyfacts lag | Detector Y; fallback reader deferred | Detector: none new (submissions already stored). Reader: 50-filing 100% match gate, SEC slot | Detector 4 (zero-fact filings 89; submissions-vs-`core.filing` T3 list; companyfacts lag 88 cos); reader 5 (after Gate C) | 2 |
| 9 | Certify I12/I13, currency (E15), scale (E2), identity suite stored-vs-filing | Y* with F2/F12 | I12/I13 depend on structure tables that do not exist: register IDs only. Currency, scale, market cap vs price x shares (I4, 3 orders of magnitude) are buildable. The "identity suite stored-vs-filing (certify P2)" is the SEC data sets reconciliation of data-team/34 P2, which has no effort line anywhere; the Verifier's C7 ("by code first") depends on it | Rules 4; precision/recall tooling 2 (sampling frames, `rule_precision_recall.csv`, seed); FSDS `num.txt`/`pre.txt` reconciliation for headline cells 7 (Range reader 2.5, num filter and headline map 2.5, compare and states 2) | 2 |
| 10 | Structure pilot (measurement only, runner) | Y, deferred to Gate C | `readme.htm` for `cal.tsv` columns; shared `SECClient.get_range` (owner of `common/sec_client.py` told); runner job; stop rules K3 and 5 req/s | 4 | 2 |

### 1.2 Added Data Engineer work

| Item | Doable? | Inputs missing | Days | Lane |
|---|---|---|---|---|
| Foundation F1: migration 0100 (cell_evidence, cell_blank_reason, filing_registrant, identity audit, rule_run manifest), evidence JSONL writer/validator/loader, reason-writer API, persist total-debt blank reasons, rule registry loader + CI graph-diff + flags via repo variable | Y | Founder D-1 (enum) for the state codes; Chief's rule IDs; the 399-line diff committed first | 7.5 | 1 |
| Foundation F2: before-image/backup, dry-run diff table, rule-run manifest, idempotency and incremental-equals-full harness | Y | none | 2 | 1 |
| Reader/index change (7 name-only readers to `metric_definition_active`, partial unique index) | Y | migration for the view and index (spec 0100 content) | 1.5 | 1 |
| Revenue-total disagreement guard NA-8, both directions, with hidden-correct counter | Y (F9) | Case table of doc 37 s2 as a fixture file; banks excluded by template flag | 5 | 2 (addenda: l1) |
| T2 OI guard (WO-14) | Y partly (F10) | Std Lead NA-3/NA-12 style card for the identity set | 3.5 | 1 (addenda: l1) |
| W6/W7 NM states + W9 reason text + R1 leaf hides (WO-15) | Y | Wording keys; S3 items 1 and 3 only change wording later | 5 | 2 (addenda: l1) |
| Partial cost line (WO-20) | Y | NA-12 option (a) hide-only | 2 | 2 (l1) |
| ProfitLoss + NCI (WO-24) | Y | none | 2 | 2 (l1) |
| Scale/unit guard (WO-27) | Y | negative-control list of genuinely large per-share values | 2 | 2 (l1) |
| Market cap publish guard at the share basis (WO-21) + currency (WO-28) + lineage (E16), one file | Y | Std Lead arithmetic card for the multi-class method before build; ADS ratio list | 4 + 2 + 1.5 = 7.5 | 2 (WO-28/E16 are l2; WO-21 l1) |
| W1/W2 date-based windows (RF-01/02) | Y | `current_quarter()` (F6); COST and 53-week negative controls | 2.5 | 2 |
| W8 TSY default removal + D-4 yfinance tier off | Y | Founder D-4; Tag Mapper's `PaymentsOfOrdinaryDividends` result is not needed for the removal, only for the later fill | 2 (W8 1, D-4 1) | 1 |
| RF-23 `_resolved` latest-period rule | Y | Period Engineer shares `current_quarter()` | 2 (DE share) | 1 |
| Reason-rule audit (WO-25) | Y | Lane B (scrooner-f9) agrees to edits in `coverage_matrix.py`, `company_coverage_dashboard.py` | 2 | 1 (Gate C) |
| Split single writer, DE share (WO-22) | Y | Period Engineer's design; 0099 applied | 2 | 1 |
| Matching copies dedupe (WO-23), in the same change set as W3, flag off | Y | Decimals-interval rule fixtures (TTWO, ANET, company 8 FY2023) | 3 | 1 |
| Status scan (WO-26) | Y | Company Master agrees status wording; class line of Form 15 for the 16 flagged cohort cases only | 4 | 1 tail (addenda: l2) |
| 10-KT (WO-19) | Y | Period Engineer's `TP` grain rule; Collector allowlist change is lossless | 3 | 1 tail (l2) |
| Institutional overcount (WO-16) | Y, investigation | 13F filings for 37 cases | 3 | 1 tail (l2) |
| Nightly incremental certify + regression reopen + synthetic-injection test (one-time condition 4) | Y | cell_state, certify rules measured | 3 | 2 |
| Definition versioning build (spec s10 13-15 days minus 1.5 for the reader change) | Y, large | Spec accepted by Eng Head and Data Head (A13); migration numbers (F7); writer refactor after guards are stable | 12 | 2 |

## 2. Estimates, order, lanes, dependencies

### 2.1 Totals

| | Lane 1 | Lane 2 |
|---|---|---|
| Gate B scope (Tier 0) | 38.0 | 36.5 |
| After Gate B | 30.0 | 35.0 |
| **Total** | **about 68** | **about 71.5** |

Grand total about 140 engineer-days (ASSUMED, plus or minus 25%). The Engineering Head's 31-40 for WO-1 pre-dates WO-14..WO-28 (about 40), the versioning build (12-15), the FSDS reconciliation (7), P1 and the F1/F2 foundation; for the original ten items alone I get about 54. Dhairya's lane split (identity, W3, cell_state, W10 in lane 1; detector, certify, pilot in lane 2) leaves lane 1 with all of the addenda's `data_engineer_l1` guards (about 30 more days); I moved five guards to lane 2 and three population items to the lane 1 tail so both lanes carry about 70. The Chief should confirm or reassign.

### 2.2 Order and cumulative days (K = engineer kickoff; assume G about K+5 because the four workflows and the founder go come first)

Lane 1 (each row ends with commit, push, and its own rollback line):

| Order | Item | Days | Cum | Ready for |
|---|---|---|---|---|
| L1-1 | F1 foundation + 0100 file + total-debt reason persistence | 7.5 | 7.5 | 0100 committed by K+3 so S1 applies it with 0096/0097 |
| L1-2 | F2 harness | 2 | 9.5 | every dry-run |
| L1-3 | Reader/index change (0101 minimal registry) | 1.5 | 11 | before any version-2 definition row |
| L1-4 | W3 + Stage 2e (+ WO-23 flag off) | 5 + 3 | 19 | **R2a** (first stored train; upstream, 103 consumers) |
| L1-5 | P1 + link table + reload | 8 | 27 | **R2b** (reload window; cohort v1.1 follows) |
| L1-6 | Identity defects (id 1840 family, PSKY, AVB, WBD, EAI) | 4.5 | 31.5 | R2c |
| L1-7 | W8 + D-4 | 2 | 33.5 | R2c |
| L1-8 | WO-22 DE share | 2 | 35.5 | R4 (Period Engineer leads) |
| L1-9 | RF-23 DE share | 2 | 37.5 | R2c |
| L1-10 | T2 OI guard | 3.5 | 41 | R2c |
| **Gate B scope ends** | | | **about K+38 (WO-23 inside L1-4 is flag-off, its 3 days can follow Gate B; then 38)** | |
| L1-11 | cell_state first cut (reasonless = 0) | 4 | 45 | Gate C |
| L1-12 | cell_state full engine | 4 | 49 | Gate D |
| L1-13 | W10 | 2 | 51 | R-next |
| L1-14 | WO-25 reason-rule audit | 2 | 53 | Gate C text |
| L1-15 | company_group / metric_template | 5 | 58 | after design review |
| L1-16 | WO-26 status scan, WO-19 10-KT, WO-16 E1 | 10 | 68 | Tier 2 |

Lane 2:

| Order | Item | Days | Cum | Ready for |
|---|---|---|---|---|
| L2-1 | A1 workflow repairs (before G) | 3 | 3 | G |
| L2-2 | 0097 amendment (F2) + INVARIANTS + tests | 1.5 | 4.5 | A4 |
| L2-3 | WO-15 NM + W9 + R1 leaf hides | 5 | 9.5 | **R1** |
| L2-4 | Certify precision/recall tooling | 2 | 11.5 | A11 (G+2) |
| L2-5 | W1/W2 | 2.5 | 14 | R2c |
| L2-6 | Revenue-total guard NA-8 | 5 | 19 | R2c |
| L2-7 | Cost (WO-20), NCI (WO-24), scale (WO-27) | 6 | 25 | R2c |
| L2-8 | Market cap + currency + lineage | 7.5 | 32.5 | R2c |
| L2-9 | Certify new rules (currency, scale, market cap vs price x shares) | 4 | 36.5 | certify re-runs |
| **Gate B scope ends** | | | **about K+36.5** | |
| L2-10 | Definition versioning build | 12 | 48.5 | before any Q4 or history backfill |
| L2-11 | Ingestion detectors | 4 | 52.5 | Tier 2 |
| L2-12 | FSDS reconciliation (certify P2) | 7 | 59.5 | before T1 certification (Gate D) |
| L2-13 | Nightly incremental certify + regression reopen | 3 | 62.5 | Gate E condition 4 |
| L2-14 | Structure pilot (runner) | 4 | 66.5 | after Gate C |
| L2-15 | Fallback reader | 5 | 71.5 | after pilot and 50-filing match |

Gate implications (ASSUMED, the Chief and scrooner-4d re-quote): code for all of Tier 0 is complete at about K+38; trains R1 about G+8, R2a about G+14, R2b about G+22, R2c in two windows about G+31-G+33, R3 about G+34, R4 (Period Engineer) about G+35; Gate B about **G+35 (range G+28 to G+45)**, not G+13. Moving W10, WO-23, WO-25 out of Gate B (done above) is already counted. G+13 would need about four DE lanes. Levers, if the founder wants earlier: (a) a third DE lane on lane 2's guards (cuts about 12 days); (b) Release Manager and Verifier capacity are not the limit, DE days are; (c) hide-at-serve for the leaf-only guards in R1 (already planned) and registry-driven interim hides read from `cell_blank_reason` by `apps/backend` (a Frontend/Backend change, not DE) so the live wrong values disappear from pages at about G+15 while stored fixes land later. Gate C "reasonless = 0" is at about K+45 (G+40); first-cut `cell_state` could move to lane 2 after L2-9 (K+40.5) if the Chief prefers.

Dependency chain that cannot be shortened: F1 (reason store) -> every concept-level guard; W3 before P1 and before any cohort-based sample (it changes which copy is authoritative); P1 before the cohort v1.1 re-draw and before any count that depends on the 986; guards before `cell_state` (it reads their rows); versioning build after guards (the writer refactor touches the same 18 writers) and before any Q4 or history backfill (Std Lead precondition Q-6).

**Conflict with the Period Engineer's plan.** Their Q4 backfill is "day 14-18"; the versioning spec makes the Q4 backfill wait for Q-6 (registry + output versioning applied, resolve reads the frozen release). With versioning at lane 2 K+48.5 the earliest Q4 backfill is about G+44. The Chief must tell the Period Engineer; the alternatives are a third lane on versioning now (earliest about G+25) or accepting a Q4 backfill under the BASELINE release with the open-AC-card caveat (not recommended; Std Lead condition 5).

### 2.3 Parallelism under one connection per agent and one heavy lane

| Class | Rule | Examples from my items |
|---|---|---|
| Code, unit and scratch-schema tests | No production connection (local test DB or CI `postgres:16`, `SCROONER_TEST_DATABASE_URL`) | everything; mutation checks |
| Light production reads | One connection, `statement_timeout` 60 s, at most 100 company ids per query, index-backed; allowed beside a heavy slot | guard census queries, fixtures for named cases, AT scripts |
| Chunked scans (52 chunks of 100) | Quiet non-heavy window (06:00-12:00Z slack or the D2/D5-D6 spare slots); never beside a heavy slot | W3 population dry-run, WO-23 dry-run, revenue guard hidden-correct counter, FSDS reconciliation reads |
| SEC fetch | Shared flock limiter, at most 3 processes, combined 5 req/s, declared User-Agent; Verifier A14 (Entergy) before my P1 fetch; one P1 candidate-header batch in one 30-minute slot | P1 headers/R1; structure pilot on a runner |
| Heavy DB slots (`heavy-db-jobs`, one at a time, one stored-data train per day, never a train and a certify in one slot) | per calendar in 48-ENG (f) | below |

My heavy-slot demand (about 17 in the first 40 working days; the calendar offers about 1.7 per day, so slots are not the limit; one failed sample costs a train a day plus a certify re-run): S1 apply 0096, 0097 (amended), 0100, and 0101/0102 if committed (one window, additive, `lock_timeout 5s`); S2 coverage rebuild + snapshot; S3 certify dry-run on the 986 (1.5 h); R1; W3 dry-run (chunked scan); R2a; certify re-run; P1 reload dry-run (small), R2b, certify re-run; R2c (two windows) + two certify re-runs; R3; R4; plus nightly incremental certify once built. Rule I add: each train's manifest lists `ciks` and rule IDs in doc 53 before dispatch; a manual dispatch left pending can replace a pending scheduled run (Eng Head).

Merge order for shared files (Chief to ratify): `concept_fallback.py` / `derived.py`: held diff committed first (Release Manager, A5), then reason persistence, D-4, OI, cost; `ttm.py`: RU-1 pass-through (Period Engineer, already written) -> W6/W7 `_growth_value` (lane 2) -> W1/W2 (lane 2); `expanded_metrics.py` / `calculate.py`: W1, then W6/W7, then OI consumers, then W10; `price_metrics.py`: RU-1 anchor (PE) -> market cap guard -> currency -> lineage; `dedupe.py`: W3 and WO-23 as one change set; `identity.py`/`facts.py`: P1 (lane 1) first, then the 10-KT allowlist; lane B files (`coverage_matrix.py`, `company_coverage_dashboard.py`): ask scrooner-f9 before WO-25. Each commit by named paths from a temporary worktree on origin/main (A3).

### 2.4 Migration set to claim in doc 53

Claim now, never skip a number, commit the claim rows to origin before the files (origin's doc 53 still says next free 0098).

| Number | As assigned in the work order | My recommendation | Contents | Needed by | Apply |
|---|---|---|---|---|---|
| 0100 | `cell_evidence` | Agree, widened | `analytics.cell_evidence` (append-only, `superseded_by`, update/delete blocked by trigger except `superseded_by`), `analytics.cell_blank_reason` (run-scoped; key = company, data_point, period_grain, period_start, period_end, basis, run_id; no FK to `core.period`), `core.filing_registrant` (accession, registrant CIK, role in primary / co_registrant / quarantined), `core.company_identity_audit` (old/new, accession), `analytics.rule_run` (rule ID, version, flag state, ciks, run id) | K+3 (before G) | S1 with 0096/0097 |
| 0101 | cell_state / company_group / metric_template | **Swap with the definition tables and split** | Definition registry, minimal first cut from the spec's "0100": new `metric_definition` columns and widened status check, partial unique index (one active row per name), `metric_definition_active` view, `rule_registry`, release tables; no data, no reader until the 7 readers switch | before any version-2 row; K+11 | after commit, empty tables |
| 0102 | definition-version tables | **cell_state objects (thin DDL early)** | `analytics.cell_state_run`, `analytics.cell_state_latest` (table, latest period, run id, `template_version` and `definition_version` nullable), `analytics.cell_state_active` view, `analytics.defect_register` view | **K+14 at the latest**, because the Period Engineer's 0103 cannot be committed before 0102 exists; the engine fills it later | after commit |
| 0103 | Period Engineer (derived-fact lineage) | unchanged | `core.derived_fact_input` | before Q4 backfill | PE |
| 0104 | (new) | `company_group`, `metric_template` | after the WO-1.6 design review | |
| 0105 | (new) | Spec's "0102" `output_versioning` | before any Q4 or history backfill, after the writer refactor is merged behind `DEFINITION_VERSIONING=off` | |
| 0106 | (new) | Spec's "0101" `slot_observation` | only if the L2 scanner is approved; not needed before Gate D | |
0098/0099 stay the Period Engineer's. If the Chief keeps the assignment as written, 0101 must still be a thin early file (cell_state DDL) and the definition tables move to 0104; either way the versioning spec's content cannot fit one number and group/template must follow the design review.

## 3. Acceptance tests rewritten as script checks

Convention (WO-ADDENDA section 0): each test is a function in `data-team/strategy/tools/acceptance/data_engineer.py` returning `{test_id, passed, observed, expected, watermark, query_sha}`; read-only, one connection, 60 s, chunks of at most 100 ids; a test with no script is NOT_RUN. Every guard test also asserts the frozen state, a `family.rule@N` ID on the reason row, and that turning the rule flag off and recomputing a 10-company subset gives a before-image diff of 0. Items that already have AT-14..AT-28 / AT-1.6 / AT-1.9 / AT-1.10 / AT-7 / AT-8 tests in WO-ADDENDA keep them; the table adds the ones WO-1 and the added work lack, and states the gaps in the addenda tests.

| ID | Item | Script computes | Pass |
|---|---|---|---|
| AT-DE-01 | Migrations | `scripts/check_migrations.py` on the tree; clean-DB replay; insert `I12`,`I13`,`I14` and `X1` into `certification_finding`; `information_schema` columns | exit 0; every table in 2.4 exists; I-inserts succeed, `X1` fails; `rule`, `rule_version`, `suite_version`, `suite_run_at` exist |
| AT-DE-02 | Reason/evidence stores | columns of `cell_blank_reason`, `cell_evidence`; attempt UPDATE (other than `superseded_by`) and DELETE on `cell_evidence` in scratch | no FK to `core.period` or period_id column; unique on key + run; both attempts rejected; grep of `pipeline/` finds no `delete from analytics.cell_evidence` |
| AT-DE-03 | Total-debt reason persistence | scratch fixtures hitting R1 containment, R5 zero, R5 floor; compare blocked decisions to `cell_blank_reason` rows; run the writer for company A and check company B and other rules' rows | counts equal; every row has rule ID and reason code from the frozen list; B rows unchanged; widening the delete scope (mutant) fails |
| AT-DE-04 | Registry | regenerate the dependency graph from code in CI; diff to `metric_dependency_graph.csv`; every rule ID in code is in the registry and the reverse; consumer count and classification recomputed | diff 0; mismatches 0 |
| AT-DE-05 | Rollback | per rule with a stored effect: scratch run, flag off, recompute manifest ciks | before-image diff 0 cells; production: same on the Verifier's 10 sampled ciks before each train |
| AT-DE-06 | Idempotency | rerun each new or changed stage on unchanged inputs; row hash of result tables | changed cells 0 |
| AT-DE-07 | Backup | per train manifest: ciks, rule IDs, flags, before-image row counts; restore script on scratch | counts equal the dry-run affected counts; restore reproduces the rows byte for byte |
| AT-DE-08 | Reader/index | grep that every `metric_definition` name lookup uses `metric_definition_active` (7 files: `ttm.py`, `expanded_metrics.py`, `fcf_growth.py`, `quality_flags.py`, `reconciliation.py`, `dividend_streak.py`, `quality_score.py`); insert a second active row with the same name; insert a proposed version-2 row then run the nightly on a fixture | grep finds 0 bare lookups; second active insert fails; outputs unchanged (diff 0) |
| AT-DE-09 | W3 constant | grep for periodic-form constants in `pipeline/src` | exactly one definition, imported by `dedupe.py`, `conflict_*`, `derived.py`, `certification` (decision on 20-F/40-F recorded) |
| AT-DE-10 | W3 Stage 2e | scratch: three consistent 10-K copies + one rounded DEF 14A copy of one period; plus a derived-from-DEF-14A row | 10-K earliest copy authoritative; non-periodic rows non-authoritative; removing the filter (mutant) fails |
| AT-DE-11 | W3 live cases | canonical values for JPM `net_income` FY2021-2025 and Q4 2025; MA FY; WTRG FY CFO and capex | JPM FY 48,334 / 37,676 / 49,552 / 58,471 / 57,048 M, Q4 2025 13,025 M, Q1-Q4 sum = FY; MA FY equals 10-K; WTRG values are WTRG's, none from 0001193125-26-124163 |
| AT-DE-12 | W3 population | `canonical_fact` rows (population and cohort) whose source facts include a non-periodic filing form; dry-run diff by class | 0 remaining (baseline 229 in cohort); classes published; each non-null to null change has a frozen-enum reason; Verifier tier V sample recorded |
| AT-DE-13 | WO-23 flag | dry-run with flag off, then on | off: diff 0; on: AT-23.1-23.5 |
| AT-DE-14 | P1 table of 9 | run the rule on the nine accessions of GATE-A 3e (ETR 10-K and 10-Q, SO, SRE, EIX, ES, DUK, WEC negative, AAPL negative) | 9 of 9 as tabulated; WEC and AAPL not shared |
| AT-DE-15 | P1 reload | Entergy id 694 FY2025 `Revenues` and `Assets` at 2025-12-31; id 142 facts on shared accessions; `core.filing_registrant` invariant | 12,946,686K and 71,890,730K; 0 facts for id 142 on shared accessions; every accession with 2+ registrants has exactly 1 primary and 0 facts on a non-primary company |
| AT-DE-16 | P1 parents | SO, SRE, AEE, ETR, CTVA, EIX, CMS, ES, TXNM: latest period end and status | each has a Q2 2026 period (end on or after 2026-06-30) and status not stale |
| AT-DE-17 | P1 quarantine and idempotency | fixture accession where dei CIK differs from the first FILER; reload twice | no facts loaded, finding row written; second reload changes 0 rows |
| AT-DE-18 | P1 regression guard | add `cert.I6.shared_accession_nonprimary_fact@1` and run on the nine | 0 findings after the reload; a seeded wrong fact is flagged |
| AT-DE-19 | Cohort v1.1 | file `cohort_v1_1` with diff to v1 (added parents, EAI/PS handling), recomputed D0, hash | present before any D0 or K1a figure is quoted for the 986; every number carries the cohort version |
| AT-DE-20 | Identity invariant | for every active company: name, former names, tickers vs stored submissions | disagreements equal the expected set (PSKY, VMRK display name, EAI, AVB, WBD) or are logged findings; 0 unexplained |
| AT-DE-21 | id 1840 and friends | `company_name`, `primary_ticker`, `display_name`, `core.listing`, market cap row, audit rows | name VIVMARK RESIDENTIAL and ticker VMRK unchanged; display name not "AvalonBay..."; EQR listing with end date 2026-08-17; market cap hidden with a rule ID until the Q3 10-Q is ingested and decision 16 is made; AVB (0001104659-26-102433) and WBD (0001193125-26-423513) not active with the accession in the audit row; PSKY name Skydance Corp, ticker SKYD; EAI has no market cap |
| AT-DE-22 | Identity rollback | reverse script from audit rows on scratch | old values restored exactly |
| AT-DE-23 | Revenue guard (NA-8) | the 30 doc 37 s8 cases as fixtures; cohort query: displayed revenue where two total tags are filed undimensioned in the same context and differ beyond the decimals interval; hidden-correct count | 30 of 30 as specified (EMR and NTAP both hidden; banks excluded); displayed cases 0; hidden-correct count published per company-period; the 28 transitive consumers non-null where revenue is hidden: 0 |
| AT-DE-24 | W8 | TSY rows computed with a defaulted $0 dividend where `dividends_paid` is blank and no evidence of non-payer; PFE | 0; PFE TSY consistent with its 5.7% dividend yield or unknown |
| AT-DE-25 | D-4 | `employee_count_resolved` rows whose only source is `core.company.y_employee_count`; changed-cell count | 0 such rows; changed count published; `core.period` rows dated after the latest filing excluded from period tests |
| AT-DE-26 | W10 | AAPL 0000320193-26-000020 book value per share at 2026-06-27; cohort nulls with a valid balance-sheet-date row | 7.36; 0 (baseline 1,427 cells / 718 companies); no value pairs shares and equity from different filings |
| AT-DE-27 | W1/W2 | cohort TTM EBITDA/FCF whose four inputs are not date-contiguous; TTM buyback/dividend older than the staleness threshold; MasTec, AAL; negative controls COST (12/12/12/16) and a 53-week filer | 0 and 0 (baselines 47/159, 62/99, 81/61/30); MasTec and AAL hidden or corrected; both controls still shown |
| AT-DE-28 | Detectors | zero-fact filings; submissions vs `core.filing`; companyfacts lag | lists all 89 and the named T3 cases (HPQ, MDB, JKHY, IREN, HEI, SJM, OLLI, DG, DE) and KO; 20-case Verifier check 0 false positives; reader (if built) 100% on 50 filings |
| AT-DE-29 | Certify tooling | `rule_precision_recall.csv` produced by script from the findings of the running commit; sampling frame export with seed | one row per rule; schema as freeze register A11; same seed gives the same frame; AT-1.9a-d pass |
| AT-DE-30 | Suite version | change `suite_version`, rerun on a scratch cohort | previously certified companies flagged recertify; state carries suite version and date |
| AT-DE-31 | Certify workflow | dispatch dry run from a different working directory as CI invokes; artifact present | success; `certify-findings` artifact; duration at most 150 min; run id in doc 53 |
| AT-DE-32 | FSDS reconciliation | headline cells (11) latest FY and quarter for 10 companies vs `num.txt`/`pre.txt` (Range read, nothing written to disk) | every disagreement listed with accession; 0 unexplained on the golden-10; mutation (scale by 1000) caught |
| AT-DE-33 | cell_state shape | rows per run, sum of eight states, reasonless, class/owner enums, hash twice, pointer rollback | 160,718 = D0 on the 986 (or cohort v1.1 D0); sum equals; reasonless 0 at Gate C; non-enum class/owner 0; two builds identical; repoint restores previous counts (AT-7.3, 7.7, 1.6c, 1.6e) |
| AT-DE-34 | cell_state correctness | `value` cells whose period end is earlier than the expected period; guard-hidden cells vs `cell_blank_reason`; metrics with a hidden input still non-null | 0; equal (AT-7.4); 0 (graph propagation) |
| AT-DE-35 | cell_state size and speed | bytes per run, three runs, `count(*)` on the active view | at most 60 MB per run, 200 MB total; under 5 s |
| AT-DE-36 | Versioning | spec section 7 tests 7.1-7.8; `seed()` raises on a changed body with the same version; lock file CI test; every `delete from analytics.canonical_fact` / `metric_value` site goes through `output_writer` | all pass; direct deletes 0 |
| AT-DE-37 | Nightly regression | inject a bad fact in staging for one cohort company; run the nightly incremental certify | company reopens within one cycle; incremental resolve equals full resolve on 20 companies |
| AT-DE-38 | Guards in general (WO-14, 15, 20, 21, 24, 27, 28, 16, 19, 25, 26) | AT-14.x ... AT-28.x as written | as written, plus the common assertions in the convention above; two gaps: AT-14.3 passes by named cases only (F10); AT-21.1 names SPCX, which is outside the 986, so the query must run on the population |

## 4. One-time-solution test: what would force a redo of backfilled history, and the control

| # | Trigger that forces a redo | Why | Control |
|---|---|---|---|
| 1 | A cell key built on `core.period.id` or fiscal labels | W5/T9 relabels or a period repair would orphan every reason, evidence and state row | Keys use dates (company, data_point, period_grain, period_start, period_end, basis) in `cell_blank_reason`, `cell_evidence`, `cell_state_latest`; AT-DE-02 checks there is no period_id |
| 2 | Cohort re-drawn after samples and baselines (P1 adds nine parents and removes EAI) | Every Verifier sample, D0, K1a and precision figure on the 986 would be redone | P1 before any cohort-dependent claim; cohort is a versioned file (v1.1); every figure and sample carries the cohort version; AT-DE-19 |
| 3 | Stage 2e (authority) changed twice (W3 now, matching copies later) | Two population recomputes and two sets of samples | One change set, WO-23 behind its own flag, enabled later with a recompute limited to the cells its dry-run moves |
| 4 | Concept-level hides stored by deleting rows | The next nightly delete-then-insert or a cell_state rebuild makes the blank reasonless again | `cell_blank_reason` first; guard stage owns the write; AT-DE-03; nightly after a release keeps reasons (AT-DE-06) |
| 5 | Guards shipped as ad hoc hide lists, then replaced by templates | Code rebuilt a second time | One registry keyed by (group, data_point, rule); Tier 1 migrates rows, not code; CI diff to the graph (AT-DE-04) |
| 6 | Stale dependency graph misclassifies serve-time vs recompute | A leaf hide leaks a wrong value through a consumer | Graph regenerated from code in CI; classification computed |
| 7 | Definitions overwritten in place (`seed()` writes version 1 with `on conflict do update`) | A definition change silently rewrites history | Spec: lock file, body hash, archive-then-replace, BASELINE release freeze; nothing rewrites history before 0105 and the writer refactor (AT-DE-36) |
| 8 | History or Q4 backfill before output versioning | Any later definition change re-derives all history | Std Lead Q-1..Q-6 and H-1..H-8 preconditions; Chief moves the Q4 date behind lane 2 versioning (section 2.2) |
| 9 | Three "current quarter" definitions | States flip when one moves | One function in `common/` (F6) |
| 10 | Evidence rows deleted or rewritten by a rebuild | Verifier work lost, the delete-scope bug again | Append-only trigger; empty delete scope; `cell_state` reads, never writes, evidence |
| 11 | Rollback by flag without a recompute | Stored hides persist because the nightly touches only recent filers | `rule_run` manifest lists ciks; rollback = flag off + recompute of the manifest ciks; AT-DE-05 |
| 12 | P1 as a one-off reload | The next nightly normalizes the subsidiary first and re-claims the accession | Rule lives in the loader and `core.filing_registrant`, plus a nightly certify rule (AT-DE-18) |
| 13 | Certification state without suite version | A suite change cannot reopen certified companies | F2 columns before 0097 is applied; AT-DE-30 |
| 14 | Cohorts defined by a live rank | Ranks move daily | Versioned id lists (freeze register s6) |
| 15 | Shared tree, claims only in an uncommitted doc 53, local main 94 commits behind origin | Number collisions, red CI, work on a stale base | Claims committed first; Release Manager temporary worktree; rebase of my reads before coding (my review read the local tree) |

## 5. Sign-off

**SIGNED WITH CONDITIONS.** The mechanisms (state enum, rule registry, reason store, evidence table, release path, rollback by flag and manifest) are sound and are one-time designs once the schema gaps in section 0 are closed. The work is feasible, but not on the dates in doc 49 section 4.

Conditions:
1. Gate B is re-quoted from section 2.2 (about G+35, range G+28 to G+45) or a third DE lane is added; I do not sign G+13. Dhairya and the Chief decide, scrooner-4d re-slots.
2. 0097 is amended before it is applied with the regex, `rule`/`rule_version` and `suite_version`/`suite_run_at` columns and the Python `INVARIANTS` tuple (F2), and migration 0100 (reason and evidence stores, registrant link, audit, manifest) is committed before G and applied in S1.
3. No concept-level guard ships until `cell_blank_reason` exists and the guard writes its reason there (F1); the Std Lead's reason-persistence condition is met by this, not by log counts.
4. Migration numbering follows section 2.4 (or the Chief's alternative with the same need-by dates); the claim rows are committed to origin before any file; the thin `cell_state` DDL is committed by K+14 so 0103 is not blocked.
5. W3 and WO-23 ship as one Stage 2e change set with a population dry-run and a single periodic-forms constant; W3 and P1 precede any cohort-dependent sample or figure; D0 is re-versioned after P1 (cohort v1.1).
6. P1 starts only after the Verifier confirms the Entergy mechanism (A14); SEC reads use the shared limiter.
7. The held guards (399-line diff) are committed by the Release Manager before any lane edits `concept_fallback.py` or `derived.py`; the merge order in 2.3 is ratified.
8. `cell_state` v0 is a table with a run id and an active view (F5) after a 20 s explain check on a 100-company chunk; if that check fails, the fallback is a view plus scoreboard snapshots written to disk.
9. The Chief tells the Period Engineer that the Q4 backfill waits for versioning (section 2.2) unless a third lane builds it.
10. Founder items I depend on: D-1 (state enum, before F1 codes are frozen), D-2 (row removals, before cell_state counts), D-4 (employee count, before the D-4 change), and decision 16 (Vivmark history basis) before the Q3 2026 10-Q is ingested; default for 16 is the P1 quarantine hold.

## 6. Commands actually run and untested scope

Run: file reads listed at the top; `git fetch`, `git status`, `git show --stat 2cfc569`, `git show origin/main:` for `pipeline-certify.yml`, migration 0097 and doc 53; `git ls-tree origin/main .github/workflows/`; `git diff HEAD -- normalizer/derived.py | grep`; `grep`/`sed` over `pipeline/src`, migrations and the strategy files; `ls`. No database connection, no SEC request, no commit, no migration, no tag-inbox line (I learned nothing new about a tag; the `dei:EntityCentralIndexKey` line is the Verifier's proposal and is still unappended).

Not verified: every database count (all inherited); whether `raw.sec_submissions` retains per-CIK accession lists usable for the P1 candidate detector; the 20 s explain for `cell_state`; the population reach of W3 (not 229); the number of D-4 cells; the origin versions of `certification/*` and `derived.py` (local main is 94 commits behind; the working-tree held diff may differ from origin); lane B's agreement; whether `book_value_per_share` lives in `calculate.py` or `expanded_metrics.py` (both mention it); day estimates are ASSUMED.
