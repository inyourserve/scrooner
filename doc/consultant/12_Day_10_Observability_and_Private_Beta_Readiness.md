# Day 10 — Observability and Private-Beta Readiness

> **Status:** READINESS ASSESSMENT COMPLETE — **NO-GO FOR PRIVATE BETA**  
> **Date:** 2026-08-19  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 10  
> **Decision basis:** Correctness and visibility gates are not weakened to manufacture a launch milestone.

## Executive decision

Scrooner is **not ready for a controlled private beta today**.

Day 10 materially improved operability: API requests now carry correlation IDs and content-free structured telemetry; the pipeline has a read-only operational status command with freshness, run, dead-letter, and row-count alerting; backup restoration was exercised successfully; and all automated product gates pass.

The decision is still No-Go because the live evidence contains explicit blockers:

- the 100-company pilot cannot start safely and has not completed;
- the production-universe migration is not deployed to the configured database;
- filing-index freshness is 119.63 hours against a 72-hour target;
- 4 Collector and 34 Mapper dead letters remain unresolved;
- only 10 distinct submissions payloads are available for a 100-company pilot;
- representative mapping coverage is not measured;
- projected 100-company database usage is 1.133 GB against a 500 MiB limit;
- API metrics are process-local and no production log/alert destination or hosting platform is configured; and
- five internal scripted sessions pass, but zero representative external users have been observed.

These are visible, measurable conditions. No evidence suggests the current golden-company UI slice should be discarded; the decision blocks beta exposure until the operating and wider-universe claims are supportable.

## What Day 10 built

### API request observability

The FastAPI application now:

- generates a UUID request ID for every request;
- returns it through `X-Request-ID`;
- emits `api.request.completed` with method, route template, status, and duration;
- avoids query strings, bodies, authorization headers, and user IDs;
- records total and per-endpoint count, client errors, server errors, server-error rate, average latency, and maximum latency; and
- exposes the single-process snapshot at `/health/metrics`.

Unmatched paths are aggregated under `<unmatched>` so user-controlled paths do not create high-cardinality or content-bearing telemetry.

### Pipeline operational status

`scrooner-operations --fail-on-alert` consolidates:

- five source/stage freshness readings and row counts;
- recent Collector run IDs, scopes, status, duration, and stats;
- Collector, Normalizer, and Mapper unresolved dead-letter counts;
- failed runs within 24 hours;
- running jobs with a heartbeat older than two hours; and
- below-50% or above-200% row-count changes between comparable successful runs with the same job and scope.

The command performs no writes and exits non-zero when an alert is active. It makes current failure state visible without manually querying raw tables.

### Recoverability

An isolated PostgreSQL cluster was created under `/tmp`, all repository migrations were applied, and the guarded backup/restore script ran against a non-production source:

```text
backup restore: PASS
source_table_count=39
restored_table_count=39
canary=backup-restore-round-trip
```

The script is also wired into CI after migration application. This proves logical schema/data round-trip mechanics. A sanitized staging-volume restore with measured RPO/RTO remains required before launch.

### Operational runbook

The [private-beta operations runbook](13_Private_Beta_Operations_Runbook.md) defines daily commands, freshness objectives, alert rules, ownership, failure triage, backup/restore guardrails, pilot gating, privacy limits, and the minimum deployment/rollback contract.

## Live operational evidence

The read-only snapshot ran against the configured database at `2026-08-19T08:07:21.727406Z`.

| Source/stage | Latest | Age | Target | Rows | State |
|---|---|---:|---:|---:|---|
| SEC Company Facts | 2026-08-14 07:43Z | 120.40h | 168h | 186 | Fresh |
| SEC Submissions | 2026-08-13 21:11Z | 130.93h | 168h | 178 | Fresh |
| Filing index | 2026-08-14 08:29Z | 119.63h | 72h | 559 | **Stale** |
| Market prices | 2026-08-17 16:36Z | 39.52h | 96h | 10 | Fresh |
| Derived metrics | 2026-08-19 08:03Z | 0.06h | 168h | 8,622 | Fresh |

Unresolved evidence:

| Layer/stage | Type | Count | Treatment |
|---|---|---:|---|
| Collector/companyfacts | `NotInBulkArchive` | 4 | Review as source absence; resolve only with demonstrated classification/rerun |
| Normalizer | — | 0 | Clear |
| Mapper/calculate | `KeyError` | 20 | Code fix exists; persisted rows still require reconciliation |
| Mapper/expanded_metrics | `NotNullViolation` | 10 | Code fix exists; persisted rows still require reconciliation |
| Mapper/quality_flags | `NotNullViolation` | 4 | Investigate and add/identify regression before resolution |

Machine-readable evidence: [operational snapshot](evidence/day10_operational_snapshot_2026-08-19.json).

## 100-company pilot regression

The read-only preflight was rerun rather than relying only on Day 7 history. It exited `1` with:

```text
day6_universe_migration_not_deployed
insufficient_eligible_primary_companies:0/100
insufficient_submissions_payloads:10/100
unresolved_mapper_errors:34
representative_mapping_coverage_not_measured
projected_database_capacity_exceeded:1133382803/524288000
```

Machine-readable evidence: [pilot preflight](evidence/day10_pilot_preflight_2026-08-19.json).

This is a hard No-Go under the plan's wider-universe rule. Running a convenience batch and calling it the pilot would invalidate the denominator, coverage result, and capacity evidence.

## Five internally scripted usability sessions

No external participants were available in this execution context. Five automated browser-component sessions were therefore run as the plan permits:

1. Build and run a structured fundamental screen.
2. Interpret supported English, review/edit the structure, then execute.
3. Resolve ambiguity without premature execution.
4. Handle partial and fully unsupported language without a guessed query.
5. Distinguish loading, zero results, partial coverage, and API failure.

All five behavioral scripts pass through the 13-test frontend suite. They validate product state handling, not human comprehension or demand. External validation remains a beta blocker. Machine-readable record: [internal sessions](evidence/day10_internal_usability_sessions_2026-08-19.json).

## Automated verification

| Gate | Result |
|---|---|
| Pipeline default suite | PASS — 132 passed, 1 live test deselected |
| Backend suite | PASS — 22 passed; one existing test-client deprecation warning |
| Frontend tests | PASS — 13 passed |
| Backup/restore round trip | PASS — 39/39 tables and canary restored |
| Full frontend lint/build | PASS — ESLint clean; Next.js production build and TypeScript pass |
| Astro production build | PASS |
| Migration, docs, secrets, compile checks | PASS — 16 contiguous migrations, 225 links, 288 files secret-scanned, Python compilation clean |

## Ten-day exit-gate assessment

| Area | Decision | Evidence |
|---|---|---|
| Data correctness | CONDITIONAL | Strong automated golden-set coverage; unresolved Mapper rows require reconciliation; wider applicable coverage unproved |
| Universe and coverage | FAIL | Valid 100-company pilot blocked and not run |
| Product | PASS for current slice | Structured and supported-English browser flows are protected and explainable |
| Engineering | CONDITIONAL | Local gates pass; hosted CI proof and platform-specific deployment/rollback remain pending |
| Operations | FAIL | Visibility and restore mechanics now exist, but stale index, unresolved errors, retry aggregation, external alert sink, and scheduling remain open |
| User validation | FAIL | Five internal scripts, zero representative external sessions |

## Risk register and target dates

| Risk | Owner | Target | Exit evidence |
|---|---|---|---|
| Reconcile 34 Mapper dead letters, including 4 new quality-flag failures | Mapper Owner | 2026-08-21 | Smallest-scope rerun green; persisted rows resolved with linked regression evidence |
| Classify/reconcile 4 Company Facts archive absences | Collector Owner | 2026-08-21 | Each classified as expected source absence or recovered by rerun |
| Restore filing-index freshness and prove scheduled cadence | Data/Pipeline Owner | 2026-08-22 | Two consecutive scheduled successes inside 72h target |
| Deploy migration 0016 and generate eligible sample | Data/Product Owner | 2026-08-22 | Non-zero approved universe and deterministic 100-company manifest |
| Provision capacity above 1.133 GB projection with operating headroom | Infrastructure Owner | 2026-08-24 | Approved staging tier and capacity evidence |
| Configure durable logs/metrics, retry totals, alert routing, and immutable deployment rollback | Infrastructure + API Owners | 2026-08-24 | Test alert delivered; rollback drill recorded |
| Complete representative mapping preflight and 100-company pilot | Data/Mapper Owners | 2026-08-26 | ≥95% applicable coverage and ≥95% unhandled-error-free completion |
| Conduct five representative external usability sessions | Product Owner | 2026-08-28 | Task completion, confusion, and request log with no silent scope expansion |

Dates are management targets, not claims that external dependencies or participant availability are already secured.

## Conditions to reconsider No-Go

Reassess only after all of the following are demonstrated:

1. The operational status command is green or every remaining warning is explicitly accepted as visible and non-corrupting.
2. The valid 100-company pilot completes with the plan's error and coverage thresholds.
3. Mapper dead letters are reconciled, including the quality-flag failures.
4. Capacity is provisioned with headroom.
5. A real deployment, alert-delivery, and rollback drill succeeds.
6. Five representative users complete the core task, or leadership explicitly accepts external validation as the sole remaining conditional-go risk.

Until then, continue internal demonstration and engineering validation against the verified slice, but do not label it a private beta.

## Post-assessment feasibility

The five remediation workstreams were subsequently tested without mutating the configured database. The result is technically positive but sequence-dependent: see [`14_Blocker_Remediation_Feasibility_Test.md`](14_Blocker_Remediation_Feasibility_Test.md).
