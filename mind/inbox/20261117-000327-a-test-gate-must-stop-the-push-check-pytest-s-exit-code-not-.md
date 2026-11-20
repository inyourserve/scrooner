---
id: a-test-gate-must-stop-the-push-check-pytest-s-exit-code-not-
title: A test gate must stop the push: check pytest's exit code, not its tail
kind: lesson
tags: ci, tests
evidence: CODE-CHECKED
created: 2026-11-17
verified: 2026-11-17
---
Running pytest in a subshell and piping to tail, then chaining git push with &&, pushes even when tests fail (the subshell's status is tail's). be9134bb shipped with a failing test (test_an_unlisted_data_point_is_never_hidden_by_this_rule used inventory as its unlisted example). Gate pushes on pytest's own exit code (e.g. pytest ... || exit 1) before committing.
