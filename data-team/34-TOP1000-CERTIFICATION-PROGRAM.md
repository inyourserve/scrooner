# Top-1000 certification program (Dhairya, 2026-10-21)

Founder goal (2026-10-21): 100% coverage and 100% correct data for the top 1,000 companies, whatever it takes, including the pipeline.

## What the claim means (so it can be tested)
A company page is **CERTIFIED** only when all of these hold at the same time, with evidence stored per company:
1. **Every cell is accounted for.** Each of the company's data points (163 per company in `analytics.company_data_point_coverage`) is either (a) a value traceable to a filed fact, or (b) a stated, evidenced non-value: `not reported by this company` / `not applicable to <family>` / `history not available before XBRL` / `not in the latest filing (last reported ...)` / `definition pending`. No unexplained blank.
2. **Every value passes the automated invariant suite** (below), run by code over ALL of the company's stored values, not a sample.
3. **Headline values are reconciled to an independent parse** of the same filings (SEC Financial Statement Data Sets `num.txt`, read from the quarterly zip, never from our own tables) within rounding, for the latest fiscal year and latest four quarters.
4. **A Verifier filing check is recorded** for the company's headline cells (revenue, operating income, net income, diluted EPS, total assets, total equity, CFO, capex, shares, total debt, market cap) for the latest FY and latest quarter, opened in the original filing, with accession and locator.
5. **No open finding** in `analytics.certification_finding` for that company.
Honest limit: certification proves the checks and the sampled filing comparison pass. It cannot prove that a filer's own filing is right; it records known filer errors (label shifts, mis-tags) as company-scoped exceptions.

States: `uncertified` -> `checks_clean` (2 and 5) -> `reconciled` (3) -> `verified` (4) -> `certified` (all). Coverage is reported per state; "100%" is only claimed for `certified`.

## The invariant suite (code, population-wide, per company)
Taken from the study (data-team/23, 24) and the shard findings. Each check writes a finding with the cell, the rule, the evidence values, and a severity (`wrong_value` blocks certification, `review` needs a human or the Verifier).
- I1 Balance identity: assets = liabilities + equity (+ NCI/redeemable) per period, within the filed decimals.
- I2 Statement ties: net income on the income statement equals the cash-flow starting net income; cash change = CFO + CFI + CFF + FX within tolerance; retained earnings roll-forward where available.
- I3 Sign policy: DQC_0015 element list (6,396 elements that must not be negative) and our concept sign policy; negative revenue, assets, shares, debt, dividends per share are findings. Never flip a sign; quarantine.
- I4 Scale and plausibility: monetary and share values against the company's own neighbouring periods and against price x shares; > 3 orders of magnitude is a finding (catches the 1,000x and 1,000,000x errors); market cap vs price x shares; margins > 100%; EPS vs net income / shares.
- I5 Period integrity: period lengths (quarter 91 +/- 30, year 364/371), full-year value under a quarter label, one value per company/concept/period, no value equal to another period's value for the same tag (label shift), comparative window of the source filing.
- I6 Source integrity: every displayed value's source fact is authoritative, from 10-K/10-Q-family forms only (no DEF 14A / 8-K), same unit family, USD; stored value equals the authoritative copy within rounding (the matching-copies rule).
- I7 Currency: every displayed value is not older than the company's own latest filing beyond the staleness rule (`common/staleness.py`), and every INPUT of a displayed metric passes the same age rule (shares: 15 months).
- I8 Composition: total_debt equals the sum of its recorded components with no double counting and is not 0 when any debt tag is nonzero; per-share derivations never by subtraction.
- I9 Split consistency: per-share history uses one share basis; a share-count change of 1.5x or more has a split on record.
- I10 Sector template: the company's family (bank, insurer, REIT, ...) is evidenced and its non-applicable metrics are suppressed with the stated reason.

## Independent reconciliation (R)
- R1 SEC Financial Statement Data Sets (`num.txt`/`sub.txt`, quarterly zips, already downloaded once for sizing): our stored headline values vs the data set's values for the same adsh/tag/ddate/qtrs, for the 1,000 companies.
- R2 SEC Frames (CY aggregates) as a cheaper secondary check on annual values. Frames agrees with latest-filed by construction, so it only catches pipeline drops, never filer errors.
- R3 yfinance remains a signal only; it never classifies or verifies.

## Pipeline work required (owners)
| # | Work | Owner | State |
|---|---|---|---|
| P1 | `scrooner-certify` CLI + tables `analytics.company_certification` and `analytics.certification_finding` (migration, committed, applied later); implements I1-I10 as SQL/Python, chunked by company, read-only except its own two tables | Data Engineer | to build |
| P2 | R1 reconciliation job against the Financial Statement Data Sets for the top-1000 | Data Engineer | to build |
| P3 | Ingestion gap: 10-Qs in `core.filing` with no facts loaded (SEC companyfacts feed gap): detector, and a filing-level reader that must match 100% on 50 filings companyfacts does carry before use | Data Engineer + Tag Expert | detector first |
| P4 | Dead letters: 88 unresolved (normalizer 72, mapper 16) block the freshness gate; classify and clear | Data Engineer | to do |
| P5 | Total debt rebuild (composition, zero-borrowings rule, the sole-tag fills), net income attributable to parent, revenue precedence (606 subset vs total), stale-input guard (15-month shares), market cap share-count rule, predecessor CIK links, split table gaps | Tag Mapper, Standardization Lead (+ accountant), Period Engineer | per fix plan batches B0-B4 (data-team/33) |
| P6 | Sector templates: banks first (148 financials in the top 1000), then REIT, insurer, asset manager, utility | Sector Analyst, Tag Expert, Standardization Lead | after the invariant suite shows the real wrong-value counts |
| P7 | Certification dashboard (`/app/data-coverage` page already exists): show per-company state, open findings, and the top-1000 certified count | Data Engineer | after P1 |
| P8 | Incremental nightly cohort selection (design done in the reprocess diagnosis) and non-overlapping scheduled jobs | Data Engineer | after D2 |

## Operating loop (every batch of 10 companies)
find (campaign shard) -> classify into rule family -> fix family (dry-run, Verifier sample with zero wrong rows, committed migration/code, reprocess) -> re-run the invariant suite and R1 for the whole cohort -> Verifier certifies headline cells -> mark `certified`. Report weekly: companies per state, open findings by rule family, new wrong values found by the suite.

## What I will not do
Fill a cell the company does not report; flip a sign to make a check pass; write a fix to the database without a reviewed dry-run and a zero-wrong Verifier sample; call a company certified on inferred evidence. A shortfall is reported as a shortfall.

## History window: January 2015 to date (founder requirement 2026-10-21)
Every top-1000 company must have its full history from 2015-01-01 to the latest filing: every annual period (FY), every quarter (Q1-Q4, with Q4 derived only where policy allows), every balance-sheet instant, and TTM where derivable, for ALL data points, not only the latest period. A missing historical cell is either filled with a correct value traceable to a filed fact, or carries a stated, evidenced reason (`not yet public / company registered {date}`, `not reported by this company`, `not in the SEC feed (filing X)`, `history lives at predecessor CIK {cik}`).
Expected periods per company = every fiscal period with period_end >= 2015-01-01 and <= the latest filed period, starting at the later of 2015-01-01 and the company's first filing (or its predecessor's, once the CIK link exists).
**Invariant I11 (history completeness)**: for each company and each consumed concept (33) and each metric, expected vs present periods since 2015-01-01; every missing cell must carry a classified cause. Certification requires zero unclassified missing cells and zero `wrong_value` findings across the whole window, not just the latest period; I1-I10 apply to every period in the window.
**Baseline, top-1000, measured 2026-10-21 (DATA-INFERRED, `analytics.period_completeness`, only 15 core concepts tracked today):** 717,052 expected, 691,859 present (96.5%), 25,193 missing; 771 of 995 companies have their earliest expected period in 2015; core.period earliest end date: 796 companies by 2015-06-30, 91 between 2015-H2 and 2018, 113 after 2018. Causes of the 2015+ gaps (`analytics.period_gap`, top 1000): q4_not_derived 5,801 and quarter_not_derived 5,345 (Period Engineer), no_mapped_tag about 8,600 across Q/FY/I/Q4 (Tag Mapper and Tag Expert: era-scoped tags, since pre-2018 filers used different tags), no_line_item_filed about 1,700 (needs rendered-statement evidence before being called absence), not_in_sec_feed about 1,500 (ingestion reader, P3), conflict_material 566 (resolver), filing_not_processed about 850 (Data Engineer).
**Work this adds:** (a) extend period_completeness from 15 to all 33 consumed concepts and to metrics (Data Engineer, in `scrooner-certify` as I11); (b) predecessor/successor CIK links so history survives re-registration (MRVL, LIN, SHOP, BLK, DIS, XOM; Company Master); (c) era-scoped tag sets so FY2015-FY2018 filings map under their own tags (Tag Expert cards must record the era per tag); (d) Q4 and interim derivation across the whole window under the additive allowlist (Period Engineer); (e) split table complete for 2015+ so per-share history is on one basis; (f) a Verifier trial of 10 companies across 2015, 2018, 2021 and 2025 annual values, not only the latest year.
Display tiers (what the public page shows vs what a logged-in user sees) are a product decision for the Head of Data Product; this window is the DATA we hold and certify.
