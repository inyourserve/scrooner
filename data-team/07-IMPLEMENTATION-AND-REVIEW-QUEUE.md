# Repository integration and review queue specification

This is an implementation contract, not a claim that these components already exist. First inspect the existing cockpit, detectors, agents, tables and jobs. Extend them; do not build a parallel agent platform by default.

## Minimal interfaces
Use existing schemas when possible. The following are logical records, not invented current table names:
- Run: run ID, stage, start/finish, watermark, code/config/policy revisions, input/output counts, checks, errors, cost/calls where measured.
- Finding: finding ID, root-cause ID, issuer-period-concept/context, detection rule/version, severity, evidence, status, first/last seen.
- Proposal: decision contract, scoped rule/formula/config diff, prerequisites, affected outputs and lineage.
- Review: candidate revision/hash, independent reviewer, source evidence, verdict, failed checks and timestamp.
- Promotion: release policy/authorization reference, source batch, approved decisions, before/after versions, rollback, monitoring.
Store immutable events or retain full revision history; never overwrite the only copy of an approval or source value.

## Data adapter contract
Implement read-only methods for expected filing inventory, observed filings/watermarks, fact/context retrieval, canonical coverage, tag coexistence, candidate derivation inputs, downstream dependency impact and failed-run logs. Record actual SQL and bound parameters in audit artifacts, excluding secrets. Use safe parameter binding. Validate join cardinality and distinct issuer/fact counts before aggregating. A query plan is not a query result.

## Execution controls
Use deterministic idempotency keys and checkpoints. Claim tasks atomically or use existing job locks so two workers cannot promote the same batch. Detect stale source/policy revisions. Bound retry count; stop repeated deterministic failures and return diagnosis. Separate read-only discovery from staging writes and production promotion through actual credentials/permissions, not just prose instructions. Do not disable host permissions or safeguards to make an agent succeed.

## Review interface
Show original statement excerpt/link, accession, issuer, tag, taxonomy, context/dimensions, exact dates, unit/scale, source value, proposed canonical value, alternatives, competing facts, downstream metric diff and unresolved cases. Permit per-decision verify/reject/block; never provide only a blanket approve button. A batch approval must enumerate exact candidate hashes/revisions and exclusions. All actions require recorded identity and timestamp.

## Acceptance of the integration
Demonstrate one real read-only task with reproducible counts, one staging replay with before/after artifacts, one failed-check case that remains unpublished, one duplicate/retry that does not duplicate changes, one stale-proposal rejection and one rollback/replay on a test dataset. Verify child findings against the actual corrected condition before closing them. State unimplemented items explicitly. Do not connect live production merely to demonstrate the workflow.
