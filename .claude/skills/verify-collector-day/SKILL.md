---
name: verify-collector-day
description: Run and verify a day of the Scrooner Collector build (doc 08) against the live SEC API and the live Supabase project, with real evidence. Use after finishing a day's implementation work in pipeline/, or when asked to verify/check/test whether a Collector day's acceptance criteria actually pass.
---

Verify a day of the Collector build plan (`pipeline/`, per `doc/08_Scrooner_Collector_Execution_Plan.md`) against its own stated acceptance test — with real evidence, not an assertion that it "looks right."

1. Read `doc/08_Scrooner_Collector_Execution_Plan.md`'s 7-day table. Identify which day is being verified (ask if ambiguous — check what's actually implemented in `pipeline/src/scrooner_pipeline/` if unclear) and copy its exact "Done when" text as the bar to check against — not a paraphrase of it.
2. Run whatever that day's deliverable actually is — the relevant command from `pipeline/pyproject.toml`'s `[project.scripts]` (e.g. `uv run scrooner-bootstrap`), or the specific module being tested. Always run from `pipeline/` with `uv run` so the pinned Python 3.12 env and locked dependencies are used, never the system Python.
3. Query the live database directly to confirm state — `psql "$DATABASE_URL" -c "..."` after loading `pipeline/.env` (`set -a; source pipeline/.env; set +a`) — row counts, idempotency (rerun the job, diff the count), constraint behavior, whatever the day's "Done when" text specifically requires. Don't infer from log output alone when a direct query can confirm it.
4. Report **PASS** or **FAIL** per individual condition in the "Done when" text, each backed by the evidence that proves it (the actual count, the actual query output) — not a single rounded-up summary claim. If a condition wasn't actually checked, say so; don't count it as passed.
5. If something looks schema- or scope-relevant while verifying (a missing constraint, an ambiguous field, anything like the `(cik, ticker)` or `sec_filing_documents` fixes from Day 2) — flag it, but don't silently edit doc 08, doc 02, or `CLAUDE.md` as part of a verification pass. Recording a decision is a separate, deliberate step in this project, not a side effect of testing.
6. Never mark a day done on partial evidence. If the acceptance test has three conditions and only two were actually checked, say exactly that — don't round up.
