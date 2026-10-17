# Release policy worksheet — DRAFT, not adopted

Purpose: allow routine, reproducible improvements without asking the founder about every cell. This document grants no deployment or production-write authority by itself.

## Populate from real repository facts
Record owner, adoption date, policy version, supported issuer/security universe, forms, accounting frameworks, templates, history, reporting view, freshness SLA, approved concept/formula revisions, permitted operations, reviewer requirements and rollback owner. Keep unknown fields explicit. Do not fabricate adoption or a sign-off.

## Eligibility classes
| Class | Candidate | Required disposition |
| --- | --- | --- |
| Existing approved exact mapping | New eligible fact with unchanged semantic/context conditions | Deterministic application within the adopted policy, regression checks and lineage |
| Existing approved additive derivation | Compatible approved inputs with no material conflicts | Decimal computation, basis/date/unit/context checks, independent verification where policy requires, staged impact diff |
| New exact mapping or concept definition | Evidence supports a new semantic rule | Proposed change, counterexamples, independent review and explicit policy decision before promotion |
| Combined/component substitution or new sector formula | Interpretation changes economic meaning | Separate proposal with scoped methodology; no silent substitution |
| Missing evidence or unresolved conflict | Source basis, context or attribution cannot be established | Quarantine the standardized output; preserve valid source information |
| Wrong published value | Evidence shows an incorrect number affecting users | Prioritize correction or withdrawal under the incident procedure; do not leave it in place while expanding coverage |

## Minimum release packet
Include exact batch and revisions, observed source evidence, before/after values, all impacted formulas and screens, exclusion changes, checks actually executed, reviewer results, unresolved material issues, authorized promotion method, monitored signals and rollback procedure. Show unchanged-denominator coverage alongside any denominator reclassification. A zero-row update is not a successful fix.

## Release gates
1. Defined scope and current inputs; no silent mutation of raw evidence.
2. Appropriate accounting/template applicability and complete input lineage for every changed published value.
3. Exact semantic and source-basis eligibility checks passed.
4. Relevant fixed regression and adversarial tests passed; rotating sample method and limits stated.
5. No unresolved known critical wrong-value defect in the affected release scope.
6. Measured impact on screener inclusion/exclusion, calculations and history where applicable.
7. Authorized reproducible promotion and tested rollback/replay plan.
8. Freshness and post-release monitoring configured in the actual system or explicitly marked NOT_IMPLEMENTED.

A packet failing a gate remains staged or blocked. Publish independently eligible unaffected subsets only when their scope and dependencies are explicit. Do not claim 100% correctness from passing samples. Do not invent a percentage target; define it after measuring the actual baseline and specifying the sampling method.

## Incident and rollback
Identify severity through concrete user effects: wrong entity, sign/scale, period, attribution, metric or screener membership. Capture the faulty rule/code/data revision and all dependents. Stop further promotion of the faulty family. Withdraw/revert affected materialized outputs under existing authorization, preserve evidence, correct the root cause, replay the full measured scope and verify before resuming. External notifications require separate existing authorization.
