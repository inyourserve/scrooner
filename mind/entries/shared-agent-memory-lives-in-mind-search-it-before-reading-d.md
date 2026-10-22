---
id: shared-agent-memory-lives-in-mind-search-it-before-reading-d
title: Shared agent memory lives in mind/, search it before reading docs
kind: howto
tags: mind, tokens, agents, memory
paths: mind/mind.py, mind/README.md
evidence: CODE-CHECKED
status: active
created: 2026-10-21
verified: 2026-10-21
---
Run python3 mind/mind.py search "<topic>" then get <id> before reading long docs; add durable learnings with mind.py add (inbox, then promote --all); feedback <id> wrong on bad entries. Hooks/agent wiring needs the user's approval (the harness blocks agents editing .claude/settings.json and .claude/agents).
