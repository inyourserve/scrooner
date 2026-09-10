# Blocker Remediation — Execution Evidence

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

> **Status:** REMEDIATION PHASE COMPLETE — operational gate green; capacity and 100-company pilot remain blocked  
> **Date:** 2026-08-19  
> **Authority used:** The explicit “go ahead” following the feasibility test authorized the staged database and Collector changes. No paid plan, billing setting, GitHub secret, workflow activation, or 174-CIK bulk acquisition was performed.

## Executive result

The responsible first remediation phase succeeded.

| Workstream | Result | Current state |
|---|---|---|
| Dead letters | **Complete** | 38/38 exact historical IDs reconciled with timestamps and evidence notes; 0 unresolved across all layers |
| Universe migration | **Complete** | Migrations 0016 and 0017 deployed; 10 filers, 38 securities, and 38/38 listings linked |
| Production universe | **Complete for current data** | Dated snapshot persisted: 38 candidates, 9 eligible listings, 19 excluded, 10 uncertain, 7 primaries |
| Mapper repair proof | **Complete** | Three golden-ten reruns succeeded; global lineage clean; no new Mapper errors |
| Filing freshness | **Complete now** | Latest finalized SEC index ingested; 2,131 new filings, 408 already known, 0 errors |
| Recurring scheduler | **Prepared, not active** | Local GitHub Actions workflow exists; activation requires repository secrets and a push to the default branch |
| Capacity | **Blocked externally** | Current Supabase account connector/billing authority is unavailable; no paid upgrade was attempted |
| Valid 100-company pilot | **Still No-Go** | Only 10 submissions CIKs and 7 eligible primaries; capacity must clear before bulk expansion |

The live operational status is now `ok` with no alerts. This is not equivalent to private-beta readiness: the 100-company evidence denominator is still absent.

## 1. Controlled reconciliation capability

Migration `0017_dead_letter_resolution_audit.sql` adds `resolved_at` and `resolution_note` to Collector, Normalizer, and Mapper error tables and enforces consistent unresolved/resolved audit state.

The new `scrooner-reconcile` command:

- accepts only a whitelisted pipeline layer;
- requires explicit positive error IDs and a meaningful evidence note;
- locks and verifies every requested row;
- refuses missing or already-resolved IDs;
- updates the exact requested set or rolls back; and
- requires `--confirm` before any write.

Focused tests cover parsing, missing IDs, already-resolved IDs, unsupported layers, short notes, exact updates, and concurrent mismatch detection.

## 2. Pre-change evidence and migration deployment

Before database writes, client-side CSV snapshots were exported to `/tmp`:

| Snapshot | Records | SHA-256 |
|---|---:|---|
| Unresolved errors | 38 | `151e0d3926c724ef0a417b0f27fd2704371508cacef21c8374fbc7b82ffbbd09` |
| Golden-ten metrics | 10,424 | `610ccda08d58397392db9c075d3a5af455cbb96e5f6f52b51446f7b8c62d64b3` |
| Companies | 10 | `540578b9b139a7c1d5823d2e0424b2883fd992e23c356d92c54feffabec8fa4f` |
| Listings | 38 | `c39e86a6c1bfbb82cb49abd600b4596df1a2ac045192da3624e35a0a264460b3` |

All 17 migrations were first applied to a clean isolated PostgreSQL cluster. Migrations 0016 and 0017 were then applied a second time there to exercise their idempotent paths. The result was six audit columns and three audit constraints, with no second-run failure.

The configured database deployment used separate single transactions:

```text
filers=10
securities=38
linked_listings=38
audit_columns=6
audit_constraints=3
```

The dated universe snapshot persisted exactly the live-data rehearsal result:

```text
snapshot_id=1
as_of=2026-08-19
candidates=38
eligible=9
excluded=19
uncertain=10
primary=7
```

## 3. Golden-ten Mapper rerun and reconciliation

| Stage | Considered | OK | Errored | Computed | Explicit nulls |
|---|---:|---:|---:|---:|---:|
| Generic calculate | 10 | 10 | 0 | 3,890 | 1,672 |
| Expanded metrics | 10 | 10 | 0 | 21 | 69 |
| Quality flags | 10 | 10 | 0 | 150 | 86 |

Global validation returned:

```text
clean=true
canonical_fact_leaks=0
metric_value_leaks=0
canonical_fact_dangling=0
metric_value_dangling=0
new_mapper_errors_after_id_35=0
metric_rows_with_missing_period_dates=0
```

The metric table remained at 10,424 golden-ten rows. The logical comparison found no value, null-reason, or lineage change across 10,334 stable keys. The remaining 90 keys were the nine daily snapshot metrics for each company moving their explicit snapshot date from August 18 to August 19; that is expected daily as-of behavior.

After this proof:

- Mapper IDs 2–35 were resolved with the rerun and validation note.
- Collector IDs 1–4 were resolved as expected SEC Company Facts absence for CIKs `0000018748` and `0000023426`, preserving the distinction between absent and zero.
- Final audited resolutions: 38.
- Final unresolved counts: Collector 0, Normalizer 0, Mapper 0.

## 4. Filing refresh and scheduler hardening

The first full-universe refresh exposed an operational performance defect: one remote transaction per matching filing produced only about 95 filings per minute. That run was intentionally closed as failed, with its reason preserved in `collector_runs`; already committed filing rows remained valid.

The Collector was changed to insert idempotent chunks of 250 rows, with per-row fallback and normal dead-letter evidence if a chunk fails. The recovered run for the identical date/scope completed in 21.18 seconds:

```text
run_id=13
index_date=2026-08-18
index_rows=5,551
considered=2,539
new=2,131
already_known=408
errors=0
```

Operational alerting now treats a later success for the exact same job and scope as recovery from the earlier attempt. It does not hide failures recovered under a different scope.

The local workflow `.github/workflows/pipeline-refresh.yml` is prepared with:

- daily `12:23 UTC` non-top-of-hour scheduling;
- serialized production concurrency;
- a 30-minute timeout;
- required-secret checks;
- the latest finalized SEC filing-index job; and
- `scrooner-operations --fail-on-alert` as the health gate.

It is **not active** until committed and pushed to the default branch with `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SEC_USER_AGENT` configured as repository secrets. Two consecutive scheduled cycles remain required before calling recurring execution proven.

## 5. Final live state

The final read-only operational gate returned `status=ok`, `alerts=[]`.

| Signal | Result |
|---|---:|
| Database size | 159,222,931 bytes |
| Company Facts | 186 rows / 174 distinct CIKs |
| Submissions | 178 rows / 10 distinct CIKs |
| Filing index | 3,098 rows |
| Metric values | 10,424 rows |
| Eligible primary companies | 7 |
| Audited resolved errors | 38 |
| Unresolved errors | 0 |

All five operational freshness readings were within target at `2026-08-19T08:58:55.885267Z`:

- SEC Company Facts: 121.26 hours / 168-hour target;
- SEC Submissions: 131.79 hours / 168-hour target;
- filing index: 0.02 hours / 72-hour target;
- market prices: 40.38 hours / 96-hour target; and
- derived metrics: 0.22 hours / 168-hour target.

## 6. Remaining gates and next responsible action

The current green status is time-bound. Company Facts and Submissions need a future bulk refresh, but the existing append-only raw-object design would create new dated objects and the feasibility projection already exceeds Free-tier capacity. Scheduling that job before capacity approval would knowingly create quota risk.

The next responsible sequence is therefore:

1. Approve and provision Supabase Pro (or equivalent PostgreSQL/object storage) and verify backup availability.
2. Configure repository production secrets and activate the prepared workflow.
3. Add the capacity-safe weekly Company Facts/Submissions refresh and an independent alert destination.
4. Prove two consecutive scheduled filing cycles and one bulk freshness cycle.
5. Acquire submissions for the 174-CIK candidate pool.
6. Normalize identity/listing/status, classify securities, and resolve foreign-filer/ADR/multi-class policy cases.
7. Rebuild the universe; require at least 100 eligible primary companies.
8. Run representative mapping preflight, then the staged `10 → 25 → 50 → 100` pilot.

## 7. Repository verification

| Gate | Result |
|---|---|
| Pipeline default suite | PASS — 146 passed, 1 live test deselected |
| Backend suite | PASS — 22 passed; one dependency deprecation warning |
| Screener app | PASS — ESLint, 13 tests, TypeScript, and Next.js production build |
| Marketing site | PASS — Astro server production build |
| Migration sequence | PASS — 17 contiguous migrations |
| Documentation links | PASS — 237 local targets |
| Secret-pattern scan | PASS — 298 text files |
| Python compilation | PASS |
| Scheduler YAML parse | PASS |
| Git whitespace check | PASS |

The local Ruff executable is not installed; CI retains the required `E9,F63,F7,F82` correctness lint.

## Consultant verdict

This phase converted four active operational blockers into verified capabilities: controlled reconciliation, deployed universe identities, clean Mapper reruns, and current filing freshness. The remediation is real and measurable.

The product remains **No-Go for a 100-company/private-beta claim** until capacity, recurring execution proof, representative submissions, universe size, and mapping coverage are demonstrated. No quality gate should be weakened to change that conclusion.

Machine-readable results: [`evidence/blocker_remediation_execution_2026-08-19.json`](evidence/blocker_remediation_execution_2026-08-19.json).
