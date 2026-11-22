---
id: a-proof-rule-version-bump-makes-every-cell-proved-under-the-
title: A proof rule version bump makes every cell proved under the old version show as UNCHECKED no_proof_row until re-proved
kind: gotcha
tags: proof, coverage, rule-version
paths: pipeline/src/scrooner_pipeline/proof/rules.py
evidence: DATA-INFERRED
status: active
created: 2026-11-22
verified: 2026-11-22
---
2026-11-22: component_parts v1->v2->v3 (86214761, cea4cf20) made ~460 PROVEN component-sum cells (TXN, GILD, AMAT, ADI, MA, MSFT...) read as UNCHECKED no_proof_row in the hourly export, because load_current_proofs accepts only proofs at current rule versions. Open shown rose 1,485->1,648 with no value change. Any rule bump must be followed by a scoped re-prove (top100_flow proof --write) before reading the scoreboard; a fix to label these proof_stale is in progress.
