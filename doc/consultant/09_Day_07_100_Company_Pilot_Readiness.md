# Day 7 — 100-Company Pilot Readiness and Stop Decision

> **Status:** NO-GO at preflight; the 100-company write-heavy pilot was correctly not launched.  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 7

## Executive decision

Do not run the 100-company Collector-to-Mapper pilot in the current production database.

This is not a schedule failure. It is the Day 7 stop condition working correctly. The live read-only preflight found that the approved Day 6 universe is not deployed, only ten companies have submissions payloads, mapping coverage has not passed its ≥95% gate, 20 historical Mapper dead letters remain unresolved, and the projected database footprint is approximately 1.13 GB against the documented 500 MB limit.

Launching anyway would produce a non-stratified, eligibility-unknown sample and would likely exhaust database capacity before the run completed.

## What was built

Day 7 now has a reusable read-only pilot toolkit:

- `scrooner-pilot preflight` — fails non-zero unless universe, raw payload, mapping, dead-letter, and capacity gates all pass
- `scrooner-pilot sample` — selects exactly 100 distinct companies from the latest approved Day 6 universe
- `scrooner-pilot mapping-preflight` — reads already-stored Company Facts objects and reports curated-tag presence without normalization or writes
- A deterministic sample algorithm that covers rare strata first, then balances underrepresented strata
- Explicit market-cap, SIC-sector, fiscal-calendar, filing-regime, issuer-kind, multi-class, and amendment strata
- A fixed failure taxonomy: code defect, mapping gap, unavailable filing data, universe error, expected structural null, upstream-source failure, and unreviewed
- 22 new automated tests

The selector never substitutes “first 100 CIKs” for a stratified sample and never selects from raw ticker data when Day 6 eligibility is absent.

Final repository verification remains green: 125 offline pipeline tests and 13 backend tests pass, the Astro production build succeeds, all 200 local documentation targets resolve, and the secret-pattern check covers 243 text files.

## Live read-only inventory

The executable preflight returned:

| Measure | Actual |
|---|---:|
| Raw company-universe rows | 10,396 |
| Distinct stored Company Facts CIKs | 174 |
| Distinct stored submissions CIKs | 10 |
| Companies with normalized facts | 8 |
| Database size | 157,117,587 bytes (~149.8 MiB) |
| Scalable pipeline tables | 84,467,712 bytes (~80.6 MiB) |
| Unresolved Normalizer errors | 0 |
| Unresolved Mapper errors | 20 |
| Day 6 universe schema deployed | No |
| Eligible primary companies measurable | 0 |

The 174 Company Facts payloads came from prior Collector activity, including a successful 147-CIK batch. They do not have matching submissions coverage and were not selected using Day 6 security eligibility or stratification rules.

Full machine-readable evidence: [`evidence/day7_preflight_2026-08-18.json`](evidence/day7_preflight_2026-08-18.json).

## Capacity projection

The five scalable relations used for the estimate are `core.fact`, `core.period`, `core.filing`, `analytics.canonical_fact`, and `analytics.metric_value`.

Current observed footprint:

```text
84,467,712 bytes / 8 normalized companies
= 10,558,464 bytes per normalized company
```

Linear 100-company estimate:

```text
current database                              157,117,587
92 additional companies × 10,558,464          971,378,688
projected database                          1,128,496,275 bytes
documented limit                              524,288,000 bytes
```

The projection is deliberately simple and should be treated as directional, but the result exceeds the limit by more than 2×. Estimation error cannot reasonably reverse the decision.

At the hard 500 MiB ceiling, observed density permits only about 34 additional normalized companies. At an 80% operational safety threshold, it permits about 24 additional companies. Ownership expansion would reduce that headroom further and is not included in the projection.

## Mapper dead-letter finding

There are 20 unresolved historical Mapper rows:

- Ten `calculate` `KeyError('net_debt_ebitda')` failures
- Ten `expanded_metrics` `NotNullViolation` failures caused by null `period_start`/`period_end`

The current code contains fixes for both defect classes and automated regression coverage. However, the persisted rows remain `resolved=false`. They should be rerun and reconciled before a wider batch; deleting or marking them resolved without proof would erase operational evidence.

## Safe 100-payload mapping preflight

The preflight read the first 100 distinct latest Company Facts objects already stored in project storage. It made no database writes and had zero download failures.

This was not the Day 7 sample: it is CIK-ordered, not stratified or eligibility-filtered. Its taxonomy mix confirms the problem:

- 95 contain `us-gaap`
- 3 contain `ifrs-full`
- 20 contain `invest`
- 1 contains `cef`

Curated tag-presence results:

| Concept | Present |
|---|---:|
| Cash and equivalents | 93% |
| CFO | 93% |
| Net income | 93% |
| Shares outstanding | 93% |
| Stockholders' equity | 93% |
| Income tax expense | 92% |
| Revenue | 91% |
| Income before tax | 90% |
| Diluted EPS | 89% |
| Total debt | 87% |
| Interest expense | 84% |
| Operating income | 79% |
| Dividends per share | 79% |
| Capex | 77% |
| Current assets/liabilities | 76% |
| Gross profit | 60% |

These are tag-presence rates, not formula-ready coverage. They do not validate periods, units, contexts, authority, TTM continuity, or structural applicability. No concept reached 95%, so this check cannot satisfy the mapping gate; it only identifies where curation and cohort definition are required.

Full machine-readable evidence: [`evidence/day7_mapping_presence_100_2026-08-18.json`](evidence/day7_mapping_presence_100_2026-08-18.json).

## Current preflight blockers

```text
day6_universe_migration_not_deployed
insufficient_eligible_primary_companies:0/100
insufficient_submissions_payloads:10/100
unresolved_mapper_errors:20
representative_mapping_coverage_not_measured
projected_database_capacity_exceeded:1128496275/524288000
```

Company Facts count is not a blocker by itself—174 payloads exist—but those payloads do not form an approved pilot cohort.

## Required sequence to unblock Day 7

1. Review and deploy migration `0016_production_universe.sql` to a staging or target database.
2. Run the Day 6 universe builder and publish eligible/excluded/uncertain counts.
3. Resolve the ADR/20-F/40-F product decision or retain those candidates outside the pilot denominator.
4. Ensure at least 100 companies have an unambiguous eligible primary security.
5. Generate the deterministic sample manifest with `scrooner-pilot sample`.
6. Run mapping presence over that exact manifest and define which absences are expected structural nulls.
7. Curate mapping gaps until the representative ≥95% gate passes for applicable required concepts.
8. Rerun the golden set with current code and reconcile the 20 historical dead-letter rows.
9. Move the pilot to a database tier/environment with at least the projected headroom, or approve a smaller 25-company wave as a separate experiment.
10. Collect matching submissions and Company Facts payloads for the approved manifest before normalization begins.
11. Only then run Normalizer and Mapper stages, stopping immediately on a systemic identity, period, lineage, or formula defect.

## Commands

Run from `pipeline/` so local environment settings load correctly:

```bash
.venv/bin/scrooner-pilot preflight --target 100 --database-limit-mb 500
.venv/bin/scrooner-pilot sample --target 100
.venv/bin/scrooner-pilot mapping-preflight --limit 100
```

The first command intentionally exits `1` while blockers remain. This makes the decision automatable in CI or an operational runbook.

## Day 7 Definition of Done

| Gate | Result |
|---|---|
| Deterministic stratified selector | PASS — implemented and tested |
| Failure taxonomy | PASS — implemented and tested |
| Capacity estimated from live database | PASS — 1.13 GB projected |
| Existing 100-payload mapping preflight | PASS — read-only, zero download failures |
| Eligible 100-company manifest | BLOCKED — Day 6 migration not deployed |
| ≥95% applicable mapping coverage | BLOCKED — not measured on an eligible sample; convenience batch is below 95% |
| Matching submissions for 100 companies | BLOCKED — 10 distinct CIKs available |
| Unresolved dead letters cleared by demonstrated rerun | BLOCKED — 20 remain |
| Collector-to-Mapper run for 100 eligible companies | NOT RUN — unsafe and invalid under current gates |
| Ten stratified manual reconciliations | NOT RUN — requires the valid completed pilot |

## Consultant assessment

The correct Day 7 outcome is **No-Go for the 100-company execution today**. The project gained an executable selection and readiness layer, quantified real coverage using existing official payloads, and prevented an expensive false milestone.

The fastest responsible next move is not to weaken the gate. It is to deploy Day 6 in a non-production environment, reconcile the fixed dead letters, make the foreign-filer decision, and either provision enough database capacity for 100 companies or explicitly authorize a 25-company staging wave. Day 8 UI work can proceed independently against the existing verified API while these data gates are cleared.
