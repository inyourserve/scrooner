# Day 4 — Screener, AI Query, API, and Authorization Evidence

> **Status:** Complete  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 4

## Outcome

The complete user-query boundary now has automated offline protection: structured validation, all Screener operators, null behavior, deterministic ordering, natural-language interpretation, API serialization, authentication, and saved-screen isolation.

The repository now runs 91 tests: 78 pipeline tests and 13 backend tests.

## Screener coverage

### Operators

Tests cover all locked operator forms:

- `>`
- `<`
- `>=`
- `<=`
- `=`
- `!=`
- `between`
- `top_n`
- `bottom_n`

`between` is inclusive at both boundaries. Null metric values never pass comparison, range, or ranking operations.

### Structural validation

The query schema now rejects:

- Comparison predicates without `value`
- Comparison predicates carrying ranked/range fields
- `between` without a range
- Reversed or equal range bounds
- `between` carrying comparison/rank fields
- Ranked predicates without a positive `n`
- Ranked predicates carrying comparison/range fields
- More than one ranked predicate
- Zero or negative result limits

Previously, incompatible extra fields and negative limits were accepted. A negative Python slice could produce surprising results rather than an explicit validation failure.

### Deterministic ordering

Tie behavior is now explicit:

- Primary order is the metric value.
- Equal values use CIK ascending as the stable tiebreaker.
- Null sort values remain last in both directions.
- Ranked results render in rank order rather than database insertion order.
- Queries without a requested order default to CIK ascending.

The earlier implementation allowed SQL row order to influence ties and converted ranked CIKs to a set before rendering. Results could contain the correct companies but appear in a non-contractual order. Identical queries are now independent of database row ordering.

### Result lineage

A `sort_by` metric is included in each result even when it is not also a filter predicate. Tests assert value, period label, period end, and formula version are present.

## AI Query coverage

Tests protect:

- Natural filler phrases
- Metric aliases
- Operator aliases
- Percent conversion
- Numeric values
- Ranges
- Top/bottom ranking
- Sector aliases
- Ambiguous metric phrases
- Unknown metrics
- Malformed language
- Mixed recognized and unrecognized clauses

A partially recognized request produces no executable query. An ambiguous request remains non-executable even when the API caller sends `run=true`.

## API contract coverage

Tests verify:

- `GET /health`
- Valid `POST /v1/screen`
- Invalid screen request returns HTTP 422 before execution
- Full Decimal precision survives the HTTP response as a JSON string
- `POST /v1/ask` shows the interpreted structured query
- `/v1/ask` does not execute by default
- Ambiguous `/v1/ask` input never executes

The precise Decimal fixture is `0.1234567890123456789012345678`; the raw JSON-decoded value matches the full string without float truncation.

## Authentication coverage

Tests verify:

- Missing Authorization header
- Empty header
- Wrong authentication scheme
- Empty Bearer token
- Invalid or expired token response
- Valid token resolution
- Provider success response missing a user ID
- Outbound token forwarding to the Supabase Auth endpoint

All rejection cases fail closed with HTTP 401. No real authentication network call is made.

## Saved-screen isolation

A stateful two-user test uses a real `uuid.UUID` for the stored owner and string IDs from the auth boundary. It proves:

- The owner can list the screen.
- The other user cannot list it.
- The owner can rename it.
- The other user cannot rename it.
- The other user cannot delete it.
- Failed non-owner actions do not mutate state.
- The owner can delete it.

This permanently protects the earlier UUID-versus-string ownership regression.

## Verification results

### Pipeline

```text
collected 78 items
78 passed in 0.55s
exit code: 0
```

### Backend

```text
collected 13 items
13 passed in 0.55s
exit code: 0
```

One non-blocking FastAPI `TestClient` dependency deprecation warning remains visible.

## Day 4 Definition of Done

| Gate | Result |
|---|---|
| All locked Screener operators protected | PASS |
| Null exclusion protected | PASS |
| Sorting, ties, ranking, and limits deterministic | PASS |
| Malformed query structures rejected | PASS |
| Natural-language aliases and filler phrases protected | PASS |
| Ambiguous/unknown/partial language never executes | PASS |
| Screen and Ask HTTP contracts protected | PASS |
| Decimal precision preserved | PASS |
| Missing, invalid, and valid authentication protected | PASS |
| Two-user list/rename/delete isolation protected | PASS |
| Known Screener/parser/API/auth bugs have regressions | PASS |

## Scope boundary

These tests are offline and use stateful connection doubles. They prove application behavior and SQL intent, not Supabase/PostgreSQL policy configuration. Real database row-level security, migration behavior, and provider integration require isolated PostgreSQL and live-integration checks in later quality gates.

