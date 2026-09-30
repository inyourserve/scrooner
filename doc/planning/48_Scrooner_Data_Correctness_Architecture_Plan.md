# 48 · Data Correctness Architecture: Audit and Plan

**Status:** Draft (2026-09-30) · Owner: Founder/Product · Review: when a core decision changes

**Written for:** whoever next changes the Normalizer or Mapper, human or agent.

## 1. The question

Is the Normalizer/Mapper built the way a trusted fundamentals provider builds one, and
what would move data confidence above 90%? Everything below was measured against the
live database on 2026-09-29/30, not inferred from docs.

## 2. What is already right

- **The Collector and Normalizer have a sound core.** Raw data is immutable, there is
  full lineage (`source_fact_ids`), money stays in `Decimal`, and conflicting filings
  stay null instead of being guessed (`is_authoritative`).
- **Tag resolution is versioned data, not code.** `concept_mapping` has a priority and
  a confidence per tag.
- Most batch jobs follow load-into-memory, one pass, then batched writes.

## 3. What is structurally wrong (measured)

### 3.1 Split brain: the screener and the company page compute from different numbers

28 of 75 canonical concepts are shadow `*_resolved` concepts. They have zero
`concept_mapping` rows and are filled by side modules. The company page
(`statements/classify.py`) and TTM margins (`ttm.py`) read the `*_resolved` layer.
`calculate.py`, which produces 26 metrics, and most metric inputs
(`metric_definition_input`) read the raw concepts.

| Concept | Periods only in `*_resolved` | Periods where layers differ >1% |
|---|---|---|
| revenue | 14,907 (1,783 companies) | 9,575 |
| operating_income | 31,254 (2,461 companies) | 151 |
| net_income | 7,577 | 249 |
| cfo | 8,693 | 141 |
| capex | 5,090 | 2,132 |

So every fix that lands in a `*_resolved` concept (conflict fills, parsers, arithmetic
fallbacks, tag preferences) is invisible to the screener's `calculate.py` metrics.
Example: Microsoft FY2015 `gross_margin` was 77.1% on the FY row (raw layer) and 64.7%
on the TTM row for the same year (resolved layer).

### 3.2 Many writers, one table, order-dependent

- `analytics.canonical_fact` has 6 writer modules: `resolve`, `concept_fallback`,
  `conflict_resolution`, `parsers/main_parser`, `sanity/tag_investigator`
  (a *sanity* module writing data) and `stock_splits`.
- `analytics.metric_value` has 10 writer modules.
- There are 21 separate `delete from` statements across them.
- Who wins a (company, concept, period) cell depends on run order and on each writer's
  `ON CONFLICT DO NOTHING` versus delete-then-insert choice.
- `canonical_fact` has no column saying which rule produced a value.

This is the root cause behind the recurring "writer A wiped writer B" bugs in
CLAUDE.md: `resolve.py` versus `total_debt_resolved`, `expanded_metrics.py`'s delete
scope, the arithmetic fallback versus the parser, and `roic`/`roe`. Each one was fixed
locally with another scoping rule. The class of bug remains.

### 3.3 Fixes are one rule per incident

Recent fixes each added a new module, a new shadow concept or a new CLI stage (for
example `revenue_sanity_resolved`). The daily cron runs 8 normalizer stages and 13
mapper stages in a hand-ordered shell list. Population-wide steps are orchestrated
separately in `pipeline-recompute.yml`. A one-line mapping change today needs the
operator to know about 20 commands and their order (see §5, which needed exactly that).

### 3.4 Coverage was measured; correctness was not

Every score so far (`coverage_snapshot`, the coverage matrix, plausibility, yfinance
agreement) measures whether a value exists, whether it is in range, or whether it
matches a third party. None checked whether a company's own numbers agree with each
other. §4 adds that.

## 4. Built in this pass: accounting identity checks

`sanity/accounting_identity.py` (migration `0082`, CLI `scrooner-sanity identities`)
checks identities that must hold for correct statements. Results go to
`analytics.identity_check_summary`, `analytics.identity_check_failure` and the
`analytics.identity_check_score` view.

Design choices, each checked on live data first:

- **Declarative identity list; adding a check is one entry.** `evaluate()` is a pure,
  unit-tested function.
- **Adjustments are optional reconciliations.** 68% of raw balance-sheet "failures"
  were noncontrolling interest or temporary equity. Adding discontinued operations, NCI
  and equity-method income moved the net-income identity from 89.1% to 95.2%.
  Without these adjustments the check reports legitimate accounting as errors.
- **Tautology guard.** A value derived from the identity's own terms (for example an
  arithmetic-fallback gross profit) is skipped, not counted as a pass. 58,123 such
  rows were skipped.
- **Chunked set-based loads, 500 companies at a time.** Only summaries and failing
  periods are stored.
- **Runs on two layers.** `display` is what the page shows; `raw` is what
  `calculate.py` reads.

Population baseline (2026-09-30, 5,216 active companies):

| Identity | Display | Raw | Checked (display) |
|---|---|---|---|
| Assets = Liabilities + Equity (+NCI, temp. equity) | 96.20% | 96.43% | 167,204 |
| Gross Profit = Revenue − Cost of Revenue | 93.06% | 93.31% | 134,810 |
| Net Income = Pretax − Tax (+adjustments) | 93.85% | 94.82% | 271,228 |
| Current assets ≤ Total assets | 99.97% | 99.98% | 167,988 |
| Cash ≤ Total assets | 99.92% | 99.94% | 200,950 |
| Revenue ≥ 0 | 99.75% | 99.73% | 338,454 |

The display layer is *less* consistent than raw on net income (93.85% vs 94.82%).
The resolved-layer fill-ins introduce inconsistency: a restated net income gets
filled in while the pretax and tax lines keep the original values. This supports §6's
single-winner design over more independent fills.

## 5. Fixed in this pass: cost_of_revenue tie (found by the checker on its first run)

`CostOfGoodsSold` and `CostOfRevenue` both sat at priority 2, so the tie was broken by
`concept_id`. For a company that sells goods and services, `CostOfGoodsSold` is goods
only. Microsoft FY2015: $21.41B picked versus a $33.04B total.

The fix was chosen by the identity rather than by opinion. Across every period where a
company reports both tags with different values, `CostOfRevenue` satisfies
Revenue − Cost = Gross Profit in 2,560 periods; `CostOfGoodsSold` does in 146 (172
companies).

The same migration (`0082`) does two things:

- Ranks `CostOfRevenue` above `CostOfGoodsSold`.
- Adds a trigger that rejects any future tied `first_match` priority. This was the only
  tie in the table.

Results for the 172 companies are in §8.

## 6. Target architecture (how mature providers do it)

Commercial fundamentals vendors (S&P Capital IQ, FactSet, Morningstar, which also
supplies Yahoo Finance's fundamentals that `yfinance` scrapes) and the XBRL US Data
Quality Committee share one shape:

1. **One standardized layer, one winner per cell, with its method recorded.** For each
   (company, line item, period), collect every candidate: each mapped tag, derived
   arithmetic, a rendered-statement parse, the latest restatement, and a manual
   override. Score them and keep one winner, plus the runners-up for audit. Every
   consumer reads only that layer.
2. **Internal consistency decides between candidates.** When candidates disagree, the
   one that satisfies the statement's identities wins. §5 is this, done by hand once.
3. **Overrides are data.** A human correction is a row (reason, author, evidence), and
   it is the highest-priority candidate. It is never an `UPDATE` that the next
   recompute silently overwrites (the Akari market-cap fix in CLAUDE.md is an example).
4. **As-reported and restated are separate versions,** not one row overwritten in
   place.
5. **The pipeline is a DAG with declared dependencies,** not a hand-ordered stage list.

Mapped onto Scrooner:

| Step | Change | Removes |
|---|---|---|
| A | Add `method` (`tag:<name>`, `derived:<rule>`, `parser`, `conflict_fill`, `override`) and `candidate_count` to `canonical_fact` | Values with no stated origin |
| B | One resolver: every current writer becomes a candidate generator returning rows in memory; a single selector picks the winner (priority, then identity consistency) and does one scoped delete-then-insert per company | The 6 writers, 21 delete scopes, and run-order dependence |
| C | Collapse `X` / `X_resolved` into one concept per line item; point `metric_definition_input` and the page at it | The split brain (§3.1) |
| D | Make `company_tag_preference` and manual fixes rows in an `override` table read by the selector | One-off `UPDATE`s that get overwritten |
| E | Declare the stages as a dependency graph in one Python module, used by both the daily cron and the full recompute | The hand-ordered shell lists in two places |
| F | Gate: the daily run records `identity_check_score`, and a regression against the last passing baseline fails the job (same ratchet as the yfinance gate) | Silent correctness regressions |

Order: A and F first (cheap, measurable). Then B and C together, one statement at a
time, starting with the income statement, each step judged by `identity_check_score`
not dropping. D and E last.

## 7. What "90% confidence" should mean

Coverage alone can't carry it. Proposed definition: a company-period is *confident*
when every applicable identity passes **and** the value agrees with the independent
cross-check where one exists (yfinance, SEC Frames). Today:

- Weighted identity pass rate is ~96% on the display layer.
- The weakest identities are gross profit (93.1%) and net income (93.9%).

So identities alone are already above 90%. The number that matters is the joint
per-company score. Build it in step F, not as another standalone percentage.

## 8. Results of this pass

See the learnings entry
`doc/learnings/2026-09-30-accounting-identity-checks-and-cogs-tie.md` for
before/after numbers on the 172 recomputed companies.
