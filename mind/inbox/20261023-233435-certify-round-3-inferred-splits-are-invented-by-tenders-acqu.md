---
id: certify-round-3-inferred-splits-are-invented-by-tenders-acqu
title: Certify round 3 inferred splits are invented by tenders, acquisitions and IPO conversions
kind: lesson
tags: certification, splits, share_basis
paths: pipeline/src/scrooner_pipeline/certification/splits.py
evidence: FILING-CHECKED
source: data-team/strategy/team/CERTIFY-ROUND3-VALIDATION-2026-10-23.md
created: 2026-10-23
verified: 2026-10-23
---
On fresh shards S025/S044/S058, 4 of 5 share_basis_mismatch flags at commit 5382813 assume splits that never happened: INCY x0.8 (2024 self-tender, SC TO-I 0001104659-24-060326), STE x0.8 (Cantel acquisition shares), TER x2 (no event), DOCU /4 (IPO preferred conversion, 10-Q 0001261333-18-000009). A share-count step is never split evidence by itself; require restated per-share comparatives for integer steps too.
