---
id: run-mind-unit-tests-from-inside-mind-not-the-repo-root
title: Run mind unit tests from inside mind/, not the repo root
kind: gotcha
tags: mind, tests, python
paths: mind/test_mind.py
evidence: CODE-CHECKED
status: active
created: 2026-10-21
verified: 2026-10-21
---
From the repo root, python3 -m unittest mind/test_mind.py errors because the mind directory shadows the mind module. Use: cd mind && python3 -m unittest test_mind.
