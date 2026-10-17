# Bootstrap and operating plan

## Bootstrap prompt
Use 10-DATA-CHIEF.md on my Scrooner repository. Start read-only. Read AGENTS.md, doc/data-moat/SYSTEMS.md, Doc 56 or its current equivalent, schema, existing agents, run logs, canonical concepts, metric definitions and current coverage queries. Locate those documents; do not assume they exist at those paths. Build a versioned baseline and an evidence-ready batch for one high-impact root cause. Use existing tools. Give me a concrete proposed publication policy, not a request to approve each cell. Limit the first run to 10 rule families and 50 representative issuer-periods. Do not publish new accounting interpretations. If access is missing, identify exactly what is required and complete the design work that does not depend on it.

## Existing analyst or founder inspection checklist
Inspect original source row, period and units. Ask whether the proposal changes the meaning, mixes a total and component, substitutes combined data, or ignores a conflicting period. Approve only what you can substantiate. A model's confident prose is not substantiation. If unresolved, defer that standardized metric and preserve valid as-reported information. Founder review is a product/release responsibility, not a substitute for accounting expertise.

## First useful cycle
1. Reproduce current statistics with scope and source watermarks; diagnose any failing nightly stage.
2. Run full candidate census for safe additive quarterly derivations. Separate eligibility from input presence.
3. Replay one approved rule or fix in staging. Verify no regression and inspect actual screener membership changes.
4. Publish only under applicable policy and authorization. Record revision, before/after and rollback.
5. Select next root cause based on corrected user-visible outputs and remaining uncertainty.

## Proposed release-policy worksheet
The founder must explicitly adopt the final policy; this document is a draft. Name the supported universe and history, approved concept/formula versions, source freshness SLA, eligible direct/derived transformations, allowed agent actions, required checks, reviewer identity rules and rollback owner. Define what counts as a critical discrepancy using concrete user effects (wrong company inclusion, incorrect sign/scale, stale current filing, mixed restatement basis). Require critical sampled discrepancies resolved and material conflicts quarantined before release. Passing checks is not proof of full-population accuracy. Do not invent a 99% target from a small sample.

Allow deterministic replay of already approved exact mappings and allowlisted additive derivations with complete lineage, basis checks and no conflicts. Hold new concept equivalence, sector formulas, non-additive derivations and unexplained source conflicts for an explicit evidence decision. Never allow UNKNOWN-to-numeric-zero. If no qualified person can resolve a case, leave it unsupported.

## Runtime and cost
Start with manual invocation. Use one active worker and one separate reviewer context; roles do not need concurrent processes. Spend model calls on rule families, not cells. Use Python/SQL for routine checks. Inspect changed facts only; skip source/policy hashes already processed. Set model-call and case caps before a cycle. Do not claim a dollar cost without measured tokens and the selected provider's verified current pricing. No paid orchestration product is required by these skills, but execution still consumes whatever model/API subscription is used.

## Minimal durable records
Reuse existing ticket and decision tables. If absent, begin with task.json, append-only decisions.jsonl, source-linked evidence manifests and checks stored alongside code revisions. A real scheduler, API integration, secrets handling and database adapter are engineering work to implement in the authorized repository; skill instructions do not provide those integrations.

## Sequence by milestone rather than promised days
A: known scope and fresh baseline.
B: successful replay and one independently checked root-cause correction.
C: repeatable bounded batches and adopted release policy.
D: representative sector pilots with explicit unsupported metrics.
E: expansion backed by observed throughput, correctness and marginal product value.

## Resume after a new session or compaction
Read the selected role, latest task record, decision log, staged diff and checkpoint. Reconfirm input/policy/code revisions before continuing. Resume completed evidence rather than rerunning broad scans. Mark a prior verdict stale when its evidence or proposal changed. Do not restart the entire project merely because a new agent context was opened.

## Daily invocation
Read 10-DATA-CHIEF.md and use the current repository state. Reconcile the previous batch, source freshness and critical incidents. Choose at most one next root-cause family. Run only needed roles. Return verified product impact, cost/call telemetry where available, unresolved cases and exact next action. Do not launch permanent loops or schedules.

## Focused role invocation
Read the selected role file and perform TASK against the supplied source/evidence. Scope to UNIVERSE and PERIOD. Start read-only; implement reversible local/staging changes if authorized. Reuse adopted policy VERSION. Return the contracted decision packet and actual checks. Do not promote new semantic interpretations without the applicable release decision.

## Missing access
If the repository or database is unavailable, stop only dependent execution. Inspect supplied source artifacts, prepare schema-neutral query requirements, identify the exact read access or export needed, and complete the evidence/policy design. Do not scan unrelated systems, guess credentials or claim that a query ran.
