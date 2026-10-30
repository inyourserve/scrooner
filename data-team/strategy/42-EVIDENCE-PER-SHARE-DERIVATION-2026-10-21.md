# Evidence for the root-cause pass: per-share and ratio values derived by subtraction (Period Engineer, 2026-10-21; code held uncommitted under the gate)

Code (held, not committed, nothing applied, no stage rerun): `pipeline/src/scrooner_pipeline/normalizer/derived.py` (+89 lines), `pipeline/tests/unit/test_derived.py` (21 -> 58 tests; full unit suite 1,303 passed, 9 skipped; 9 of 9 mutants killed, the last after adding a test). Census: read-only, one connection, `statement_timeout` 60s, `default_transaction_read_only=on`, chunks of 250 companies (ratio-unit sub-query in chunks of 50 after a 250-chunk timeout), 5,283 companies, 2,416 s, client connections 9-12 throughout, no query over 10 minutes. Evidence class: counts are DATA-INFERRED (our tables); the MSFT, AAPL, KLAC and V values are FILING-CHECKED by data-team/35 and the top-1000 shards (locators below).

## 1. Root cause (code, FILING-CHECKED against the repository)
`normalizer/derived.py` has **no additive allowlist and no non-additive guard**. Both stages subtract every authoritative duration fact that has the inputs:
- `derive_q4_for_company`: groups every `(concept_id, unit_id, fiscal_year)` from `_load_quarterly_candidates` (HEAD lines 135-152; all authoritative duration facts, any tag, any unit), then `_q4_value` returns `fy_value - first_three` for anything not in `average_ids` (HEAD lines 85-94, called at 362-367). The only exception, added 2026-10-17 (commit 7825b47), is tags `LIKE 'WeightedAverage%'`; its comment says "EPS and other non-additive tags are deliberately unchanged".
- `derive_interim_quarters_for_company`: `half - q1` and `three_q - half` for every non-average concept (HEAD lines 659-662, 697-701).
- The FY - 9M fallback (commit 07a463a, 2026-09-27) widened the reach: from 2020 the number of derived Q4 rows on mapped EPS/DPS tags roughly doubles (table 2c).
- An allowlist exists only in the dry-run module `normalizer/q4_vintage_dryrun.py` (`additive_concept_ids` is a caller parameter, line 697) and in the certification model (`certification/model.py` `ADDITIVE_FLOWS`, `PER_SHARE`); the production deriver never consults either.
So EPS is not derived through a fallback or a missing branch of a guard: there was never a guard. The Normalizer works on raw tags, so a guard there cannot use canonical concept names; it has to be structural (unit, tag).

## 2. Impact (since 2015-01-01, period end; derived = `core.fact.is_derived`)
Selection: derived facts whose unit contains `/` or is `pure`, or whose tag matches `Per(Basic|Diluted|BasicAndDiluted)?Share|PerOutstanding[A-Za-z]*Unit|PerUnit`. 268,909 rows at 4,830 companies; 268,677 authoritative (shown). Top 1000 (1,014 ids from `doc/data-moat/team/top1000/shards.csv`): 59,880 rows at 997 companies.

### 2a. By family and period (rows; almost all authoritative)
| Family | Top 1000 Q2 / Q3 / Q4 / total | All companies Q2 / Q3 / Q4 / total |
|---|---|---|
| Basic EPS (any per-basic-share tag) | 76 / 78 / 7,322 / 7,476 | 410 / 484 / 31,882 / 32,776 |
| Diluted EPS (any per-diluted-share tag) | 82 / 77 / 6,948 / 7,107 | 360 / 408 / 27,022 / 27,790 |
| Dividends / distributions per share or unit (incl. dividend-rate `pure` tags) | 826 / 897 / 5,121 / 6,844 | 4,147 / 4,466 / 14,742 / 23,355 |
| Other per-share (option exercise prices, grant-date fair values, antidilutive share counts) | 5,843 / 5,890 / 9,940 / 21,673 | 31,036 / 31,196 / 43,379 / 105,611 |
| Ratios in `pure` (effective tax rate, statutory rate, volatility, segment counts) | 3,652 / 3,708 / 9,180 / 16,540 | 21,567 / 21,201 / 35,689 / 78,457 |
| Other ratio units (usd/bbl etc.) | 7 | 23 |
Plus 262 (top 1000) / 897 (all) rows on periods labelled Q1 or unlabelled. Only 69 rows (all companies) sit in a cell that also has a filed fact.

### 2b. The mapped tags that feed the product
| Tag family (concept_mapping) | Top 1000 rows (companies) | All rows (companies) |
|---|---|---|
| EarningsPerShareBasic | 5,303 (925) | 22,154 (4,287) |
| EarningsPerShareDiluted (+ LP unit tag) | 5,206 (931) | 21,184 (4,262) |
| EarningsPerShareBasicAndDiluted | 219 (90) | 4,233 (1,311) |
| CommonStockDividendsPerShareDeclared / CashPaid | 4,859 (580) | 11,955 (1,486) |

### 2c. Mapped EPS/DPS derived Q4 rows by year (all / top 1000)
2015 2,183/628; 2016 2,343/633; 2017 2,470/648; 2018 2,702/700; 2019 2,942/729; 2020 4,494/1,088; 2021 6,967/1,821; 2022 7,128/1,944; 2023 7,599/2,030; 2024 8,097/2,100; 2025 8,841/2,227; 2026 1,265/376.

### 2d. Displayed canonical cells sourced from a derived per-share fact
| Concept | Top 1000 (Q4 / Q2+Q3 / other) | All (Q4 / Q2+Q3 / other) |
|---|---|---|
| diluted_eps and diluted_eps_resolved | 5,263+5,260 / 38+37 / 15+15 | 23,876+23,867 / 303+301 / 53+52 |
| basic_eps and basic_eps_resolved | 5,354+5,354 / 31+30 / 17+17 | 24,545+24,539 / 289+286 / 54+54 |
| dividends_per_share and _resolved | 3,914+3,881 / 379+379 / 10+10 | 9,288+9,223 / 1,395+1,395 / 29+29 |
119,578 canonical rows in total.

### 2e. Stored metric rows whose `source_fact_ids` include a derived per-share fact
| Metric | Top 1000 | All |
|---|---|---|
| trailing_pe (TTM) | 874 | 3,334 |
| dividend_yield (TTM) | 420 | 938 |
| eps_growth_yoy / 3y / 5y / 10y | 4,973 / 3,605 / 3,276 / 2,481 | 19,605 / 12,763 / 10,886 / 6,738 |
| dps_growth_yoy / 3y | 3,739 / 3,399 | 8,725 / 7,746 |
| payout_ratio | 7,289 | 29,391 |
| eps_dilution_spread | 5,464 | 25,548 |
Not found in any source list: peg_ratio, piotroski_f_score, total_shareholder_yield, dividend_growth_streak_years, per-share balance metrics (they do not carry EPS/DPS fact ids; peg and Piotroski declare no registry inputs, see 41's companion note, so their dependence cannot be proven from the registry).
125,674 metric rows in total.

## 3. Real cases (stored inputs, core.fact ids)
| Case | Arithmetic the deriver did | Stored | Filed / correct | Evidence |
|---|---|---|---|---|
| MSFT Q4 FY26 diluted EPS | 17.95 - (3.72 + 5.16 + 4.27) | 4.80 (341935) | 4.81 | FILING-CHECKED: 8-K 0001193125-26-323632 Ex. 99.1 (data-team/35) |
| AAPL Q4 FY25 diluted EPS | 7.46 - (2.40 + 1.65 + 1.57) | 1.84 (341384) | 1.85 | FILING-CHECKED: 8-K 0000320193-25-000077 Ex. 99.1 |
| KLAC Q4 FY26 diluted EPS | post-split FY 3.66 - pre-split 8.47 + 8.68 + 9.12 | -22.61 (77564004) | 1.04 | FILING-CHECKED: 8-K 0000319201-26-000024 (status.md S006) |
| KLAC Q4 FY26 DPS | 0.8 - 3 x 1.9 | -4.9 (77563969) | n/a | DATA-INFERRED (same split mix) |
| V Q4 FY25 DPS | FY context carries the quarterly 0.59 (10-K 0001403161-25-000089 R8); 0.59 - 3 x 0.59 | -1.18 (78616210, also CashPaid 78616208; FY24 -1.04) | 0.59 quarterly | FILING-CHECKED (S002); note the H1 and 9M contexts also carry 0.59 |
| LEA Q4 FY25 DPS | FY context 0.77 (10-K 0000842162-26-000011) - 3 x 0.77 | -1.54 (77999241; FY24 too) | 0.77 quarterly | DATA-INFERRED |
| DIS Q4 FY25 interest expense | FY filed NEGATIVE -1,812M (10-K 0001744489-25-000155), quarters positive 487 / 471 / 438M | -3,208M (79297939) | about +416M | DATA-INFERRED (companyfacts confirms the sign, S007). **Additive concept: NOT fixed by this change** |
Derived negative DPS (authoritative): 210 rows in the top 1000, 513 in all.
Two side findings: (1) V's and LEA's stored **FY** DPS is itself wrong (a quarterly amount on the annual context), so a "use the filed FY value" rule needs a guard too; (2) KLAC's FY EPS (post-split) and its 10-Q quarters (pre-split) are on different bases in stored history, the split-adjustment family (fix register 8).

## 4. The change as implemented (held)
- `is_ratio_unit(unit)` (`/` in unit or `pure`) and `is_per_share_tag(tag)`; `_load_non_additive(conn)` returns the ratio-unit ids and per-share concept ids (global lookups).
- `derive_q4_for_company`: for such a (concept, unit) no Q4 is derived (stat `non_additive_not_derived`); a filed "Q4" equal to the FY value is still demoted as before but not replaced (`demoted_full_year_q4_not_replaced`); filed discrete Q4 facts are untouched.
- `derive_interim_quarters_for_company`: no Q2/Q3 for such groups.
- Weighted-average share counts keep their founder-adopted window-weight method; additive flows are unchanged.
- `NON_ADDITIVE_UNAVAILABLE_REASON = "not filed separately (per-share values are not derived)"` for consumers.
- Existing derived rows are deliberately NOT retired by the stage (that would be an unreviewed nightly shared-table write).
Tests: real fixtures for MSFT, AAPL, KLAC (EPS and DPS), V, LEA; each test first proves the unguarded arithmetic reproduces the wrong stored value, then that nothing is derived. Plus additive-neighbour, pure unit, per-share tag filed in USD, chain path, demotion, filed Q4 left alone, interim, classifiers and loader. Mutants killed: guard removed, units-only, tags-only, interim guard removed, demotion removed, `pure` dropped, `PerUnit` dropped, Basic/Diluted share dropped, guard moved behind the inputs check (counter now pinned).

## 5. What the product would show after a no-derivation rule (code reading of mapper/price_metrics.py, mapper/ttm.py; DATA-INFERRED)
- Q4 EPS / DPS cells: blank with the reason above, unless a discrete Q4 is filed in XBRL (rare; 10-K quarterly tables). FY EPS from the 10-K stays.
- **TTM EPS** (`price_metrics.py` lines 110-125, sum of four quarters from canonical_fact): every window contains a Q4, so TTM EPS becomes unavailable for nearly every company.
- **Trailing P/E**: the existing fallback (lines 367-383) already uses market cap / TTM net income when TTM EPS is missing, so P/E stays populated where net income TTM exists (net income is additive; derived Q4 net income remains, subject to the vintage/sign issues of the additive family). Its basis changes: current shares x price over net income to parent, versus price over EPS (EPS uses weighted shares and income to common after preferred dividends).
- **Anchor regression that must be fixed first**: lines 289-298 anchor ALL six TTM concepts on the latest diluted_eps quarter. With no Q4 EPS, a company that just filed its 10-K anchors on Q3, so TTM revenue, CFO and capex go one quarter stale for about three months each year. `price_metrics.py` must anchor on the latest revenue/net-income quarter (or each concept on its own) before or with this change; derived.py must not ship alone.
- **Dividend yield** (TTM DPS sum): becomes unavailable for most payers (938 rows today use a derived DPS).
- **EPS growth YoY** (`ttm.py` same fiscal_period): Q4 rows disappear (both sides derived); Q1-Q3 and FY rows unchanged; 3/5/10y CAGRs on FY unchanged. **DPS growth**, **payout ratio**, **eps_dilution_spread**: Q4 rows disappear, FY rows unchanged.
- **Gap labelling**: `sanity/period_completeness.py` lines 263 and 285 would label every blank Q4 EPS `q4_not_derived` / `pipeline_bug`. It needs a new `gap_cause` (a `period_gap` CHECK value, so a migration) meaning "per-share, not filed separately".

## 6. TTM proposal (for decision, not adopted)
Per data-team/14 ("Do not sum four EPS values as an exact universal TTM EPS method"):
1. Trailing P/E = market cap / TTM net income attributable to common shareholders (net income minus preferred dividends where filed); label the basis.
2. TTM EPS is displayed only as "FY EPS (filed)" for the latest fiscal year with its period end; a quarterly-anchored TTM EPS is unavailable with the reason. Optional: when all four quarters are FILED (no derived), show their sum labelled "sum of four reported quarters", never as exact.
3. Dividend yield = latest filed FY DPS / price, guarded by FY DPS >= each filed quarter of that year (catches V, LEA), or TTM common dividends paid (cash flow, additive) / market cap; pick one.
4. EPS growth: FY over FY and same-quarter Q1-Q3 only.

## 7. Retirement list for the later reviewed dry-run (no write done)
Files (scratchpad, may be wiped; reproducible from the selection in section 2):
- `/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/derived_per_share_fact_ids.csv` (268,909 rows: fact id, company, top1000 flag, tag, unit, period, authority, value, family, filed-in-same-cell)
- `.../scratchpad/dependent_canonical_fact_ids.csv` (119,578), `.../scratchpad/dependent_metric_value_ids.csv` (125,674), `.../scratchpad/census_summary.json`; script `.../scratchpad/census.py`.
Suggested order: price_metrics anchor fix and period_gap reason first; then demote (`is_authoritative=false`, never delete) the derived rows; then re-resolve canonical facts and recompute metrics for affected companies.

## 8. Needs the Standardization Lead (or root-cause pass)
1. Whether dividends declared per share are excluded too: within a split-free year they are arithmetically additive (declared amounts add up); the observed failures (V, LEA, KLAC) are context mis-tags and split mixes, not non-additivity. The founder's instruction says never derive; the change follows it.
2. Scope of "ratio": the guard also stops deriving effective tax rate, option prices and fair values, segment counts (`pure`) and antidilutive share counts (tag contains EarningsPerShare). None should be derived; confirm none is a displayed quarterly value someone relies on.
3. Share counts other than weighted averages (antidilutive, incremental dilutive shares) and the window-weight approximation for weighted averages: still derived; keep or block.
4. TTM EPS / P/E / dividend-yield definitions in section 6.
5. The FY-equals-Q4 demotion for per-share (kept from the old behaviour): can misfire on very small EPS where Q1-Q3 net close to zero; it only blanks a value.
6. DIS-type sign conflicts between the 10-K and 10-Qs on additive flows: a separate guard (FY and quarter signs disagree -> blocked), not covered here.
