# Scrooner Private-Beta Operations Runbook

> **Status:** Beta-candidate runbook; production hosting and alert destination remain open decisions  
> **Date:** 2026-08-19  
> **Scope:** API request health, Collector/Normalizer/Mapper state, freshness, recovery, and beta release control

## Operating principle

Scrooner must fail visibly. A stale source, failed or stuck run, unresolved dead letter, anomalous row count, or elevated API error rate is an operational event—not an invitation to guess, hide a null, or continue a wider run.

The controls below do not log query strings, request bodies, authorization headers, or user identifiers. API telemetry is restricted to a server-generated request ID, HTTP method, route template, status, and duration.

## Daily checks

Run from `pipeline/`:

```bash
.venv/bin/scrooner-operations --fail-on-alert
```

Until the editable package is resynced, the equivalent source command is:

```bash
.venv/bin/python -m scrooner_pipeline.jobs.operations --fail-on-alert
```

The command is read-only and returns JSON. Exit `0` means no active rule fired; exit `1` means at least one alert requires triage.

API process telemetry:

```bash
curl --fail --silent https://<api-host>/health
curl --fail --silent https://<api-host>/health/metrics
```

Every HTTP response carries `X-Request-ID`. Search deployment logs for the matching `api.request.completed` event when investigating an error. `/health/metrics` is process-local and resets on restart; deployment logs are the durable integration point until a metrics backend is selected.

## Freshness objectives

| Source/stage | Target | Rationale | Primary owner |
|---|---:|---|---|
| SEC Company Facts | ≤168 hours | Current beta ingestion cadence; tighten after scheduling is proven | Data/Pipeline Owner |
| SEC Submissions | ≤168 hours | Current beta ingestion cadence | Data/Pipeline Owner |
| Filing index | ≤72 hours | Daily source with weekend/holiday allowance | Data/Pipeline Owner |
| Market prices | ≤96 hours | Daily bars with weekend/market-closure allowance | Market Data Owner |
| Derived metrics | ≤168 hours | Must follow the current weekly facts refresh during beta | Data/Pipeline Owner |

Any missing source or breach is an alert. Tighten these service objectives only after the scheduled job cadence is operating reliably; do not advertise fresher data than the control can prove.

## Alert rules and response

| Alert | Trigger | Immediate response | Escalation |
|---|---|---|---|
| `freshness_missing` / `freshness_stale` | Empty source or age above target | Stop affected refresh claims; inspect latest run and upstream availability | Data/Pipeline Owner immediately |
| `recent_failed_run` | Collector run failed within 24 hours | Open the run detail and dead letters; rerun only after cause is understood | Data/Pipeline Owner |
| `stuck_run` | Running with heartbeat older than 2 hours | Confirm process death, preserve evidence, then use the existing reap/resume mechanism | Data/Pipeline Owner |
| `unresolved_dead_letters` | Any unresolved Collector, Normalizer, or Mapper row | Classify as source absence, structural null, mapping gap, or code defect; reconcile by demonstrated rerun | Layer owner before beta |
| `row_count_anomaly` | Same successful job and scope changes below 50% or above 200% on a comparable count | Compare source volume and parameters; do not normalize the anomaly away | Data/Pipeline Owner |
| API server-error rate | Any sustained 5xx increase by route | Use request IDs to inspect logs, roll back application revision if introduced by deploy | Product API Owner |
| API latency | Material sustained change from the beta baseline | Check database latency and endpoint breakdown before scaling | Product API Owner |

Retry attempts are presently visible in selected structured events but are not durably aggregated per run. Durable per-run retry totals are a pre-beta operations backlog item.

## Failed-run investigation

```bash
.venv/bin/scrooner-report runs --limit 20
.venv/bin/scrooner-report run <run-id>
```

Required triage sequence:

1. Confirm the exact run ID, job, scope, start/finish time, heartbeat, duration, and stats.
2. Inspect tied errors and the relevant layer dead-letter count.
3. Determine whether the failure is upstream, structural, data-specific, or a code defect.
4. Add or identify an automated regression for code defects.
5. Rerun the smallest valid scope.
6. Mark historical evidence resolved only after the rerun proves the condition cleared.

Never delete failed runs or dead letters to make the dashboard green.

## Pilot regression gate

Before any wider-universe batch or beta decision:

```bash
.venv/bin/scrooner-pilot preflight --target 100 --database-limit-mb 500
```

Exit `1` blocks the wider pilot. Do not bypass eligibility, representative mapping coverage, submissions availability, dead-letter, or database-capacity gates.

## Backup and restore proof

The repository provides [`scripts/verify_backup_restore.sh`](../../scripts/verify_backup_restore.sh). It refuses to run unless:

- `SCROONER_ALLOW_EPHEMERAL_RESTORE=1`; and
- `PGDATABASE` clearly identifies a test, development, local, or staging database.

It creates a unique restore database, inserts a canary in the non-production source, creates a custom-format backup, restores it, compares table counts, verifies the canary, and removes only its own temporary objects. CI runs this after applying every migration.

Example against an isolated environment:

```bash
SCROONER_ALLOW_EPHEMERAL_RESTORE=1 bash scripts/verify_backup_restore.sh
```

A passing schema/canary exercise proves the mechanism. Before launch, repeat against a sanitized staging snapshot large enough to measure recovery time and record RPO/RTO.

## Deployment and rollback

Hosting is not selected, so there is no honest platform-specific deployment command yet. The minimum release contract is:

1. Deploy an immutable application revision only after all required CI jobs pass.
2. Apply additive, backward-compatible migrations before switching traffic.
3. Run `/health`, `/health/metrics`, one structured screen, one supported English interpretation, and an operational status check.
4. Promote the revision only if smoke checks and freshness/dead-letter gates are acceptable.
5. On application regression, route traffic to the immediately previous immutable revision and verify the same smoke checks.
6. Never roll a database backward destructively. Migrations are additive; correct schema problems with a reviewed forward migration.

Selecting the host, configuring an external log/metrics destination, and replacing these generic steps with tested platform commands are beta prerequisites owned by the Infrastructure Owner.

## Incident close-out

An incident is closed only when:

- user impact and affected data window are identified;
- source and code causes are separated;
- the smallest valid rerun is green;
- dead letters and freshness return to acceptable state;
- any defect has a regression test; and
- the evidence links the request ID or pipeline run ID to the resolution.
