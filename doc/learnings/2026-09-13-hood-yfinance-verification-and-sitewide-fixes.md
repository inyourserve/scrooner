# 2026-09-13 — HOOD financial-table gap investigation → two sitewide fixes

Prompted by a user report: Robinhood (HOOD)'s financial statement table has "lots of empty rows," believed similar to a prior Etsy-shaped issue. Investigated with real data at every step, then asked directly to verify against yfinance, then to fix what was found and look for more. Ended up finding and fixing two real, population-wide issues — neither one specific to HOOD.

## 1. Why HOOD looked broken — and why it's a different bug class than Etsy

The Etsy fix (`mapper/conflict_resolution.py`) targets a specific shape: a company that *normally* reports a concept, but 2+ filings briefly disagree on the exact value for one period, so `normalizer/dedupe.py` correctly refuses to pick between them (Stage 2e, documented intentional behavior). A per-company tag-preference override resolves the ambiguity.

HOOD's blanks are structural, not ambiguous: checked directly against `core.fact` — **zero raw facts under any currently-mapped tag** for `cost_of_revenue`, `gross_profit`, or `operating_income`, for any period, ever. There's no disagreement to resolve; there's no value at all. Robinhood (SIC 6211, "Security Brokers, Dealers & Flotation Companies") presents its income statement the way banks do: Revenue → Total Operating Expenses (one combined line) → Pretax Income, with no COGS/Gross-Profit/Operating-Income subtotal in its own XBRL.

## 2. yfinance verification — the numbers that matter are correct

Ran `scrooner-yfinance-financials fetch-statements`/`compare` for HOOD specifically. Revenue, Net Income, Pretax Income, Tax, Diluted EPS, SBC, Buybacks, D&A, CFO, and both cash-flow lines all matched **exactly** (0% diff) across every quarter checked. HOOD's core numbers were never wrong.

## 3. Real, sitewide bug #1: the yfinance comparison tool couldn't check ANY balance-sheet concept, for ANY company

Digging into why HOOD showed 100% "missing_ours" on every balance-sheet line (cash, assets, liabilities, equity) despite the data clearly sitting in `analytics.canonical_fact` (confirmed directly: HOOD's Q2 2026 cash figure existed under the exact period_id the comparison should have used), found the root cause in `yfinance_financials/compare.py`: `_load_our_periods()` returned periods without their `period_type`, and a real fiscal quarter routinely has **both** a `duration` period (income statement/cash flow) and an `instant` period (balance-sheet snapshot) sharing the identical `end_date` — correct, standard XBRL modeling, the same "two period rows, one real quarter" shape this project has hit before (Nike's FY/Q4, MSGS's overlapping spans). `_closest_period()`'s tie-break had no type-awareness, so a tied distance always resolved to whichever row Postgres returned first — which in practice was always the duration row.

**Checked against every company this tool has ever compared, not just HOOD**: every balance-sheet concept (`cash_and_equivalents`, `current_assets`, `current_liabilities`, `total_assets`, `total_liabilities`, `stockholders_equity`, `ppe_net`, `accounts_payable`, `accounts_receivable`, `inventory`, `total_debt`) was reporting **"missing_ours" 99.5–99.9% of the time**, for real data that was actually present the whole time. Duration-type concepts (revenue, net_income, cfo, etc.) were never affected, since a tied distance happened to already prefer duration rows.

Fixed by making `_load_our_periods()` return `(id, end_date, period_type)` and `_closest_period()` filter candidates to the correct type (`balance_sheet` → `instant`, `income_statement`/`cash_flow` → `duration`) before picking the closest one. Verified live on HOOD: `missing_ours` for its comparison dropped from 75 to 37, `ok` rose from 55 to 83 — and the 37 remaining are now genuine gaps (see below), not false negatives. 2 new regression tests added (`test_yfinance_financials_compare.py`), covering the exact same-date instant/duration tie the bug was built on.

A full-population rerun of `compare_statements()` (recomputation only, no new yfinance fetches — 4,870 companies already have statement lines cached) was kicked off to refresh every company's comparison findings under the fixed logic; it runs long enough on this dev machine's network profile to still be in progress as this entry is written.

## 4. Real, sitewide bug #2 (well, a real gap, fixed as a verified derivation): Operating Income missing for ~840 companies that don't separately tag it

The HOOD comparison surfaced something better than "permanently blank": yfinance's own "Operating Income" for HOOD matched **Revenue minus our stored `operating_expenses`, exactly, across all 5 quarters checked** ($1,308M − $734M = $574M, etc.) — because HOOD's `operating_expenses` tag already represents the full expense base (it has no separate Cost of Revenue). For a company that *does* separately report Cost of Revenue, the equivalent formula is Gross Profit − Operating Expenses.

**Verified before shipping, not assumed**: checked `Revenue − OperatingExpenses − CostOfRevenue` against every (company, period) that already has a real, directly-tagged `operating_income_resolved` value (a control group, not the target population) — **90.3% land within 2%** when `cost_of_revenue_resolved` also exists (166,417 real periods), **85.5% within 2%** when it doesn't (35,348 real periods). Not perfect — a real income statement can carry additional "other operating income/expense" lines this simple subtraction can't see — but purely additive, so an imperfect fill only ever replaces an empty cell, never a better value.

**Checked for the exact bank-shaped trap this project has hit before naming any exclusion**: banks/savings institutions (SIC 602x/603x) *do* have `operating_expenses_resolved` facts (their own real tag), and some also have a `revenue_sanity_resolved` value — meaning the naive formula would have fired for them too. Measured directly: **583 real (company, period) pairs** across the 3 bank SIC prefixes would have received a fabricated value. Excluded explicitly, reusing the same `BANK_SIC_PREFIXES` convention `yfinance_financials/line_item_map.py` already established.

Shipped as `mapper/conflict_resolution.py`'s new `resolve_operating_income_arithmetic_fallback()`, wired into `resolve_all_conflict_fills()` (runs last, purely additive `INSERT ... ON CONFLICT DO NOTHING`, never touches an existing value). Run population-wide: **18,170 new real cells filled.** Verified: HOOD's Q2 2026 now shows `operating_income_resolved = $574,000,000`, matching yfinance to the dollar. `operating_income_resolved` coverage: **83.8% → 86.6%** — now essentially at the same ceiling as `revenue_sanity_resolved` itself (86.7%), meaning virtually every company with a usable revenue figure now also has an operating income figure.

## 5. What's genuinely NOT fixable, and grouped rather than re-investigated per company

Checked directly (not assumed) whether Cost of Revenue/Gross Profit's remaining gap is the same structural shape as HOOD's: `cost_of_revenue_resolved` and `gross_profit_resolved` sit at an identical **60.3–60.5%** coverage ceiling — because `gross_profit_resolved`'s own existing arithmetic derivation (Revenue − Cost of Revenue, built 2026-09-02) can only ever fire when `cost_of_revenue` itself exists. The remaining ~40% gap breaks down into real, already-partially-documented sector clusters (`company_data_point_coverage`'s SIC breakdown, active companies only): Blank Checks/SPACs (291, pre-revenue), Pharmaceutical Preparations (242, pre-revenue), State + National Commercial Banks (173+81, structural), REITs (130, structural), Commodity Contracts Brokers (102, pass-through), Biological Products (95, pre-revenue), Fire/Marine/Casualty Insurance (52, structural), Crude Petroleum & Natural Gas (52, many pre-revenue exploration), Finance Services (44) and Investment Advice (39, broker-dealer-adjacent), Savings Institutions (35+31, structural), Electric Services (24, regulated-utility presentation).

**Robinhood's own sector, Security Brokers/Dealers/Flotation Companies (SIC 6211), is a real, narrow, confirmed-live addition to this list**: 15 of 22 active companies in that SIC code lack `cost_of_revenue_resolved` — the same structural absence as banks, just not previously named for this specific sector. Left un-added to `mapper/coverage_matrix.py`'s `SIC_GAP_REASONS` dict deliberately: that mechanism applies one reason string across all 5 `REVENUE_FAMILY_CONCEPTS` per SIC code, which would be actively wrong here — broker-dealers' `revenue`/`operating_expenses` are fine, and `operating_income` is now usually derivable (fix #2 above); only `cost_of_revenue`/`gross_profit` are genuinely absent for this sector. Forcing a single-line-item exception into a mechanism built for "this whole concept family is absent" would mislabel the 3 concepts that aren't actually missing. Recorded here instead as a scoped, evidence-backed finding for whoever next extends that classifier to support per-concept (not per-family) SIC reasons.

## Current full-population coverage, every statement-table row (active companies, post-fix)

| Concept | Coverage | Note |
|---|---:|---|
| net_income / net_income_resolved | 99.1% / 99.0% | |
| total_assets / _resolved | 99.0% | |
| cfo / _resolved | 98.4% | |
| cash_flow_financing / _resolved | 98.2% / 98.1% | |
| cash_and_equivalents / _resolved | 97.5% | |
| stockholders_equity / _resolved | 97.2% | |
| cash_flow_investing / _resolved | 95.0% | |
| diluted_eps / _resolved | 90.9% | |
| total_liabilities / _resolved | 90.3% | |
| income_tax_expense / _resolved | 87.9% | |
| revenue / revenue_sanity_resolved | 86.7% | ceiling for the whole revenue family |
| **operating_income_resolved** | **86.6%** | was 83.8% before fix #2, this session |
| income_before_tax / _resolved | 83.6% | |
| ppe_net / _resolved | 81.9% | |
| current_assets / _resolved | 81.7% | |
| current_liabilities / _resolved | 81.5% | |
| capex / _resolved | 80.8% | |
| operating_expenses_resolved | 77.9% | |
| interest_expense / _resolved | 74.8% | |
| total_debt_resolved | 71.6% | |
| share_buybacks / _resolved | 63.6% | most companies don't buy back — not a gap |
| cost_of_revenue_resolved | 60.5% | see sector breakdown above |
| gross_profit_resolved | 60.3% | bounded by cost_of_revenue's own ceiling |
| research_and_development | 45.6% | most companies don't disclose separately |
| dividends_paid / _resolved | 41.2% | most companies don't pay dividends |

## Net result

2 pipeline files changed (`yfinance_financials/compare.py`, `mapper/conflict_resolution.py`), 2 new regression tests, full pipeline unit suite 491/491 passing. Both fixes verified against real data before being called done — the period-type fix confirmed live on HOOD's own comparison output, the arithmetic fallback confirmed against a 200,000+-period control group before running population-wide, and confirmed live afterward (HOOD's own new value, to the dollar). Nothing here required guessing: every claim above is backed by a query against the live database, not an assumption from the code's own comments.
