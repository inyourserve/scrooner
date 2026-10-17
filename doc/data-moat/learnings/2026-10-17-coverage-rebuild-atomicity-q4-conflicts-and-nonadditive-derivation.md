# 2026-10-17: three root causes behind "coverage is low" and stale

Found by a fresh-eyes audit plus two data-team role runs (Period Engineer, Tag Mapper). Counts are samples unless stated; each names its limits.

## 1. The coverage table was left half-built by a non-atomic rebuild (fixed, `7cb4970`)
- **Symptom:** `analytics.company_data_point_coverage` had only the 78 concept columns (no metric rows) and no `gap_reason` at all; `coverage_snapshot` last written 2026-10-13; every dashboard reading either was wrong.
- **Cause:** the 2026-10-16 nightly's matrix, tag-candidate and snapshot steps all died with `QueryCanceled: statement timeout`. `build_coverage` committed the delete and each insert separately, so the timeout in the metric insert left a deleted-and-partly-rebuilt table. The timeouts were raised on 2026-10-17 (`7f4eb17`), which addresses the trigger but not the half-built risk.
- **Fix:** delete, all inserts and the three classification passes now run in one transaction, committed once. A failure rolls back and the previous complete table stays. Tests fail if an intermediate commit is reintroduced.
- **Watch:** one transaction means one long-held transaction (about 15 min in CI, longer under load). Locally under contention it exceeded 27 min. The per-statement timeout is 30 min.

## 2. Q4 "not derived" gaps are mostly input conflicts, not missing arithmetic
Period Engineer census, 3,587 cells in six company_id blocks (about 11% of 32,671; not random):
| Category | Share |
|---|---|
| clean, derivable (authoritative single-value FY plus 9M or Q1-Q3 chain) | 2.1% |
| conflicting values, no authoritative copy on FY or 9M side | 65.3% |
| no 9-month source (FY exists) | 31.5% (overstated: ~13% of a checked block had 9M under another mapped tag) |
| no FY fact | 0.9% |
- Of the conflicting cells: FY not authoritative 42.8% of sample, 9M conflicting 22.6%; 6.4% have mixed signs within one period (46 cells differ only by sign).
- **Why the resolver misses them:** `normalizer/conflict_latest_filed.py` promotes the latest-filed full-year fact for only 6 validated tags (NetIncomeLoss, CFO, Revenues, RevenueFromContract..., OperatingIncomeLoss, GrossProfit), and quarters for 4. It does not cover 9-month YTD periods, investing and financing cash flow, income before tax, income tax expense, or EPS.
- **Real restatement pairs matter:** examples 1, 3 and 4 in the run show original FY with original 9M gives a different Q4 than restated FY with restated 9M, and mixed vintages give a third answer. A fix must pair inputs from the same vintage, or block.
- **Earlier 60% claim was wrong.** It counted `canonical_fact` values picked by the display layer from conflicting duplicates. Always read the raw `core.fact` rows (with `is_authoritative` and filing dates) before calling a gap "derivable".
- Policy still needed (not decided): extend latest-filed to the unvalidated additive tags after a SEC Frames annual check (Frames cannot validate 9M); same-vintage pairing for FY and 9M; precision-aware rounding tolerance (not 0.1% without sign-off); sign-only conflicts quarantined.

## 3. The deriver subtracted non-additive concepts (guard added `46399a6`; correct method found, awaiting approval)
- `derive_q4_for_company` and `derive_interim_quarters_for_company` derived Q4/Q2/Q3 for **every** duration concept with FY - (Q1+Q2+Q3).
- For a weighted-average share count that is structurally wrong: each quarter is about S, so FY - 3S is about -2S. Confirmed live, companies 1-150: derived `WeightedAverageNumberOfDilutedSharesOutstanding` 469 rows, 444 negative; basic 478 rows, 452 negative; all `is_authoritative`. Apple Q4 FY2025 diluted: derived -30.15B (reported quarters 15.15B, 15.06B, 14.95B; FY 15.00B).
- **Correction to an earlier statement:** the tag IS consumed. `mapper/price_metrics.py::_load_latest_diluted_weighted_shares` uses the latest authoritative **positive** value as a Market Cap share-count fallback (multi-class filers). Negative derived rows are skipped by that filter, so Market Cap fell back to the Q3 value (a quarter stale); a positive wrong derived value (rare, ~5% of derived rows) could be picked. Not measured: how many companies' Market Cap currently rest on a derived row.
- **Independent check (yfinance + competitor):** for 44 company-FY-share-type cases across 20 companies and varied fiscal year-ends, `Q4 = 4*FY - (Q1+Q2+Q3)` matches Yahoo's own quarterly Diluted/Basic Average Shares with median error 0.024%, p90 0.20%, max 0.78% (INTC); our current formula was negative in 44 of 44. Apple exact: 14,863,611,000 vs Yahoo 14,863,609,000. Trendlyne's saved Apple page (`doc/html/trendlyne-apple.html`) shows the same positive quarterly series (14,815.3M for Q4 FY25). So Yahoo and Trendlyne both carry a Q4 share count built this way; Scrooner's was wrong. Script: not committed (scratchpad `q4_shares_vs_yf.py`); yfinance is a comparison only, never a stored value.
- **Method is an approximation, not an identity:** it assumes equal quarter lengths and that the annual average is the mean of the quarterly averages (52/53-week years and large mid-year buybacks add error; diluted adds treasury-method effects). It must be flagged as derived/approximate with lineage.
- **Decision for the founder / Standardization Lead:** adopt `Q4 = 4*FY - (Q1+Q2+Q3)` (and `Q_n = n*YTD_n - (n-1)*YTD_(n-1)` for interim) for weighted-average share counts only. With that, the existing wrong rows are **overwritten in place** by the deriver's upsert (`on conflict ... do update`), so no deletion is needed. Until adopted, the guard keeps new wrong rows from being created and old ones stay (harmless to Market Cap because of the `> 0` filter).
- EPS is also non-additive but left unchanged; the same independent check should be run for derived Q4 EPS before any decision.
- Also unchecked: other non-additive duration tags (rates, per-share dividends, percentages); a units breakdown query timed out under load.

## 4. Wave 1 tag proposals (Tag Mapper, 300-company convenience sample; nothing approved)
Proposed concepts: `retained_earnings` (exact, signed), `weighted_avg_shares_basic` and `_diluted` (exact; must exclude derived), `operating_lease_rou_asset`, `operating_lease_liability_total` (with current+noncurrent sum fallback), the current/noncurrent components, `interest_paid_cash` and `income_taxes_paid_cash` (not equivalent to expense; never a fallback for it).
Checks that shaped the proposals: retained earnings equals stockholders' equity in only 27 of 10,560 company-periods (never an alias); lease current+noncurrent equals the total within 0.5% in 97.7% of 2,708 company-periods, with counterexamples (companies 1550, 1312, 683); interest paid within 10% of interest expense in 2,064 of 4,854 pairs and taxes paid off by more than 2x in 2,288 of 6,173 (hard rule: cash paid is not expense).
Still required before any mapping: full-population coexistence check, unit policy for non-USD retained earnings (CAD, EUR seen), review of finance-lease separation, Verifier check of counterexample filings, and adoption of the corrected weighted-share Q4 method (section 3).

## Process lessons
- A table rebuilt as delete-then-insert in several commits is a latent outage; rebuilds must be one transaction or build-and-swap.
- Convenience samples (low company ids, every 17th id) differ systematically from the population. Report sample design with every percentage.
- Background MCP queries that time out may keep running on the server; check `pg_stat_activity` and cancel your own.

## 5. Outcome and rollout state (end of 2026-10-17)
- **Coverage table repaired** by the manual rebuild (first run of the atomic version): 163 data points, 5,206 companies, 848,578 rows, 193,196 rows with a gap reason (13,903 `line_not_presented_in_filing`).
- **Weighted-share method (`7825b47`) verified against the companies' own earnings releases** (Data Verifier, 8-K Exhibit 99.1 three-month columns): Apple, Microsoft, Nike, Costco verified, differences 0.000007% to 0.027% (Costco's 16-week Q4 also matched). Coca-Cola showed the old negative row only because it was not in the re-derived slice (fact ids created 2026-08-25); it is expected to correct on the population re-derive. Five issuers do not prove the population: after the re-derive, query all `is_derived` rows of the two tags for non-positive values.
- **EPS: no change.** Derived Q4 EPS (FY - Q1 - Q2 - Q3) vs Yahoo's Q4 EPS across 42 cases: median abs error $0.007, p90 $0.010, max $0.070 (Cisco FY2025). NI/shares alternative was not better where testable.
- **Latest-filed resolver extended (`cb0305b`)** to IncomeTaxExpenseBenefit, pre-tax income, investing and financing cash flow (annual). Frames validation, 600 companies: 100.0%, 100.0%, 99.8%, 100.0% (earliest-filed 18-34%, majority 65-79%).
- **Not yet applied to the full population.** The resolver extension and the weighted-share re-derive take effect only when `conflict-latest-filed`, `derive-interim-quarters`, `derive-q4` and the mapper chain next run for each company. The nightly handles only recently-filed companies. Run the full chain through the manual `Full-population recompute` workflow with `normalize_stages="conflict-latest-filed derive-interim-quarters derive-q4"`, shards 3, in a quiet window: its own header says no daily refresh, sanity run or local batch job may overlap (a 2026-09-27 overlap took the database down for ~7 hours). It also rebuilds the screener snapshot (P/E, market cap and TTM metrics can move slightly where fallback share counts or newly-authoritative annual values change).
- **After the recompute, measure:** `q4_not_derived` count before/after (period_completeness), non-positive derived share rows (expect 0), Market Cap coverage and values for companies that used the weighted-share fallback, and a Verifier sample of newly-authoritative annual values against filings.
