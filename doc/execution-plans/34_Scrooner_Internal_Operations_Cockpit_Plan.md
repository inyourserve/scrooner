# Scrooner Internal Operations Cockpit — Scalable Django Plan

**Status:** Proposed  
**Owner:** Internal operations  
**Scope:** A separate, staff-only Django control plane for inspecting and operating Scrooner. It does not replace the Next.js product, FastAPI product API, or pipeline workers.

## 1. Outcome

Build an internal cockpit that answers four questions quickly and safely:

1. Is the data pipeline healthy right now?
2. Is coverage and correctness improving or regressing by date and dataset version?
3. Why is a company, filing, concept, metric, or screen result wrong or missing?
4. What controlled action can an authorized operator take, and who approved it?

The cockpit must remain useful at millions of facts and findings. It must never depend on an unbounded table scan, run a pipeline stage inside an HTTP request, or allow an accidental Django Admin edit to mutate financial truth.

## 2. Architectural decision

Create a new deployable application:

```text
apps/admin/
  manage.py
  config/                 # settings, URLs, ASGI/WSGI, security
  cockpit/                # overview and cross-domain navigation
  coverage/               # snapshots, gaps and regression views
  pipeline_ops/           # runs, stages, failures and retries
  data_quality/           # findings, sanity checks and incidents
  company_inspector/      # company → filing → facts → metrics lineage
  mappings/               # concepts, tags, candidates and overrides
  product_ops/            # datasets, templates, entitlements, usage
  audit/                   # immutable action and approval history
```

```text
Customer plane                 Internal control plane
Next.js → FastAPI ─┐           Django cockpit ───────┐
Pipeline workers ──┼──────────→ Supabase Postgres ←─┤
Scheduled jobs ────┘                    ↑             │
                                  Redis/job queue ←───┘
```

Boundaries:

- Next.js remains the customer experience.
- FastAPI remains the customer-facing product API.
- Pipeline packages remain the only owners of financial transformation logic.
- Django provides staff authentication, navigation, inspection, approvals and safe command dispatch.
- Django models for `raw`, `core`, `analytics` and existing `app` tables are read-only and `managed = False`.
- New cockpit-owned records live in an `ops` schema.
- All expensive summaries are persisted snapshots, summary tables or narrowly scoped queries.

## 3. Technology choices

| Concern | Choice | Reason |
|---|---|---|
| Web application | Django with Django Admin plus custom views | Mature staff workflows, permissions, forms and list filtering |
| UI | Django templates, shared Scrooner tokens, small HTMX enhancements | Fast server rendering without building a second SPA |
| Database | Existing Supabase Postgres through its pooler | One source of truth; no replica system in phase one |
| Sessions and caching | Existing Redis, distinct `admin:` key namespace | Shared infrastructure with strict logical separation |
| Background work | Queue-backed command dispatcher and dedicated worker | No long-running work in HTTP requests |
| Authentication | Company SSO/OIDC when available; staff-only fallback initially | Central revocation, MFA and no customer-session ambiguity |
| Observability | Structured logs, request IDs, audit events, queue metrics | End-to-end operational traceability |

Do not install a large third-party admin theme initially. Establish the information architecture and Scrooner design tokens first; a theme must not dictate the data model or workflows.

## 4. Access and security model

The cockpit is not merely another authenticated product route.

### 4.1 Network and identity

- Deploy on a separate internal hostname, for example `ops.scrooner.com`.
- Put it behind an identity-aware proxy or VPN where practical.
- Require staff identity, verified email and MFA.
- Never accept customer Supabase sessions as staff authorization.
- Use short-lived sessions with secure, HTTP-only, same-site cookies.
- Disable public signup and password-reset enumeration.

### 4.2 Roles

| Role | Capabilities |
|---|---|
| Viewer | Read dashboards and drill-down views |
| Analyst | Add investigation notes and propose mapping decisions |
| Operator | Dispatch allow-listed reruns and retries |
| Approver | Approve high-impact mapping, override and publish actions |
| Administrator | Manage staff access and emergency controls |

Permissions must be action-specific, not a single `is_staff` switch. Dataset publishing, bulk recomputation and truth overrides require two-person approval once the team has more than one qualified operator.

### 4.3 Database roles

- `scrooner_ops_read`: `SELECT` only on allow-listed existing views/tables.
- `scrooner_ops_write`: insert/update only on explicitly cockpit-owned `ops` tables.
- `scrooner_ops_worker`: execute approved command-claim functions and write action results.
- No cockpit role receives broad ownership, `BYPASSRLS`, service-role access or direct delete rights on financial truth tables.
- Production defaults to read-only. Mutation features remain feature-flagged until their audit and approval tests pass.

## 5. Cockpit-owned data model

Add these tables through the repository's canonical SQL migration path. Use `bigint generated always as identity` primary keys for local append-heavy tables and UTC `timestamptz` timestamps.

### 5.1 `ops.staff_profile`

- One row per staff identity.
- External identity subject, display name, role, enabled state, last login.
- Unique external subject and normalized email indexes.
- Disabling a profile immediately blocks cockpit access.

### 5.2 `ops.audit_event`

Append-only record for login, view of sensitive records, proposal, approval, command dispatch and result.

Required fields:

- actor identity and effective role
- event type and target type/id
- request/correlation ID
- structured before/after JSON where applicable
- IP/user agent metadata with a defined retention policy
- UTC creation timestamp

Application roles receive insert/select only—no update or delete. Retention/archival is a separately privileged maintenance operation.

### 5.3 `ops.command_request`

Durable command state machine:

```text
draft → pending_approval → approved → queued → running → succeeded
                                                └────→ failed
                     rejected / cancelled / expired
```

Fields include command type, validated parameters, requested/approved actors, idempotency key, priority, timestamps, worker lease, result summary, output artifact reference and error classification.

Indexes:

- `(status, priority desc, created_at)` for worker claims
- `(command_type, created_at desc)` for operational history
- unique partial idempotency key for active commands

Workers claim jobs with `FOR UPDATE SKIP LOCKED`. Retries create explicit attempts; they do not overwrite failure history.

### 5.4 `ops.command_attempt`

One append-only row per attempt with start/end time, worker identity, exit classification, metrics and bounded log/artifact references. Large logs belong in object storage, not Postgres JSON.

### 5.5 `ops.investigation`

Tracks a human investigation attached to a company, filing, concept, metric, finding, incident or pipeline run. Includes owner, status, severity, conclusion and links to evidence. Comments are append-only child records.

### 5.6 `ops.approval`

Records proposal, reviewer, decision, reason and immutable payload hash. The requester cannot approve their own high-impact action.

## 6. Read models and scalability

Do not let Django Admin introspect and expose every database table automatically.

### 6.1 Existing truth tables

Create explicit unmanaged Django models only for fields needed by an operational screen. Mark all financial truth model admins read-only:

- deny add/change/delete permissions
- remove bulk delete actions
- use explicit `list_display`, `list_filter`, `search_fields` and `autocomplete_fields`
- never render large JSON/blob fields in list views
- defer heavy columns and load them only on detail pages

### 6.2 Operational views

Prefer stable SQL views or summary tables for cross-domain screens:

- latest pipeline status by stage
- latest coverage score and prior-date delta
- coverage regression ranking
- unresolved findings by severity/source
- company investigation summary
- latest dataset publication status
- mapping candidate review queue

Materialize only proven expensive aggregations. Refresh materialized views asynchronously after the relevant pipeline stage; never refresh them synchronously during a page request.

### 6.3 Query rules

- Default every list to a recent bounded time window.
- Use keyset pagination for high-volume tables such as facts, findings and logs.
- Avoid exact `COUNT(*)` on very large filtered tables in normal page rendering.
- Put equality predicates before range/order columns in composite indexes.
- Require `EXPLAIN (ANALYZE, BUFFERS)` evidence on representative production-scale data before adding a cockpit query to a hot page.
- Set a low cockpit statement timeout; export/report jobs use the worker path.
- Enforce maximum export rows and store generated exports with expiry.

### 6.4 Connection management

- Connect through the existing Supabase pooler.
- Keep Django persistent connections bounded and shorter than pooler idle timeouts.
- Size web and worker pools independently.
- Add pool saturation, query timeout and slow-query metrics before enabling mutation workflows.

## 7. Information architecture

### 7.1 Operations overview

The landing page answers “Are we healthy?” in under ten seconds:

- current dataset version and publish age
- latest scheduled pipeline state
- stage duration versus trailing baseline
- coverage scores and change versus prior snapshot
- open critical/high findings
- failed commands and retries
- stale sources or overdue jobs

Every summary links to the exact filtered investigation page.

### 7.2 Coverage command center

- Daily coverage score history from `analytics.coverage_snapshot`
- Core, all-metric and concept scores
- Largest positive and negative changes by date
- Weakest metrics by corrected applicable population
- Gap-reason distribution
- Drill-down metric → missing companies → expected/structural/unexplained cause
- Dataset-version comparison
- CSV export through a bounded background job

The Next.js coverage page remains a lightweight summary. Django becomes the detailed operational version.

### 7.3 Pipeline operations

- Scheduled run calendar and date-wise run log
- Stage timeline with duration, row counts and status
- Collector/normalizer/mapper/sanity failures
- Dead-letter queues grouped by signature
- Retry eligibility and attempt history
- Worker heartbeat and queue depth
- Git SHA, dataset version and configuration fingerprint for every run

### 7.4 Company inspector

One navigation chain:

```text
Company
 ├─ listings and universe status
 ├─ filings and raw-object references
 ├─ periods and facts
 ├─ canonical mappings and lineage
 ├─ statement lines and metrics
 ├─ sanity findings and overrides
 └─ screening snapshot representation
```

Provide side-by-side period comparison and provenance links. Do not allow raw fact editing.

### 7.5 Data quality and incidents

- Unified findings inbox
- Severity/source/status/date filters
- Accounting identity failures
- Plausibility, outlier, freshness, split and period-completeness checks
- Assignment, notes, resolution reason and evidence
- Incident timeline linked to dataset and pipeline versions

### 7.6 Mapping review

- Canonical concepts and active mappings
- SEC tag library and candidate rankings
- Company-specific preferences
- Proposed mapping diff with expected coverage impact
- Approval workflow and rollback reference

Mapping changes are proposals first. Approved changes are applied by a versioned pipeline command—not a direct Django model save.

### 7.7 Product operations

- Screening dataset versions and publish readiness
- Natural-language templates and interpretation diagnostics
- Saved-screen/run troubleshooting by user ID with strict support permissions
- Entitlement and usage inspection
- Cache health and safe invalidation actions

Sensitive user data access is separately permissioned and audited.

## 8. Safe action framework

Every action is an allow-listed command with a typed schema. No arbitrary shell, SQL or Python console is exposed in production.

Each command defines:

- required permission
- parameter schema and maximum scope
- whether approval is required
- idempotency behavior
- dry-run support
- timeout and retry policy
- concurrency key
- success evidence
- rollback or compensating action

Initial allowed actions:

1. Retry one failed filing/stage.
2. Recompute one company or a bounded company set.
3. Rebuild a coverage snapshot for one date.
4. Invalidate a narrow cache key.
5. Propose/approve a mapping or sanity override.
6. Publish a prepared dataset version after readiness gates pass.

Bulk or destructive actions stay disabled until approval, audit and restore drills have been demonstrated.

## 9. Date-wise logs

There are three distinct histories; do not collapse them into one vague log:

1. **Data-state history:** existing daily coverage snapshots and dataset versions.
2. **Execution history:** pipeline runs, stages, attempts, durations and outputs.
3. **Human-action history:** investigations, approvals, commands and audit events.

All use UTC timestamps. UI may display the staff member's timezone but always shows the timezone explicitly. Date filters use half-open ranges (`>= start`, `< next_day`) to avoid boundary ambiguity.

Retention proposal:

- aggregate coverage and dataset history: indefinite
- command/audit metadata: minimum seven years unless policy changes
- detailed application logs: hot 30–90 days, archived afterward
- generated exports: short expiry with explicit download audit

## 10. UX system

- Reuse Scrooner tokens for typography, spacing, status colors and tables.
- Dense, quiet, keyboard-accessible operational UI.
- Global command/search palette for company, filing, CIK, ticker, run ID and incident ID.
- Saved filters and shareable URLs for every list view.
- Column preferences per staff user.
- Status color is never the sole carrier of meaning.
- Dangerous actions use explicit scope summaries and confirmation; approval is separate from confirmation.
- Mobile supports emergency inspection, but complex mutation workflows may require desktop.

## 11. Observability and service objectives

Initial cockpit objectives:

- overview p95 server response under 800 ms
- normal filtered list p95 under 1 second
- no request query above the configured statement timeout
- command enqueue under 500 ms; execution time reported separately
- 100% of mutations produce an audit event and correlation ID
- 100% of worker attempts end in a terminal or recoverable leased state

Instrument:

- request latency/status by route
- database query latency and timeouts
- pool occupancy
- cache hit rate
- queue depth and oldest queued age
- worker heartbeat and command duration
- login and permission denials
- audit-write failures as critical alerts

## 12. Delivery phases

### Phase 0 — Contracts and threat model

- Inventory operational tables, volumes and representative query plans.
- Lock roles, mutation boundaries and sensitive-data classification.
- Decide SSO/IAP and worker deployment mechanism.
- Document backup/restore and emergency-access procedure.

**Exit:** approved architecture, threat model and database-role matrix.

### Phase 1 — Secure read-only foundation

- Scaffold `apps/admin` with environment-separated settings.
- Add staff identity, RBAC, audit middleware, request IDs and health checks.
- Configure read-only database role and Redis namespace.
- Implement shared tokens, navigation and global search shell.
- Add deployment and CI smoke tests.

**Exit:** staff can sign in and access only permitted read-only pages; no truth-table mutation is possible.

### Phase 2 — Operations and coverage

- Operations overview.
- Full coverage command center with date-wise history.
- Pipeline run/stage history and failures.
- Data-quality inbox and bounded exports.

**Exit:** daily operational review can be completed entirely in the cockpit.

### Phase 3 — Investigation workflows

- Company inspector and lineage drill-down.
- Investigation ownership, notes and status.
- Mapping candidate review and impact preview.
- Incident timelines.

**Exit:** a data discrepancy can be traced from company output to source evidence without manual SQL.

### Phase 4 — Controlled actions

- Command request/attempt tables and worker.
- Dry runs, idempotency, leases, retry rules and cancellation.
- Approval workflow and action audit.
- Start with single-company recompute and narrow retry.

**Exit:** operators can safely execute the initial allow-list with complete audit evidence.

### Phase 5 — Hardening and scale

- Load tests on production-scale copies.
- Query-plan regression tests and index review.
- Backup/restore, worker-crash and expired-lease drills.
- SSO/MFA enforcement, IAP/VPN, security review.
- Materialized read models only where measurements justify them.

**Exit:** signed production-readiness checklist and operator runbook.

## 13. Testing strategy

- Unit tests for permissions, state transitions and command validation.
- Integration tests against an isolated Postgres database for all operational queries.
- RLS/grant tests proving read roles cannot mutate truth tables.
- Query-plan tests for high-volume list pages.
- Browser tests for login, filtering, investigation and approval flows.
- Worker tests for idempotency, lease expiry, retry and duplicate delivery.
- Audit completeness tests: every mutation must have actor, target, request ID and result.
- Restore tests for cockpit-owned schema and archived artifacts.

CI must fail on unbounded admin query patterns, missing list pagination, mutable truth-model registration, missing permission declarations or unaudited command types.

## 14. First implementation slice

Build the smallest slice that proves the architecture:

1. `apps/admin` Django scaffold and Docker/runtime entry point.
2. Staff authentication and Viewer role.
3. Explicit read-only database connection.
4. Operations overview.
5. Coverage history, weakest metrics and regression pages.
6. Pipeline-run list/detail.
7. Append-only access audit.
8. CI, health check and deployment documentation.

Do not implement retries or mutations in this slice. Establish safe visibility first.

## 15. Definition of done

The cockpit is production-ready only when:

- it is independently deployable from the customer application;
- staff identity, MFA/SSO path and role permissions are enforced;
- financial truth tables are read-only from the web process;
- all lists are bounded and indexed with production-scale query evidence;
- coverage, run and action history are date-wise and durable;
- no pipeline work executes in an HTTP request;
- every controlled action is typed, queued, idempotent and audited;
- approval-required actions cannot be self-approved;
- backup/restore and worker-failure drills pass;
- operational documentation names owners and escalation paths.

## 16. Recommendation

Proceed with Phases 0–2 first. They deliver the highest leverage: one secure place to understand pipeline health, coverage direction and failures. Keep the existing Next.js data-coverage page as a lightweight product-side summary, while the Django cockpit becomes the durable internal system of record for operations, investigation and—only after hardening—controlled actions.
