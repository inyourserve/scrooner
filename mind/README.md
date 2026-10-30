# mind — shared memory for every agent, worker and LLM session

> **Status: BETA and on demand. Everything here is optional, never a blocker.** No agent or session is required to search or add. Results are hints: verify against the source before relying on them, and the canonical doc always wins. Mind does not run automatically at session start or stop.

Goal: nobody pays tokens to re-learn something the team already knows. Search returns ~1 line per hit; a full entry is fetched only when needed (an entry is ~100-300 tokens, a doc it replaces is thousands).

## The loop (this is the self-improvement)

```
 search ──hit──> get <id> ──used──> feedback <id> helped | wrong
    │ miss (logged as a gap)
    ▼
 do the work ──> add (inbox) ──> promote (curator, dedupes) ──> entries/
                                                                  │
 lint: broken paths, duplicates, disputed, cold, un-reverified <──┘
 stats: hit rate, top gaps (what to write next), top fetched
```

- **Capture is cheap and conflict-free:** `add` writes one file in `inbox/`. Concurrent sessions never edit the same file.
- **Promotion is gated:** `promote` refuses ids that exist and >=60% token-overlap duplicates (use `amend`). It is the only way into `entries/`, so quality is enforced in one place.
- **Wrong knowledge gets removed:** `feedback <id> wrong` flips the entry to `disputed` (still returned, flagged) until a curator verifies or supersedes it.
- **Dead knowledge gets removed:** `lint` fails on entries whose `paths:` no longer exist, and lists cold (never fetched) and un-reverified ones.
- **The team learns what it lacks:** every zero-result search is logged; `brief` shows the top gaps at session start and `stats` ranks them.

## Commands (`python3 mind/mind.py ...`)

| Command | Use |
|---|---|
| `search "<q>" [-k 5]` | ranked one-liners (title and tags weigh 3x body) |
| `get <id>` | the full entry |
| `add --title --kind --evidence [--tags --paths --source] --body -` | capture a learning (body from stdin with `-`) |
| `amend <id> --note` | append to and re-verify an existing entry |
| `promote --all` | curator: inbox to entries, with dedupe |
| `feedback <id> helped|wrong|stale` | usage signal; wrong marks it disputed |
| `lint` | health check, exit 1 on errors (safe for CI) |
| `stats` | hit rate, top gaps, top fetched, feedback |
| `brief` | optional compact summary; run only when memory health or known gaps matter |
| `ingest-ledger` | seed from `data-team/22-FILING-LESSONS-LEDGER.md` (idempotent) |

Kinds: `rule lesson howto decision gotcha reference`. Evidence: `FILING-CHECKED DATA-INFERRED CODE-CHECKED ASSUMED` (same labels as the data team's constitution). Add `pinned: true` to an entry's frontmatter to show its title in every session brief (keep to ~10).

## Rules

1. An entry is **one fact** with evidence. If it needs a section heading it is a doc, not an entry; link the doc in `paths:`.
2. Entries point at the source (`paths:`, `source:`); they do not replace canonical docs. Where an entry and a canonical doc disagree, the doc wins and the entry gets amended.
3. Never store secrets, credentials or connection strings.
4. `log/` is local usage telemetry and is gitignored; `entries/` and `inbox/` are committed.

## What it does not do yet (deliberately)

No embeddings or vector DB (keyword ranking is enough at hundreds of entries; revisit when `stats` shows a poor hit rate despite entries existing). No auto-promotion by an LLM (a curator agent runs `promote --all` and reviews). No automatic migration of CLAUDE.md content; see the platform engineer brief for that.
