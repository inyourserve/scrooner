---
id: this-dev-mac-s-local-disk-filling-up-can-silentl-c19d08
title: This dev Mac's local disk filling up can silently hang a process with zero active query and zero error output
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
— `df -h /private/tmp` is a cheap first check. `/tmp` (and anything running there) can also be wiped mid-session by an environment restart with no warning; always re-derive local state from a live DB query rather than trusting a file/process from more than a few minutes ago.
