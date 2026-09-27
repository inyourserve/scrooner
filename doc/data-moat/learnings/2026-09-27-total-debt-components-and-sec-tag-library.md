# 2026-09-27 — Total debt rebuilt from components; SEC Tag Library

## What prompted it

Triage of the 17,007 yfinance-ratio `major` findings. Grouping them by metric and ratio (ours ÷ yfinance) showed a few systemic causes, not 17k separate problems. The largest was debt: our debt-to-equity was a median **0.2×** yfinance's, and EV/EBITDA and EV/Sales (which both include debt) were also low.

## Root cause: `total_debt` summed whatever tags happened to exist

`total_debt` was a `sum`-mode concept over `LongTermDebt`, `ShortTermBorrowings`, `DebtCurrent` and `SecuredDebtCurrent`, plus a pair fallback to `LongTermDebtNoncurrent`+`LongTermDebtCurrent` that ran only when the primary was entirely absent.

- **Chevron, 2026-06-30:** it resolved to **$0.4B**, which was only `ShortTermBorrowings`. Its real $36.7B long-term debt sits under `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities`, a tag that wasn't mapped. Because the partial primary value existed, the fallback never ran.
- **Chevron, 2025-12-31: double count.** It added `ShortTermBorrowings` on top of `DebtCurrent`, which already contains it.
- The same pattern hit AT&T ($9.3B vs $144B), Oracle, Exxon, Verizon, RTX, GE and ConocoPhillips.

## Fix: `compute_total_debt()`, one tag per component, never summing overlapping tags

The rules live in `mapper/concept_fallback.py`. Each was checked against yfinance's Total Debt minus Capital Lease Obligations over 16,064 company-dates. yfinance is used only as the target; the stored value always comes from the filing.

1. Use the company's own stated total, `DebtLongtermAndShorttermCombinedAmount`, when filed.
2. Otherwise, long-term debt including current maturities plus short-term borrowings, with two exceptions:
   - When `LongTermDebt` equals `LongTermDebtNoncurrent`, the company uses it for the noncurrent part only (Diamondback, Cheniere), so current debt is added.
   - When short-term borrowings equal the current LTD portion, it's the same debt tagged twice (Boxlight), so it isn't added again.
3. Otherwise, noncurrent + `DebtCurrent`.
4. Otherwise, noncurrent + current LTD + short-term.
5. Otherwise, `DebtAndCapitalLeaseObligations`.

| vs yfinance ex-lease | Old | New |
|---|---|---|
| Within 5% | 42.5% | **50.0%** |
| Wrong (>20% off) | 12.4% | **7.5%** |
| Blank | 40.1% | 38.6% |

For non-financial companies alone, within-5% went from 45.2% to 53.6%.

### Candidate rules rejected on evidence

- **Summing individual instruments** (convertible notes, lines of credit, notes payable) for companies with none of the main tags: 946 right vs 1,184 wrong. A wrong number is worse than a blank.
- **Short-term borrowings alone as the total:** 69% wrong. T-Mobile's long-term debt is under a company-specific tag that Company Facts omits entirely. These periods are now blank instead of undercounted.
- **`LongTermDebt` + `DebtCurrent` with nothing else to go on** is a coin flip (Tesla). The company's own `DebtInstrumentCarryingAmount` is used as a tiebreaker: when it equals the sum within 1%, the sum is right 7/9 times and `LongTermDebt` alone 0/9. Without that confirmation, `LongTermDebt` alone wins (16 vs 10). The carrying amount is only a check, never stored.

### Left as-is

- **Financial companies** (Freddie Mac, Wells Fargo, Schwab, State Street, Rocket): yfinance's "debt" includes deposits, advances and securitization debt. That's a definition difference, the same as the existing bank carve-outs.
- **About 38% of company-dates are still blank.** These are mostly companies whose debt is under custom tags or instrument-level tags.

### Two-writer guard

`sanity/tag_investigator.resolve_company_tag_preferences()` copied raw `total_debt` into `total_debt_resolved` for every empty period, which would have put the wrong sums back into the blanks. `NO_BASELINE_COPY = {"total_debt"}` turns that off. The 37 companies with a verified `company_tag_preference` for debt are skipped by the new resolver, so their rows remain owned by the investigator.

## SEC Tag Library (migration 0077, `mapper/tag_library.py`)

This came from founder direction: tag → concept → metric → company, covering every tag and every company. Every debt gap above had been found by hand, and the tag behind Chevron's debt was sitting in `core.fact` the whole time.

| Table | Rows | Answers |
|---|---|---|
| `company_sec_tag` | ~2.04M | Every tag each company files: count, date range, latest value |
| `sec_tag_library` | ~12.4K | Tag → companies using it, mapping status (approved / provisional / company_preference / candidate / rejected / unmapped), concepts, metrics |
| `company_concept_lineage` | ~391K | Company × concept → the source tag behind our latest value; if missing, which mapped and candidate tags the company files |
| view `metric_company_tag_lineage` | — | Metric → company → concept → tag |

`scrooner-map gap-tags <concept>` ranks every tag filed by companies that are missing the concept. That turns gap discovery into a single query. Every result is still only a lead and needs a coexistence check before any `concept_mapping` change (doc 40).

The build is chunked (150 companies per delete+insert+commit, with a reconnect on pooler drop). It is built once and rebuilt manually (`.github/workflows/pipeline-tag-library.yml`, workflow_dispatch) after any concept_mapping or resolver change -- companies file the same tags period after period, so a schedule would mostly redo identical work. A full rebuild takes about an hour.

## Q4 derived from the 9-month YTD (same day)

The next systemic cause, found by triaging the margin/ROA yfinance majors: **2,002 active companies had no valid current TTM**. 916 of them were silently showing a TTM a median two-plus years old, because the "TTM-preferred" rule picks the latest *non-null* TTM row.

The largest single cause was a missing Q4. `normalizer/derived.py` derived Q4 only as FY − Q1 − Q2 − Q3, which needs all three quarters present, authoritative and contiguous. It never used the 9-month year-to-date figure that every Q3 10-Q reports. For net income alone, 1,326 recent company-years (1,017 companies) had a FY plus a 9-month YTD but no Q4.

Fix: when the chain isn't available, fall back to FY − 9-month YTD, and only when all of these hold:
- the YTD starts on the fiscal-year start;
- the remainder is 80–100 days;
- exactly one authoritative YTD value exists.

The chain still wins when both are available. Verified live against exact arithmetic: IMA FY2025 Q4 = −$6,908K, LUVU −$343K, FCCN $3,030K. On the 5 sample companies, 704 of 2,156 Q4s derived came from the new path.

Still open: companies like EXEL, whose FY fact itself is non-authoritative (disagreeing values across filings), can't get a Q4 from either path. That is a Stage 2e conflict case, not a derivation gap.

A second, smaller cause: the `*_resolved` fills (`resolve-conflict-fills`) and `ttm-margins` are in no scheduled job, so they aren't recomputed after new filings. Net income resolved lags raw for 166 companies, operating income for 115.

## Full-population recompute moved to CI

From the dev machine each Supabase round trip is 0.3–1.7 s. A local debt recompute managed about six 50-company batches an hour (roughly 20 hours for everyone). `.github/workflows/pipeline-recompute.yml` (manual `workflow_dispatch`) runs the chain on GitHub-hosted runners in four ordered phases:
1. sharded normalize + resolve;
2. population-wide fills + `company_tag_preference` merge;
3. sharded metrics;
4. screener snapshot.

It runs committed code only, so uncommitted work in someone's working tree never reaches production data. The first run (2026-09-27) applies both the component debt resolver and the Q4 fallback to every active company.

## Still to do

- Add `ttm-margins` and the population-wide `*_resolved` fills to the daily reprocessing, so a new filing's quarter reaches the TTM without a manual recompute.
- Other systemic yfinance-major clusters found in the same triage, not yet worked:
  - `institutional_ownership_pct` is a median 0.17× yfinance's.
  - `roa` is only ever stored from annual (FY) rows, never trailing-twelve-months, and has 646 sign flips.
- The other session's `calculate-expanded-metrics` process (worktree `88a574e4`) had been running 2h42m at the time of this writing, likely the known silent hang.
