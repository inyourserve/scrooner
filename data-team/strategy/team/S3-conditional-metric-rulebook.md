# S3. Conditional-metric rulebook (Standardization Lead, 2026-10-21)

Status: PARTIAL (rulebook drafted for every conditional data point; nothing approved; four live defects found and routed). Every definition below is **PROPOSED**. None is approved; items marked **[ACCT]** need the named accountant (not yet named, data-team/27 next action 4) before they can drive a displayed state. No agent approves its own rule; this file goes to the Verifier next.

Role: Standardization Lead. Objective: define how a template cell that is legitimately not a plain number resolves, with the evidence that proves it, whether it counts as covered, and how it propagates. Scope: the 163 data points in `data-team/strategy/data/cohort_cells.csv` (986 companies, top-1000 cohort), classes E1, M1, H1, A1 from BRIEF2 plus the pre-revenue overlay. Read-only: no code, migration or shared-table write. Evidence labels: FILING-CHECKED (filing opened, accession + locator), DATA-INFERRED (our tables or code reading), ASSUMED.

Inputs read: BRIEF.md, BRIEF2.md, data-team/20, 21, 22, 11, 03, 27 (decision 3), 30 (sections 3 and 5), strategy/41, 44, team/R4, R5; code (read-only) `mapper/definitions.py`, `expanded_definitions.py`, `expanded_metrics.py`, `price_metrics.py`, `quality_flags.py`, `ttm.py` (`_growth_value`, `CONCEPT_MATERIALITY_FLOORS`), `calculate_shapes/{ratio,days,sum_diff_ratio,materiality}.py`, `dividend_streak.py`, `coverage_matrix.py` (`SIC_GAP_REASONS`, populations), `company_coverage_dashboard.py`, `common/sector_applicability.py`.

## 0. What I found that changes the rulebook (read first)

| # | Finding | Evidence | Class |
|---|---|---|---|
| F1 | **Growth over a negative base is computed and published with the wrong meaning.** `ttm._growth_value` returns `(t - p)/p` for YoY whenever `p != 0` and above the floor, so a loss-to-profit turnaround shows as a decline: RDDT net income FY2024 -484,276K -> FY2025 +529,721K is stored as `net_income_growth_yoy` = -209.5%. For CAGR it nulls only when the ratio is negative, so two losses produce a "growth" rate: Ford (company 417) net income FY2020 -1,276M -> FY2025 -8,162M is stored as `net_income_growth_5y_cagr` = **+44.9%**; TAP 3y CAGR +130.2% with both ends losses. In the cohort (latest FY ending 2024-06 or later, my replica of the engine on `canonical_fact`): 123 NI and 122 EPS YoY values sit on a negative prior; 72/72/24 NI and 66/71/26 EPS 3y/5y/10y CAGRs have both ends negative. These are wrong displayed values, not blanks. | RDDT inputs FILING-CHECKED: 0001713445-26-000022 R8 and R5 ("Net income (loss)" 529,721 / (484,276) / (90,824), $K). Stored values DATA-INFERRED (`analytics.metric_value`, company 10, 417, 301). Counts DATA-INFERRED (query in section 9) | M1 defect |
| F2 | **Negative-denominator ratios are published as numbers.** Cohort latest values below zero: trailing P/E 117 (Ford -7.81), payout ratio 24 (PFE -21.5, Ford -0.36, TAP -0.17), PEG 36 (Ford -0.0185: negative P/E divided by positive growth passes the `eps_growth <= 0` guard), ROE 145 (46 cohort companies have negative latest-FY equity, where a loss over negative equity shows as a positive ROE), P/B 48, debt/equity 44, EV/EBITDA 58, OCF/NI 130. Not all negatives are wrong (a negative margin or a negative FCF yield is a value), so section 3 splits them per metric. | DATA-INFERRED (`metric_value`, latest row per company, section 9 query Q1); code read `price_metrics.py` L372-383, `expanded_metrics.py` L633-645, `ratio.py` | M1 defect |
| F3 | **Total shareholder yield counts unmapped dividends as zero.** `expanded_metrics.py` L686-690 treats a missing `dividends_ttm` as $0 on the stated assumption that `dividends_paid` capture is complete for payers. It is not: JNJ, PFE and CL file cash dividends under `PaymentsOfOrdinaryDividends` (JNJ and PFE since 2007, CL since 2009), which `dividends_paid` does not map (only `PaymentsOfDividends`, `PaymentsOfDividendsCommonStock`). PFE's stored TSY is **-0.25%** while its dividend yield is 5.7% and its 10-Q shows "Cash dividends paid (4,896)" ($M, 6M 2026). In the cohort, 26 of the 280 companies with a blank `dividends_paid` file a common-dividend or distribution tag we do not map (ACGL, CL, CQP, EPD, ET, GE, JNJ, MPLX, PAA, PFE, SPG, ZTS and others), and 225 companies have a TSY value while `dividends_paid` is blank. So "no dividends_paid fact" can never be the evidence for a non-payer. | PFE FILING-CHECKED: 0000078003-26-000095 R8, row "Cash dividends paid", defref `us-gaap_PaymentsOfOrdinaryDividends`. Tag usage DATA-INFERRED (`company_sec_tag`, `concept_mapping`) | E1 defect |
| F4 | **A SIC label prints "Pre-revenue biotech/pharma -- genuinely has no revenue yet" on 44 revenue-reporting companies.** `coverage_matrix.SIC_GAP_REASONS` maps SIC descriptions "Pharmaceutical Preparations" and "Biological Products" to `pre_revenue_biotech_pharma` for every revenue-family blank (gross profit, cost of revenue, operating expenses, operating income). In the cohort it fires on ABT, ABBV, AMGN, BMY, GILD, JNJ, LLY, MRK, PFE, REGN, VRTX, ZTS and 32 others, all with revenue in hand. Only 1 cohort company (PCVX) has no revenue. The reason is wrong text on a displayed blank and violates "SIC alone is never evidence". | DATA-INFERRED (`cohort_cells.csv` gap_reason with `revenue` has_value=t; code read `coverage_matrix.py` L50-67) | Overlay defect |
| F5 | **About 42% of "history" blanks are not history.** Of 1,879 cohort blanks with `missing:prior_period(...)`, 961 belong to companies whose first 10-K/10-Q under the CIK was filed after the base window (plausible H1), 132 are borderline (first periodic filing in the year after the base year, so the first 10-K may carry the base year), and **786 belong to companies that were filing during the base year** (a period or mapping defect, not short history). Example: 153 of 342 `revenue_growth_10y_cagr` history blanks. Also, the latest cell for 10y CAGRs is often a single-quarter row (Q2 2026 vs Q2 2016), which ties history coverage to quarterly derivation. | DATA-INFERRED (`core.filing` first periodic filing date per company vs the base year in the gap reason; does not see predecessor CIKs, R5 section 7) | H1 split |

Defects F1 to F4 are routed in section 8. They are the reason the rulebook below defines states by **verified inputs and filing evidence**, never by the absence of one of our tags or by a SIC label.

## 1. The cell state model (PROPOSED)

Every template cell resolves to exactly one state. States extend data-team/41 section 3 (four resolutions) and data-team/30 section 3.0 (evidence classes); BRIEF2 class names are kept.

| State | Meaning | Shown as | Counts as covered? | Evidence required to count |
|---|---|---|---|---|
| V | Reported or derived value | the number | yes, once certified (data-team/34) | filing locator + formula version |
| Z (BRIEF2 **E1**) | Evidenced zero activity: the activity did not occur in the window | "None" text or 0 with a label (per metric, section 2) | **yes** | tag-agnostic filing evidence for every filing in the window (section 2.1); never "no fact under our tags" |
| NM (BRIEF2 **M1**) | Math undefined or not meaningful: verified inputs make the formula meaningless (non-positive base or denominator, immaterial base) | "Not meaningful: <reason>" | **yes, only if every input it names is itself V or Z and certified** | the input values and their locators; the rule ID |
| SH (BRIEF2 **H1**) | History shorter than the window | "History shorter than N years (data from FY<first>)" | **yes, only with the first-period evidence** (section 2.3) | earliest period with any XBRL fact for the concept across all filings (incl. S-1/10-12B comparatives), and no predecessor-CIK link (R5 list) |
| NP (BRIEF2 **A1**) | Line not presented on the filer's own statements, or presented only combined | "Not reported separately by this company" / "Reported combined with <label>" | **yes, only with FILING-CHECKED evidence or an audited detector** (section 2.4) | accession + statement + R-file or presentation row; for the detector: a passed 30-per-family audit with zero false absents (R4 control c) |
| PR (overlay) | Pre-revenue: no material revenue in the window | "Pre-revenue: no material revenue (TTM revenue $X)" | yes, for the revenue-denominated cells only | section 2.5 |
| NT | Not in the group's template | the cell does not exist | not a cell (outside the denominator by group membership, data-team/41 section 2) | audited group membership |
| OPEN | Any other blank: input missing, not extracted, conflict, period gap, unknown | "Not available yet" (internal: defect register with root-cause pointer) | **no, never** | n/a |

Rules that apply to every state:
- S1. Never convert OPEN, NP, SH or NT to zero. Only Z is a zero, and only with section 2.1 evidence.
- S2. A displayed reason must name its rule ID and evidence locator in lineage (same field the UI already renders, `is_null_reason`, extended with the rule ID; storage is an engineering choice, R6).
- S3. A state derived from our own values (NM) is only as good as those values: if any named input is OPEN or uncertified, the cell is OPEN.
- S4. When the condition is false, the metric is computed normally; when the evidence is missing, the cell is OPEN, never the conditional state.
- S5. Effective-dating: the condition is evaluated per period (a non-payer that starts paying leaves Z in the first window that contains a payment; a pre-revenue company leaves PR in the first fiscal year it presents revenue).

## 2. The five classes: condition, evidence, state, coverage, wording

### 2.1 E1 / Z: evidenced zero activity (PROPOSED)
Applies to activity concepts only: dividends to common holders, share repurchases, borrowings (data-team/27 decision 3), interest expense, capital expenditure, stock-based compensation, acquired-intangible amortization. Never to balance-sheet lines like inventory or goodwill (those are NP, section 2.4).

| Concept | Condition (true -> Z) | Evidence (all required) | Counterexamples the rule must survive |
|---|---|---|---|
| Dividends to common (TTM window and FY window) | No cash dividend or distribution to common holders paid or declared in the window | (a) every filing covering the window (latest 10-K plus later 10-Qs; cash flow is YTD, data-team/21 s2) has **no financing row whose label or tag denotes dividends or distributions to common or unit holders** (rendered R-file or FSDS `pre.txt`); (b) no DPS-declared or DPS-paid fact for the window in **any** tag of the family, including per-class dimensioned facts (ledger 2026-10-19 BRK/GOOGL) and the quarterly-rate-on-annual-context pattern (ledger V, LEA); (c) optional E4: Item 5 text "never declared or paid" | PFE/JNJ/CL use `PaymentsOfOrdinaryDividends` (F3); MLPs use `PartnersCapitalAccountDistributions` / `DistributionMadeToLimitedPartnerCashDistributionsPaid`; preferred-only dividends do not make a common payer; NCI distributions (`PaymentsOfDividendsMinorityInterest`) do not make a common payer; a dividend declared after period end is not paid in the window but must be noted |
| Share repurchases | No repurchase of common stock in the window | no financing row for repurchase of common stock in any window filing; treasury-stock purchases in the equity statement also absent | RSU net-share-settlement tax payments are NOT buybacks (RDDT R8 "Taxes paid related to net share settlement" (104,028)K, FILING-CHECKED); AMD 3-month equity-statement repurchase columns carry YTD (ledger 2026-10-21) |
| Borrowings (`total_debt`) | No borrowings outstanding at the instant | data-team/27 D3: E4 filing text "no borrowings outstanding" **and** no borrowing line on the face BS (CATO). A face BS with no debt line and no debt note (ATEX) is NOT Z: it stays OPEN with "No borrowings reported" until the accountant rules [ACCT] | leases are outside borrowings (vendor "Total Debt" includes them, ledger CATO/ATEX); finance-lease perimeter is open (ledger Walmart) |
| Interest expense | No interest expense in the window | borrowings Z for every instant in the window **and** no interest-expense row on the face IS or in the notes | interest can be capitalized, or sit inside "other expense, net" (combined -> NP, not Z) |
| Capex | No capital expenditure in the window | no investing row for property, equipment, software or productive assets in any window filing | capex can sit on `PaymentsToAcquireProductiveAssets`, software or flight-equipment rows (ledger Aptiv, ArcBest, Air Lease) |
| SBC | No share-based compensation in the window | no operating-section add-back row for share-based compensation and no SBC expense fact | SBC can be combined with other non-cash items (NP combined) |

State shown when true: Z. Wording: "No dividends paid in the last 12 months" / "No share repurchases in the last 12 months" / "No borrowings outstanding (filing states none)" / "No capital expenditure reported". Covered: yes, with all evidence items stored with accessions. If evidence item (a) is the only proof, the label is DATA-INFERRED until the detector passes the R4-style audit; until then the cell is OPEN.

### 2.2 M1 / NM: math undefined (PROPOSED)
Condition is on verified input values. Two generic rules, then per-metric rules in section 3.
- M1-G (growth). YoY growth is NM when the prior value is <= 0 or below the concept's materiality floor (`ttm.CONCEPT_MATERIALITY_FLOORS`). A CAGR is NM when the start **or** the end value is <= 0, or the start is below the floor. Wording: "Not meaningful: prior-year value negative" / "... base value zero" / "... base too small" / "Not meaningful: loss in start or end year". Optional companion text (product): "Turned profitable", "Loss widened", "Loss narrowed" (a direction word, not a percentage) [ACCT for the wording]. **This replaces today's behaviour (F1), which publishes sign-inverted and both-negative values.**
- M1-R (ratios). A ratio is NM when its denominator is <= 0 for the ratio families listed in section 3 (P/E, PEG, payout, ROE, P/B, D/E, EV and EBITDA multiples, coverage, OCF/NI, dilution spread, ROIC invested capital, ETR), or when its denominator is below the materiality floor. Wording names the input: "Not meaningful: negative earnings", "Not meaningful: negative shareholders' equity", "Not meaningful: negative EBITDA".
- A negative **result** is still a value when the denominator is positive and the metric is a margin, yield or return (operating margin -12%, FCF yield -3%, ROE -20% on positive equity, net cash per share negative). Only the denominator sign decides NM.
Covered: yes, if every input the rule reads is V (certified). Evidence: the input values with their source facts, the rule ID, the floor version.

### 2.3 H1 / SH: history shorter than the window (PROPOSED)
Condition: the required base period ends before the company's earliest available period for that concept.
Evidence: (a) earliest period end with any XBRL fact for the concept, across all filings including comparatives in the first 10-K and S-1/10-12B (ledger 2026-10-18: Apple's first XBRL 10-Q tags 2007-2008; RDDT's first 10-K, filed 2025-02-13, carries FY2022 net income); (b) no predecessor CIK (R5 section 7 lists MRVL, DIS, STE, BLK and others; a link must be FILING-CHECKED before history is joined); (c) the base period is not inside a fiscal-year change or transition period (10-KT).
NOT H1 (stays OPEN): the company filed during the base period but the value is missing (F5: 786 cohort cells), a quarter that was never derived, a conflict, an era tag we do not map (R5 section 3: 134 FY2015 filers with no mapped revenue tag).
History gate interaction [founder/product decision, not accounting]: doc 38 forbids pre-2015 data as current for display; a 10y CAGR ending FY2024 needs FY2014 as its base. Proposed: a base period may be used as the start point of a growth rate if the fact itself is post-2009 XBRL and certified, because the gate is about "current" display; otherwise every 10y CAGR ending before FY2025 is SH by policy and must say "Base year before 2015 not used".
Wording: "History shorter than 10 years: first reported fiscal year FY2022". Covered: yes, with (a) and (b) stored.
Period basis [ACCT]: growth cells should be evaluated on FY (or TTM) bases, not single quarters (a 10y Q2-vs-Q2 CAGR is a quarter's seasonality compounded); proposed: growth templates show FY and TTM rows only, quarter rows remain series data.

### 2.4 A1 / NP: line not presented on the statements (PROPOSED)
Condition: the line is not on the face statement of the filing in force for the period, and no undimensioned fact for it exists in the filing (notes included), and no dimension-only face row sums to it (ledger CAT, AMH, BRK).
Evidence: accession + statement + R-file row list (FILING-CHECKED), or the `company_filing_line_evidence` detector (accession, statement, matched label) after a passed audit. Today the detector covers only 9 lines (AP, AR, cost of revenue, goodwill, gross profit, interest income, inventory, operating expenses, R&D; IS/BS only, no cash flow) and is label-regex based (DATA-INFERRED; 14-34% of held values show no face line, CLAUDE.md 2026-10-13).
Sub-states: NP-absent ("Not reported separately by this company") and NP-combined ("Reported combined with <filed label>"). A combined line is never mapped as the narrow concept and never split by subtraction without an approved composition rule (data-team/11 example boundary).
Covered: yes for NP-absent and NP-combined, only with the evidence above. A1 is never a zero in arithmetic unless a metric-specific rule in section 3 says so and the accountant approved it.

### 2.5 Pre-revenue overlay / PR (PROPOSED)
Condition (per fiscal year, effective-dated): revenue TTM (or FY) is reported and below the $1M materiality floor (`REVENUE_TTM_MATERIALITY_FLOOR`), **or** the latest 10-K income statement presents no revenue line (NP-absent for revenue, FILING-CHECKED or audited detector), and the company is an operating company (not SPAC/trust, which are NT). SIC is a hint for which companies to check, never the evidence (F4).
Effect: every revenue-denominated cell becomes PR (list in section 3, marked "PR"); EPS-based ratios usually become NM through M1 (negative earnings) on their own evidence, not through the overlay.
Exit: the first fiscal year in which revenue is >= $1M or a revenue line is presented; history keeps the overlay for earlier years.
Wording: "Pre-revenue: no material revenue in the last 12 months (TTM revenue $0.4M)". Covered: yes, with the revenue value or the NP evidence.
Overlay additions (cash runway, accumulated deficit, equity proceeds) belong to the Sector Analyst template, not this rulebook (data-team/41 section 5).

## 3. Per-metric rulebook (every conditional data point among the 163)

Columns: class(es) that can apply; condition -> state; covered and evidence; propagation; current code behaviour (code read, DATA-INFERRED); [ACCT] where the named accountant must decide. Cohort blank counts are from `cohort_cells.csv` (DATA-INFERRED). "num"/"den" = numerator/denominator. All rows PROPOSED.

### 3.1 Dividend and capital-return family
| Data point | Classes | Condition -> state | Covered / evidence | Propagation, dependents | Today |
|---|---|---|---|---|---|
| dividends_paid, dividends_paid_resolved | Z, OPEN | non-payer per 2.1 -> Z "No dividends paid in FY/TTM" | yes with 2.1 evidence | feeds dividend_yield (via DPS), dividends_pct_fcf, cash_returned, TSY, payout_ratio; Z -> 0 in those | blank 280; 26 cohort payers on unmapped tags (F3) |
| dividends_per_share(_resolved) | Z, OPEN | non-payer -> Z; quarterly rate tagged on FY context -> OPEN (ledger V/LEA) | yes with 2.1 | dividend_yield, payout_ratio, dps growth, streak | blank 294 |
| dividend_yield | Z, OPEN | DPS Z -> **0% shown as "No dividend"** | yes with 2.1 | TSY dividend term | `missing:dividends_per_share_ttm` 453 |
| payout_ratio | Z, NM, OPEN | DPS Z -> "No dividend" (0%); diluted EPS <= 0 (same period) -> NM "Not meaningful: negative earnings"; period basis must match (FY DPS / FY EPS; never quarterly DPS over quarterly EPS mixed with a FY-context rate) [ACCT basis] | NM needs certified EPS | none | negative values stored (PFE -21.5, F2); 405 blank |
| dividends_pct_fcf | Z, NM, OPEN | dividends Z -> 0% "No dividend"; FCF TTM <= 0 -> NM "Not meaningful: negative free cash flow" | as above | none | 563 blank (378 missing dividends TTM) |
| dividend_growth_streak_years | Z, SH, OPEN | non-payer -> Z "No dividend" (not 0 years, which reads as "paid but did not raise"); payer whose streak reaches the first available FY -> V with qualifier ">= N years (all available history)"; FY DPS that is a quarterly rate -> OPEN | Z needs 2.1 (today `no_dividend_history` = no DPS fact, not evidence) | none | `no_dividend_history` 323 (BRIEF2 E1) |
| dps_growth_yoy, dps_growth_3y_cagr | Z, NM, SH, OPEN | both ends Z -> "No dividend"; prior DPS Z and current > 0 -> NM "Dividend initiated in FY<t>"; current Z and prior > 0 -> V -100% with label "Dividend suspended" [ACCT wording]; base window before first period -> SH | per class | none | 431/370 blank; `zero_base_value` 12/29 |
| share_buybacks(_resolved) | Z, OPEN | no repurchase per 2.1 -> Z "No buybacks" | 2.1 | buyback_yield, share_repurchases_pct_fcf, cash_returned, TSY | blank 89 |
| buyback_yield | Z, OPEN | buybacks Z -> 0% "No buybacks" | 2.1 | TSY | `missing:share_buybacks_ttm` 291 |
| share_repurchases_pct_fcf | Z, NM, OPEN | buybacks Z -> 0%; FCF TTM <= 0 -> NM | as above | none | 445 blank |
| cash_returned_to_shareholders | Z, OPEN | sum of dividends and buybacks; a Z component enters as 0; an OPEN component makes the sum OPEN; both Z -> 0 "No capital returned" | each component's evidence | none | `incomplete:add` 477 |
| total_shareholder_yield | Z, SH, OPEN | components enter as 0 only when Z; an OPEN dividend or buyback component makes TSY OPEN (replaces the unconditional $0 default, F3); dilution SH (no share count ~1y ago because first filing is younger) -> SH | each component | none | stored -0.25% for PFE (F3); 123 blank |

### 3.2 Valuation family (price-dependent)
| Data point | Classes | Condition -> state | Covered / evidence | Propagation | Today |
|---|---|---|---|---|---|
| trailing_pe | NM, PR, OPEN | TTM diluted EPS <= 0 (or TTM net income <= 0 on the market-cap / net-income fallback) -> NM "Not meaningful: negative earnings" | certified TTM EPS (no derived Q4 EPS: ledger 2026-10-21 MSFT/AAPL) | PEG | negatives stored (117 cohort, Ford -7.81, F2) |
| peg_ratio | NM, SH, OPEN | P/E NM -> NM; growth <= 0 -> NM "Not meaningful: earnings not growing"; growth input must be the same basis as P/E (TTM vs FY) [ACCT]; growth SH -> SH | inputs certified | none | negative P/E passes guard (Ford -0.0185); `non_positive_growth_not_meaningful` 328; growth read is "latest eps_growth_yoy", which can be a quarter row |
| price_to_book | NM, OPEN | equity <= 0 -> NM "Not meaningful: negative shareholders' equity" | certified equity | none | 48 negative |
| price_to_sales, ev_sales | PR, NM, OPEN | PR overlay -> PR; EV <= 0 (ev_sales) -> NM | revenue evidence | none | 60 / 57 blank |
| ev_ebitda | NM, OPEN | EBITDA TTM <= 0 -> NM "Not meaningful: negative EBITDA"; EV <= 0 -> NM; partial EV (debt or cash missing) -> OPEN, never a value with a "partial" reason | certified EBITDA | none | 58 negative; today a partial EV is stored as a value with `partial:missing_debt_or_cash` |
| fcf_yield | V (negative ok), OPEN | negative FCF is a value | | none | 255 blank: input blanks |
| market_cap | OPEN | no conditional state (share count stale or price stale is OPEN) | | all price metrics | 0 blank |

### 3.3 Leverage, coverage and return family
| Data point | Classes | Condition -> state | Covered / evidence | Propagation | Today |
|---|---|---|---|---|---|
| debt_to_equity | Z, NM, OPEN | debt Z -> 0 "No borrowings"; equity <= 0 -> NM "Not meaningful: negative equity" | 2.1 + equity | none | 44 negative |
| zero_debt | Z, OPEN | 1 only with borrowings Z evidence (2.1, data-team/27 D3 E2); 0 when debt V > 0; ATEX-type (no line, no note) -> OPEN [ACCT] | 2.1 | none | `missing:total_debt` 184 |
| net_cash, net_cash_per_share | Z, OPEN | debt Z enters as 0; negative result is a value ("net debt") | 2.1 | none | 208 / 865 blank (mostly period alignment, OPEN) |
| debt_to_ebitda, net_debt_ebitda | Z, NM, OPEN | debt Z -> 0x "No borrowings" (debt_to_ebitda) and net cash / EBITDA as a value (negative = net cash); EBITDA TTM <= 0 -> NM | 2.1 + certified EBITDA | none | 118 negative net_debt_ebitda (mix of valid net cash and invalid negative EBITDA) |
| interest_coverage_ratio | Z, NM, NP, OPEN | interest expense Z -> "No interest expense" (not a number; covered) ; operating income <= 0 -> NM "Not meaningful: operating loss" [ACCT: some practice shows negative coverage]; interest expense below $10K floor -> NM; interest inside a combined "other expense, net" -> NP-combined | per class | none | 788 blank (588 `incomplete:denominator`) |
| roe | NM, OPEN | average or ending equity <= 0 -> NM "Not meaningful: negative shareholders' equity"; negative NI on positive equity is a value | certified equity | none | 145 negative; loss over negative equity shows positive ROE (F2) |
| roa | NM, OPEN | total assets below floor -> NM (exists) | | none | 14 blank |
| roic | NM, NP, OPEN | invested capital <= 0 -> NM; income before tax <= 0 makes the tax-rate term undefined -> [ACCT: NOPAT = OI x (1 - statutory rate), or NM]; operating income NP (banks) -> NT by template | inputs certified | none | 422 blank (mostly debt/OI inputs: OPEN) |
| effective_tax_rate_gap | NM, OPEN | income before tax <= 0 -> NM "Not meaningful: pretax loss" | | none | 89 blank |
| ocf_to_net_income | NM, OPEN | net income <= 0 -> NM; negative CFO on positive NI is a value (a real signal) | certified NI | none | 130 negative |
| eps_dilution_spread | NM, OPEN | basic EPS <= 0 -> NM "Not meaningful: loss per share (anti-dilution)" | | none | 23 blank |
| book_value_per_share | V (negative ok), OPEN | negative equity gives a negative value, shown | | none | 851 blank: period alignment of equity vs shares (OPEN, not conditional) |

### 3.4 Growth family (M1-G and H1 apply to every row)
`revenue_growth_yoy/3y/5y/10y`, `eps_growth_yoy/3y/5y/10y`, `net_income_growth_yoy/3y/5y/10y`, `fcf_growth_yoy/3y/5y`, `diluted_shares_growth_yoy/3y/5y`, `dps_growth_*` (3.1).
- Condition -> state: M1-G (section 2.2) -> NM; base before earliest available period (2.3) -> SH; revenue below floor in the base year -> NM "base too small" (existing `immaterial_prior_base`), or PR if the overlay applies to that year.
- Covered: NM needs both endpoint values certified; SH needs 2.3 evidence; F5's 786 "filed during base year" cells stay OPEN.
- Propagation: eps_growth_yoy -> PEG. Restated or recast bases: both endpoints must come from compatible bases (ledger MSFT 2016 606 recast, LLY 8-K recast); a cross-basis pair is OPEN, not NM [ACCT for the basis policy].
- Per-share rows: never compare split-unadjusted with adjusted values (ledger BURU, NVDA); a pair across an unadjusted split is OPEN.
- Today: sign-inverted YoY and both-negative CAGR published (F1); `negative_ratio_undefined_cagr` 968 cohort cells already NM-like.

### 3.5 Operating-structure family (A1/NP drives these)
| Data point | Classes | Condition -> state | Covered / evidence | Propagation | Today |
|---|---|---|---|---|---|
| research_and_development | NP, PR, OPEN | no R&D line (2.4) -> NP "No R&D expense reported separately"; R&D inside "SG&A and R&D" -> NP-combined. **Never 0** (data-team/30 rnd row) | 2.4 | rnd_intensity | `line_not_presented_in_filing` 500 (detector, DATA-INFERRED) |
| rnd_intensity | NP, PR, OPEN | R&D NP -> NP "No R&D line reported"; PR overlay -> PR | inherits R&D evidence | none | `incomplete:numerator` 632 |
| inventory | NP, OPEN | no inventory line -> NP "No inventory reported" | 2.4 | inventory_days, CCC, quick_ratio, inventory reconciliation, cf_inventory_change | 359 NP (detector) |
| inventory_days | NP, NM, OPEN | inventory NP -> NP; cost of revenue NP -> NP; cost of revenue <= 0 -> NM | | CCC | 498 blank |
| cash_conversion_cycle | NP, NM, OPEN | any of DSO, DIO, DPO is NP -> NP "Not applicable: no inventory/receivables/payables line" **unless** the accountant approves a differently named variant (DSO - DPO for inventory-free companies, data-team/30) [ACCT]; inputs must be the same FY (today each input's own latest FY is used, `expanded_metrics.py` L463-491) | | none | 598 blank; 359 cohort companies with inventory NP |
| quick_ratio | NP, OPEN | formula is (current assets - inventory) / current liabilities; inventory NP on a classified balance sheet -> [ACCT: treat inventory as 0 so quick = current ratio, or show NP]; unclassified BS -> NT/NP | | none | 169 blank (160 `''`, 167 cohort companies have no current assets) |
| current_assets, current_liabilities, current_ratio, working_capital | NP, NT | unclassified balance sheet (2.4 evidence, R-file shows no current subtotal) -> NP "Balance sheet not classified into current and non-current"; banks/insurers/REITs -> NT | 2.4 | quick_ratio, piotroski | 167 blank each, no reason recorded |
| accounts_receivable, accounts_payable | NP, OPEN | NP-absent or NP-combined ("accounts payable and accrued liabilities", never plain AP) | 2.4 | debtor_days, payables_days, CCC, reconciliation gaps, cf_*_change | 242 / 267 blank; AP combined 116 |
| debtor_days, payables_days | NP, NM, PR, OPEN | input NP -> NP; revenue PR -> PR (debtor days); cost of revenue <= 0 -> NM | | CCC | 318 / 438 blank |
| ar/ap/inventory_change_reconciliation_gap | NP, SH, OPEN | balance line NP -> NP; cash-flow change line NP -> NP; prior FY absent by history -> SH | 2.4 / 2.3 | none | 498/545/507 blank, mostly `''` (no reason recorded) |
| cf_ar_change, cf_ap_change, cf_inventory_change | NP, OPEN | no such operating-section row -> NP; combined working-capital line -> NP-combined | 2.4 (cash flow not in today's detector) | reconciliation gaps | 365/422/413 blank, no reason |
| goodwill | NP, OPEN | no goodwill line and no goodwill note -> NP "No goodwill reported"; "goodwill and intangibles" combined -> NP-combined | 2.4 | goodwill_pct_assets | 94 NP |
| goodwill_pct_assets | NP, OPEN | goodwill NP-absent -> [ACCT: 0% "No goodwill" (a balance with nothing recorded is economically zero) or NP]; combined -> NP | | none | 190 blank |
| cost_of_revenue, gross_profit (+ _resolved) | NP, PR, NT, OPEN | no cost line -> NP; gross profit not presented but revenue and cost are -> V derived (not NP); banks/insurers -> NT | 2.4 | gross_margin, margin_expanding_3yr, inventory_days, payables_days, piotroski | 276/466 blank; SIC pre-revenue reason misapplied (F4) |
| gross_margin | NP, PR, NT, OPEN | cost of revenue NP -> NP "No cost of revenue line"; PR -> PR | | margin_expanding_3yr, piotroski | 391 blank |
| margin_expanding_3yr | NP, SH, PR, OPEN | gross margin NP -> NP (a renamed "operating margin expanding" variant is a new metric, data-team/30); fewer than 3 consecutive FYs since first period -> SH; non-consecutive because of a missing year inside filed history -> OPEN | | none | `missing:fewer_than_3_years_gross_margin` 530 (mostly NP, not history) |
| operating_expenses(_resolved), sga_expense, sga_pct_revenue | NP, PR, OPEN | NP-absent / combined; sga_pct_revenue PR -> PR | 2.4 | none | 580/149/187 blank |
| operating_income(_resolved), operating_margin | NP, NT, PR, OPEN | single-step IS with no operating subtotal -> NP (do not derive from CostsAndExpenses without the identity check, ledger CVX/XOM/HP); banks -> NT; margin PR -> PR | | ebitda, interest coverage, roic | 155/209 blank |
| depreciation_and_amortization(_resolved), amortization_of_intangibles | NP, Z, OPEN | anchor D&A to the cash-flow add-back total (ledger Kura, AMD); no amortization row and no finite-lived intangibles -> Z "No intangible amortization" [ACCT] | 2.1/2.4 | ebitda family | 126/151 blank |
| ebitda, ebitda_margin | NP, NM, PR, OPEN | operating income NP -> NP; negative EBITDA is a value; ebitda_margin PR -> PR; banks NT | | EV/EBITDA, debt/EBITDA, net debt/EBITDA (NM when EBITDA <= 0) | 427/452 blank (`missing:4_consecutive_quarters`, OPEN) |
| interest_income | NP, OPEN | no interest income row (corporates often net it into "other income") -> NP / NP-combined | 2.4 | net_interest_income | 521 blank |
| interest_expense(_resolved) | Z, NP, OPEN | per 2.1 / combined "interest expense, net" -> NP-combined (sign per ledger ANDE/BBW) | | interest coverage, roic inputs | 136 blank |
| other_income_expense_net | NP, OPEN | no other income line -> NP | 2.4 | none | 314 blank, no reason |
| capex(_resolved), capex_pct_revenue | Z, OPEN, PR | capex Z per 2.1 -> 0; capex_pct_revenue PR -> PR | 2.1 | fcf family, fcf_gt_net_income | 81/191 blank |
| fcf, fcf_margin, fcf_per_share | V (negative ok), PR, OPEN | fcf_margin PR -> PR; negative is a value | | fcf growth, payout-of-FCF ratios (NM when FCF <= 0) | 176/191/281 blank |
| fcf_gt_net_income | Z, OPEN | capex Z enters as 0 | 2.1 | none | `missing:capex` 148 |
| sbc, sbc_pct_revenue | Z, PR, OPEN | SBC Z -> 0%; PR -> PR | 2.1 | none | 20/148 blank |
| net_margin, pretax_margin | PR, NT(bank pending), OPEN | PR -> PR; revenue floor -> NM (exists) | | none | 26/88 blank |
| comprehensive_income | NP, Z, OPEN | a company with no OCI items may present no statement of comprehensive income (ASC 220) -> [ACCT: comprehensive income = net income, or NP] | 2.4 | none | 28 blank |
| effective_tax_rate_reported | NP, NM, OPEN | rate not disclosed as a number -> NP; pretax loss -> NM | | effective_tax_rate_gap | 42 blank |

### 3.6 Scores, streaks and share-count rows
| Data point | Classes | Condition -> state | Covered / evidence | Today |
|---|---|---|---|---|
| piotroski_f_score | NP, SH, NT, OPEN | any of the 9 tests' inputs NP (gross margin, current ratio) -> NP "Not computable: needs gross margin and a classified balance sheet"; no prior FY -> SH; banks/insurers/REITs -> NT. No reduced-test variant under this name (data-team/30) | per input | 710 blank |
| profitable_streak_years | SH, OPEN | streak reaching the earliest available FY -> V with ">= N years (all available history)" [product wording]; latest FY NI missing -> OPEN | 2.3 | 9 blank |
| share_dilution_trend, diluted_shares_growth_* | SH, OPEN | no share count ~1y (or N y) before because the first period is younger -> SH; multi-class issuers with only dimensioned cover counts (data-team/21 s8.7) -> OPEN until per-class sum is approved | 2.3 | `missing:share_count_1y_ago` 110 |
| institutional_ownership_pct | OPEN (data defect) | > 100% is a denominator defect, never NM | n/a | `implausible:...` 204 |
| insider_ownership, mutual_fund_ownership | Z, OPEN | no Form 4 / no N-PORT holder in the window -> Z "No insider transactions in 12 months" / "No fund holders reported" [product wording] | filing index for the window | 5/51 blank |
| public_float | SH, OPEN | first 10-K after IPO may state no float as of the prior Q2 end -> SH "Not public at measurement date" (E4 cover-page text) | E4 | 10 blank |
| employee_count(_resolved) | NT until a source decision | not in XBRL face statements for most filers (dei tag optional); source decision needed (doc 44) | n/a | 925 blank |

Data points with **no conditional state** (V or OPEN only): revenue (except PR and bank REP), net_income(_resolved), diluted_eps/basic_eps(_resolved) (loss per share is a value), total_assets(_resolved), total_liabilities(_resolved), stockholders_equity(_resolved) (negative is a value), cash_and_equivalents(_resolved), cfo(_resolved), cash_flow_investing/financing(_resolved), net_change_in_cash, shares_outstanding(_resolved), total_debt_split (OPEN or Z via total_debt), ppe_net(_resolved) (NP only for asset-light filers without a PP&E line, rare; treat as 2.4 if found), income_before_tax(_resolved), income_tax_expense(_resolved) (a tax benefit is a value), revenue_sanity_resolved, institutional_ownership.

## 4. Propagation rules (dependency graph, PROPOSED)

- P1 (sufficiency first). If one input's legitimate state on its own decides the dependent (rnd_intensity with R&D NP; payout_ratio with DPS Z; P/E with EPS <= 0), the dependent takes that state even if another input is OPEN. The OPEN input is still a defect on its own row.
- P2 (otherwise OPEN wins). If no single legitimate input decides the dependent and any input is OPEN, the dependent is OPEN with a pointer to the leaf (dependency-graph attribution, BRIEF2: fix leaves first). This prevents a legitimate state from hiding a defect.
- P3 (Z in arithmetic). Z enters additive composites as 0 (cash_returned, TSY, net_cash, debt/EBITDA numerator, FCF with capex Z). Z in a numerator gives 0 or "None" (dividend_yield 0% "No dividend"). Z in a denominator gives a stated state (interest coverage "No interest expense"), never a division.
- P4 (NP in arithmetic). NP is never 0 in arithmetic except where section 3 names an [ACCT] option (quick_ratio, goodwill_pct_assets, CCC variant). NP propagates as NP with the input named: "Not applicable: no inventory line".
- P5 (NM). NM propagates as NM to every dependent whose formula uses it as a multiplier or divisor (P/E NM -> PEG NM; EBITDA <= 0 -> all EBITDA multiples NM). A dependent that uses the input additively (EV uses market cap) is unaffected.
- P6 (SH). SH propagates to every dependent that needs the missing base (eps_growth SH -> PEG SH; share count 1y ago SH -> TSY SH).
- P7 (PR). PR applies to the revenue-denominated set only; it does not propagate to EPS, cash or balance-sheet rows.
- P8 (NT). A template removal removes the dependent too; a removed input in a kept metric means the template is inconsistent and must be fixed, not displayed.
- P9 (precedence for the displayed reason when several legitimate states apply): NT > PR > NP > Z > SH > NM. Example: a pre-revenue biotech with no R&D line shows PR on rnd_intensity, not NP.
- P10 (same period). Every input of one cell comes from one period and one restatement basis (ledger LLY 8-K recast, MSFT 2016). A dependent assembled from inputs' own "latest" periods (CCC today, PEG today) is OPEN until aligned.

Worked cases: rnd_intensity with no R&D line -> NP (P1); CCC with no inventory -> NP or the approved variant (P4, [ACCT]); payout ratio for a non-payer -> "No dividend" 0% (P3), for a loss-maker payer -> NM (P5); PEG with non-positive growth -> NM, with negative P/E -> NM (P5); 10y CAGR for a company whose first XBRL FY is FY2020 -> SH "History shorter than 10 years: first reported fiscal year FY2020" (P6); TSY with a dividend OPEN -> OPEN (P2, replaces the $0 default).

## 5. Coverage accounting (PROPOSED)
- Covered = V + Z + NM + SH + NP + PR, each only with its stored evidence; OPEN never; NT is outside the denominator by audited group membership.
- Report coverage three ways so nothing hides: (1) values only (V/(template cells)), (2) resolved (all covered states), (3) open defects by root-cause leaf. A rise in (2) without (1) must be visible.
- A class may count as covered only after its detector passes an audit: 30 cells per class per group opened against the filing, zero wrong states (R4 control c). Until then the state may be shown with "(provisional)" internally, and counts as OPEN.
- Per-class audit targets for the cohort: Z dividends (start with the 253 companies blank on both dividends_paid and DPS), NP R&D (500), NP inventory (359), SH (961 plausible), NM growth (every M1-G cell, after F1 is fixed).

## 6. Metrics to remove from a group's template (definition meaningless for the group, PROPOSED)
| Group | Remove (NT) | Why |
|---|---|---|
| All groups | the 29 `*_resolved` duplicates as separate template cells (keep one displayed cell per concept, the resolved one) | 163 counts each concept twice for 29 concepts; a template cell must be one economic line |
| Corporate (non-lessor, non-BDC) | bdc_total_investment_income, net_lease_revenue (keep for lessors where presented), collaborative_arrangement_revenue (a component line, not a template cell; show in statements only where presented) | sector-only rows counted against everyone: 957, 861, 982 cohort blanks (doc 44) |
| Corporate | net_interest_income under that name | it is a bank concept; for corporates rename "net interest income (expense), non-operating" or drop (data-team/30); 892 blanks |
| All groups until a source decision | employee_count | not an XBRL face line for most filers (925 blanks) |
| Bank / thrift | as `sector_applicability.BANK_SUPPRESSED_METRICS` "not applicable" list (gross/operating margin, ROIC, interest coverage, EBITDA family, FCF family incl. fcf_gt_net_income, net cash, D/E, zero_debt, EV/sales, current/quick/working capital, days metrics, CCC, Piotroski, dividends_pct_fcf, share_repurchases_pct_fcf, OCF/NI) plus rnd_intensity, sga_pct_revenue, margin_expanding_3yr, goodwill_pct_assets optional, reconciliation gaps | meaningless by definition for deposit funding and unclassified balance sheets (data-team/30, 32) |
| Insurer | gross margin, days metrics, CCC, current/quick/working capital, Piotroski, rnd_intensity, margin_expanding_3yr, EBITDA family, interest coverage, ROIC, sga_pct_revenue, FCF family | float-driven cash flow, no classified BS (data-team/30) |
| Equity REIT | days metrics, CCC, R&D rows, Piotroski, margin_expanding_3yr, current/quick/working capital, gross margin, FCF family, sga_pct_revenue (swap to G&A % revenue) | unclassified BS, no COGS, capex not separable (data-team/30) |
| Mortgage REIT, BDC/fund | as equity REIT plus EBITDA family, interest coverage, ROIC, operating margin | interest is the business (data-team/41) |
| Pre-revenue overlay (years in overlay) | all PR rows: gross/operating/net/pretax/EBITDA/FCF margins, rnd_intensity, sga/capex/sbc % revenue, P/S, EV/S, revenue growth family, debtor days, CCC, margin_expanding_3yr | revenue-denominated; shown as PR (state), not removed, because the company leaves the overlay; Sector Analyst decides display vs removal |
| Non-screener (SPAC, trusts, ABS) | all | data-team/41 |

## 7. Items that need the named accountant [ACCT]
1. Growth across a sign change: NM with a direction word, or a different measure (absolute change) (M1-G).
2. Period basis for PEG (TTM P/E with which growth) and for payout ratio (FY vs TTM; DPS declared vs paid).
3. Interest coverage with an operating loss: NM or a negative value.
4. ROIC when income before tax <= 0 (tax-rate term), and ROIC/ROE on average vs ending equity.
5. Quick ratio with no inventory line: treat as 0 or NP.
6. Cash conversion cycle without inventory: approve a differently named "DSO - DPO" variant or NP.
7. Goodwill % assets with no goodwill line: 0% or NP.
8. Borrowings with no line and no note (ATEX): Z or "not reported" (data-team/27 D3 E3), and the finance-lease perimeter for Z-debt.
9. Dividend suspended / initiated wording and the -100% value for a suspended dividend.
10. MLP and LLC distributions counted as dividends to common holders.
11. Comprehensive income where no OCI statement is presented.
12. Amortization of intangibles Z when no finite-lived intangibles exist.
13. Restatement basis for growth endpoints (as-originally-reported vs restated).
Product (founder), not accounting: history-gate use of pre-2015 base periods (2.3); streak wording ">= N years"; UI wording in general.

## 8. Defects routed (not proposals: wrong values or wrong reasons on display today)
| ID | Defect | Owner | Next step |
|---|---|---|---|
| D-S3-1 | F1 growth over negative base published (YoY sign inversion, both-negative CAGR) | Data Engineer (mapper `ttm._growth_value`, `fcf_growth.py` reuses it) | dry-run: count rows that would flip to NM; Verifier checks RDDT, Ford, TAP, AIG |
| D-S3-2 | F2 negative-denominator P/E, payout, PEG, ROE on negative equity, P/B, D/E, EV/EBITDA, debt/EBITDA, OCF/NI published as values | Data Engineer (`price_metrics.py`, `expanded_metrics.py`, `calculate_shapes/ratio.py`) | dry-run per metric after the accountant answers item 3 |
| D-S3-3 | F3 TSY counts unmapped dividends as $0 (PFE -0.25%); `PaymentsOfOrdinaryDividends` unmapped for dividends_paid | Tag Mapper (coexistence check; its definition includes preferred and NCI dividends, so a perimeter check is needed) and Data Engineer (remove the $0 default unless Z) | Tag Mapper full-population coexistence for `PaymentsOfOrdinaryDividends` vs `PaymentsOfDividends`/`...CommonStock` |
| D-S3-4 | F4 SIC-based "pre-revenue" reason shown on 44 revenue-reporting pharma companies | Lane B (`coverage_matrix.SIC_GAP_REASONS`) | replace the SIC rule by 2.5 evidence; until then show the A1/OPEN reason |
| D-S3-5 | F5 786 history blanks are period/mapping gaps, not history | Period Engineer | split `missing:prior_period` by first-period evidence (2.3) in the coverage build |

## 9. Commands actually run (all read-only; pooler 17 of 60 at start, one connection, statement_timeout 60s)
- Python over `cohort_cells.csv` / `group_assignment_draft.csv`: blanks and reasons per data point; class split (E1 323, M1 1,468, H1-candidate 2,916, A1 2,314, A1 combined 178; my bucket rules, DATA-INFERRED).
- Q1: latest `metric_value` per (company, metric) for 20 sign-sensitive metrics over the 986 cohort ids: valued vs negative counts (section 0 F2).
- Q2: FY `canonical_fact` for net_income, diluted_eps, stockholders_equity, dividends_per_share, dividends_paid, share_buybacks over the cohort (72,013 rows) -> replica of `_growth_value` (F1). A first attempt joining in SQL hit the 60s timeout and was abandoned.
- Q3: stored growth, PEG, P/E, ROE, payout rows for companies 10 (RDDT), 114 (AIG), 301 (TAP), 417 (F).
- Q4: `company_sec_tag` dividend/distribution tags for the 280 cohort companies with blank dividends_paid; `concept_mapping` for dividends, buybacks, R&D, inventory; JNJ/PFE/CL dividend tags; stored TSY/yield rows for JNJ, PFE, CL.
- Q5: `company_filing_line_evidence` present/absent counts for the cohort (9 data points); `data_point_registry` gated populations; first 10-K/10-Q filing date for 585 companies with history blanks (F5).
- SEC (declared User-Agent, under 1 request/second, 7 requests, about 2 MB, deleted after): RDDT 0001713445-26-000022 index, FilingSummary, R5, R8; PFE 0000078003-26-000095 FilingSummary, R8.

## 10. Untested scope and what would change this
- NOT_RUN: no state rule implemented or dry-run; no audit of the NP detector, the Z dividend evidence, or SH first-period evidence; no accountant review; F2 not split per company into "valid negative" vs "denominator negative" beyond the code rule; F1 counts are my replica of the engine on `canonical_fact`, checked against stored values for 4 companies only.
- Ford FY2025 and FY2020 net income values were not opened in the filing (DATA-INFERRED); RDDT and PFE inputs were.
- F5 does not see predecessor CIKs or S-1 comparatives, so some "H1 plausible" cells are actually fillable and some "filed during base year" cells may be fiscal-year changes.
- What would change my mind: if the accountant prefers showing negative P/E, coverage and payout as values (some vendors do), F2 becomes a wording change, not a defect; if a full-population coexistence check shows `PaymentsOfOrdinaryDividends` usually includes material preferred/NCI dividends, it cannot fill common dividends_paid directly and the Z evidence for non-payers must rely on the face-row rule alone.

## 11. Exact next actions
1. Verifier: review sections 0 and 2 independently, starting with RDDT R8/R5 and PFE R8, then a 20-cell sample of F1 and F2.
2. Founder: name the accountant for section 7; decide the history-gate question in 2.3.
3. Data Engineer: dry-run D-S3-1 and D-S3-3 (TSY default) as proposed-writes tables; no live change before review.
4. Tag Mapper: coexistence check for `PaymentsOfOrdinaryDividends` (and the MLP distribution tags) against the dividends_paid perimeter.
5. Lane B: retire the SIC pre-revenue reason (D-S3-4); extend `company_filing_line_evidence` to cash-flow rows (dividends, repurchases, capex, working-capital changes) so Z and NP evidence exist for those rows.
