# 42. End-to-end plan: from today to "100% coverage, 100% moat" and keeping it there (Ritwik, Head of Data Product, 2026-10-21)

Audience: Dhairya (chief of staff), then the data and engineering teams. Founder direction: 100% data coverage and 100% data moat, by grouping companies and giving each group its own template. This plan joins doc 41 (the model), doc 40 as amended (the defect-closing evidence and ranks) and R8 (Chief's challenge). Evidence labels: FILING-CHECKED / DATA-INFERRED / ASSUMED. Every duration below is ASSUMED and is re-baselined at Gate 1 after the first measured run. Nothing here is approved or built; accounting definitions are proposals for a named accountant.

## 1. End state (what "done" means, testable)
For every company in scope, on its page and in the screener:
1. It belongs to one audited group; its page shows exactly the group's template cells.
2. Every template cell is one of: a certified value with filing locator; a derived value with its inputs; an evidenced zero; or, rarely, "Not disclosed by this company" with Verifier evidence. No other state exists on a published page.
3. The company is `certified` per data-team/34: invariants I1-I11 clean over all stored values; headline values reconciled to the independent SEC data-set parse; Verifier filing check recorded; no open finding; history from 2015-01-01 complete or classified.
4. The defect register (internal) is empty for that company.
5. The state stays true: new filings flow through nightly incremental certification; a regression reopens the company.
Cohorts: T1 top 100, T2 top 1,000 (986 non-excluded), T3 the remaining active companies (about 5,216 in total). The words "100%" are used publicly only for a cohort whose every company is certified.

## 2. Operating principles (from the Chief and the standing rules)
- No denominator shrinks without filing evidence: group membership is audited (30 per group, zero wrong), and "Not disclosed" requires an opened filing.
- Suppress with a reason before guessing; never fabricate, flip a sign or fill a cell the company does not report.
- Every fix ships through one path: classify into a rule family, dry-run, Verifier sample with zero wrong rows (about 30 filings), Release Manager commits only the named paths, a separate first live run, re-run the invariant suite for the whole cohort.
- Build once: reuse data-team/33 families, `scrooner-certify` (34), `company_filing_line_evidence` (0093), `common/sector_applicability.py`. No parallel tracker, no duplicate identity table.
- One heavy database job at a time (doc 53 lanes, `heavy-db-jobs` concurrency group). Capacity checked live 2026-10-21: Postgres `max_connections` 60 (15 in use), database 46 GB of a 60 GB plan, Mac disk 8.1 GB free (founder will free 10 GB). The pooler's own pool size is not yet verified.
- Stop launching new campaign shards (S062+) once the invariant suite exists; shards become exception work.

## 3. Roles and owners
| Role | Owns |
|---|---|
| Head of Data Product (Ritwik) | Group and template product choices, visible metric sets, tiers, scoreboard, trust surfaces, roadmap, kill decisions (recommends; founder decides) |
| Data Chief | Dependency order, batch scoping, release tiers, weekly challenge |
| Sector Analyst | Group shape signatures, audits, template drafts |
| Standardization Lead (+ named accountant) | Definitions for replaced / composite cells; accountant approves |
| Tag Expert / Tag Mapper | Vocabulary defects, coexistence checks, tag cards, era tag sets |
| Period Engineer | Q4 and interim derivation, per-share pairing, eras, restatement basis |
| Data Engineer | Tables, jobs, certify suite, ingestion, performance |
| Data Verifier | Filing checks, precision samples, "Not disclosed" evidence |
| Data Triage | Defect classification, dedupe, scoreboard numbers |
| Release Manager | Tests, diff review, named-path commits, safe pushes (never applies migrations) |
| Mind Curator | Promote lessons; stop repeated mistakes |
| Frontend / Backend engineering | Template-only rendering, badge, "why this number", scorecard |
| Accounting reviewer (HUMAN, to be named) | Approves replaced and composite definitions |
| Founder | Scope, pricing, release policy, naming the reviewer |

## 4. Phases, gates and work packages

### Phase 0 (days 0-3): unblock and measure
- **WP0.1 Measured baseline** (Data Engineer, Triage). Release Manager commits then the Data Engineer applies migrations 0096 and 0097 (reviewed); run R1's four read-only gap queries on the 986 cohort with a data watermark; `scrooner-certify` dry-run on the top 1,000 (about 1.5 h, PLAN.md). Output: measured split of defects by class; certify findings by invariant.
- **WP0.2 Certify precision** (Verifier). Open 30 flagged cells per invariant; record false positives and misses (data-team/36 already shows both). Any invariant with more than half false flags is demoted to `review`.
- **WP0.3 Founder gates:** accept the amended plan (releases held guards); confirm the single visible "Not disclosed" state; name the accounting reviewer; free Mac disk.
- **Gate 1 (end of day 3):** measured baseline exists. If any defect class differs from R1's projection by more than one third, re-rank before proceeding.

### Phase 1 (weeks 1-2): groups, templates v1, held guards
- **WP1.1 Release held guards** (Release Manager, Verifier): total-debt consistency guard, no-derived Q4 EPS/DPS, revenue-total disagreement guard (doc 37). Each: tests rerun, cohort dry-run, Verifier reviews 30 hits including a count of correct values hidden by mistake. Acceptance: guard hides no correct value in the sample; FILING-CHECKED wrong values in data-team/36 (JPM 5 cells, Visa FY DPS, NVDA about 216 cells, MSFT growth basis) are corrected or hidden with a reason.
- **WP1.2 Group assignment** (Sector Analyst, Triage): shape signatures from the filer's statements for the 986 (FSDS pre.txt plus existing `company_filing_line_evidence`); groups: corporate, bank, insurer, equity REIT, mortgage REIT, BDC/fund, pre-revenue overlay, non-screener; asset manager and broker only after a 30-company shape review. Audit 30 companies per group against opened statements, zero wrong memberships.
- **WP1.3 Template v1** (Head of Data Product drafts, Sector Analyst, Standardization Lead): freeze corporate, bank, insurer, REIT cell lists per doc 41 section 5. Replaced definitions (bank revenue = NII + noninterest income, REIT capex, insurer revenue composition) go to the accountant with filing evidence.
- **WP1.4 Template engine design** (Data Engineer): `company_group` (company, group, effective period, evidence accession) and `metric_template` (group, cell, rule, definition version), extending 0093 and `sector_applicability`; the coverage computation reads templates; defect register view. Design review before migration numbers are claimed in doc 53.
- **Gate 2 (end of week 2):** groups assigned and audited for the four first groups; template v1 frozen; three held guards released and verified; first template-based coverage number computed on a fixed denominator.

### Phase 2 (weeks 3-6): close defects for T1 (top 100), certify T1
Defect families, each run through the common release path, in R8's order and always on a named group:
- **WP2.1 Source authority and mixed vintage** (Data Engineer; 33 C; split certify I6).
- **WP2.2 Split table** (Period Engineer + Verifier; 156 candidates, each new split row filing-checked).
- **WP2.3 Population gating and wrong reasons** (Data Engineer, Sector Analyst; 33 Q and B5): dividend/buyback rows only where evidenced.
- **WP2.4 Interest-expense rule incl. the 2024 `InterestExpenseNonoperating` era break** (Tag Mapper; coexistence check + 12-case sample; net tags never map).
- **WP2.5 Per-share date pairing** (Period Engineer; 2,100-2,800 cells projected).
- **WP2.6 Structure pilot, measurement only** (Data Engineer): read FSN `readme.htm`, Range-read one `cal.tsv`, test CVX/XOM/AMD calculation cases, reconcile top-1000 headline cells to FSDS `num.txt` as certify P2. No new tables. Stops on K1/K3/K5 below.
- **WP2.7 T1 certification** (Verifier, Triage): per company: invariants clean, reconciled, headline cells opened in the filing (revenue, operating income, net income, diluted EPS, total assets, total equity, CFO, capex, shares, total debt, market cap; latest FY and quarter), no open finding.
- **Gate 3 (end of week 6):** top 100 certified OR a written shortfall by defect class and company; wrong-value rate in the Verifier sample at 0 for released families; fill on the template denominator reported beside value-filled and current cells on the all-cells denominator.

### Phase 3 (weeks 7-12): T2 (top 1,000)
- **WP3.1 Remaining templates**: BDC/fund, mortgage REIT, pre-revenue overlay, then asset manager and broker after the shape review; same audit gates.
- **WP3.2 Composition layer** (Standardization Lead + accountant + Data Engineer; only if K1 passes): versioned definitions, per-company perimeter records, reported and standardized value, for D&A, capex, total debt, interest, revenue, net income attributable. Decisions C1 (finance leases) and C4 (capitalized software) first.
- **WP3.3 Structure evidence layer in production** (Data Engineer): Range fetch of FSDS/FSN (about 29 MB per quarter without values, 72 MB with), `structure/` package, identity suite stored-vs-filing inside certify, structure-only candidate report (Tag Mapper: agree / disagree / structure-only); migrations only after the pilot passes. Estimated storage about 0.35 GB top-1000, 1.3 GB full (ASSUMED).
- **WP3.4 Period and history** (Period Engineer): Q4 as a filed fact for fiscal years before 2021-08-09 (75% of top-1000 FY2015 10-Ks file one), additive-allowlist derivation with calendar-aware windows, era-scoped tag sets (SalesRevenueGoodsNet and similar; interest-expense eras), predecessor CIK links, I11 history completeness over all 33 concepts from 2015-01-01.
- **WP3.5 Ingestion** (Data Engineer): detector for filings with zero facts (10-Q accessions missing from companyfacts) first; a fallback reader only after it matches 100% on 50 filings companyfacts does carry.
- **WP3.6 Trust surfaces** (Frontend/Backend, Head of Data Product): page renders template cells only; Certified badge with date; "why this number" panel (filing link, period, formula version, as-of date); restatement note; public data-quality scorecard (companies per state, open defects by class, wrong values per 1,000 cells); screener filter "certified only", default on for T1/T2.
- **WP3.7 T2 certification in batches** (Verifier, Triage): batches of 10 following the operating loop in data-team/34; Verifier samples about 10% of companies plus every invariant/reconciliation disagreement (ASSUMED).
- **Gate 4 (end of week 12):** top 1,000 certified or a per-company shortfall list; zero wrong values in released families; history window complete or classified.

### Phase 4 (months 4-6): T3 and the rest of the population
Apply the same groups, templates and release path to about 4,200 more companies in cohorts of 100-250; automation (structure candidates, identities, reconciliation) does the bulk, the Verifier does exceptions and the audit sample per group. Budget: storage about 1.3 GB, within the 14 GB database headroom.

### Phase 5 (continuous): keep it true
- Nightly incremental pipeline: new filing -> normalize -> map -> template cells -> incremental certify; a filing that breaks an invariant reopens the company and blocks its badge.
- Yearly taxonomy diff job (data-team/tags/sources.md): new, deprecated, redefined tags joined to mapped tags and tag cards.
- Quarterly group re-audit (30 per group) and tag-card calibration; the Mind Curator promotes lessons.
- Alarms: certified-company regressions, drift of the "Not disclosed" share above its ceiling, pooler/runtime breaches.

## 5. Scoreboard and cadence
Weekly founder report (one page, from Triage numbers): per group: companies, template cells, certified, evidenced-zero, "Not disclosed" (with evidence), defects by class, companies certified. Also on the fixed denominator (160,718 cells for the top 986): value-filled cells, current-and-not-stale cells, FILING-CHECKED wrong values removed. Daily: Data Chief standup note (what shipped, what is blocked). Fortnightly: Head of Data Product review of template choices and kill list.
| Measure | Baseline | Target |
|---|---|---|
| Cells filled, all-cells denominator, top 986 | about 77.1% corrected (projection) | measured at Gate 1; about +2-3 points by week 6; then per phase |
| Template cells certified | 0 | T1 100% at Gate 3; T2 100% at Gate 4 |
| Unexplained blanks | about 13,349 (shard baseline) | 0 (defect register) |
| Wrong values in released families, Verifier sample | 5-25% of total-debt cells; stale value at 78% of examined companies (pre-guard) | 0 |
| Companies certified | 0 | 100 -> 1,000 -> all active |

## 6. Kill criteria and failure tests (stop and report; do not continue by momentum)
- K1: if the calculation tree explains fewer than half of the remaining D&A/capex perimeter differences, the composition layer stays disclosure-only.
- K2: more than half of 30 sampled certify `wrong_value` flags are not real: demote that invariant to `review`.
- K3: more than 5% of accessions fail to join `core.filing`, or SEC refuses Range requests.
- K4: a group audit finds any false "absent" or wrong membership: that group's template is not used in the denominator.
- K5: any auto-published structure-only value, flipped sign, or definition closed without the accountant.
- Failure tests (R8): denominator theatre (value-filled and current cells must rise, not only the template percentage); building on projections (Gate 1 must exist by day 3, else stop new builds); infrastructure before visible fixes (by day 10 the three held guards are live and the data-team/36 wrong-value list is corrected or hidden with a reason).

## 7. Dependencies on humans (the real critical path)
1. Founder: accept the plan, name the accounting reviewer, approve the single "Not disclosed" state, confirm per-group visible metric sets. Not blocking: the Range-fetch raw departure (pilot stores nothing), migrations 0098-0100 (not needed in 30 days).
2. Accounting reviewer: bank revenue, REIT capex, insurer revenue, finance leases (C1), capitalized software (C4), net income attributable. Blocks composition and any accountant-gated template cell; does not block Phase 1-2 families.
3. Verifier capacity: about 30 filings per released family and per audited group (about 10 families + 8 groups, so roughly 400-500 filing opens in the first 12 weeks, ASSUMED), plus 10% of companies per certification batch. This, not engineering, is the likely bottleneck; automated reconciliation to the SEC data sets must carry the bulk.
4. Engineering: template-only rendering and trust surfaces in `apps/app` / `apps/backend` (Phase 3); can start from the template contract in Phase 1.

## 8. Risks
- Plan numbers are projections from a market-cap-ordered 45% sample (S001-S045) and file-based reading; Gate 1 replaces them.
- Pooler pool size not verified despite `max_connections` 60; heavy jobs still run one at a time.
- Certify has measured false positives and misses; Gate 0.2 sets its precision before it gates anything.
- FSDS/FSN come from the same XBRL as companyfacts: structure is independent of our mapping, not of the filer's tagging; FSDS values exclude note facts.
- Template membership errors could hide real gaps; mitigated by audits, quarterly re-audit and K4.
- A filer's own error cannot be "fixed"; it is recorded as a company-scoped exception.
- Scope creep: new metrics or sources before certification is done are on the kill list (doc 37 section 7).

## 9. First seven days, day by day
- Day 1: founder gates (accept plan, name reviewer, free Mac disk); Release Manager reviews and commits 0096/0097; Dhairya schedules a quiet database window; Sector Analyst starts shape signatures; Verifier starts certify precision sampling.
- Day 2: Data Engineer applies 0096/0097; runs R1 queries and certify dry-run; Release Manager reruns tests on the three held guards.
- Day 3: Gate 1 review (measured split vs projection); re-rank if off by more than one third.
- Days 4-5: group assignment for the 986; Verifier reviews 30 hits per held guard; template v1 draft to the accountant.
- Days 6-7: first guard releases (reviewed, dry-run, first live run); first weekly scoreboard.

## 10. Source map
Evidence and detail: doc 40 (with v2 amendments), doc 41 (model), team/R1-R8, data-team/33 (families), data-team/34 (certification definition), data-team/36 (certify dry-run lessons), doc/data-moat/team/PLAN.md, doc/planning/53 (lanes and migration ledger).
