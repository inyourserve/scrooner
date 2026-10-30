---
id: a-github-actions-job-that-fails-in-2s-with-zero--1e1794
title: A GitHub Actions job that "fails" in ~2s with zero steps never started
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
— read the reason from job annotations (`gh api repos/<owner>/<repo>/check-runs/<job_id>/annotations --jq '.[].message'`), not the logs; sort failed runs into "never started" (billing/infra) vs. "really ran" before chasing code.
