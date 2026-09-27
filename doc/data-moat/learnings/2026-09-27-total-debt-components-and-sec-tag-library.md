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

## Still to do

- **Recompute the metrics that use `total_debt_resolved`**: `calculate`, `ttm-returns`, `calculate-expanded-metrics`, `calculate-piotroski`, `calculate-quality-flags`, then rebuild the screener snapshot. This is held back because `calculate.py`/`ttm.py`/`expanded_metrics.py` carry another session's uncommitted materiality-floor changes, and a full recompute would push those to production too.
- **Other systemic yfinance-major clusters found in the same triage, not yet worked:**
  - `institutional_ownership_pct` is a median 0.17× yfinance's.
  - `roa` is only ever stored from annual (FY) rows, never trailing-twelve-months, and has 646 sign flips.
  - Around 400 trailing-twelve-month margin rows compared against yfinance are more than 400 days old.
