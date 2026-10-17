# Scrooner Operations Cockpit

Separate staff-only Django application. Financial truth is read through the `warehouse` database alias; Django authentication and sessions use `default`.

## Local setup

```bash
cd apps/admin
uv sync
cp .env.example .env
set -a; source .env; set +a
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver 127.0.0.1:8100
```

For live operational dashboards, set `WAREHOUSE_DATABASE_URL` to a read-only Postgres role. The local SQLite default is sufficient for authentication, workflow development, and health checks only.

The repository-local launcher reuses the existing pipeline database configuration without copying credentials into another file:

```bash
./scripts/run_local.sh
```

This mapping is for local development. Production must use a dedicated read-only warehouse credential.

## Security boundary

- Never use the Supabase service role as `WAREHOUSE_DATABASE_URL`.
- The warehouse role must have `SELECT` only on explicitly allowed tables/views.
- Warehouse queries are parameterized and bounded; coverage uses persisted daily snapshots.
- Django owns investigations, command requests, attempts, and append-only audit events in the `default` database.
- Command execution defaults to disabled. Set `OPS_COMMAND_EXECUTION_ENABLED=true` only for a deployment with an authenticated worker, narrow database permissions, and operational approval.
- Requesters cannot approve their own commands. Approval requires the `operations.approve_commandrequest` permission.

## Cockpit modules

- `/ops/pipeline/` — collector runs and unresolved collector/normalizer/mapper errors
- `/ops/quality/` — company findings and external sanity checks
- `/ops/companies/` — bounded company search and evidence inspection
- `/ops/mappings/` — canonical concept mapping and candidate coverage
- `/coverage/` — date-wise coverage scores and weak metrics
- `/ops/commands/` — idempotent, independently approved command requests
- `/ops/activity/` — date-filterable audit log and investigation count
- `/ops/work/` — canonical worker inbox, leases, attempts, evidence, and outcomes
- `/admin/` — staff, permissions, investigations, reviews, and detailed records

## Worker contract

Workers do not scan warehouse tables or run ad-hoc scripts to find work. The cockpit is the source of truth:

1. Schedule `python manage.py sync_work_queue` after validation jobs to ingest unresolved findings idempotently.
2. Claim one item with `POST /ops/worker/v1/claim/` and a dedicated bearer token.
3. Heartbeat before the 15-minute lease expires.
4. Append observations, root cause, patch, test, impact, and verification evidence.
5. Move through the allowed state machine; resolve only after verification.

The worker API never accepts arbitrary SQL, shell commands, or code. Production workers use a rotated secret from the deployment secret manager, not the local `.env` value.
