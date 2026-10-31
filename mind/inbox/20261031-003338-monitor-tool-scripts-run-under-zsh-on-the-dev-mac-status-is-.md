---
id: monitor-tool-scripts-run-under-zsh-on-the-dev-mac-status-is-
title: Monitor-tool scripts run under zsh on the dev Mac: 'status' is a read-only variable and bash associative arrays are not portable
kind: gotcha
tags: claude-code, monitor, zsh
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
A Monitor poll loop that assigned status=... died at once with '(eval):9: read-only variable: status' (exit 1), so the CI watch silently stopped. Use names like st/cc, plain variables instead of declare -A, and check the task output file when a monitor reports 'failed' right after starting.
