---
id: nightly-refresh-and-sanity-have-not-been-green-for-weeks-red
title: Nightly refresh and sanity have not been green for weeks; red is the baseline
kind: lesson
tags: workflows, ci, observability
evidence: DATA-INFERRED
source: doc/learnings/2026-10-24-github-workflows-deep-dive.md
created: 2026-10-24
verified: 2026-10-24
---
gh run list on 2026-10-24: pipeline-refresh last success 2026-08-20 (0 of last 30), pipeline-sanity no success in 45 listed runs since 2026-09-09, workflow-health-check red weekly since 2026-09-14. Causes seen in logs: gates coupled to job health (unresolved_dead_letters:normalizer:3 fails the whole operational job while all freshness is fresh; sanity ends with report --fail-on-findings so 1,810 normal yfinance majors turn it red), plus real statement timeouts and dropped connections. A constantly red monitor hides new regressions.
