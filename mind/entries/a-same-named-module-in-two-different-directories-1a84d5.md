---
id: a-same-named-module-in-two-different-directories-1a84d5
title: A same-named module in two different directories (`apps/backend/reference_data.py` vs. `apps/backend/routers/reference_data.py`) crashes mypy outright
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
("Duplicate module named...") with zero real findings reported, not just a warning — add `--explicit-package-bases` to the CI invocation (fixed 2026-10-13). A green-looking-but-crashed advisory job can hide 80+ real findings the same way a failed earlier step does (see the bullet above).
