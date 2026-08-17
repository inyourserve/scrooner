# Data pipeline build — day-by-day learnings

Not a decision doc (no status line, not part of the canonical 01-10 set) — this is a running engineering journal: what actually went wrong, how it was actually found, and what changed as a result. The canonical docs say what's decided; this says how we found out we were wrong about something, so the next session (human or agent) doesn't have to rediscover it from scratch.

Covers both the Collector (`day-NN-*.md`, doc 08, frozen/complete) and the Normalizer (`normalizer-day-NN-*.md`, doc 09, in progress) — separate filename prefixes since both phases number their own days starting at 1.

**One file per day**, written as part of closing out that day (the `run-collector-day` skill writes Collector entries automatically; Normalizer entries are written manually for now, same discipline). Structure per entry:

- **Problem** — what broke, or what was wrong, stated plainly.
- **How it was found** — the specific check that surfaced it. If the answer is "I just thought about it," that's worth noting too — most of these were found by verifying against live data/state, not by reasoning from memory.
- **Fix / decision** — what actually changed, and where (file, doc, schema).
- **Why it matters going forward** — the generalizable lesson, not just the one-off fix. This is the part that's actually meant to prevent a repeat.

Read the relevant day's entry (or skim recent ones) before starting related work — that's the whole point of this folder existing.
