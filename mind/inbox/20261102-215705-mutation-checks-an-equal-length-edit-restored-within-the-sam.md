---
id: mutation-checks-an-equal-length-edit-restored-within-the-sam
title: Mutation checks: an equal-length edit restored within the same second leaves a stale .pyc running the mutated code
kind: gotcha
tags: testing, mutation, python
paths: pipeline/src/scrooner_pipeline/fsn_store/bs_derive.py
evidence: CODE-CHECKED
created: 2026-11-02
verified: 2026-11-02
---
Python validates a .pyc by source mtime (1 s resolution) and size. A mutation that keeps the length ('mezz' -> 'liab') restored by mv within the same second keeps the mutated bytecode: later tests and measurement runs silently execute the mutation (2026-11-02, bs_derive). Run mutation checks with PYTHONDONTWRITEBYTECODE=1, or delete __pycache__ after restoring.
