# Work-order addenda (Data Chief, 2026-10-22): script-evaluable acceptance tests, WO-14 to WO-28, theme traceability, Verifier independence

Status: PROPOSED for the three heads; amends doc 47 section 4 and its v2 sections B/C without editing them (Ritwik folds in). Planning only: no code, no DB writes, no commits. Register this file depends on: `../FREEZE-REGISTER-2026-10-22.md` (state enum, cell key, RF rule IDs, denominators, cohorts).
Evidence labels: FILING-CHECKED (inherited from the cited report; I opened no filing), DATA-INFERRED, CODE-READ, ASSUMED.

## 0. Conventions every test below follows
- **Executable form.** Each test is a function in `data-team/strategy/tools/acceptance/<wo>.py` returning `{test_id, passed, observed, expected, watermark, query_sha}`. The role that builds writes the script; the independent Verifier lane (section 4) runs it. A test with no script is NOT_RUN, never passed.
- **Read limits.** Read-only, one connection, `set statement_timeout = '60s'`, chunks of at most 100 company ids, never beside a heavy slot's forbidden reads (48-ENG (f)).
- **Scope.** "Cohort" = T2 of the freeze register (cohort file v1 minus EAI and PS) unless a test names T1. Every count test records `max(checked_at)`/`max(snapshot_date)`/run ids as its watermark.
- **Sample tiers (Verifier C2, doc 49 7.5).** H = hide-with-reason: 30 hidden cells + 10 risk cells; V = value-changing: 60 + 15 risk + 15 negative controls; P = 30; census when the population is 60 or fewer. "Zero wrong" and "hidden-correct = 0" are both required; any failure fixes the rule and re-runs the sample. A clean sample means "none found in this sample".
- **Named cases** are FILING-CHECKED in the cited report; the test compares our stored or shown value to the value recorded there, and the Verifier re-opens at least the T1 members.
- **Every guard test** also asserts: emitted state is from the frozen enum, `is_null_reason` (or the cell_state row) carries the rule ID `family.rule@N`, and the rollback flag of that rule ID restores the before-image exactly (diff = 0 on a 10-company subset).

## 1. Acceptance tests rewritten for the work orders that had none
### WO-7 Data Triage
| Test | Script computes | Pass |
|---|---|---|
| AT-7.1 | for every scoreboard figure, the query file `data-team/strategy/scoreboard/queries/<kpi>.sql` exists and re-running it at the recorded watermark returns the published integer | 100% of figures have a query; 100% equal |
| AT-7.2 | scoreboard header fields: `max(checked_at)` coverage, `max(snapshot_date)`, certify run id, cell_state run id, `template_version`, `definition_version`, register version | all present and non-null |
| AT-7.3 | D0 = 160,718 exactly; D0e = 131,138 (if D-2 adopted); D1 with `template_version`; per denominator, the sum of the eight state counts equals it | all equalities hold |
| AT-7.4 | hidden-by-guard (K1b) per rule ID; total equals count of `defect(guard_hidden)` in the cell_state run | equal |
| AT-7.5 | the three ALL-SHARDS section 5 contradictions (683 companies vs cells; 3,433 companies vs cells; 497 vs 477 blank shares) each restated with one query, one unit, one watermark | 3 of 3 |
| AT-7.6 | second draw of 40 cells from the reasonless set excluding S4's 40 (seed recorded), each labeled with a frozen state or defect class plus a locator; Verifier re-checks 4 | 40 of 40 labeled; the 4 re-checks recorded with any disagreement listed |
| AT-7.7 | defect register: every `defect` row has class and owner from the frozen enums | rows with null or non-enum class/owner = 0 |
| AT-7.8 | weekly K1a (valued, not hidden) on D0 and D0e, with the previous week beside it | present every Monday |

### WO-8 Data Chief
| Test | Script computes | Pass |
|---|---|---|
| AT-8.1 | the freeze register status line reads APPROVED with a date; doc 49 items 4, 5, 13 marked decided | both true |
| AT-8.2 | section 3 of this file parses to 28 theme rows, each with at least one RF id from the register, an owner from the frozen enum and a test id that exists in sections 1-2 | 28 of 28 |
| AT-8.3 | every heavy job to Gate C (S1-S3, R1-R4 trains, certify re-runs, recomputes) has a dated row in doc 53 with owner and `ciks` | missing = 0 |
| AT-8.4 | each weekly batch file: families <= 10, cases <= 50, every family an RF id, a reconciliation section for the previous batch | all true |
| AT-8.5 | Friday file per week: the five integrity checks of 48-HANDOVER 2.5 plus failure test 1 on K1a; when any is red, a "new builds stopped" line naming the red check | present by Friday 23:59 UTC; red implies stop line |
| AT-8.6 | for every released family: proposer/tuner lane differs from the verifier lane (section 4 table vs release records) | violations = 0 |
| AT-8.7 | at each gate, the doc 48 section 5 re-measure list: each item has a number, a query and a watermark | 100% |
| AT-8.8 | one daily note per working day (shipped, blocked, next, unblock request) | count = working days |

### WO-1 item 6 (`company_group`, `metric_template`)
| Test | Script computes | Pass |
|---|---|---|
| AT-1.6a | design review sign lines (Engineering Head, Data Head) dated before the first appearance of any D1/K3 figure in doc 53 or the scoreboard | 0 figures before the sign date |
| AT-1.6b | symmetric difference on (company_id, group, effective_from) between `company_group` (latest) and `data/group_assignment_v2.csv` | 0 rows |
| AT-1.6c | rebuild twice from the same inputs; sha256 of sorted rows of `company_group`, `metric_template` and the cell_state run | hashes equal |
| AT-1.6d | every `metric_template` row has rule code in {REQ, REP, COND}, a rule ID and a `definition_version`; every group lists all 133 economic lines as a row or an explicit `not_in_template` | nulls = 0; 133 per group |
| AT-1.6e | repoint the active `template_version` to the previous one; recompute D1 | equals the previous published D1 |

### WO-1 item 9 (certify I12/I13, currency, scale)
| Test | Script computes | Pass |
|---|---|---|
| AT-1.9a | every new rule has a row in `gate-a/rule_precision_recall.csv` (30 flagged + 30 passed or all, recall against the regression list cases of its class) before its severity may be `wrong_value` | rules with `wrong_value` severity and no measured row = 0 |
| AT-1.9b | recall on named cases: currency flags CP and IMO; scale flags MOS DPS 220,000 / yield 12,246, CHE net income FY2022-25, PLXS negative revenue, the 13 `EntityPublicFloat` cases of ALL-SHARDS E2 | 100% of named cases flagged |
| AT-1.9c | CI scratch DB: inserting invariants `I12` and `I13` into `certification_finding` succeeds after the 0097 amendment | both inserts succeed |
| AT-1.9d | any rule with more than half false in its 30 flagged is demoted to `review` (K2) | demotions applied = rules over threshold |

### WO-1 item 10 (structure pilot)
| Test | Script computes | Pass |
|---|---|---|
| AT-1.10a | the only outputs are `data/structure_pilot_measurement.csv` (quarter, file, bytes read, rows, accessions, join rate to `core.filing`, runtime, peak req/s) and code; the diff adds no migration | file present; migrations in diff = 0 |
| AT-1.10b | run id of the GitHub runner job recorded; no SEC bulk file written to the Mac | run id present |
| AT-1.10c | stop rules logged: join miss over 5% of accessions (K3), a refused Range read, or peak combined rate over 5 req/s per host | each stop condition checked and logged; run stopped if any fired |
| AT-1.10d | CVX `CostsAndExpenses` calc children include `InterestExpenseDebt` (ledger 2026-10-19, 0000093410-26-000078 cal), plus XOM and AMD cases reproduced from `cal.tsv` | 3 of 3 match the ledger |

### WO-3 items 2-3 (structure candidate report; tag cards and era sets)
| Test | Script computes | Pass |
|---|---|---|
| AT-3.2a | for revenue, D&A, capex, interest, debt, operating income: agree + disagree + structure-only = scanned population per concept | 6 of 6 sums equal |
| AT-3.2b | NJR, Spire, TVA, Nikola, Photronics, DLH each present with accession and calc path, category equal to strategy/39's filing-checked classification | 6 of 6 |
| AT-3.2c | rows that would map a custom tag globally | 0 (every custom-tag row company-scoped with accession) |
| AT-3.2d | Verifier P-tier check on 12 report rows before any row becomes a mapping proposal | 0 disagreements |
| AT-3.3a | `tags/cards/capex.md` and a D&A card exist; each listed tag has at least one FILING-CHECKED case (accession + R-file) and an era range with its source query | 100% of listed tags |
| AT-3.3b | every era-scoped tag (e.g. `SalesRevenueGoodsNet`; the 2024 interest-expense break) has `valid_from` and `valid_to` or an explicit open bound | missing bounds = 0 |
| AT-3.3c | `INDEX.md` and `CHANGELOG.md` updated; inbox lines the cards rely on marked processed | true |

### WO-4 item 2 (templates v1)
| Test | Script computes | Pass |
|---|---|---|
| AT-4.2a | every cell of every template (corporate with utility/energy/midstream variants, bank, insurer, equity REIT, mortgage REIT, BDC/fund, pre-revenue overlay, managed care/insurance broker/exchange variants) has a rule ID and `definition_version` | nulls = 0 |
| AT-4.2b | D1 computed from `company_group` + `metric_template` only, by Triage, reproduced by the Verifier | equal |
| AT-4.2c | every `not_in_template` cell cites an S3 section 6 row or a new reason; every REP cell cites a Standardization definition id with status | missing = 0 |
| AT-4.2d | each of the 133 economic lines appears in each template | 133 per template |
| AT-4.2e | visible metric set per group signed by the Head of Data Product within the doc 02 guardrail | sign line present per group |

### WO-5 item 2 (conditional rulebook)
| Test | Script computes | Pass |
|---|---|---|
| AT-5.2a | each conditional data point in S3 section 3 has six non-empty fields: condition, evidence, frozen state, coverage treatment, propagation rule (P1-P10), wording key | N of N |
| AT-5.2b | each wording key exists in the wording catalog | missing = 0 |
| AT-5.2c | each of the 13 S3 section 7 items has a decision record (approved/rejected/pending, accountant name, date); rows depending on a pending item map to `defect(definition_pending)` | 13 of 13 records; dependents mapped |
| AT-5.2d | each state rule has at least one FILING-CHECKED positive and one negative fixture (e.g. RDDT 0001713445-26-000022 R5/R8 for growth over a negative base; PFE 0000078003-26-000095 R8 as a payer that must not become evidenced zero) | 100% of rules |

## 2. New work orders WO-14 to WO-28 (ticket-ready)
Common to all: release path of doc 47 rule 1 (classify into the RF family, dry-run table of proposed writes, Verifier tier sample, Release Manager commit by named paths, separate first live run on 10 companies then the cohort, certify re-run). No accountant needed unless stated: every Tier 0 item here only hides with a reason or applies arithmetic. Budget cap per WO: one proposal pass, one review pass, one revision pass (data-team/10 work limits).

### WO-14 Operating-income guard (T2) — RF-14 `oi.derived_not_face@1`
Owner: data_engineer_l1. Rule review: Standardization Lead (classification identities are arithmetic). Verifier: V-B. Train R2 (operating income has 5 consumers, doc 49 7.6).
Facts: `conflict_resolution.py::resolve_operating_income_arithmetic_fallback` (CODE-READ, L1384) writes `operating_income_resolved` = revenue - `operating_expenses_resolved` - cost of revenue wherever no OI row exists; its own docstring states 85.5-90.3% land within 2% of a real value. Shards: 168 companies on the two-input derivation, 103 with a 2026 period (S023, DATA-INFERRED); segment-note OI read as consolidated (MET, HONA, MOG-A); pretax labelled as OI (AFG 0001042046-26-000010 R5, ELS 0001628280-26-008722 R5, ledger).
Steps: (1) list every fallback cell (operating_income_resolved row with no `operating_income` base row for the same company and period); (2) keep a fallback value only where the filer's own face satisfies an identity in the overlap periods (revenue - OpEx = OI, or GP - OpEx = OI, ledger HP/XOM classification) — else hide; (3) hide any OI fact not on the income statement role (segment note); (4) hide any OI value equal to the same filing's pretax income with an income-tax row next; (5) metrics consuming OI carry the passthrough state.
| Test | Pass |
|---|---|
| AT-14.1 fallback census: count of fallback cells and companies in the population and cohort, with watermark | published; re-measures S023's 168 |
| AT-14.2 cohort cells shown where source = fallback AND no identity passed | 0 |
| AT-14.3 AFG, ELS, MET, HONA, MOG-A, DVN, AJG, ELV, CASY each corrected or `defect(composition)` with the rule ID | 9 of 9 |
| AT-14.4 Verifier tier H (30 hidden + 10 risk) zero wrong; hidden-correct = 0, including 15 negative controls where the fallback equals a face OI | both zero |
| AT-14.5 `operating_margin`, `roic`, `interest_coverage_ratio`, `ebitda` non-null where their OI input is hidden | 0 |

### WO-15 Undefined-by-math states for growth and ratios (T8; W6/W7) — RF-06, RF-07
Owner: data_engineer_l1 (`ttm._growth_value`, `fcf_growth.py`, `price_metrics.py`, `expanded_metrics.py`, `calculate_shapes/ratio.py`). Verifier: V-A. Train R2 at the metric stage (trailing P/E and EPS growth feed PEG); R1 may hide the true leaves first (doc 49 R1 list). Interim wording is a guard; final wording waits on S3 section 7 items 1 and 3 (accountant), and adds a metric version, never a backfill.
| Test | Pass |
|---|---|
| AT-15.1 cohort latest rows of every YoY growth metric with prior value <= 0 or below the materiality floor and a non-null value (replica of S3 Q2 on `canonical_fact`) | 0 (baseline 123 NI, 122 EPS) |
| AT-15.2 CAGRs with start or end <= 0 and a non-null value | 0 (baseline 72/72/24 NI, 66/71/26 EPS) |
| AT-15.3 non-null `trailing_pe` < 0; `payout_ratio` with EPS <= 0; `peg_ratio` with P/E <= 0 or growth <= 0; `price_to_book`, `roe`, `debt_to_equity` with equity <= 0; `ev_ebitda`, `net_debt_ebitda` with EBITDA <= 0; `ocf_to_net_income` with NI <= 0 | 0 each |
| AT-15.4 negative results on positive denominators unchanged (negative operating margin, FCF yield, ROE on positive equity): before/after diff | 0 changed |
| AT-15.5 RDDT `net_income_growth_yoy` NM (0001713445-26-000022 R5/R8); Ford 5y NI CAGR NM; TAP 3y CAGR NM; PFE payout NM; Ford PEG NM | 5 of 5 |
| AT-15.6 each NM cell carries `math.*@1` and names its input | 100% |

### WO-16 Institutional-ownership overcount (E1) — RF-47
Owner: data_engineer_l2 (`ownership/`). Verifier: V-B. Tier 2; cells stay honestly blank meanwhile (S3: an over-100% value is a denominator defect, never NM). Product rule kept: never sum institutional and mutual-fund percentages (`doc/scoping/insider_info.md`).
| Test | Pass |
|---|---|
| AT-16.1 cause attribution for CCK, FIVE, HSIC, SAIA, OC, MDGL, DPZ plus 30 random companies from the `implausible:institutional_shares_exceed_shares_outstanding` population: duplicate filer rows / amendment rows / sub-adviser or option legs / wrong share base, each with 13F accession lines | 37 of 37 attributed |
| AT-16.2 the 683 unit dispute restated (companies and cells, one query) | done |
| AT-16.3 decision record (fix design or stays blank) with the cause shares | recorded |
| AT-16.4 after any fix: displayed `institutional_ownership_pct` > 100% | 0, and the guard count falls |
| AT-16.5 fixed values: Verifier tier V against the 13F filings | zero wrong |

### WO-17 EPS per class and non-standard EPS tags (E3) — RF-44
Owner: tag_mapper with Tag Expert; per-class display policy: Standardization Lead. Verifier: V-A. Tier 2.
Caution recorded for the card: `IncomeLossFromContinuingOperationsPerDilutedShare` (ABNB, HXL) is continuing-operations EPS; it equals total diluted EPS only when the period has no discontinued operations, so it is a conditional synonym, not a plain one (ledger ANDE 0000821026-26-000010 R3 shows the same switch).
| Test | Pass |
|---|---|
| AT-17.1 full-population coexistence of the continuing-ops tag with `EarningsPerShareDiluted` in the same context: both-present count, equality count, and every unequal case with a discontinued-ops EPS fact | published |
| AT-17.2 rule accepts the continuing-ops value only when no discontinued-ops EPS fact exists for the context and the face row is the total EPS; 12-case filing sample (30 if over 1,000 companies) | zero wrong |
| AT-17.3 ABNB and HXL diluted EPS filled; HSY, MNST, VRSN stale EPS filled or hidden with the rule ID | 5 of 5 |
| AT-17.4 per-class issuers (V, BRK, GOOGL): decision record naming the class shown and its label; EPS summed across classes | record present; summed values = 0 |
| AT-17.5 Verifier tier V | zero wrong |

### WO-18 Partnership equity and distributions (E5) — RF-45
Owner: tag_mapper. Verifier: V-B. Tier 2. Equity side may use the synonym class (founder item 11); distributions as dividends to common holders is S3 section 7 item 10 (accountant).
| Test | Pass |
|---|---|
| AT-18.1 population coexistence of `PartnersCapital`, `PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest` and `StockholdersEquity` in the same context | published |
| AT-18.2 EPD, PAA, MPLX, ET, CQP, WES equity equals the face "Total partners' equity" (CQP 754,000K at 2026-06-30, 0001383650-26-000028 R3) | 6 of 6 |
| AT-18.3 an NCI-inclusive partners' capital tag mapped as attributable equity | 0 |
| AT-18.4 distribution-based dividend cells stay `defect(definition_pending)` until the accountant rules item 10 | 0 shown as dividends before the ruling |
| AT-18.5 Verifier tier V | zero wrong |

### WO-19 10-KT transition filings (E8) — RF-42
Owner: data_engineer_l2 (Collector form allowlist; the Collector stays lossless) + period_engineer (rule R5 B4 `TRANSITION_PERIOD`). Verifier: V-A. Tier 2. History gate (doc 38) applies: 2015+.
| Test | Pass |
|---|---|
| AT-19.1 per cohort company, 10-KT and 10-KT/A since 2015 in `core.filing` vs in SEC submissions | difference 0 (baseline: 0 rows in `core.filing`, S027) |
| AT-19.2 FERG 10-KT 0002011641-26-000006 loaded with facts; Aug-Dec 2025 revenue 12,833M and NI 786M stored on grain `TP`, not `FY` | true |
| AT-19.3 metric values whose source period is a `TP` stub used as a FY or a TTM leg | 0 |
| AT-19.4 FERG fiscal labels for Jan-Mar and Apr-Jun 2026 equal SEC `fy=2026`, `fp=Q1`/`Q2` | true |
| AT-19.5 SEC fetch through the shared limiter; reviewed dry-run before any write | logged |

### WO-20 Gross-margin guard on a partial cost line (E12) — RF-16
Owner: data_engineer_l1. Rule card: Standardization NA-12 option (a), hide-only. Verifier: V-B. Train R2 at the `cost_of_revenue` input (4 consumers incl. inventory and payables days; `gross_profit_resolved` feeds Piotroski).
| Test | Pass |
|---|---|
| AT-20.1 cohort cells shown for `gross_margin`, `gross_profit_resolved` or `cost_of_revenue_resolved` whose cost input comes from `CostsAndExpenses`, from a member-only row, or from a tag the face does not present as cost of revenue | 0 |
| AT-20.2 UNH 88.6%, ELV 89.1%, CVX 43.6%, WM, EPD, CI, COP, RCL, RSG, KMI, MPC, CNP corrected or hidden with the rule ID | 12 of 12 |
| AT-20.3 consumers (`inventory_days`, `payables_days`, `piotroski_f_score`, `margin_expanding_3yr`) non-null where the input is hidden | 0 |
| AT-20.4 Verifier tier H zero wrong; hidden-correct = 0 with 15 negative controls where the cost line is the face cost of revenue | both zero |

### WO-21 Market-cap publish guard at the share basis (T4) — RF-15
Owner: data_engineer_l1. Method decision (multi-class market cap = sum over classes at each class's price, or at the listed price for unlisted classes): Standardization Lead, as an arithmetic NA card before build. Verifier: V-A. Train R2 (market cap 7 consumers; shares outstanding 12).
| Test | Pass |
|---|---|
| AT-21.1 AKTX, TBLA, RPAY, ZLAB, SCNI, KZIA, DBVT, AMRN, GPCR (ADS ratio or x1000 WASO, S000) market cap hidden or corrected; SPCX corrected by the class sum or hidden | 10 of 10 |
| AT-21.2 cohort market caps computed from a WASO fallback that failed the plausibility rule (rule version holds the bound) | 0 |
| AT-21.3 certify I4 market cap vs price x cover shares: breaks over 3 orders of magnitude without an explanation row | 0; every break over 1.5x listed with a reason |
| AT-21.4 the 7 consumers non-null where market cap is hidden | 0 |
| AT-21.5 market cap computed for a non-common security (EAI: 466.6M shares x another security's price) | 0 |
| AT-21.6 Verifier tier H zero wrong; hidden-correct = 0 | both zero |

### WO-22 Split basis (T10, T4) — RF-22
Owner: period_engineer (rule) + data_engineer_l1 (single writer; `split_event`, `filing_share_basis`, archive-then-replace into `canonical_fact_retired`; migrations 0098/0099 claimed in doc 53 first). Verifier: V-B. Train R4.
| Test | Pass |
|---|---|
| AT-22.1 `split_event` rows without a FILING-CHECKED accession and locator | 0 |
| AT-22.2 NVDA (2024 10-for-1 on duration contexts; 2021 4-for-1 counted once), GOOG (20:1 once), WMT (FY2024 EPS 1.92 not re-divided), AAPL shares re-based, TSLA, KLAC: every cell on the data-team/36 list equals the filing-derived expected value | 100% of listed cells (NVDA about 216) |
| AT-22.3 certify `split_ratio_counted_twice`, `per_share_basis_mix`, `share_basis_mismatch`, `share_jump_without_split` findings for those six companies | 0 |
| AT-22.4 synthetic split for one fixture company in a scratch schema: changed cells outside that company | 0 |
| AT-22.5 idempotency: second run on unchanged inputs changes | 0 cells |
| AT-22.6 every replaced `canonical_fact` row present in `canonical_fact_retired` with `superseded_by` | 100% |

### WO-23 Matching copies are not conflicts (T10) — RF-46
Owner: data_engineer_l1 + period_engineer (Normalizer Stage 2e `dedupe.py`; the decimals-interval rule of domain rule 8.4 and the XBRL duplicates guidance in data-team/03). Verifier: V-A. Tier 2 (adds values, value-changing tier).
| Test | Pass |
|---|---|
| AT-23.1 unit tests: TTWO 3,372,772K vs 3,372.8M consistent (prefer the larger `decimals` copy); ANET 14,043,921,000 vs 14,043,900,000 consistent; company 8 FY2023 copies differing 5-10x stay a conflict | 3 of 3 |
| AT-23.2 ANET 2024-12-31 balance sheet concepts with a canonical value after the change | all that had only rounding-consistent copies |
| AT-23.3 S006's 82 tag-periods each resolved or still a conflict with a reason | 82 of 82 classified |
| AT-23.4 population dry-run: periods changing from conflict to authoritative where decimals intervals do not overlap | 0 |
| AT-23.5 Verifier tier V, negative controls drawn from real material conflicts | zero wrong |

### WO-24 ProfitLoss with non-controlling interest (T11) — RF-17
Owner: data_engineer_l1. Verifier: V-B. Train R2 (net income 12 consumers). Tier 0 hides only; attributable-first precedence is WO-5.1 (net income attributable to parent, accountant).
| Test | Pass |
|---|---|
| AT-24.1 cohort `net_income_resolved` cells shown whose source tag is `ProfitLoss` while a non-zero NCI net income fact exists for the same company and period | 0 |
| AT-24.2 FCX (Q1 2026 1,387M vs 881M attributable, 0000831259-26-000036 R3), CMI (968M vs 932M, 0000026172-26-000029 R2), SPG, QSR, O, IRM and the rest of the ALL-SHARDS T11 FC list hidden or correct | 100% of the list |
| AT-24.3 `ProfitLoss` with zero or absent NCI stays shown: 15 negative controls | hidden-correct = 0 |
| AT-24.4 the same guard for equity from `...IncludingPortionAttributableToNoncontrollingInterest` with non-zero NCI (T 15,990; CL 236M vs 566M) | 0 shown |
| AT-24.5 TTM and the 12 consumers non-null where the input is hidden | 0 |
| AT-24.6 population count of `ProfitLoss`-sourced net income re-measured (S062 said 231 of 5,210, method not shown) | published with query |

### WO-25 Reason-rule audit (T7) — RF-34
Owner: sector_analyst (audit) + data_engineer_l1 (rules). Files belong to lane B (`coverage_matrix.py`, `company_coverage_dashboard.py`): lane B agrees before any edit (doc 53). Verifier: V-A. Gate C (reason text only; R1 for W9).
| Test | Pass |
|---|---|
| AT-25.1 inventory of every reason rule in `coverage_matrix.py`, `company_coverage_dashboard.py`, `common/sector_applicability.py` with its trigger (SIC, tag, fact, filing evidence) | 100% listed |
| AT-25.2 rules triggered by SIC alone or by a tag test with no period, size or group limit (unit test over the inventory) | 0 |
| AT-25.3 contradiction counts in the cohort: financial-institution reason on a non-financial group (was 142 of 328); REIT net-interest reason on `reit_equity` (189 companies / 789 cells); `no_dividend_history` where `dividends_paid` has a value in the window (502); pre-revenue reason where TTM revenue >= $1M (44 cohort) | 0 each |
| AT-25.4 SCHW, HCA, TRV, EOG, HOOD, UAL, CCL, WAT, HRB, BLCO, CAI: `line_not_presented_in_filing` or `line_in_filing_not_extracted` contradicted by the face, fixed | 11 of 11 |
| AT-25.5 Verifier P tier: 30 sampled reasons per surviving rule | zero contradicted |

### WO-26 Population status scan (E10) — RF-25
Owner: data_engineer_l2 + company_master (Company Master never asserts `delisted` without a real source, `pipeline/CLAUDE.md`). Verifier: V-B. Train R2.
| Test | Pass |
|---|---|
| AT-26.1 for every active company: latest Form 25/25-NSE, 15-12B/G, 15-15D, and latest annual form since 2015 (10-K vs 20-F/40-F) from SEC submissions | table for 100% of active companies |
| AT-26.2 WBD (8-K 0001193125-26-415055; 15-12G 0001193125-26-423513) not active and no current market cap | true |
| AT-26.3 BMO, BNS, AEM, CNI, KZIA, SCNI, ZLAB (FPI) and IAU, SLV (trusts) classified out of the operating population with accession; NUTR classified | 10 of 10 |
| AT-26.4 companies shown with a current market cap after a Form 25 effective date | 0 |
| AT-26.5 status-change rows without an accession | 0 |

### WO-27 Scale and unit publish guard (E2) — RF-18
Owner: data_engineer_l1. Verifier: V-A. Train R2 at the input (`dividends_per_share` 6 consumers). DEF 14A thousands-as-dollars (CHE, SCHW) is closed by RF-03; negative annual revenue is certify I3 quarantine; WASO scale is WO-21.
| Test | Pass |
|---|---|
| AT-27.1 MOS DPS 220,000 and yield 12,246 hidden or corrected; CHE NI FY2022-25 equals 265.2M-scale filed values or hidden; PLXS negative revenue hidden; the 13 `EntityPublicFloat` cases (ONTO, TTMI, SKY, OLED, NOVT, ENVA, CBT, WTTR, CRD-A, RPAY; ARES, LB, PTCT) hidden as `public_float` | 16 of 16 |
| AT-27.2 certify I4 scale breaks over 3 orders of magnitude without an explanation row | 0 |
| AT-27.3 `dividends_per_share_resolved` shown with absolute value >= 1,000 not FILING-CHECKED (S096 baseline 140 rows / 39 companies) | 0 |
| AT-27.4 negative controls: genuinely large per-share values (BRK-A class A EPS once admitted; high-price issuers) stay shown | hidden-correct = 0 |
| AT-27.5 `EntityPublicFloat` outside $1M-$10T (DQC_0222) shown | 0 |

### WO-28 Reporting-currency guard (E15) — RF-19
Owner: data_engineer_l2. Verifier: V-B. Train R2 at market cap. Product question for the Head of Data Product (not founder): V1 is USD only (CLAUDE.md), so decide whether non-USD statements are shown with a currency label or hidden; default here hides only the price ratios.
| Test | Pass |
|---|---|
| AT-28.1 reporting currency per cohort company recorded from the unit of its monetary facts in the latest 10-K/10-Q | 100% recorded; count of non-USD reporters published |
| AT-28.2 CP (0000016875-26-000026) and IMO price ratios (P/E, P/B, P/S, yields, EV multiples) hidden with the rule ID | 2 of 2 companies, all ratios |
| AT-28.3 cohort cells combining a USD price with a non-USD statement value | 0 |
| AT-28.4 certify currency check (I6 `wrong_unit_family` or a new rule) flags every non-USD reporter | recall 100% on the count from AT-28.1 |

## 3. Traceability: 28 of 28 themes (owner and acceptance test; tests prefixed AT-47 are doc 47 v2 section B rows, which still need script form by their owners)
| Theme | RF | Owner | Work order | Acceptance test ids |
|---|---|---|---|---|
| T1 revenue partial/sub-line | RF-13, RF-48 | data_engineer_l1 (guard); tag_mapper + standardization_lead (structure rule) | doc 47 v2 B (build), WO-3 | data-team/37 section 8 (30 of 30, incl. EMR and NTAP both directions); AT-3.2a-d |
| T2 operating income derived | RF-14 | data_engineer_l1 | WO-14 | AT-14.1-14.5 |
| T3 zero-fact / unregistered filing | RF-40, RF-41 | data_engineer_l2 | WO-1.8 | AT-47 T3 (every named case listed, zero false positives in a 20-case check); reader 100% on 50 filings |
| T4 shares, market cap, per-share cascade | RF-10, RF-15, RF-22 | data_engineer_l1; period_engineer | WO-1.7, WO-21, WO-22 | AAPL 0000320193-26-000020 shows 7.36 at 2026-06-27; AT-21.1-21.6; AT-22.1-22.6 |
| T5 stale series as filled | RF-02, RF-23 | data_engineer_l2; data_engineer_l1 + period_engineer | WO-2.1 (W2), doc 47 v2 B (T5) | Verifier AAL clean; K7 re-measured; CDNS, INTU, VRTX, LOW, MRSH corrected or hidden |
| T6 true zero / total debt | RF-08, RF-11, RF-36, RF-43 | data_engineer_l1; sector_analyst; tag_mapper | held guards (R3), WO-3.1, WO-4 (Z detector) | R3 criteria (doc 49 section 4); Z detector 30 per group zero false; PFE TSY consistent with its dividend yield |
| T7 wrong or missing reasons | RF-09, RF-30, RF-33, RF-34, RF-38 | data_engineer_l1; sector_analyst | WO-1.5, WO-25 | K2 = 0 at Gate C; AT-25.1-25.5 |
| T8 negative / meaningless ratios | RF-06, RF-07 | data_engineer_l1 | WO-15 | AT-15.1-15.6 |
| T9 fiscal labels | RF-05 | period_engineer | WO-2.1 (W5) | label from FY start/end equals SEC `fy`/`fp` for every cohort period since 2015 (224 companies / 322 groups, S022) |
| T10 recast, split, matching copies | RF-04, RF-22, RF-46 | period_engineer; data_engineer_l1 | WO-2.4, WO-22, WO-23 | Verifier HON clean; AT-22.*; AT-23.* |
| T11 net income basis / NCI | RF-17, RF-03 | data_engineer_l1 | WO-24, WO-1.4 | AT-24.1-24.6 |
| T12 capex, D&A, interest, AR tags | RF-43 | tag_mapper | WO-3.1, WO-3.3 | coexistence + zero-wrong Verifier sample per mapping; AT-3.3a-c |
| E1 institutional overcount | RF-47 | data_engineer_l2 | WO-16 | AT-16.1-16.5 |
| E2 scale and unit | RF-18, RF-15, RF-03 | data_engineer_l1 | WO-27, WO-21 | AT-27.1-27.5 |
| E3 EPS per class / non-standard tag | RF-44 | tag_mapper | WO-17 | AT-17.1-17.5 |
| E4 dividends / DPS | RF-08, RF-12, RF-36 | data_engineer_l1; period_engineer | WO-3.1, WO-2.3, held guards | Visa FY DPS corrected or hidden (Gate B); V and LEA rate-on-YTD sample |
| E5 partnership tags | RF-45 | tag_mapper | WO-18 | AT-18.1-18.5 |
| E6 multi-registrant filings | RF-21 | data_engineer_l1 | WO-1.3 (rewritten) | Entergy Arkansas no longer holds Entergy Corp revenue/assets (0000065984-26-000174); Gate A A14 |
| E7 identity | RF-20, RF-49 | data_engineer_l1 | WO-1.2 | zero CIK/name/ticker disagreements or each logged; id 1840 corrected |
| E8 10-KT | RF-42 | data_engineer_l2 + period_engineer | WO-19 | AT-19.1-19.5 |
| E9 predecessor / successor / IPO | RF-37, RF-49 | period_engineer + company_master | WO-2.5 | each link FILING-CHECKED (8-K12B/G3 or 10-K predecessor statement); XOM history joined |
| E10 population / scope | RF-25 | data_engineer_l2 + company_master | WO-26 | AT-26.1-26.5 |
| E11 sector templates | RF-31, RF-32 | sector_analyst + standardization_lead | WO-4.1, WO-4.2 | zero wrong memberships in 30 per group; AT-4.2a-e |
| E12 partial cost line | RF-16 | data_engineer_l1 | WO-20 | AT-20.1-20.4 |
| E13 Q4/TTM, YTD cash flow | RF-01, RF-12, RF-50 | data_engineer_l2; period_engineer | WO-2.1-2.3 | Verifier MasTec clean; COST calendar windows; no derived Q4 EPS/DPS |
| E14 face line present, concept blank | RF-43 | tag_mapper (+ standardization_lead for derived total liabilities) | WO-3.1 | per-mapping coexistence + sample; derived-total-liabilities rule card with fixtures |
| E15 reporting currency | RF-19 | data_engineer_l2 | WO-28 | AT-28.1-28.4 |
| E16 provenance | RF-24, RF-03 | data_engineer_l2 | doc 47 v2 B (E16), WO-1.4 | META, ABNB, NET, CME, DDOG, V market-cap lineage populated or hidden; "why this number" never shows absent lineage |

## 4. Verifier independence assignment (no family is verified by its proposer or tuner)
Two Verifier sessions through the shared fetch queue (doc 49 7.5 C5). V-A and V-B are lanes, not people; a session that proposed or tuned a family may not verify it.
| Lane | Verifies | Must not verify |
|---|---|---|
| V-A | WO-15, WO-17, WO-19, WO-21, WO-23, WO-25, WO-27; Entergy mechanism (A14); period families RF-01/02/04/05/12/22 when proposed by the Period Engineer | anything V-A proposed (e.g. a detector it helped tune) |
| V-B | Gate A per-rule precision and recall (the certify precision study, data-team/36, was Verifier-authored, so V-B must be a session that did not author 36); WO-14, WO-16, WO-18, WO-20, WO-22, WO-24, WO-26, WO-28; held guards R3 | certify rules it tuned after Gate A |
| Either | group audits and detector audits (Sector Analyst proposes) | the session that drew the audit sample cannot also adjudicate it |

## 5. Untested scope
NOT_RUN: no script exists yet for any test above; baselines are copied from the cited reports (DATA-INFERRED unless marked); no filing was opened for this file; consumer counts are from doc 49 7.6 (`metric_dependency_graph.csv`), not recomputed.
