---
id: a-latest-filing-wins-rule-cannot-be-validated-ag-fe9ec0
title: A "latest filing wins" rule cannot be validated against SEC Frames (found 2026-10-18)
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
Frames serves the most recent filing's own value, so it agrees with the rule by construction and cannot catch a flipped sign or a restated-later error in that filing; `conflict_latest_filed.py` published ~4,000 wrong values that way (sign-only conflicts, DEF 14A/10-Q winners). Validate such rules by opening original filings and checking the statement's own arithmetic. Details: `doc/data-moat/learnings/2026-10-17-coverage-rebuild-atomicity-q4-conflicts-and-nonadditive-derivation.md` section 6.
