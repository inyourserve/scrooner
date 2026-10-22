# 40. Solution: tag non-uniformity, coverage and data quality at scale (Ritwik, Head of Data Product, 2026-10-21)

Status: v1 synthesis of six specialist reports (R1 triage, R2 tag expert, R3 standardization lead, R4 sector analyst, R6 data engineer, R7 verifier) in `data-team/strategy/team/`. R5 (period/history) and the Data Chief challenge (R8) have since reported; their effect is in the v2 AMENDMENTS block below, which overrides conflicting text. Every definition here is a proposal: no accounting definition is approved, no database write was made, no database count was measured (the shared pooler stayed above the 14-connection limit for every agent; see Risk 1). Labels: FILING-CHECKED / DATA-INFERRED / ASSUMED.

## v2 AMENDMENTS (after Data Chief challenge R8 and period report R5). Where this block conflicts with sections below, THIS BLOCK WINS.
1. **Withdrawn: "keep max-of-two D&A out of ratios."** Code-read by the Chief: `ebitda` reads `depreciation_and_amortization_resolved`, which takes the LARGER of the two tags, so at Kura and Starbucks ratios already use the right (cash-flow) total. My fix would have made ratios worse. The base-concept display path is unverified; replace with a read-only count of stored D&A vs D&D&A disagreements and which one `_resolved` picks. Also: R7's "115 of 137 conflicting filings" are filing-periods (130 are 10-Q).
2. **Reclassified to the accountant queue:** "FCF reads `capex_resolved`" (adopts capitalized software as capex, decision C4) and "split lease-inclusive debt roles" (decision C1). Definition-free versions only: suppress FCF with a reason where `capex` and `capex_resolved` differ; store the total-debt path.
3. **Do not rebuild what exists or is held.** W1/W2 are data-team/33 families (B5, Q, H, B1 guards); the staleness guard is already released (commit 9e77357), so the "78% stale" baseline is pre-guard and must be re-measured. Total-debt, Q4-EPS and revenue-total guards are built, filing-checked and HELD under the root-cause gate; releasing them is rank 1, 2, 4 below. The identity suite is data-team/34 P2 inside `scrooner-certify` (stored side already exists as I1/I2), not a parallel `structure/identities.py`. Extend `company_filing_line_evidence` (migration 0093); do not add `filing_statement_line`.
4. **Targets cut for 30 days:** the 95.5% applicable-denominator fill and the 83% all-cell fill. Policy: never shrink a denominator without filing evidence. Report weekly, on the fixed 986-company / 160,718-cell denominator: value-filled cells, current-and-not-stale cells, FILING-CHECKED wrong values removed. Realistic 30-day gain without a named accountant is about +2-3 points (3,000-5,000 cells, ASSUMED). The "20 points" of population gating is about 20% of blanks (about 4 points of all cells).
5. **Effort claim withdrawn:** R6's 13-16 engineer-days covers fetch, parse, load and identities only; the evidence layer, three templates and the four fixes were never sized.
6. **W3 is independent of OUR mapping, not of the filer's tagging** (same XBRL as companyfacts).
7. **Missing root-cause classes added:** restatement-basis mix (MSFT FY2016-17 growth 0.6845 vs 0.3777), split-table defects (NVDA about 216 cells; 156 candidates), DPS rate stored as FY total (Visa), proxy/8-K lineage and mixed-vintage cells (JPM, LLY), certify's own false positives and misses (data-team/36).
8. **R5 (history) findings now in scope:** (a) for fiscal years ending before 2021-08-09, 75% of top-1000 FY2015 10-Ks that tag FY revenue also file a discrete Q4 in the Item 302(a) note (388 of 515; Q4 diluted EPS 407 of 540), so Q4 for 2015-2020 can be a filed fact and an independent check on derivation; from FY2021 only 9% do (DATA-INFERRED, rule change FILING-CHECKED). (b) Pre-2018 era tags unmapped (SalesRevenueGoodsNet at KO, PFE, JNJ, MRK; 17.3% of FY2015 filers lack a mapped revenue tag vs 2.3% from FY2018). (c) A live era break: `InterestExpense` on the face fell from 571 (2022q1) to 175 (2025q4) top-1000 filers while 363 present `InterestExpenseNonoperating`; neither new tag is confirmed in our mapping (DB not checked). (d) Derivation needs a canonical-concept allowlist and calendar-aware windows (Costco's 24-week YTD is 167 days, outside the fixed 170-200 band).

### Revised 30-day plan (R8, cap 10 families, 50 cases; each: dry-run, reviewed, then a separate first live run)
Step 0 (prerequisite): one measured baseline in a quiet pooler window: apply committed migrations 0096 and 0097 via the Release Manager, run R1's four SQL queries on the 986 cohort, run a `scrooner-certify` dry-run on the top 1,000 (about 1.5 h); Verifier measures certify precision per invariant on 30 flagged cells each. If the measured split moves any bucket by more than a third, re-rank before day 10.
| Rank | Family | First step |
|---|---|---|
| 1 | Total-debt consistency guard (33 D-guard, held) | Release Manager reruns tests on the held diff; cohort dry-run; Verifier reviews 30 hits (LLY, RTX, ABBV, CSCO, MAR) |
| 2 | Per-share integrity: no derived Q4 EPS/DPS; DPS rate-on-YTD guard (held) | Release held Q4 EPS change; certify rate-on-YTD rule (KLAC, V, MSFT, AAPL, WELL) |
| 3 | Source authority and mixed vintage (33 C; 36 I6 split) | Split I6 into lineage vs mixed-vintage; read-only detector for non-periodic-form sources (JPM, MA, LLY, MSFT, MDT) |
| 4 | Revenue total by presentation (doc 37; 33 G) | Ship the disagreement guard; dry-run the per-company rule on all 201 (GE, MA, BLK, EMR, AMT, WMT, ITC, NTAP) |
| 5 | Split table (33 M; 156 candidates) | Dry-run implied splits and 12 duplicates; each new row filing-checked (NVDA, AAPL, BKNG) |
| 6 | Population gating and wrong reasons (33 Q, B5) | Code-read every reason rule and its gate; dry-run against the company's own facts (SCCO, DHR, C, MRK, EPD) |
| 7 | Sector suppression for insurer, REIT, broker/exchange (33 H; R4) | 30-filing zero-false-absent review per family (PGR, TRV, MET, PLD, O, ICE); parallel from day 1, no DB |
| 8 | Interest-expense rule incl. the 2024 `InterestExpenseNonoperating` era break (33 B4 #1) | Full-population coexistence check + 12-case sample; net tags never map (DLH, LOW, SNPS, Agree Realty, AAON) |
| 9 | Per-share date pairing (R1, 2,100-2,800 cells) | Period Engineer writes the pairing rule; 10 filing-checked cases (AAPL, MSFT, JPM, XOM) |
| 10 | Structure pilot, measurement only | Read FSN readme; Range-read one `cal.tsv`; test CVX/XOM/AMD; FSDS reconciliation as 34 P2 inside certify; no new tables |
Deferred past day 30: composition tables and composer (needs named accountant and the K1 test), production structure ingest, migrations 0098-0100, I12/I13, path-B resolver, ingestion fallback reader (detector only now), classifying the 2,000 unknown cells, bank revenue NII + noninterest income, era-scoped tag backfill and Q4-from-note capture (sequence after step 0; owner Period Engineer + Tag Mapper).

### Revised founder decisions
Blocking: (1) accept doc 40 as amended, which releases the held guards (ranks 1, 2, 4); (2) name the accounting reviewer (blocks C1, C4, bank revenue, NI attributable and every composition rebuild; does NOT block ranks 1-10); (3) database capacity: if no quiet window by day 5, the pooler size/plan (founder-only dashboard) blocks step 0. Not blocking: the Range-fetch raw departure (pilot stores nothing), migrations 0098-0100.

### Three ways this fails, with a test (R8)
1. Denominator theatre: test = weekly value-filled and current cells must rise, not only the applicable-denominator figure.
2. Building on projections and an unproven instrument: test = by day 7 step 0 has run and certify precision per invariant is known; else stop new builds and escalate capacity.
3. Infrastructure before visible fixes: test = by day 10 ranks 1, 2, 4 are live and the filing-checked wrong-value list in data-team/36 (JPM 5 cells, Visa FY DPS, NVDA about 216 cells, MSFT growth) is corrected or hidden with a reason.

## 0. One-page answer
**What the problem really is.** "Tags are not uniform" is true, but it is only one of five distinct problems that all look like "a blank or a wrong number." Treating them as one tag-mapping problem is why effort has not moved the needle. Measured split of the ~36,800 blank cells in the top 986 companies (R1, DATA-INFERRED projection, corrected for the coverage over-count; fill is about 77.1%, not the reported 81.4%):

| Cause | Cells | Share | What fixes it |
|---|---|---|---|
| Line does not apply to that kind of company, or no reason recorded | ~20,900 | 57% | Evidence layer + sector templates (no new data) |
| Tag filed but not mapped (vocabulary) | ~4,900 | 13% | Structural candidate generator + tag mapper |
| Period/date alignment (per-share pairing, Q4) | ~3,800 | 10% | Pairing and derivation rules |
| Line composed differently (perimeter) | ~3,700 | 10% | Composition layer |
| Unknown | ~2,000 | 5% | Classify before claiming completeness |
| Ingestion (filing facts missing upstream) | ~1,400 | 4% | Detector + fallback reader |
| Resolver bug producing a blank | ~100 | <1% | Bug fix |

Wrong values are a different population and mostly tag-and-perimeter problems (section 3). Fixing them matters more for trust than the blank fill does.

**The strategy in five workstreams, in order:**
- W1 **Make every blank honest** (denominator + reason). Largest share, no accountant, no data risk.
- W2 **Stop known wrong values at serve time** (guards and four fixes needing no new accounting definition).
- W3 **Build the structure-evidence layer** (statement positions, calculation trees, accounting identities) as an independent second path and wrong-value detector.
- W4 **Build the composition layer** (versioned definitions, per-company perimeter, reported vs standardized value), gated by a named accountant.
- W5 **Fix date alignment and ingestion gaps.**
Expected: top-1000 fill on the applicable denominator from about 88.6% to about 95.5% (R1 upper bound), wrong-value classes closed one family at a time, and every remaining blank carrying a stated reason. Realistic effort: about 13-16 engineer-days to a measured foundation, about 15 more for definitions and perimeters, about 7-10 more after adoption decisions (R6, ASSUMED).

## 1. What changed in my own understanding (so the teams do not repeat it)
1. My first diagnosis (tag name matching is the problem) was incomplete. For revenue, two tags cover 89% of lines and the name path already finds a value for about 97% of filers that have a revenue line (R2, R7).
2. My proof of concept had a bug (rows read in file order, not statement-line order). Corrected: D&A "differences" 61 to 20, capex 29 to 5. Of 90 original differences, 78% were my rule being wrong, 12% were the name path picking the wrong line, 9% were real perimeter differences (R7, 12 of 90 filing-checked). The net-income cross-statement "324/324" is vacuous when both statements use one element (R6). Doc 39 carries the correction.
3. But the composition problem is real, just differently shaped: it shows in specific, checkable defects (section 3) and in the way totals are built, not in a count of position mismatches (R3, R2).

## 2. The five problems, evidence and fix

### P1. Applicability and reason layer (57% of blanks) -> W1
- 20.5% of the (filer x 29 concepts + 17 metrics) cells do not appear on the filer's own statements; about 40% of that is family-structural (a template removes it), about 60% varies by filer inside a family (only per-filing evidence removes it) (R4, DATA-INFERRED, 4,960 filers).
- Bank "revenue" has no total line (Popular R5, FILING-CHECKED); a proposal exists for bank revenue = net interest income + noninterest income (needs accountant). Insurers and REITs still show industrial gross margin, current ratio, FCF yield because suppression code covers banks only (R4, code-read).
- About 20 points of the top-1000 blank rate are population gating, not sector: dividend/buyback rows counted against non-payers, bdc/net-lease rows counted against everyone, PEG on negative growth (R4, R1). That is the cheapest large change.
- Fix: (a) gate sector-only and non-payer rows out of the denominator; (b) per-filing five-state evidence (face with value, face but missing, combined line, note only, not filed) extending `company_filing_line_evidence`; (c) templates for bank, insurer, REIT first, then pre-revenue and BDC/fund (95% of family-structural cells). Only the state "not on face and not filed anywhere" may read "not reported".
- Gate: a 30-filing audit per family with zero false "absent" before the reason is shown.

### P2. Vocabulary misses (13%) -> W3 candidate generator
- Real, filing-checked: NJR/Spire/TVA utility revenue tags, Nikola and Photronics custom tags, DLH `InterestExpenseNonoperating`, Franklin Covey custom D&A total (R7). Custom extension tags are 11.3% of FSDS pre lines (R6).
- Structure alone finds the face figure in these cases; name matching cannot. But label rules are noisy, so structure only proposes; the existing coexistence check and a Verifier sample decide. A custom tag that rolls into a standard anchor via the filer's calculation tree becomes a company-scoped mapping, never global.

### P3. Composition / perimeter (10%, and most wrong values) -> W4
Verified defects (R3 code-read vs FASB 2025 calculation trees; R2/R3/R7 filing-checked):
- **Total debt:** `LongTermDebtAndCapitalLeaseObligations` is treated as another spelling of `LongTermDebtNoncurrent`; FASB says it equals that plus noncurrent finance leases. Finance leases are inside debt at CVX and outside at Walmart (borrowings 46,369 vs 53,127). The computed path is never stored.
- **FCF vs capex:** `fcf`, `fcf_margin`, `fcf_yield` read raw `capex`; the statement row shows `capex_resolved` (adds software). One company-period can show two capex figures today.
- **D&A:** resolver takes the larger of two tags (fitted to yfinance); `DepreciationAndAmortization` ranks above `DepreciationDepletionAndAmortization`, and in FSDS 2025q4 the first-ranked tag is the smaller one in 115 of 137 conflicting filings (Kura Sushi 448K vs true 14,046K, 31x; Starbucks 1,684.7M vs 1,771.5M; both FILING-CHECKED). D&A built from separate lines (AMD 556 + 1,697 = 2,253; Aptiv 585 + 156) is invisible to us.
- **Net income:** one chain mixes parent, consolidated incl. NCI, and available-to-common; 259 filings show `ProfitLoss` with no `NetIncomeLoss`.
- **Revenue:** contract-revenue tag wins over the face total (Walmart 177,769 vs 179,496; ITC 515 vs 454); 201 of 467 top-1000 companies that file both `Revenues` and the contract tag differ by more than 1% in some period (R1, DATA-INFERRED).
- **`CostsAndExpenses`** means four things across 958 filers (opex only at 29, includes interest at 42, equals revenue minus operating income at 651); `Revenues` includes other income at XOM, sales only at COP (R2, FILING-CHECKED examples).
- **Capex** under the standard tag is understated at about 152 filers (Air Lease: 237.7M tag vs 2,348M flight equipment).
Design (R3): each composite concept is a versioned definition of named components marked include / exclude / separate; a per-company-period perimeter record (inside reported line / separate line / not present / inseparable / unknown, with evidence); store both the reported value (face line, company's own label) and a standardized value. Screens and ratios use only standardized values whose components are all known; otherwise a reasoned blank, and the statement tables still show the reported line. Version every standardized value; never overwrite silently (lesson from Compustat re-standardization practice, Lyle-Siano-Yohn 2024, VENDOR/ACADEMIC).
Gate: a named accountant. Decision C1 (do finance leases count as debt?) must be answered once and applied to debt, interest, D&A and FCF together.

### P4. Date alignment and history (10%) -> W5, R5 PENDING
Per-share date pairing (book value per share, net cash per share) is worth about 2,100-2,800 cells (R1). History from 2015, era-scoped tags and Q4 derivation: awaiting R5; baseline from data-team/34 is 25,193 missing of 717,052 on only 15 concepts.

### P5. Ingestion (4%) -> W5
SEC companyfacts holds zero facts for some 10-Q accessions (NEE, WELL, C, KO FILING-CHECKED in data-team/33). Detector first; a filing-level fallback reader only after it matches 100% on 50 filings companyfacts does carry. FSDS `num.txt` has face facts only, not note facts (R7, R2), so it cannot be the fallback for note-only values.

## 3. Wrong values: the trust problem (the part customers see)
- Stale value shown as current: 107 of 138 examined companies (78%, 95% interval 70-84), about 3,000-3,900 cells that the old fill measure counted as filled (R1).
- Total debt displayed wrong: 5% (arithmetic tests, data-team/31) to 15-25% (filing-checked shard samples). Split table defects: 156 candidates; NVDA alone 216 wrong per-share display cells.
- 10 wrong market caps in the ranking itself (status.md S000).
Order of attack: serve-time guards first (cannot create a wrong value, only a reasoned blank), then real fixes with a dry-run and a zero-wrong Verifier sample (data-team/33 B1/B2).

## 4. The architecture (engineering contract, R6)
- Fetch FSDS and FSN zip members by HTTP Range (central directory + needed members: `pre.txt` ~18 MB, `cal.tsv` ~9 MB, `sub.txt`, filtered `num.txt` ~43 MB per quarter), nothing written to disk. Fifteen quarters about 0.44 GB (1.1 GB with num) transferred. New `collector/bulk_datasets.py` and one new `SECClient.get_range` in `common/sec_client.py` (notify its owner). The Collector logs a hash and fetch record, not the bytes: a departure from "lossless raw" that the founder must approve.
- New adjacent package `structure/` (parse_pre, parse_cal, parse_num, load, recipe, resolver, identities) + `scrooner-structure` CLI; plugs into `certification/structure_checks.py` registered in `runner.CHECKS`. It never writes `core.*` or `canonical_fact`; adopting a perimeter into displayed values is a later Mapper step gated on Standardization Lead, accountant and Verifier.
- New tables: `filing_statement_line`, `filing_calc_edge`, `structure_ingest_log`, `concept_perimeter`, `company_concept_recipe`, `structure_concept_candidate`, `filing_identity_check`, raw fetch log. Reuse: `core.filing.accession_number` (= `adsh`), `sanity/accounting_identity.IDENTITIES`, `analytics.certification_finding`. Migrations 0098-0100 proposed (claim in doc 53; apply 0097 first; 0100 adds invariants I12 structure_disagree, I13 recipe_changed).
- Identity suite on two substrates (filing numbers and our stored canonical values); the diagnostic is the 2x2 of filing-pass/fail against stored-pass/fail. Identities: balance, gross profit, cash roll (CFO+CFI+CFF), subtotal trees (skip, not fail, when children are missing), net income IS vs CF only when tags differ.
- Run monthly in the `heavy-db-jobs` concurrency group; nightly gets a SELECT-only certify step. Top-1000 backfill about 20-30 minutes (ASSUMED).

## 5. Sequenced backlog (owners = data-team roles)
| # | Work | Owner | Size | Needs |
|---|---|---|---|---|
| 0 | Read FSN `readme.htm` (cal.tsv column layout); resolve measurement honesty (confirm migration 0096 and rebuild) | Data Engineer | S | pooler <= 14 |
| 1 | Population gating of dividend / bdc / net-lease / PEG rows; reason on every remaining blank | Data Engineer + Sector Analyst | M | none |
| 2 | Four no-definition fixes: FCF reads `capex_resolved`; store total-debt path; split lease-inclusive vs lease-exclusive debt tags; keep max-of-two D&A out of ratios; plus stale-value guard | Tag Mapper + Data Engineer | M | Verifier dry-run sample |
| 3 | Evidence layer v1 (extend `company_filing_line_evidence`, five states) + bank/insurer/REIT templates | Sector Analyst + Data Engineer | L | 30-filing zero-false-absent audit per family; accountant for bank revenue |
| 4 | Structure ingest (pre, cal) via Range, top-1000, latest 8 filings; size pilot | Data Engineer | M | Founder: raw-log departure |
| 5 | Identity suite (stored vs filing) in certify | Data Engineer | M | after 0097 applied |
| 6 | Structure candidate report: agree / disagree / structure-only for revenue, D&A, capex, interest, debt, operating income | Tag Mapper | M | 4, 5 |
| 7 | Composition layer for D&A, capex, total debt, interest, revenue, net income: definitions, perimeter records, reported vs standardized | Standardization Lead + accountant + Data Engineer | L | Named accountant; decision C1 |
| 8 | Per-share date pairing rule | Period Engineer | M | none |
| 9 | Ingestion detector + fallback reader | Data Engineer | M | 50-filing exact-match gate |
| 10 | Classify the ~2,000 unknown cells | Triage + Verifier | M | after 1-3 |
Sizes from R6 (S/M/L, ASSUMED): items 0-6 about 13-16 engineer-days; 7-11 about 15 more incl. accountant review; the rest about 7-10.

## 6. How we will know it worked (baseline, target, gate)
| Measure | Baseline (source) | Target | Gate |
|---|---|---|---|
| Fill on all cells, top 986 | ~77.1% corrected (R1, projection) | ~83% after W2-W5 | re-measure after 0096 rebuild |
| Fill on applicable denominator | ~88.6% | ~95.5% | applicability audit |
| Blanks with no reason | 13,349 of 29,931 (44.6%, shard baseline) | 0 | code check over all cells |
| Wrong value displayed, filing-checked sample | 5-25% of total-debt cells; 78% of companies show a stale value | 0 in the T1 100 companies first | zero-wrong Verifier sample per fix |
| Companies certified | 0 | 100, then 1,000 per data-team/34 | invariant suite + Verifier headline check |
Rule: report all three fill measures (value, applicable-denominator, current-and-not-stale) so denominator work never looks like a gain.

## 7. Kill criteria (stop and report, do not continue by momentum)
- K1: if the calculation tree explains fewer than half of the remaining D&A/capex perimeter cases after the R7 fix (about 20 and 5 of ~300), the composition layer stays disclosure-only.
- K2: more than half of 30 sampled `wrong_value` flags prove not real: demote that identity to `review`.
- K3: more than 5% of accessions miss the join to `core.filing`, or SEC refuses Range requests.
- K4: any family audit finds a false "absent": that family's reasons are not shown.
- K5: auto-publishing a structure-only value, flipping a sign, or closing a definition without the accountant is never allowed.

## 8. Decisions only the founder can make
1. **Name the accounting reviewer** and get decision C1 (finance leases in debt, interest, D&A, FCF). Highest-impact single action; W4 cannot start without it.
2. **Approve the Range-fetch design** that stores a hash and log of SEC bulk files instead of the bytes (departure from lossless raw).
3. **Approve migrations 0098-0100** and their numbers in doc 53.
4. **Fix the shared database ceiling** (see Risk 1) before any of this is measured or built.

## 9. Risks
1. **The shared pooler was above the limit (17-23 connections) for every agent for the whole investigation.** No count in this document is a fresh database measurement. Several sessions saturating the pooler is itself a program risk: certification, backfills and these queries cannot run. Fix the schedule (one heavy job at a time; doc 53) before engineering starts.
2. The R1 sample is S001-S045 ranked by market cap, not random; 550 companies in S046-S100 were never examined; financial strata are thin (8 banks, 21 other financials). Allocation of `mapping_gap` into vocabulary/composition/ingestion (65/22/10) and the 1,800-cell combined-line carve-out are ASSUMED.
3. Without FSN calculation-tree data many perimeter components stay "unknown": values stay correct but blank. Every claim that a tree resolves a pattern is ASSUMED except the CVX case already in the ledger; the pilot (item 4) tests it.
4. FSDS/R-files come from the same XBRL, so a filer tagging error would appear in both; FSDS `num.txt` has no note facts, so face-only counts are lower bounds.
5. R2/R4 regex precision is unmeasured (assume under 80% until a 50-filer sample per main pattern says otherwise). Only 10-Ks of FY2025 (and 3 quarters for R4) were covered: no 10-Q quarters, no ASC 606/842 era breaks yet.
6. Company-level overrides for perimeter could grow without bound; cap them and review monthly.

## 10. Not yet done
R5 history/eras section; Data Chief challenge and ranking; a Verifier review of the AMD, Aptiv, Walmart, ArcBest cases from R3; the section 8 SQL in R1 (needs pooler <= 14); precision samples per pattern; a 10-Q/Q4 version of the structural test.
