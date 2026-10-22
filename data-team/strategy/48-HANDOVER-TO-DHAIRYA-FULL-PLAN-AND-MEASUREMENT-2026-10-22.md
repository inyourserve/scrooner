# 48. Handover to Dhairya: the full plan and how to measure it (Ritwik, Head of Data Product, 2026-10-22)

Written for: Dhairya (chief of staff), who will run execution with the data and engineering teams. Founder direction: 100% data coverage and 100% data moat, delivered through company groups with their own templates. This is the single entry point. It states the plan, the measurement system, the calendar, ownership and the founder decisions. Detail lives in the referenced docs; read them by need, not all at once.

## 0. One-page summary
- **Problem, restated by what we measured:** top 986 companies, 160,718 cells, 123,326 valued = **76.7%**; 37,392 blanks, of which **13,349 (36%) have no reason at all**. Roughly **55% of blanks are not missing data** (a row that should not exist for that kind of company, or a line the company legitimately does not report) and roughly **38% (~14,300) are real defects** to fix; ~4% wait on an accountant or are unexamined (doc 46). Separately, **12 classes of wrong or misleading values are live on the site** (register W1-W12) plus two new root classes (company identity, multi-registrant filings). Trust problems come before coverage problems.
- **Solution:** a system, not a patch (doc 45): sources, facts, concept resolution, a metric dependency graph, **group templates**, a **cell state machine** (every cell is a value, a derived value, an evidenced zero/undefined/horizon/not-presented state, not in the template, or a defect with an owner), quality gates, certification and serving, and a nightly operating loop. Positioning (doc 43): the certified screener.
- **Definition of done (testable):** coverage = template cells in a non-defect state with evidence / template cells; 100% = zero defects. Moat = every number has filing locator, formula version, as-of date and a certification state. We claim "checked against the filing, error rate published", never "guaranteed correct".
- **Calendar (assumed, re-baselined at Gate A):** Gate A days 0-3 start and measure; B day 10 wrong values fixed; C day 15 every cell classified; D day 45 top 100 certified and capture defects closed for them; E day 90 top 986 certified, trust surfaces live; then the ~4,200 remaining companies.
- **Founder asks (4, blocking Gate A):** accept the plan; name the accounting reviewer; approve the cell-state model incl. the single visible "Not disclosed by this company" state; approve removing internal/duplicate rows from the coverage count.

## 1. Read order for the team
1. `47-MASTER-PLAN-AND-WORK-ORDERS` (13 work orders, gates, rules) — the execution document.
2. `46-INTEGRATED-SYSTEM-PLAN-V2` (where blanks go, wrong-value register W1-W12, group rules, campaign coverage check, backlog tiers).
3. `45-COVERAGE-OPERATING-SYSTEM` (architecture and data model), `41-TEMPLATE-DRIVEN-100-PERCENT-COVERAGE` (template contents v1), `43-STRATEGY` (why), `44-MEASURED-BASELINE` (numbers).
4. Evidence: `team/R1-R8`, `team/S1-S5`, `data/*.csv`; supporting: data-team/33 (fix families), 34 (certification definition), 36 (certify dry-run lessons), `doc/data-moat/team/top1000/results/ALL-SHARDS-ROOT-CAUSES.md`, doc 53 (lanes, migrations).

## 2. Measurement system (the part that makes execution honest)

### 2.1 Principles
1. **One definition per metric, versioned, frozen per gate.** No metric definition changes mid-gate; a change is a new version reported beside the old.
2. **Fixed denominators.** Report on both (a) the all-cells denominator (986 x 163 = 160,718 per period now) and (b) the template denominator once groups are frozen. Denominator work must never look like progress: always show value-filled and current-and-not-stale cells beside any percentage.
3. **Independent measurer.** Data Triage computes the scoreboard from stored tables; owners do not self-report. The Verifier samples independently of the engineer who built the fix.
4. **Evidence class on every number** (MEASURED live query / FILING-CHECKED / DATA-INFERRED / ASSUMED), and a data watermark (table build time) on every figure.
5. **Measure the instruments.** Invariants and detectors get precision/miss rates before they gate anything (Chief R8).
6. **Snapshots, not memory.** Write each weekly result to `analytics.coverage_snapshot` (existing) or a CSV under `data-team/strategy/scoreboard/YYYY-MM-DD.csv` so trends survive session loss. Check `max(snapshot_date)` and that `company_data_point_coverage.gap_reason` is populated before quoting a number (CLAUDE.md).

### 2.2 The KPI tree
| # | KPI | Exact definition | Baseline (MEASURED 2026-10-21, doc 44) | Gate C | Gate D | Gate E | Owner of number |
|---|---|---|---|---|---|---|---|
| K1 | Fill (all cells), K1@1 'table as stored' | cells with `has_value` / 160,718; `has_value` is latest-period for METRIC rows only and any-period for CONCEPT rows (F2) | 76.7% (123,326) | >= 77.6% (cover-date fix +1,427 cells) | >= 80% (S1: top-10 leaves + engine/feed +5,441 = 80.1%) | >= 84% (ceiling about 85.6% if all ~14,300 defects close) | Triage |
| K2 | Reasonless blanks | blank cells with null `gap_reason` / `cell_state` unclassified | 13,349 | **0** | 0 | 0 | Data Engineer; Triage verifies |
| K3 | Template coverage | template cells in a non-defect state with evidence / template cells | not yet defined (needs groups, Gate C) | measured, per group | >= 95% T1; 100% T1 defects closed | 100% T2 | Triage |
| K4 | Defect register | open defects by class (vocabulary, composition, period, ingestion, resolver, evidence) and age | unknown until `cell_state` (blank classes in 44/46 are proxies) | counted | falling weekly | 0 for T1/T2 | Triage |
| K5 | Wrong values live | W1-W12 and new items: open count; Verifier-sampled wrong-value rate in released families | 12 classes open | all W-items released or hidden with reason (**Gate B day 10**) | 0 in sample | 0 in sample | Verifier |
| K6 | Hidden-by-mistake | correct values hidden by a guard, per sample | n/a | measured at each release; any guard that hides correct values is fixed first | 0 | 0 | Verifier |
| K7 | Stale-as-current | companies/cells where latest period older than the staleness rule but shown as current | 78% of examined companies, PRE-guard (R1, 107 of 138) | re-measured after guard 9e77357 | falling | ~0 | Triage |
| K8 | Companies certified | state `certified` per data-team/34 | 0 | pilot on 10 | 100 (T1) | 986 (T2) | Verifier + Data Engineer |
| K9 | Cost per certified company | Verifier minutes + engineer-hours per company, per batch of 10 | n/a | first batch measured | must fall batch over batch | falling | Chief |
| K10 | Rule-closed share | defects closed by a reusable rule / closed by hand | n/a | tracked | rising | high | Chief |
| K11 | Instrument quality | per invariant/detector false-positive and miss rate on 30 flagged and 30 passed cells | known problems (data-team/36) | **precision set at Gate A** | each demoted if over half false | maintained | Verifier |
| K12 | Freshness | 10-Q/10-K filed in last 60 days with facts loaded; companyfacts lag | 89 filings with zero facts (89 cos); 88 companies lagging | detector live | <= 10 | <= 5 | Data Engineer |
| K13 | Group integrity | wrong memberships in 30-per-group audit | 114 reassignments under rules v2; 660 corporates unopened | 0 wrong in audited groups | 0 | 0 | Sector Analyst |
| K14 | Trust surface | share of page views/screener results on certified companies; scorecard published | n/a | spec done | badge live for T1 | scorecard live | Head of Data Product |
Targets for K1/K8 are ASSUMED from S1 and R6 upper bounds and are re-set at Gate A from the measured `cell_state`.

### 2.3 Baseline queries (reproducible; read-only; `pipeline/.env` DATABASE_URL; one connection; `statement_timeout` 60s; cohort ids from `doc/data-moat/team/top1000/shards.csv`, non-excluded = 986)
```sql
-- K1/K2: fill and blanks by reason (analytics.company_data_point_coverage; has_value = latest period for metric rows, any period for concept rows; see K1c)
select count(*) cells, count(*) filter (where has_value) valued,
       count(*) filter (where not has_value and gap_reason is null) reasonless
from analytics.company_data_point_coverage where company_id = any(:ids);
select coalesce(gap_reason,'(none)') reason, count(*) from analytics.company_data_point_coverage
where company_id = any(:ids) and not has_value group by 1 order by 2 desc;
-- period gaps
select gap_cause, count(*) from analytics.period_gap where company_id = any(:ids) group by 1 order by 2 desc;
-- K12: filings with zero facts
select count(*), count(distinct f.company_id) from core.filing f where f.company_id = any(:ids)
 and f.form in ('10-Q','10-K') and f.filing_date >= date '2026-07-01'
 and not exists (select 1 from core.fact x where x.filing_id = f.id);
-- watermark
select max(checked_at) from analytics.company_data_point_coverage;
```
Measured 2026-10-21 (build 2026-10-20 18:52 UTC): 160,718 / 123,326 / 13,349; period_gap top: no_mapped_tag 8,324; q4_not_derived 5,767; quarter_not_derived 5,320; no_line_item_filed 1,876; not_in_sec_feed 1,796; filing_not_processed 851; conflict_material 785; zero-fact filings 89 in 89 companies. Exports used for the analysis: `data-team/strategy/data/cohort_cells.csv` etc.

### 2.4 Weekly scoreboard (Triage publishes Monday; Dhairya sends the one-pager to the founder)
Per group: companies, template cells, value / derived / evidenced-zero / undefined-by-math / history-horizon / not-presented / not-in-template / defect (by class and owner); fill on both denominators; value-filled and current cells; W-items open; certified count; cost per certified company; instrument precision; Gate status (green / amber / red, with reason). Format for the founder: one page, five lines of "what changed", three numbers that moved, one decision needed.

### 2.5 Measurement integrity checks (Chief runs these every Friday)
- Denominator audit: no cell left the denominator without a recorded evidence reference.
- Sample audit: Verifier re-checks 5 closed defects per week against filings.
- Regression watch: any previously certified company with a new open finding is reopened and reported.
- Gaming test: value-filled and current cells must rise whenever the percentage rises; if only the percentage rises, escalate.
- Stale-baseline check: quote no number older than its table's watermark.

## 3. Execution calendar and gate exit criteria
| Gate | Days | Exit criteria (all required) |
|---|---|---|
| A start/measure | 0-3 | Founder decisions 1-4 done (or defaults in section 5 applied); migrations 0096/0097 reviewed, committed (Release Manager) and applied (Data Engineer); certify dry-run on 986 complete; K11 precision for every invariant measured; K2/K4 baseline from `cell_state` v0; re-rank if any defect class is off by more than one third from doc 46 |
| B trust | 10 | W1-W12 plus identity (id 1840) and registrant-context gate released or hidden-with-reason; held guards live; data-team/36 wrong-value list corrected or hidden; K5 = 0 in Verifier sample; K6 = 0 |
| C classify | 15 | `cell_state` computed for the cohort, K2 = 0, groups v2 audited and frozen for corporate/bank/insurer/REIT, sector-only rows gated (~4,400 cells), pass-through reasons live (~880), cover-date anchor fixed |
| D capture + T1 | 45 | Tier 2 leaves fixed for T1 (capex, total debt, interest, D&A, buybacks, dividends, AR, bank NII), feed freshness fixed, successor CIKs linked, accountant items answered, T1 (100) certified, K1 >= 80% |
| E scale | 90 | T2 (986) certified, trust surfaces live (badge, "why this number", scorecard), K1 >= 84%, cost per certified company has fallen over three batches |
| F long tail | 90+ | T3 in cohorts of 100-250 by the same path |
Daily: Chief's note. Weekly: scoreboard + Friday integrity checks. Fortnightly: Head of Data Product reviews templates and the kill list.

## 4. Ownership map (RACI summary; full tickets in doc 47 section 4)
| Area | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Orchestration, scoreboard to founder | Dhairya | Dhairya | Chief, Triage | Founder |
| Ranking, work cap, failure tests | Data Chief | Dhairya | all | Founder |
| Measured numbers | Data Triage | Data Chief | Verifier | Dhairya |
| Cell state, templates, identity, authority and registrant gates, ingestion | Data Engineer | Data Chief | Sector Analyst, Release Manager | Dhairya |
| TTM, per-share pairing, derivation, history | Period Engineer | Data Chief | Verifier | Dhairya |
| Vocabulary and tag cards | Tag Mapper + Tag Expert | Data Chief | Verifier | Dhairya |
| Groups and templates | Sector Analyst | Head of Data Product | Standardization Lead | Dhairya |
| Definitions | Standardization Lead | **named accounting reviewer** | Tag Expert | Founder |
| Verification, certification | Data Verifier | Data Chief | Engineer | Dhairya |
| Release (commit/push, never migrations) | Release Manager | Dhairya | Verifier | Founder |
| Page, badge, scorecard | Frontend/Backend | Head of Data Product | Data Engineer | Founder |
| Positioning, kill list, user test | Head of Data Product | Founder | Dhairya | all |
| Scope, accountant, "Not disclosed" state, employee-count source, pre-2015 base | Founder | Founder | Ritwik | Dhairya |

## 5. Founder decisions and defaults if not decided
| # | Decision | Needed by | Default if undecided (reversible) |
|---|---|---|---|
| 1 | Accept the plan (releases held guards) | Gate A | none: held guards stay held; Gate A measurement still runs |
| 2 | Name the accounting reviewer | day 10 | Tier 3 stays blocked; REPLACED cells remain defects, not blanks; T1 certification excludes those cells |
| 3 | Approve cell-state model incl. one visible "Not disclosed by this company" | Gate A | `not_presented` states show only with Verifier evidence; no public "Not disclosed" label until approved |
| 4 | Remove internal/duplicate rows (total_debt_split, base employee_count, 29 `*_resolved` twins) from the coverage count | Gate C | report both counts side by side |
| 5 | Employee-count source | Gate D | use `employee_count_resolved` (978 of 986 valued), flag staleness |
| 6 | Pre-2015 base year for 10-year growth | Gate D | not used; show "history from FYxxxx" |
| 7 | Exclusions/holds (Entergy Arkansas, Pershing Square; HONA, INIO, ARXS, JAN) | Gate C | hold all from denominators with reason |
| 8 | Per-group visible metric sets | Gate C | doc 41 section 5 as drafted |

## 6. Risks that execution must watch
1. Projections (class shares) come from small samples; Gate A replaces them. Re-rank on a one-third deviation.
2. Shared database load: 15 of 60 connections in use now; one heavy job at a time; the pooler's own pool size is not verified.
3. Verifier capacity is the likely bottleneck (about 30 filings per released family and per audited group, about 400-500 opens in 12 weeks, ASSUMED); automate reconciliation to carry the bulk.
4. Evidence detectors can wrongly shrink denominators; none counts until audited.
5. Account usage limits interrupted agent work twice on 2026-10-21/22; reports were saved and resumed. Ask agents to write report files early; keep Verifier-heavy steps off-peak.
6. Scope creep (new metrics, sources, vendors) is on the kill list until T1/T2 are certified.
7. A filer's own error cannot be fixed; it is recorded as a company-scoped exception.

## 7. First 72 hours for Dhairya (do in this order)
1. Put decisions 1-4 to the founder with docs 47 and 48; apply defaults if no answer in 24h.
2. Check `ListAgents` and `pg_stat_activity`; schedule a quiet window (peer sessions: scrooner-a5 and others).
3. Release Manager: review and commit 0096/0097 (and the uncommitted `certification/` work) with tests rerun; Data Engineer applies them in the window.
4. Data Engineer: run the baseline queries (2.3) and the certify dry-run on the 986; write `data-team/strategy/scoreboard/2026-10-2x.csv`.
5. Verifier: certify precision per invariant (30 flagged cells each); confirm id 1840 identity, Entergy Arkansas registrant case, KO feed lag, WTRG.
6. Triage: reconcile the Gate A numbers with doc 46 and report deviations; Chief re-ranks if any class moved by more than one third.
7. Release Manager: release the three held guards (total-debt consistency, no-derived Q4 EPS/DPS, revenue-total) after the Verifier sample passes.
8. Publish the first weekly scoreboard and the founder one-pager.

## 8. What I need to hear back
Gate A numbers (K1, K2, K11, defect classes) and any class off by more than one third; founder decisions; any template cell the data team believes is mis-specified. I will update the group and template choices and the kill list at each fortnightly review.


---
## Amendments after the head and role reviews (2026-10-22; doc 49 wins on conflict)
- **K1 split:** K1a = valued cells not hidden by a guard; K1b = cells hidden by a guard (reported separately). The Gate C target of 77.6% is withdrawn (it ignored cells Tier 0 hides); targets are re-set at Gate A. Failure test 1 judges correct value-filled cells.
- **K11:** precision AND recall per RULE (not per invariant), measured on the top-986 run; code-assertion rules proven by code.
- **K5/public error rate:** only from a separate rotating random audit of displayed certified cells (300 a month, exact 95% bound per 1,000 cells, also bounded on companies); never "0%" or "100% correct".
- **Verifier sample sizes** replace "about 30 filings": 30 for hide-with-reason; 60 + 15 risk + 15 negative controls for value-changing.
- **Dates** are provisional until scrooner-4d's slot calendar; Gate B is day 13 with four release trains; Gate D splits into non-financial and financial T1.
- **K13 (group integrity)** wording is replaced: not 'zero wrong in a 30-per-group audit' (invalid for groups over 60) but the group audit standard in doc 49 section 5 and the supported statement 'every member opened against its signature, independent re-read 0 wrong, residual bound at 95%, latest fiscal year only'. D1 / K3 are defined over `catalog_version` (133 lines + about 60 sector rows) and may be claimed only after the detector audit (G+35).
- **K1c (honest headline):** valued AND current. K1@1 (76.7%) is frozen as 'table as stored' and is overstated because CONCEPT rows count any period (63,127 valued concept cells in the 986: 57,691 with a latest period on or after 2025-07-01, 5,436 older). Proxy K1c = 117,890 / 160,718 = 73.4% (cutoff is a proxy for `common/staleness.py`). K14b removed from the Gate A-E tree (no company dimension in `app.usage_event`). Dates in this file are superseded by doc 49 section 4 (Gate B about G+27, three Data Engineer lanes).
- **Wording correction (Data Triage, 2026-10-22):** 'latest period' applies to metric rows only; concept rows are any-period. K1c and K7 cannot be computed from the cell export (no periods); the reported 73.35% is a proxy (117,890 / 160,718) until the live extract E0 runs after the 0096/0097 apply. Baseline check passed 59 of 59 (D0 160,718; valued 123,326 = 76.73%; D0e 74.98%).
- **K1 definitions (freeze register section 4, AMD 7):** K1@1 'table as stored' never gets a target; K1c@1 = K1@1 valued, currency proven under `common/staleness.py`, minus K2c (the 116), minus vendor-tier values, minus the K12b lag list, failing closed with unknowns as K7u, reported on D0 and D0e; K1c@2 from Gate C; Gate A has measurement targets only; first numeric K1c rule at Gate B: K1c(B) >= K1c(A) minus cells hidden by Verifier-confirmed guards. The 73.35% proxy is not a baseline (baseline = live extract E0). Interim rule: no percentage without K1a@0 beside it.
