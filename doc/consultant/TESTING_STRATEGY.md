# Scrooner Testing Strategy

> **Status:** Day 1 implementation guidance  
> **Default rule:** Tests must be deterministic, offline, and unable to touch production data.

## Test layers

| Layer | Marker | Default run | External access |
|---|---|---:|---|
| Unit | `unit` | Yes | None |
| Database integration | `integration` | No until an isolated test DB is explicitly configured | Test database only |
| Frozen-fixture pipeline | `integration` | Added incrementally | Local fixtures and test database only |
| Live verification | `live` | No | Explicit SEC/vendor credentials and network |

Unit tests protect pure transformations, query validation, formulas, and request contracts. Integration tests will protect migrations, SQL behavior, idempotency, and stage isolation. Live checks remain independent verification and must never be the only protection for a discovered bug.

## Commands

From the repository root:

```bash
pipeline/.venv/bin/pytest pipeline/tests -m unit
```

From `apps/backend`:

```bash
.venv/bin/pytest tests -m unit
```

Run all default offline tests:

```bash
pipeline/.venv/bin/pytest pipeline/tests
cd apps/backend && .venv/bin/pytest tests
```

## Database isolation

Database integration tests must request the `isolated_database_url` fixture and use `SCROONER_TEST_DATABASE_URL`. The fixture refuses to run unless:

- The database name contains `test`.
- The test URL differs from `DATABASE_URL` when both exist.
- The URL was explicitly provided for the test run.

Future integration fixtures should create a unique schema per test session and remove it after the run. Until that implementation exists, database integration tests must remain skipped rather than falling back to a developer or production database.

## Frozen SEC fixtures

Fixtures live under `pipeline/tests/fixtures/sec/`. They should be the smallest payload capable of reproducing the behavior under test. Keep the source accession number in the fixture or associated test evidence. Remove irrelevant data and never store credentials, private user data, or vendor responses whose terms prohibit redistribution.

## Regression rule

When a correctness bug is found:

1. Add a test that fails for the observed input.
2. Apply the fix.
3. Confirm the new test passes.
4. Run the complete relevant offline suite.
5. Record any necessary live-data confirmation separately.

Manual verification remains valuable, but it does not replace a permanent executable regression test.
