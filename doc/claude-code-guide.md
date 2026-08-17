# Extending Claude Code — Skills, Subagents, Slash Commands

A practical reference for adding custom skills, subagents, and slash commands to a repo or a subtree within one (e.g. this repo's root, or `pipeline/`). Not a Scrooner product doc — this is meta documentation about the tooling itself, so it doesn't carry a canonical status line.

---

## The short version

| Mechanism | Use it for | Lives at |
|---|---|---|
| **Skill** | Reference knowledge or a repeatable procedure Claude should pull in automatically when relevant (or run manually) | `.claude/skills/<name>/SKILL.md` |
| **Subagent** | A specialized worker that runs in its own isolated context — for research, review, or long autonomous tasks that shouldn't clutter the main conversation | `.claude/agents/<name>.md` |
| **Slash command** | A quick manual shortcut that only runs when explicitly typed — the simplest of the three | `.claude/commands/<name>.md` (functionally now a special case of a skill) |

All three can live at **project scope** (`.claude/...`, checked into git, shared with the team) or **personal scope** (`~/.claude/...`, just for you across all projects).

---

## 1. Skills

### What they're for

A skill is a packaged set of instructions Claude loads when it's relevant — a procedure, a style guide, domain knowledge, or a template you'd otherwise paste into chat repeatedly. Claude can trigger a skill on its own based on the task, or you can invoke it manually with `/skill-name`.

### File location

```
.claude/skills/<skill-name>/
├── SKILL.md          # required
├── reference.md       # optional — loaded only if SKILL.md links to it
└── scripts/
    └── helper.sh       # optional supporting files
```

Project-scoped: `.claude/skills/`. Personal, across all projects: `~/.claude/skills/`.

The directory name becomes the command name — `.claude/skills/stock-research/` → `/stock-research`.

### Minimal example

```markdown
---
name: stock-research
description: Research a stock with technical and fundamental analysis. Use when analyzing a ticker or preparing a research summary.
arguments: [ticker]
---

Research the stock $ticker:

1. **Fundamentals** — revenue growth, margins, FCF, ROIC, dilution (pull from Scrooner's own metrics, not outside sources)
2. **Filing check** — anything notable in the most recent 10-K/10-Q
3. **Summary** — 3-5 sentence plain-English readout, no buy/sell recommendation (Scrooner is a research tool, not an adviser — see doc 03)
```

### Key frontmatter fields

| Field | Purpose |
|---|---|
| `description` | The most important field — this is what Claude matches against user intent to decide whether to auto-invoke. Be specific. |
| `disable-model-invocation: true` | Makes it manual-only (`/name` required, no auto-trigger) |
| `user-invocable: false` | Hides it from the `/` menu — Claude-only |
| `allowed-tools` | Pre-approve specific tools for this skill's turn |
| `model` / `effort` | Override model or reasoning effort just for this skill |
| `arguments` | Named positional args, referenced in the body as `$argname` |
| `context: fork` + `agent:` | Run the skill in an isolated subagent instead of inline |

### Gotchas

- Keep `SKILL.md` itself short (rule of thumb: under ~500 lines) — put large reference material in a separate file and link to it, so it only loads into context when actually needed.
- `description` gets truncated around 1,500 characters combined with `when_to_use` — front-load the part that matters for triggering.
- Personal skills override project skills of the same name.

---

## 2. Subagents

### What they're for

A subagent is a separate "worker" with its own context window, its own tool access, and optionally its own model. Use one when a task would otherwise flood the main conversation with intermediate noise — deep research, a thorough code review, a long autonomous data-pipeline task — and you just want the finished result back.

### File location

```
.claude/agents/<name>.md          # project-scoped
~/.claude/agents/<name>.md        # personal, all projects
```

Subdirectories are allowed for organization (e.g. `.claude/agents/data/collector-tests.md`) but the agent's actual identity comes from the `name` field in its frontmatter, not the file path.

### Minimal example

```markdown
---
name: filing-reconciler
description: Manually reconciles a company's parsed metrics against its actual SEC filing. Use when spot-checking data quality on a golden-company set.
tools: Read, Grep, Glob, Bash, WebFetch
model: sonnet
---

You are a data-quality reconciler for Scrooner. Given a ticker, pull the
parsed metrics from the pipeline output and compare them line-by-line
against the actual SEC filing. Flag any mismatch with the exact source
line and filing reference. Never guess at a number — if something can't
be verified, say so explicitly rather than assuming it's correct.
```

### Key frontmatter fields

| Field | Purpose |
|---|---|
| `name` | Required, unique identifier |
| `description` | Required — this is what triggers automatic delegation, so write it the way you'd explain to a teammate when to use this agent |
| `tools` | Restrict which tools it can use (defaults to inheriting everything if omitted) |
| `model` | Pin a specific model, or `inherit` |
| `background` | Run detached, returning only a final summary — useful for long jobs |
| `skills` | Preload specific skills' full content at startup |
| `memory` | `project` (shared via git), `user`, or `local` — lets the agent retain notes across runs |

### Invocation

- **Automatic** — Claude decides based on the task and the agent's `description`.
- **Explicit** — ask for it by name ("use the filing-reconciler agent on AAPL").
- **Session-wide default** — `claude --agent filing-reconciler`, or set it in `.claude/settings.json`.

### Gotchas

- Automatic delegation lives or dies on the `description` — vague descriptions mean Claude either never picks the agent or picks it too eagerly.
- A subagent can't itself spawn another subagent, ask the user a clarifying question, or enter plan mode — those tools are stripped out for isolation.

---

## 3. Slash commands

### What they're for

The simplest of the three: a fixed prompt you trigger by typing `/name`. No auto-invocation, no supporting files — just a shortcut for something you type often.

### File location

```
.claude/commands/<name>.md        # project-scoped
~/.claude/commands/<name>.md      # personal
```

The filename (without `.md`) becomes the command — `deploy.md` → `/deploy`.

Under the hood, a slash command and a skill with `disable-model-invocation: true` are now functionally the same thing — commands were folded into the skills system. If you think you might ever want auto-invocation or supporting files later, just build it as a skill from the start.

### Minimal example

```markdown
---
description: Run the Collector's golden-company reconciliation suite
---

Run the golden-company reconciliation tests:
1. `pytest tests/golden_companies/ -v`
2. Summarize any failures by company and metric
3. Do not attempt to fix failures automatically — just report them
```

Invoke with `/reconcile-golden`.

### Arguments

```
/reconcile-golden AAPL
```
is available in the body as `$ARGUMENTS`, or as named args if you declare `arguments: [ticker]` in frontmatter and reference `$ticker`.

---

## Choosing between them

| If you want... | Use |
|---|---|
| Claude to automatically know a procedure or convention and apply it when relevant | **Skill** |
| A reusable prompt template you fill in with arguments, but always want to trigger yourself | **Skill with `disable-model-invocation: true`** (or a plain **slash command**) |
| An isolated worker that does a big job and reports back without cluttering the main thread | **Subagent** |
| Several of those isolated workers running in parallel on different pieces of a task | **Subagent**, dispatched via the Agent/Task tool, possibly several at once |
| The absolute simplest "type this, get that prompt" shortcut, nothing fancy | **Slash command** |

---

## Suggested starting set for Scrooner

Given the project breakdown in doc 06, a reasonable first batch:

- **Skill** — `scrooner-conventions`: a distilled version of the KISS BORING principles and the "Collector must stay lossless" boundary rules from doc 04/05, so Claude applies them automatically without being reminded every session.
- **Skill** — `golden-company-check`: the reconciliation procedure from doc 05's data-quality methodology, runnable manually or auto-triggered when someone asks to verify a company's numbers.
- **Subagent** — `filing-reconciler` (example above): isolated, thorough, doesn't need to live in the main conversation.
- **Subagent** — `collector-tester`: runs the Collector's idempotency/resume/dedupe test suite end-to-end and reports pass/fail, without flooding the main thread with test logs.
- **Slash command** — `/reconcile-golden`: quick manual trigger for the golden-company suite during active development.

All of these should live in `.claude/` at the repo root and get checked into git so the whole team shares them — pipeline-specific ones still live at the repo-root `.claude/`, same as frontend-specific ones, since `pipeline/` is a folder in this repo, not a separate one.

---

## Sources

- [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
- [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
- [code.claude.com/docs/en/slash-commands](https://code.claude.com/docs/en/slash-commands)
