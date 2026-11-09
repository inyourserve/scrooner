---
id: workflow-code-ref-must-be-a-full-40-char-sha-actions-checkou
title: Workflow code_ref must be a full 40-char SHA: actions/checkout reads a short SHA as a branch
kind: gotcha
tags: ci, github-actions, fsn-write
paths: .github/workflows/pipeline-fsn-write.yml
evidence: CODE-CHECKED
created: 2026-11-09
verified: 2026-11-09
---
pipeline-fsn-write run 42559698212 (2026-11-09) failed at actions/checkout with code_ref=bc6ab31: checkout fetched +refs/heads/bc6ab31* and exited 1 three times; nothing was written. The same run with code_ref=bc6ab31b46a76e46eedf791844272977c6f408dd (run 42561798991) checked out fine. Pass branch names or full SHAs to any workflow's code_ref input, never a short SHA.
