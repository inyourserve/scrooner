# WO-REVIEW: Period Engineer review of WO-2 (doc 47) before execution (2026-10-22)

Role: Period Engineer (data-team/14). Objective: review WO-2 before anyone executes it. That means: is each item doable and are its inputs present; a complete per-cell share-basis design; the price_metrics release unit that must ship with "no derived Q4 EPS/DPS"; the order of my days; the one-time-solution test; and a sign-off. Scope: planning only. No commits, no DB reads or writes (none were needed; every count below is quoted from the cited report). The held code `normalizer/derived.py` and `tests/unit/test_derived.py` stays uncommitted.

Evidence labels: FILING-CHECKED (an SEC document was opened, by me or by the cited report, with its locator), DATA-INFERRED (our tables or code), ASSUMED. Code claims come from reading HEAD plus the working tree on 2026-10-22 (line numbers are given).

Read: data-team 20, 21, 22, 14, 03, 36; strategy 42, 46, 47; team R5, S5; code `corporate_actions/stock_splits.py`, `mapper/conflict_resolution.py` (lines 60-112, 1167-1370), `mapper/dedup_majority_resolver.py` (lines 42-93), `mapper/price_metrics.py`, `mapper/ttm.py` (grep), `sanity/period_completeness.py` (lines 130-290), `certification/splits.py` (working tree), `certification/model.py` (grep), `normalizer/derived.py` (HEAD and the held diff), migrations 0004, 0065, 0090; doc 53 migration ledger; git log on derived.py, price_metrics.py, period_completeness.py, stock_splits.py, q4_vintage_dryrun.py.

---

## 1. WO-2 item by item: is it doable, and what input is missing

| WO-2 item | Doable? | Inputs missing / conflicts found | Owner dependency |
|---|---|---|---|
| 1a W1: TTM EBITDA/FCF need four consecutive quarters | Yes, small. `expanded_metrics._ebitda_ttm/_fcf_ttm` (S5 W1, lines 145-206) sum the latest 4 non-null rows. Fix: contiguous date windows that end at the company's current quarter (rule B8) | None. MasTec company 225 is the fixture (DATA-INFERRED, exact arithmetic) | none |
| 1b W2: age guard per TTM concept | Yes, small. Anchor every TTM on the company's current quarter (the latest periodic-filing period end), not on the concept's own latest quarter (B9). Reuse `common/staleness.py` thresholds, do not invent new ones | We need one definition of "current quarter" shared with `cell_state` (WO-1.5). Today price_metrics uses EPS-or-revenue, expanded uses each concept's own anchor, staleness.py uses `core.filing` latest period_of_report | Data Engineer (staleness.py owner) agrees on one function |
| 1c W5: repair broken fiscal labels (24 cos) | Partly. The root cause of the labels is NOT diagnosed (S5: DATA-INFERRED from `core.period` for companies 171 and 1171). Rewriting `core.period.fiscal_year/fiscal_period` is a Normalizer write to a shared table that the statements page also reads | Missing: a cause (periods.py fiscal-year assignment vs `DocumentFiscalYearFocus`). Recommendation: do not "repair labels" one by one. Make every TTM, growth and Q4 window date-based (B3/B8), so a wrong label cannot change a value. Fix `periods.py` afterwards, as a separate reviewed change | Normalizer is my lane for derived.py only; periods.py edit needs Data Chief lane check (doc 53) |
| 2a per-share date pairing (W10, book value / net cash per share) | Yes | **Owner conflict:** WO-1.7 gives the same W10 cover-date anchor to the Data Engineer. One owner only. My proposal: I write the pairing rule with 10 FILING-CHECKED cases (it is period alignment); the Data Engineer implements it in the metric code if that is where WO-1.7 already sits. The Chief decides | Data Chief |
| 2b YTD route into price and expanded metrics (97 cells) | Yes, for additive concepts only. `ttm._ttm_from_ytd` computes ytd + prior FY - prior ytd. That is subtraction, so it must never be wired for EPS, DPS or any ratio. Allowlist guard required in the wiring | none | none |
| 2c calendar-aware windows (COST, XOM: 181 cells) | COST/KR/ACI: yes (B3 rule, FILING-CHECKED Costco 167-day 24-week YTD, R5). **XOM is not a calendar case.** It is a successor CIK (8-K12B 0001193125-26-291990, S5), so it belongs under item 5 | Split the 181 into calendar vs successor before the cells are claimed | Company Master / Data Engineer for XOM |
| 3a derivation allowlist by canonical concept | Doable, with a **boundary correction**. `derived.py` is in the Normalizer, and the Normalizer must not map concepts (pipeline/CLAUDE.md). So the canonical-concept allowlist is enforced at the Mapper: a derived source fact is eligible for `canonical_fact` only if its concept is in the approved class A/B list (R5 section 6; `certification/model.py ADDITIVE_FLOWS` already exists). The Normalizer keeps its structural guard (ratio unit, per-share tag: the held code). It also gains a form gate (see 3d) | Class A/B list needs Standardization Lead approval. Open questions from doc 42 section 8 (antidilutive/incremental share counts; window-weighted weighted averages) | Standardization Lead |
| 3b never derive Q4 EPS/DPS | Done in held code (derived.py +89 lines, 58 tests, 9 of 9 mutants killed, doc 42). **Cannot ship alone**: see section 3 | dividend-yield and TTM-EPS definitions (doc 42 section 6) | Standardization Lead; Release Manager |
| 3c filed Q4 from Item 302(a) notes for FY ending before 2021-08-09 | Doable. Rule FILING-CHECKED (Release 33-10890, R5). Reach: 388 of 515 top-1000 FY2015 10-Ks tag a 3-month Q4 revenue, and 407 of 540 tag Q4 diluted EPS (FSDS, DATA-INFERRED) | **Missing input:** whether those note facts are already in `core.fact` and authoritative (R5 step 1, NOT_RUN). Rule B5: when filed and derived disagree beyond rounding, publish neither (SUN x1000 note, SWK/CB/Ford shifted contexts) | Verifier sample of 20 incl. SUN, MPLX |
| 3d (added) periodic-form gate on derivation inputs | Needed, not in WO-2. `derived.py::_load_quarterly_candidates` (lines 192-209) takes any authoritative duration fact from any form. Example: JPM Q4 net income was derived from a DEF 14A FY (fact 182608846, data-team/36 item 2), and WTRG Q4 CFO from an 8-K FY of another entity (W3). Use the same periodic-form list as WO-1.4 (one constant in `common/`) | none | Data Engineer (shared constant) |
| 4 restatement-basis rule (MSFT growth, HON W4) | Doable; it is the largest item. `normalizer/q4_vintage_dryrun.py` (commit 324d514) already classifies same-vintage pairs with no writes; production needs B1 (same-vintage pairs) and B2 (block when the FY filing reports discontinued ops and the 9M predates the disposal). The MSFT case is a metric-level R-BASIS problem (growth must compare FYs from the same vintage), not only derivation | **Missing decision:** which basis the display series uses (latest basis with one-vintage pairs vs as filed). R5 section 8 and doc 36 item 1 leave it open. Founder or accountant, before any Q4 backfill (see section 5) | Founder / accounting reviewer; Standardization Lead |
| 5 history horizon states and successor links | My part is doable: horizon reason codes with first-fact evidence (S5 4a: IPO 530, spin 168, successor 96 + 74). The links need old-CIK ingestion (XOM 0000034088 is not in `core.company`) | Collector/bootstrap of predecessor CIKs; FILING-CHECKED link per company (8-K12B/G3); the `cell_state` interface (WO-1.5) to receive the states | Data Engineer (ingestion, cell_state), Verifier |
| (missing from WO-2) **split basis, R-SPLIT-BASIS** | Gate B lists "NVDA ~216 cells corrected or hidden", but no work order owns the mechanism. Add it to WO-2 as item 6 (design in section 2) | none for the design; the migration needs a number (section 3.5) | Data Engineer applies migrations; Verifier |

Acceptance in WO-2 ("Verifier samples MasTec, AAL, HON clean") is too narrow. Add: NVDA, AAPL, GOOG, WMT, TSLA, KLAC (split basis); MSFT FY2016 growth (R-BASIS); V and LEA DPS (rate-on-YTD); JPM Q4 net income (form gate). Each sample must also count correct values hidden by mistake (doc 47 rule 1).

---

## 2. Per-cell share basis: the complete design (R-SPLIT-BASIS as a mechanism)

### 2.1 What is wrong today (code, FILING-CHECKED cases from data-team/36)
1. Detection reads `instant` contexts only (`stock_splits.py` line 116). NVDA's 10-for-1 is filed only on duration contexts, so 2024 is missing (0001045810-24-000264 R8).
2. Disclosures are merged within a fixed 45-day window (line 99). NVDA 4:1 (46 days apart) and GOOG 20:1 (2022-02-01 announced, 2022-07-15 effective, 164 days apart) are counted twice, so GOOG 2015-2021 EPS is divided by 400.
3. The adjustment tests `split effective_date > period end_date` (line 308). It should test the filing date of the source. WMT FY2024 EPS was filed after the 2024-02-23 split, already adjusted, and was divided by 3 again (0000104169-24-000056 R3).
4. Share counts are never re-based (`RETROACTIVE_ADJUSTMENT_CONCEPTS`, line 210). AAPL has 45 share cells on the pre-2020 basis (0000320193-20-000096 R8), and TSLA, AMZN, AVGO, GOOG and WMT have the same problem.
5. Insert-only: `on conflict do nothing` plus the `already_resolved` skip (line 303). A cell filled earlier with an unadjusted value is never corrected (AAPL FY2018 diluted EPS 11.91 vs 2.98 filed).
6. **Five writers** fill the same `*_resolved` per-share concepts, each with its own split heuristic: retroactive adjustment, baseline passthrough, conflict fill, `resolve_split_like_conflicts` (a 1.5x-20x ratio band that keeps the highest fact_id, conflict_resolution.py lines 1177-1220), and `dedup_majority_resolver._split_reconcile`. Every patch so far has added a writer, not removed one.
7. Consumers read the as-filed base concepts across a split. `price_metrics.TTM_CONCEPTS` reads `diluted_eps` and `dividends_per_share` (lines 53-60). `ttm.py` growth reads `diluted_eps` and `dividends_per_share` (lines 43-60). A TTM or YoY that spans a split mixes bases (KLAC Q4 -22.61). DATA-INFERRED, code.

### 2.2 Principle
A share basis belongs to a **filing**, not to a period. Every number in one filing is on that filing's own share basis. The factor that converts a cell to today's basis is therefore a property of the cell's **source filing**. It is computed once per filing from a single event table and checked against what the filings themselves report. One writer produces every current-basis cell from it, with full recompute and no insert-only shortcut.

### 2.3 Where the factor lives (new tables; one migration, number claimed per 3.5)
- `analytics.split_event` replaces the role of `company_stock_split`. That table stays as the raw disclosure log, renamed in meaning only, so no reader breaks. One row per **economic event**: `company_id, ratio, basis_date` (the first date from which filings report on the new basis), `evidence` (jsonb: disclosure fact ids with context type and dates; filed-pair ids; share-step filing pair), `evidence_kinds` (subset of {ratio_fact, filed_pair, share_step}), `status` (`confirmed` | `review`), `detector_version`. Unique key `(company_id, ratio, basis_date)`.
- `analytics.filing_share_basis`: one row per (company, periodic filing): `filing_id, filing_date, factor_to_current` (product of the ratios of confirmed events with `basis_date > filing_date`), `event_ids`, `observed_factor` (from that filing's own share counts, see 2.6), `status` (`consistent` | `date_only` | `conflict` | `review`), `basis_version`.
- The cell layer is the existing `*_resolved` per-share concepts in `canonical_fact` (the app already reads them through `statement_line`). The writer adds the factor and event ids to `source_fact_ids` lineage as today. The full per-cell record goes in `analytics.share_basis_cell` (company, concept, period, candidate source facts with as-filed values, chosen source, factor, current value, status, reason, basis_version). The base concepts (`diluted_eps`, `basic_eps`, `dividends_per_share`, `shares_outstanding`, weighted averages) stay **as filed**. That is the point-in-time series; nothing in it changes.

### 2.4 How an event is detected (all evidence from filings; no vendor)
Three independent evidence kinds:
1. **ratio_fact**: `StockholdersEquityNoteStockSplitConversionRatio(1)` on **instant and duration** contexts. The existing `_classify` scale rules are kept. Context end and disclosed dates become candidate dates.
2. **filed_pair**: the same period and tag filed in two periodic filings whose values differ by a clean ratio k (2, 3, 4, 5, 10, 15, 20... or 1/k for reverse) within decimals-aware rounding. Example: KLAC FY2025 EPS 30.37 vs 3.04 in the next 10-K. This is also how reverse splits that the ratio tag misses are found (BURU, GURE, NCRA, SVMB, ledger 2026-10-18).
3. **share_step**: in the share-count series ordered by **filing date** (cover `dei:EntityCommonStockSharesOutstanding` and balance-sheet shares, median per filing), one clean step of ratio k between two consecutive filings. The `certification/splits.py::_shares_by_filing` idea, reimplemented, not imported (see 2.9).

An event is `confirmed` when at least two kinds agree on ratio and date range. With only one kind it is `review`. `review` events never re-base anything; every cell they would touch gets status `basis_review` and is shown as unavailable with the reason "share basis under review" (suppress before guessing). `basis_date` = the filing date of the first filing observed on the new basis (share_step or filed_pair). It is bounded below by the earliest disclosure date. With no observation, it is the latest disclosed date (the effective date; the WMT/NVDA/AAPL filings after the effective date are adjusted, FILING-CHECKED in data-team/36). The general SAB Topic 4C rule (retroactive presentation when a split happens after period end and before issuance) is ASSUMED and is not relied on: each filing's basis is observed where possible (2.6).

### 2.5 How a split recorded twice is detected
Identity is (ratio, basis boundary), not a day window. Two same-ratio disclosures are one event when the filing-dated share series shows at most one step of that ratio between them, and no filed pair spans them with ratio k^2. GOOG: FY2020 EPS filed 59.15 (2021) and re-presented 2.96 (FY2022 10-K) gives a pair ratio of 20, not 400, so the 2022-02-01 and 2022-07-15 rows collapse into one event. Belt and braces: a **company invariant** requires every filed pair between filings F1 and F2 to equal `factor(F1)/factor(F2)` within rounding. Any violation sets every per-share cell of that company to `basis_review` (hidden with reason) until resolved. A double count can then never be shown, even by a detector bug.

### 2.6 How the factor is computed from source-filing date, and checked
`factor_to_current(F) = product(ratio for confirmed events with basis_date > F.filing_date)`. Observed check per filing: compare F's cover share count with the next filing on the current basis. The expected ratio is `factor(F)`, and clean-ratio tolerance absorbs normal issuance and buybacks. `consistent` = observed agrees with predicted. `date_only` = F has no share count and is more than 30 days from any basis_date. `conflict` or `review` = disagreement, or a filing date within 30 days of a basis_date with no share count. Only `consistent` and `date_only` filings feed shown values.

### 2.7 How share counts are included
Current value = as-filed / factor for per-share (EPS basic, diluted and BasicAndDiluted, continuing-ops per-share tags if mapped, DPS). Current value = as-filed x factor for share counts (`shares_outstanding`, weighted-average basic and diluted). Downstream metrics (book value per share, P/E, dividend yield, payout, EPS and DPS growth, diluted-share CAGR, market-cap share base) read only the current-basis layer. Point-in-time uses read the as-filed base. Award prices, option fair values and antidilutive counts are not displayed and are excluded.

### 2.8 Choosing the cell value when a period has several filed copies
Each candidate copy (periodic forms only) is converted with its own filing's factor. If all agree within decimals-aware rounding, the value comes from the **latest** filing, which needs the least arithmetic (a re-presented post-split value is filed evidence and beats our division). If they disagree, the cell is a real restatement or a factor error, so status `basis_conflict`, hidden with reason. Route it to R-BASIS; never pick by highest fact_id. This replaces `resolve_split_like_conflicts` and `_split_reconcile` for these concepts: their ratio-band guesses become evidenced conversions.

### 2.9 Single writer, backfill and nightly
- One module `corporate_actions/share_basis.py` is the **only** writer of `diluted_eps_resolved`, `basic_eps_resolved`, `dividends_per_share_resolved`, `shares_outstanding_resolved` and the weighted-average resolved twins. These concepts come out of `CONFLICT_FILL_TARGETS` baseline/conflict/split-like passes and out of `dedup_majority_resolver.SAFE_CONCEPTS`. A unit test asserts that exactly one registered writer exists per resolved concept (mutation: re-add one, and the test fails).
- Per company it is a full deterministic recompute (events, then filing basis, then cells). It upserts changed cells. Each replaced or removed row is copied first to an archive table (`analytics.canonical_fact_retired`: old row, reason code, run id, basis_version) in the same transaction. Nothing is lost, and rollback re-inserts from the archive.
- Nightly: runs after `resolve-facts` and before conflict fills, price/ttm/expanded metrics. It recomputes a company when (a) it has a new periodic filing, or (b) its **event-set hash** changes. A new split re-bases that company's whole history in one pass and triggers its metric recompute. Bounded by the existing per-stage cap; own `statement_timeout`; chunked writes.
- Backfill: one dry-run over the 986, then the population. Output: per cell old value, new value and class (unchanged / re-based / was-double-divided / was-unadjusted / share-count-rebased / now-hidden-with-reason). Verifier samples about 30 filings per class with zero wrong rows, plus the count of correct values newly hidden. Then a separate first live run (doc 47 rule 1).
- Verification is non-circular. The production detector and the certification I9 (`certification/splits.py`, working tree, another owner) are kept as **separate implementations**. The production gate is the filed-pair invariant (2.5), which uses values the company filed, not our factor.

### 2.10 Existing rows
- `core.fact` derived per-share rows (268,909; 59,880 top-1000; doc 42 section 7): demoted `is_authoritative=false` after a reviewed dry-run. Never deleted (the `_retire_derived` pattern, derived.py lines 154-189).
- `canonical_fact` `*_resolved` per-share rows (119,578 dependent rows from derived facts, plus every split-touched row): replaced or archived by the writer's first live run. Reviewed dry-run first. Never deleted without the archive copy.
- `analytics.company_stock_split`: kept as the disclosure log, read by the detector, no longer read by any adjuster.
- Decision for the Release Manager or Chief: I read "never delete" as "never lose": archive-then-replace in one transaction. If it is read literally (rows must stay in `canonical_fact`), the alternative is a `retired_at` column that every reader (app, backend, screener snapshot) must filter. That is a much larger change and a riskier one.

### 2.11 Why this removes the class for all 986 at once (one rule run over every company, not per-company patches)
| Case | Cause | Removed by |
|---|---|---|
| NVDA 10:1 missing (~216 cells) | duration-only ratio fact | 2.4 kinds 1-3 (duration contexts + share step + filed pairs) |
| NVDA 4:1 x2, GOOG 20:1 x2 (EPS / 400) | 45-day window | 2.5 event identity + filed-pair invariant |
| WMT FY2024 divided again | period-end test | 2.6 factor by source filing date (filed after split, factor 1) |
| AAPL 45 shares, TSLA, AMZN, AVGO, GOOG, WMT share series | shares not re-based | 2.7 share counts multiplied |
| AAPL FY2018 11.91, TSLA Q3 2019 /5 not /15 | insert-only, stale fills | 2.9 full recompute + upsert with archive |
| KLAC Q4 -22.61, TTM or YoY across a split | consumers read as-filed series | 2.7 consumers read current basis; no derived per-share (section 3) |
| 12 companies with same-ratio rows 46-120 days apart; 156 with duration-only ratio facts (data-team/36, DATA-INFERRED) | same two detector defects | the same rule, population-wide; each moves to `confirmed` or to hidden-with-reason |
Expected cells changed: the 486 `share_basis_mismatch` findings (S001/S002, 94% precision, data-team/36) plus the recall misses. The population count is NOT_RUN and comes from the dry-run.

---

## 3. The release unit that must ship WITH "no derived Q4 EPS/DPS" (RU-1)

Ship all of the following together, in one Release Manager commit; the first live run is separate:

3.1 `normalizer/derived.py` (held): structural non-additive guard (done), **plus** a periodic-form gate on the input loaders (10-K, 10-Q, 10-KT and their amendments only; one shared constant with WO-1.4). Tests: JPM DEF 14A FY (fact 182608846 pattern) and WTRG 8-K FY produce no derived Q4.

3.2 `mapper/price_metrics.py` anchor (lines 287-299 today: `eps_anchor = _latest_quarter(diluted_eps_q)`, `anchor = eps_anchor or revenue_anchor`). Without derived Q4 EPS, a company that just filed its 10-K anchors on Q3. TTM revenue, net income, CFO and capex then go a quarter stale for about three months a year. Change:
- `anchor` = the company's current quarter = the latest of the revenue and net-income quarters (the shared "current quarter" function of 1b). EPS never sets the anchor.
- TTM EPS: at a Q4 anchor, the TTM window is the fiscal year, so use the **filed FY diluted EPS** (exact, filed). At Q1-Q3 anchors TTM EPS is unavailable, and P/E uses the existing fallback market cap / TTM net income (lines 367-383 path, already used for multi-class filers), with that basis recorded in the row's lineage. No sum of quarterly EPS.
- Belt and braces: any per-share quarter whose source fact `is_derived` is treated as missing. RU-1 is then safe even before the retirement of old derived rows has run.
- Dividend yield (lines 415-422, sum of four quarterly DPS) would go blank for most payers. A definition is required before release. Option (a): filed FY DPS / price, guarded by FY DPS >= each filed quarter of that year (catches V, LEA; R-RATE-ON-YTD), labelled "FY". Option (b): TTM common dividends paid (cash flow, additive) / market cap, labelled "cash basis". The Standardization Lead decides (WO-5 DPS policy). Until then the metric is unavailable with a reason, which is honest but a visible regression on a locked V1 metric.
- Read the current-basis per-share layer once section 2 lands. Until then, use the base concept with the guard above.
- Tests (each mutation-checked): (i) 10-K just filed: Q4 revenue present, Q4 EPS absent, so TTM revenue includes Q4 (mutant: revert to the EPS anchor, and the test fails); (ii) Q4 anchor gives TTM EPS = filed FY EPS; (iii) Q2 anchor gives P/E = market cap / TTM NI with fact ids; (iv) a derived per-share quarter is never summed; (v) dividend-yield definition fixture (V FY2025 0.59 on the 12-month context must not pass the guard); (vi) stale EPS (KKR shape) still covered.

3.3 `mapper/ttm.py`: EPS and DPS growth Q4 rows lose both sides. The null reason must carry the input's cause (pass-through), not `missing:*`. Guard: the YTD route (`_ttm_from_ytd`) is never applied to a per-share or ratio concept (test).

3.4 `sanity/period_completeness.py` (lines 255-287, owned by lane F scrooner-2b per doc 53, so I contact them first): for a per-share base concept (`basic_eps`, `diluted_eps`, `dividends_per_share`), where a Q4 has FY present but no filed 3-month fact, or a Q2/Q3 has only YTD, return the new cause `per_share_not_filed_separately`. Its `finding_type` is `data_limit`, not `pipeline_bug`: there is no fact in the periodic filing's XBRL. It is not `legitimate_absence`, because "not in XBRL" is not "not in the filing" (18% rule) and the earnings release carries the value. Label: "Q4 EPS not reported separately; per-share values are not derived". Today the same cells are labelled `q4_not_derived` / `pipeline_bug` (doc 42 section 5), so the change also stops inflating the bug count.

3.5 Migration (period_gap CHECK constraint, migration 0090 pattern): add `per_share_not_filed_separately`. The same migration creates `analytics.canonical_fact_retired` (archive, 2.9), because RU-1's retirement of `*_resolved` Q4 per-share rows needs it too. **Claim: 0098** (doc 53 says "Next free number: 0098"; 0096 and 0097 are committed and not applied). The split tables (2.3) take the next number, **0099**. Both are claimed in doc 53 before the file is written. The Data Engineer's `cell_state`, `company_group` and `metric_template` work (WO-1.5/1.6) also needs numbers, so the Data Chief arbitrates if they claim first. I have not edited doc 53, because this is a review only.

3.6 Retirement (separate reviewed dry-run, then a first live run): demote the 268,909 derived per-share `core.fact` rows; archive and remove the derived-sourced `*_resolved` per-share Q4/Q2/Q3 rows; re-resolve; recompute price, ttm and expanded metrics for the affected companies. Impact list (doc 42 section 7): trailing_pe 3,334 rows, dividend_yield 938, eps_growth 50k across horizons, payout 29,391, eps_dilution_spread 25,548 (DATA-INFERRED). The dry-run reports, per metric, the rows that change value, the rows that become null with a reason, and the rows that stay. The Verifier samples each class.

Release order inside RU-1: code (3.1-3.4) and migration 0098 applied, then nightly running without new derived per-share rows (no visible change, because of the 3.2 guard), then the retirement dry-run reviewed, then the live retirement, then the recompute, then certify I8/I9 for the cohort.

---

## 4. Order of my work (working days from Gate A day 0; durations ASSUMED)

| Days | Period Engineer work | Runs in parallel with | Needs |
|---|---|---|---|
| 1-2 | RU-1 code and tests (3.1-3.4), migration 0098 file (not applied) | Data Engineer applies 0096/0097; Verifier measures certify precision | Standardization Lead: dividend-yield definition by day 3; lane F agreement on period_completeness |
| 3 | RU-1 dry-runs (metric impact, retirement list) | Verifier samples RU-1 | Release Manager commit after the Verifier passes |
| 4-11 | Split basis (section 2): detector v2 (1.5 d), filing basis (1 d), single writer and writer removal (1.5 d), archive/retire path (1 d), consumers to the current basis (0.5 d), tests and mutants (1 d), 986 dry-run (1 d) | Data Engineer: authority gate W3, identity, 0099 applied after commit; Verifier: split-class sample about day 11 | Data Engineer applies 0099; certification owner keeps I9 independent |
| 12-13 | W5 safety (date-contiguity check in TTM windows, labels cannot move values) + B2 discontinued-ops guard (stops W4 recurring); dry-runs | Verifier: MasTec, AAL, HON, NVDA, AAPL, GOOG, WMT, TSLA | none |
| W1/W2 (1.5 d) | **Hand to the Data Engineer** or another engineer, if Gate B must hold at day 10. Otherwise they are my days 12-13 and W5/B2 moves to 14-15 | | Data Chief decides |
| 14-18 | Same-vintage Q4 pairing B1 in production (from `q4_vintage_dryrun.py`) + R-BASIS for growth (MSFT FY2016 0.6845 vs 0.3777) | Standardization Lead/accountant: restatement display basis must be decided **before** day 14 | Founder / accountant |
| 19-21 | Calendar-aware windows B3/B4 (Costco 12/12/12/16, transitions); YTD route for additive concepts (97 cells) | Tag Mapper (none needed) | none |
| 22-23 | Mapper-side additive allowlist gate; Item 302(a) filed-Q4 audit + B5 cross-check | Verifier sample of 20 (SUN, MPLX) | Standardization Lead approves the A/B list |
| 24-25 | Horizon reason codes with first-fact evidence; predecessor-link spec | Data Engineer ingests old CIKs; Verifier opens 8-K12B/G3 | cell_state interface (WO-1.5) |
| (26-27) | W10 pairing rule + 10 filing-checked cases, only if the Chief assigns W10 to me | | Chief |

Totals: about 25 working days of Period Engineer time (27 with W10). Tier 0 period items are RU-1, split basis, W5/B2 guards and W1/W2: about 13.5 days. **Gate B at day 10 is not reachable for the split class by me alone.** Either the Chief accepts day 12-13 for the split class, or W1/W2 move to another engineer and the split class still lands about day 12. I do not propose an interim "hide 486 cells" write: it would be a second shared-table write on the same rows, which the real fix replaces two days later.

---

## 5. One-time-solution test: what would force a redo of backfilled periods, and the control

| Trigger that forces redo | Why it would | Control (built into the design) |
|---|---|---|
| Restatement display-basis decision made after the Q4 backfill | Every class-B Q4 derived on one vintage would be re-derived | Decide the basis before day 14. Each derived row also stores both candidate pairs' input fact ids and vintage (B6 lineage), so a later policy change re-selects instead of re-deriving |
| Allowlist change (a concept moves between class A/B/D) | Rows produced or retired again | The allowlist is enforced at the Mapper gate, not by creating or deleting Normalizer rows: a change is a filter flip plus a recompute |
| Another writer re-fills `*_resolved` per-share holes with as-filed values | Undoes the re-basing every night (the AAPL/KLAC history) | Single-writer test per resolved concept; the four other paths removed for these concepts |
| A split found later (new filing or detector fix) | Factor changes for the whole history of that company | Event-set hash per company triggers an automatic deterministic rebuild of that company only; versioned `basis_version`; nightly diff report; not a manual redo |
| Insert-only semantics anywhere in the path | Stale fills never refresh (ledger 2026-10-17, TSLA OI, JPM) | Upsert with archive; idempotency test (run twice gives zero diff) |
| Label-keyed windows built before W5 is fixed | Values change when labels are repaired | All windows date-based; labels never select inputs |
| Mixed-form inputs (DEF 14A, 8-K) | JPM/WTRG-style wrong derivations to redo | Periodic-form gate in derived.py and canonical (one constant) |
| Filed Item 302 notes found to disagree with derived Q4 after publication | Retroactive withdrawal | B5 check runs nightly as an invariant before publication; disagreement publishes neither |
| Dividend-yield / TTM EPS definition changed later | Metric-only recompute | Cheap by construction (metrics are recomputed from stored inputs); no period backfill touched |
| Verifier finds the detector wrong on a class after the live run | Mass rollback | Archive table gives a one-statement rollback per run id; the first live run is separate from the code release |

Test of the claim: after the backfill, re-running every stage on unchanged inputs must produce zero changed cells (idempotency), and a synthetic new split for one fixture company must change only that company's cells. Both are written as tests before the live run.

---

## 6. Sign-off

**SIGNED WITH CONDITIONS.**

Conditions:
1. Split basis (section 2) is added to WO-2 as item 6 with this design, and Gate B's date for the split class is set at day 12-13, or W1/W2 move to another engineer.
2. "No derived Q4 EPS/DPS" ships only as RU-1 (section 3): the price_metrics anchor, the derived per-share guard, the TTM EPS rule, the dividend-yield definition, the ttm.py pass-through, the new `per_share_not_filed_separately` cause and migration 0098, and the derived.py periodic-form gate, together, with their tests.
3. The Standardization Lead decides the dividend-yield / TTM EPS / P/E basis (doc 42 section 6) by day 3, and approves the additive A/B list before the Mapper gate.
4. The founder/accountant decides the restatement display basis before any Q4 backfill (day 14).
5. W10 has one owner (WO-1.7 vs WO-2.2) and XOM moves from "calendar" to "successor" (item 5).
6. The allowlist is enforced at the Mapper, not by concept mapping in the Normalizer (boundary).
7. "Never delete" is confirmed as archive-then-replace for `canonical_fact` (2.10).
8. Lane F (scrooner-2b) agrees to the period_completeness change; the certification owner keeps I9 as an independent implementation.

## Commands actually run
File reads listed at the top; `git log`/`git diff`/`git status` on the named modules; `grep`/`sed` on code and migrations; `python3 mind/mind.py search "split basis"` and `"Q4 EPS derivation"` (hints only; nothing relied on without the cited source). No DB connection was opened (NOT_RUN: every count is quoted from data-team/36, strategy 42, R5, S5). No SEC fetch. No commits.

## Not verified
- Population counts for the split class beyond S001/S002 (dry-run will measure).
- Whether Item 302 Q4 note facts are already authoritative in `core.fact` (R5 step 1).
- The W5 label root cause.
- That `analytics.canonical_fact_retired` does not duplicate an existing archive mechanism: the Data Engineer should confirm before the migration is written.
