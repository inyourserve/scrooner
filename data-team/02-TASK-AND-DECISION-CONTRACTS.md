# Task and handoff contracts

Use JSON artifacts where a machine consumer exists; otherwise use the same fields in a concise table. Extend existing repository contracts instead of creating a parallel database. These are proposed interfaces, not claims about current tables.

## task.json
Required: task_id, role, objective, universe_definition, period_window, as_of, input_refs, policy_version, allowed_actions, acceptance_checks, budget (case_limit, tool_call_limit, max_llm_cost_usd or null), owner.
If cost telemetry is unavailable, do not invent spend. Cap calls and report cost as unknown.

## decision.json
Required:
- decision_id, task_id, kind (mapping/derivation/template/engineering/coverage/release), status (proposed/verified/approved/rejected/blocked)
- scope: issuer IDs, concepts, periods, taxonomy versions, dimensions and exclusions as relevant
- evidence: list of {ref, locator, source_type, source_hash or null}; synthetic fixtures must be identified as synthetic
- rationale, alternatives_considered, unresolved_questions
- impact: affected issuers, periods, cells and downstream metrics, each null if not measured
- checks: list of {name, passed: boolean, artifact_ref}
- proposed_by, reviewed_by (null until reviewed), policy_version, code_revision, created_at
- next_action, rollback_ref (null for read-only work)
Use append-only decisions with supersedes IDs rather than silently editing approvals. An AI verification is not a human accounting approval.

## Required mapping extension
Include source taxonomy/namespace and version, tag, canonical concept, positive and negative conditions, statement role, unit, period type, consolidation/dimensional eligibility, effective filing range, precedence, composition (exact/combined/component/calculated/not_equivalent), supporting fact refs and counterexamples. Quantify coexistence without interpreting coexistence as equivalence.

## Required derivation extension
Include input fact IDs and source refs, values, exact dates, reported basis, units, currency, scope, formula ID/version, arithmetic, output period and output value, lineage hash, restatement compatibility and any conflict. Preserve input precision; do not perform arithmetic on display-rounded values when raw values exist.

## Review bundle and acceptance
Bundle task, decisions, evidence manifest, impact diff, checks, exclusions and rollback/replay plan. The reviewer returns per-decision verdicts and evidence, not one blanket batch approval. State NOT_RUN for checks not executed. Zero affected rows is not a successful correction.

## Queue state machine
new -> evidence_ready -> proposed -> independently_verified -> policy_eligible -> staged -> published -> monitored
Branch to blocked, rejected or superseded from any appropriate stage. Verification does not imply publication authorization. Link children to one root-cause task; resolve child findings only after replay verifies their actual condition is fixed. Use idempotency keys based on root cause + scope + policy/source version.

## Machine-readable example: synthetic proposed decision
```json
{
  "decision_id": "example-decision-001",
  "task_id": "example-task-001",
  "kind": "mapping",
  "status": "proposed",
  "scope": {"issuer_ids": ["SYNTHETIC-A"], "periods": ["2025-12-31"], "exclusions": ["segment contexts"]},
  "evidence": [{"ref": "fixture://A/BS/row12", "locator": "balance sheet row 12", "source_type": "synthetic", "source_hash": null}],
  "rationale": "A combined payable line requires a combined concept rather than a narrower AP concept.",
  "alternatives_considered": ["Map to accounts payable only: rejected because that narrows the source meaning."],
  "unresolved_questions": ["Confirm actual taxonomy version and original filing context before any operational use."],
  "impact": {"affected_issuers": null, "affected_periods": null, "affected_cells": null, "downstream_metrics": null},
  "checks": [],
  "proposed_by": "mapping-worker-run-001",
  "reviewed_by": null,
  "policy_version": "example-draft-v1",
  "code_revision": null,
  "created_at": "2026-10-17T00:00:00Z",
  "next_action": "Independent source review",
  "rollback_ref": null
}
```
This example is not an approved mapping and is not SEC data. Replace synthetic identifiers only with observed values. No passed check is implied by an empty checks array.

## Task result vs decision result
Task outcomes: COMPLETE, PARTIAL, BLOCKED, REJECTED.
Decision statuses: proposed, verified, approved, rejected, blocked.
Queue lifecycle: new, evidence_ready, proposed, independently_verified, policy_eligible, staged, published, monitored; blocked/rejected/superseded are explicit branches.
A task can be COMPLETE after correctly rejecting a bad mapping. A published batch must identify the exact approved decision revisions used; never equate task completion with publication readiness.

## Handoff integrity
Include input content hashes where available, query text/revision and parameters, source watermark, evidence locators, repository revision, policy versions and batch ID. Detect stale proposals when any prerequisite changes. A reviewer cannot verify a materially different proposal under an old verdict. Never put passwords, connection strings, tokens or unnecessary personal data into artifacts or logs.
