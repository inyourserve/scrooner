# Blocker Remediation — Feasibility Test

> **Status:** COMPLETE — staged remediation is technically feasible; immediate 100-company execution is not  
> **Date:** 2026-08-19  
> **Safety boundary:** Live database and storage were queried read-only. All database writes were intercepted in memory or executed in an isolated PostgreSQL cluster under `/tmp`. No configured database row, migration, dead-letter state, filing record, metric, or storage object was changed.

> **Execution update:** The authorized first remediation phase was subsequently executed. See [`15_Blocker_Remediation_Execution_Evidence.md`](15_Blocker_Remediation_Execution_Evidence.md). This document remains the pre-write feasibility baseline.

## Executive verdict

The remediation program is **feasible**, but it is not one operation and should not be authorized as “run the 100-company pilot now.”

| Workstream | Feasibility verdict | Ready to execute live? |
|---|---|---|
| Reconcile dead letters | **High feasibility** | After adding a controlled reconciliation step and taking a pre-rerun snapshot |
| Restore scheduled freshness | **High technical feasibility** | No — production scheduler, secrets, and missed-run alert are not configured |
| Deploy universe migration | **High schema feasibility** | Yes with normal migration approval; it will not by itself create a 100-company universe |
| Provision capacity | **High feasibility** | Requires billing approval; current free quotas are insufficient |
| Complete valid 100-company pilot | **Conditional feasibility** | No — submissions, approved universe, representative coverage, and capacity gates must clear first |

The likely critical path is **5–8 focused working days**, plus enough elapsed time to prove two scheduled refresh cycles and any external data/vendor delays. This is an engineering estimate, not a delivery commitment.

## Test 1 — Dead-letter remediation

### Live classification

The 38 unresolved rows represent four failure classes, not 38 distinct active defects.

| Layer/stage | Rows | Distinct scope | Current interpretation |
|---|---:|---|---|
| Collector/companyfacts | 4 | Two CIKs observed twice | Expected official-source absence |
| Mapper/calculate | 20 | Golden ten × two historical catalog errors | Code path corrected |
| Mapper/expanded_metrics | 10 | Golden ten | Missing composite period dates corrected |
| Mapper/quality_flags | 4 | Four golden companies | Missing null-row period dates corrected |

The two Collector CIKs are Central Securities Corp (`0000018748`) and Connecticut Light & Power Co (`0000023426`). Current official SEC checks returned:

- Company Facts: HTTP `404` for both;
- Submissions: HTTP `200` for both.

They are therefore not transient Collector failures. They are valid evidence that the issuers have submissions histories but no SEC Company Facts resource. These rows can be reconciled as expected source absence; they must not be turned into fabricated facts or zeroes.

### Live-data, write-captured Mapper rehearsal

The current calculation functions were executed against live facts through a connection proxy that allowed `SELECT` but captured `INSERT`, `UPDATE`, and `DELETE` instead of sending them to PostgreSQL.

Results:

| Path | Scope | Result | Captured output quality |
|---|---|---|---|
| Generic calculate | Golden ten | 10 okay, 0 errored; 3,890 values and 1,672 explicit nulls | Historical `KeyError` did not recur |
| Expanded metrics | Golden ten | 10 okay, 0 errored; 21 values and 69 explicit nulls | 90/90 rows had non-null period dates |
| Quality flags | Four previously failing CIKs | 4 okay, 0 errored; 49 values and 41 explicit nulls | 90/90 rows had non-null period dates |

### Feasibility finding

The rerun itself is ready. The missing operational piece is a safe reconciliation command. Current CLIs can show dead letters but do not mark a historical row resolved after a proven rerun. Direct ad-hoc `UPDATE ... SET resolved=true` would be difficult to audit and should not become the normal procedure.

Recommended live sequence:

1. Export the 38 unresolved rows as immutable pre-rerun evidence.
2. Add a reconciliation command that accepts layer, stage, CIK, evidence note, and successful rerun timestamp.
3. Rerun only the golden ten Mapper stages.
4. Run global lineage validation and compare metric counts/checksums.
5. Resolve only error rows whose exact stage/CIK rerun succeeded.
6. Classify the four Collector rows as expected official-source absence with the SEC status evidence.

Estimated effort: **0.5–1 day**. Risk: low for code execution, medium for audit discipline.

## Test 2 — Scheduled freshness

The most recent official SEC daily index was discovered as `2026-08-18` and parsed successfully:

```text
index_rows=5,551
golden_matches=152
forms=144, 4, 424B2, 424B3, 424B8, FWP
```

This proves the upstream endpoint, User-Agent, rate limiting, date discovery, format parser, and golden-CIK filter still work. The stale database state is not caused by an inaccessible SEC feed or a parser break.

The repository has a weekly scheduled **contract test**, but no scheduled ingestion workflow. Therefore the freshness blocker is operational: nothing invokes `scrooner-incremental daily` in production.

GitHub Actions is a feasible provisional scheduler, but GitHub explicitly warns that scheduled runs can be delayed or even dropped under load and only run from the default branch. It therefore needs an independent stale-data alert rather than being treated as its own proof of success. [GitHub schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

Minimum feasible implementation:

- daily incremental filing-index run at a non-top-of-hour minute;
- daily market-price refresh on trading days;
- metric recomputation after successful facts/price refresh;
- `scrooner-operations --fail-on-alert` after every run;
- alert delivery independent from the scheduled job; and
- two consecutive successful scheduled cycles before changing freshness to green.

Estimated implementation: **0.5–1 day**, plus **2 elapsed days** of proof. Risk: medium until an external alert destination is configured.

## Test 3 — Universe migration

Migration `0016_production_universe.sql` was applied twice to an isolated pre-0016 database containing two companies and three listings.

```json
{
  "companies": 2,
  "filers": 2,
  "listings": 3,
  "securities": 3,
  "linked_listings": 3,
  "snapshot_tables": 2
}
```

The second application completed using the intended conflict/idempotence paths. Every listing was linked to a security, and the filer/security/snapshot structures existed as expected.

The exact current live listing data was also passed through the universe policy without persisting it:

| Result | Count |
|---|---:|
| Listing candidates | 38 |
| Eligible | 9 |
| Excluded | 19 |
| Uncertain | 10 |
| Eligible primary companies | **7** |

The difference between 9 eligible listings and 7 eligible primaries is material. Alphabet's two eligible share classes remain primary-ambiguous; TSM and Enbridge remain uncertain because foreign-filer/ADR scope is open. Deploying the migration is feasible, but deploying it today would still leave the pilot at 7/100 eligible primary companies.

Estimated deployment and verification: **0.25–0.5 day** after backup and migration approval. Populating a valid universe is a separate data-acquisition and product-policy task.

## Test 4 — Capacity

### Current and projected usage

| Resource | Current | 100-company projection or next-step estimate |
|---|---:|---:|
| PostgreSQL database | 157.58 MB | 1.133 GB |
| Raw object storage | 693.13 MB | ~1.266 GB after 90 more submissions CIKs |
| Company Facts objects | 629.49 MB | Existing 174 CIK payload set is already sufficient as a candidate pool |
| Submissions objects | 63.63 MB across 10 CIKs | Roughly +572.69 MB for 90 more at the observed average |
| Current SEC submissions archive | — | 1,558,873,846 bytes to download before extraction |

The object-storage estimate is directional because continuation-page counts vary substantially by filer; JPM alone has many historical pages. It is sufficient for the decision: both the database projection and likely object-storage total exceed free-plan gates.

As of this feasibility test, Supabase's Free plan includes a 500 MB database-size quota and 1 GB object storage. Pro starts at **$25/month**, includes an **8 GB database disk**, **100 GB object storage**, and seven days of daily backups. The 1.133 GB database projection and ~1.266 GB object estimate fit within those included Pro allocations with substantial headroom. [Supabase pricing](https://supabase.com/pricing), [database/disk behavior](https://supabase.com/docs/guides/platform/database-size), [disk pricing](https://supabase.com/docs/guides/platform/manage-your-usage/disk-size)

### Feasibility finding

Capacity is not an architecture blocker for the 100-company pilot. It is a **billing-approval blocker**. The minimum responsible choice is Supabase Pro or a separately provisioned PostgreSQL/storage environment with equivalent backup and headroom. Staying on Free while attempting the valid pilot is not feasible.

Estimated action time: same day after approval. Minimum current platform cost: **$25/month**, subject to the account's actual organization/project configuration and future pricing.

## Test 5 — Valid 100-company pilot

Current inputs:

```text
Company Facts CIKs             174
Submissions CIKs                10
Eligible primary companies       0 persisted / 7 simulated
Representative mapping coverage  not measured
Unresolved Mapper rows           34
```

The Company Facts candidate pool is likely large enough, but eligibility cannot be assumed from XBRL presence. The responsible path is to collect submissions for the full 174-CIK candidate pool, normalize identity/listings/status, classify securities, build the universe, and only then determine whether at least 100 eligible primary companies exist.

The current SEC `submissions.zip` is about **1.559 GB**, and there is no cached local copy. Download/extraction is therefore a real operational prerequisite, not a small API call.

### Feasible pilot sequence

1. Approve and provision capacity.
2. Reconcile existing dead letters.
3. Deploy migration 0016.
4. Collect submissions for all 174 Company Facts candidate CIKs.
5. Normalize identity, listing, status, and filing metadata.
6. Run security classification and resolve ADR/foreign-filer and multi-class-primary policy decisions.
7. Build the dated universe snapshot.
8. If fewer than 100 eligible primaries remain, expand the candidate pool before sampling.
9. Produce the deterministic stratified 100-company manifest.
10. Run mapping preflight on that exact manifest and curate applicable coverage to at least 95%.
11. Execute in waves of 10, 25, 50, and 100, stopping on any systemic identity, period, lineage, or formula defect.
12. Reconcile ten stratified companies manually and publish completion/error/null-reason evidence.

Estimated effort after capacity approval: **3–6 days**, with uncertainty concentrated in security classification and mapping gaps. Risk: medium-high until the 100-company manifest and coverage report exist.

## Recommended critical path

```text
Billing + backup approval
        ↓
Dead-letter reconciliation mechanism and golden-ten rerun
        ↓
Migration 0016 deployment
        ↓
174-CIK submissions acquisition and identity/security normalization
        ↓
Universe decisions and deterministic 100-company manifest
        ↓
Representative mapping preflight
        ↓
10 → 25 → 50 → 100 staged pilot
```

Freshness scheduling can proceed in parallel after secrets and an alert destination are approved.

## Authority required before execution

This feasibility test does **not** authorize the following state changes:

- upgrading the Supabase plan;
- deploying migration 0016 to the configured database;
- scheduling workflows with production secrets;
- rerunning write-producing Mapper or Collector jobs;
- resolving historical dead-letter rows; or
- downloading/uploading the 1.559 GB submissions archive.

Those actions are feasible, but each needs explicit execution approval because they change billing, database state, external schedules, or stored data.

## Final consultant recommendation

Proceed with remediation. Do not proceed directly to the 100-company run.

The blockers are not evidence that the product architecture is unworkable. They show that the project has reached the point where infrastructure, operational reconciliation, and representative data acquisition—not more UI work—control the critical path.

Machine-readable results: [`evidence/blocker_remediation_feasibility_2026-08-19.json`](evidence/blocker_remediation_feasibility_2026-08-19.json).
