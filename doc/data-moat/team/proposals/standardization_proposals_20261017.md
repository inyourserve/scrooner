# Standardization proposals for 10 balance-sheet / cash-flow / share-count concept families

Role: Scrooner Standardization Lead (AI research role; not a CPA, not accounting approval).
Objective: turn the Tag Mapper's 10 proposed decision records into reviewable standardization proposals (definition, naming, equivalence classes, explicit rules, downstream risk, missing evidence, regression fixtures).
Scope: the 10 records in `tag_mapper_decisions_20261017.json` (150-company seed-fixed sample plus library counts, as supplied). Catalog conventions read from `mapper/concepts.py` and `mapper/expanded_concepts.py`; `doc/data-moat/decisions.md` read.
Limits: READ-ONLY. No database, no SEC fetch, no repo edit, no commit. Every number below is quoted from the Tag Mapper's record (a supplied claim, not re-measured) or from a repo file I read; nothing here is a new measurement.
Status of every decision below: **proposed**. `reviewed_by`: null. An AI review is not accounting approval and I cannot approve my own rule; hand-off is the Data Verifier, then a human reviewer under an adopted release policy (none exists: `policy_version` = "data-team-pack-draft").

Task status: **PARTIAL** (all 10 proposals drafted; every evidence check that needs the database, taxonomy files or original filings is NOT_RUN, listed per family and in section 12).

## Commands and checks actually run

| Item | Result |
|---|---|
| Read role/infra/accounting docs, Tag Mapper JSON (all 1,519 lines), `decisions.md` | done |
| Read `mapper/concepts.py` (catalog tuple shapes, `shares_outstanding`, `diluted_eps` and `net_income` fallbacks), `mapper/expanded_concepts.py` (catalog tuple shapes, naming), `normalizer/derived.py` header (window-weight rule) | done |
| `mapper/resolve.py` (does the resolver support sign transforms or conditional fallbacks?) | NOT_RUN (not read) |
| `analytics.metric_definition` / `metric_definition_input` inventory (real downstream consumers) | NOT_RUN |
| Taxonomy label / balance / deprecation lookup for every tag | NOT_RUN |
| Full-population coexistence SQL, original-statement reads, dimension check | NOT_RUN |
| Unit tests, any SQL | NOT_RUN |

## Existing catalog conventions I followed (read from the repo)

- Concept tuple: `(name, statement, combination_mode, description)`, statement in {income_statement, balance_sheet, cash_flow}. Mapping tuple: `(concept, taxonomy, tag, priority, confidence, notes)`, confidence approved / provisional.
- Names are snake_case, no unit suffix, with a few semantic suffixes (`_change`, `_expense`, `_per_share`, `_reported`). `shares_outstanding` is already approved on `us-gaap:CommonStockSharesOutstanding` (1) and `dei:EntityCommonStockSharesOutstanding` (2) and is not touched here.
- `first_match` is the default; `sum` exists only for `total_debt` and only where tags are mutually exclusive.
- Two existing approved fallbacks already cross a perimeter and sit in tension with the policy in section 11: `diluted_eps` priority 3 = `EarningsPerShareBasicAndDiluted` (85.7% agree within 1% with EarningsPerShareDiluted per the file comment), and `net_income` priority 3 = `NetIncomeLossAvailableToCommonStockholdersBasic` (38.6% of coexisting pairs disagree by more than 1%). I do not propose changing them; I list them so the reviewer decides whether the new policy is "grandfather" or "revisit".
- Window-weight derivation for averages is live in `normalizer/derived.py` (adopted by the founder 2026-10-17 for the "WeightedAverage%" tag family only): Q4 = 4*FY - (Q1+Q2+Q3), or 4*FY - 3*YTD9; Q2 = 2*H1 - Q1; Q3 = 3*YTD9 - 2*H1; non-positive result never stored; stored `is_derived=true`; the header cites an approximation error of median 0.024% / p90 0.20% / max 0.78% over 44 company-FY-share-type cases (quoted from the code comment, not re-verified). Note the pattern `WeightedAverage%` is broader than share counts; whether it also catches non-share tags (rates, units) is NOT_RUN and is flagged for the Period Engineer.

## Disposition summary (all remain `proposed`)

| # | Concept | Disposition |
|---|---|---|
| 1 | `retained_earnings` | Recommend with changes |
| 2 | `common_stock_value` | Recommend with changes |
| 3 | `preferred_stock_value` | Recommend with changes |
| 4 | `additional_paid_in_capital` | Recommend with changes (primary tag only); the APIC-common-stock fallback is HOLD |
| 5 | `weighted_average_shares_basic` | Recommend with changes (replaces blanket "exclude is_derived") |
| 6 | `weighted_average_shares_diluted` | Recommend with changes (same) |
| 7 | `operating_lease_rou_asset` | Recommend with changes |
| 8 | `interest_paid_cash` | Recommend with changes (predecessor tag gated) |
| 9 | `income_taxes_paid_cash` | Recommend with changes (primary tag only); `IncomeTaxesPaid` fallback is HOLD |
| 10 | share counts (issued / authorized) | Recommend with changes (adds `preferred_shares_outstanding`; generic tags HOLD) |

---

## 1. retained_earnings

**1. Definition.** Cumulative undistributed net income of the consolidated reporting entity, attributable to the registrant's shareholders, shown as a single line within stockholders' equity on the balance sheet at a point in time (instant). Includes: the line titled retained earnings, accumulated deficit, or both on one line. Excludes: appropriated and unappropriated sub-lines when presented as components, undistributed equity-method earnings (a memo amount), development-stage deficit presented as a separate additional line, equity-roll adjustments (Cumulative effect / Adjustments), AOCI, treasury stock. Unit USD (reporting currency must be USD; the 5 CAD facts are out of the concept, not converted). Sign: as reported, positive = retained earnings, **negative = accumulated deficit**; never abs(). Zero: a reported numeric zero is valid and preserved (for example after a quasi-reorganization or a new entity); a missing line is NOT zero (the sample issuer in the Tag Mapper record that files equity but no retained-earnings tag stays null with a reason, never zero-filled).

**2. Name / mode / precedence.** `retained_earnings`, balance_sheet, `first_match`. Precedence: 1 `us-gaap:RetainedEarningsAccumulatedDeficit` (approved on adoption). `ifrs-full:RetainedEarnings` (65 companies): HOLD, not mapped, because 20-F/40-F scope is an open founder decision (doc 02); revisit if FPIs enter scope.

**3. Equivalence classes.**

| Tag | Tag Mapper | Mine | Reason |
|---|---|---|---|
| RetainedEarningsAccumulatedDeficit | exact | exact (agree) | dominant, 148/150 sample issuers |
| ifrs-full:RetainedEarnings | exact_ifrs_alternate | hold (disagree on timing only) | different taxonomy, scope undecided, not sampled |
| RetainedEarningsAppropriated | component | component (agree) | sub-amount; 0 of 38 shared contexts equal |
| RetainedEarningsUnappropriated | component | component (agree) | 0 of 14 equal |
| RE...EquityMethodInvestees | not_equivalent (memo) | not_equivalent (agree) | memo sub-amount |
| DevelopmentStageEnterpriseDeficit... | not_equivalent (opposite sign) | **component (disagree on class)** | see rule R1.1 |

**4. Rules.**
- R1.1 Development-stage deficit (pre-2015 era tag, ASU 2014-15 removed the concept): it is a positive-magnitude deficit and, for an issuer in the development stage, the balance sheet may present a pre-development-stage accumulated deficit **plus** a deficit accumulated during the development stage; total retained earnings would then be the sum of both lines, so negating the development-stage tag alone is not safely the total. It is therefore a component of the equity line, not an alternate. Rule: never mapped to `retained_earnings` by sign flip. Preserve as reported; the tag stays unmapped, reason COMBINED_LINE_ONLY / component-only. Sign rule if a human later approves a conditional fill: negate the magnitude (`retained_earnings = -DevelopmentStageDeficit`) ONLY for a context where the issuer files no RetainedEarningsAccumulatedDeficit and the Verifier has confirmed on the statement that the development-stage line is the only retained-earnings-type line. Not default; it needs the resolver to support a sign transform (NOT_RUN, see B6). Because pre-2015 data is not current display data (history gate), the practical value is low; the safe default is no mapping.
- R1.2 Component sum: `Appropriated + Unappropriated = RetainedEarnings` is conceptually plausible (company 1117 shows the unappropriated figure below the total, consistent with a missing appropriated part) but untestable in the sample (0 shared contexts). A calculated total is NOT allowed until a full-population test shows both components present and equal to the total in the contexts where the total also exists, and a human approves the composition rule.
- R1.3 Plausibility checks must not bound retained earnings by total stockholders' equity (749 of 5,465 shared contexts had RE > equity, normal with treasury stock / AOCI).
- R1.4 A line absent from the statement of an entity type with no retained earnings (partnerships, LLC members' equity) is `not_applicable` or unresolved, never zero.

**5. Downstream.** Candidate consumers (by reasoning; `metric_definition_input` NOT_RUN): Altman-style retained-earnings-to-assets ratios, equity composition sanity check (common + preferred + APIC + RE + AOCI - treasury vs `stockholders_equity`), accumulated-deficit flags, payout sustainability. Formula risk: do not use as a proxy for book value; do not infer dividends or earnings history from changes in the balance (changes include restatements, buybacks charged to RE, and reclassifications).

**6. Evidence still missing.** Full-population coexistence of the primary tag against all components; the number of issuers with equity but no retained-earnings tag (custom or absent); the Tag Mapper's coexistence line "RE vs DevelopmentStage: 8 equal, 9 unequal" is ambiguous (the counterexamples show opposite signs, so raw equality should be rare); the Mapper must state whether "equal" meant raw or sign-flipped; Verifier reads of original balance sheets for company ids 1117, 599, 4393, 1600, 2301, 2952; dimensions and custom tags unobservable.

**7. Regression fixtures.**
- F1.1 (named, Tag Mapper): company 1117 FY2010-2012, RE 17.154B and Unappropriated 12.9B, same context -> `retained_earnings` = 17.154B; Unappropriated unmapped.
- F1.2 (named): company 599 2010-12-31, RE 7.827B, Appropriated 0.0938B -> value 7.827B, never 0.0938B.
- F1.3 (named): companies 1600 / 2301 / 2952, RE -206,949 / -62.569M / -15,000 with dev-stage deficit +same magnitude -> output stays negative, never doubled, never sign-flipped twice.
- F1.4 (named): company 4393 files StockholdersEquity but no RE/appropriated/dev-stage tag -> null with reason, not 0.
- F1.5 (synthetic): only `RetainedEarningsAppropriated` and `RetainedEarningsUnappropriated` present -> `retained_earnings` null (no calculated total without an approved rule).
- F1.6 (synthetic): RE reported as exact 0 -> output 0 (reported zero preserved).
- F1.7 (synthetic): RE unit CAD -> not mapped.

---

## 2. common_stock_value

**1. Definition.** Balance-sheet carrying amount of common stock (par or stated value of common shares issued) at an instant, in USD, as a single positive credit-balance magnitude. Includes: the line titled "Common stock" showing par/stated value. Excludes: APIC, any line combining common stock with APIC, per-share par values (usd/shares), share counts, and common stock in temporary equity. Zero is a valid reported value (109 zero facts in the sample). Sign: as reported, expected non-negative; a negative is quarantined, not abs()'d. Caveat on perimeter: for no-par issuers the line titled "Common stock" frequently carries all paid-in capital, so values are **not comparable across par and no-par issuers**; the concept is "the line as presented", and comparability across issuers is limited.

**2. Name / mode / precedence.** `common_stock_value`, balance_sheet, `first_match`. Precedence: 1 `us-gaap:CommonStockValue`. `CommonStockValueOutstanding` (469 companies): HOLD (not mapped as a fallback; see class below). Optional second concept, separate and low priority: `common_stock_including_apic` (combined line) = first_match over `CommonStocksIncludingAdditionalPaidInCapital` (1), `CommonStockIncludingAdditionalPaidInCapital` (2); only worth building if a consumer wants total paid-in capital for issuers that file only the combined line. Not required for this batch.

**3. Equivalence classes.**

| Tag | Tag Mapper | Mine | Reason |
|---|---|---|---|
| CommonStockValue | exact | exact (agree) | dominant |
| CommonStockValueOutstanding | alternate, hold | **not_equivalent until label read (agree on hold)** | the tag name implies an outstanding perimeter (net of treasury) vs issued; 27/36 equal and 9 unequal is consistent with a perimeter difference; taxonomy definition NOT_RUN |
| CommonStockNoParValue | not_equivalent | not_equivalent (agree) | 217/219 facts are usd/shares (per-share) |
| CommonStocksIncludingAdditionalPaidInCapital | combined | combined (agree) | |
| CommonStockIncludingAdditionalPaidInCapital | combined | combined (agree) | possibly the same line as the plural tag, unverified |

**4. Rules.**
- R2.1 Combined-line only: if an issuer files only a combined common-stock-plus-APIC tag, `common_stock_value` is null with reason COMBINED_LINE_ONLY. Do not set it equal to the combined amount, and do not subtract APIC to split it unless an approved composition rule exists. The single-issuer finding (company 3631, 8 of 8 contexts: CommonStockValue + AdditionalPaidInCapitalCommonStock = combined) supports the class, not a rule.
- R2.2 Unit rule: only unit USD; usd/shares facts are never a balance.
- R2.3 `CommonStockValueOutstanding` never substitutes silently; at most a separate concept after a label read.
- R2.4 Zero: preserved. Missing: null.

**5. Downstream.** Equity composition check; paid-in-capital total (needs a decision on the combined concept); not a market-cap input and not a share count proxy (par value x shares is not derivable without the par per share). Formula risk: using it as "equity base" or in equity ratios is wrong; for no-par issuers it is inflated relative to par issuers.

**6. Evidence missing.** Full-population unit check and zero rate; share of issuers that are no-par or combined-line-only; taxonomy label for ValueOutstanding; Verifier reads of company ids 1377, 2952, 1800, 607, 3631.

**7. Fixtures.**
- F2.1 (named): company 1377 2020-12-31 CommonStockValue 10.753M with CommonStockNoParValue 0 (usd/shares) -> 10.753M.
- F2.2 (named): company 1800 2023-12-31, CommonStockValue 9,755, CommonStocksIncludingAPIC 500,000 -> value 9,755; combined tag never read as `common_stock_value`.
- F2.3 (named): company 607 2010, value 482M with combined 2.0B-2.14B -> 482M.
- F2.4 (named): company 2952 2013-06-30, CommonStockValue 12,000 vs ValueOutstanding 30.3M -> 12,000; ValueOutstanding ignored.
- F2.5 (synthetic): only the combined tag present -> null, reason COMBINED_LINE_ONLY.
- F2.6 (synthetic): CommonStockValue = 0 -> 0.

---

## 3. preferred_stock_value

**1. Definition.** Carrying amount of preferred stock classified within permanent (stockholders') equity at an instant, USD, as presented on the balance sheet. Excludes: preferred stock in temporary/mezzanine equity, APIC attributable to preferred, per-share values, share counts, and lines combining preferred with APIC. Sign: as reported, expected non-negative. **Zero is a valid reported value and is preserved; it means "the line is reported as zero", NOT "the issuer has no preferred equity"** (company 5714: PreferredStockValue 0 with 973M AdditionalPaidInCapitalPreferredStock; company 5356: value 0 with 75.2M mezzanine preferred). Missing is null.

**2. Name / mode / precedence.** `preferred_stock_value`, balance_sheet, `first_match`. Precedence: 1 `us-gaap:PreferredStockValue`. `PreferredStockValueOutstanding` (251 companies): HOLD.

**3. Classes.** PreferredStockValue exact (agree). PreferredStockValueOutstanding: not_equivalent until label read (Tag Mapper "alternate; hold"; company 3720: 0 vs 26.5M in the same context, so they are not interchangeable). PreferredStockNoParValue: not_equivalent (per-share). TemporaryEquityValueExcludingAdditionalPaidInCapital: not_equivalent (different balance-sheet position; keep for a possible future `temporary_equity_value`, not in this batch). AdditionalPaidInCapitalPreferredStock: component of APIC (agree).

**4. Rules.**
- R3.1 Reported zero preserved; reported zero must never be used to infer "no preferred". A `has_preferred_equity` flag, if ever wanted, needs shares outstanding > 0, APIC-preferred, mezzanine and statement text together; it is NOT derivable from this concept and is not proposed.
- R3.2 Mezzanine preferred is outside this concept; it is not folded in to "improve" coverage.
- R3.3 Unit USD only.
- R3.4 74% of authoritative facts are zero (1,753 of 2,378) and 60 of 88 issuers only ever report zero; consumers must treat the value as "balance-sheet line value", and coverage reports must count a reported zero as a value present (value_status reported) but flag it low-information.

**5. Downstream.** Equity composition check; **book value per common share must not subtract carrying value as a stand-in for liquidation preference** (formula risk; carrying amount and liquidation preference differ); net income available to common (preferred dividends) is a separate flow concept. Leverage conventions: preferred is outside `total_debt` unless a separate approved policy says otherwise.

**6. Evidence missing.** Full-population zero rate; how many issuers carry preferred in mezzanine or APIC only; Verifier reads of company ids 5356, 5714, 3720.

**7. Fixtures.**
- F3.1 (named): company 5714 2025-12-31, PreferredStockValue 0 and APIC-Preferred 973M -> value 0; no `has_preferred` conclusion.
- F3.2 (named): company 5356 2026-06-30, PreferredStockValue 0 with TemporaryEquityValue 75.2M -> value 0; mezzanine not added.
- F3.3 (named): company 3017 2018-2020 PreferredStockNoParValue 0.001 (usd/shares) -> never a balance.
- F3.4 (named): company 3720 2019-03-31, value 0 vs ValueOutstanding 26.5M -> 0.
- F3.5 (synthetic): tag absent -> null, not 0.

---

## 4. additional_paid_in_capital

**1. Definition.** Total amount received from shareholders in excess of the par/stated value of stock, shown within stockholders' equity at an instant, USD. Includes: the total APIC line. Excludes: APIC movements in the equity roll-forward (duration `Adjustments*` tags), APIC attributable to a single class (common-only or preferred-only) when the issuer presents the classes separately, combined common-plus-APIC lines, pre/post-confirmation (fresh-start) APIC. Sign: as reported; **negative values are legitimate** (6 negative facts, for example company 2952 2013-03-31 -1.117M and 4490 2013-12-31 -13.1M) and are preserved, never abs(); zero valid when reported (32 zero facts).

**2. Name / mode / precedence.** `additional_paid_in_capital`, balance_sheet, `first_match`. Precedence: 1 `us-gaap:AdditionalPaidInCapital` only. The Tag Mapper's conditional second entry (`AdditionalPaidInCapitalCommonStock`) is **HOLD, not part of this proposal**. Optional separate concept for visibility without risk: `additional_paid_in_capital_common` (first_match on `AdditionalPaidInCapitalCommonStock`), so the data is available and labeled but never presented as total APIC.

**3. Classes.** AdditionalPaidInCapital: exact for "total APIC" (agree). AdditionalPaidInCapitalCommonStock: **component (disagree with "component or alternate")**: 12 of 45 shared contexts differ (27%), and company 1851 shows 7.887M vs 294.2M (37x), company 2730 shows total above the common part; these are not interchangeable. AdditionalPaidInCapitalPreferredStock: component. CommonStocksIncludingAdditionalPaidInCapital: combined, never APIC (company 1800: 500,000 vs APIC 72.4M).

**4. Rules (the fallback question).**
- R4.1 **APIC-common-stock -> additional_paid_in_capital fallback is NOT allowed by default.** It could become allowed, as a staged, `provisional`, lineage-labeled fill (flag `fallback_used = component_as_total`), only if ALL hold in the same company-period context: (a) no `AdditionalPaidInCapital`, (b) no `AdditionalPaidInCapitalPreferredStock`, (c) no `PreferredStockValue` > 0 (preferred, if any, has no separate APIC), (d) no combined-line tag in the context, and (e) the Verifier has confirmed on original statements, for a defined issuer set, that such issuers present one APIC line equal to the common figure. The sample shows 73 issuers file only the total tag and 32 only the common variant (of 138 with APIC by either), so the fallback matters for coverage (about 30%); that is the reason to resolve it, but coverage never justifies the substitution. Conditions (a)-(d) are observable only for standard tags; custom APIC tags and multi-class presentation are not (B4). Whether the resolver can express conditional fallbacks is NOT_RUN (B6).
- R4.2 `APIC = Common + Preferred components` is not a rule (0 shared contexts to test).
- R4.3 `Adjustments*` duration tags never map here.

**5. Downstream.** Equity composition check only. Not an input to book value (use `stockholders_equity`), nor to dilution (use share counts); a net-of-dilution proxy from APIC changes is invalid (stock comp, repurchases, restatements all move it). Formula risk: do not subtract it from a combined line to derive common stock value.

**6. Evidence missing.** Full-population equality of Total vs Common-component where both present and by what cause the 27% differ (scale vs perimeter vs filing error); original statements for company ids 1851, 2730, 1800, 2952, 4490; custom APIC tags unobservable.

**7. Fixtures.**
- F4.1 (named): company 1851 2018-12-31, total 7.887M vs common 294.2M -> `additional_paid_in_capital` = 7.887M, common variant never substituted when the total exists.
- F4.2 (named): company 2730 2016-12-31 total 62.95M vs common 56.71M -> 62.95M.
- F4.3 (named): company 1800 2023-12-31 combined 500,000 vs APIC 72.4M -> 72.4M.
- F4.4 (named): company 2952 2013-03-31 APIC -1.117M -> stays -1.117M.
- F4.5 (synthetic): only `AdditionalPaidInCapitalCommonStock` present, no other APIC/preferred tags -> under the default policy null (reason COMPONENT_ONLY); under a later approved R4.1 policy the fill is flagged `component_as_total`. The fixture must pass under the default.
- F4.6 (synthetic): `AdditionalPaidInCapitalCommonStock` plus `AdditionalPaidInCapitalPreferredStock` present, total missing -> null even under R4.1.

---

## 5. weighted_average_shares_basic

**1. Definition.** Weighted-average number of common shares outstanding used as the denominator of basic EPS for a **duration** (quarter, half-year, nine-month YTD, or fiscal year), unit shares, strictly positive, as reported in the EPS computation (income statement face or EPS note). It is a **time-average over its own window**, not a point-in-time count and not a flow. Excludes: point-in-time `shares_outstanding`, issued or authorized counts, weighted-average *issued* shares, the diluted figure, the dilution increment, restricted-stock weighted counts, pro forma counts, and any value in a unit other than shares. Zero or negative is never valid (a weighted-average of zero shares is not an EPS denominator): quarantine, never store as zero. A value of EPS magnitude (for example -0.06 in a shares-unit fact, company 5820) is a mis-tagging and is quarantined.

**2. Name / mode / precedence.** `weighted_average_shares_basic`, income_statement (EPS note, same practical bucketing as `basic_eps`), `first_match`. Precedence: 1 `us-gaap:WeightedAverageNumberOfSharesOutstandingBasic`. Combined single-line tags go to a **separate** concept, `weighted_average_shares_basic_and_diluted` (income_statement, first_match: `WeightedAverageNumberOfShareOutstandingBasicAndDiluted` (1), `WeightedAverageNumberOfSharesOutstandingBasicAndDiluted` (2)), reported as combined.

**3. Classes.**

| Tag | Tag Mapper | Mine | Reason |
|---|---|---|---|
| ...OutstandingBasic | exact | exact (agree) | |
| WeightedAverageNumberOfShareOutstandingBasicAndDiluted (2063 cos) | combined | combined (agree) | 489 of 576 equal to basic, 87 unequal incl. scale mismatches |
| WeightedAverageNumberOfSharesOutstandingBasicAndDiluted (74 cos) | combined | combined; **the two spellings are separate tags, equivalence between them not verified** | 2 instant-typed facts anomaly |
| WeightedAverageNumberOfSharesIssuedBasic | not_equivalent | not_equivalent (agree) | issued vs outstanding; company 2260 shows -282.9M vs 1.157M |
| ...DilutedSharesOutstandingAdjustment | component | component (agree) | 1,339 of 1,419 exact |
| ProForma... | not_equivalent | not_equivalent (agree) | |

**4. Rules.**
- R5.1 **Never derived by subtraction.** `FY - Q1 - Q2 - Q3` and `YTD - YTD` are invalid for an average. The only admitted derivation is the repo's window-weight method in `normalizer/derived.py` (4*FY - 3*YTD9 etc.), which yields an approximation and is stored `is_derived=true`, positive only.
- R5.2 **Disagreement with the Tag Mapper:** the record proposes excluding all `is_derived=true` facts. That rule was written against the pre-fix defect (it reports 921 of 1,019 derived basic facts negative; the code header records the same defect measured live 2026-10-17 and the founder-adopted correction). I propose instead: the concept admits (a) **reported** facts (value_status reported), and (b) **window-weight derived** facts (value_status derived, flagged approximation), never the old subtraction output. Because the correction only prevents *new* bad rows, previously stored subtraction-derived negatives may still exist (reprocess status NOT_RUN); the `value > 0` guard therefore stays as a hard mapper condition and the stored negatives must be cleared or excluded before any canonical value is published. A consumer that needs only reported figures filters on value_status; where both a reported and a derived value exist for a period, **the reported value wins**. The window-weight method itself was adopted by the founder, which is release policy, not accounting approval; the approximation (equal-length-quarter assumption, treasury-method effects ignored) needs a human reviewer's acceptance, and the evidence quoted is a 44-case comparison against yfinance (a comparator, not a filing). This is a flagged risk, not a block on the mapping.
- R5.3 **Combined line policy:** `BasicAndDiluted` is never mapped as plain basic. When an issuer files only the combined line, `weighted_average_shares_basic` is null (reason COMBINED_LINE_ONLY) and the value sits in `weighted_average_shares_basic_and_diluted`. A consumer needing basic may use the combined concept only through an explicit "reported_as_combined" path (see section 11, policy P-COMB option); the mapper does not do it silently. Note the existing `diluted_eps` priority-3 fallback to `EarningsPerShareBasicAndDiluted` is a precedent in the opposite direction.
- R5.4 Scale rule: where basic and combined or diluted differ by an exact power of ten for the same context (company 1143: 2,037,000 vs 2,037; company 1307: 4,901,464,000 vs 4,901,464), the pair is quarantined as a unit/scale conflict and neither is "corrected" by the mapper.
- R5.5 52/53-week and non-calendar windows: the period type buckets (3m, 6m, 9m, 12m) are by duration; the concept does not require calendar alignment.
- R5.6 Weighted-average counts are never mixed with `shares_outstanding`, issued or authorized counts in the same formula without an explicit rule (see section 11).

**5. Downstream.** EPS reconstruction (net income to common / weighted average), dilution spread (diluted vs basic), buyback effectiveness (period-average, not period-end), share-count trend. Formula risk: dividing by period-end `shares_outstanding` instead of the weighted average mis-states EPS in a year with large issuance or buyback; EPS must not be summed across quarters (non-additive); stock splits restate comparatives (see B9); the existing `basic_eps` and `diluted_eps` concepts must remain reported-only and are not recomputed from these.

**6. Evidence missing.** The state of stored negative derived rows after the 2026-10-17 correction and whether a reprocess has run; full-population counts of reported-vs-derived and of issuers with combined-only; Verifier reads of the EPS notes for company ids 2052, 1143, 5820, 2260; whether the `WeightedAverage%` derive pattern catches non-share tags; dimensions and custom EPS tags unobservable; split-adjustment status.

**7. Fixtures.**
- F5.1 (named): company 2052 FY2022-2025 derived values of -197M..-230M against a ~101M median -> never output as `weighted_average_shares_basic`; if derived, must come from the window-weight method and be positive.
- F5.2 (named): company 1143 2018-03-31 Basic 2,037,000 vs BasicAndDiluted 2,037 -> quarantine as scale conflict; neither promoted.
- F5.3 (named): company 5820 2010-07-01..09-30 value -0.06 under shares unit -> rejected (non-positive and EPS-sized).
- F5.4 (named): company 2260 2024-12-31 Q4 Basic -282,915,000 vs IssuedBasic 1,157,000 -> neither used; Issued never substituted.
- F5.5 (synthetic, arithmetic): FY=100, Q1=Q2=Q3=100 -> window-weight Q4 = 4*100-300 = 100 (NOT FY-Q1-Q2-Q3 = -200); and FY=100, YTD9=100 -> 4*100-3*100 = 100.
- F5.6 (synthetic): 4*FY - 3*YTD9 <= 0 -> no value stored.
- F5.7 (synthetic): only BasicAndDiluted present -> basic null; `weighted_average_shares_basic_and_diluted` holds the value.
- F5.8 (synthetic): reported and derived both present -> reported wins.

---

## 6. weighted_average_shares_diluted

**1. Definition.** Weighted-average number of common shares used as the denominator of diluted EPS (basic shares plus dilutive potential shares under the treasury-stock / if-converted methods), duration, unit shares, strictly positive. Excludes basic, the dilution increment, pro forma, a combined basic-and-diluted line (separate concept), and point-in-time counts. Zero/negative never valid. Note that diluted may legitimately equal basic (net-loss years, antidilution) and may legitimately be below basic only if anti-dilutive items are excluded in the issuer's computation (not expected: treat diluted < basic with caution, flag).

**2. Name / mode / precedence.** `weighted_average_shares_diluted`, income_statement, `first_match`; precedence 1 `us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding`. The combined concept from section 5 is the home of `BasicAndDiluted`.

**3. Classes.** Diluted: exact. BasicAndDiluted: combined (disagree with nothing; note it matches diluted in only 355 of 484 contexts (73%), 129 unequal, company 1051 FY2014-15 5,049,813 vs 5,029,343, so even for the combined line the identity "combined = diluted" is not safe). DilutionAdjustment: component. ProForma: not_equivalent.

**4. Rules.** R5.1-R5.6 apply identically. In addition:
- R6.1 **`diluted = basic + adjustment` is a coexistence statistic, not a derivation rule**: exact in 1,339 of 1,419 contexts (94%); 80 inexact (company 599 2014Q3: -1,252.6M + -0.1M != -1,253.4M; company 1020 2011Q3: 16.509M + -0.023M != 16.528M). Calculation is not allowed for a missing diluted value. Agree with the Tag Mapper's rejection.
- R6.2 The dilution increment tag is not diluted shares.
- R6.3 Same derived-value policy as R5.2 (reported wins; window-weight derived admitted, flagged; subtraction output never admitted; `value > 0`).

**5. Downstream.** Diluted EPS reconstruction, dilution percentage (diluted vs basic), valuation per share. Risk: using diluted from one period and basic from another; mixing derived and reported in a spread (flag a spread computed from derived inputs as lower-confidence); the existing `diluted_eps` concept stays reported-only.

**6. Evidence missing.** As section 5; company ids 103 (derived negatives), 1307 (scale), 1051, 599, 1020 for original EPS notes.

**7. Fixtures.**
- F6.1 (named): company 103 2022-07-02..09-30 derived basic -327.3M / diluted -329.0M -> neither output.
- F6.2 (named): company 1307 2014 Q1 Diluted 4,901,464,000 vs BasicAndDiluted 4,901,464 -> scale quarantine.
- F6.3 (named): company 1051 FY2014-15 Diluted 5,049,813 vs BasicAndDiluted 5,029,343 -> Diluted used; combined not substituted.
- F6.4 (named): company 599 2014Q3 Basic + Adjustment != Diluted -> reported Diluted is output; no recomputation.
- F6.5 (synthetic): diluted missing, basic and adjustment present -> null (no calculation).
- F6.6 (synthetic): same window-weight arithmetic as F5.5 applied to diluted.

---

## 7. operating_lease_rou_asset

**1. Definition.** Right-of-use asset arising from operating leases under ASC 842, balance-sheet carrying amount at an instant, USD, presented as a separate line or disclosed in the lease note. Excludes: finance-lease ROU assets, PP&E lines that combine PP&E with finance-lease ROU, operating-lease liabilities (current and noncurrent are separate concepts, not in this batch), lease amortization expense, lease income. Sign: non-negative; zero valid when reported (49 zero facts). Applicability: ASC 842 effective for public companies for fiscal years beginning after 2018-12-15; the earliest sampled date is 2018-03-31, consistent with early adopters. Before adoption the line does not exist: `not_applicable`/not reported, **not zero**, and a period series across adoption is a **comparability break** (modified retrospective: prior periods not restated).

**2. Name / mode / precedence.** `operating_lease_rou_asset`, balance_sheet, `first_match`; precedence 1 `us-gaap:OperatingLeaseRightOfUseAsset`.

**3. Classes.** OperatingLeaseRightOfUseAsset: exact (agree). FinanceLeaseRightOfUseAsset: not_equivalent (agree; 0 of 359 equal). PP&E-and-finance-ROU combined: combined / not_equivalent (agree; 0 of 228 equal; the combined line contains no operating ROU in company 1113). Operating lease liability: different balance (37 of 1,895 equal by coincidence).

**4. Rules.**
- R7.1 If an issuer presents operating ROU inside another line (for example other assets) or combines operating and finance ROU in one line (custom tag), the concept is null with reason NOT_SEPARATELY_DISCLOSED or COMBINED_LINE_ONLY; no subtraction, no estimate from the liability.
- R7.2 "Total lease assets" (operating + finance) is a possible later calculated concept; not proposed; it needs both inputs present and an approved composition rule.
- R7.3 Plausibility: ROU > total assets is a quarantine flag (company 1600 2019-03-31: 1,389,731 vs Assets 1,111,590); the mapper does not auto-correct.
- R7.4 The issuer that files an operating-lease liability but no ROU tag stays null, absent != zero.

**5. Downstream.** Lease-adjusted leverage or EV (needs a debt-perimeter policy: today `total_debt` excludes leases; adding operating lease liabilities, not this asset, is the usual adjustment); asset turnover and capital-intensity ratios shift at ASC 842 adoption because total assets include ROU from adoption (comparability break); ROIC invested-capital definitions must state treatment. Formula risk: never add ROU to total debt; never net it against lease liabilities as "lease equity".

**6. Evidence missing.** Full-population share of issuers with a separately presented operating ROU, combined-with-finance, or inside other assets; the adoption-date split; original statements for company ids 1113, 1600, 604 and the liability-without-ROU issuer.

**7. Fixtures.**
- F7.1 (named): company 1113 2019-12-31 ROU 4.758B vs PP&E+FinanceROU 30.17B -> 4.758B; combined not used.
- F7.2 (named): company 604 2024-11-30 operating ROU 61.1M, finance ROU 9.2M -> 61.1M, finance excluded.
- F7.3 (named): company 1600 2019-03-31 ROU > Assets -> flagged/quarantined, not corrected.
- F7.4 (named): liability-without-ROU issuer -> null, not zero.
- F7.5 (synthetic): period before ASC 842 adoption -> null/not_applicable, not 0.

---

## 8. interest_paid_cash

**1. Definition.** Cash paid for interest during the period, from the supplemental cash-flow disclosure (cash-flow statement footer or note), duration (quarter / YTD / fiscal year), USD, expressed as a **positive magnitude of cash outflow** as filed. Intended perimeter: interest on borrowings, net of amounts capitalized into asset cost where the tag says so (basis to be confirmed from the taxonomy label, NOT_RUN). Excludes: interest expense (accrual), capitalized interest (memo), discontinued-operations interest, combined dividends-and-interest paid, and IFRS classified-by-activity variants. Zero is a valid reported value (271 zero facts). "No tag" is not zero: the disclosure is supplemental and many issuers omit it (NOT_SEPARATELY_DISCLOSED / not reviewed). Sign: as reported; a negative (52 negative `InterestPaidNet` facts in the sample, plus derived ones) is not expected for interest paid and is **flagged, never abs()'d**.

**2. Name / mode / precedence.** `interest_paid_cash`, statement `cash_flow` (supplemental), `first_match`. Precedence: 1 `us-gaap:InterestPaidNet` (approved on adoption); 2 `us-gaap:InterestPaid` as **provisional**, gated on the taxonomy-label read and a Verifier check, applied per company-period context (a later predecessor tag never overrides a present `InterestPaidNet` in the same context).

**3. Classes.** InterestPaidNet exact (agree). InterestPaid: **exact_predecessor with a basis caveat (agree with caveat)**: 248 of 298 shared contexts equal (83%), 50 unequal (company 1800 2025 H1: 4,629 vs 5,870), so the two tags are treated as the same concept in different eras only for contexts where they do not both appear; 63 issuers file both in different periods. InterestPaidCapitalized: component/memo. InterestPaidDiscontinuedOperations: not_equivalent (scope). InterestExpense: not_equivalent (cash vs accrual; 386 of 2,336 pairs outside 1/3-3x).

**4. Rules.**
- R8.1 **Never fall back to `interest_expense`** (cash != accrual).
- R8.2 Conflict rule: if both cash tags exist in the same context and differ by more than a tolerance chosen by the reviewer, `InterestPaidNet` wins and the conflict is recorded in lineage; it is not averaged.
- R8.3 Quarter derivation by YTD subtraction is permitted only if the concept is placed on the additive-flow allowlist by the Period Engineer / reviewer (cash paid is an additive flow; 1,816 of 4,834 sample facts are derived); a derived negative or implausible quarter is not stored.
- R8.4 Currency: USD only.

**5. Downstream.** A cash interest coverage metric, FCF-to-equity adjustments, cash vs accrual interest gap. Not an input to EBIT/interest-expense coverage (that uses `interest_expense`). Formula risk: substituting expense for paid, or summing paid with expense; era change of tag mid-series (comparability caution).

**6. Evidence missing.** Taxonomy label, balance, and deprecation status of `InterestPaid` vs `InterestPaidNet` (whether net-of-capitalized is the difference); full-population share of issuers with each tag per era and in the same context; Verifier reads of the cash-flow supplemental notes for company ids 1800, 103, 604; derived-negative review.

**7. Fixtures.**
- F8.1 (named): company 103 2008-2009 InterestPaid 1.225M vs InterestExpense 4.353M -> output 1.225M; expense never substituted.
- F8.2 (named): company 103 2020-10-03..2021-07-02 InterestPaidNet 0 vs InterestExpense 2.6M -> output 0 (reported zero), not 2.6M.
- F8.3 (named): company 1800 2025 H1 InterestPaid 4,629 vs InterestPaidNet 5,870 -> `InterestPaidNet` wins, conflict logged.
- F8.4 (named): company 604 2013 InterestPaid 11.999M vs InterestPaidCapitalized 0.443M -> 11.999M; capitalized not substituted.
- F8.5 (synthetic): neither cash tag present, InterestExpense present -> null.
- F8.6 (synthetic): derived quarter from YTD subtraction negative -> not stored.

---

## 9. income_taxes_paid_cash

**1. Definition.** Cash paid for income taxes during the period (federal, state and foreign combined as the issuer reports the total), from the supplemental cash-flow disclosure, duration, USD, positive = cash outflow as filed. Whether the figure is net of refunds depends on the tag: `IncomeTaxesPaidNet` is net of refunds by its name; the basis of `IncomeTaxesPaid` is unverified. Excludes: income tax expense / provision (accrual), deferred taxes, component tags by jurisdiction (not evaluated here), and dividends-and-interest-paid. Sign: as reported. **A negative net amount (net refund received) is a legitimate reported figure** (303 negative `IncomeTaxesPaidNet` facts across 50 issuers); preserve and flag; do not abs(); derived-quarter negatives from YTD subtraction need review. Zero valid (357 zero facts); missing is not zero.

**2. Name / mode / precedence.** `income_taxes_paid_cash`, cash_flow, `first_match`; precedence 1 `us-gaap:IncomeTaxesPaidNet`. `IncomeTaxesPaid` as fallback: **HOLD** until the label is read and the Verifier confirms the basis (see below).

**3. Classes.** IncomeTaxesPaidNet: exact (agree). IncomeTaxesPaid: **alternate with unverified basis; HOLD (the Tag Mapper has it at precedence 2 as exact predecessor/alternate)**: 192 of 234 shared contexts equal (82%) and 42 unequal; company 612 FY2025 shows `IncomeTaxesPaid` 211.2M < `IncomeTaxesPaidNet` 221.1M, which contradicts the simple "gross, net of refunds" reading (net should not exceed gross), so the basis difference is not understood; company 1051 shows 250,000 vs 24,000 (about 10x). IncomeTaxExpenseBenefit: not_equivalent (cash vs accrual; company 103 FY2008: paid 1.156M vs expense -28.8M).

**4. Rules.**
- R9.1 Never fall back to tax expense.
- R9.2 `IncomeTaxesPaid` enters only after the basis is established; until then, issuers who only file it get null with reason BASIS_UNVERIFIED (lost coverage is the accepted cost).
- R9.3 If both tags exist in the same context and differ, `IncomeTaxesPaidNet` wins and the conflict is logged.
- R9.4 Derivation of quarters by YTD subtraction as in R8.3; refunds make derived quarters sign-sensitive.

**5. Downstream.** Cash tax rate (cash taxes / pretax income), cash vs book tax gap, FCF adjustments, NOPAT cash variants. Formula risk: dividing by pretax income when it is negative or near zero; treating a negative as a data error; mixing net-of-refund and gross figures across eras.

**6. Evidence missing.** Taxonomy labels for both tags; full-population same-context agreement and the cause of the 18% disagreement; Verifier reads for company ids 612, 1051, 103; derived-negative review.

**7. Fixtures.**
- F9.1 (named): company 612 FY2025 Paid 211.2M vs Net 221.1M -> output 221.1M (Net) and a logged conflict; the fallback does not override Net.
- F9.2 (named): company 1051 2025-05-01..07-31 Paid 250,000 vs Net 24,000 -> output 24,000 (Net), conflict logged.
- F9.3 (named): company 103 FY2008 Paid 1.156M vs IncomeTaxExpenseBenefit -28.8M -> never uses expense.
- F9.4 (synthetic): `IncomeTaxesPaidNet` = -5,000,000 (refund) -> stored as -5,000,000 and flagged, not abs().
- F9.5 (synthetic): only `IncomeTaxesPaid` present, policy default -> null (BASIS_UNVERIFIED).

---

## 10. Share-count concepts: common/preferred shares issued and authorized

**1. Definitions (four concepts, plus one added by me).** All balance-sheet instants (usually the balance-sheet parenthetical), unit shares, non-negative integers.
- `common_shares_issued`: shares of common stock issued as of the balance-sheet date, including shares held in treasury (issued >= outstanding in the same class).
- `common_shares_authorized`: maximum number of common shares the charter permits to be issued. A legal cap, not a holding.
- `preferred_shares_issued`, `preferred_shares_authorized`: same for preferred stock.
- **Proposed addition** `preferred_shares_outstanding` (the Tag Mapper lists `PreferredStockSharesOutstanding` as exact with no concept): same perimeter as issued minus treasury; 2,500 of 2,504 shared contexts equal to issued in the sample, but it is a different quantity.
- `shares_outstanding` (existing) is unchanged. **Issued, outstanding and authorized are never substituted for one another.** Weighted-average counts (sections 5-6) are a separate family and are never combined with these by arithmetic.
Reported zero is valid and preserved (2,653 of 3,128 preferred issued facts are zero); a zero does not mean "no authorization" or "no preferred", and missing is not zero.

**2. Names / mode / precedence.** All `first_match`, balance_sheet: `common_shares_issued` = `us-gaap:CommonStockSharesIssued`; `common_shares_authorized` = `CommonStockSharesAuthorized`; `preferred_shares_issued` = `PreferredStockSharesIssued`; `preferred_shares_authorized` = `PreferredStockSharesAuthorized`; `preferred_shares_outstanding` = `PreferredStockSharesOutstanding`. Generic `SharesIssued` and `SharesOutstanding` (640 and 512 companies, "mixed use"): HOLD, not mapped (class unknown).

**3. Classes.** Each class-specific tag: exact for its own concept (agree). Across kinds: not_equivalent (81% issued=outstanding is due to no treasury stock, and the 19% differ; issued vs authorized equal in 4 of 4,267). `dei:EntityCommonStockSharesOutstanding`: not_equivalent to a balance-sheet count (different date and possibly class scope; 35 of 144 pairs unequal); it keeps its existing approved fallback inside `shares_outstanding` only. SharesIssued / SharesOutstanding generic: hold.

**4. Rules.**
- R10.1 No derivation among the three kinds: outstanding != issued unless reported; issued != authorized; `issued - outstanding` as a treasury count is a possible later calculated concept, only when both come from the same class and context and a composition rule is approved; not proposed.
- R10.2 Multi-class issuers: Company Facts exposes no class dimension (dimensional facts are stripped), so an undimensioned value may be one class or a total; the stored value is "the reported undimensioned value", and totals across classes are never summed or assumed. Where an issuer reports share counts only by class (dimensioned), the concept is null with reason DIMENSION_REQUIRED / MULTI_CLASS_NOT_VISIBLE, not an invented total.
- R10.3 Consistency flags (not corrections): issued < outstanding (7 of 4,017 contexts, company 5773 2024-09-30: 2.660B vs 2.960B) and issued > authorized (1 of 4,267, company 1851 2021-06-30: 370.1M vs 150M) are quarantine flags.
- R10.4 Split restatement: later filings restate prior-period share counts after splits; the decision in `doc/data-moat/decisions.md` (latest-filed figure wins for restated periods) applies, but whether a split-adjustment stage covers these new concepts is NOT_RUN (B9); until decided, cross-period comparisons of these counts are caution-flagged.

**5. Downstream.** Dilution trend (should use `shares_outstanding`, not issued), market cap (price x outstanding, per class; issued is never a market-cap input), governance headroom (authorized minus issued is a legal-capacity indicator, not a dilution forecast), buyback detection (issued minus outstanding changes; weak). Formula risk: using issued for per-share book value or market cap; summing classes; comparing a pre- and post-split count; using authorized as a share-count proxy.

**6. Evidence missing.** Full-population issued/outstanding/authorized relationships and multi-class prevalence (needs dimensional data); original cover and balance-sheet parenthetical for company ids 5773, 1851, 1051, 103; whether any consumer metric would use these (metric_definition_input NOT_RUN); custom tags unobservable.

**7. Fixtures.**
- F10.1 (named): company 103 2009-10-02 Issued 177.9M, Outstanding 172.8M, Authorized 525M -> three distinct concept values, none substituted.
- F10.2 (named): company 5773 2024-09-30 Issued 2.660B < Outstanding 2.960B -> both stored as reported, consistency flag raised.
- F10.3 (named): company 1851 2021-06-30 Issued 370.1M > Authorized 150M -> both stored, flag raised.
- F10.4 (named): company 1051 2023-07-31 Outstanding 8.503M vs dei cover 4.929M -> `common_shares_*` unaffected; cover count never enters issued/authorized.
- F10.5 (synthetic): preferred issued = 0 -> stored 0; absent tag -> null.
- F10.6 (synthetic): only generic `SharesOutstanding` present -> not mapped to any of the five.
- F10.7 (synthetic): only a class-dimensioned fact exists -> null, DIMENSION_REQUIRED, no sum.

---

## 11. Cross-cutting policy: combined lines, signs, zeros, fallbacks

**P-COMB (combined lines).**
1. A line that combines two or more economic items (common stock + APIC; basic + diluted; PP&E + finance ROU; payable + accrued) is **never mapped as the plain line**. It gets its own concept (or stays as-reported, unmapped), with `composition = combined`.
2. If a company files **only** the combined line, the plain concept is null with reason COMBINED_LINE_ONLY (disclosure_status = included_in_combined). The as-reported combined value is preserved and shown labeled; it is not split, not scaled, not estimated.
3. A combined line may be used as an input only through an **explicit, named, human-approved, per-concept rule** (for example "treat a BasicAndDiluted weighted-average line as basic"), which records `fallback_used` in lineage and is excluded from the plain concept's coverage count unless the reviewer decides otherwise. Default: no such rule. The decision whether to grandfather or revisit the existing `diluted_eps` priority-3 `EarningsPerShareBasicAndDiluted` fallback and `net_income` priority-3 `NetIncomeLossAvailableToCommonStockholdersBasic` fallback sits with the reviewer; I classify the first as "combined line used as plain" and the second as "attribution crossing (common vs total)", and neither meets this policy as written.
4. Component tags (sub-amounts of a total) are not totals; a calculated total from components requires all components present in the same context, an approved composition rule, and Decimal arithmetic from raw values.
5. Coexistence is not equivalence: matching amounts in shared contexts support a class, they never prove it; "equal" rates of 73-94% in the records are evidence of limited scope.

**P-SIGN (sign).**
1. Source sign and display sign are separate. The canonical value keeps the **reported sign**. No automatic abs().
2. Retained earnings: negative = deficit. APIC: negative legitimate. Cash paid for interest/taxes: positive = outflow; a negative is a flagged exception (net refund for taxes is legitimate; for interest it is suspect). Shares: non-negative; weighted averages strictly positive.
3. **Pre-2015 development-stage deficit tag** (`DevelopmentStageEnterpriseDeficitAccumulatedDuringDevelopmentStage`): reports the deficit as a positive magnitude. It is a component (a deficit accumulated in a period of an entity that had a prior accumulated deficit), not a replacement for the total. Default: unmapped. If a human approves a conditional fill, the rule is `retained_earnings = -(magnitude)`, applied only when no `RetainedEarningsAccumulatedDeficit` exists in the same context and the Verifier has confirmed on the statement that the line is the sole retained-earnings line. Needs a sign-transform mechanism the mapper may not have (B6); this is a one-way, flagged fill, never bidirectional.
4. Sign-conflicting pairs (same magnitude, opposite signs, as with the dev-stage tag) are never "resolved" by choosing the sign that makes them equal.

**P-ZERO (zeros and missing).**
1. A reported numeric zero is a value and is preserved (value_status reported).
2. Missing, not applicable, not separately disclosed, and not reviewed are four distinct non-values; none becomes zero. Applicability (for example pre-ASC 842, partnerships without retained earnings, issuers with no preferred) is recorded separately from value status.
3. A reported zero in a line never implies absence of the economic item elsewhere in the filing (preferred value 0 with preferred APIC; mezzanine preferred).
4. Weighted-average share counts of zero or below are invalid, not "zero".

**P-FALLBACK (fallbacks).**
1. A fallback is allowed only when the fallback tag has the **same economic perimeter** as the target (exact class) and cannot co-exist with a different value in the same context, or is applied per-context so that it can never override a present preferred tag.
2. A fallback across a perimeter (component-as-total, combined-as-plain, cash-as-expense, expense-as-cash, gross-as-net) is not a fallback; it is a different concept or a quarantine.
3. A conditional fallback (APIC common-stock only; development-stage deficit only; `InterestPaid` / `IncomeTaxesPaid` predecessors) is staged `provisional` until the taxonomy label is read, the Verifier has checked original statements, and the resolver is shown to implement the condition.
4. Every applied fallback is recorded in lineage (`fallback_used`) so it can be filtered out.
5. Era-based predecessor tags (InterestPaid then InterestPaidNet) are acceptable only per company-period context, not by calendar cut-off.

**P-DERIVED (derived values).**
1. Averages (weighted-average shares, EPS), positions (balance-sheet instants) and ratios are **never** derived by subtraction. Weighted-average shares may be derived only by the repo's window-weight rule (approximation, `is_derived=true`, positive only). EPS stays reported-only.
2. Reported beats derived whenever both exist; derived values are labeled and can be filtered.
3. An additive flow (interest paid, taxes paid) may be derived by YTD subtraction only if on the additive allowlist; negatives from derivation are reviewed, not stored blindly.

**P-DIM (dimensions, custom tags, units).**
1. Entity-level undimensioned facts only; dimensional and custom-namespace facts are unobservable in `core.fact` today, so any absence claim is scoped to the inspected standard tags.
2. Units must match the concept (USD for amounts, shares for counts); `usd/shares`, CAD, CNY or other currencies are out, not converted.
3. A power-of-ten disagreement between two tags in the same context is a unit/scale quarantine.

**P-BASIS (restated vs as-filed).** Stored figures for restated historical periods follow `doc/data-moat/decisions.md` (latest-filed wins, original kept non-authoritative; carve-outs for mislabeled periods and precision tie-break). Not implemented: "prefer the authoritative same-tag copy when one exists" (39 mismatched rows in a 150-company sample). The first-time conflict rates in the records (weighted-average 392 of 589 conflicted contexts spread more than 15%; primary-tag conflict counts per family) mean any canonical value for a conflicted context is a conflict-resolution fill (up to 15% worst-case disagreement per `mapper/conflict_resolution.py`), not a clean authoritative fact.

---

## 12. Evidence still missing before a human could approve (blockers)

- **B1 Full-population coexistence check per family** (NOT_RUN for all ten). The 150-company sample supports a proposal, not a rule; each family needs the library-wide same-context agreement and disagreement counts for every candidate tag, including the "calculated" identities (Appropriated + Unappropriated, common + APIC = combined, basic + adjustment = diluted).
- **B2 Verifier reading the original statements** (R*.htm / filing HTML, own interpretation before reading the Tag Mapper's rationale) for the named counterexample issuers (company ids): retained earnings 1117, 599, 4393, 1600, 2301, 2952; common stock 1377, 2952, 1800, 607, 3631; preferred 5356, 5714, 3720, 3017; APIC 1851, 2730, 1800, 2952, 4490; weighted average 2052, 1143, 5820, 2260, 103, 1307, 1051, 599, 1020; ROU 1113, 1600, 604 plus the liability-without-ROU issuer; interest 1800, 103, 604; taxes 612, 1051, 103; shares 5773, 1851, 1051, 103. Note the Tag Mapper cites internal company ids; the Verifier needs accession and R-file locators, which the records do not give (source_hash null throughout).
- **B3 Taxonomy label, balance, deprecation and effective-version lookup** for every candidate tag (NOT_RUN): needed for ValueOutstanding variants, InterestPaid vs InterestPaidNet, IncomeTaxesPaid, and the combined tags.
- **B4 Unobservable items**: dimensions (multi-class share counts, segment-only lines), custom/issuer-extension tags (retained earnings, ROU, leases combined with finance), the share of issuers presenting a line only via custom tags. Needs SEC Financial Statement Data Sets or R-files.
- **B5 Weighted-average state**: whether the stored subtraction-derived negative rows were cleared after the 2026-10-17 correction (reprocess status unknown, NOT_RUN); a human reviewer's acceptance of the window-weight approximation (founder adopted it, which is release policy, not accounting approval; the supporting comparison is against yfinance, a comparator); whether the `WeightedAverage%` derive pattern catches non-share tags.
- **B6 Resolver capability** (`mapper/resolve.py` not read): can it express conditional fallbacks and a sign transform, and does it keep `fallback_used` in lineage?
- **B7 No adopted release policy and no qualified human reviewer identified**; all ten stay `proposed`; "verified" at best after the Verifier.
- **B8 Applicability and denominators**: financials, partnerships, and pre-ASC 842 periods must be handled as applicability, not coverage loss; the denominator must not be shrunk silently.
- **B9 Split/restatement policy for the new share-count and weighted-average concepts**: whether the retroactive split-adjustment stage covers them, and how restated comparatives are handled.
- **B10 Downstream inventory**: `metric_definition` and `metric_definition_input` NOT_RUN; the consumer lists above are reasoned candidates, not a catalog of actual inputs.
- **B11 Tag Mapper record clarifications**: meaning of "8 equal" in the retained-earnings vs development-stage coexistence; the retained-earnings/other sample extract artifacts (`extract.py`, `an.py`) were not re-run by me; the "ifrs-full" tags were not sampled.

## 13. Catalog diff proposal (for the reviewer; not applied)

| New concept | Statement | Mode | Primary tag | Gated / held |
|---|---|---|---|---|
| `retained_earnings` | balance_sheet | first_match | us-gaap:RetainedEarningsAccumulatedDeficit | ifrs-full RetainedEarnings hold; dev-stage deficit unmapped |
| `common_stock_value` | balance_sheet | first_match | us-gaap:CommonStockValue | ValueOutstanding hold |
| `common_stock_including_apic` (optional) | balance_sheet | first_match | CommonStocksIncludingAdditionalPaidInCapital, then CommonStockIncludingAdditionalPaidInCapital | low priority |
| `preferred_stock_value` | balance_sheet | first_match | us-gaap:PreferredStockValue | ValueOutstanding hold |
| `additional_paid_in_capital` | balance_sheet | first_match | us-gaap:AdditionalPaidInCapital | common-stock APIC fallback hold |
| `additional_paid_in_capital_common` (optional) | balance_sheet | first_match | AdditionalPaidInCapitalCommonStock | visibility only |
| `weighted_average_shares_basic` | income_statement | first_match | ...OutstandingBasic | value>0, reported or window-weight derived |
| `weighted_average_shares_diluted` | income_statement | first_match | ...DilutedSharesOutstanding | same |
| `weighted_average_shares_basic_and_diluted` | income_statement | first_match | the two combined spellings | combined concept |
| `operating_lease_rou_asset` | balance_sheet | first_match | OperatingLeaseRightOfUseAsset | |
| `interest_paid_cash` | cash_flow | first_match | InterestPaidNet (1), InterestPaid (2, provisional) | gated |
| `income_taxes_paid_cash` | cash_flow | first_match | IncomeTaxesPaidNet | IncomeTaxesPaid hold |
| `common_shares_issued`, `common_shares_authorized`, `preferred_shares_issued`, `preferred_shares_authorized`, `preferred_shares_outstanding` | balance_sheet | first_match | the matching CommonStock/PreferredStock Shares* tag | generic SharesIssued/SharesOutstanding hold |

No `sum` mode anywhere. No `concept_mapping` edit is proposed before blockers B1-B3 clear, in line with the decisions.md rule that a global mapping change needs multi-company evidence (a single flagged company is a lead, not evidence).
