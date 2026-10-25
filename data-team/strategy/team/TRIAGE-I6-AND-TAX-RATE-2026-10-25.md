# Triage: I6 wrong_value families and effective_tax_rate_reported (2026-10-25)

Role: Data Triage. Read-only. Query revision: findings artifacts of GitHub run 40094543570 (scrooner-certify, dry-run, 2026-10-24), 92 `certify-findings/S###.json` files downloaded with `gh run download`; cohort = `doc/data-moat/team/top1000/shards.csv` rows with an empty `excluded` column (986 of 1,014). Cell = distinct (company_id, data_point_name, period_end).

## Scope corrections (read first)
1. **Run 40094543570 is incomplete.** Its job failed: shards S024 S047 S056 S065 S068 S073 S078 S085 S101 S102 failed or hit the 1800s cap (S102 had no non-excluded company). Those shards hold 94 shard-rows (rows, not all non-excluded) of the 1,014. Every count below is a **lower bound** for the cohort; the 94 are untested.
2. **The two families are in different invariants.** The 6,245 `wrong_value` findings are I6 *source integrity* (source form, authority, unit, value vs source), not arithmetic. The 5,079 effective-tax-rate findings are **I8 `per_share_derived_by_subtraction`** (a derived Q4/interim rate built by subtraction), not I6. Genuine arithmetic wrong_values (I1 4,532, I3 1,398, I4 667, I5 944, I9 8,034, other I8) are not in this triage.
3. All 6,245 I6 and all 5,079 tax findings are for cohort companies (252 and 618 companies). Findings = cells for the tax family (5,079 unique cells). For I6, 6,245 findings = 4,221 distinct cells (a cell can carry several findings; 129 cells carry both `non_periodic_form` and `differs_from_authoritative_copy`).
4. Not run by me: ListAgents (no such tool in this role). I used one read-only connection, `statement_timeout=60000`, ids in chunks of 150-400; 19 sessions were visible in pg_stat_activity at the start. No writes.

## Ranked table (by cohort cells)

| Rank | Family | Findings | Cohort cells | Companies | Root cause class | Evidence level | Owner |
|---|---|---|---|---|---|---|---|
| 1 | effective_tax_rate_reported, `per_share_derived_by_subtraction` (I8) | 5,079 | 5,079 | 618 | Derived value built by a forbidden method (Q4 = FY rate minus 9M rate; rate is unit `pure`, non-additive) | Class FILING-CHECKED (13 of 13 sampled cells wrong, 1 NOT-VERIFIED). Per cell DATA-INFERRED | Data Engineer |
| 2 | I6 `wrong_unit_family` | 3,822 | 2,623 | 9 | Non-USD facts in USD slots: reporting-currency policy absent (CP, IMO) plus unit gates missing on a few tags | Mixed, see split | Standardization (policy), Data Engineer (gate) |
| 3 | I6 `reit_calculated_subtotal` | 1,655 | 1,025 | 32 | Subtotals (gross profit, operating income, operating expenses) built for REITs whose face statements have none | Class FILING-CHECKED (DOC 10 of 10); definition question on OHI | Standardization |
| 4 | I6 `differs_from_authoritative_copy` | 413 | 407 | 175 | Displayed value is a non-authoritative copy (older vintage, or DEF 14A) that differs from authoritative copies; 129 cells overlap family 5 | Mixed, see split | Data Engineer |
| 5 | I6 `non_periodic_form` | 252 | 192 | 64 | Proxy-statement (DEF 14A / DEFR14A) net income displayed: rounded or unscaled | Class FILING-CHECKED (ledger 2026-10-18 AEMD; 2026-10-22 JPM); per cell DATA-INFERRED | Data Engineer |
| 6 | I6 `mixed_vintage` | 81 | 81 | 27 | Calculated cell whose inputs come from different filings (8-K recast plus original 10-K/10-Q) | FILING-CHECKED for LLY; AVGO refuted (false positive) | Data Engineer |
| 7 | I6 `sign_flip_between_copies` | 18 | 18 | 11 | Displayed copy has the opposite sign of the majority of other filings (1 vs 2-3) | DATA-INFERRED | Data Engineer (Tag Mapper consult on sign convention) |
| 8 | I6 `cross_vintage_arithmetic` | 4 | 4 | 3 | Derived by a-b with inputs filed 375 days apart | DATA-INFERRED | Data Engineer |

I6 total: 6,245 findings, 4,221 distinct cells, 252 companies. Tax: 5,079 cells, 618 companies.

## 1. effective_tax_rate_reported (5,079 cells, 618 companies)
- Evidence in the artifacts: all 5,079 are tag `EffectiveIncomeTaxRateContinuingOperations`, `rule=per_share_derived_by_subtraction`, `method_policy=true`, `value_checked=false`. `value_status`: differs_from_recompute 4,687; no_recompute_inputs 333 (an unsourced number, no filed Q4 figure and no inputs); consistent_with_recompute 59. Of 4,746 cells with a recompute (Q4 tax / Q4 pretax from stored facts), only 41 are within 0.005 of the stored rate. 39 are on YTD context. Period-end months: 2,835 are December, i.e. mostly derived Q4.
- Prior FILING-CHECKED samples (not mine, re-cited): CERTIFY-HELDOUT-VALIDATION-2026-10-22 (7 of 7 wrong, e.g. PGR 10-K 0000080661-24-000007 R3: stored -0.404, true 20.6%), CERTIFY-ROUND3-VALIDATION-2026-10-23 (6 of 6 wrong, e.g. NRG 10-K 0001013871-22-000010 R3: stored -0.787, true 28.2%). One NOT-VERIFIED (MPC Q4 2018). Arithmetic is invalid by construction: a Q4 rate cannot be obtained by subtracting a 9-month rate from a full-year rate.
- Root cause is in code that exists: `normalizer/derived.py` in the working tree (uncommitted, plus untracked `common/derivation_policy.py`) now stops deriving for `pure`/ratio units, which covers this tag. The comment there states stored rows from before the change are NOT retired and need their own reviewed dry-run. So the 5,079 are old stored derived facts (e.g. fact 77587072), not a pending nightly regression.
- Next action (Data Engineer): commit the deriver gate; write a retirement migration for derived (is_derived) facts on ratio-unit concepts; reviewed dry-run first (cell list = the 5,079 plus whatever the 10 missing shards add). After retirement the cell is blank with a reason; whether a recomputed Q4 rate from Q4 tax / Q4 pretax may be shown is a Standardization definition call (S3 rulebook row effective_tax_rate_reported says NP when not disclosed). Verifier must then re-check that the cells are blank and the filed FY and 10-Q rates are untouched.
- Dependency note: the 59 "consistent" cells are wrong only by method; retiring them is still correct per policy, but the Verifier should confirm they do not remove a rate that was also filed.

## 2. wrong_unit_family (2,623 cells, 9 companies)
Split by cause (cells):
| Sub-class | Cells | Companies | Cause | Evidence |
|---|---|---|---|---|
| CP and IMO: all monetary and per-share facts in CAD; no USD sibling fact exists (checked: sibling unit list empty for all of them) | 2,569 (CP 1,290, IMO 1,279) | 2 | These registrants file 10-Ks in CAD. Values are right in CAD but sit in USD canonical slots and render without a currency; price ratios mix USD price with CAD statements | FILING-CHECKED by prior sessions (S018 results NEW-1: CAD headers, `core.fact` unit `cad`; S020 line 102; VERIFY-SPLIT-REBASE-1000 "CP CAD EPS shown as USD"). I did not reopen filings |
| CB, LOGI, TEL dividends per share in CHF | 44 (CB 26, LOGI 16, TEL 2) | 3 | A CHF dividend fact is chosen; USD per-share sibling exists for most (`usd/shares` sibling found) | CB and LOGI stored-in-CHF: FILING-CHECKED in VERIFY-SPLIT-REBASE-1000-2026-10-24 line 106. TEL DATA-INFERRED |
| VRNS EPS (unit `afn/shares`, a bad unit code in the filing), SOFI equity 2020-07-09 (`usn`), FTI DPS (`eur/shares`, no USD sibling), PEP total_debt (CAD unit, USD sibling exists) | 10 | 4 | Odd unit codes or a wrong-unit instance picked | DATA-INFERRED (core.unit names and siblings only) |
- Fix split: (a) Standardization decides the reporting-currency policy for CP/IMO (convert at dated FX, or show native currency and blank price ratios, or mark unavailable with reason); this is a policy decision, not a code bug, and the displayed numbers are not arithmetic errors. Population-wide effect is larger: any 10-K filer in CAD (CNI, ENB-like) and WO-28 AT-28.1 (record reporting currency per company) is already specified in WO-ADDENDA. (b) Data Engineer: a USD unit gate in canonical selection (prefer the USD sibling; never take chf/eur/afn/usn per-share facts into a USD slot). Existing ledger line 100 (HOVR CAD equity) and tag inbox 2026-10-22 and 2026-10-24 (CP) say the same.
- Check before closing: the 54 non-CP/IMO cells are small enough for a FILING-CHECKED pass by the Verifier (VRNS and SOFI and FTI first, since the unit code may be a filer typo).

## 3. reit_calculated_subtotal (1,025 cells, 32 REITs, SIC 6798)
- Top companies by findings: RYN 136, LAMR 132, EXR 129, RHP 129, EQIX 122, DOC 117, CCI 107, WELL 91, WY 76, VICI 70. By concept: gross_profit_resolved 688 findings, operating_expenses_resolved 521, operating_income_resolved 446. Input tags are mostly CostOfGoodsAndServicesSold / OperatingExpenses with Revenues.
- Evidence: CERTIFY-ROUND3-VALIDATION-2026-10-23 lines 19 and 93: DOC 10 of 10 confirmed (no gross profit or operating income subtotal on the face; example GP -251.5M). OHI (row 17) is a DEFINITION-QUESTION: revenue minus total expenses (both face totals) equals 61.76M, and the face then adds other income to income before tax, so an operating income may be legitimate where both totals are face lines. Do not blanket-hide OHI-type cases.
- Owner Standardization: ruling per REIT row set (gross profit not applicable; operating income either defined as face revenue less face total expenses, labelled, or unavailable), then Data Engineer applies it at the rule registry. The Sector Analyst applicability is the input, outside the four owners requested.
- Not verified per cell: DATA-INFERRED beyond DOC.

## 4. differs_from_authoritative_copy (407 cells, 175 companies)
Sub-split by form and relative age of the authoritative copy (findings by fact id, all 413 classified from `core.fact`/`core.filing`):
| Sub-class | Findings | Reading |
|---|---|---|
| Displayed fact is a DEF 14A value, authoritative copy is an earlier 10-K | 155 (140 reported, 15 derived) | Same defect as family 5 (proxy net income); 129 cells overlap with it |
| Displayed fact is an older 10-K / 10-Q / 8-K / 10-K/A, authoritative copy is from a LATER filing | 225 (revenue_sanity mostly; 10-K 142, 10-Q 75, 8-K 2, 10-K/A 4+1) | Vintage choice: a restated figure exists in a later filing and we display the original. Gaps are small (143 of 407 are under 0.1%, 83 under 1%) but 98 cells are 10% or more, which includes real errors |
| Authoritative copy is EARLIER than the displayed fact | 34 (DPS 15, operating income, financing and investing cash flow, derived revenue) | Includes plainly wrong values: company 2553 derived revenue 2025-12-31 -4,624,288,000 vs 2,646,067,000 (fact 185882640), DPS 2.7 vs 0.68 (fact 2514610) |
- Evidence: DATA-INFERRED (both sides read from our tables). No filing opened. Precedent: root CLAUDE.md 2026-10-18 note that a "latest filed wins" rule cannot be validated against Frames and published about 4,000 wrong values; so the vintage sub-class needs original-filing statement checks, not agreement with the later copy.
- Owner Data Engineer (conflict resolution and vintage selection); the vintage policy (original as filed vs latest restated, per metric) is a Standardization ruling to request first. Start with the 34 earlier-copy cells and the 98 cells of 10% or more.

## 5. non_periodic_form (192 cells, 64 companies, 252 findings)
- 236 net_income_resolved, 14 net_income, 1 basic and 1 diluted EPS. Forms: DEF 14A 240, DEFR14A 10, 8-K 2. 101 of the DEF 14A facts are flagged `is_authoritative=true`, 139 false.
- Value gap versus the periodic copy: 158 findings under 0.1% (rounding, e.g. 1,316,000,000 vs 1,315,605,000), 71 under 1%, and **23 at 10% or more, which are scale errors**: CHE net_income 268,550 vs 268,550,000 (DEFR14A 0001562762-26-000052, in thousands, unscaled), ANET 2,087 vs 2,087,321,000 (DEF 14A 0001193125-26-158942, in millions). Those 23 are real wrong displayed values, not rounding.
- Evidence: class FILING-CHECKED (ledger 2026-10-18 AEMD DEF 14A 0001683168-26-006844 R2: pay-versus-performance net income rounded; ledger 2026-10-22 JPM DEF 14A 0000019617-26-000096 R2). Per cell: DATA-INFERRED, with 10-K copies present in our store.
- Owner Data Engineer: the gate for derivation inputs exists (`common/derivation_policy.PERIODIC_FORMS_DOMESTIC`, uncommitted); the missing piece is authority/display: a non-periodic-form fact must never be authoritative or displayed, and old rows need a retirement dry-run (same shape as tax). Related: ledger 2026-10-22 JPM says a gate on derivation inputs does not repair conflicts already caused.

## 6-8. Small families
- mixed_vintage (81 cells, 27 companies: APD ATO BAX CNP COHR CSL CVI CVS DD DELL EXE FCX GE GPC HSY KEYS LLY MET MMM OMF PG RTX STT TMUS VAL VZ WES): operating_expenses 44, gross_profit 19, operating_income 7, cost_of_revenue 5, liabilities and equity 6. Input forms: 8-K 97, 10-Q 81, 10-K 52. FILING-CHECKED: LLY gross profit FY2016 and Q4 2017 operating income (36-VERIFIER-CERTIFY-DRYRUN-FINDINGS, items 19-20, 8-K 0000059478-19-000274 R99); AVGO refuted (both vintages agree, 10-K 0001730168-19-000144 R4), so the rule over-flags when vintages agree. Owner Data Engineer: derive only from inputs of one filing vintage, and flag only when input vintages disagree.
- sign_flip_between_copies (18 cells, 11 companies: CCI 6, HL 2, AMD 2, others 1 each; interest_expense 6, income_tax 4, cash-flow lines and dividends/buybacks 8): stored copy is the minority sign (1 copy vs 2-3). DATA-INFERRED; sign convention per filing differs (interest expense stored negative). Owner Data Engineer, Tag Mapper to confirm the sign convention of the tag before a rule is written. Verifier opens CCI 2022 interest expense and AMD 2021 financing first.
- cross_vintage_arithmetic (4 cells: WDAY, VOYA operating income, 0.17% apart, probably rounding noise; GD total liabilities 2015 and 2019, 1.1-1.4% apart). DATA-INFERRED. Owner Data Engineer, lowest priority.

## Oldest and most uncertain items
- Highest reach per fix: family 1 (one retirement migration clears 5,079 cells) then family 5+4 DEF 14A authority gate (about 320 distinct cells, includes 23 scale-wrong values) then CP/IMO currency policy (2,569 cells, 2 companies, but a policy call).
- Blind spots: 10 failed shards; the 986-company cohort is judged by 920-ish run companies; I6 was not run on cells outside the display layer (the check says it covers only the displayed `_resolved` row); no per-cell FILING-CHECKED pass was done by me on any family (I read artifacts and our tables only, labelled above).
- Cohort cell denominator was not recomputed; "cohort cells" here means flagged cells among non-excluded companies.

## Acceptance checks for closing (verifier, per family)
1. Tax: stored derived rows retired for the listed fact ids, filed rates unchanged, certify rerun shows zero `per_share_derived_by_subtraction` on this tag; cell shows a reason.
2. Unit: no non-`usd` unit fact in a USD canonical slot (query `core.unit`), CP/IMO shown with the policy outcome.
3. REIT: certify shows zero `reit_calculated_subtotal` after the ruling; OHI-type cells keep their ruled definition.
4-5. DEF 14A and 8-K facts have `is_authoritative=false` and are not in the display layer; the 23 scale cells re-checked against the 10-K R pages.
6-8. Per-cell original-filing check on the confirmed sample before rule changes.
