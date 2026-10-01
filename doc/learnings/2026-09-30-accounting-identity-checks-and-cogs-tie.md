# 2026-09-30 · Accounting identity checks, the cost_of_revenue tie, and two connection bugs

**Prompt:** "our normalizer, mapper should be scalable, top class... how are we fixing
things... how have the big sites done this... make a bigger improvement." The audit and
target architecture are in doc 48. This entry covers what was built, what it found, and
what broke along the way.

## 1. Correctness had never been measured

Every existing score measured coverage, range plausibility, or agreement with yfinance.
None checked whether a company's own numbers agree with each other. The new
`sanity/accounting_identity.py` (`scrooner-sanity identities`, migration 0082) does that.
Population baseline is in doc 48 §4: 93–99.9% per identity.

Two design points mattered, each checked on a 10% live sample before writing code:

- **Adjustments are needed.** Without NCI and temporary equity, 13% of balance sheets
  "failed"; 68% of those closed once noncontrolling interest and mezzanine equity were
  added. Net income went from 89.1% to 95.2% after adding discontinued ops, NCI and
  equity-method income. An identity check without these reports legitimate accounting
  as errors.
- **Tautology guard.** A derived value (for example an arithmetic-fallback gross profit)
  trivially satisfies the identity it was derived from. Such rows are detected by
  overlapping `source_fact_ids` and skipped (58,123 rows), not counted as passes. One
  near-miss: `array_agg` over array columns builds a 2-D array, `[1]` on it is NULL, and
  that would have silently disabled the guard. Aggregate the unnested ids instead.

## 2. Its first run found a real mapping bug

`CostOfGoodsSold` and `CostOfRevenue` were both priority 2 for `cost_of_revenue`, so
`first_match` broke the tie by `concept_id`. For a goods-plus-services company,
`CostOfGoodsSold` is goods only. Microsoft FY2015: we stored $21.4B against a true $33.0B,
so FY gross margin showed **77.1%** (real 64.7%) and quarters showed 80–82%.

The fix was chosen by the identity, not by opinion. Where both tags exist and differ,
`CostOfRevenue` satisfies Revenue − Cost = Gross Profit in 2,560 periods;
`CostOfGoodsSold` does in 146 (172 companies). Migration 0082 does two things:

- Ranks `CostOfRevenue` first.
- Adds a trigger rejecting any future tied `first_match` priority. A unique index can't
  be used because `sum`-mode concepts legitimately share priorities.

**After (172 companies, gross-profit identity):** raw 74.1% → 91.1%, display 73.2% →
89.3%. Microsoft FY2015 gross margin is now 64.7%, and its FY row agrees with its TTM row.

## 3. A population-wide stage left the site half-updated

`resolve-statement-fallbacks` rebuilds `gross_profit/cost_of_revenue/
operating_expenses_resolved` for every company. Conflict fills and tag preferences
then add their values back. The database went read-only between those two steps
(04:53:53–04:55:23 UTC, `default_transaction_read_only` from the configuration file,
45 GB, about 1M dead tuples in `canonical_fact`; consistent with Supabase disk
autoscale). For about an hour, some cells those later steps fill were blank sitewide.

Lesson: these population steps are not independent. A failure between them is a
user-visible regression. This is doc 48 §6 step B's argument (one resolver, one write per
company) in practice.

## 4. Two connection bugs, fixed at the root (b61c257)

- **No TCP keepalives anywhere.** A socket the pooler dropped silently left
  `calculate-fcf-growth` blocked in `recv()` for 29 hours, with no query in
  `pg_stat_activity`. This is the same "hung for hours" pattern CLAUDE.md records from
  earlier sessions. `common/config.py` now appends `keepalives*` and `tcp_user_timeout`
  to `DATABASE_URL`, so a dead socket errors in about two minutes.
- **13 batch loops used a dead connection after an error.** In `quality_flags`,
  `reconciliation`, `tax_reconciliation` and 10 others, `log_error(conn, ...)` was
  followed by `continue` with no `safe_rollback`. One pooler drop failed 169 of 172
  companies. Because `log_error` correctly swallows its own failure, `mapper_error`
  stayed empty.

  A single-company rerun on a healthy database succeeds, which makes this look
  "transient". It isn't: the cascade is the bug. All 13 now reconnect, and
  `tests/unit/test_connection_hardening.py` fails if the log-then-continue shape
  reappears anywhere in the package. The test caught one more site
  (`expanded_metrics.py`) on its first run.

## 5. Multi-session coordination

Three sessions shared one database and one working tree. What went wrong:

- I numbered a migration 0081 after another session had pushed 0081.
- I ran production writes from uncommitted code.
- Two of us briefly prepared to run the same 172-company batch.

What fixed it: announce heavy jobs, commit and push before writing, and hand off a batch
explicitly instead of both relaunching it.
