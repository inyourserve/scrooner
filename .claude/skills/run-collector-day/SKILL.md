---
name: run-collector-day
description: Launch a remote/cloud agent to build the next day of the Scrooner Collector (doc 08), then independently verify it before trusting its self-report. Use when asked to run, start, continue, or kick off a Collector build day (Day 3, Day 4, etc.), especially "even if I'm away/asleep."
---

Coordinate one day of the Collector build via a remote agent — the full loop, not just the verification half. Learned the hard way on Day 3: a remote agent's own "completed"/"done" status is not evidence. Independent verification against the live database is what actually tells you whether the day is done.

1. **Identify the day.** Read `doc/08_Scrooner_Collector_Execution_Plan.md`'s 7-day table and check what's actually implemented in `pipeline/src/scrooner_pipeline/` to find the next undone day. Copy that day's exact "Deliverable" and "Done when" text verbatim — don't paraphrase it into the agent prompt, and don't paraphrase it into your own verification later either.

2. **Launch a remote agent** (`Agent` tool, `isolation: "remote"`, `run_in_background: true`) with a fully self-contained prompt, since it has no memory of this conversation. Include:
   - Read order: root `CLAUDE.md` → `pipeline/CLAUDE.md` → doc 06 → doc 07 → doc 08.
   - The one day's scope only — explicitly tell it not to start the next day.
   - The project's actual discipline, not just the task: verify against live SEC/DB data instead of assumed shapes (this project has caught real bugs this way — a primary-key design error, a schema inconsistency, a doc/reality mismatch); the Collector must never normalize/map/calculate, only fetch-store-checksum; fix genuine implementation bugs directly but flag (don't silently resolve) product/architecture ambiguities.
   - Instruct it to invoke the `verify-collector-day` skill itself once its work is actually run against real data (not just unit-tested), and to include that skill's literal output in its final report.
   - Instruct it to stop after this one day — no chaining into the next.

3. **When a completion notification arrives, do not treat it as evidence.** Read its `<result>` critically — vague language ("waiting for...", "will resume when...", "set a background watcher") means the work likely isn't actually finished, regardless of `<status>completed</status>` (that field means the agent's *turn* ended, not that the day's task succeeded).

4. **Verify independently**, the same way `verify-collector-day` does it directly against the live database and, if the agent used an isolated worktree, against the actual files (`diff` the worktree against the main checkout, or just check the main checkout directly if the sync already happened) — don't rely solely on the agent's own account.

5. **If incomplete or ambiguous: resume the same agent** (`SendMessage` to its agent ID, not a fresh `Agent` call — a fresh one loses all context) with the specific gap you found, from direct evidence ("`raw.sec_submissions` has 0 rows, doc 08 requires both companyfacts and submissions"), not a vague "are you done yet?". Repeat steps 3-4 until the evidence actually supports PASS.

6. **Write the day's learnings entry** at `doc/learnings/day-NN-<slug>.md` (see `doc/learnings/README.md` for the exact structure: Problem / How it was found / Fix / Why it matters going forward) — for every real problem hit, not just ones that turned into code changes. A design decision forced by a live-data discovery counts; so does a doc/reality mismatch; so does a process failure like an agent's report not matching reality. This is what keeps the same mistake from being rediscovered on Day N+2. Skipping this step when something genuinely went wrong defeats the point of the skill.

6b. **Update `doc/PROGRESS.md`'s Data Collector row** — status (still 🔄 until Day 7, then ✅), and the one-line note (which day, anything notable). This is the single project-wide status file across all 14 parts (doc 06); don't let it go stale just because doc 08 and the learnings folder already have the detail.

7. **Close out deliberately — and confirm the agent actually stopped.** A `SendMessage` telling it to stop is not itself confirmation; it queues for the agent's next tool round, and an agent stuck in its own wait-loop (e.g. repeatedly calling `Monitor`/waiting on a background job of its own that will never resolve) may not reach that round for a long time, or may keep looping regardless (learned on Day 6: the agent's real work was done and independently verified, but it kept running for another hour, generating repeated "waiting for the next notification" reports with **climbing `tool_uses`/`subagent_tokens` on every repeat** — genuinely still active and burning cost, not just replaying stale messages).
   - A single `status` field is not reliable either — `TaskStop` reported "not running (completed)" once when the agent was, moments later, confirmed `running` via `ListAgents`. Treat `ListAgents` as ground truth when in doubt, not whatever the most recent notification's `status` said.
   - If repeat notifications keep arriving from the same task-id after you've already verified the day is done, check `ListAgents` for that task-id. If it's genuinely still running, call `TaskStop` directly rather than waiting further or sending another polite stop message — don't assume it'll wind down on its own.
   - Report to the user with the real evidence (not the agent's prose), any bugs found and fixed, anything flagged as an ambiguity rather than decided, and any doc/reality mismatches worth fixing (fix docs directly if the fix is mechanical/factual; flag and ask if it's a product/scope decision). Then stop — the next day starts only when the user says so, matching this project's "checkpoint each day" agreement.
