# Day 3 — Mapper and Metrics Regression Evidence

> **Status:** Complete for current-screen calculation scope; two architecture follow-ups recorded  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 3

## Outcome

Canonical resolution, generic financial formulas, TTM/growth windows, all six locked price metrics, and all twelve expanded metric definitions now have deterministic regression coverage. Two previously untested price-path defects were found and fixed.

The pipeline suite increased from 19 to 50 tests.

## Coverage added

### Canonical concept resolution

- `first_match` selects the highest-priority available tag for each period.
- A lower-priority tag fills only periods where the preferred tag is absent.
- `sum` combines all mapped summands.
- Source fact IDs match the exact facts selected or summed.
- Canonical-fact replacement deletes only the requested company.

### Generic metric engine

Positive formula cases now cover:

- Gross Margin
- Operating Margin
- Net Margin
- ROE
- ROIC
- FCF
- FCF Margin
- Debt/Equity
- Current Ratio
- Interest Coverage
- ROA
- Quick Ratio
- SBC as % of Revenue
- EBITDA

Edge cases cover missing roles, partial multi-concept roles, zero denominators, zero pretax income, and exact Decimal behavior. The ROIC fixture independently asserts the pinned NOPAT/invested-capital formula.

### Period and stage ownership

- Duration inputs anchor a metric's reporting period.
- Instant balance-sheet inputs match the duration period by end date.
- A missing member of a multi-concept role nulls the entire metric.
- Point-in-time calculation deletes only its owned metric IDs.
- Point-in-time calculation explicitly preserves `period_label='TTM'` rows written by the TTM stage.
- Selected source fact IDs are preserved on calculated rows.

This permanently protects the previously discovered shared-table delete-scoping bug.

### TTM and growth

- Fiscal trailing-quarter windows across Q1 and Q4 boundaries
- Four-quarter completeness requirement
- TTM source-fact lineage aggregation
- YoY growth
- Three-year CAGR
- Zero-base rejection
- Negative-ratio CAGR rejection

The growth calculation was extracted into a pure helper used by the production job and tests, without changing its formula.

### Locked price-dependent metrics

All six compute together from one deterministic input set:

- Market Cap
- Trailing P/E
- Price/Sales
- Price/Book
- Dividend Yield
- FCF Yield

The regression asserts exact Decimal values, TTM input completeness, source-fact lineage, and TTM-scoped replacement.

### Expanded composite metrics

Positive and null-path tests cover:

- Net Debt/EBITDA
- EV/EBITDA
- EV/Sales
- PEG Ratio
- Buyback Yield
- Total Shareholder Yield
- Institutional Ownership %
- Share Count Dilution Trend

The four expanded metrics handled by the generic engine—ROA, Quick Ratio, SBC % Revenue, and EBITDA—are covered in the generic formula suite.

All 20 V1 database definitions and all 12 expanded definitions are asserted unique.

## Defect 1 — Non-positive prices crashed Dividend Yield

### Finding

A stored price of zero allowed several metrics to proceed but caused `Dividend Yield = DPS / Price` to raise `Decimal.DivisionByZero`. The exception aborted the entire six-metric stage for that company.

### Fix

The price-metric stage now treats any price less than or equal to zero as unusable. It writes six explicit null results with reason `invalid:non_positive_price` instead of crashing or publishing misleading values.

## Defect 2 — Missing-price null rows violated the database schema

### Finding

When no real Alpaca price existed, the stage correctly intended to write six null rows with reason `missing:real_price`, but used `None` for `period_start` and `period_end`. Both columns are `NOT NULL` in `analytics.metric_value`.

The golden set had prices for every company, so live verification never exercised this path. A wider universe would have produced a constraint failure precisely when honest missing-price handling was needed.

### Fix

Missing-price null rows are now anchored to the calculation date. They retain the explicit missing-data reason and satisfy the metric table's required as-of dates.

## Verification

### Pipeline

```text
collected 50 items
50 passed in 0.53s
exit code: 0
```

### Backend regression check

```text
collected 1 item
1 passed in 0.60s
exit code: 0
```

The existing FastAPI `TestClient` dependency warning remains unchanged.

## Day 3 gates

| Gate | Result |
|---|---|
| Standard-tag priority and fallback protected | PASS |
| Sum-mode canonical concepts protected | PASS |
| Generic V1 and expanded formulas protected | PASS |
| TTM and growth windows protected | PASS |
| Missing/zero/negative edge behavior protected | PASS |
| Decimal precision protected | PASS |
| Shared-table delete scope protected | PASS |
| Canonical source-fact lineage protected | PASS |
| All six price metrics protected | PASS |
| All expanded metric families protected | PASS |
| Historical as-known/no-look-ahead screening | NOT IMPLEMENTED — product currently serves latest/current screens only |
| Generalized external-source lineage | DESIGN GAP — `source_fact_ids` cannot reference price or ownership rows |

## Architecture follow-ups

### Historical point-in-time screening

Current calculations produce the latest authoritative view, including later amendments where applicable. This is correct for the present-day Screener. It is not a historical backtesting model and must not be marketed as one.

Supporting an “as known on date X” screen would require filing-acceptance-time filtering, versioned calculated outputs, point-in-time company/security eligibility, and tests proving future amendments cannot influence earlier results.

### Multi-source lineage

`analytics.metric_value.source_fact_ids` can trace XBRL-derived inputs in `core.fact`. It cannot represent:

- `core.market_price_alpaca` rows
- `core.shares_outstanding_fallback` rows
- `core.institutional_ownership` rows
- Upstream `analytics.metric_value` dependencies

Composite metrics therefore do not yet have one generalized lineage mechanism covering every source type. Before claiming complete user-auditable lineage for these metrics, introduce a typed lineage relation such as `(metric_value_id, source_type, source_id, role)`, or an equivalent explicit design. This should be an architecture decision, not an overloaded array convention.

## Scope boundary

All Day 3 tests are deterministic and offline. SQL ownership is asserted through stateful connection doubles; no production database or external API was used. Real PostgreSQL migration/integration execution remains a subsequent quality-gate task.

