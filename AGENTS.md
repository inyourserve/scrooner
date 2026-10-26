# Scrooner agent entrypoint

Use progressive disclosure. Do not read the repository's planning history by default.

## Start here

1. Read `data-team/NOW.md` (current state, priorities, blockers).
2. Run `python3 scripts/agent_context.py` for a compact live Git/task summary.
3. Read only the source files named for the task below.

## Route by task

- Data execution/status: `data-team/strategy/TASK-BOARD-TOP1000.md` (if absent locally, use the compact script, which reads it from `origin/main`)
- Product direction or priorities: `data-team/strategy/THE-PLAN.md`
- Data-moat principles, quality gates or definitions of done: `data-team/DATA-MOAT-OPERATING-STANDARD.md`
- Pipeline implementation: `pipeline/CLAUDE.md` plus the touched module
- Accounting or XBRL meaning: the relevant card in `data-team/tags/cards/`; then search `data-team/22-FILING-LESSONS-LEDGER.md`
- Database schema/migration: the relevant file in `pipeline/db/migrations/`
- Release/commit: `data-team/08-RELEASE-MANAGER.md`
- Frontend: `apps/app/` and the relevant file under `doc/design/`

Search before opening long files. Prefer `rg -n "term" file` and read a narrow range. Use `mind/mind.py search` only when prior case knowledge is useful.

## Context budget

- Default initial reading: at most 3 files and roughly 300 lines total.
- Do not load `doc/data-moat/team/PLAN.md`, the full filing ledger, all tag cards, or all strategy reviews unless the task explicitly requires a historical audit.
- Treat `data-team/strategy/THE-PLAN.md` as direction and `TASK-BOARD-TOP1000.md` as execution state. Older strategy files are evidence/history, not startup context.
- Cite the exact source when a decision depends on a historical fact; do not copy the fact into another permanent document.

## Durable updates

- Update existing canonical state instead of creating another status document.
- Current state goes in `TASK-BOARD-TOP1000.md`; durable direction goes in `THE-PLAN.md`; verified filing lessons go in the ledger; tag findings go in `data-team/tags/feedback-inbox.md`.
- Keep summaries short. Link to evidence instead of duplicating it.

## Safety

The working tree may be shared and dirty. Preserve unrelated changes. Never force-push or apply production migrations without explicit authorization. Value-changing data work requires a dry run, evidence, review, rollback, and a flag.
