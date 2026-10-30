# S5. D1 (TTM input missing) and H1 (history too short): fixable vs legitimate (Period Engineer, 2026-10-22)

Status: PARTIAL. All 4,086 D1 cells and all 2,839 H1 cells in the 986-company cohort are classified from live tables. 30 companies were sampled at raw-fact level. 6 cases were opened at SEC. Read-only: no code, migration or table was changed. Cohort and cells come from `data-team/strategy/data/cohort_cells.csv` (BRIEF2). Live DB reads ran 2026-10-21/22 with one connection at a time, `statement_timeout` 60 s, chunked by company id (pooler at 16-18 of 60).

Evidence labels: FILING-CHECKED means an SEC document was opened (accession and locator given). DATA-INFERRED means the conclusion comes from our tables (`core.fact`, `analytics.canonical_fact`, `metric_value`, `core.filing`) plus code reading. ASSUMED is stated as such. Only FILING-CHECKED evidence can make a blank "structural". Every LEGIT row below is still a proposal until it has that evidence.

## 0. Wrong values found while doing this (route first; zero tolerance)
| # | Defect | Scope (cohort) | Evidence |
|---|---|---|---|
| W1 | `expanded_metrics._ebitda_ttm` and `_fcf_ttm` sum the 4 most recent **non-null** quarterly rows. There is no check that the quarters are consecutive, so a null quarter is skipped and an older one is pulled in. MasTec "TTM EBITDA" 1,019.3M = Q2'26 349.8 + Q1'26 263.7 + Q2'25 260.7 + Q1'25 145.1 (Q3/Q4'25 are null: `incomplete:add`). PepsiCo uses Q3, Q2, Q1'26 + Q1'25. The reason code `missing:4_consecutive_quarters` claims a check the code does not make | EBITDA: 47 companies, 159 displayed cells (ebitda, ev_ebitda, ebitda_margin, debt_to_ebitda, net_debt_ebitda). FCF: 62 companies, 99 displayed cells (fcf_per_share, share_repurchases_pct_fcf, dividends_pct_fcf) | code `pipeline/src/scrooner_pipeline/mapper/expanded_metrics.py` lines 145-206; `metric_value` rows for company 225. DATA-INFERRED (arithmetic exact) |
| W2 | buybacks, dividends_paid and revenue TTMs in `expanded_metrics` are anchored on each concept's own latest quarter, with no staleness guard. American Airlines `buyback_yield` 0.23% is built from FY2021 quarters. Air Products `buyback_yield` = 0 is built from FY2014 quarters, which is before the 2015 history gate | buyback_yield anchor more than 2 quarters behind the company's current quarter: 81 companies; share_repurchases_pct_fcf: 61; dividends_pct_fcf: 30 | `canonical_fact` concept 60 for companies 123 and 89; `metric_value` 2026-10-18. DATA-INFERRED |
| W3 | Essential Utilities (WTRG) 8-K 0001193125-26-124163 furnishes **American Water's** statements (merger, Item 7.01/9.01, Ex. 99.1), XBRL-tagged under WTRG's CIK. Our WTRG FY2023-25 CFO (1,874/2,045/2,059M) and capex (2,575/2,856/3,126M) are American Water's figures. The derived WTRG Q4 CFO (e.g. 1,254.7M for Q4'25) subtracts WTRG's own 9M from American Water's FY | 21 WTRG canonical rows. Cohort-wide, 229 canonical rows on 8 concepts since 2023 come from non-periodic forms: 65 8-K, 105 DEF 14A (net income; the ledger rule already bans these), 37 20-F, 6 40-F, 6 DEFR14A | FILING-CHECKED: R1 (cover WTRG), R7 (CFO 2,059 / capex 3,126 FY2025), 8-K body text naming American Water |
| W4 | Honeywell Q4 2025 capex is stored as **58M** (derived). It is the recast continuing-ops FY 986M minus the original pre-spin 9M 928M: a mixed-vintage subtraction (R5 rule B1) | 1 cell found here. The class is general wherever discontinued operations appear (R5 section 6) | FILING-CHECKED: HON 10-K 0000773840-26-000013 R7 (continuing-ops capex 986M, discontinued-ops cash flows on separate lines). 9M from 10-Q 0000773840-25-000105 |
| W5 | Fiscal labels in `core.period` are broken for 24 cohort companies (ADP labels calendar quarters as Q1/Q2 of the wrong fiscal year; TXT's Q4 ending 2026-01-03 is labelled FY2026 Q4). The TTM and growth code keys on (fiscal_year, fiscal_period), so these companies get blanks or can be summed over the wrong window | 24 companies: ADP, NUE, PG, SWK, TXT, ONTO, MU, CGNX, LSCC, TRMB, CAKE, DAR, EXEL, WAT, SLAB, NI, TTMI, TLN, GEV, FERG, QXO, LDOS, AMCR, TEL. 173 D1 cells | `canonical_fact` + `core.period` for companies 171 and 1171. DATA-INFERRED |

## 1. D1: 4,086 blanks `missing:*_ttm`
Method. For each blank, find the root input concept(s): ebitda = operating_income_resolved + D&A_resolved; fcf = cfo - capex; and the 7 direct TTM concepts. Then test the trailing 4 quarters that end at the company's current quarter, which is the latest revenue or net-income quarter. Each missing quarter is classified as: derivable (Q4 = FY - 9M, Qn = YTD - prior YTD, or the chain cumulative - discrete quarters; inputs authoritative or conflict-filled), reachable by the YTD route (latest YTD + prior FY - prior YTD, same tag), absent, absent but zero-by-comparative, or blocked as per-share. Raw `core.fact` candidate tags were checked for every input that had no canonical fact (653 companies). Ingestion was checked against `core.filing` (filings after the current quarter and their fact counts). Scripts: scratchpad `s5/d1b.py`. DATA-INFERRED throughout, plus the filing checks cited.

| Class | Cells | Verdict | Owner / fix |
|---|---|---|---|
| Non-payer / no buyback: no fact for the concept or its counterpart (DPS vs dividends paid) since 2024, and no raw candidate tag | 811 | **LIKELY LEGITIMATE**. Show "None reported" only with E1 evidence: the face line is absent from the latest 10-K/10-Q (`company_filing_line_evidence`). Until then it is OPEN | Data Engineer (E1 evidence); Verifier sample |
| Financials template (bank, insurer, BDC, other financial): EBITDA/FCF/capex | 630 | **LEGITIMATE by template**. ASSUMED convention, pending Sector Analyst approval; show "Not meaningful for banks/insurers" | Sector Analyst |
| Vocabulary / composition: the line is filed under tags we do not read. D&A as `Depreciation` + `AmortizationOfIntangibleAssets` (MSFT, GOOG, ABT, AMD, INTC, SWKS, SPGI), REIT capex (`PaymentsForCapitalImprovements`, `PaymentsToAcquireRealEstate`, `PaymentsToDevelopRealEstateAssets`), dividends seen only on the other side | 710 | **FIXABLE** (composition, per R3 slots; perimeter decision needed: MSFT's CF line "Depreciation, amortization, and other" exceeds Depreciation + Amortization) | Tag Mapper -> Standardization Lead |
| Missing quarter, mixed causes | 352 | **MOSTLY FIXABLE**. Zero-by-absence (filer omits the line in a year with no activity, and later comparatives show 0; CMI is FILING-CHECKED, see section 3): 75 cells. Recast-basis conflicts (HON). 10-K not ingested (CLX FY2026 10-K has 0 facts). Remainder OPEN | Period Engineer + Data Engineer |
| Latest 10-Q/10-K is indexed but has **0 facts** (ABT, KO, F, GD, HUBB, HUM, OMC, FRT...) | 348 | **FIXABLE** (ingestion) | Data Engineer (the 89 zero-fact filings in doc 44) |
| EBITDA where the company has no operating-income line (NKE, JNJ, IBM, GE, BMY, CLX, BALL, ADP, XOM) | 314 | **FIXABLE by definition**: "EBITDA = pretax + interest expense + D&A", labelled. Not legitimate: these companies have EBITDA | Standardization Lead + accountant |
| Upstream income-statement quarter gap: 12/12/12/16 calendars (COST, KR, ACI), successor CIK (XOM, PSKY), ingestion | 181 | **FIXABLE** (calendar-aware windows, R5 B3; predecessor links) | Period Engineer; Company Master |
| No candidate tag found (GATX, NEE, ELS, DTE, PSX capex; MATX D&A) | 181 | **OPEN**: needs custom/extension tags (FSDS) or the rendered statement | Tag Mapper |
| Input reported annually only (BAX capex, SPGI D&A, BF-A DPS) | 147 | TTM is legitimately unavailable at Q1-Q3 anchors **if** the quarterly line is truly absent. Show the latest FY labelled "FY2025", not as TTM. Some of these are vocabulary cases (SPGI files the components quarterly) | Product display rule + Tag Mapper |
| Fiscal-label defect (W5) | 101 | **FIXABLE** (`core.period` labelling / date-based windows) | Period Engineer |
| YTD route available but not wired: `price_metrics`/`expanded_metrics` import a `_ttm_sum` without the `ttm.py` YTD fallback | 97 | **FIXABLE** (code, additive class A/B only) | Period Engineer |
| Derivable now under the R5 allowlist, inputs authoritative (APD, ADP, PEP, BDX, AZO) | 85 | **FIXABLE** (derive; Verifier sample first) | Period Engineer |
| Per-share quarter missing (DPS 80, EPS 1) | 81 | **BLOCKED** by R5 class D. Fixable only with filed values or an approved DPS rule (section 3) | Standardization Lead |
| Latest periodic filing not indexed in `core.filing` (DG, HPQ, DE, SJM, BURL, JKHY) | 44 | **FIXABLE** (collector/index) | Data Engineer |
| Other | 4 | OPEN | |

Totals: **FIXABLE about 2,480 cells (61%)**: vocabulary 710, ingestion 392, EBITDA definition 314, upstream 181, labels 101, YTD route 97, derive 85, plus most of the 352. **Likely legitimate 1,441 (35%)**: no activity 811 and template 630, both still needing evidence. **Display rule 147 / blocked 81 / open about 185.**
Share fixable by the R5 section 6 derivation allowlist alone (derive + YTD route + calendar/label windows + zero-by-absence): **about 360 cells (9%)**. The allowlist is not the main lever for D1. Vocabulary, ingestion and the EBITDA definition are 1,416 cells.

By data point: ebitda_ttm 1,641 (427 companies: 119 template, 100 D&A vocabulary, 82 no operating income line, 59 ingestion/labels, 26 missing quarter, 17 annual-only, 15 open, 7 upstream, 2 derive). fcf_ttm 602 (263 companies: 68 ingestion/labels, 50 template, 56 capex vocabulary, 32 open). dividends_per_share_ttm 453 (303 non-payer, 80 per-share blocked, 30 dividends paid but no DPS tag). dividends_paid_ttm 378 (258 non-payer). share_buybacks_ttm 582 cells / 291 companies (105 none, 75 missing quarter of which about 34 zero-by-absence, 38 YTD route, 30 vocabulary). capex_ttm 180, revenue_ttm 139, cfo_ttm 75, diluted_eps_ttm 36.

## 2. Stratified sample, 30 companies (raw `core.fact` read per missing window; scratchpad `s5/samp_report.txt`)
| Company | D1 root | Verdict | Evidence |
|---|---|---|---|
| MSFT, GOOG, ABT, AMD, INTC, SWKS, IBM | D&A only as Depreciation + AmortizationOfIntangibleAssets (authoritative, discrete and YTD) | FIXABLE composition (MSFT notes are $0.1B-rounded: use CF face) | DATA-INFERRED |
| SPGI | D&A tag FY only | FIXABLE composition, not annual-only | DATA-INFERRED |
| KO, ABT | Q2-2026 10-Q indexed with 0 facts (0001628280-26-050503, -050134) | FIXABLE ingestion | `core.filing` + fact count |
| DG | Q2-2026 10-Q not in `core.filing` | FIXABLE ingestion | DATA-INFERRED |
| CLX | FY2026 10-K 0000021076-26-000034 has 0 facts; no operating income line | FIXABLE ingestion + EBITDA definition | DATA-INFERRED |
| NKE, JNJ, BALL, IBM | no OperatingIncomeLoss in any recent filing | FIXABLE by definition | DATA-INFERRED |
| JPM | EBITDA/FCF/capex | LEGIT template (proposed) | ASSUMED convention |
| COST | 16-week Q4 outside the derivation band | FIXABLE calendar (R5 B3) | R5 FILING-CHECKED period |
| XOM | new CIK 0002115436 (8-K12B 2026-07-01, 0001193125-26-291990); old CIK 0000034088 is **not in `core.company`** | FIXABLE predecessor link | FILING-CHECKED (EDGAR submissions index, form 8-K12B) |
| CMI | buybacks: no repurchase line in FY2023-25; 2026 10-Qs show 2025 comparatives = 0 | FIXABLE zero-by-absence: TTM = 0 + 0 + 243 + 225 = 468M | FILING-CHECKED: 10-K 0000026172-26-000009 R6 financing section has no repurchase row |
| RDDT | same pattern (repurchases start 2026, 2025 comparatives 0) | FIXABLE zero-by-absence | DATA-INFERRED |
| GOOG buybacks | Q3'25 via chain (9M - Q1 - Q2); 6M'25 conflict 28,706 vs 28,306. 6M'26 repurchases really are 0 | FIXABLE derive | FILING-CHECKED: 10-Q 0001652044-26-000071 R9 "Repurchases of stock 0 (28,306)" |
| HON | Solstice spin: original vs recast quarters conflict | FIXABLE after same-vintage pairing; current Q4 capex is wrong (W4) | FILING-CHECKED R7 |
| PEP, APD, ADP | derivable, authoritative inputs | FIXABLE derive | DATA-INFERRED |
| SWKS, CW | YTD route available | FIXABLE code wiring | DATA-INFERRED |
| CAT | DPS declared lumpily (Q2 2.92 on both 3M and 6M contexts, Q3 0.00, Q4 3.02, FY 5.94) | BLOCKED per-share; also shows that the "equal 3M and YTD = rate" guard (ledger 2026-10-21, V/NVDA) misfires on genuine double declarations | DATA-INFERRED (internally consistent) |
| LNG | DPS tagged in 1 of the last 5 quarters | OPEN (custom/dimension tag?) | DATA-INFERRED |
| BA | DPS missing, dividends paid present | FIXABLE vocabulary | DATA-INFERRED |
| AMD | no dividend facts or tags | LIKELY LEGIT non-payer | DATA-INFERRED |
| INTC | no DPS in the window (dividend suspended 2024) | LIKELY LEGIT, needs E1 | DATA-INFERRED |
| FRT | REIT capex tags; dividends paid on the other side | FIXABLE vocabulary | DATA-INFERRED |
| BAX | capex and buybacks FY only | display rule (FY labelled) unless the 10-Q line exists | DATA-INFERRED |
| MATX | capex Q2'26 absent; D&A no tag | OPEN | DATA-INFERRED |
| TXT | label defect W5 | FIXABLE | DATA-INFERRED |

## 3. Rules this adds to R5 section 6 (proposals for the Standardization Lead and an accountant; not approved)
- B8 consecutiveness: a TTM is 4 quarters with contiguous dates ending at the company's current quarter (date-based, not label-based), or the R5/ttm.py YTD route. Never "4 latest non-null" (W1).
- B9 currency: every TTM anchors on the company's current quarter, the latest filed 10-Q/10-K period. A concept whose latest fact is older gets a blank with reason "no value in last 12 months", never an old TTM (W2).
- B10 zero-by-absence (optional flows: buybacks, dividends paid, capex). A missing quarter counts as 0 only when (a) the filed statement for that period has no such row (rendered statement or `company_filing_line_evidence`), and (b) a later filing reports that period's comparative as 0 or omits it. Cohort screen: 75 cells.
- B11 form gate: periodic forms only (10-K, 10-Q, their amendments, 10-KT) feed `canonical_fact` and derivations (W3). Ledger rule exists for DEF 14A; extend it to 8-K, 20-F and 40-F.
- DPS: "declared" DPS is additive across periods in principle, but tagging is noisy both ways (V/LEA put the rate on the FY context; CAT shows a real double declaration). Proposal: dividend yield on the cash basis (dividends paid TTM / shares) as the fallback, labelled. Keep DPS derivation blocked.

## 4. H1: 2,839 blanks
### 4a. `missing:prior_period(...)` 1,879 (builds on S3 F5: 786 "filed during base year")
Method: for each blank, find the base period end from the company's own calendar. Compare it with the earliest `core.fact` period end (core concepts, all years) and the first 10-K/10-Q. Pull raw facts for the concept's mapped tags at the base period, at any authority. Check SEC submissions for the 198 companies that have no data before the base: 8-K12B/G3 (successor), 10-12B/G (spin-off), S-1/424B4 (IPO). Scripts: `s5/h1.py`.

| Class | Cells | Companies | Verdict |
|---|---|---|---|
| (a) First XBRL fact after the base period, IPO (S-1/424B4) | 530 | 128 | **LEGITIMATE horizon** (DATA-INFERRED; S-1 comparatives not checked) |
| (a) Spin-off registered via 10-12B/G | 168 | 34 | **LEGITIMATE horizon** for this CIK (the parent's history is not the spin's) |
| (a) Other / older registrants with no data before the base | 149 | 50 | Probably legitimate; OPEN until the earliest filing is opened |
| (c) Successor issuer, 8-K12B/G3 (XOM, PSKY, FERG, LIN, BKR, EVRG, OVV, APA, APO, DINO, BG, VNOM, KKR, DRS, PRMB, SMMT, EAI) | 96 | 22 | **FIXABLE by a predecessor link**: holding-company reorganizations (XOM, KKR) join cleanly; merger successors (LIN, BKR) need an accounting-predecessor decision |
| (c) R5 predecessor candidates (MRVL, DIS, STE, BLK, DKNG, NE, PNFP, ...) | 74 | 10 | FIXABLE if filing-checked |
| (b) FY base exists, quarterly base absent (the latest row is a single quarter: Q2'26 vs Q2'16) | 330 | 234 | **FIXABLE by method**: compute CAGRs on FY or TTM endpoints |
| (b) Base fact present but non-authoritative (conflict: restatement, split basis e.g. GOOG 2021 EPS 27.26 pre-split vs 1.36 post-split, recasts) | 269 | 213 | FIXABLE after basis/split resolution |
| (b) No mapped tag at base (era vocabulary per R5 section 3; BDC EPS; DPS before dividend initiation, which is legitimate) | 152 | 99 | Mixed: vocabulary is FIXABLE; dividend initiation is LEGIT with evidence |
| (b) Authoritative raw fact present but not in canonical (mostly W5 labels, e.g. ADP) | 35 | 14 | FIXABLE |
| (b) Quarter not derived, cumulative exists | 33 | 22 | FIXABLE derive |
| Calendar unknown | 43 | 17 | OPEN |
Totals: legitimate horizon **698** (plus up to 149 probable); fixable **989** (predecessor 170 + filed-during-base 819); open 192. This matches S3 (786 filed during base, about 961 plausible horizon); the difference is that I move 170 successor/predecessor cells out of "horizon".

### 4b. `missing:fewer_than_3_years_gross_margin` 530 + `non_consecutive_years` 3: **not history**
- 470: no gross profit in canonical in any year (banks, insurers, REITs and utilities about 250; corporates 220 incl. GOOG, MATX, AAL that present cost of revenue but no GP line). This is template / derived-GP (revenue - cost of revenue), not a horizon problem.
- 51: GP quarters exist but no FY GP (ABT, CAT, GE, GIS): FIXABLE (the FY GP is unresolved or the job reads `gross_profit`, not `gross_profit_resolved`; not verified).
- 5: real short history (ATO, RKT, RBA, INSM, FPS). 4: GP years fewer than revenue years (vocabulary/era).
- 3: non-consecutive: OPEN.

### 4c. `missing:4_consecutive_quarters` 427 (ebitda TTM): same root as D1 ebitda, not history
Company split: 119 template, 100 D&A vocabulary, 82 no operating income line, 59 ingestion/labels, 26 missing quarter, 17 annual-only, 15 open, 7 upstream, 2 derive. The reason string should become specific to the root.

**H1 overall: about 703 cells are real history horizon (25% of 2,839).** The rest is period/derivation/basis (about 1,000), template or definition (about 900, mislabelled as history), predecessor (170), and open.

## 5. Display rule for horizons (proposal; wording is a product call)
1. CAGR endpoints are FY or TTM values, never a single quarter. A quarterly row may show YoY only.
2. N-year CAGR requires an FY base N years before the latest FY. If the company's first certified FY is later: show the longest available CAGR, labelled, e.g. a 6-year-old filer shows "10y CAGR: n/a, history from FY2020 (IPO 2020)" plus "5y CAGR x%". Never extrapolate and never relabel a 5y figure as 10y.
3. Successor CIKs show "History before 2026-07 under predecessor (Exxon Mobil Corp)" until the link is filed and verified. After that, history joins with a visible boundary.
4. Spin-offs: "Independent since <date>; earlier figures are carve-out estimates" only where Form 10 XBRL exists. Otherwise the history starts at the spin.
5. Base before 2015-01-01 (doc 38): blank with "Base year before 2015 not used" (S3 2.3; founder decision).
6. Legitimate absences (no dividend, no buybacks) display as "None reported" only with E1 evidence. Otherwise "Not available: <reason>".

## 6. 25 most affected companies (D1 + H1 blanks)
EAI 28 (horizon, IS gap), JHX 28 (FY base exists, IS gap), PNFP 27 (predecessor), INIO 27 (horizon), XOM 27 (successor CIK), PSKY 26 (successor), FDXF 26 (spin, IS gap), CBC 25, AMRZ 24 (spin), Q 24, SOLS 24 (spin), SUNB 24, HONA 24 (spin), IREN 23, SN 23, FERG 23 (labels + successor), JAN 23, ADP 22 (labels, definition, derive), PS 22, PACS 21, VNOM 21 (successor), ARXS 20, NUE 19 (labels), CNH 19, NE 19 (predecessor). 18 of the 25 are new CIKs (IPO, spin or successor). Their D1 blanks are mostly "upstream IS gap": fewer than 4 quarters exist under the new CIK, so for spins and IPOs these are legitimate until 4 quarters are filed.

## 7. Commands actually run
- Reads: data-team 20, 21, 22, 14; strategy BRIEF, BRIEF2, R5, 44, S3; code `mapper/expanded_metrics.py`, `price_metrics.py`, `ttm.py`, `quality_flags.py`, `coverage_matrix.py` (grep).
- psql (read-only, `statement_timeout` 60 s, chunks of 40-100 company ids): `canonical_fact` for 10 concepts since 2021 (292,810 rows); `metric_value` ebitda/fcf since 2023; raw `core.fact` candidate tags for 653 companies; `core.filing` recent periodic filings with fact counts; H1 canonical (293,067 rows) and raw facts 2013-2024 (806,514 rows); non-periodic source forms; single-company checks (225, 89, 123, 215, 1031, 5351, 1436).
- SEC (declared User-Agent, at most 2 requests/s, under 5 MB total): WTRG 8-K 0001193125-26-124163 index, R1, R7, 8-K body; CMI 10-K R6; HON 10-K R7; GOOG 10-Q R9; submissions JSON for 0002115436 and the 198 horizon CIKs.
- Scratchpad: `/private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/s5/` (`d1b.py`, `h1.py`, outputs).

## 8. Not verified / risks
- The template, no-activity and horizon verdicts have no rendered-statement evidence; they stay proposals.
- The derivability test uses `canonical_fact` and a 5-day date tolerance. The authority flag of the inputs comes from source facts (conflict-filled inputs were counted as not clean).
- Raw candidate-tag regexes can catch components (e.g. `PaymentsOfDividendsMinorityInterest`). "FIX_VOCAB" means "a lead exists", not "a mapping is safe" (coexistence check required).
- S-1/Form 10 XBRL comparatives were not checked; some IPO/spin horizon cells may be fillable.
- Cell counts include cascades: one root fixes up to 4-5 cells.

## 9. Next actions
1. Data Engineer: W3 form gate; re-ingest the 0-fact filings (348 D1 cells); index missing filings (DG, HPQ, DE...).
2. Period Engineer (code, dry-run first): W1 consecutiveness, W2 anchoring, wire the YTD route, date-based windows (W5 + B3), then a derivation dry-run for the 85 + 97 cells. Verifier samples MasTec, PEP, AAL, HON.
3. Company Master: predecessor links for the 22 successor CIKs (XOM first: old CIK 0000034088 is absent from `core.company`).
4. Standardization Lead: EBITDA-without-operating-income definition (314 cells); D&A/capex composition (710); DPS policy.
5. Coverage build: relabel `fewer_than_3_years_gross_margin` (template) and `4_consecutive_quarters` (root-specific) so they stop being counted as history.
