# Scrooner financial-data team — portable Claude Code instructions

Version: 1.0. Prepared October 17, 2026. Purpose: run evidence-backed financial-data work without hiring a full data team. These files are role instructions and operating contracts, not a deployed integration or professional accounting certification.

## Keep one folder
Keep all files together as `scrooner-data-team/` inside your Scrooner repository or any directory Claude Code can read. All eight numbered role files are self-contained: they embed common policy and the handoff contract so you can attach one role file on its own. Supporting files centralize implementation details and evaluation cases.

## First prompt to Claude Code
```text
Read scrooner-data-team/10-DATA-CHIEF.md and
scrooner-data-team/06-BOOTSTRAP-AND-RUNBOOK.md.

Apply those instructions to this Scrooner repository. Locate existing
CLAUDE.md, AGENTS.md, data-moat SYSTEMS.md, Doc 56 or its equivalent,
canonical concepts, metric formulas, coverage queries, run logs and
review/cockpit tooling. Respect existing repository instructions.

Start read-only. Reproduce a fresh baseline and select one high-impact
root cause, preferably safely derivable additive Q4 gaps. Use existing
tools. Do not build a new agent platform.

Read the relevant role file before each role phase. Run only the roles
needed. Use a separate reviewer context when available. Bound the batch
to 10 rule families and 50 representative issuer-period cases, with one
review and one revision pass. Use code for population counts and math.

Complete authorized local/staging work. Return evidence, actual checks,
before/after impact, blocked cases and a concrete release-policy proposal.
Do not publish new accounting interpretations or invent missing access.
```

## Files and roles
| File | Use |
| --- | --- |
| 01-TEAM-CONSTITUTION.md | Shared invariants and authority boundaries |
| 02-TASK-AND-DECISION-CONTRACTS.md | Machine-readable handoffs, audit evidence and lifecycle |
| 03-SEC-XBRL-ACCOUNTING-RULES.md | Source limits, identity, semantics, periods and formulas |
| 04-RELEASE-POLICY.md | Draft worksheet; must be adopted before it grants routine publication eligibility |
| 05-ACCEPTANCE-TESTS.md | Synthetic/adversarial instruction tests |
| 06-BOOTSTRAP-AND-RUNBOOK.md | Start, resume, bounded execution and missing-access handling |
| 07-IMPLEMENTATION-AND-REVIEW-QUEUE.md | Integration, adapters, cockpit and replay acceptance |
| 20-SCROONER-INFRA-MAP.md | **Read first.** Real Scrooner repo, database, CLIs, workflows, rules and per-role starting points (added 2026-10-17) |
| 10-DATA-CHIEF.md | Founder/product coordination and batch ownership |
| 11-STANDARDIZATION-LEAD.md | Accounting concepts, equivalence and rules |
| 12-SECTOR-ANALYST.md | Templates and metric applicability |
| 13-TAG-MAPPER.md | Tag investigation and mapping proposals |
| 14-PERIOD-ENGINEER.md | Historical gaps and safe quarter derivation |
| 15-DATA-ENGINEER.md | Reliable ingestion, storage and replay |
| 16-DATA-VERIFIER.md | Source-based independent challenge |
| 17-DATA-TRIAGE.md | Root-cause grouping and impact prioritization |
| 21-US-FILINGS-DOMAIN-KNOWLEDGE.md / 22-FILING-LESSONS-LEDGER.md | Shared US filing mechanics (v1, items marked [VERIFY] need a live check) and an append-only ledger of repo-proven cases (added 2026-10-18) |
| 18-REPORTED-NUMBERS-CHECKER.md | **DRAFT v0.1 (2026-10-17)** Compare stored headline values to the issuer's own published documents (any format); comparison signal only |

## Native Claude Code skills: optional
Flat role files can be read or attached directly. A folder of arbitrarily named Markdown files does not automatically register eight Claude Code skills.

For native project skills, copy each role file into its own directory as `.claude/skills/<frontmatter-name>/SKILL.md`. The YAML name and description are already included. Preserve each role file's embedded common policy and contracts. Any coordinator links to supporting/role files must resolve to the original `scrooner-data-team/` folder from the repository root; adjust links explicitly during installation. Do not install or overwrite existing skills or CLAUDE.md implicitly.

After installation, use `/scrooner-data-chief`, `/scrooner-tag-mapper`, etc. Confirm discovery in your installed Claude Code version. Before converting roles to `.claude/agents/` files, follow the current subagent format; skill frontmatter is not a substitute for an agent configuration. This pack deliberately imposes no model, unrestricted tool allowlist or permission bypass.

Official format references, checked October 17, 2026:
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents

## Efficient use
Do not attach/read the entire pack on every task. Begin with the coordinator and runbook; load the relevant role and necessary references. One worker context and one reviewer context are enough to start. Sharing a model is not independent accounting authority. Cache unchanged evidence, operate on rule families instead of cells and record actual model cost only when measurable.

## First delivery milestones
A: current scope and reproducible baseline.
B: one corrected root cause with source evidence and staging impact.
C: bounded repeatable runs and an adopted publication policy.
D: sector pilots with clear unsupported cases.
E: expansion based on measured correctness, maintenance effort and product value.

## What is not installed
No database adapter, scheduler, production permission, API key, credential, live collector or automatic publication is included. Ask Claude to inspect and integrate with existing implementation using 07-IMPLEMENTATION-AND-REVIEW-QUEUE.md. Counts from earlier audits are supplied historical claims until remeasured. These instructions do not replace original filings as evidence.
