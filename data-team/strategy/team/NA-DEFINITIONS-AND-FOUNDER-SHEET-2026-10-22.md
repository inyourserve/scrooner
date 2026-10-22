# NA-1 to NA-14: final definition text (ready to implement) and the F-1 to F-3 founder sheet (WO-5 deliverable 3, Standardization Lead, 2026-10-22)

Status: **PROPOSED final text.** These 14 rules need no accounting ruling: each only hides a value, is arithmetic, or selects a source by the filing's own arithmetic within an unchanged meaning (WO-REVIEW-standardization-lead section 2A). Before release, each still needs:
- the founder's plan acceptance (doc 49 section 9: given 2026-10-22);
- a dry-run;
- a Verifier sample by a lane that did not propose or tune the rule;
- the release path of doc 47 rule 1.

NA-7 and NA-9 are MINOR without the accountant only if the founder's release policy accepts filing-proven source selection as non-definitional (founder item 11). If not, they join AC-2 and AC-9.

Conventions used in every rule:
- **Rule ID** `family.rule@version`; the registry row is in `RULE-REGISTRY-DRAFT-2026-10-22.md`.
- **Version class**: PATCH, MINOR or MAJOR (`DEFINITION-VERSIONING-SPEC.md` section 4).
- **States**: the frozen enum of doc 49 section 2.1: `value`, `derived`, `evidenced_zero`, `undefined_by_math`, `history_horizon`, `not_presented`, `not_in_template`, `defect(class, owner)`.
  - Classes and owners are the frozen lists of `FREEZE-REGISTER-2026-10-22.md` section 1. A guard that hides a value emits `defect(guard_hidden, <family owner>)`, with its rule ID and a reason key. It is counted in K1b (hidden by a guard), never as covered.
  - Rule IDs follow the register's RF families; my finer IDs are sub-rules (see RULE-REGISTRY-DRAFT-2026-10-22.md).
  - This document was aligned to the register after my first draft.
- **Wording key**: the UI string id. The proposed English text is given; product owns final copy.
- **"Shall"** means a code-enforced condition, tested by unit test, real-SQL scratch-schema test and a mutation check (doc 49 section 7.1 item 10).
- **Tolerance "within rounding"** follows the decimals-interval rule (data-team/21 section 8 rule 4; XBRL duplicates guidance). It is never a percentage unless a percentage is stated.
- **Evidence labels** are as recorded in the cited file; nothing was re-opened for this document.

---

## NA-1. Per-share values are never derived by subtraction
- **Rule IDs:** RF-12 `pershare.never_derive@1`. Sub-rules: `pershare.no_subtraction@1` (derivation block) and `pershare.q4_state@1` (state of the resulting blank).
- **Class:** PATCH (hides only). **Locus:** `normalizer/derived.py` (structural, tag-independent; Normalizer boundary respected) and `sanity/period_completeness.py` (cause `per_share_not_filed_separately`, migration 0098).

**Definition.**
1. A quarterly or Q4 value whose unit is a ratio of two measures (contains `/`, such as USD/shares or USD/unit) or `pure`, or whose tag matches `Per(Basic|Diluted|BasicAndDiluted)?Share|PerOutstanding[A-Za-z]*Unit|PerUnit`, **shall not** be produced by subtracting one period from another (FY minus 9M, FY minus Q1-Q3, or YTD differences).
2. A per-share value for a quarter **shall** be shown only if the company filed it for that exact 3-month context in a periodic filing (10-Q, 10-K note, amendments). This covers EPS basic and diluted, EPS from continuing operations, dividends declared per share and dividends paid per share.
3. Existing derived per-share facts **shall** be demoted (never deleted) by a reviewed retirement dry-run with an archive copy (0098). The nightly stage does not do this.
4. **State of a blank Q4 per-share cell:**
   - (a) `not_presented`, wording `pershare.q4_not_filed`, when the fiscal year ends after 2021-08-09 (Item 302(a) quarterly data no longer required, Release 33-10890 per WO-REVIEW-period-engineer 3c) and the FY 10-K has no 3-month per-share fact for Q4 under any per-share tag;
   - (b) otherwise `defect(period, period_engineer) [reason `q4_note_not_captured`]`, because the 10-K's quarterly note very likely presents it (388 of 515 top-1000 FY2015 10-Ks tag a 3-month Q4 revenue, DATA-INFERRED).
5. **State of a blank Q2/Q3 per-share cell** with only YTD filed: `defect(period, period_engineer) [reason `per_share_not_filed_separately`]` until a 3-month fact is found.

**Wording.** `pershare.q4_not_filed`: "Not reported for Q4 separately. Companies report per-share figures for the full year; Scrooner does not derive them by subtraction."

**Fixtures (FILING-CHECKED, ledger rows 49, 71):** MSFT Q4 FY26 derived 4.80 vs 4.81 filed (8-K 0001193125-26-323632 Ex. 99.1); AAPL Q4 FY25 1.84 vs 1.85 (0000320193-25-000077 Ex. 99.1); KLAC derived -22.61 vs 1.04 filed; V Q4 DPS -1.18; LEA -1.54.

**Test.** For every fixture the Q4 per-share cell is blank with the stated state; zero derived per-share rows are created on a rerun; the mutation "allow per-share derivation" fails the test.

**Ships with (RU-1, condition 4):**
- the `price_metrics.py` anchor fix (TTM anchors no longer require a Q4 diluted EPS);
- the `ttm.py` reason pass-through;
- the periodic-form gate;
- the P/E basis shown labelled until AC-14;
- dividend yield hidden where it used a derived DPS until AC-13 (state `defect(definition_pending, accountant)`);
- NA-3.

**Verifier tier:** P 30 plus the count of correct values hidden.

## NA-2. Scope of "non-additive"
- **Rule IDs:** RF-12 companion `derive.non_additive_block@1`; `derive.weighted_average_window@1`; proposed RF-27 `derive.additive_allowlist@1` (my `derive.mapper_eligibility@1`).
- **Class:** PATCH. **Locus:** `normalizer/derived.py` (structural block); Mapper gate (eligibility of derived facts for `canonical_fact`).

**Definition.**
1. The NA-1 block **shall** apply to every ratio-unit or `pure` fact (effective tax rate, volatility, counts expressed as pure) and every per-share tag (exercise prices, grant-date fair values), not only EPS and DPS.
2. Share counts that are not weighted averages (antidilutive securities excluded, incremental dilutive shares, shares authorized/issued/outstanding) **shall not** be derived by subtraction. They are instants or non-additive counts.
3. Weighted-average share counts for a quarter may use the founder-adopted window-weight method (wave1 line 38, commit 7825b47). Such a value is `derived`, wording `derive.weighted_average_approximation`.
4. A derived fact is eligible for `canonical_fact` only if its canonical concept is in the approved additive allowlist (classes A/B; starting list `certification/model.py ADDITIVE_FLOWS`). Allowlist changes are a new version of `derive.mapper_eligibility`, enforced at the Mapper, never by creating or deleting Normalizer rows.

**Wording.** `derive.weighted_average_approximation`: "Quarterly weighted-average shares computed from year-to-date figures (approximation)."

**Pre-release check (CODE-READ, Data Engineer):** no displayed metric reads a derived quarterly `pure` value. If one does, it is listed and hidden with `defect(guard_hidden, period_engineer) [reason `non_additive`]`.

**Reach (DATA-INFERRED, 42-EVIDENCE 2a):** stops 16,540 derived `pure` rows and 21,673 other per-share rows in the top 1000.

**Verifier tier:** P 30 (the block hides only).

## NA-3. A filed FY per-share value that is really a quarterly rate; FY-equals-Q4 demotion
- **Rule IDs:** proposed RF-28 `pershare.fy_rate_guard@1`; `period.fy_equals_q4_demotion@1` (existing behavior, now registered).
- **Class:** PATCH. **Locus:** Mapper (canonical selection of per-share FY values) and the metric stage.

**Definition.**
1. For a company-fiscal-year with a filed FY dividends-per-share value D_FY, and filed 3-month values D_Q1..D_Q3 on the same split basis (train R4 basis; until R4 ships, only quarters from filings dated after the last split event), D_FY **shall** satisfy D_FY >= sum of the filed D_Qi minus rounding (one unit of the smallest reported decimals per quarter).
   - Where it does not, the FY value is `defect(guard_hidden, standardization_lead) [reason `fy_per_share_is_quarterly_rate`]`, and every metric reading it inherits the state (P2).
   - **Correction to my review and to ledger row 71:** the earlier test "at least each filed quarter" does not catch the V pattern when the rate is unchanged through the year (0.59 against quarters of 0.59 passes it). The sum test catches it for any rate history. DATA-INFERRED reasoning over the ledger's FILING-CHECKED values.
2. A per-share value equal on a 3-month context and a YTD or 12-month context of the same filing **shall** be treated as a rate: never stored as FY, never an input to any derivation (ledger row 66, V, NVDA). The flag is the L2 slot `DIV.RATE_ON_ANNUAL_CONTEXT`.
3. For EPS, an FY value whose split basis differs from its quarters (KLAC) **shall not** be compared or combined with them until R4 re-bases the series; until then the comparison cells are `defect(guard_hidden, period_engineer) [reason `split_basis_unresolved`]`.
4. A stored "Q4" fact equal to the same filing's FY value (UP, RTB, AIBT ledger row 30) keeps being demoted. The demotion only blanks. Near-zero misfires (42 section 8.5) are accepted because they only hide.

**Fixtures:** V 0001403161-25-000089 R8; LEA 0000842162-26-000011 (DATA-INFERRED in the ledger); KLAC 8-K 0000319201-26-000024; UP 0001819516-22-000009 R5.

**Verifier tier:** P 30.

## NA-4. Additive derivation only on same-sign, same-basis inputs
- **Rule ID:** RF-04 `period.same_vintage_derivation@1`; this text is its version 1 content (my sub-rule ID `derive.same_sign_same_basis@1`).
- **Class:** PATCH (blocks a derivation; never computes a replacement). **Locus:** `normalizer/derived.py` (structural, tag-level).

**Definition.** Q4 = FY - 9M YTD, Q4 = FY - (Q1 + Q2 + Q3), or a discrete quarter = YTD(n) - YTD(n-1) **shall** be produced only if all of the following hold:
1. Every input is an authoritative fact from a periodic form (10-K, 10-Q, their amendments, 10-KT). Never 8-K, DEF 14A, 20-F or 40-F (W3).
2. All inputs have the same tag, unit and undimensioned context, and the YTD shares the fiscal year's start date.
3. **Same sign:** for each input pair, sign(FY) = sign(YTD) or one of them is zero (DIS interest expense FY -1,812M vs quarters +487/+471/+438M is blocked).
4. **Same basis:** the FY filing reports no discontinued-operations fact for that fiscal year that the YTD filing lacks for its period, and no later periodic filing presents a different value for the YTD period under the same tag (a recast). If either holds, the pair is cross-basis (HON capex: recast FY 986M minus original 9M 928M is blocked).
5. The result respects the tag's sign domain: a tag on the DQC_0015 non-negative list must not produce a negative derived value (ledger row 29: negative derived revenue and DPS).

A blocked cell is `defect(guard_hidden, period_engineer) [reason `basis_conflict`]` (conditions 4 and 2) or `defect(guard_hidden, period_engineer) [reason `sign_conflict`]` (conditions 3 and 5). Which basis to show later is AC-19, not this rule.

**Wording.** `derive.basis_conflict`: "Not available: the full-year and year-to-date figures were reported on different bases."

**Fixtures:** HON 0000773840-26-000013 R7 with 10-Q 0000773840-25-000105; DIS (data-team/31, FILING-CHECKED there); MUR 0001193125-14-077534 R132; AGNT 0001104659-26-019145 R6.

**Verifier tier:** P 30, plus the hidden-correct count.

## NA-5. Undefined by math (W6/W7)
- **Rule IDs:** RF-06 `math.growth_nonpositive_base@1`, RF-07 `math.ratio_nonpositive_denominator@1`, proposed RF-26 `state.definition_pending@1` (my `nm.*` IDs are aliases).
- **Class:** PATCH. **Locus:** the metric stage, so stored consumers inherit the state (`ttm._growth_value`, `price_metrics.py`, `expanded_metrics.py`, `calculate_shapes/ratio.py`, `fcf_growth.py`). Not a page-only hide: `trailing_pe` and `eps_growth_yoy` feed `peg_ratio`.

**Definition.**
1. **Growth (`nm.growth_nonpositive_base`).**
   - A YoY growth value **shall** be `undefined_by_math` when the base value is <= 0 or its absolute value is below the concept's materiality floor (`calculate_shapes/materiality.py CONCEPT_MATERIALITY_FLOORS`, version recorded in the rule params).
   - A CAGR **shall** be `undefined_by_math` when the start or the end value is <= 0, or the start is below the floor.
   - Applies to every growth metric in the dependency graph: revenue, net income, EPS, FCF and DPS growth (YoY, 3y, 5y, 10y) and diluted-share growth.
   - DPS from or to zero is NA-14, not this rule.
2. **Ratios (`nm.ratio_nonpositive_denominator`).** A ratio **shall** be `undefined_by_math` when its denominator is <= 0 or below the floor, for:
   - trailing P/E (TTM earnings), PEG (P/E not meaningful, or EPS growth <= 0), payout ratio (EPS);
   - ROE, P/B and D/E (equity); ROIC (invested capital);
   - EV/EBITDA, debt/EBITDA, net debt/EBITDA (EBITDA);
   - OCF/net income (net income); EPS dilution spread (basic EPS); effective tax rate (pretax income).
3. **Negative results stay values.** A negative result with a positive denominator is a `value` (operating margin -12%, FCF yield -3%, ROE -20% on positive equity, negative net cash per share). Only the denominator decides.
4. **Propagation P5.** A state reached by a multiplier or divisor input propagates to the dependent (P/E not meaningful makes PEG not meaningful; EBITDA <= 0 makes every EBITDA multiple not meaningful). An additive use does not propagate (EV uses market cap additively).
5. **Requires a valid input.** The state is valid only if every input it names is a `value` (or `evidenced_zero`) and not itself a defect (S3). Otherwise the cell is the input's defect.
6. **`nm.awaiting_definition`.** Interest coverage with an operating loss (AC-15) and ROIC when pretax income <= 0 (AC-16) **shall** be `defect(definition_pending, accountant)` until those cards are signed. They are not shown as numbers in the meantime.

**Wording keys** (the input is named):
- `nm.base_nonpositive`: "Not meaningful: prior-period value is zero or negative"
- `nm.base_small`: "Not meaningful: base value too small"
- `nm.cagr_loss_endpoint`: "Not meaningful: loss in the start or end year"
- `nm.neg_earnings`: "Not meaningful: negative earnings"
- `nm.neg_equity`: "Not meaningful: negative shareholders' equity"
- `nm.neg_ebitda`: "Not meaningful: negative EBITDA"
- `nm.neg_invested_capital`: "Not meaningful: negative invested capital"

**Fixtures:**
- FILING-CHECKED: RDDT NI growth -209.5% on (484,276)K to 529,721K (0001713445-26-000022 R5/R8).
- DATA-INFERRED: Ford 5y NI CAGR +44.9%.
- Cohort counts (DATA-INFERRED, doc 46 W6/W7): about 245 YoY values plus CAGRs, 117 negative P/E, 36 negative PEG, 24 negative payout.

**Acceptance:** zero numeric growth values on a non-positive base in the cohort; zero negative P/E, PEG or payout shown as numbers (doc 47 v2 T8).

**Verifier tier:** P 30.

## NA-6. Held total-debt guards
- **Rule IDs:** RF-11 `debt.total_debt_consistency@1`, with five sub-rules: `debt.containment_r1b@1`, `debt.zero_r5@1`, `debt.floor_r5@1`, `debt.preference_filter_r4@1`, `debt.fallback_overcount_hold@1`. They are separate sub-rules because they differ in version class (MINOR vs PATCH) and in params.
- **Locus:** `mapper/concept_fallback.py` (held diff), `total_debt_resolved`. Train R3.

**Definitions.**
1. **Containment, R1(b)** (MINOR: values change). A bare `LongTermDebt` value **shall not** be used as the total when it is smaller than the filed `LongTermDebtNoncurrent`, smaller than `LongTermDebtCurrent`, or smaller than half of a lease-combined noncurrent debt tag for the same instant. The total then falls to the next approved path. Fixture: MAR 23M to 16,915M (41-EVIDENCE; 317 instants at 72 companies).
2. **Zero, R5** (MINOR). A total of 0 next to a nonzero debt tag for the same instant **shall** be recomputed without the zero-valued role tags. If no non-zero path remains, the cell is `defect(guard_hidden, data_engineer_l1) [reason `composition_undecidable`]`. 68 instants at 37 companies.
3. **Floor, R5** (PATCH: hide only). A total more than 2% below a single filed debt instrument tag for the same instant **shall not** be published; state `defect(guard_hidden, data_engineer_l1) [reason `composition_undecidable`]`.
   - The tolerance is 2% and is part of the rule version. Not 5%, and no blanket exemption of the company's own total path.
   - A later MINOR version may exempt a row only when the difference equals a filed unamortized discount or issuance-cost fact for the same instant, within rounding.
   - Banks are served by the bank template (total debt not in it), so their floor blanks are `not_in_template` at serve time.
4. **Preference filter, R4** (MINOR). A `company_tag_preference` for total debt that names a single component tag **shall not** be applied. Preference rows stay in the database. WFC 25,168M to 207,307M; all 41 rows.
5. **Fallback overcount hold** (PATCH). A guard **shall** only blank, or fall to a path whose value is not contradicted by another filed debt tag:
   - the fallback value never exceeds the sum of the filed parts (CVX 2016: 43,330M to 55,033M because `DebtCurrent` exceeds short-term plus LTD current);
   - it never sits below a filed lease-inclusive total (DPZ 2024: 14.7M to 3,825.8M while `DebtAndCapitalLeaseObligations` is 4,975M).
   - The named instants (CVX 2016, DPZ 2024, PFE 2020, MMM, COR, PPG, DD and about 12 more) are FILING-CHECKED or blanked before release.

**Release conditions (my sign-off condition 2):**
- the blank reason reaches the cell: the writer persists the rule ID through `is_null_reason` pass-through or `cell_state`; today `resolve_total_debt_components` drops it (CODE-READ, WO-REVIEW 0.2);
- every guard-changed VALUE, not only the blanks, is in the Verifier sample;
- fixtures MAR, TSCO, CSGP, WTRG, DPZ, ALGM.

**Wording.** `debt.composition_undecidable`: "Not available: the company's debt lines do not add up to a single total we can verify."

**Verifier tier:** V 60 + 15 + 15 for the MINOR parts; P 30 for the floor; plus the hidden-correct count (61 own-total rows: WMT, HIG, WY, SCHW, BIIB...).

## NA-7. Prefer the balance-sheet carrying lines over a differing `LongTermDebt` (R1a)
- **Rule ID:** proposed `debt.nc_reorder@1`, a future MINOR version of RF-11 (not Tier 0).
- **Class:** MINOR (subject to founder item 11).

**Definition.** Where `LongTermDebt` (L), `LongTermDebtNoncurrent` (N) and `LongTermDebtCurrent` (C) are all filed undimensioned for the same instant in the same periodic filing, and L differs from N + C beyond rounding, the long-term part of total debt **shall** be N + C, not L.
- L remains stored as an as-reported line.
- Where only L is filed, L is used (today's path).

**Reach (DATA-INFERRED, data-team/31 B):** 1,122 of 7,102 company-instants at 158 of 428 companies; 100 at their latest period.

**Fixtures:** FILING-CHECKED, AMZN 0001018724-26-000004 R69 and GOOG 0001652044-26-000018 R67 (L is face value). PFE 2020: L 4,000M vs N + C 39,135M. The sample must include MCD (L smaller), CTAS, NXPI, CL and TMUS 2021.

**Interim (PATCH, `debt.l_vs_nc_hide@1`), only if the sample fails:** hide total debt where L and N + C differ beyond rounding and the stored path used L.

**Verifier tier:** V 60 + 15 + 15.

## NA-8. Revenue-total disagreement guard (a BUILD item; no code exists)
- **Rule ID:** RF-13 `revenue.total_disagreement@1`.
- **Class:** PATCH. **Locus:** the Mapper, at `revenue` and `revenue_sanity_resolved` (23 direct consumers: recompute). Banks are excluded; their own template.

**Definition.** For a non-bank company and a duration context, consider undimensioned facts in the same periodic filing for at least two of:
- `Revenues`;
- `RevenueFromContractWithCustomerExcludingAssessedTax`;
- `RevenueFromContractWithCustomerIncludingAssessedTax`;
- `RegulatedAndUnregulatedOperatingRevenue`;
- `RevenuesNetOfInterestExpense`.

If they differ beyond rounding, revenue for that company-period **shall** be `defect(guard_hidden, data_engineer_l1) [reason `revenue_total_undecidable`]`. This holds in **both directions** and whichever tag is currently displayed, until NA-9 selects the face total for that filing.
- The guard also fires when the displayed fact is a `Revenues` value outside the income-statement role or not equal to the face line, when that is known (EMR 1,660M vs face 13,804M, 0000032604-23-000030; NTAP 6,237M vs 6,925M, 0001193125-26-259683 R4).
- Every revenue-denominated dependent inherits the state (P2).

**Wording.** `revenue.total_undecidable`: "Not available: the company reports two different revenue totals; we are confirming which is the total on its income statement."

**Honest cost:** in doc 37's sample, 15 of 22 displayed periods were correct, so this guard hides many correct values. That is allowed, but it is short-lived (paired with NA-9), and the Verifier reports the hidden-correct count.

**Reach (DATA-INFERRED, data-team/31 B):** up to 4,479 company-periods (772 annual) at 201 top-1000 companies.

**Acceptance:** data-team/37 section 8, 30 of 30, plus the both-direction cases (EMR, NTAP, MA, WMB, FCX, DVN, THC); the insurer case MET 724M vs 19,154M is covered.

**Verifier tier:** P 30 plus the hidden-correct count.

## NA-9. Revenue: select the face total by structure (clean subset)
- **Rule ID:** RF-48 `revenue.structure_total@1`.
- **Class:** MINOR (subject to founder item 11). **Locus:** Mapper (the doc 37 section 4 resolver), on FSDS/FSN structure evidence (L1).

**Definition.** For a non-bank template company, revenue for a filing's context **shall** be the undimensioned fact that is all of the following:
- (P1) the last revenue-section row before the first expense row on the income statement;
- (P2) a calc child of a profit subtotal and not contradicted as a parent;
- (P3) equal, within rounding, to the sum of its weighted calc children, or of the presentation siblings above it when the filing has no calc children.

It also requires that the selected tag is standard us-gaap and that every addend is revenue-family (no gains, equity-method or other income).

Tie-breaks, in order:
1. the calc parent of the other candidates;
2. the candidate whose identity holds;
3. two passing candidates: `defect(guard_hidden, data_engineer_l1) [reason `revenue_total_undecidable.two_totals`]`;
4. otherwise `defect(guard_hidden, data_engineer_l1) [reason `revenue_total_undecidable.identity_failed`]`.

A fixed tag priority or "largest" is never used. A single revenue row with nothing to sum is selected by P1 + P2 and flagged `single_line`. Everything outside the clean subset stays under NA-8 until AC-9.

**Withdrawal:** any Verifier case where the selected value is not the printed total, any identity that passes by a sign flip, or any selected fact outside the statement role withdraws the version.

**Fixtures:** Walmart Q3 179,496 not 177,769 (0000104169-25-000191 R2); ITC Q3 454 not 515 (0001317630-25-000018 R4); OGE transition zero columns (0001021635-19-000015 R2) never selected.

**Verifier tier:** V 60 + 15 + 15 (doc 37 section 8's 30 cases are the first part).

## NA-10. Consistency guards for capex/FCF and D&A
- **Rule IDs:** proposed RF-51 `fcf.perimeter_consistency@1`, with sub-rules `fcf.capex_perimeter_consistency@1` and `ebitda.da_two_tag_divergence@1`.
- **Class:** PATCH. **Locus:** the metric stage (FCF has 6 consumers, EBITDA 4).

**Definition.**
1. Where `capex_resolved` and raw `capex` differ beyond rounding for the same company-period, FCF, FCF margin, FCF yield, FCF per share, capex % revenue and FCF growth for that period **shall** be `defect(guard_hidden, standardization_lead) [reason `capex_perimeter_inconsistent`]` until AC-5 is signed. Today the statement row and the FCF use different perimeters (CODE-READ; the graph shows `capex_resolved` has 0 consumers while `capex` has 6).
2. Where both `DepreciationDepletionAndAmortization` and `DepreciationAndAmortization` (or another D&A pair used by the larger-of-two rule) are filed for the same context and differ beyond rounding, the larger-of-two value **shall not** feed EBITDA. EBITDA and its multiples become `defect(guard_hidden, standardization_lead) [reason `da_perimeter_undecided`]` until AC-6.

**Fixtures:** Kura Sushi (0001193125-25-269773 R4/R6); SBUX IS 1,684.7M vs CF 1,771.5M (0000829224-25-000114 R3/R5).

**Verifier tier:** P 30 plus the hidden-correct count.

## NA-11. Net income sourced from `ProfitLoss` while non-zero NCI exists
- **Rule ID:** RF-17 `ni.profitloss_with_nci@1`.
- **Class:** PATCH. **Locus:** Mapper, at `net_income` (12 consumers: recompute).

**Definition.** Where the resolved net income for a company-period comes from `ProfitLoss`, and a non-zero `NetIncomeLossAttributableToNoncontrollingInterest` fact exists for the same context in the same periodic filing, net income and every consumer **shall** be `defect(guard_hidden, data_engineer_l1) [reason `attribution_unresolved`]`. The subtraction fix is AC-8, not this rule.

**Wording.** `ni.attribution_unresolved`: "Not available: reported net income includes noncontrolling interests."

**Fixture:** FCX Q1 2026, 1,387M shown vs 881M attributable (FILING-CHECKED in data-team/33 I). Population 1,189 rows (DATA-INFERRED).

**Verifier tier:** P 30.

## NA-12. Gross margin only from `GrossProfit` or one total cost-of-revenue line
- **Rule IDs:** RF-16 `cost.partial_cost_line@1`: input guard (recompute) plus display state (my `margin.gross_profit_source@1`).
- **Class:** PATCH. **Locus:** the guard on the `cost_of_revenue` input (4 consumers: inventory days, payables days, gross margin, `cost_of_revenue_resolved`); the display state on `gross_margin` (0 consumers).

**Definition.** Gross margin and the cost-of-revenue consumers **shall** be computed only where the company files, undimensioned for the same context, either `GrossProfit` or a single total cost-of-revenue line. That excludes `CostsAndExpenses` and any cost line that is one of several cost-of-revenue components on the face. Otherwise:
- `gross_margin` is `not_presented` with wording `margin.gross_profit_not_presented`, when the face evidence (FILING-CHECKED or an audited detector) shows no gross profit and no single cost-of-revenue total;
- else `defect(guard_hidden, data_engineer_l1) [reason `cost_line_partial`]`.

Summing dimension members (CAT, AMH, BRK) is a later composition rule, not this one.

**Wording.** `margin.gross_profit_not_presented`: "Not reported: this company does not present gross profit."

**Fixtures (FILING-CHECKED in 33 N):** UNH 88.6%, ELV 89.1%, CVX 43.6%, WM, RCL, RSG.

**Verifier tier:** P 30.

## NA-13. Unknown is never zero; evidenced zero needs tag-agnostic filing evidence
- **Rule IDs:** RF-08 `composite.unknown_not_zero@1`; RF-36 `evidence.evidenced_zero@1`, with the sub-rule `zero.omitted_row_later_zero@1`.
- **Class:** PATCH (the first) and state rules (the others). **Locus:** `expanded_metrics.py` (TSY) and the `cell_state` job.

**Definition.**
1. **`zero.unknown_not_zero`.** A composite (total shareholder yield, cash returned to shareholders) **shall** treat a component as 0 only when that component's cell is `evidenced_zero`. A component that is a defect or unknown makes the composite `the input's own defect class and owner (P2)`. This removes the unconditional $0 dividend default (W8). Fixture: PFE stored -0.25% vs 5.7% yield, 0000078003-26-000095 R8.
2. **`zero.evidenced_zero`.** An activity cell (dividends to common, share repurchases, capex, SBC, acquired-intangible amortization; interest expense only together with AC-4 borrowings evidence) **shall** be `evidenced_zero` only when all of the following hold:
   - (a) every periodic filing covering the window has no row on the relevant statement whose label or tag denotes the activity. This is checked on the rendered statement or the presentation linkbase, not against our tag list;
   - (b) no fact for the activity exists in any tag of its family, including per-class dimensioned facts and the rate-on-annual-context pattern;
   - (c) the detector producing (a) has passed a 30-per-group audit with zero false zeros.

   Until (c) holds, the cell is `defect(evidence_pending, sector_analyst) [reason `zero_unproven`]`. NCI distributions, preferred-only dividends and net-share-settlement tax payments never make an activity non-zero for common holders (S3 2.1 counterexamples). Borrowings with no line and no note stay with AC-4.
3. **`zero.omitted_row_later_zero`.** An omitted optional cash-flow row in the 10-K, plus a later 10-Q that shows the same period's comparative as 0, **shall** count as evidenced zero for those periods (CMI 0000026172-26-000009 R6).

**Wording.**
- `zero.no_dividends`: "No dividends paid in the last 12 months"
- `zero.no_buybacks`: "No share repurchases in the last 12 months"
- `zero.no_capex`: "No capital expenditure reported"

**Fixtures:** PFE; CMI; GOOG 6M 2026 buyback 0 is a real zero (0001652044-26-000071 R9).

**Verifier tier:** P 30 for (1); the 30-per-group detector audit for (2).

## NA-14. Dividend initiated or suspended
- **Rule ID:** proposed RF-52 `dividend.initiated_suspended@1`.
- **Class:** PATCH. **Locus:** `ttm.py` growth metrics for DPS; `dividend_streak.py`.

**Definition.**
1. Prior-period DPS > 0 and current period `evidenced_zero` (NA-13): DPS growth **shall** be the value -100% with wording `dividend.suspended`.
2. Prior period `evidenced_zero` and current DPS > 0: DPS growth **shall** be `undefined_by_math` with wording `dividend.initiated`.
3. Prior period not `evidenced_zero` and not a value: the input's defect.

Wording copy is product's (founder).

**Wording.**
- `dividend.suspended`: "Dividend suspended"
- `dividend.initiated`: "Dividend initiated in FY<year>"

**Verifier tier:** P 30, drawn from companies where NA-13 Z evidence exists.

---

## F-1 to F-3: founder decision sheet (one page)

These are product calls, not accounting. My recommendation is given for each, with what changes and whether it can be undone. All three are reversible: each is a rule version, and changing it later is a published diff.

| # | Decision | Options | Recommendation | What changes | If undecided (default) |
|---|---|---|---|---|---|
| **F-1** | Remove the 30 duplicate/internal rows from the coverage count (28 base twins + `revenue` + `total_debt_split`; base `employee_count` is one of the twins, so the count is 30, not 31; freeze register D-2) | (a) remove: one cell per economic line, the `_resolved` row is the cell of record (D0e = 131,138 cells); (b) keep: the base and `_resolved` rows are counted twice | **YES (a).** Keep both scoreboards: D0, the fixed 160,718-cell denominator, is always reported; D1 is the template denominator. The change is then visible, not hidden. | coverage % changes once, with a published old-vs-new reconciliation; no displayed value changes | (b): the double count stays; Gate C cannot close |
| **F-2** | May a fiscal year before 2015 be the base of a 10-year growth rate? | (a) yes, if the base fact is post-2009 XBRL and certified; (b) no: only periods ending on or after 2015-01-01 | **NO (b): no pre-2015 base.** It keeps one rule for everything we show (doc 38) and certification needs only the 2015+ window. The cost is small and shrinking: a 10-year rate ending FY2025 uses FY2015, which is allowed. Rates ending FY2024 or earlier show "Base year before 2015 not used". | about 342 revenue 10y-CAGR history blanks in the cohort (S3 F5, DATA-INFERRED) become `history_horizon` with that wording; most latest-year 10y rates (FY2025 end) remain computable | (b) by the history gate |
| **F-3** | Growth period basis and history wording | (a) growth cells on FY and TTM rows only; quarterly rows stay as series data; streaks say ">= N years (all available history)"; (b) keep quarter-row growth (a 10y Q2-vs-Q2 CAGR compounds one quarter's seasonality) | **YES (a).** | quarter-row growth cells leave the template (counted as `not_in_template` via the template version, with a reconciliation); streak wording changes | (b): seasonal growth artefacts stay |

Note on F-2: in my WO review I recommended (a). I now recommend (b), in line with Dhairya's delegated ruling, for two reasons. First, the history gate is one rule for the product and simpler to certify. Second, FY2025 10-Ks make the latest 10-year rate computable from an FY2015 base, so the cost of (b) is mostly older endpoints. (a) remains available later as a MINOR rule version if users ask for it.

Founder answer: F-1 ______ F-2 ______ F-3 ______ Date ______

---

## Evidence and scope of this document
- Read: data-team/20, 21, 22, 11, 03, 37 (sections 4-8); strategy/47, 49; team/WO-REVIEW-standardization-lead, S3 (sections 1-2, 4), R3 (sections 4-5); tags/feedback-inbox.md; `normalizer/derived.py` and `mapper/concept_fallback.py` held diffs (reason constants and the per-share regex); `data-team/strategy/data/metric_dependency_graph.csv` (consumer counts, computed in this session).
- No filing was opened in this run. Every FILING-CHECKED label is relayed from the cited file.
- No database write and no code.
- New in this document versus my review: the NA-3 sum test (a correction), the NA-1 state split by fiscal-year end (Item 302 change), and explicit `defect` classes and owners for every hide.
