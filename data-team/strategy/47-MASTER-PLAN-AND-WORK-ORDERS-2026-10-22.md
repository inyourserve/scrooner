# 47. Master plan and work orders: the one document the data and engineering teams execute from (Ritwik, 2026-10-22)

This is the execution layer. It does not repeat the analysis; it states the goal, the rules, the sequence, and one work order per role with acceptance tests. Detail and evidence live in: 41 (template model), 43 (strategy), 44 (measured baseline), 45 (architecture), 46 (integrated plan v2, wrong-value register W1-W12, group rules, campaign coverage check), team/R1-R8 and S1-S5 (specialist reports), data-team/33 (fix families), data-team/34 (certification definition). Where this file and those differ, this file's sequence wins, and doc 46's numbers win over earlier docs. All durations are ASSUMED until Gate A below; all definitions are PROPOSED and need the named accountant where marked. Nothing here is approved or built.

## 1. Goal and definition of done
Goal (founder, 2026-10-21): 100% data coverage and 100% data moat. Made testable:
- Every company belongs to one audited group and its page shows only that group's template cells.
- Every template cell is in exactly one state with evidence: `value` | `derived` | `evidenced_zero` | `undefined_by_math` | `history_horizon` | `not_presented` (evidenced, incl. the rare visible "Not disclosed by this company") | `not_in_template` | `defect(class, owner)`.
- **Coverage = template cells in any non-defect state with evidence / template cells.** 100% = zero defects.
- **Moat = every shown number has a filing locator, formula version, as-of date and a certification state** (data-team/34: invariants I1-I11 clean, reconciled to the SEC data sets, Verifier headline check, no open finding).
- "100%" is claimed publicly only for a cohort whose every company is certified. We do not claim "100% correct"; we claim "checked against the filing, error rate published".
Cohorts: T1 top 100, T2 top 986 (non-excluded), T3 the rest (~4,200).

## 2. Rules that apply to every work order
1. One release path for every change that touches stored or shown values: classify into a rule family, dry-run, Verifier sample with zero wrong rows (about 30 filings) that also counts correct values hidden by mistake, Release Manager commits only the named paths, a separate first live run, re-run the invariant suite for the cohort.
2. A denominator never shrinks without evidence: group membership audited (30 per group, zero wrong), evidenced states need a detector that passed a 30-per-group audit with zero false positives, "Not disclosed" needs a Verifier-opened filing.
3. Suppress with a stated reason before guessing. Never fabricate, flip a sign, or fill a cell the company does not report. Unmapped is unknown, not zero.
4. Reuse before building: data-team/33 families, `scrooner-certify` (34), `company_filing_line_evidence` (0093), `common/sector_applicability.py`, `staleness.py`. No parallel trackers.
5. Capacity: Postgres `max_connections` 60; agents stay at one connection each, `statement_timeout` 60s, chunked by company ids; heavy jobs one at a time (doc 53 lanes, `heavy-db-jobs` group). Database 46 of 60 GB; Mac disk 8 GB free (10 GB being freed): stream SEC bulk files, delete after.
6. Shared-file ownership and the migration ledger follow doc 53; claim numbers there. Migration 0097 is committed but not applied; 0096 not applied.
7. Evidence labels on every claim: FILING-CHECKED / DATA-INFERRED / ASSUMED.

## 3. Gates (sequence)
- **Gate A (days 0-3): founder acceptance + measured start.** Founder accepts the plan (releases the held guards), names the accounting reviewer, approves the state model and denominator-row removals. Release Manager commits then the Data Engineer applies 0096/0097; run certify dry-run on the top 986; Verifier measures certify precision per invariant.
- **Gate B (day 10): Tier 0 trust fixes live.** W1-W12 plus identity and registrant-context fixes released or hidden-with-reason; the data-team/36 wrong-value list (JPM 5 cells, Visa FY DPS, NVDA ~216 cells, MSFT growth basis) corrected or hidden.
- **Gate C (day 15): every cell classified.** `cell_state` computed for the cohort; reasonless blanks = 0; group assignment v2 audited and frozen for corporate, bank, insurer, REIT.
- **Gate D (day 45): capture defects closed for T1; T1 certified.** Tier 2 leaves fixed, accountant items answered.
- **Gate E (day 90): T2 certified, trust surfaces live.** Then T3 rollout.
Kill and stop rules: K1 composition layer stays disclosure-only if the filers' calculation trees explain under half of the remaining perimeter differences; K2 demote any invariant where over half of 30 sampled flags are false; K3 stop structure ingest if over 5% of accessions miss the join to `core.filing` or SEC refuses Range reads; K4 a group audit with any false "absent" or wrong membership is not used in a denominator; K5 never auto-publish a structure-only value, flip a sign, or close a definition without the accountant. Weekly failure tests (Chief R8): value-filled and current cells must rise, not only the template percentage; Gate A must exist by day 3; held guards live by day 10.

## 4. Work orders (one per role; each is a ticket-ready list)

### WO-1 Data Engineer
1. Apply 0096 and 0097 after Release Manager commit; confirm `coverage_matrix` rebuild and the any-period overcount retired.
2. **Identity master check (new, Tier 0):** invariant comparing CIK vs `company_name` vs ticker vs SEC submissions for every company; fix `core.company` id 1840 (CIK 906107 stored as VIVMARK RESIDENTIAL / VMRK; no Equity Residential row). Accept: zero CIK/name/ticker disagreements in the population or each logged as a finding.
3. **Registrant-context gate (new, Tier 0):** a fact from a combined multi-registrant filing attaches only to the registrant its entity context names (`dei:LegalEntityAxis`); scan for combined filings (Entergy 6 registrants; likely Duke, Southern, AEP); decision list per subsidiary registrant. Accept: Entergy Arkansas no longer holds Entergy Corp's revenue/assets (Verifier checks 0000065984-26-000174).
4. **Authority gate (W3):** canonical facts only from periodic forms (229 rows from 8-K/DEF 14A/20-F/40-F in the cohort); fix WTRG (8-K 0001193125-26-124163).
5. **`cell_state` job:** per (company, period, cell) enumerated state + evidence reference + defect class/owner, computed by code nightly; a null metric row carries the input's reason (pass-through, ~880 cells). Accept: reasonless cells = 0 for the cohort; no value changed by this job.
6. `company_group` and `metric_template` tables (extend 0093 and `sector_applicability`); coverage computed on templates; defect register view; scoreboard query. Design review before numbers are claimed in doc 53.
7. Cover-date anchor (W10): anchor book value per share and net cash per share on the balance-sheet date or fall back to the latest non-null row (1,427 cells, 718 companies). Accept: AAPL 10-Q 0000320193-26-000020 shows 7.36 at 2026-06-27.
8. Ingestion: detector for filings with zero facts (89 in the cohort) and for companyfacts lag (88 companies, 576 TTM cells; KO); fallback reader only after it matches 100% on 50 filings companyfacts does carry.
9. Certify: add I12 structure_disagree and I13 recipe_changed only after precision gate; add currency (E15) and scale/unit (E2) checks; identity suite stored-vs-filing as certify P2 (no parallel `structure/identities.py`).
10. Structure pilot (measurement only, no new tables): Range-read FSDS/FSN (`pre.txt` ~18 MB, `cal.tsv` ~9 MB, `sub.txt` per quarter), read the FSN readme for `cal.tsv` columns, test CVX/XOM/AMD calculation cases. Productionize only if K-criteria pass.

### WO-2 Period Engineer
1. W1: TTM EBITDA/FCF require four consecutive quarters (47 cos/159 cells; 62/99); W2: age guard per TTM concept (81/61/30 companies); W5: repair broken fiscal labels (24 companies).
2. Per-share date pairing rule (book value/net cash per share) written with 10 filing-checked cases; YTD route wired into price and expanded metrics (97 cells); calendar-aware windows (COST, XOM: 181 cells).
3. Derivation allowlist by canonical concept (additive concepts only); never derive Q4 EPS/DPS; use the filed Q4 from the Item 302(a) note for fiscal years before 2021-08-09 (75% of top-1000 FY2015 10-Ks file one).
4. Restatement-basis rule (MSFT FY2016-17 growth 0.6845 vs 0.3777 on one basis; HON Q4 capex W4); recast conflicts.
5. History horizon states with first-fact evidence; successor/predecessor CIK links with Company Master (22 companies with 8-K12B/G3; XOM old CIK 0000034088 missing from `core.company`).
Accept: Verifier samples MasTec (W1), AAL (W2), HON (W4) clean.

### WO-3 Tag Mapper (with Tag Expert)
1. Vocabulary with full-population coexistence checks and a 12-case sample each (30 if over 1,000 companies): interest expense (`InterestExpenseNonoperating`, `InterestAndDebtExpense`, net tags never map), capex (`PaymentsToAcquireOtherPropertyPlantAndEquipment`, productive assets, software, custom), D&A as separate lines (710 cells), total debt (custom noncurrent lines, segment-only: CDE, AMP), share buybacks, AR change (`IncreaseDecreaseInAccountsAndNotesReceivable`), `OtherNonoperatingIncomeExpense`, dividends (`PaymentsOfOrdinaryDividends`, includes preferred: coexistence first), bank net interest income and interest income extraction (USB R4).
2. Structure-path candidate report: agree / disagree / structure-only for revenue, D&A, capex, interest, debt, operating income (NJR, Spire, TVA, Nikola, Photronics, DLH are the filing-checked examples). Never global mapping from a custom tag; company-scoped with accession and calculation path.
3. Tag cards for capex and D&A; era-scoped tag sets (SalesRevenueGoodsNet etc.; interest-expense era break 2024).
Accept: each mapping carries coexistence result and a Verifier zero-wrong sample; no self-approval.

### WO-4 Sector Analyst
1. Freeze group rules v2 (S2): SIC first, statement-shape check for 6411, 6199, 6211, 6200, 6282, 4610, 492x, blank SIC; data values never override SIC. Extend the audit to the ~660 unopened corporates (even-spaced sample plus captive finance PCAR, CAT, DE, F, GM) and run a 30-company shape review for asset managers and brokers.
2. Template v1 for corporate (utility, energy, midstream variants), bank, insurer, equity REIT, mortgage REIT, BDC/fund, pre-revenue overlay, managed care/insurance broker/exchange (corporate plus sector lines); cell lists per doc 41 section 5 and S3.
3. Evidence detectors for `not_presented` per filing (face + notes + dimension-only rows), audited 30 per group with zero errors; replace circular `has_*_company` populations.
4. Retire SIC-based "pre-revenue biotech/pharma" reason (W9, 44 companies) in favor of filing evidence.
Accept: zero wrong memberships in a 30-per-group audit; groups moved (114 under the v2 rules) logged with evidence.

### WO-5 Standardization Lead (+ named accountant)
1. Answer decisions in S3 section 7 (13 items) and R3: C1 finance leases in debt, C4 capitalized software, EBITDA when no operating-income line (314 cells), D&A and capex composition, dividends-per-share policy, net income attributable to parent, bank revenue (NII + noninterest income), REIT capex, insurer revenue composition.
2. Conditional rulebook (S3): for every conditional metric the condition, evidence, state, coverage treatment, propagation rule, UI wording; remove 29 `*_resolved` twins and internal rows from the denominator (founder approval).
3. Versioned definitions for the composition layer (reported value and standardized value, perimeter record per company-period) once K1 passes.
Accept: each definition has a FILING-CHECKED fixture set and is marked approved by the named accountant before any REPLACED cell goes live.

### WO-6 Data Verifier
1. Gate A: certify precision per invariant (30 flagged cells each); confirm company identity (id 1840), Entergy registrant case, KO feed lag, WTRG.
2. Sample every released family: about 30 filings with zero wrong rows, plus count of correct values hidden by mistake. Families in order: total debt guard, Q4 EPS/DPS, revenue-total guard, W1/W2, W6/W7 (RDDT 0001713445-26-000022 R5/R8; PFE 0000078003-26-000095 R8), W10, group audits.
3. "Not disclosed" evidence: open the filing for every cell where the line is not presented or filed anywhere; record accession and locator.
4. Certification headline check (revenue, operating income, net income, diluted EPS, total assets, total equity, CFO, capex, shares, total debt, market cap; latest FY and quarter) for T1, then 10% of each T2 batch plus every reconciliation disagreement.

### WO-7 Data Triage
Own the defect register and the weekly numbers: per group companies, template cells, state counts, defects by class and owner, closure rate by rule versus by hand; re-run the S1 cascade attribution after each tier; keep `metric_dependency_graph.csv` current; classify the remaining ~1,076 unexamined reasonless cells and the 8% not covered by any sampled data point (second 40-cell sample).

### WO-8 Data Chief
Rank weekly; hold the work cap (at most 10 rule families and 50 cases per batch); run the failure tests (value-filled and current cells rising; Gate dates met); stop new shards S062+ once the invariant suite exists; arbitrate lane and migration conflicts (doc 53).

### WO-9 Release Manager
Reruns tests, reviews the diff, commits only the named paths, pushes safely beside other sessions' uncommitted work; first the held guards (total-debt consistency, no-derived Q4 EPS/DPS, revenue-total disagreement guard) after the founder's acceptance. Never applies migrations or touches the database.

### WO-10 Frontend and Backend engineering (`apps/app`, `apps/backend`)
1. Template-only rendering: the company page and screener read `company_group` + `metric_template` + `cell_state`; no empty grid; each state has its own wording from the rulebook (e.g. "No dividend paid in the last 4 quarters", "Not meaningful: negative earnings", "History from FY2020"). A `not in template` cell is never shown.
2. Certified badge with date; "why this number" panel (filing link, period, formula version, as-of date); restatement note; screener filter "certified only" (default on for T1/T2).
3. Public data-quality scorecard (companies per state, open defects by class, wrong values per 1,000 cells sampled, our own error rate).
4. Fetches to `apps/backend` from flat pages need `force-dynamic` (CLAUDE.md gotcha); pool `max` stays well below the pooler budget.
Accept: screenshot-verified on bank, insurer, REIT, corporate, pre-revenue, and one multi-registrant company; no layout shows a hole.

### WO-11 Head of Data Product (Ritwik)
Own group and template product choices and the visible metric set per group (the ~18-metric guardrail holds); hold the kill list (no new metrics, sources or vendors before the certified cohort); the weekly founder one-pager; test the "certified screener" hypothesis with real users on the certified top 100 before investing past it; maintain `strategy/LOG.md`.

### WO-12 Mind Curator
Promote lessons from the inbox (identity, registrant context, filing-order bug in structural rules, resolved-path reading before claiming display defects); retire contradicted entries; report knowledge gaps agents keep hitting.

### WO-13 Founder / Accounting reviewer (human)
Founder: accept the plan; name the accounting reviewer; approve the state model and the single visible "Not disclosed" state; approve removing internal/duplicate rows from the coverage count; choose the employee-count source (not an XBRL fact; 978 of 986 have a `_resolved` value); decide whether a pre-2015 base year may start a 10-year growth rate; confirm exclusions (Entergy Arkansas, Pershing Square) and holds (HONA, INIO, ARXS, JAN); confirm per-group visible metric sets.
Accounting reviewer: WO-5 decisions.

## 5. Weekly operating rhythm
Monday: Triage publishes the scoreboard (fixed 160,718-cell denominator and template denominator; value-filled, current-and-not-stale, FILING-CHECKED wrong values removed; state mix per group). Daily: Chief note (shipped, blocked, next). Friday: Head of Data Product + Chief review the kill list, template choices and one-page founder report. Every release goes through the rule-2 path; every fix ends with a permanent artifact (tag card, template cell, rule, invariant, ledger line).

## 6. What is still open (stated so nobody assumes it is done)
- Gate A not yet run: every count is projection or sample until `cell_state` and the certify dry-run exist.
- About 660 corporates unopened for group audit; evidence detectors unaudited; class shares extrapolated from 40-cell and per-company samples.
- Long tail (T3, ~4,200 companies) and the 2015+ history window are planned, not measured; the same method and release path apply.
- Ownership, insider and price metrics are in the 163 data points but not yet analyzed here; they follow the same template and state model and need their own pass (source dates, 13F vintage, price vendor).
- Dates are ASSUMED; they are re-baselined at Gate A and again at each gate.
- Accounting definitions are proposals until the named accountant approves.


---
## v2 AMENDMENTS (2026-10-22; from the Engineering Head and Data Head reviews; where they conflict with section 4 above, THESE WIN)
Sources: `48-ENGINEERING-HEAD-REVIEW-2026-10-22.md` (signed with conditions), `48-DATA-HEAD-REVIEW-2026-10-22.md` (signed with conditions). Full disposition and both positions on any disagreement: doc 49 sections 6-7.

### A. Corrections of fact
1. **W12 / WO-9 "held, already built" is wrong for the revenue-total guard.** It does not exist in code (verified: no match for `revenue_total_undecidable`, `two_totals`, "contract-revenue subtotal" in `pipeline/` or `apps/backend/`). It is a BUILD item for the Data Engineer; acceptance = data-team/37 section 8 (30 of 30 cases). What does exist, uncommitted: total-debt guards (`concept_fallback.py` R1/R5) and never-derive Q4 EPS/DPS (`derived.py`), in a 2,540-line / 17-file diff in the shared tree together with the `certification/` package. WO-9's first task is to review and commit that diff by named paths from a temporary worktree.
2. **WO-1 item 3 (registrant-context gate) premise was wrong:** Company Facts strips `dei:LegalEntityAxis`. Replace with a shared-accession primary-filer rule (accession served under more than one CIK: keep the fact only for the primary filer named in the submission header; subsidiaries excluded or loaded from the filing instance). The Verifier confirms the mechanism on Entergy before any code.
3. **W10 has ONE fix:** anchor per-share balance-sheet metrics on the balance-sheet date with a stated share-date rule. Remove "latest non-null row" (WO-1 item 7). Rule owner: Period Engineer (WO-2 item 2); implementer: Data Engineer (WO-1 item 7). They are one ticket.
4. **W1 uses date-based contiguous windows**, not fiscal labels (W5 changes labels). Calendar-aware windows ship in the same release.
5. **`cell_state`:** cell key = (company, period, data_point) from day one; v0 is a read-only latest-period view + defect register (no migration); history states derived on read; full-history table only after a size check against the 14 GB headroom; Verifier evidence (accession, locator, rule version) lives in a separate durable table that a rebuild never deletes.
6. **Gate B is three release trains** (R1/R2/R3), not twelve releases (doc 49 section 4).

### B. Work added so every one of the 28 campaign themes has an owner and an acceptance test (Data Head condition 1)
| Theme / item | Owner | Lane | Acceptance test |
|---|---|---|---|
| T1 revenue-total guard (BUILD) + per-company structure rule for 201-206 companies | Data Engineer (guard); Tag Mapper + Standardization (rule) | DE lane 1 | data-team/37 section 8: 30 of 30; insurers (MET 724M vs 19,154M) covered; guard hides no correct value in the Verifier sample |
| T2 operating-income guard: the Revenue minus `OperatingExpenses` fallback (168 companies), segment-note OI read as consolidated (MET, HONA, MOG-A), pretax-labelled OI (AFG, ELS) | Data Engineer | lane 1 | all 168 fallback cases listed; Verifier 30 cases zero wrong rows; AFG, ELS, MET, HONA, MOG-A fixed or hidden with reason |
| T3 filing row never registered (HPQ, MDB, JKHY, IREN, HEI, SJM, OLLI, DG, DE): submissions-vs-`core.filing` detector | Data Engineer | lane 2 | detector lists every named case; zero false positives in a 20-case Verifier check |
| T4 market-cap publish guard (33 M R3/R4; AKTX $1.27T, TBLA $999B, SPCX understated), multi-class cover sum, ADS ratio | Data Engineer | lane 1 | AKTX, TBLA, SPCX corrected or hidden; market cap vs price x shares plausibility invariant in certify I4 zero unexplained breaks over 3 orders of magnitude; Verifier 30 |
| T5 `_resolved` concepts obey the latest-period rule; non-TTM staleness guard; re-measure K7 after 9e77357 | Data Engineer + Period Engineer | lane 1 | K7 re-measured and published; named cases (CDNS, INTU, VRTX, LOW, MRSH) corrected or hidden |
| T6/T7 Z (evidenced-zero) detector for debt/dividends/buybacks; reason-rule audit (financial-institution reason on 142 non-financials, REIT-interest reason on 189 equity REITs, `no_dividend_history` at 502 payers) | Sector Analyst (detector audit); Data Engineer (rules) | lane 1 | zero contradicted reasons in the cohort (every reason rule gated on the company's own facts); Z detector 30 per group, zero false |
| T8 W6/W7 builder: growth over non-positive base, negative-denominator ratios as NM state (`ttm._growth_value`, `price_metrics`, `expanded_metrics`, `ratio.py`) | Data Engineer | lane 1 | RDDT YoY shows NM; zero numeric growth values on a non-positive base in the cohort (query); zero negative P/E, payout, PEG shown as numbers; PFE, Ford spot-checked |
| T9 fiscal labels | Period Engineer | | label derived from FY start/end equals SEC `fy`/`fp` for every cohort period since 2015; 224 companies / 322 duplicate-label groups (S022), not only the 24 |
| T10 split table (NVDA ~216 cells, GOOG double entry, WMT double adjust, AAPL, TSLA; refresh, not insert-only) and matching-copies dedupe (ANET balance sheet, 82 tag-periods S006) | Period Engineer + Data Engineer | joint | every new split row FILING-CHECKED before insert; NVDA fixed (Gate B); decimals-interval test for dedupe, ANET clean; Verifier 20 |
| T11 ProfitLoss + NCI guard (33 I; FCX TTM ~42% high) | Data Engineer | lane 1 | suppress where source is `ProfitLoss` and non-zero NCI exists for the context; FCX corrected or hidden |
| T12 / E4 / E14 | Tag Mapper | | as in section 4; plus derived total liabilities (~25 companies) needs a Standardization rule |
| E1 institutional-ownership overcount (204 blocked cells) | Data Engineer | lane 2 | share-base cause isolated; decision recorded; cells stay honestly blank until fixed |
| E2 scale/unit publish guard (MOS DPS 220,000 / yield 12,246, CHE NI, PLXS negative revenue, `EntityPublicFloat` x1000) | Data Engineer | lane 1 | named cases corrected or hidden; I4 zero unexplained |
| E3 EPS per class / non-standard EPS tag (ABNB, HXL `IncomeLossFromContinuingOperationsPerDilutedShare`; V, BRK, GOOGL) | Tag Mapper | | coexistence + zero-wrong Verifier sample |
| E5 MLP/LP vocabulary (`PartnersCapital*`, `DistributionMadeToLimitedPartner*`) | Tag Mapper | | EPD, PAA, MPLX equity filled; coexistence + sample |
| E8 10-KT transition filings (zero 10-KT rows; FERG) | Data Engineer + Period Engineer | lane 2 | Collector form allowlist includes 10-KT; FERG loaded; transition-period rule R5 B4 covers stub periods |
| E10 population status scan (Form 25/15, 20-F/40-F: WBD active at $77.8B, NUTR, BMO, BNS, AEM, CNI, IAU, SLV) | Data Engineer + Company Master | lane 2 | every named case classified; status changes FILING-CHECKED |
| E12 gross-margin guard (33 N; UNH 88.6%, ELV 89.1%, CVX 43.6%) | Data Engineer | lane 1 | the three cases corrected or hidden; guard where cost line is a partial cost line or `CostsAndExpenses` |
| E15 currency: suppress price ratios for non-USD reporters (CP, IMO) | Data Engineer | lane 2 | named cases suppressed with reason; certify I6 currency check |
| E16 market-cap lineage (META, ABNB, NET, CME, DDOG, V have NULL `source_fact_ids`) | Data Engineer | lane 2 | lineage populated or the cell hidden; "why this number" never shows a lineage that does not exist |
| W8 remove the TSY $0 default for unmapped dividends | Data Engineer | lane 1 | PFE TSY consistent with its 5.7% dividend yield or shown as unknown |
| Identity (id 1840), registrant rule, W3 authority gate | Data Engineer | lane 1 | as in section 4 (registrant rule per correction 2) |

### C. Acceptance tests for work orders that had none (Data Head)
- **WO-7 Triage:** every scoreboard figure reproducible by the Verifier from the stored query text, with watermark (`max(checked_at)`, `max(snapshot_date)`), both denominators and the hidden-by-guard count; first task: reconcile the contradictions in ALL-SHARDS section 5 (683 companies vs cells, 3,433 vs cells, 497 vs 477 shares); classify the 1,076 unexamined cells with a second 40-cell draw.
- **WO-8 Data Chief:** rewritten per Data Head section 6: A0 freeze register approved with the state-model decision; slot calendar (heavy DB, SEC fetch, Release Manager queue) with scrooner-4d by day 2; traceability matrix 28 of 28 themes with owner and acceptance test by Gate A exit; weekly ranking under the cap; failure tests every Friday; Verifier independence assignment.
- **WO-1 item 6** (`company_group`/`metric_template`): acceptance = design review passed, loader reproduces the frozen groups file exactly, rebuild twice gives identical rows. **Item 9** (certify I12/I13, currency, scale): acceptance = precision and recall measured per invariant on the 986 run before any gating (Data Head condition 8). **Item 10** (structure pilot): acceptance = measurement table only, runner-based, stop criteria K3 and 10 req/s approached.
- **WO-3.2 / 3.3** (structure candidate report; tag cards and era sets): acceptance = report lists agree/disagree/structure-only for the six concepts with the named filing-checked examples (NJR, Spire, TVA, Nikola, Photronics, DLH); each card cites a FILING-CHECKED case and an era range.
- **WO-4.2** (templates v1): acceptance = every cell in each template has a rule ID and a definition version; Triage can compute D1 from `template_version`.
- **WO-5.2** (conditional rulebook): acceptance = each conditional metric has condition, evidence, state, coverage treatment, propagation rule and UI wording; reviewed by the named accountant for the 13 items.

### D. Rules added
- **Verifier independence:** no family is verified by the agent or lane that proposed or tuned it.
- **Tag Mapper release split:** every vocabulary item is classified "synonym class" (company-scoped tag switch where the filer's own face row carries the same value in the overlap year, no coexisting component tag, coexistence checked population-wide: ships without the accountant if the founder adopts the class) or "composition" (waits for the accountant). Founder adoption needed (doc 49 section 9, item 11).
- **One rule registry** keyed by (group, data_point, rule) for all Tier 0 serve-time guards; every guard emits the frozen state enum and rule ID (`family.rule@version`), never free text; Tier 1 migrates rows into `metric_template`, not code.
- **SEC fetch rule (decided by Dhairya):** up to 3 concurrent SEC processes, combined cap 5 requests per second, declared User-Agent.
- **Incremental = full test:** the incremental resolve must equal the full resolve; every FILING-CHECKED case becomes a regression fixture; a nightly incremental certify reopens regressions.
- **Founder-visible Gate D split:** D(non-financial T1) and D(financial T1): the 15-20 financials in the top 100 cannot be certified without the named accountant.


### E. Gate A identity and registrant results (Verifier, 2026-10-22, FILING-CHECKED: `team/GATE-A-IDENTITY-REGISTRANT-CHECKS.md`) — replaces WO-1 item 2 and the E6/E7 parts of item 3
1. **WO-1 item 2 (identity master check) is rewritten.** The id 1840 premise ("no Equity Residential row, every page mislabeled, fix id 1840") was WRONG: CIK 906107 is correctly VIVMARK RESIDENTIAL / VMRK (Equity Residential renamed after merging with AvalonBay; 8-K 0001140361-26-033377). Do not rename. Real defects for Data Engineer lane 1: `display_name` 'AvalonBay Communities, Inc.' on id 1840; AvalonBay id 1895 status `active` though delisted/deregistered (25-NSE, 15-12G 0001104659-26-102433, 15-15D); EQR ticker history; market cap about half (pre-merger 374.9M shares vs about 773.7M post-merger); PSKY renamed Skydance Corp / SKYD; WBD acquired (15-12G 2026-10-16) still `active`; exclude subsidiary/bond/preferred pseudo-tickers from the universe and market cap; identity check compares against per-CIK submissions JSON.
2. **Shared-accession bug is OURS** (`normalizer/identity.py` never updates `company_id` on conflict; `normalizer/facts.py` assumes one company per filing). Rule candidate **P1**: the undimensioned `dei:EntityCentralIndexKey` names the primary filer, cross-checked with the submission header's first filer; disagreement quarantines the accession. Build P1, reload the 9 stale parent groups (SO, SRE, AEE, ETR, CTVA, EIX, CMS, ES, TXNM) plus Entergy under a reviewed dry-run, then **re-draw the cohort (986 / T1 / T2)**; freeze-register cohort lists are provisional until then.
3. **Reverse acquisition (id 1840).** AvalonBay is the accounting acquirer: the Q3 2026 10-Q (about early November) will carry AvalonBay's history under CIK 906107. A founder/accounting decision on the history basis is needed BEFORE that filing is ingested (same family as the Q4 restatement-basis decision).
4. **Second independent reader:** three readers agree on all 309 rows over 5 filings; 166 member rows are the regex reader's blind spot (use the second reader on the 10% subsample, Verifier C4).
