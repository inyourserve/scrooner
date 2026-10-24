# ONE company at 100% data and 100% coverage: engineering half (Data Engineer, 2026-10-24)

PLAN ONLY. Nothing built, dispatched or written to a database for this file. Product half: `ONE-COMPANY-100-PRODUCT-2026-10-24.md` (Ritwik).
Evidence labels: FILING-CHECKED (a cited filing or a Verifier report that opened it), DATA-INFERRED (our tables/code, no filing opened), ASSUMED.
Inputs read: my 2026-10-24 answer to the founder; mind (FSDS, calc linkbase, composite perimeter); PLAN.md certification round 2 and Lane 1 re-cut sections; ledger rows on AAPL. **The as-filed pilot (branch `work/data-engineer/as-filed-pilot`) had not landed** (no such branch on origin on 2026-10-24). I assume it will show: FSDS `num/pre/sub` give 100% of face-statement rows with accession and period for a cohort company, with no note facts and no custom-tag semantics (mind: "FSDS num.txt is face-statement facts only", FILING-CHECKED). If the pilot shows a different join rate, section 6 step 2 changes, not the design.

## 1. The correct approach for ONE company: the filing is the oracle, our tables are the product
Hybrid, one direction of authority:

| Source | Used for | Not used for |
|---|---|---|
| SEC companyfacts API (what we store today) | the production value path and the nightly (cheap, all 5,200 companies) | proof: it loses dimensions, which filing a value came from, conflicting copies, custom tags |
| FSDS `sub` + `num` + `pre` (+`tag`) | the AS-FILED EXTRACT of every face-statement row: accession, period, value, uom, statement, line order | note facts, custom-tag meaning, presentation labels beyond the face |
| Filing instance (`_htm.xml` / iXBRL) | custom (extension) tags, dimensioned facts (leases, debt note, segments), cover `dei` facts, the default-context CIK | bulk path (1-20 MB each) |
| Filing `cal` / `pre` linkbases | the PERIMETER record of each composite slot: what a total contains (mind: filer's own calc linkbase shows what is inside a total, FILING-CHECKED) and where a line sits on the face | values |
| Rendered R-file / the filing HTML | the human check by the Verifier (independent reader) | automation |
| 8-K Item 2.02 Ex. 99.1 | cross-check of derived Q4 and Q4 EPS (not in XBRL) | storage |

Direction: stored value -> proven against the as-filed extract of the SAME accession; never the other way. The extract is a read-only artifact (file + hash), not a new product table. Vendor data (yfinance, Alpaca prices) is never an oracle for statement cells.

## 2. "100% data correct", defined so it can be TESTED (AAPL scope)
Scope (ASSUMED, to be fixed in step 1): 163 data points x periods since 2015-01-01: FY 2015-2025 (11), discrete quarters Q1-Q3 (33) and derived Q4 (11), instants at 44 period ends, TTM at each quarter end. About 7,000 cells, of which a large share are `not_in_template` for a non-financial.

| Cell class | How EACH cell is proven | Coverage of the proof |
|---|---|---|
| A. Face-statement reported (income statement, balance sheet, cash flow, face EPS and share lines) | Programmatic full reconciliation: stored value equals the as-filed extract row for the cell's accession, period dates, uom, sign and scale; a cell with no extract row is a finding | 100% of cells, no sampling |
| B. Note-level reported (lease, debt composition, share counts by class, tax) | Value taken from an identified instance fact id (dimensions matched); reconciliation against the instance, not FSDS | 100% for the cells we store; the set of cells is bounded by the perimeter records |
| C. Derived periods (Q2/Q3 from YTD cash flow, Q4 = FY minus 9M, gross profit) | Recompute from class-A inputs with the registered formula and same-vintage inputs; Q4 also against Ex. 99.1 (11 Q4s x key lines is a census for one company) | 100% arithmetic; Ex. 99.1 census on the key lines |
| D. Per-share (EPS, DPS) | No derivation: filed value or `not_presented`/NM state; split basis checked against the filing's own restated comparative of the later filing | 100% |
| E. Metrics and TTM (ratios, growth, margins) | Independent recomputation by separate code from proven class A-D cells with the metric's formula version; exact equality | 100% |
| F. Price-dependent metrics | Arithmetic only (market cap = filed cover or balance-sheet shares x Alpaca price); the price itself is vendor evidence | arithmetic 100%, price stays a named residual |
| G. Not statement data (employees, ownership, text) | Out of scope for the proof | n/a |

Residual risk after all of this (honest list): (1) a filer's own XBRL error: the filing is the truth by definition, so we reproduce it, and flag with a certify rule; (2) shared-parser blind spots (FSDS and our parser read the same filer XBRL; mitigation: Verifier reads the HTML R-file independently, and three-reader harness exists, FILING-CHECKED on 5 filings); (3) concept definition choices that need an accountant (debt perimeter, NM rules): the cell is `definition_pending`, never "100% correct"; (4) 52/53-week comparability; (5) vendor price.

## 3. "100% coverage" definition
Every TEMPLATE cell of the company (template = the lines AAPL's own statements present, derived from the as-filed `pre` extract, not from SIC) in every period of scope is in exactly one of: `value`/`derived` (proven by section 2), `evidenced_zero`, `undefined_by_math`, `not_presented` (FILING-CHECKED locator), `not_in_template` (outside the denominator by audited rule). `defect`, `unclassified` and `guard_hidden` = 0 at exit. Coverage % = proven value cells / template cells; reported next to hidden-correct = 0.
How the reason layer is checked: every non-value state carries a `cell_evidence` row (migration 0100) with accession and locator; for ONE company this is a CENSUS, not a sample: the Verifier opens each distinct reason (expect fewer than 150 distinct company-line-reason combinations) and confirms it from the filing; the engineer's script confirms the count of cells per state sums to the template size (AT-7.3 style). A reason contradicted by the filing fails the exit.

## 4. Mechanisms needed for this one company, and where they stand
Hash = commit I know; "branch only" = branch name seen on origin, content not inspected by me (ASSUMED state).

| Mechanism | Needed because (AAPL) | State |
|---|---|---|
| As-filed extract + reconciler (FSDS num/pre/sub, instance) | the proof itself | MISSING (pilot not landed; AT-DE-32 unbuilt) |
| Authority gate (non-periodic never a source) + Stage 2e-b ban | DEF 14A/8-K copies in AAPL's facts | BUILT, flag off: `lane1-stage2e-authority-v2` 4bf20f1 |
| Matching copies (rounding) | duplicate copies across 10-K/10-Q | BUILT inferred-decimals version, same branch; real fix = store decimals (missing) |
| Reason store + evidence table | coverage definition | BUILT, not applied: 0100, `lane1-p1-primary-filer-v2` fccf6c1 contains it; contiguity blocker 0098/0099 |
| Rule flags (off/dry_run/on) | safe release | BUILT `lane1-rule-flags-v2` ee77148 |
| Share-date anchor (cover vs balance sheet) | AAPL cover shares are later than the balance-sheet date (book value/share 7.36 case, ledger) | branch only: `lane2-w10-anchor`, `lane2-w10-alone` |
| Split basis (4-for-1, Aug 2020) | AAPL shares never re-based (ledger 2026-10-21) | MISSING on origin (Period Engineer 0099 split tables held) |
| Per-share derivation ban + Q4 EPS state | Q4 EPS differs by 0.01 from release (AAPL Q4 FY25 1.84 vs 1.85, FILING-CHECKED) | HELD (`held/ru1-per-share`, not on origin as far as I saw) |
| TTM windows (calendar-aware, 52/53 weeks) | AAPL FY2023 is 371 days | branch only: `lane2-ttm-guards-v2` |
| Perimeter records (slot level) for debt, revenue, D&A, capex, interest, shares | composite lines: lease inside/outside debt, 3 revenue tags over time, D&A composed, LongTermDebt rounded narrative at AAPL (ledger 2026-10-21) | MISSING as a store; partial code `lane3-total-debt` (held guards), no cal-linkbase source yet |
| Structural revenue pick | not needed for AAPL (3 tags by period, solved by period-scoped mapping) | defer |
| Identity/P1 registrant | AAPL is single-registrant | NOT NEEDED (header test only) |
| Cell state / defect register | the scoreboard of exit | branch only: `lane2-cell-state-0102` |

## 5. Which company
**AAPL first.** Reasons: (a) it has more known, FILING-CHECKED defects than any golden company (4-for-1 2020 split not re-based; 3 revenue tags 2008-2025; rounded `LongTermDebt` narrative; 53-week FY2023 and shifted Q1; derived-Q4 EPS off by 0.01; shares cover-vs-balance date), so a pass means something; (b) single registrant, single share class, no NCI, no segment-dimension dependence, no custom revenue structure; (c) its filings are already opened in this repo (R-files for 10 filings in the Verifier scratch, FILING-CHECKED). MSFT is the control (June year end, no split since 2003) but exercises less. A simpler non-financial would not hit splits and leases together, so the proof would be weaker.
**Company #2: JPM (bank)**, not a REIT first: different template (net revenue, no gross profit), DEF 14A defects already measured (57,000M vs 57,048M), big FDIC cross-source option, and the group-template layer is the next structural risk. REIT (e.g. PLD) is #3.

## 6. Work breakdown (engineer-days ASSUMED +/-25%; waits for slots and Verifier excluded)
1. Fix scope and oracle (AAPL template from `pre`, cell list, period grid, cell key, exit script skeleton): 2 d. Exit: cell list file with hash; count per class.
2. As-filed extract for AAPL (FSDS 2015q1-2026q3 streamed from a runner, 46 quarters, plus instances for custom/dimensioned facts of the 44 filings): 4 d. Exit: every face row with accession/period/value; row count equals the R-file row count on 10 sampled filings.
3. Reconciler stored-vs-extract, classes A-D: 4 d. Exit: report of all disagreements, each with accession; unexplained = 0 is NOT yet required.
4. Fix what step 3 finds, using the built branches first (authority, W10 anchor, TTM, split basis, per-share): 8 d (largest uncertainty). Exit: class A disagreements = 0 or each classified filer-error/definition-pending.
5. Perimeter records for the six slots from `cal`/`pre` of AAPL filings, versioned and flag-gated: 4 d. Exit: each composite cell lists its slots and the filing calc evidence; lease/debt cells reconcile.
6. Independent metric recomputation and TTM (class E, F arithmetic): 3 d. Exit: exact equality on 100% of metric cells.
7. Template and reason layer with evidence rows; state sums equal template size: 4 d. Exit: defect = 0, unclassified = 0.
8. Verifier: independent HTML read of a risk-ranked set plus the reason census plus Q4 census vs Ex. 99.1: 5 Verifier-days. Exit: zero contradicted.
9. Freeze: certify run, scoreboard, ledger, rollback rehearsed: 2 d.
Total about 31 engineer-days + 5 Verifier-days + about 2 Standardization/accountant days (debt perimeter, NM, Q4 EPS cards). Minimum agents: 1 Data Engineer (serial), 1 Verifier, Standardization Lead part-time, Release Manager for commits, scrooner-4d for the single heavy slot (extract and reconcile are light reads; only the recompute needs one slot). Prerequisite outside the plan: 0098/0099 contiguity (or the 0099 no-op) so 0100 can apply.

## 7. What could make the one-company proof fail
- The accountant decisions (debt perimeter, Q4 EPS display, NM) stay open: those cells can only be `definition_pending`, so "100%" is not reachable; decide before step 4.
- FSDS lacks a line our product shows (note-level or custom tag) and the instance reader has gaps: coverage claim drops to "note cells by instance only".
- Shared blind spot: FSDS, instance parser and our mapping all inherit one XBRL error; only the Verifier's HTML read catches it.
- Changing a rule after the proof (a version change re-opens every cell): freeze definitions and flag versions first (A13 versioning not built).
- Core.fact bloat / database state (14M dead tuples at 2026-10-22, DATA-INFERRED) makes the recompute step fail; VACUUM approval pending.
- Disk: 9 GiB free; mitigated by streaming FSDS from a runner and keeping one file at a time, but a local extract of 46 quarters would not fit.
- Scope creep: the same machinery proves AAPL, not "the pipeline"; company #2 may expose a template problem rather than a data one.
