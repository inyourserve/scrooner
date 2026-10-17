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

## 3. The deriver subtracted non-additive concepts (guard added, `46399a6`)
- `derive_q4_for_company` and `derive_interim_quarters_for_company` derived Q4/Q2/Q3 for **every** duration concept.
- Confirmed live, companies 1-150: derived `WeightedAverageNumberOfDilutedSharesOutstanding` 469 rows, 444 negative; basic 478 rows, 452 negative; all `is_authoritative`. Nothing consumes those tags today (unmapped), so no screen was wrong, but Wave 1 would have mapped negative share counts.
- **Fix:** both paths now skip `WeightedAverage%` concepts. EPS is deliberately not changed: it is also non-additive, but removing derived Q4 EPS would change TTM EPS and P/E coverage. **Decision needed** from the founder/Standardization Lead.
- **Not done (needs approval):** existing derived weighted-share rows are still in `core.fact`. A cleanup would delete `is_derived` facts for `WeightedAverage%` concepts; raw reported facts stay.
- Also unchecked: other non-additive duration tags (rates, per-share dividends, percentages). A units breakdown of derived facts timed out under load; rerun when the database is quiet.

## 4. Wave 1 tag proposals (Tag Mapper, 300-company convenience sample; nothing approved)
Proposed concepts: `retained_earnings` (exact, signed), `weighted_avg_shares_basic` and `_diluted` (exact; must exclude derived), `operating_lease_rou_asset`, `operating_lease_liability_total` (with current+noncurrent sum fallback), the current/noncurrent components, `interest_paid_cash` and `income_taxes_paid_cash` (not equivalent to expense; never a fallback for it).
Checks that shaped the proposals: retained earnings equals stockholders' equity in only 27 of 10,560 company-periods (never an alias); lease current+noncurrent equals the total within 0.5% in 97.7% of 2,708 company-periods, with counterexamples (companies 1550, 1312, 683); interest paid within 10% of interest expense in 2,064 of 4,854 pairs and taxes paid off by more than 2x in 2,288 of 6,173 (hard rule: cash paid is not expense).
Still required before any mapping: full-population coexistence check, unit policy for non-USD retained earnings (CAD, EUR seen), review of finance-lease separation, Verifier check of counterexample filings, and fixing the derived-share defect (done) first.

## Process lessons
- A table rebuilt as delete-then-insert in several commits is a latent outage; rebuilds must be one transaction or build-and-swap.
- Convenience samples (low company ids, every 17th id) differ systematically from the population. Report sample design with every percentage.
- Background MCP queries that time out may keep running on the server; check `pg_stat_activity` and cancel your own.
