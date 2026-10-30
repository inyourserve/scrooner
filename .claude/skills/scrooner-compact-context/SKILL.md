---
name: scrooner-compact-context
description: Work on Scrooner with a small context budget by loading current state first and routing to only the relevant evidence. Use for Scrooner status, planning, data-quality, pipeline, or release tasks. Do not use for unrelated repositories.
---

# Scrooner compact context

Start with `AGENTS.md` and `data-team/NOW.md`. Run:

```bash
python3 scripts/agent_context.py
```

Choose one task row from `data-team/strategy/TASK-BOARD-TOP1000.md`. Load only the implementation file and evidence linked by that row.

## Context rules

- Initial context: no more than three files or roughly 300 lines.
- Search long files before reading ranges.
- Do not read the full strategy directory, full ledger, all tag cards, or `doc/data-moat/team/PLAN.md` by default.
- `THE-PLAN.md` owns direction. `TASK-BOARD-TOP1000.md` owns execution state. Older documents are history/evidence.
- Update a canonical file rather than creating another status or plan document.
- Link evidence instead of copying it.

Expand context only when a concrete ambiguity cannot be resolved from the selected task row, touched code, tests, and directly linked evidence.
