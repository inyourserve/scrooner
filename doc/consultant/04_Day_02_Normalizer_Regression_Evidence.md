# Day 2 — Normalizer Regression Protection Evidence

> **Status:** Complete  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 2

## Outcome

The Normalizer's highest-risk period, unit, duplicate, amendment, and derived-quarter behavior now has deterministic automated regression coverage. The work also found and fixed one real production correctness gap in Q4 derivation.

## Coverage added

### Period identity and classification

- Extraction of objective `(end, start)` periods from Company Facts
- Instant versus duration identity
- Instant periods represented with `start_date == end_date`
- Observed fiscal-year-end anchors
- Non-calendar fiscal-year classification
- Full-year and Q1 classification
- Half-year YTD spans remaining deliberately unclassified

### Unit handling

- Distinct raw-unit extraction
- Case-fold and whitespace canonicalization
- `Segment`/`segment` collision resolving to the same canonical unit
- No semantic fuzzy merging

### Duplicate resolution

- Earliest-filed fact remains authoritative when duplicates agree
- Every row becomes non-authoritative when duplicate values conflict
- Singleton facts remain unchanged
- Repeat execution produces the same authority state
- Processing one company leaves another company's facts unchanged

### Formal amendments and restatements

- A `10-K/A` links to the most recent matching prior filing
- The amended fact becomes authoritative
- The original fact remains stored and becomes non-authoritative
- `supersedes_fact_id` preserves fact-level lineage
- An amendment without a defensible original remains unmatched rather than guessed

### Derived quarters

- Q4 equals FY minus discrete Q1, Q2, and Q3
- Q4 lineage uses the FY filing/raw object
- A directly reported Q4 is never overwritten with a derivation
- An incomplete FY/Q1/Q2/Q3 chain remains underived
- Cumulative YTD values decompose exactly into discrete Q2 and Q3
- Non-nested YTD spans are rejected
- Repeated interim derivation produces identical logical rows

## Correctness defect found and fixed

### Finding

`derive_q4_for_company` grouped inputs by company, concept, unit, and fiscal year, then trusted the fiscal-period labels `FY`, `Q1`, `Q2`, and `Q3`. It did not independently prove that their date contexts were contiguous and nested within the same fiscal-year duration.

A malformed, irregular, or incorrectly labeled filing could therefore cause subtraction across quarters with a gap or overlap. The unit grouping already prevented cross-unit arithmetic, but the date-context assumption was unguarded.

### Test-first proof

A regression fixture supplied:

- A valid FY span
- A Q1 beginning at the FY start
- A Q2 beginning several days after Q1 ended
- A Q3 following that Q2

Before the fix, the code proceeded toward creating a Q4 derivation. The focused test failed, proving the missing guard.

### Fix

Q4 derivation now requires:

- Q1 starts on the FY start date
- Q2 starts exactly one day after Q1 ends
- Q3 starts exactly one day after Q2 ends
- Q3 ends before the FY end date

If any condition fails, the candidate is counted as incomplete and no fact or period is derived. Unit comparability continues to be guaranteed by the grouping key.

## Verification results

### Pipeline

```text
collected 19 items
19 passed in 0.47s
exit code: 0
```

The 19 tests comprise the original five pipeline smoke tests plus fourteen Day 2 regression tests.

### Backend regression check

```text
collected 1 item
1 passed in 0.62s
exit code: 0
```

The previously recorded FastAPI `TestClient` dependency warning remains non-blocking and unchanged.

## Day 2 Definition of Done

| Gate | Result |
|---|---|
| Instant/duration and fiscal classification protected | PASS |
| Unit canonicalization and collision behavior protected | PASS |
| Duplicate agreement/conflict behavior protected | PASS |
| Amendment precedence preserves original facts | PASS |
| Direct Q4 is not overwritten | PASS |
| Incomplete chains remain underived | PASS |
| Incomparable contexts are not subtracted | PASS — missing Q4 guard found and fixed |
| Cumulative YTD becomes exact discrete Q2/Q3 | PASS |
| Repeated execution is logically stable | PASS |
| Single-company processing is isolated | PASS |

## Scope boundary

These are deterministic offline regression tests. SQL-bound behavior is exercised through stateful connection doubles, not a live PostgreSQL instance. No production database, Supabase, SEC, or Alpaca call was made. Migration and real-PostgreSQL integration checks remain part of the CI/database-integration work in subsequent days.

