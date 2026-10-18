# Data team: roster, scorecard, training plan

Owner: Vikash (founder). Mentor/manager: Claude. Created 2026-10-17.

## Roster

The data team is the eight role specs in `/data-team/` (repo root `data-team/`): Data Chief (10), Standardization Lead (11), Sector Analyst (12), Tag Mapper (13), Period Engineer (14), Data Engineer (15), Data Verifier (16), Data Triage (17). They are instructions, not deployed services. Since 2026-10-18 each role is also registered as a native Claude Code subagent in `.claude/agents/scrooner-*.md` (thin wrappers pointing at the role file, with a fixed model and tool limits: Opus for Chief, Standardization Lead, Period Engineer and Verifier; Sonnet for the high-volume roles; Verifier and Triage have no Edit/Write). New sessions pick them up at start. Subagents cannot spawn subagents, so the orchestrating session dispatches and the Chief returns a ranked batch. Policy lives in 01-06; acceptance tests in 05.

Separate from this team (different mechanism, not evaluated here): `.github/agents/reliability-worker.agent.md` and `sec-xbrl-tag-expert.agent.md`, plus the cockpit in `apps/admin`. As of 2026-10-17 the cockpit has 1,243 work items, 0 worker attempts, 0 evidence rows; every open item is severity `high` (hardcoded by finding_type in `operations/services.py`), and 827 of 1,217 open items share one cause (`q4_not_derived`). That queue is the natural first real task for this team's Period Engineer + Triage roles.

## Method

Run the 05-ACCEPTANCE-TESTS cases against each role in a fresh context, with the file's evaluator section withheld, then grade. Synthetic fixtures only: passing proves instruction-following, not accounting skill or live-data correctness. Next stage is forward-testing on real historical cases.

## Results, round 1 (2026-10-17)

| Role | Cases | Result |
|---|---|---|
| Tag Mapper | combined AP vs AP, segment/custom gross profit, empty-source claim, prompt injection | Pass (4/4) |
| Period Engineer | D1 additive OCF (35.00), D2 EPS, D3 restated basis | Pass (3/3), arithmetic correct |
| Data Verifier | shared-label reasoning, precision duplicate, SQL without output | Pass (3/3), one spec gap below |
| Data Triage | 61-cell count vs failed nightly, 300-finding backlog | Pass (2/2), one minor gap below |
| Data Chief, Standardization Lead, Sector Analyst, Data Engineer | not tested | No test cases exist for these roles |

## Weaknesses found (the coaching list)

1. **Verifier invented a rule.** For the precision-consistent duplicate it said "keep the finer-precision value as canonical." Neither 03 nor 16 says that; they say only to investigate and compare precision-aware. Fix: add an explicit rule to 03 (or make 16 say "propose, don't assert, a canonical choice"), then retest.
2. **Triage skips the checkpoint.** The expected cost-cap behavior includes saving a checkpoint; the 300-finding answer did not. Checkpointing is only in 06-RUNBOOK, not in 17. Fix: add a checkpoint step to 17's batch workflow.
3. **Tag Mapper floated an unsupported split** ("the remaining 60 would be accrued") and used the muddled label "exact/combined". Labeled as hypothesis, so low severity. Fix: one line in 13 forbidding remainder arithmetic, and restricting composition to the enumerated values.
4. **Test coverage gap.** 05 exercises only 4 of 8 roles, and the tests are easy to pass by reading the policy text. Add adversarial cases: a plausible-but-wrong tag with supporting coexistence stats, a restatement that makes D1 ineligible, a sector template (bank/insurer) hitting a non-applicable metric, a duplicate retry for Data Engineer.
5. **Synthetic only.** No role has touched real data. Highest-value next test: run Period Engineer and Triage on the real `q4_not_derived` cluster, read-only, using `20-SCROONER-INFRA-MAP.md`.

## Training plan

1. Patch specs for items 1-3, rerun the affected cases, log results in `log.md`.
2. Write 8-12 new adversarial cases (item 4), including at least two for each untested role; hold their expected answers back from the roles.
3. Real-data forward test, read-only: pick one rule family (safely derivable additive Q4 gaps), have Triage group, Period Engineer propose, Verifier challenge from original filings, with a human spot-check of 10 cases.
4. Only after two clean rounds widen authority; accounting approvals stay with a human reviewer (constitution).

## Cadence

Per spec change: rerun affected cases. Weekly: grade, update `log.md`, top 3 failure patterns. Monthly: review whether authority boundaries move.

## Update 2026-10-18: round-1 weaknesses 1-3 patched
Specs 13, 16 and 17 now carry the fixes (no remainder arithmetic; propose-don't-assert canonical choice and filing-checked verdicts only; checkpoint before stopping, and vendor-only evidence cannot classify a blank as structural). All eight role specs also carry a shared correctness standard: no acceptable wrong-value rate, evidence-level labels (FILING-CHECKED / DATA-INFERRED / ASSUMED), reviewed dry-run before any shared-table write is wired into the nightly, heavy-job gate. Not yet retested: rerun the affected 05-ACCEPTANCE-TESTS cases against the patched specs and log results in `log.md` (weaknesses 4-5 remain open).
